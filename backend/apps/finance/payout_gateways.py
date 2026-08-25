from dataclasses import dataclass
from uuid import uuid4

from django.conf import settings


@dataclass(frozen=True)
class PayoutResult:
    payout_no: str
    payload: dict


class PayoutGatewayError(ValueError):
    pass


class ManualPayoutGateway:
    channel = "manual"

    def submit(self, *, application):
        return PayoutResult(
            payout_no=f"MANUAL{uuid4().hex[:18].upper()}",
            payload={
                "provider": "manual",
                "withdrawal_id": application.id,
                "amount": str(application.amount),
                "status": "waiting_manual_transfer",
            },
        )


class WeChatPayoutGateway:
    channel = "wechat"

    def _ensure_configured(self):
        required = [
            "WECHAT_APPID",
            "WECHAT_MCH_ID",
            "WECHAT_PAY_SERIAL_NO",
            "WECHAT_PAY_API_V3_KEY",
            "WECHAT_PAY_PRIVATE_KEY_PATH",
        ]
        missing = [name for name in required if not getattr(settings, name, "")]
        if missing:
            raise PayoutGatewayError(f"WeChat payout is not configured: {', '.join(missing)}.")

    def submit(self, *, application):
        self._ensure_configured()
        # Third-party integration placeholder:
        # Call WeChat transfer API here after merchant payout permissions are available.
        return PayoutResult(
            payout_no="",
            payload={
                "provider": "wechat",
                "withdrawal_id": application.id,
                "amount": str(application.amount),
                "account_no": application.account_no,
                "configured": True,
            },
        )


class BankPayoutGateway:
    channel = "bank"

    def submit(self, *, application):
        # Third-party integration placeholder:
        # Integrate bank/enterprise payment provider here when API credentials are provided.
        return PayoutResult(
            payout_no="",
            payload={
                "provider": "bank",
                "withdrawal_id": application.id,
                "amount": str(application.amount),
                "account_no": application.account_no,
                "configured": False,
            },
        )


def get_payout_gateway(channel):
    if channel == "manual":
        return ManualPayoutGateway()
    if channel == "wechat":
        return WeChatPayoutGateway()
    if channel == "bank":
        return BankPayoutGateway()
    raise PayoutGatewayError(f"Unsupported payout channel: {channel}.")
