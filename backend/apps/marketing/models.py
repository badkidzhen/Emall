from django.conf import settings
from django.db import models

from apps.catalog.models import Product, ProductCategory, ProductSku
from apps.core.models import TimeStampedModel

from .activity_models import ActivityPurchaseRecord  # noqa: F401


class CouponTemplate(TimeStampedModel):
    class CouponType(models.TextChoices):
        FULL_REDUCTION = "full_reduction", "满减券"
        DISCOUNT = "discount", "折扣券"
        NEW_USER = "new_user", "新人券"
        PRODUCT = "product", "指定商品券"
        CATEGORY = "category", "指定分类券"

    name = models.CharField("优惠券名称", max_length=100)
    coupon_type = models.CharField("优惠券类型", max_length=32, choices=CouponType.choices)
    threshold_amount = models.DecimalField("使用门槛", max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField("优惠金额", max_digits=12, decimal_places=2, default=0)
    discount_rate = models.DecimalField("折扣比例", max_digits=4, decimal_places=2, default=1)
    total_quantity = models.PositiveIntegerField("发行数量", default=0)
    per_user_limit = models.PositiveIntegerField("每人限领", default=1)
    started_at = models.DateTimeField("领取开始时间")
    ended_at = models.DateTimeField("领取结束时间")
    valid_days = models.PositiveIntegerField("领取后有效天数", default=7)
    products = models.ManyToManyField(Product, verbose_name="适用商品", blank=True)
    categories = models.ManyToManyField(ProductCategory, verbose_name="适用分类", blank=True)

    class Meta:
        db_table = "coupon_template"
        verbose_name = "优惠券模板"
        verbose_name_plural = verbose_name


class UserCoupon(TimeStampedModel):
    class Status(models.TextChoices):
        UNUSED = "unused", "未使用"
        USED = "used", "已使用"
        EXPIRED = "expired", "已过期"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户", on_delete=models.CASCADE, related_name="coupons")
    template = models.ForeignKey(CouponTemplate, verbose_name="优惠券模板", on_delete=models.PROTECT)
    status = models.CharField("状态", max_length=20, choices=Status.choices, default=Status.UNUSED)
    valid_from = models.DateTimeField("有效开始时间")
    valid_to = models.DateTimeField("有效结束时间")
    used_at = models.DateTimeField("使用时间", null=True, blank=True)

    class Meta:
        db_table = "user_coupon"
        indexes = [
            models.Index(fields=["user", "status"], name="idx_coupon_user_status"),
        ]
        verbose_name = "用户优惠券"
        verbose_name_plural = verbose_name


class GroupBuyingActivity(TimeStampedModel):
    name = models.CharField("团购名称", max_length=100)
    sku = models.ForeignKey(ProductSku, verbose_name="团购 SKU", on_delete=models.PROTECT)
    group_price = models.DecimalField("团购价", max_digits=12, decimal_places=2)
    min_members = models.PositiveIntegerField("成团人数", default=2)
    stock = models.PositiveIntegerField("团购库存", default=0)
    started_at = models.DateTimeField("开始时间")
    ended_at = models.DateTimeField("结束时间")
    enabled = models.BooleanField("是否启用", default=True)

    class Meta:
        db_table = "group_buying_activity"
        verbose_name = "团购活动"
        verbose_name_plural = verbose_name


class SeckillActivity(TimeStampedModel):
    name = models.CharField("秒杀名称", max_length=100)
    sku = models.ForeignKey(ProductSku, verbose_name="秒杀 SKU", on_delete=models.PROTECT)
    seckill_price = models.DecimalField("秒杀价", max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField("秒杀库存", default=0)
    per_user_limit = models.PositiveIntegerField("每人限购", default=1)
    started_at = models.DateTimeField("开始时间")
    ended_at = models.DateTimeField("结束时间")
    enabled = models.BooleanField("是否启用", default=True)

    class Meta:
        db_table = "seckill_activity"
        verbose_name = "秒杀活动"
        verbose_name_plural = verbose_name
