from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class CityAgentApplication(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "待审核"
        APPROVED = "approved", "已通过"
        REJECTED = "rejected", "已拒绝"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="申请人", on_delete=models.PROTECT)
    level = models.PositiveSmallIntegerField("代理等级")
    region_code = models.CharField("区域编码", max_length=20)
    region_name = models.CharField("区域名称", max_length=100)
    contact_name = models.CharField("联系人", max_length=50)
    contact_phone = models.CharField("联系电话", max_length=20)
    status = models.CharField("审核状态", max_length=20, choices=Status.choices, default=Status.PENDING)
    audit_remark = models.CharField("审核备注", max_length=255, blank=True, default="")

    class Meta:
        db_table = "city_agent_application"
        verbose_name = "代理申请"
        verbose_name_plural = verbose_name


class CityAgent(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="代理用户", on_delete=models.PROTECT, related_name="agent_regions")
    level = models.PositiveSmallIntegerField("代理等级")
    region_code = models.CharField("区域编码", max_length=20)
    region_name = models.CharField("区域名称", max_length=100)
    commission_rate = models.DecimalField("区域抽成比例", max_digits=5, decimal_places=2, default=0)
    enabled = models.BooleanField("是否启用", default=True)

    class Meta:
        db_table = "city_agent"
        constraints = [
            models.UniqueConstraint(fields=["level", "region_code"], name="uk_agent_level_region"),
        ]
        verbose_name = "城市代理"
        verbose_name_plural = verbose_name

