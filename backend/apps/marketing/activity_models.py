from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class ActivityPurchaseRecord(TimeStampedModel):
    class ActivityType(models.TextChoices):
        GROUP = "group", "Group"
        SECKILL = "seckill", "Seckill"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.PROTECT)
    activity_type = models.CharField("Activity Type", max_length=20, choices=ActivityType.choices)
    activity_id = models.PositiveBigIntegerField("Activity ID")
    order = models.ForeignKey("orders.Order", verbose_name="Order", on_delete=models.PROTECT, related_name="activity_records")
    quantity = models.PositiveIntegerField("Quantity")

    class Meta:
        db_table = "activity_purchase_record"
        indexes = [
            models.Index(fields=["user", "activity_type", "activity_id"], name="idx_activity_user"),
            models.Index(fields=["activity_type", "activity_id"], name="idx_activity_lookup"),
        ]
        verbose_name = "Activity Purchase Record"
        verbose_name_plural = verbose_name
