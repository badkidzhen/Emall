from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.distribution.models import UserTeamStat

from .models import RewardDistributionRecord, RewardPool, RewardPoolRule


class RewardError(ValueError):
    pass


def distribute_pool(pool_id):
    with transaction.atomic():
        pool = RewardPool.objects.select_for_update().get(pk=pool_id)
        if not pool.enabled:
            raise RewardError("Reward pool is disabled.")
        if RewardDistributionRecord.objects.filter(pool=pool).exists():
            raise RewardError("Reward pool has already been distributed.")

        rule = pool.rules.first() or RewardPoolRule.objects.create(
            pool=pool,
            team_amount_weight=Decimal("0.50"),
            team_count_weight=Decimal("0.20"),
            personal_amount_weight=Decimal("0.30"),
        )
        candidates = list(UserTeamStat.objects.select_related("user").filter(team_order_amount__gte=pool.min_performance))
        scored = []
        for stat in candidates:
            score = (
                stat.team_order_amount * rule.team_amount_weight
                + Decimal(stat.team_count) * rule.team_count_weight
                + stat.team_commission * rule.personal_amount_weight
            )
            if score > 0:
                scored.append((stat.user, score))

        total_score = sum(score for _, score in scored)
        if total_score <= 0:
            raise RewardError("No eligible reward candidates.")

        max_amount = pool.amount * pool.max_user_ratio / Decimal("100.00")
        records = []
        for user, score in scored:
            amount = (pool.amount * score / total_score).quantize(Decimal("0.01"))
            amount = min(amount, max_amount)
            if amount > 0:
                records.append(
                    RewardDistributionRecord(
                        pool=pool,
                        user=user,
                        score=score,
                        amount=amount,
                        status=RewardDistributionRecord.Status.PENDING,
                    )
                )
        RewardDistributionRecord.objects.bulk_create(records)
    return list(RewardDistributionRecord.objects.filter(pool_id=pool_id))


def mark_pool_records_paid(pool_id):
    now = timezone.now()
    paid_count = 0
    with transaction.atomic():
        records = list(
            RewardDistributionRecord.objects.select_for_update().filter(
                pool_id=pool_id,
                status=RewardDistributionRecord.Status.PENDING,
            )
        )
        for record in records:
            record.status = RewardDistributionRecord.Status.PAID
            record.distributed_at = now
            record.save(update_fields=["status", "distributed_at", "updated_at"])
            from apps.finance.services import add_income

            add_income(
                record.user,
                record.amount,
                biz_type="reward_pool",
                biz_id=record.id,
                remark=f"pool:{record.pool_id}",
            )
            paid_count += 1
    return {"paid_count": paid_count}
