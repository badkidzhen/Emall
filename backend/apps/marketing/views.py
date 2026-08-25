from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly

from .models import CouponTemplate, GroupBuyingActivity, SeckillActivity, UserCoupon
from .activity_models import ActivityPurchaseRecord
from .serializers import (
    ActivityPurchaseSerializer,
    ActivityPurchaseRecordSerializer,
    CouponTemplateSerializer,
    GroupBuyingActivitySerializer,
    SeckillActivitySerializer,
    UserCouponSerializer,
)
from .services import MarketingError, claim_coupon, expire_coupons, purchase_group_activity, purchase_seckill_activity


class CouponTemplateViewSet(viewsets.ModelViewSet):
    queryset = CouponTemplate.objects.all()
    serializer_class = CouponTemplateSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    filterset_fields = ["coupon_type"]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def claim(self, request, pk=None):
        try:
            coupon = claim_coupon(request.user, pk)
        except MarketingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserCouponSerializer(coupon).data, status=status.HTTP_201_CREATED)


class UserCouponViewSet(viewsets.ModelViewSet):
    queryset = UserCoupon.objects.select_related("user", "template").all()
    serializer_class = UserCouponSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "template", "status"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "expire"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return queryset.filter(user=user)
        return queryset

    @action(detail=False, methods=["post"])
    def expire(self, request):
        return Response(expire_coupons())


class GroupBuyingActivityViewSet(viewsets.ModelViewSet):
    queryset = GroupBuyingActivity.objects.select_related("sku", "sku__product").all()
    serializer_class = GroupBuyingActivitySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    filterset_fields = ["enabled", "sku"]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        serializer = ActivityPurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = purchase_group_activity(request.user, pk, serializer.validated_data["quantity"])
        except MarketingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"order": order.id, "order_no": order.order_no, "pay_amount": order.pay_amount}, status=status.HTTP_201_CREATED)


class SeckillActivityViewSet(viewsets.ModelViewSet):
    queryset = SeckillActivity.objects.select_related("sku", "sku__product").all()
    serializer_class = SeckillActivitySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    filterset_fields = ["enabled", "sku"]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        serializer = ActivityPurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = purchase_seckill_activity(request.user, pk, serializer.validated_data["quantity"])
        except MarketingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"order": order.id, "order_no": order.order_no, "pay_amount": order.pay_amount}, status=status.HTTP_201_CREATED)


class ActivityPurchaseRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityPurchaseRecord.objects.select_related("user", "order").all()
    serializer_class = ActivityPurchaseRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "activity_type", "activity_id", "order"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return queryset.filter(user=user)
        return queryset
