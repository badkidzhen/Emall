from rest_framework import serializers

from .models import CartItem, InvoiceApplication, LogisticsRecord, Order, OrderAddress, OrderItem, PaymentRecord, RefundApplication


def format_spec_text(specs):
    if not specs:
        return ""
    if isinstance(specs, dict):
        return " / ".join(f"{key}: {value}" for key, value in specs.items() if str(value).strip())
    return str(specs)


class CartItemSerializer(serializers.ModelSerializer):
    sku_code = serializers.CharField(source="sku.sku_code", read_only=True)
    product_title = serializers.CharField(source="sku.product.title", read_only=True)
    spec_text = serializers.SerializerMethodField()
    price = serializers.DecimalField(source="sku.price", max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = "__all__"
        read_only_fields = ["user"]

    def get_spec_text(self, obj):
        return format_spec_text(getattr(obj.sku, "specs", {}) or {})


class CartAddSerializer(serializers.Serializer):
    sku = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(required=False, default=True)


class OrderItemSerializer(serializers.ModelSerializer):
    spec_text = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = "__all__"

    def get_spec_text(self, obj):
        return format_spec_text(obj.spec_json or {})


class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = "__all__"
        read_only_fields = ["user"]


class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = "__all__"


class LogisticsRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogisticsRecord
        fields = "__all__"


class InvoiceApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceApplication
        fields = "__all__"
        read_only_fields = ["order", "user", "amount", "status", "audit_remark", "issued_at"]


class RefundApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundApplication
        fields = "__all__"
        read_only_fields = [
            "refund_no",
            "user",
            "status",
            "audit_remark",
            "gateway_refund_no",
            "requested_at",
            "refunded_at",
            "raw_payload",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment_records = PaymentRecordSerializer(many=True, read_only=True)
    refund_applications = RefundApplicationSerializer(many=True, read_only=True)
    logistics = LogisticsRecordSerializer(read_only=True)
    invoice = InvoiceApplicationSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = [
            "order_no",
            "user",
            "status",
            "total_amount",
            "discount_amount",
            "pay_amount",
            "paid_at",
            "completed_at",
        ]


class CreateOrderItemSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    items = CreateOrderItemSerializer(many=True, required=False)
    from_cart = serializers.BooleanField(required=False, default=False)
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")
    coupon_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    address_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    address = serializers.DictField(required=False)

    def validate(self, attrs):
        from_cart = attrs.get("from_cart", False)
        items = attrs.get("items") or []
        if not from_cart and not items:
            raise serializers.ValidationError("items is required when from_cart is false.")
        return attrs


class CancelOrderSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")


class ConfirmPaidSerializer(serializers.Serializer):
    payment_no = serializers.CharField(max_length=128)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    channel = serializers.ChoiceField(choices=PaymentRecord.Channel.choices, required=False, default=PaymentRecord.Channel.MOCK)
    raw_payload = serializers.JSONField(required=False, default=dict)


class CreatePaymentSerializer(serializers.Serializer):
    channel = serializers.ChoiceField(choices=PaymentRecord.Channel.choices, required=False, default=PaymentRecord.Channel.MOCK)
    client_ip = serializers.IPAddressField(required=False, allow_null=True)
    openid = serializers.CharField(required=False, allow_blank=True, max_length=128, default="")


class ShipOrderSerializer(serializers.Serializer):
    company = serializers.CharField(required=False, allow_blank=True, max_length=100, default="")
    tracking_no = serializers.CharField(required=False, allow_blank=True, max_length=100, default="")
    traces = serializers.JSONField(required=False, default=list)


class ApplyRefundSerializer(serializers.Serializer):
    refund_type = serializers.ChoiceField(
        choices=RefundApplication.RefundType.choices,
        required=False,
        default=RefundApplication.RefundType.REFUND_ONLY,
    )
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    reason = serializers.CharField(max_length=255)


class RefundAuditSerializer(serializers.Serializer):
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")


class IssueInvoiceSerializer(serializers.Serializer):
    audit_remark = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")


class EmptyActionSerializer(serializers.Serializer):
    pass
