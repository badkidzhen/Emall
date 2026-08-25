from rest_framework.routers import DefaultRouter

from .views import CityAgentApplicationViewSet, CityAgentViewSet

router = DefaultRouter()
router.register("applications", CityAgentApplicationViewSet)
router.register("", CityAgentViewSet)

urlpatterns = router.urls

