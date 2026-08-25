from rest_framework.routers import DefaultRouter

from .views import (
    ActivityPurchaseRecordViewSet,
    CouponTemplateViewSet,
    GroupBuyingActivityViewSet,
    SeckillActivityViewSet,
    UserCouponViewSet,
)

router = DefaultRouter()
router.register("coupon-templates", CouponTemplateViewSet)
router.register("user-coupons", UserCouponViewSet)
router.register("groups", GroupBuyingActivityViewSet)
router.register("seckills", SeckillActivityViewSet)
router.register("activity-records", ActivityPurchaseRecordViewSet)

urlpatterns = router.urls
