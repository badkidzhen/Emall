from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import CartItem, InvoiceApplication, LogisticsRecord, Order, OrderAddress, RefundApplication
from .payment_gateways import PaymentGatewayError
from .serializers import (
    ApplyRefundSerializer,
    CancelOrderSerializer,
    CartAddSerializer,
    CartItemSerializer,
    ConfirmPaidSerializer,
    CreateOrderSerializer,
    CreatePaymentSerializer,
    EmptyActionSerializer,
    InvoiceApplicationSerializer,
    IssueInvoiceSerializer,
    LogisticsRecordSerializer,
    OrderSerializer,
    OrderAddressSerializer,
    PaymentRecordSerializer,
    RefundApplicationSerializer,
    RefundAuditSerializer,
    ShipOrderSerializer,
)
from .services import (
    OrderCreateError,
    add_cart_item,
    apply_invoice,
    apply_refund,
    approve_refund,
    cancel_order,
    complete_order,
    confirm_order_paid,
    create_payment_request,
    create_order,
    issue_invoice,
    mark_refund_success,
    receive_order,
    reject_refund,
    request_refund_to_gateway,
    ship_order,
)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.select_related("user", "sku", "sku__product").all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "selected"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return queryset.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def add(self, request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cart_item = add_cart_item(
                user=request.user,
                sku_id=serializer.validated_data["sku"],
                quantity=serializer.validated_data["quantity"],
                selected=serializer.validated_data["selected"],
            )
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


class OrderAddressViewSet(viewsets.ModelViewSet):
    queryset = OrderAddress.objects.select_related("user").all()
    serializer_class = OrderAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        address = serializer.save(user=self.request.user)
        if address.is_default:
            OrderAddress.objects.filter(user=self.request.user).exclude(pk=address.pk).update(is_default=False)

    def perform_update(self, serializer):
        address = serializer.save()
        if address.is_default:
            OrderAddress.objects.filter(user=address.user).exclude(pk=address.pk).update(is_default=False)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user").prefetch_related("items").all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["order_no", "user__mobile", "user__username"]
    filterset_fields = ["status", "user"]
    ordering_fields = ["created_at", "pay_amount"]

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy"}:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return queryset.filter(user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        return self.create_order_response(request)

    @action(detail=False, methods=["post"], url_path="create")
    def create_order(self, request):
        return self.create_order_response(request)

    def create_order_response(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = create_order(
                user=request.user,
                items=serializer.validated_data.get("items"),
                from_cart=serializer.validated_data["from_cart"],
                remark=serializer.validated_data["remark"],
                coupon_id=serializer.validated_data.get("coupon_id"),
                address_id=serializer.validated_data.get("address_id"),
                address=serializer.validated_data.get("address"),
            )
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="create-payment")
    def create_payment(self, request, pk=None):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment, payload = create_payment_request(
                order_id=self.get_object().id,
                channel=serializer.validated_data["channel"],
                client_ip=serializer.validated_data.get("client_ip") or request.META.get("REMOTE_ADDR", ""),
                openid=serializer.validated_data.get("openid", ""),
            )
        except (OrderCreateError, PaymentGatewayError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"payment": PaymentRecordSerializer(payment).data, "pay_params": payload}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = cancel_order(
                order_id=self.get_object().id,
                user=request.user,
                reason=serializer.validated_data["reason"],
            )
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"], url_path="confirm-paid", permission_classes=[IsAdminUser])
    def confirm_paid(self, request, pk=None):
        serializer = ConfirmPaidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order, payment, created = confirm_order_paid(
                order_id=self.get_object().id,
                payment_no=serializer.validated_data["payment_no"],
                paid_amount=serializer.validated_data["paid_amount"],
                channel=serializer.validated_data["channel"],
                raw_payload=serializer.validated_data["raw_payload"],
            )
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "created": created,
                "order": OrderSerializer(order).data,
                "payment": PaymentRecordSerializer(payment).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def ship(self, request, pk=None):
        serializer = ShipOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = ship_order(
                self.get_object().id,
                operator=request.user,
                company=serializer.validated_data["company"],
                tracking_no=serializer.validated_data["tracking_no"],
                traces=serializer.validated_data["traces"],
            )
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        EmptyActionSerializer(data=request.data).is_valid(raise_exception=True)
        try:
            order = receive_order(self.get_object().id, user=request.user)
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"], url_path="apply-refund")
    def apply_refund(self, request, pk=None):
        serializer = ApplyRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refund = apply_refund(
                user=request.user,
                order_id=self.get_object().id,
                amount=serializer.validated_data["amount"],
                reason=serializer.validated_data["reason"],
                refund_type=serializer.validated_data["refund_type"],
            )
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundApplicationSerializer(refund).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="apply-invoice")
    def apply_invoice(self, request, pk=None):
        serializer = InvoiceApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = apply_invoice(
                user=request.user,
                order_id=self.get_object().id,
                invoice_type=serializer.validated_data["invoice_type"],
                title=serializer.validated_data["title"],
                tax_no=serializer.validated_data.get("tax_no", ""),
                email=serializer.validated_data.get("email", ""),
                content=serializer.validated_data.get("content", "商品明细"),
            )
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InvoiceApplicationSerializer(invoice).data, status=status.HTTP_201_CREATED)


class RefundApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RefundApplication.objects.select_related("order", "user").all()
    serializer_class = RefundApplicationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["order", "user", "status", "refund_type"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        serializer = RefundAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refund = approve_refund(pk, serializer.validated_data["remark"], operator=request.user)
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundApplicationSerializer(refund).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        serializer = RefundAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refund = reject_refund(pk, serializer.validated_data["remark"], operator=request.user)
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundApplicationSerializer(refund).data)

    @action(detail=True, methods=["post"], url_path="request-gateway", permission_classes=[IsAdminUser])
    def request_gateway(self, request, pk=None):
        EmptyActionSerializer(data=request.data).is_valid(raise_exception=True)
        try:
            refund = request_refund_to_gateway(pk, operator=request.user)
        except (OrderCreateError, PaymentGatewayError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundApplicationSerializer(refund).data)

    @action(detail=True, methods=["post"], url_path="mark-refunded", permission_classes=[IsAdminUser])
    def mark_refunded(self, request, pk=None):
        serializer = RefundAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refund = mark_refund_success(pk, serializer.validated_data["remark"])
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RefundApplicationSerializer(refund).data)


class InvoiceApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InvoiceApplication.objects.select_related("order", "user").all()
    serializer_class = InvoiceApplicationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["order", "user", "status", "invoice_type"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        return queryset

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def issue(self, request, pk=None):
        serializer = IssueInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = issue_invoice(pk, serializer.validated_data["audit_remark"])
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InvoiceApplicationSerializer(invoice).data)


class LogisticsRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogisticsRecord.objects.select_related("order", "order__user").all()
    serializer_class = LogisticsRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["order", "tracking_no"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(order__user=self.request.user)
        return queryset

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def complete(self, request, pk=None):
        EmptyActionSerializer(data=request.data).is_valid(raise_exception=True)
        try:
            order = complete_order(self.get_object().id, operator=request.user)
        except OrderCreateError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)
