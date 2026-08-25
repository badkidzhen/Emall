from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .responses import api_success


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return api_success({"service": "emall-api", "status": "ok"})


class ImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

    allowed_content_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    max_size = 5 * 1024 * 1024

    def post(self, request):
        image = request.FILES.get("file")
        if not image:
            return Response({"detail": "请选择要上传的图片。"}, status=status.HTTP_400_BAD_REQUEST)
        if image.size > self.max_size:
            return Response({"detail": "图片不能超过 5MB。"}, status=status.HTTP_400_BAD_REQUEST)
        suffix = Path(image.name).suffix.lower()
        if image.content_type not in self.allowed_content_types or suffix not in self.allowed_extensions:
            return Response({"detail": "仅支持 jpg、png、webp、gif 图片。"}, status=status.HTTP_400_BAD_REQUEST)

        storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
        filename = storage.save(f"uploads/images/{uuid4().hex}{suffix}", image)
        relative_url = storage.url(filename)
        if not relative_url.startswith("/"):
            relative_url = f"/{relative_url}"
        return Response(
            {
                "url": request.build_absolute_uri(relative_url),
                "path": relative_url,
                "name": image.name,
                "size": image.size,
            },
            status=status.HTTP_201_CREATED,
        )
