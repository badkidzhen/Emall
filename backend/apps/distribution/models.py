from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.orders.models import Order


class UserTeamStat(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="用户", on_delete=models.CASCADE, primary_key=True)
    team_count = models.PositiveIntegerField("团队总人数", default=0)
    direct_count = models.PositiveIntegerField("直推人数", default=0)
    indirect_count = models.PositiveIntegerField("间推人数", default=0)
    team_order_amount = models.DecimalField("团队订单总额", max_digits=12, decimal_places=2, default=0)
    team_commission = models.DecimalField("团队佣金总额", max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "user_team_stat"
        verbose_name = "团队统计"
        verbose_name_plural = verbose_name


class DistributionConfigModel(TimeStampedModel):
    name = models.CharField("配置名称", max_length=100, default="平台默认配置")
    default_rate_lv1 = models.DecimalField("默认一级佣金比例", max_digits=5, decimal_places=2, default=10)
    default_rate_lv2 = models.DecimalField("默认二级佣金比例", max_digits=5, decimal_places=2, default=5)
    settlement_delay_days = models.PositiveIntegerField("冻结期天数", default=7)
    enabled = models.BooleanField("是否启用", default=True)

    class Meta:
        db_table = "distribution_config"
        verbose_name = "分销配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CommissionRecord(TimeStampedModel):
    class Level(models.IntegerChoices):
        FIRST = 1, "一级佣金"
        SECOND = 2, "二级佣金"

    class Status(models.TextChoices):
        FROZEN = "frozen", "冻结中"
        SETTLED = "settled", "已结算"
        CANCELED = "canceled", "已取消"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="受益用户", on_delete=models.PROTECT, related_name="commissions")
    order = models.ForeignKey(Order, verbose_name="订单", on_delete=models.PROTECT, related_name="commission_records")
    source_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="下单用户", on_delete=models.PROTECT, related_name="generated_commissions")
    level = models.PositiveSmallIntegerField("分销层级", choices=Level.choices)
    rate = models.DecimalField("佣金比例", max_digits=5, decimal_places=2)
    amount = models.DecimalField("佣金金额", max_digits=12, decimal_places=2)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.FROZEN)
    settle_at = models.DateTimeField("预计结算时间", null=True, blank=True)

    class Meta:
        db_table = "commission_record"
        indexes = [
            models.Index(fields=["user", "status"], name="idx_commission_user_status"),
            models.Index(fields=["order"], name="idx_commission_order"),
        ]
        verbose_name = "佣金明细"
        verbose_name_plural = verbose_name

