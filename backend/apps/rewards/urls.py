from rest_framework.routers import DefaultRouter

from .views import RewardDistributionRecordViewSet, RewardPoolRuleViewSet, RewardPoolViewSet

router = DefaultRouter()
router.register("pools", RewardPoolViewSet)
router.register("rules", RewardPoolRuleViewSet)
router.register("records", RewardDistributionRecordViewSet)

urlpatterns = router.urls

