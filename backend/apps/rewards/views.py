from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import RewardDistributionRecord, RewardPool, RewardPoolRule
from .serializers import RewardDistributionRecordSerializer, RewardPoolDistributeSerializer, RewardPoolRuleSerializer, RewardPoolSerializer
from .services import RewardError, distribute_pool, mark_pool_records_paid


class RewardPoolViewSet(viewsets.ModelViewSet):
    queryset = RewardPool.objects.prefetch_related("rules").all()
    serializer_class = RewardPoolSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name"]
    filterset_fields = ["pool_type", "enabled"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "distribute", "mark_paid"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(enabled=True)
        return queryset

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def distribute(self, request, pk=None):
        RewardPoolDistributeSerializer(data=request.data).is_valid(raise_exception=True)
        try:
            records = distribute_pool(pk)
        except RewardError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RewardDistributionRecordSerializer(records, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="mark-paid", permission_classes=[IsAdminUser])
    def mark_paid(self, request, pk=None):
        return Response(mark_pool_records_paid(pk))


class RewardPoolRuleViewSet(viewsets.ModelViewSet):
    queryset = RewardPoolRule.objects.select_related("pool").all()
    serializer_class = RewardPoolRuleSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["pool"]


class RewardDistributionRecordViewSet(viewsets.ModelViewSet):
    queryset = RewardDistributionRecord.objects.select_related("pool", "user").all()
    serializer_class = RewardDistributionRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["pool", "user", "status"]
    ordering_fields = ["score", "amount", "created_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset
