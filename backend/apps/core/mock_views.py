from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.finance.models import WithdrawApplication
from apps.finance.serializers import FundFlowSerializer, WithdrawApplicationSerializer
from apps.finance.services import FinanceError, add_income, approve_withdraw, mark_withdraw_paid
from apps.orders.models import LogisticsRecord, Order, PaymentRecord, RefundApplication
from apps.orders.serializers import (
    LogisticsRecordSerializer,
    OrderSerializer,
    PaymentRecordSerializer,
    RefundApplicationSerializer,
)
from apps.orders.services import (
    OrderCreateError,
    approve_refund,
    confirm_order_paid,
    mark_refund_success,
    trigger_order_completed,
)
from apps.users.serializers import UserSerializer


MOCK_SMS_CODE = "123456"
_SMS_CODES = {}


def mock_response(data=None, http_status=status.HTTP_200_OK):
    payload = {"mock": True}
    if data:
        payload.update(data)
    return Response(payload, status=http_status)


def mock_error(exc, http_status=status.HTTP_400_BAD_REQUEST):
    return mock_response({"detail": str(exc)}, http_status=http_status)


def mock_trade_no(prefix, pk):
    timestamp = timezone.localtime().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{pk}-{timestamp}"


class MockPaymentSuccessView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        payment_no = request.data.get("payment_no") or self.resolve_payment_no(order)
        paid_amount = order.pay_amount
        try:
            order, payment, created = confirm_order_paid(
                order_id=order.id,
                payment_no=payment_no,
                paid_amount=paid_amount,
                channel=PaymentRecord.Channel.MOCK,
                raw_payload={
                    "provider": "mock",
                    "trade_no": mock_trade_no("MOCKPAY", order.id),
                    "paid_amount": str(paid_amount),
                    "operator_id": request.user.id,
                },
            )
        except OrderCreateError as exc:
            return mock_error(exc)
        return mock_response(
            {
                "created": created,
                "order": OrderSerializer(order).data,
                "payment": PaymentRecordSerializer(payment).data,
            },
            http_status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def resolve_payment_no(self, order):
        payment = (
            PaymentRecord.objects.filter(order=order, status=PaymentRecord.Status.PENDING)
            .order_by("-created_at")
            .first()
        )
        if payment:
            return payment.payment_no
        return mock_trade_no("MOCKPAY", order.id)


class MockRefundSuccessView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, refund_id):
        refund = get_object_or_404(RefundApplication, pk=refund_id)
        remark = request.data.get("remark") or "mock_refund_success"
        try:
            if refund.status == RefundApplication.Status.PENDING:
                refund = approve_refund(refund.id, remark=remark, operator=request.user)
            if refund.status not in {RefundApplication.Status.APPROVED, RefundApplication.Status.REFUNDING}:
                raise OrderCreateError("Only pending/approved/refunding refunds can be mocked as refunded.")
            refund = mark_refund_success(
                refund.id,
                remark=remark,
                raw_payload={
                    "provider": "mock",
                    "refund_trade_no": mock_trade_no("MOCKRF", refund.id),
                    "operator_id": request.user.id,
                },
            )
        except OrderCreateError as exc:
            return mock_error(exc)
        return mock_response({"refund": RefundApplicationSerializer(refund).data})


class MockWithdrawPaidView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, withdrawal_id):
        application = get_object_or_404(WithdrawApplication, pk=withdrawal_id)
        remark = request.data.get("remark") or "mock_withdraw_paid"
        try:
            if application.status == WithdrawApplication.Status.PENDING:
                application = approve_withdraw(application.id, remark=remark)
            if application.status not in {WithdrawApplication.Status.APPROVED, WithdrawApplication.Status.PAYING}:
                raise FinanceError("Only pending/approved/paying withdrawals can be mocked as paid.")
            application = mark_withdraw_paid(application.id, remark=remark)
            application.payout_no = application.payout_no or mock_trade_no("MOCKPO", application.id)
            application.raw_payload = {
                "provider": "mock",
                "payout_no": application.payout_no,
                "operator_id": request.user.id,
            }
            application.save(update_fields=["payout_no", "raw_payload", "updated_at"])
        except FinanceError as exc:
            return mock_error(exc)
        return mock_response({"withdrawal": WithdrawApplicationSerializer(application).data})


