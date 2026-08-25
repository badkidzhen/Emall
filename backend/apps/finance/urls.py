from rest_framework.routers import DefaultRouter

from .views import FundFlowViewSet, WalletViewSet, WithdrawApplicationViewSet

router = DefaultRouter()
router.register("wallets", WalletViewSet)
router.register("flows", FundFlowViewSet)
router.register("withdrawals", WithdrawApplicationViewSet)

urlpatterns = router.urls
