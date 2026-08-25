from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.utils import timezone

from apps.core.permissions import IsAdminOrReadOnly
from rest_framework.response import Response
from rest_framework import viewsets

from .models import MemberLevel, User
from .serializers import MemberLevelSerializer, RealnameAuditSerializer, RealnameSubmitSerializer, UserSerializer


class MemberLevelViewSet(viewsets.ModelViewSet):
    queryset = MemberLevel.objects.all()
    serializer_class = MemberLevelSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["sort", "upgrade_amount", "created_at"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("level", "parent").all()
    serializer_class = UserSerializer
    search_fields = ["username", "mobile", "nickname", "openid"]
    filterset_fields = ["role", "is_distributor", "city_agent_level", "city_code", "realname_status"]
    ordering_fields = ["id", "date_joined"]

    def get_permissions(self):
        if self.action == "me":
            return [IsAuthenticated()]
        if self.action == "submit_realname":
            return [IsAuthenticated()]
        if self.action == "audit_realname":
            return [IsAdminUser()]
        if self.action in {"list", "create", "update", "partial_update", "destroy"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return queryset.filter(id=user.id)
        return queryset

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=["post"], url_path="submit-realname", permission_classes=[IsAuthenticated])
    def submit_realname(self, request):
        serializer = RealnameSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.realname = serializer.validated_data["realname"]
        user.id_card = serializer.validated_data["id_card"]
        user.realname_status = User.RealnameStatus.PENDING
        user.realname_remark = ""
        user.realname_verified_at = None
        user.save(
            update_fields=[
                "realname",
                "id_card",
                "realname_status",
                "realname_remark",
                "realname_verified_at",
            ]
        )
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=["post"], url_path="audit-realname", permission_classes=[IsAdminUser])
    def audit_realname(self, request, pk=None):
        serializer = RealnameAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        if serializer.validated_data["approved"]:
            user.realname_status = User.RealnameStatus.VERIFIED
            user.realname_verified_at = timezone.now()
        else:
            user.realname_status = User.RealnameStatus.REJECTED
            user.realname_verified_at = None
        user.realname_remark = serializer.validated_data["remark"]
        user.save(update_fields=["realname_status", "realname_remark", "realname_verified_at"])
        return Response(UserSerializer(user).data)