class MockWalletIncomeView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        user = get_object_or_404(get_user_model(), pk=user_id)
        try:
            amount = Decimal(str(request.data.get("amount", "100.00")))
        except (InvalidOperation, TypeError):
            return mock_error("amount must be a valid decimal.")
        if amount <= 0:
            return mock_error("amount must be greater than zero.")
        flow = add_income(
            user=user,
            amount=amount,
            biz_type=request.data.get("biz_type") or "mock_income",
            biz_id=request.data.get("biz_id") or mock_trade_no("MOCKIN", user.id),
            remark=request.data.get("remark") or "mock_wallet_income",
        )
        return mock_response({"flow": FundFlowSerializer(flow).data}, http_status=status.HTTP_201_CREATED)


class MockRealnameSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id=None):
        if user_id is not None:
            if not request.user.is_staff:
                return mock_error("Only admin users can mock another user's real-name verification.", status.HTTP_403_FORBIDDEN)
            user = get_object_or_404(get_user_model(), pk=user_id)
        else:
            user = request.user

        user.realname = request.data.get("realname") or user.realname or "测试用户"
        user.id_card = request.data.get("id_card") or user.id_card or "110101199001011234"
        user.realname_status = user.RealnameStatus.VERIFIED
        user.realname_remark = request.data.get("remark") or "mock_realname_verified"
        user.realname_verified_at = timezone.now()
        user.save(
            update_fields=[
                "realname",
                "id_card",
                "realname_status",
                "realname_remark",
                "realname_verified_at",
            ]
        )
        return mock_response({"user": UserSerializer(user).data})


class MockSmsSendView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile")
        if not mobile:
            return mock_error("mobile is required.")
        _SMS_CODES[mobile] = {"code": MOCK_SMS_CODE, "created_at": timezone.now().isoformat()}
        return mock_response({"mobile": mobile, "code": MOCK_SMS_CODE})


class MockSmsVerifyView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile")
        code = request.data.get("code")
        if not mobile or not code:
            return mock_error("mobile and code are required.")
        expected = _SMS_CODES.get(mobile, {}).get("code", MOCK_SMS_CODE)
        verified = code == expected
        return mock_response({"mobile": mobile, "verified": verified}, status.HTTP_200_OK if verified else status.HTTP_400_BAD_REQUEST)


class MockLogisticsDeliveredView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        now = timezone.now()
        company = request.data.get("company") or "Mock Express"
        tracking_no = request.data.get("tracking_no") or mock_trade_no("MOCKLG", order_id)
        traces = request.data.get("traces") or [
            {"time": timezone.localtime(now).isoformat(), "status": "已签收", "remark": "Mock 物流已送达"},
        ]
        should_trigger_completion = False
        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update(), pk=order_id)
            if order.status not in {Order.Status.PENDING_SHIPMENT, Order.Status.PENDING_RECEIPT, Order.Status.COMPLETED}:
                return mock_error("Only paid fulfillment orders can receive mock logistics.")
            should_trigger_completion = order.status != Order.Status.COMPLETED
            order.status = Order.Status.COMPLETED
            order.completed_at = order.completed_at or now
            order.save(update_fields=["status", "completed_at", "updated_at"])
            logistics, _ = LogisticsRecord.objects.update_or_create(
                order=order,
                defaults={
                    "company": company,
                    "tracking_no": tracking_no,
                    "shipped_at": order.paid_at or now,
                    "delivered_at": now,
                    "traces": traces,
                    "raw_payload": {"provider": "mock", "operator_id": request.user.id},
                },
            )
        if should_trigger_completion:
            trigger_order_completed(order.id)
        return mock_response(
            {
                "order": OrderSerializer(order).data,
                "logistics": LogisticsRecordSerializer(logistics).data,
            }
        )
