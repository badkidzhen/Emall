from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MemberLevel, User


@admin.register(MemberLevel)
class MemberLevelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "upgrade_amount", "team_upgrade_amount", "discount", "sort")
    search_fields = ("name",)


@admin.register(User)
class EmallUserAdmin(UserAdmin):
    list_display = ("id", "username", "mobile", "nickname", "role", "is_distributor", "is_active")
    list_filter = ("role", "is_distributor", "city_agent_level", "is_active")
    search_fields = ("username", "mobile", "nickname", "openid")
    fieldsets = UserAdmin.fieldsets + (
        ("商城资料", {"fields": ("parent", "path", "openid", "mobile", "nickname", "avatar", "level", "role")}),
        ("分销与代理", {"fields": ("is_distributor", "city_agent_level", "city_code")}),
        ("实名认证", {"fields": ("realname", "id_card")}),
    )

