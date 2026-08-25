from rest_framework import serializers

from .models import MemberLevel, User


class MemberLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberLevel
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    level_name = serializers.CharField(source="level.name", read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    parent_display = serializers.SerializerMethodField()
    parent_mobile = serializers.SerializerMethodField()
    relation_chain = serializers.SerializerMethodField()
    relation_chain_text = serializers.SerializerMethodField()
    direct_count = serializers.SerializerMethodField()
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "email",
            "is_staff",
            "is_active",
            "is_superuser",
            "mobile",
            "nickname",
            "avatar",
            "level",
            "level_name",
            "role",
            "is_distributor",
            "city_agent_level",
            "city_code",
            "realname",
            "id_card",
            "realname_status",
            "realname_remark",
            "realname_verified_at",
            "parent",
            "parent_display",
            "parent_mobile",
            "path",
            "relation_chain",
            "relation_chain_text",
            "direct_count",
            "team_count",
            "date_joined",
        ]
        read_only_fields = ["realname_status", "realname_remark", "realname_verified_at", "path", "date_joined"]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "is_staff": {"required": False},
            "is_active": {"required": False},
            "is_superuser": {"required": False},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", "")
        user = super().create(validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(update_fields=["password"])
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", "")
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def user_label(self, user):
        return user.nickname or user.username or f"用户{user.id}"

    def get_parent_display(self, obj):
        if not obj.parent_id:
            return ""
        return f"{self.user_label(obj.parent)}（ID {obj.parent_id}）"

    def get_parent_mobile(self, obj):
        return obj.parent.mobile if obj.parent_id and obj.parent else ""

    def get_relation_chain(self, obj):
        ids = [int(item) for item in (obj.path or "").strip(",").split(",") if item]
        ids.append(obj.id)
        users = User.objects.in_bulk(ids)
        chain = []
        for user_id in ids:
            user = users.get(user_id)
            if not user:
                continue
            chain.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "mobile": user.mobile,
                    "label": self.user_label(user),
                }
            )
        return chain

    def get_relation_chain_text(self, obj):
        return " > ".join(item["label"] for item in self.get_relation_chain(obj))

    def get_direct_count(self, obj):
        return obj.children.count()

    def get_team_count(self, obj):
        return User.objects.filter(path__contains=f",{obj.id},").count()


class RealnameSubmitSerializer(serializers.Serializer):
    realname = serializers.CharField(max_length=50)
    id_card = serializers.CharField(max_length=32)


class RealnameAuditSerializer(serializers.Serializer):
    approved = serializers.BooleanField()
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")
