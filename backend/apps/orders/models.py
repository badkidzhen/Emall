from django.conf import settings
from django.db import models

from apps.catalog.models import Product, ProductSku
from apps.core.models import TimeStampedModel

from .payment_models import PaymentRecord  # noqa: F401


class CartItem(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户", on_delete=models.CASCADE, related_name="cart_items")
    sku = models.ForeignKey(ProductSku, verbose_name="SKU", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("数量", default=1)
    selected = models.BooleanField("是否选中", default=True)

    class Meta:
        db_table = "cart_item"
        constraints = [
            models.UniqueConstraint(fields=["user", "sku"], name="uk_cart_user_sku"),
        ]
        verbose_name = "购物车"
        verbose_name_plural = verbose_name


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "待付款"
        PENDING_SHIPMENT = "pending_shipment", "待发货"
        PENDING_RECEIPT = "pending_receipt", "待收货"
        COMPLETED = "completed", "已完成"
        REFUNDING = "refunding", "售后中"
        REFUNDED = "refunded", "已退款"
        CLOSED = "closed", "已关闭"

    order_no = models.CharField("订单号", max_length=64, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户", on_delete=models.PROTECT, related_name="orders")
    status = models.CharField("订单状态", max_length=32, choices=Status.choices, default=Status.PENDING_PAYMENT)
    total_amount = models.DecimalField("商品总额", max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField("优惠金额", max_digits=12, decimal_places=2, default=0)
    pay_amount = models.DecimalField("实付金额", max_digits=12, decimal_places=2, default=0)
    paid_at = models.DateTimeField("支付时间", null=True, blank=True)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)
    remark = models.CharField("备注", max_length=255, blank=True, default="")
    receiver_name = models.CharField("Receiver Name", max_length=50, blank=True, default="")
    receiver_mobile = models.CharField("Receiver Mobile", max_length=20, blank=True, default="")
    province = models.CharField("Province", max_length=50, blank=True, default="")
    city = models.CharField("City", max_length=50, blank=True, default="")
    district = models.CharField("District", max_length=50, blank=True, default="")
    address_detail = models.CharField("Address Detail", max_length=255, blank=True, default="")
    postal_code = models.CharField("Postal Code", max_length=20, blank=True, default="")

    class Meta:
        db_table = "order"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_no"], name="idx_order_no"),
            models.Index(fields=["user", "status"], name="idx_order_user_status"),
        ]
        verbose_name = "订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_no


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, verbose_name="订单", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.PROTECT)
    sku = models.ForeignKey(ProductSku, verbose_name="SKU", on_delete=models.PROTECT)
    product_title = models.CharField("商品标题快照", max_length=200)
    sku_code = models.CharField("SKU 编码快照", max_length=64)
    spec_json = models.JSONField("规格快照", default=dict, blank=True)
    price = models.DecimalField("单价", max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField("数量")
    total_amount = models.DecimalField("小计", max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_item"
        verbose_name = "订单商品"
        verbose_name_plural = verbose_name


class OrderAddress(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.CASCADE, related_name="addresses")
    receiver_name = models.CharField("Receiver Name", max_length=50)
    receiver_mobile = models.CharField("Receiver Mobile", max_length=20)
    province = models.CharField("Province", max_length=50, blank=True, default="")
    city = models.CharField("City", max_length=50, blank=True, default="")
    district = models.CharField("District", max_length=50, blank=True, default="")
    address_detail = models.CharField("Address Detail", max_length=255)
    postal_code = models.CharField("Postal Code", max_length=20, blank=True, default="")
    is_default = models.BooleanField("Is Default", default=False)

    class Meta:
        db_table = "order_address"
        ordering = ["-is_default", "-updated_at"]
        indexes = [models.Index(fields=["user", "is_default"], name="idx_addr_user_default")]
        verbose_name = "Order Address"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.receiver_name} {self.receiver_mobile}"


class InvoiceApplication(TimeStampedModel):
    class InvoiceType(models.TextChoices):
        PERSONAL = "personal", "Personal"
        COMPANY = "company", "Company"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ISSUED = "issued", "Issued"
        REJECTED = "rejected", "Rejected"

    order = models.OneToOneField(Order, verbose_name="Order", on_delete=models.PROTECT, related_name="invoice")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.PROTECT, related_name="invoices")
    invoice_type = models.CharField("Invoice Type", max_length=20, choices=InvoiceType.choices, default=InvoiceType.PERSONAL)
    title = models.CharField("Title", max_length=100)
    tax_no = models.CharField("Tax No", max_length=50, blank=True, default="")
    email = models.EmailField("Email", blank=True, default="")
    content = models.CharField("Content", max_length=100, blank=True, default="商品明细")
    amount = models.DecimalField("Amount", max_digits=12, decimal_places=2, default=0)
    status = models.CharField("Status", max_length=20, choices=Status.choices, default=Status.PENDING)
    audit_remark = models.CharField("Audit Remark", max_length=255, blank=True, default="")
    issued_at = models.DateTimeField("Issued At", null=True, blank=True)

    class Meta:
        db_table = "invoice_application"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"], name="idx_invoice_user_status")]
        verbose_name = "Invoice Application"
        verbose_name_plural = verbose_name


class LogisticsRecord(TimeStampedModel):
    order = models.OneToOneField(Order, verbose_name="Order", on_delete=models.PROTECT, related_name="logistics")
    company = models.CharField("Company", max_length=100, blank=True, default="")
    tracking_no = models.CharField("Tracking No", max_length=100, blank=True, default="")
    shipped_at = models.DateTimeField("Shipped At", null=True, blank=True)
    delivered_at = models.DateTimeField("Delivered At", null=True, blank=True)
    traces = models.JSONField("Traces", default=list, blank=True)
    raw_payload = models.JSONField("Raw Payload", default=dict, blank=True)

    class Meta:
        db_table = "logistics_record"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["tracking_no"], name="idx_logistics_tracking")]
        verbose_name = "Logistics Record"
        verbose_name_plural = verbose_name


