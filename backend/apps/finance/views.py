from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import FundFlow, Wallet, WithdrawApplication
from .serializers import (
    ApplyWithdrawSerializer,
    FundFlowSerializer,
    WalletSerializer,
    WithdrawApplicationSerializer,
    WithdrawAuditSerializer,
    WithdrawPayoutSerializer,
)
from .payout_gateways import PayoutGatewayError
from .services import (
    FinanceError,
    apply_withdraw,
    approve_withdraw,
    get_wallet,
    mark_withdraw_paid,
    reject_withdraw,
    submit_withdraw_payout,
)


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Wallet.objects.select_related("user").all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    @action(detail=False, methods=["get"])
    def mine(self, request):
        return Response(WalletSerializer(get_wallet(request.user)).data)


class FundFlowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FundFlow.objects.select_related("user", "wallet").all()
    serializer_class = FundFlowSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "flow_type", "biz_type", "biz_id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset


class WithdrawApplicationViewSet(viewsets.ModelViewSet):
    queryset = WithdrawApplication.objects.select_related("user").all()
    serializer_class = WithdrawApplicationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "status"]

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy", "approve", "reject", "submit_payout", "mark_paid"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = ApplyWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = apply_withdraw(
                request.user,
                serializer.validated_data["amount"],
                serializer.validated_data["account_name"],
                serializer.validated_data["account_no"],
                channel=serializer.validated_data["channel"],
            )
        except FinanceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WithdrawApplicationSerializer(application).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        serializer = WithdrawAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = approve_withdraw(pk, serializer.validated_data["remark"])
        except FinanceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WithdrawApplicationSerializer(application).data)

    @action(detail=True, methods=["post"], url_path="submit-payout", permission_classes=[IsAdminUser])
    def submit_payout(self, request, pk=None):
        serializer = WithdrawPayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = submit_withdraw_payout(pk, serializer.validated_data["remark"])
        except (FinanceError, PayoutGatewayError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WithdrawApplicationSerializer(application).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        serializer = WithdrawAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = reject_withdraw(pk, serializer.validated_data["remark"])
        except FinanceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WithdrawApplicationSerializer(application).data)

    @action(detail=True, methods=["post"], url_path="mark-paid", permission_classes=[IsAdminUser])
    def mark_paid(self, request, pk=None):
        serializer = WithdrawAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = mark_withdraw_paid(pk, serializer.validated_data["remark"])
        except FinanceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(WithdrawApplicationSerializer(application).data)
