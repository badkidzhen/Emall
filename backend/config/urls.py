from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.views import ImageUploadView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/uploads/images/", ImageUploadView.as_view(), name="image-upload"),
    path("api/health/", include("apps.core.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/catalog/", include("apps.catalog.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/distribution/", include("apps.distribution.urls")),
    path("api/marketing/", include("apps.marketing.urls")),
    path("api/agents/", include("apps.agents.urls")),
    path("api/rewards/", include("apps.rewards.urls")),
    path("api/finance/", include("apps.finance.urls")),
    path("api/system/", include("apps.core.system_urls")),
]

if settings.ENABLE_MOCK_API:
    urlpatterns.append(path("api/mock/", include("apps.core.mock_urls")))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