class RefundApplication(TimeStampedModel):
    class RefundType(models.TextChoices):
        REFUND_ONLY = "refund_only", "Refund Only"
        RETURN_AND_REFUND = "return_and_refund", "Return And Refund"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REFUNDING = "refunding", "Refunding"
        REFUNDED = "refunded", "Refunded"
        CLOSED = "closed", "Closed"

    refund_no = models.CharField("Refund No", max_length=64, unique=True)
    order = models.ForeignKey(Order, verbose_name="Order", on_delete=models.PROTECT, related_name="refund_applications")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.PROTECT, related_name="refund_applications")
    refund_type = models.CharField("Refund Type", max_length=30, choices=RefundType.choices, default=RefundType.REFUND_ONLY)
    reason = models.CharField("Reason", max_length=255)
    amount = models.DecimalField("Amount", max_digits=12, decimal_places=2)
    status = models.CharField("Status", max_length=20, choices=Status.choices, default=Status.PENDING)
    audit_remark = models.CharField("Audit Remark", max_length=255, blank=True, default="")
    gateway_refund_no = models.CharField("Gateway Refund No", max_length=128, blank=True, default="")
    requested_at = models.DateTimeField("Requested At", null=True, blank=True)
    refunded_at = models.DateTimeField("Refunded At", null=True, blank=True)
    raw_payload = models.JSONField("Raw Payload", default=dict, blank=True)

    class Meta:
        db_table = "refund_application"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "status"], name="idx_refund_order_status"),
            models.Index(fields=["user", "status"], name="idx_refund_user_status"),
            models.Index(fields=["refund_no"], name="idx_refund_no"),
        ]
        verbose_name = "Refund Application"
        verbose_name_plural = verbose_name
