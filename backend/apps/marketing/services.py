from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from .models import CouponTemplate, GroupBuyingActivity, SeckillActivity, UserCoupon
from .activity_models import ActivityPurchaseRecord


class MarketingError(ValueError):
    pass


def claim_coupon(user, template_id):
    now = timezone.now()
    with transaction.atomic():
        template = CouponTemplate.objects.select_for_update().get(pk=template_id)
        if template.started_at > now or template.ended_at < now:
            raise MarketingError("Coupon is not claimable now.")
        claimed_total = UserCoupon.objects.filter(template=template).count()
        if template.total_quantity and claimed_total >= template.total_quantity:
            raise MarketingError("Coupon is sold out.")
        claimed_by_user = UserCoupon.objects.filter(user=user, template=template).count()
        if claimed_by_user >= template.per_user_limit:
            raise MarketingError("User coupon claim limit exceeded.")

        coupon = UserCoupon.objects.create(
            user=user,
            template=template,
            status=UserCoupon.Status.UNUSED,
            valid_from=now,
            valid_to=now + timezone.timedelta(days=template.valid_days),
        )
    return coupon


def calculate_coupon_discount(user_coupon, subtotal):
    now = timezone.now()
    if user_coupon.status != UserCoupon.Status.UNUSED:
        raise MarketingError("Coupon is not unused.")
    if user_coupon.valid_from > now or user_coupon.valid_to < now:
        raise MarketingError("Coupon is expired.")

    template = user_coupon.template
    if subtotal < template.threshold_amount:
        raise MarketingError("Order amount does not meet coupon threshold.")

    if template.coupon_type == CouponTemplate.CouponType.DISCOUNT:
        discount = subtotal * (Decimal("1.00") - template.discount_rate)
    else:
        discount = template.discount_amount
    if discount < 0:
        return Decimal("0.00")
    return min(discount.quantize(Decimal("0.01")), subtotal)


def mark_coupon_used(user_coupon):
    user_coupon.status = UserCoupon.Status.USED
    user_coupon.used_at = timezone.now()
    user_coupon.save(update_fields=["status", "used_at", "updated_at"])
    return user_coupon


def expire_coupons(limit=1000):
    now = timezone.now()
    ids = list(
        UserCoupon.objects.filter(status=UserCoupon.Status.UNUSED, valid_to__lt=now)
        .order_by("valid_to")
        .values_list("id", flat=True)[:limit]
    )
    updated = UserCoupon.objects.filter(id__in=ids).update(status=UserCoupon.Status.EXPIRED, updated_at=now)
    return {"expired_count": updated}


def purchase_group_activity(user, activity_id, quantity):
    with transaction.atomic():
        activity = GroupBuyingActivity.objects.select_for_update().select_related("sku").get(pk=activity_id)
        validate_activity_window(activity)
        if activity.stock < quantity:
            raise MarketingError("Group activity stock is insufficient.")
        activity.stock -= quantity
        activity.save(update_fields=["stock", "updated_at"])

        from apps.orders.services import create_order

        order = create_order(
            user=user,
            items=[{"sku_id": activity.sku_id, "quantity": quantity}],
            price_overrides={activity.sku_id: activity.group_price},
            remark=f"group_activity:{activity.id}",
        )
        ActivityPurchaseRecord.objects.create(
            user=user,
            activity_type=ActivityPurchaseRecord.ActivityType.GROUP,
            activity_id=activity.id,
            order=order,
            quantity=quantity,
        )
    return order


def purchase_seckill_activity(user, activity_id, quantity):
    with transaction.atomic():
        activity = SeckillActivity.objects.select_for_update().select_related("sku").get(pk=activity_id)
        validate_activity_window(activity)
        purchased = (
            ActivityPurchaseRecord.objects.filter(
                user=user,
                activity_type=ActivityPurchaseRecord.ActivityType.SECKILL,
                activity_id=activity.id,
            ).aggregate(total=Sum("quantity"))["total"]
            or 0
        )
        if purchased + quantity > activity.per_user_limit:
            raise MarketingError("Seckill per-user limit exceeded.")
        if activity.stock < quantity:
            raise MarketingError("Seckill stock is insufficient.")
        activity.stock -= quantity
        activity.save(update_fields=["stock", "updated_at"])

        from apps.orders.services import create_order

        order = create_order(
            user=user,
            items=[{"sku_id": activity.sku_id, "quantity": quantity}],
            price_overrides={activity.sku_id: activity.seckill_price},
            remark=f"seckill_activity:{activity.id}",
        )
        ActivityPurchaseRecord.objects.create(
            user=user,
            activity_type=ActivityPurchaseRecord.ActivityType.SECKILL,
            activity_id=activity.id,
            order=order,
            quantity=quantity,
        )
    return order


def validate_activity_window(activity):
    now = timezone.now()
    if not activity.enabled:
        raise MarketingError("Activity is disabled.")
    if activity.started_at > now or activity.ended_at < now:
        raise MarketingError("Activity is not active now.")
