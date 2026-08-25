from rest_framework.routers import DefaultRouter

from .views import (
    CartItemViewSet,
    InvoiceApplicationViewSet,
    LogisticsRecordViewSet,
    OrderAddressViewSet,
    OrderViewSet,
    RefundApplicationViewSet,
)

router = DefaultRouter()
router.register("cart-items", CartItemViewSet)
router.register("addresses", OrderAddressViewSet)
router.register("refunds", RefundApplicationViewSet)
router.register("invoices", InvoiceApplicationViewSet)
router.register("logistics", LogisticsRecordViewSet)
router.register("", OrderViewSet)

urlpatterns = router.urls
