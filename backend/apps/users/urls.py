from rest_framework.routers import DefaultRouter

from .views import MemberLevelViewSet, UserViewSet

router = DefaultRouter()
router.register("levels", MemberLevelViewSet)
router.register("", UserViewSet)

urlpatterns = router.urls

