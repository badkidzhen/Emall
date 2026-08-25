from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .menu import ADMIN_MENU
from .models import AdminMenu


class PermissionSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type", "label"]

    def get_label(self, obj):
        return f"{obj.content_type.app_label}.{obj.codename}"


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, required=False)
    permission_count = serializers.IntegerField(source="permissions.count", read_only=True)

    class Meta:
        model = Group
        fields = ["id", "name", "permissions", "permission_count"]


class AdminMenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = AdminMenu
        fields = [
            "id",
            "parent",
            "name",
            "code",
            "icon",
            "path",
            "component",
            "permission",
            "sort",
            "level",
            "is_show",
            "children",
            "created_at",
            "updated_at",
        ]

    def get_children(self, obj):
        children = getattr(obj, "_prefetched_children", None)
        if children is None:
            children = obj.children.all()
        return AdminMenuSerializer(children, many=True).data


class LogEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    content_type_label = serializers.SerializerMethodField()
    action_label = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = [
            "id",
            "action_time",
            "username",
            "content_type",
            "content_type_label",
            "object_id",
            "object_repr",
            "action_flag",
            "action_label",
            "change_message",
        ]

    def get_content_type_label(self, obj):
        if not obj.content_type:
            return ""
        return f"{obj.content_type.app_label}.{obj.content_type.model}"

    def get_action_label(self, obj):
        labels = {1: "新增", 2: "修改", 3: "删除"}
        return labels.get(obj.action_flag, "未知")


class MenuTreeView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        roots = list(
            AdminMenu.objects.filter(parent__isnull=True, is_show=True)
            .prefetch_related("children")
            .order_by("-sort", "id")
        )
        if roots:
            return Response(AdminMenuSerializer(roots, many=True).data)
        return Response(
            [
                {
                    "code": section["code"],
                    "name": section["name"],
                    "icon": section.get("icon", ""),
                    "path": "",
                    "permission": "",
                    "sort": section.get("sort", 0),
                    "level": 1,
                    "is_show": True,
                    "children": [
                        {
                            "code": f'{section["code"]}:{item["path"]}',
                            "name": item["name"],
                            "icon": "",
                            "path": item["path"],
                            "permission": item.get("permission", ""),
                            "sort": item.get("sort", 0),
                            "level": 2,
                            "is_show": True,
                            "children": [],
                        }
                        for item in section.get("children", [])
                    ],
                }
                for section in ADMIN_MENU
            ]
        )


class AdminMenuViewSet(viewsets.ModelViewSet):
    queryset = AdminMenu.objects.select_related("parent").prefetch_related("children").all()
    serializer_class = AdminMenuSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    filterset_fields = ["parent", "level", "is_show"]
    search_fields = ["name", "code", "path", "permission"]
    ordering_fields = ["sort", "created_at"]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.select_related("content_type").order_by("content_type__app_label", "codename")
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    search_fields = ["name", "codename", "content_type__app_label"]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.prefetch_related("permissions").order_by("id")
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]
    search_fields = ["name"]


class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogEntry.objects.select_related("user", "content_type").order_by("-action_time")
    serializer_class = LogEntrySerializer
    permission_classes = [IsAdminUser]
    search_fields = ["user__username", "object_repr", "change_message"]
