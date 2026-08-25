from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import FundFlow, Wallet, WithdrawApplication
from .payout_gateways import PayoutGatewayError, get_payout_gateway


class FinanceError(ValueError):
    pass


def get_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def add_income(user, amount, biz_type="", biz_id="", remark=""):
    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get_or_create(user=user)[0]
        wallet.balance += amount
        wallet.total_income += amount
        wallet.save(update_fields=["balance", "total_income", "updated_at"])
        flow = FundFlow.objects.create(
            user=user,
            wallet=wallet,
            flow_type=FundFlow.FlowType.INCOME,
            amount=amount,
            balance_after=wallet.balance,
            biz_type=biz_type,
            biz_id=str(biz_id),
            remark=remark,
        )
    return flow


def apply_withdraw(user, amount, account_name, account_no, channel=WithdrawApplication.Channel.MANUAL):
    if amount <= 0:
        raise FinanceError("Withdraw amount must be positive.")
    if settings.FINANCE_REQUIRE_REALNAME_FOR_WITHDRAW and user.realname_status != user.RealnameStatus.VERIFIED:
        raise FinanceError("Real-name verification is required before withdrawal.")
    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get_or_create(user=user)[0]
        if wallet.balance < amount:
            raise FinanceError("Insufficient wallet balance.")
        wallet.balance -= amount
        wallet.frozen_balance += amount
        wallet.save(update_fields=["balance", "frozen_balance", "updated_at"])
        application = WithdrawApplication.objects.create(
            user=user,
            amount=amount,
            channel=channel,
            account_name=account_name,
            account_no=account_no,
        )
        FundFlow.objects.create(
            user=user,
            wallet=wallet,
            flow_type=FundFlow.FlowType.FREEZE,
            amount=amount,
            balance_after=wallet.balance,
            biz_type="withdraw",
            biz_id=application.id,
            remark="withdraw_apply",
        )
    return application


def submit_withdraw_payout(application_id, remark=""):
    with transaction.atomic():
        application = WithdrawApplication.objects.select_for_update().select_related("user").get(pk=application_id)
        if application.status != WithdrawApplication.Status.APPROVED:
            raise FinanceError("Only approved withdrawals can submit payout.")
        gateway = get_payout_gateway(application.channel)
        try:
            result = gateway.submit(application=application)
        except PayoutGatewayError:
            raise
        application.status = WithdrawApplication.Status.PAYING
        application.audit_remark = remark or application.audit_remark
        application.payout_no = result.payout_no
        application.raw_payload = result.payload
        application.save(update_fields=["status", "audit_remark", "payout_no", "raw_payload", "updated_at"])
    return application


def approve_withdraw(application_id, remark=""):
    now = timezone.now()
    with transaction.atomic():
        application = WithdrawApplication.objects.select_for_update().select_related("user").get(pk=application_id)
        if application.status != WithdrawApplication.Status.PENDING:
            raise FinanceError("Only pending withdrawals can be approved.")
        application.status = WithdrawApplication.Status.APPROVED
        application.audit_remark = remark
        application.audited_at = now
        application.save(update_fields=["status", "audit_remark", "audited_at", "updated_at"])
    return application


def reject_withdraw(application_id, remark=""):
    now = timezone.now()
    with transaction.atomic():
        application = WithdrawApplication.objects.select_for_update().select_related("user").get(pk=application_id)
        if application.status != WithdrawApplication.Status.PENDING:
            raise FinanceError("Only pending withdrawals can be rejected.")
        wallet = Wallet.objects.select_for_update().get(user=application.user)
        wallet.balance += application.amount
        wallet.frozen_balance -= application.amount
        wallet.save(update_fields=["balance", "frozen_balance", "updated_at"])
        application.status = WithdrawApplication.Status.REJECTED
        application.audit_remark = remark
        application.audited_at = now
        application.save(update_fields=["status", "audit_remark", "audited_at", "updated_at"])
        FundFlow.objects.create(
            user=application.user,
            wallet=wallet,
            flow_type=FundFlow.FlowType.UNFREEZE,
            amount=application.amount,
            balance_after=wallet.balance,
            biz_type="withdraw",
            biz_id=application.id,
            remark="withdraw_reject",
        )
    return application


def mark_withdraw_paid(application_id, remark=""):
    now = timezone.now()
    with transaction.atomic():
        application = WithdrawApplication.objects.select_for_update().select_related("user").get(pk=application_id)
        if application.status not in {WithdrawApplication.Status.APPROVED, WithdrawApplication.Status.PAYING}:
            raise FinanceError("Only approved/paying withdrawals can be marked paid.")
        wallet = Wallet.objects.select_for_update().get(user=application.user)
        wallet.frozen_balance -= application.amount
        wallet.total_withdraw += application.amount
        wallet.save(update_fields=["frozen_balance", "total_withdraw", "updated_at"])
        application.status = WithdrawApplication.Status.PAID
        application.audit_remark = remark or application.audit_remark
        application.paid_at = now
        application.save(update_fields=["status", "audit_remark", "paid_at", "updated_at"])
        FundFlow.objects.create(
            user=application.user,
            wallet=wallet,
            flow_type=FundFlow.FlowType.WITHDRAW,
            amount=application.amount,
            balance_after=wallet.balance,
            biz_type="withdraw",
            biz_id=application.id,
            remark="withdraw_paid",
        )
    return application
