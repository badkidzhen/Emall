from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class RewardPool(TimeStampedModel):
    class PoolType(models.TextChoices):
        GLOBAL = "global", "平台全局池"
        CITY_AGENT = "city_agent", "城市代理池"
        TEAM_LEADER = "team_leader", "团队长池"
        DISTRIBUTOR = "distributor", "分销精英池"
        MONTHLY = "monthly", "月度争霸池"

    name = models.CharField("池子名称", max_length=100)
    pool_type = models.CharField("池子类型", max_length=32, choices=PoolType.choices)
    amount = models.DecimalField("池子金额", max_digits=12, decimal_places=2, default=0)
    min_performance = models.DecimalField("最低业绩门槛", max_digits=12, decimal_places=2, default=0)
    max_user_ratio = models.DecimalField("单用户最高占比", max_digits=5, decimal_places=2, default=20)
    enabled = models.BooleanField("是否启用", default=True)

    class Meta:
        db_table = "reward_pool"
        verbose_name = "奖金池"
        verbose_name_plural = verbose_name


class RewardPoolRule(TimeStampedModel):
    pool = models.ForeignKey(RewardPool, verbose_name="奖金池", on_delete=models.CASCADE, related_name="rules")
    team_amount_weight = models.DecimalField("团队业绩权重", max_digits=5, decimal_places=2, default=0)
    team_count_weight = models.DecimalField("团队人数权重", max_digits=5, decimal_places=2, default=0)
    personal_amount_weight = models.DecimalField("个人业绩权重", max_digits=5, decimal_places=2, default=0)
    rank_config = models.JSONField("排名阶梯配置", default=dict, blank=True)

    class Meta:
        db_table = "reward_pool_rule"
        verbose_name = "奖金池规则"
        verbose_name_plural = verbose_name


class RewardDistributionRecord(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "待发放"
        PAID = "paid", "已发放"
        CANCELED = "canceled", "已取消"

    pool = models.ForeignKey(RewardPool, verbose_name="奖金池", on_delete=models.PROTECT, related_name="records")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="受益用户", on_delete=models.PROTECT)
    score = models.DecimalField("分配得分", max_digits=18, decimal_places=4, default=0)
    amount = models.DecimalField("分配金额", max_digits=12, decimal_places=2, default=0)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.PENDING)
    distributed_at = models.DateTimeField("发放时间", null=True, blank=True)

    class Meta:
        db_table = "reward_distribution_record"
        indexes = [
            models.Index(fields=["pool", "status"], name="idx_reward_pool_status"),
            models.Index(fields=["user", "status"], name="idx_reward_user_status"),
        ]
        verbose_name = "奖金池分配记录"
        verbose_name_plural = verbose_name

