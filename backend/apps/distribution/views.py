from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import CommissionRecord, DistributionConfigModel, UserTeamStat
from .serializers import (
    BindMineParentSerializer,
    BindParentSerializer,
    CommissionRecordSerializer,
    DistributionConfigSerializer,
    UserTeamStatSerializer,
)
from .services import DistributionError, bind_parent, settle_due_commissions, sync_user_team_stat


class UserTeamStatViewSet(viewsets.ModelViewSet):
    queryset = UserTeamStat.objects.select_related("user").all()
    serializer_class = UserTeamStatSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user"]
    ordering_fields = ["team_count", "team_order_amount", "team_commission"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "sync"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def sync(self, request):
        user_id = request.data.get("user_id")
        stat = sync_user_team_stat(user_id)
        return Response(UserTeamStatSerializer(stat).data)

    @action(detail=False, methods=["get"], url_path="tree", permission_classes=[IsAuthenticated])
    def tree(self, request):
        User = get_user_model()
        root = request.user
        user_id = request.query_params.get("user_id")
        if request.user.is_staff and user_id:
            try:
                root = User.objects.get(pk=user_id)
            except (TypeError, ValueError, User.DoesNotExist):
                return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        descendants = list(
            User.objects.filter(path__contains=f",{root.id},")
            .values("id", "username", "nickname", "mobile", "role", "parent_id")
            .order_by("id")
        )
        children_by_parent = {}
        for item in descendants:
            item["label"] = item["nickname"] or item["username"] or f'用户{item["id"]}'
            item["children"] = []
            children_by_parent.setdefault(item["parent_id"], []).append(item)

        def attach_children(node):
            node["children"] = children_by_parent.get(node["id"], [])
            for child in node["children"]:
                attach_children(child)
            return node

        root_node = {
            "id": root.id,
            "username": root.username,
            "nickname": root.nickname,
            "mobile": root.mobile,
            "role": root.role,
            "parent_id": root.parent_id,
            "label": root.nickname or root.username or f"用户{root.id}",
            "children": [],
        }
        return Response(attach_children(root_node))


class DistributionConfigViewSet(viewsets.ModelViewSet):
    queryset = DistributionConfigModel.objects.all()
    serializer_class = DistributionConfigSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["post"], url_path="bind-parent", permission_classes=[IsAdminUser])
    def bind_parent_action(self, request):
        serializer = BindParentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = bind_parent(serializer.validated_data["user_id"], serializer.validated_data["parent_id"])
        except DistributionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": user.id, "parent": user.parent_id, "path": user.path})

    @action(detail=False, methods=["post"], url_path="bind-mine", permission_classes=[IsAuthenticated])
    def bind_mine(self, request):
        serializer = BindMineParentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = bind_parent(request.user.id, serializer.validated_data["parent_id"])
        except DistributionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": user.id, "parent": user.parent_id, "path": user.path})

    @action(detail=False, methods=["post"], url_path="settle-commissions", permission_classes=[IsAdminUser])
    def settle_commissions(self, request):
        return Response(settle_due_commissions())


class CommissionRecordViewSet(viewsets.ModelViewSet):
    queryset = CommissionRecord.objects.select_related("user", "order", "source_user").all()
    serializer_class = CommissionRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "order", "level", "status"]
    ordering_fields = ["amount", "created_at", "settle_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset
