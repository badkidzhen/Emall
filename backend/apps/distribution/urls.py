from rest_framework.routers import DefaultRouter

from .views import CommissionRecordViewSet, DistributionConfigViewSet, UserTeamStatViewSet

router = DefaultRouter()
router.register("team-stats", UserTeamStatViewSet)
router.register("configs", DistributionConfigViewSet)
router.register("commissions", CommissionRecordViewSet)

urlpatterns = router.urls

