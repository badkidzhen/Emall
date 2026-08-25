from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import CityAgent, CityAgentApplication
from .serializers import AgentAuditSerializer, CityAgentApplicationSerializer, CityAgentSerializer
from .services import AgentError, approve_application, reject_application


class CityAgentApplicationViewSet(viewsets.ModelViewSet):
    queryset = CityAgentApplication.objects.select_related("user").all()
    serializer_class = CityAgentApplicationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "level", "region_code", "status"]
    search_fields = ["region_name", "contact_name", "contact_phone"]

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy", "approve", "reject"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return queryset.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        serializer = AgentAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            agent = approve_application(
                pk,
                commission_rate=serializer.validated_data["commission_rate"],
                remark=serializer.validated_data["remark"],
            )
        except AgentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CityAgentSerializer(agent).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        serializer = AgentAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = reject_application(pk, remark=serializer.validated_data["remark"])
        except AgentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CityAgentApplicationSerializer(application).data)


class CityAgentViewSet(viewsets.ModelViewSet):
    queryset = CityAgent.objects.select_related("user").all()
    serializer_class = CityAgentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "level", "region_code", "enabled"]
    search_fields = ["region_name", "user__mobile", "user__username"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset
