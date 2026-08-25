from django.urls import path

from .mock_views import (
    MockLogisticsDeliveredView,
    MockPaymentSuccessView,
    MockRealnameSuccessView,
    MockRefundSuccessView,
    MockSmsSendView,
    MockSmsVerifyView,
    MockWalletIncomeView,
    MockWithdrawPaidView,
)


urlpatterns = [
    path("payments/<int:order_id>/success/", MockPaymentSuccessView.as_view(), name="mock-payment-success"),
    path("refunds/<int:refund_id>/success/", MockRefundSuccessView.as_view(), name="mock-refund-success"),
    path("withdrawals/<int:withdrawal_id>/paid/", MockWithdrawPaidView.as_view(), name="mock-withdraw-paid"),
    path("wallets/<int:user_id>/income/", MockWalletIncomeView.as_view(), name="mock-wallet-income"),
    path("realname/success/", MockRealnameSuccessView.as_view(), name="mock-realname-success"),
    path("users/<int:user_id>/realname-success/", MockRealnameSuccessView.as_view(), name="mock-user-realname-success"),
    path("sms/send/", MockSmsSendView.as_view(), name="mock-sms-send"),
    path("sms/verify/", MockSmsVerifyView.as_view(), name="mock-sms-verify"),
    path("logistics/<int:order_id>/delivered/", MockLogisticsDeliveredView.as_view(), name="mock-logistics-delivered"),
]
