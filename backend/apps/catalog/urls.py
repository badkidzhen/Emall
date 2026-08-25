from rest_framework.routers import DefaultRouter

from .views import (
    ProductCategoryViewSet,
    ProductSkuViewSet,
    ProductViewSet,
    SpecTemplateViewSet,
    StockLogViewSet,
)

router = DefaultRouter()
router.register("categories", ProductCategoryViewSet)
router.register("products", ProductViewSet)
router.register("skus", ProductSkuViewSet)
router.register("spec-templates", SpecTemplateViewSet)
router.register("stock-logs", StockLogViewSet)

urlpatterns = router.urls

