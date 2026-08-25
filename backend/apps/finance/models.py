from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Wallet(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField("Balance", max_digits=12, decimal_places=2, default=0)
    frozen_balance = models.DecimalField("Frozen Balance", max_digits=12, decimal_places=2, default=0)
    total_income = models.DecimalField("Total Income", max_digits=12, decimal_places=2, default=0)
    total_withdraw = models.DecimalField("Total Withdraw", max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "wallet"
        verbose_name = "Wallet"
        verbose_name_plural = verbose_name


class FundFlow(TimeStampedModel):
    class FlowType(models.TextChoices):
        INCOME = "income", "Income"
        WITHDRAW = "withdraw", "Withdraw"
        FREEZE = "freeze", "Freeze"
        UNFREEZE = "unfreeze", "Unfreeze"
        ADJUST = "adjust", "Adjust"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.PROTECT)
    wallet = models.ForeignKey(Wallet, verbose_name="Wallet", on_delete=models.PROTECT, related_name="flows")
    flow_type = models.CharField("Flow Type", max_length=20, choices=FlowType.choices)
    amount = models.DecimalField("Amount", max_digits=12, decimal_places=2)
    balance_after = models.DecimalField("Balance After", max_digits=12, decimal_places=2)
    biz_type = models.CharField("Biz Type", max_length=50, blank=True, default="")
    biz_id = models.CharField("Biz ID", max_length=64, blank=True, default="")
    remark = models.CharField("Remark", max_length=255, blank=True, default="")

    class Meta:
        db_table = "fund_flow"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "flow_type"], name="idx_fund_user_type"),
            models.Index(fields=["biz_type", "biz_id"], name="idx_fund_biz"),
        ]
        verbose_name = "Fund Flow"
        verbose_name_plural = verbose_name


class WithdrawApplication(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        PAYING = "paying", "Paying"
        REJECTED = "rejected", "Rejected"
        PAID = "paid", "Paid"

    class Channel(models.TextChoices):
        MANUAL = "manual", "Manual"
        WECHAT = "wechat", "WeChat"
        BANK = "bank", "Bank"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.PROTECT, related_name="withdrawals")
    amount = models.DecimalField("Amount", max_digits=12, decimal_places=2)
    channel = models.CharField("Channel", max_length=20, choices=Channel.choices, default=Channel.MANUAL)
    account_name = models.CharField("Account Name", max_length=100)
    account_no = models.CharField("Account No", max_length=100)
    status = models.CharField("Status", max_length=20, choices=Status.choices, default=Status.PENDING)
    audit_remark = models.CharField("Audit Remark", max_length=255, blank=True, default="")
    audited_at = models.DateTimeField("Audited At", null=True, blank=True)
    payout_no = models.CharField("Payout No", max_length=128, blank=True, default="")
    paid_at = models.DateTimeField("Paid At", null=True, blank=True)
    raw_payload = models.JSONField("Raw Payload", default=dict, blank=True)

    class Meta:
        db_table = "withdraw_application"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"], name="idx_withdraw_user_status"),
        ]
        verbose_name = "Withdraw Application"
        verbose_name_plural = verbose_name
