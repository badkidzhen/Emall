# Money-related Integration Placeholders

This document records the payment, refund, invoice, wallet, and payout integration points that are already scaffolded in the backend. Real third-party API credentials can be filled in later without rewriting the main order or finance workflows.

The current project also exposes Mock endpoints under `/api/mock/` for local testing. Keep `ENABLE_MOCK_API=false` in production.

## Current API entry points

- Payment request: `POST /api/orders/{id}/create-payment/`
- Development payment confirmation: `POST /api/orders/{id}/confirm-paid/`
- Refund application: `POST /api/orders/{id}/apply-refund/`
- Admin refund audit: `POST /api/orders/refunds/{id}/approve/` or `reject/`
- Admin refund gateway request: `POST /api/orders/refunds/{id}/request-gateway/`
- Admin manual refund completion: `POST /api/orders/refunds/{id}/mark-refunded/`
- Invoice application: `POST /api/orders/{id}/apply-invoice/`
- Admin invoice issue: `POST /api/orders/invoices/{id}/issue/`
- Withdraw application: `POST /api/finance/withdrawals/`
- Admin withdraw audit: `POST /api/finance/withdrawals/{id}/approve/`
- Admin payout request: `POST /api/finance/withdrawals/{id}/submit-payout/`
- Admin manual payout completion: `POST /api/finance/withdrawals/{id}/mark-paid/`
- Real-name submission: `POST /api/users/submit-realname/`
- Admin real-name audit: `POST /api/users/{id}/audit-realname/`

## Production environment variables

```text
WECHAT_APPID=
WECHAT_APP_SECRET=
WECHAT_MCH_ID=
WECHAT_PAY_SERIAL_NO=
WECHAT_PAY_API_V3_KEY=
WECHAT_PAY_PRIVATE_KEY_PATH=
WECHAT_PAY_NOTIFY_URL=https://api.example.com/api/payments/wechat/notify/
WECHAT_REFUND_NOTIFY_URL=https://api.example.com/api/payments/wechat/refund-notify/
FINANCE_REQUIRE_REALNAME_FOR_WITHDRAW=true
```

## Placeholder files to complete later

- `backend/apps/orders/payment_gateways.py`
- `backend/apps/finance/payout_gateways.py`

The current `mock` and `manual` channels are for local development, admin reconciliation, and demos. Before production launch, add signature verification, callback idempotency, certificate validation, provider transaction numbers, and failure retry handling.
