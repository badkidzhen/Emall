from collections import defaultdict
from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.conf import settings
from django.utils import timezone

from apps.catalog.models import ProductSku, StockLog

from .models import CartItem, InvoiceApplication, LogisticsRecord, Order, OrderAddress, OrderItem, PaymentRecord, RefundApplication
from .payment_gateways import PaymentGatewayError, get_payment_gateway


class OrderCreateError(ValueError):
    pass


def add_cart_item(user, sku_id, quantity, selected=True):
    sku = ProductSku.objects.select_related("product").get(pk=sku_id)
    if not sku.is_active:
        raise OrderCreateError("SKU is inactive.")
    if quantity < 1:
        raise OrderCreateError("Quantity must be greater than zero.")

    cart_item, created = CartItem.objects.get_or_create(
        user=user,
        sku=sku,
        defaults={"quantity": quantity, "selected": selected},
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.selected = selected
        cart_item.save(update_fields=["quantity", "selected", "updated_at"])
    return cart_item


def create_order(user, items=None, from_cart=False, remark="", coupon_id=None, price_overrides=None, address_id=None, address=None):
    price_overrides = price_overrides or {}
    normalized_items = normalize_order_items(user, items, from_cart)
    if not normalized_items:
        raise OrderCreateError("Order items are required.")
    address_snapshot = resolve_address_snapshot(user, address_id=address_id, address=address)

    sku_ids = list(normalized_items.keys())
    with transaction.atomic():
        skus = {
            sku.id: sku
            for sku in ProductSku.objects.select_for_update()
            .select_related("product")
            .filter(id__in=sku_ids)
        }
        missing_ids = set(sku_ids) - set(skus)
        if missing_ids:
            raise OrderCreateError(f"SKU not found: {sorted(missing_ids)}.")

        total_amount = Decimal("0.00")
        order = Order.objects.create(
            order_no=generate_order_no(),
            user=user,
            status=Order.Status.PENDING_PAYMENT,
            remark=remark,
            **address_snapshot,
        )

        order_items = []
        for sku_id, quantity in normalized_items.items():
            sku = skus[sku_id]
            if not sku.is_active or not sku.product.is_active:
                raise OrderCreateError(f"SKU {sku_id} is inactive.")
            if quantity < 1:
                raise OrderCreateError("Quantity must be greater than zero.")
            if sku.stock < quantity:
                raise OrderCreateError(f"SKU {sku.sku_code} has insufficient stock.")

            unit_price = price_overrides.get(sku_id, sku.price)
            line_amount = unit_price * quantity
            total_amount += line_amount
            before_stock = sku.stock
            sku.stock -= quantity
            sku.locked_stock += quantity
            sku.save(update_fields=["stock", "locked_stock", "updated_at"])
            StockLog.objects.create(
                sku=sku,
                change_type=StockLog.ChangeType.LOCK,
                quantity=quantity,
                before_stock=before_stock,
                after_stock=sku.stock,
                remark=f"order:{order.order_no}",
            )

            order_items.append(
                OrderItem(
                    order=order,
                    product=sku.product,
                    sku=sku,
                    product_title=sku.product.title,
                    sku_code=sku.sku_code,
                    spec_json=sku.specs,
                    price=unit_price,
                    quantity=quantity,
                    total_amount=line_amount,
                )
            )

        discount_amount = Decimal("0.00")
        user_coupon = None
        if coupon_id:
            from apps.marketing.models import UserCoupon
            from apps.marketing.services import calculate_coupon_discount, mark_coupon_used

            user_coupon = UserCoupon.objects.select_for_update().select_related("template").get(pk=coupon_id, user=user)
            discount_amount = calculate_coupon_discount(user_coupon, total_amount)

        OrderItem.objects.bulk_create(order_items)
        order.total_amount = total_amount
        order.discount_amount = discount_amount
        order.pay_amount = total_amount - discount_amount
        order.save(update_fields=["total_amount", "discount_amount", "pay_amount", "updated_at"])

        if user_coupon:
            mark_coupon_used(user_coupon)

        if from_cart:
            CartItem.objects.filter(user=user, sku_id__in=sku_ids).delete()

    return order


def ship_order(order_id, operator=None, company="", tracking_no="", traces=None):
    traces = traces or []
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if order.status != Order.Status.PENDING_SHIPMENT:
            raise OrderCreateError("Only pending shipment orders can be shipped.")
        order.status = Order.Status.PENDING_RECEIPT
        order.remark = append_remark(order.remark, f"shipped_by:{getattr(operator, 'id', 'system')}")
        order.save(update_fields=["status", "remark", "updated_at"])
        LogisticsRecord.objects.update_or_create(
            order=order,
            defaults={
                "company": company,
                "tracking_no": tracking_no,
                "shipped_at": timezone.now(),
                "traces": traces,
            },
        )
    return order


def receive_order(order_id, user=None):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if user and not user.is_staff and order.user_id != user.id:
            raise OrderCreateError("Order is not owned by current user.")
        if order.status != Order.Status.PENDING_RECEIPT:
            raise OrderCreateError("Only pending receipt orders can be received.")
        order.status = Order.Status.COMPLETED
        order.completed_at = timezone.now()
        order.save(update_fields=["status", "completed_at", "updated_at"])

    trigger_order_completed(order.id)
    return order


def complete_order(order_id, operator=None):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if order.status not in {Order.Status.PENDING_RECEIPT, Order.Status.PENDING_SHIPMENT}:
            raise OrderCreateError("Only paid fulfillment orders can be completed.")
        order.status = Order.Status.COMPLETED
        order.completed_at = timezone.now()
        order.remark = append_remark(order.remark, f"completed_by:{getattr(operator, 'id', 'system')}")
        order.save(update_fields=["status", "completed_at", "remark", "updated_at"])

    trigger_order_completed(order.id)
    return order


def trigger_order_completed(order_id):
    try:
        from apps.distribution.services import calculate_order_commission

        calculate_order_commission(order_id)
    except Exception:
        # The API should not fail order completion because a downstream reward calculation needs inspection.
        return


def cancel_order(order_id, user=None, reason=""):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if user and not user.is_staff and order.user_id != user.id:
            raise OrderCreateError("Order is not owned by current user.")
        if order.status != Order.Status.PENDING_PAYMENT:
            raise OrderCreateError("Only pending payment orders can be canceled.")

        items = list(OrderItem.objects.select_related("sku").filter(order=order))
        sku_ids = [item.sku_id for item in items]
        skus = ProductSku.objects.select_for_update().in_bulk(sku_ids)

        for item in items:
            sku = skus[item.sku_id]
            if sku.locked_stock < item.quantity:
                raise OrderCreateError(f"SKU {sku.sku_code} locked stock is inconsistent.")
            before_stock = sku.stock
            sku.stock += item.quantity
            sku.locked_stock -= item.quantity
            sku.save(update_fields=["stock", "locked_stock", "updated_at"])
            StockLog.objects.create(
                sku=sku,
                change_type=StockLog.ChangeType.UNLOCK,
                quantity=item.quantity,
                before_stock=before_stock,
                after_stock=sku.stock,
                remark=f"cancel_order:{order.order_no}",
            )

        order.status = Order.Status.CLOSED
        if reason:
            order.remark = append_remark(order.remark, reason)
        order.save(update_fields=["status", "remark", "updated_at"])

    return order


def close_expired_pending_orders(timeout_minutes=None, limit=100):
    if timeout_minutes is None:
        timeout_minutes = settings.ORDER_PAYMENT_TIMEOUT_MINUTES
    cutoff = timezone.now() - timezone.timedelta(minutes=timeout_minutes)
    order_ids = list(
        Order.objects.filter(status=Order.Status.PENDING_PAYMENT, created_at__lte=cutoff)
        .order_by("created_at")
        .values_list("id", flat=True)[:limit]
    )

    closed_count = 0
    failed = []
    for order_id in order_ids:
        try:
            cancel_order(order_id, reason="payment_timeout")
            closed_count += 1
        except OrderCreateError as exc:
            failed.append({"order_id": order_id, "error": str(exc)})

    return {"closed_count": closed_count, "failed": failed}


def confirm_order_paid(order_id, payment_no, paid_amount, channel=PaymentRecord.Channel.MOCK, raw_payload=None):
    raw_payload = raw_payload or {}

    with transaction.atomic():
        existing_payment = PaymentRecord.objects.select_for_update().filter(payment_no=payment_no).first()
        if existing_payment:
            if existing_payment.order_id != int(order_id):
                raise OrderCreateError("Payment number is already used by another order.")
            if existing_payment.status == PaymentRecord.Status.SUCCESS:
                return existing_payment.order, existing_payment, False
            if existing_payment.status != PaymentRecord.Status.PENDING:
                raise OrderCreateError("Only pending payments can be confirmed as paid.")

        order = Order.objects.select_for_update().get(pk=order_id)
        if order.status != Order.Status.PENDING_PAYMENT:
            raise OrderCreateError("Only pending payment orders can be confirmed as paid.")
        if paid_amount != order.pay_amount:
            raise OrderCreateError("Paid amount does not match order pay amount.")

        items = list(OrderItem.objects.select_related("sku").filter(order=order))
        sku_ids = [item.sku_id for item in items]
        skus = ProductSku.objects.select_for_update().in_bulk(sku_ids)

        for item in items:
            sku = skus[item.sku_id]
            if sku.locked_stock < item.quantity:
                raise OrderCreateError(f"SKU {sku.sku_code} locked stock is inconsistent.")
            sku.locked_stock -= item.quantity
            sku.save(update_fields=["locked_stock", "updated_at"])
            StockLog.objects.create(
                sku=sku,
                change_type=StockLog.ChangeType.OUT,
                quantity=item.quantity,
                before_stock=sku.stock,
                after_stock=sku.stock,
                remark=f"payment:{order.order_no}",
            )

        paid_at = timezone.now()
        if existing_payment:
            payment = existing_payment
            payment.channel = channel
            payment.amount = paid_amount
            payment.status = PaymentRecord.Status.SUCCESS
            payment.paid_at = paid_at
            payment.raw_payload = raw_payload
            payment.save(update_fields=["channel", "amount", "status", "paid_at", "raw_payload", "updated_at"])
            created = False
        else:
            payment = PaymentRecord.objects.create(
                order=order,
                payment_no=payment_no,
                channel=channel,
                amount=paid_amount,
                status=PaymentRecord.Status.SUCCESS,
                paid_at=paid_at,
                raw_payload=raw_payload,
            )
            created = True
        order.status = Order.Status.PENDING_SHIPMENT
        order.paid_at = paid_at
        order.save(update_fields=["status", "paid_at", "updated_at"])

    return order, payment, created


def create_payment_request(order_id, channel=PaymentRecord.Channel.MOCK, client_ip="", openid=""):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if order.status != Order.Status.PENDING_PAYMENT:
            raise OrderCreateError("Only pending payment orders can create payment requests.")
        payment_no = generate_payment_no()
        gateway = get_payment_gateway(channel)
        try:
            gateway_result = gateway.create_payment(
                order=order,
                payment_no=payment_no,
                client_ip=client_ip,
                openid=openid,
            )
        except PaymentGatewayError:
            raise

        payment = PaymentRecord.objects.create(
            order=order,
            payment_no=payment_no,
            channel=channel,
            amount=order.pay_amount,
            status=PaymentRecord.Status.PENDING,
            gateway_trade_no=gateway_result.gateway_trade_no,
            raw_payload=gateway_result.payload,
        )
    return payment, gateway_result.payload


def apply_refund(user, order_id, amount, reason, refund_type=RefundApplication.RefundType.REFUND_ONLY):
    if amount <= 0:
        raise OrderCreateError("Refund amount must be positive.")
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if user and not user.is_staff and order.user_id != user.id:
            raise OrderCreateError("Order is not owned by current user.")
        if order.status not in {Order.Status.PENDING_SHIPMENT, Order.Status.PENDING_RECEIPT, Order.Status.COMPLETED}:
            raise OrderCreateError("Only paid orders can apply for refund.")
        refunded_total = sum(
            item.amount
            for item in RefundApplication.objects.filter(
                order=order,
                status__in=[
                    RefundApplication.Status.PENDING,
                    RefundApplication.Status.APPROVED,
                    RefundApplication.Status.REFUNDING,
                    RefundApplication.Status.REFUNDED,
                ],
            )
        )
        if refunded_total + amount > order.pay_amount:
            raise OrderCreateError("Refund amount exceeds order payable amount.")
        refund = RefundApplication.objects.create(
            refund_no=generate_refund_no(),
            order=order,
            user=order.user,
            refund_type=refund_type,
            reason=reason,
            amount=amount,
        )
        order.status = Order.Status.REFUNDING
        order.save(update_fields=["status", "updated_at"])
    return refund


def approve_refund(refund_id, remark="", operator=None):
    with transaction.atomic():
        refund = RefundApplication.objects.select_for_update().select_related("order").get(pk=refund_id)
        if refund.status != RefundApplication.Status.PENDING:
            raise OrderCreateError("Only pending refunds can be approved.")
        refund.status = RefundApplication.Status.APPROVED
        refund.audit_remark = remark
        refund.save(update_fields=["status", "audit_remark", "updated_at"])
    return refund


def reject_refund(refund_id, remark="", operator=None):
    with transaction.atomic():
        refund = RefundApplication.objects.select_for_update().select_related("order").get(pk=refund_id)
        if refund.status != RefundApplication.Status.PENDING:
            raise OrderCreateError("Only pending refunds can be rejected.")
        refund.status = RefundApplication.Status.REJECTED
        refund.audit_remark = remark
        refund.save(update_fields=["status", "audit_remark", "updated_at"])
        restore_order_status_after_refund(refund.order)
    return refund


def request_refund_to_gateway(refund_id, operator=None):
    with transaction.atomic():
        refund = RefundApplication.objects.select_for_update().select_related("order").get(pk=refund_id)
        if refund.status != RefundApplication.Status.APPROVED:
            raise OrderCreateError("Only approved refunds can request gateway refund.")
        payment = (
            PaymentRecord.objects.select_for_update()
            .filter(order=refund.order, status=PaymentRecord.Status.SUCCESS)
            .order_by("-paid_at")
            .first()
        )
        if not payment:
            raise OrderCreateError("Successful payment record is required before refund.")
        gateway = get_payment_gateway(payment.channel)
        gateway_result = gateway.request_refund(refund=refund, payment=payment)
        refund.status = RefundApplication.Status.REFUNDING
        refund.gateway_refund_no = gateway_result.gateway_trade_no
        refund.requested_at = timezone.now()
        refund.raw_payload = gateway_result.payload
        refund.save(update_fields=["status", "gateway_refund_no", "requested_at", "raw_payload", "updated_at"])
    return refund


def mark_refund_success(refund_id, remark="", raw_payload=None):
    raw_payload = raw_payload or {}
    with transaction.atomic():
        refund = RefundApplication.objects.select_for_update().select_related("order").get(pk=refund_id)
        if refund.status not in {RefundApplication.Status.APPROVED, RefundApplication.Status.REFUNDING}:
            raise OrderCreateError("Only approved/refunding refunds can be marked refunded.")
        refund.status = RefundApplication.Status.REFUNDED
        refund.audit_remark = remark or refund.audit_remark
        refund.refunded_at = timezone.now()
        if raw_payload:
            refund.raw_payload = raw_payload
        refund.save(update_fields=["status", "audit_remark", "refunded_at", "raw_payload", "updated_at"])
        total_refunded = sum(
            item.amount for item in RefundApplication.objects.filter(order=refund.order, status=RefundApplication.Status.REFUNDED)
        )
        if total_refunded >= refund.order.pay_amount:
            refund.order.status = Order.Status.REFUNDED
        else:
            restore_order_status_after_refund(refund.order)
        refund.order.save(update_fields=["status", "updated_at"])
    return refund


def apply_invoice(user, order_id, invoice_type, title, tax_no="", email="", content="商品明细"):
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if user and not user.is_staff and order.user_id != user.id:
            raise OrderCreateError("Order is not owned by current user.")
        if order.status == Order.Status.PENDING_PAYMENT:
            raise OrderCreateError("Pending payment orders cannot apply invoice.")
        invoice, _ = InvoiceApplication.objects.update_or_create(
            order=order,
            defaults={
                "user": order.user,
                "invoice_type": invoice_type,
                "title": title,
                "tax_no": tax_no,
                "email": email,
                "content": content,
                "amount": order.pay_amount,
                "status": InvoiceApplication.Status.PENDING,
            },
        )
    return invoice


def issue_invoice(invoice_id, remark=""):
    with transaction.atomic():
        invoice = InvoiceApplication.objects.select_for_update().get(pk=invoice_id)
        if invoice.status != InvoiceApplication.Status.PENDING:
            raise OrderCreateError("Only pending invoices can be issued.")
        invoice.status = InvoiceApplication.Status.ISSUED
        invoice.audit_remark = remark
        invoice.issued_at = timezone.now()
        invoice.save(update_fields=["status", "audit_remark", "issued_at", "updated_at"])
    return invoice


def normalize_order_items(user, items, from_cart):
    normalized = defaultdict(int)
    if from_cart:
        cart_items = CartItem.objects.filter(user=user, selected=True).values("sku_id", "quantity")
        for item in cart_items:
            normalized[item["sku_id"]] += item["quantity"]
        return dict(normalized)

    for item in items or []:
        normalized[int(item["sku_id"])] += int(item["quantity"])
    return dict(normalized)


def resolve_address_snapshot(user, address_id=None, address=None):
    if address_id:
        address_obj = OrderAddress.objects.get(pk=address_id, user=user)
        return {
            "receiver_name": address_obj.receiver_name,
            "receiver_mobile": address_obj.receiver_mobile,
            "province": address_obj.province,
            "city": address_obj.city,
            "district": address_obj.district,
            "address_detail": address_obj.address_detail,
            "postal_code": address_obj.postal_code,
        }
    address = address or {}
    return {
        "receiver_name": address.get("receiver_name", ""),
        "receiver_mobile": address.get("receiver_mobile", ""),
        "province": address.get("province", ""),
        "city": address.get("city", ""),
        "district": address.get("district", ""),
        "address_detail": address.get("address_detail", ""),
        "postal_code": address.get("postal_code", ""),
    }


def generate_order_no():
    timestamp = timezone.localtime().strftime("%Y%m%d%H%M%S")
    suffix = uuid4().hex[:8].upper()
    return f"EM{timestamp}{suffix}"


def generate_payment_no():
    timestamp = timezone.localtime().strftime("%Y%m%d%H%M%S")
    suffix = uuid4().hex[:8].upper()
    return f"PAY{timestamp}{suffix}"


def generate_refund_no():
    timestamp = timezone.localtime().strftime("%Y%m%d%H%M%S")
    suffix = uuid4().hex[:8].upper()
    return f"RF{timestamp}{suffix}"


def restore_order_status_after_refund(order):
    has_active_refunds = RefundApplication.objects.filter(
        order=order,
        status__in=[
            RefundApplication.Status.PENDING,
            RefundApplication.Status.APPROVED,
            RefundApplication.Status.REFUNDING,
        ],
    ).exists()
    if has_active_refunds:
        order.status = Order.Status.REFUNDING
    elif order.completed_at:
        order.status = Order.Status.COMPLETED
    elif order.paid_at:
        order.status = Order.Status.PENDING_SHIPMENT
    else:
        order.status = Order.Status.PENDING_PAYMENT
    order.save(update_fields=["status", "updated_at"])
    return order


def append_remark(existing, reason):
    if not existing:
        return reason
    return f"{existing}; {reason}"
