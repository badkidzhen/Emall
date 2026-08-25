from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class MemberLevel(TimeStampedModel):
    name = models.CharField("等级名称", max_length=50)
    upgrade_amount = models.DecimalField("升级消费金额", max_digits=12, decimal_places=2, default=0)
    team_upgrade_amount = models.DecimalField("团队升级金额", max_digits=12, decimal_places=2, default=0)
    commission_rate_lv1 = models.DecimalField("一级佣金比例", max_digits=5, decimal_places=2, default=0)
    commission_rate_lv2 = models.DecimalField("二级佣金比例", max_digits=5, decimal_places=2, default=0)
    discount = models.DecimalField("会员折扣", max_digits=4, decimal_places=2, default=1)
    sort = models.PositiveIntegerField("排序", default=0)

    class Meta:
        db_table = "member_level"
        ordering = ["-sort", "id"]
        verbose_name = "会员等级"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        NORMAL = "normal", "普通用户"
        MEMBER = "member", "会员"
        DISTRIBUTOR = "distributor", "分销商"
        TEAM_LEADER = "team_leader", "团队长"
        CITY_AGENT = "city_agent", "城市代理"
        ADMIN = "admin", "平台管理员"

    class CityAgentLevel(models.IntegerChoices):
        NONE = 0, "无"
        DISTRICT = 1, "区县级"
        CITY = 2, "市级"
        PROVINCE = 3, "省级"

    class RealnameStatus(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    parent = models.ForeignKey(
        "self",
        verbose_name="上级",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    path = models.CharField("关系路径", max_length=255, blank=True, default="")
    openid = models.CharField("微信 OpenID", max_length=64, null=True, blank=True, unique=True)
    mobile = models.CharField("手机号", max_length=20, null=True, blank=True, unique=True)
    nickname = models.CharField("昵称", max_length=50, blank=True, default="")
    avatar = models.URLField("头像", max_length=500, blank=True, default="")
    level = models.ForeignKey(
        MemberLevel,
        verbose_name="会员等级",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )
    role = models.CharField("角色", max_length=32, choices=Role.choices, default=Role.NORMAL)
    is_distributor = models.BooleanField("是否分销商", default=False)
    city_agent_level = models.PositiveSmallIntegerField(
        "城市代理等级",
        choices=CityAgentLevel.choices,
        default=CityAgentLevel.NONE,
    )
    city_code = models.CharField("代理区域编码", max_length=20, null=True, blank=True)
    realname = models.CharField("真实姓名", max_length=50, blank=True, default="")
    id_card = models.CharField("身份证号", max_length=32, blank=True, default="")
    realname_status = models.CharField(
        "Realname Status",
        max_length=20,
        choices=RealnameStatus.choices,
        default=RealnameStatus.UNVERIFIED,
    )
    realname_remark = models.CharField("Realname Remark", max_length=255, blank=True, default="")
    realname_verified_at = models.DateTimeField("Realname Verified At", null=True, blank=True)

    class Meta:
        db_table = "user"
        indexes = [
            models.Index(fields=["parent"], name="idx_user_parent"),
            models.Index(fields=["path"], name="idx_user_path"),
            models.Index(fields=["openid"], name="idx_user_openid"),
            models.Index(fields=["mobile"], name="idx_user_mobile"),
        ]
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def bind_parent(self, parent):
        if parent and parent.pk == self.pk:
            raise ValueError("用户不能绑定自己为上级")
        self.parent = parent
        self.path = "{0}{1},".format(parent.path or ",", parent.pk) if parent else ""
