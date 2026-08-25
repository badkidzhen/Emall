from django.db import models

from apps.core.models import TimeStampedModel


class PaymentRecord(TimeStampedModel):
    class Channel(models.TextChoices):
        MOCK = "mock", "Mock"
        WECHAT = "wechat", "WeChat"
        BALANCE = "balance", "Balance"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        CLOSED = "closed", "Closed"

    order = models.ForeignKey("orders.Order", verbose_name="Order", on_delete=models.PROTECT, related_name="payment_records")
    payment_no = models.CharField("Payment No", max_length=128, unique=True)
    channel = models.CharField("Channel", max_length=20, choices=Channel.choices, default=Channel.MOCK)
    amount = models.DecimalField("Amount", max_digits=12, decimal_places=2)
    status = models.CharField("Status", max_length=20, choices=Status.choices, default=Status.PENDING)
    gateway_trade_no = models.CharField("Gateway Trade No", max_length=128, blank=True, default="")
    paid_at = models.DateTimeField("Paid At", null=True, blank=True)
    raw_payload = models.JSONField("Raw Payload", default=dict, blank=True)

    class Meta:
        db_table = "payment_record"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "status"], name="idx_payment_order_status"),
            models.Index(fields=["payment_no"], name="idx_payment_no"),
        ]
        verbose_name = "Payment Record"
        verbose_name_plural = verbose_name
