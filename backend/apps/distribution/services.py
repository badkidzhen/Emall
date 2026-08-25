from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.orders.models import Order

from .models import CommissionRecord, DistributionConfigModel, UserTeamStat


class DistributionError(ValueError):
    pass


def bind_parent(user_id, parent_id):
    User = get_user_model()
    with transaction.atomic():
        user = User.objects.select_for_update().get(pk=user_id)
        parent = User.objects.select_for_update().get(pk=parent_id)
        if user.id == parent.id:
            raise DistributionError("User cannot bind self as parent.")
        if parent.path and f",{user.id}," in parent.path:
            raise DistributionError("Cannot bind descendant as parent.")
        user.bind_parent(parent)
        if user.role == User.Role.NORMAL:
            user.role = User.Role.MEMBER
        user.save(update_fields=["parent", "path", "role"])
        sync_user_team_stat(parent.id)
    return user


def calculate_order_commission(order_id):
    with transaction.atomic():
        order = Order.objects.select_for_update().select_related("user").get(pk=order_id)
        if order.status != Order.Status.COMPLETED:
            raise DistributionError("Only completed orders can generate commission.")
        if CommissionRecord.objects.filter(order=order).exists():
            return list(CommissionRecord.objects.filter(order=order))

        config = DistributionConfigModel.objects.filter(enabled=True).order_by("-id").first()
        delay_days = config.settlement_delay_days if config else 7
        parent_chain = get_parent_chain(order.user)
        records = []
        for level, user in enumerate(parent_chain[:2], start=1):
            rate = get_commission_rate(user, level, config)
            if rate <= 0:
                continue
            amount = (order.pay_amount * rate / Decimal("100.00")).quantize(Decimal("0.01"))
            if amount <= 0:
                continue
            records.append(
                CommissionRecord(
                    user=user,
                    order=order,
                    source_user=order.user,
                    level=level,
                    rate=rate,
                    amount=amount,
                    status=CommissionRecord.Status.FROZEN,
                    settle_at=timezone.now() + timezone.timedelta(days=delay_days),
                )
            )

        CommissionRecord.objects.bulk_create(records)
        update_team_stats_for_order(order)
    return list(CommissionRecord.objects.filter(order=order))


def settle_due_commissions(limit=500):
    now = timezone.now()
    settled_count = 0
    with transaction.atomic():
        records = list(
            CommissionRecord.objects.select_for_update()
            .filter(status=CommissionRecord.Status.FROZEN, settle_at__lte=now)
            .order_by("settle_at")[:limit]
        )
        for record in records:
            record.status = CommissionRecord.Status.SETTLED
            record.save(update_fields=["status", "updated_at"])
            from apps.finance.services import add_income

            add_income(
                record.user,
                record.amount,
                biz_type="commission",
                biz_id=record.id,
                remark=f"order:{record.order_id}",
            )
            settled_count += 1
    return {"settled_count": settled_count}


def sync_user_team_stat(user_id):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    direct_count = User.objects.filter(parent=user).count()
    team_users = User.objects.filter(path__contains=f",{user.id},")
    team_count = team_users.count()
    indirect_count = max(team_count - direct_count, 0)
    team_user_ids = list(team_users.values_list("id", flat=True))
    orders = Order.objects.filter(user_id__in=team_user_ids, status=Order.Status.COMPLETED)
    team_order_amount = orders.aggregate(total=Sum("pay_amount"))["total"] or Decimal("0.00")
    team_commission = CommissionRecord.objects.filter(user=user).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    stat, _ = UserTeamStat.objects.update_or_create(
        user=user,
        defaults={
            "team_count": team_count,
            "direct_count": direct_count,
            "indirect_count": indirect_count,
            "team_order_amount": team_order_amount,
            "team_commission": team_commission,
        },
    )
    return stat


def update_team_stats_for_order(order):
    for user in get_parent_chain(order.user):
        sync_user_team_stat(user.id)


def get_parent_chain(user):
    if not user.path:
        return []
    User = get_user_model()
    ids = [int(item) for item in user.path.strip(",").split(",") if item]
    users = User.objects.in_bulk(ids)
    return [users[user_id] for user_id in reversed(ids) if user_id in users]


def get_commission_rate(user, level, config):
    if user.level:
        if level == 1 and user.level.commission_rate_lv1:
            return user.level.commission_rate_lv1
        if level == 2 and user.level.commission_rate_lv2:
            return user.level.commission_rate_lv2
    if not config:
        return Decimal("0.00")
    return config.default_rate_lv1 if level == 1 else config.default_rate_lv2
