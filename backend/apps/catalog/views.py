from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly

from .filters import ProductFilter
from .models import Product, ProductCategory, ProductSku, SpecTemplate, StockLog
from .serializers import (
    GenerateSkuSerializer,
    ProductCategorySerializer,
    ProductCategoryTreeSerializer,
    ProductSerializer,
    ProductSkuSerializer,
    SpecTemplateSerializer,
    StockLogSerializer,
)
from .services import build_category_tree, generate_product_skus


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.select_related("parent").all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    filterset_fields = ["parent", "level", "is_show", "is_distribution"]
    ordering_fields = ["sort", "created_at"]

    @action(detail=False, methods=["get"])
    def tree(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        tree = build_category_tree(list(queryset))
        serializer = ProductCategoryTreeSerializer(tree, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related("skus", "categories").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["title", "sub_title"]
    ordering_fields = ["price", "total_stock", "created_at"]

    @action(detail=True, methods=["post"], url_path="generate-skus", permission_classes=[IsAdminUser])
    def generate_skus(self, request, pk=None):
        serializer = GenerateSkuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product, created_skus, total_combinations = generate_product_skus(
            product_id=pk,
            spec_options=serializer.validated_data["spec_options"],
            defaults={
                "price": serializer.validated_data["price"],
                "market_price": serializer.validated_data["market_price"],
                "stock": serializer.validated_data["stock"],
                "warning_stock": serializer.validated_data["warning_stock"],
            },
            overwrite=serializer.validated_data["overwrite"],
        )

        return Response(
            {
                "product": product.id,
                "total_combinations": total_combinations,
                "created_count": len(created_skus),
                "created_skus": ProductSkuSerializer(created_skus, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ProductSkuViewSet(viewsets.ModelViewSet):
    queryset = ProductSku.objects.select_related("product").all()
    serializer_class = ProductSkuSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["sku_code", "product__title"]
    filterset_fields = ["product", "is_active"]
    ordering_fields = ["price", "stock", "created_at"]


class SpecTemplateViewSet(viewsets.ModelViewSet):
    queryset = SpecTemplate.objects.all()
    serializer_class = SpecTemplateSerializer
    permission_classes = [IsAdminUser]
    search_fields = ["name"]


class StockLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockLog.objects.select_related("sku", "sku__product").all()
    serializer_class = StockLogSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["sku", "change_type"]
