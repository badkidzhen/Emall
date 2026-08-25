from dataclasses import dataclass
from uuid import uuid4

from django.conf import settings


@dataclass(frozen=True)
class GatewayResult:
    gateway_trade_no: str
    payload: dict


class PaymentGatewayError(ValueError):
    pass


class BasePaymentGateway:
    channel = "base"

    def create_payment(self, *, order, payment_no, client_ip="", openid=""):
        raise NotImplementedError

    def request_refund(self, *, refund, payment):
        raise NotImplementedError


class MockPaymentGateway(BasePaymentGateway):
    channel = "mock"

    def create_payment(self, *, order, payment_no, client_ip="", openid=""):
        return GatewayResult(
            gateway_trade_no=f"MOCK{uuid4().hex[:20].upper()}",
            payload={
                "provider": "mock",
                "payment_no": payment_no,
                "order_no": order.order_no,
                "amount": str(order.pay_amount),
                "pay_status": "created",
            },
        )

    def request_refund(self, *, refund, payment):
        return GatewayResult(
            gateway_trade_no=f"MOCKRF{uuid4().hex[:18].upper()}",
            payload={
                "provider": "mock",
                "refund_no": refund.refund_no,
                "payment_no": payment.payment_no,
                "amount": str(refund.amount),
                "refund_status": "created",
            },
        )


class WeChatPaymentGateway(BasePaymentGateway):
    channel = "wechat"

    def _ensure_configured(self):
        required = [
            "WECHAT_APPID",
            "WECHAT_MCH_ID",
            "WECHAT_PAY_SERIAL_NO",
            "WECHAT_PAY_API_V3_KEY",
            "WECHAT_PAY_PRIVATE_KEY_PATH",
            "WECHAT_PAY_NOTIFY_URL",
        ]
        missing = [name for name in required if not getattr(settings, name, "")]
        if missing:
            raise PaymentGatewayError(f"WeChat Pay is not configured: {', '.join(missing)}.")

    def create_payment(self, *, order, payment_no, client_ip="", openid=""):
        self._ensure_configured()
        # Third-party integration placeholder:
        # Build WeChat JSAPI prepay request here after merchant credentials are provided.
        return GatewayResult(
            gateway_trade_no="",
            payload={
                "provider": "wechat",
                "payment_no": payment_no,
                "order_no": order.order_no,
                "amount": str(order.pay_amount),
                "appid": settings.WECHAT_APPID,
                "mch_id": settings.WECHAT_MCH_ID,
                "notify_url": settings.WECHAT_PAY_NOTIFY_URL,
                "prepay_id": "",
                "pay_params": {},
                "configured": True,
            },
        )

    def request_refund(self, *, refund, payment):
        self._ensure_configured()
        # Third-party integration placeholder:
        # Call WeChat refund API here and store provider refund id in gateway_trade_no.
        return GatewayResult(
            gateway_trade_no="",
            payload={
                "provider": "wechat",
                "refund_no": refund.refund_no,
                "payment_no": payment.payment_no,
                "amount": str(refund.amount),
                "notify_url": settings.WECHAT_REFUND_NOTIFY_URL,
                "configured": True,
            },
        )


def get_payment_gateway(channel):
    if channel == "mock":
        return MockPaymentGateway()
    if channel == "wechat":
        return WeChatPaymentGateway()
    raise PaymentGatewayError(f"Unsupported payment channel: {channel}.")
