from django.urls import path
from rest_framework.routers import DefaultRouter

from .system_views import AdminMenuViewSet, GroupViewSet, LogEntryViewSet, MenuTreeView, PermissionViewSet

router = DefaultRouter()
router.register("menu-items", AdminMenuViewSet)
router.register("roles", GroupViewSet)
router.register("permissions", PermissionViewSet)
router.register("logs", LogEntryViewSet)

urlpatterns = [
    path("menus/", MenuTreeView.as_view(), name="admin-menu-tree"),
]
urlpatterns += router.urls
