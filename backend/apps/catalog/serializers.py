from rest_framework import serializers

from .models import Product, ProductCategory, ProductSku, SpecTemplate, StockLog
from .services import normalize_spec_options


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductCategoryTreeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    parent = serializers.IntegerField(allow_null=True)
    level = serializers.IntegerField()
    path = serializers.CharField(allow_blank=True)
    icon = serializers.CharField(allow_blank=True)
    banner = serializers.CharField(allow_blank=True)
    sort = serializers.IntegerField()
    is_show = serializers.BooleanField()
    is_distribution = serializers.BooleanField()
    children = serializers.ListField()


class ProductSkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSku
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), many=True, required=False)
    skus = ProductSkuSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        product = super().create(validated_data)
        if categories:
            product.categories.set(categories)
        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        product = super().update(instance, validated_data)
        if categories is not None:
            product.categories.set(categories)
        return product


class SpecTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecTemplate
        fields = "__all__"


class StockLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLog
        fields = "__all__"


class GenerateSkuSerializer(serializers.Serializer):
    spec_options = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    market_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False, default=0)
    stock = serializers.IntegerField(min_value=0, required=False, default=0)
    warning_stock = serializers.IntegerField(min_value=0, required=False, default=0)
    overwrite = serializers.BooleanField(required=False, default=False)

    def validate_spec_options(self, value):
        try:
            return normalize_spec_options(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
