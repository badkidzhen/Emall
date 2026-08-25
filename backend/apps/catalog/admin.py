from django.contrib import admin

from .models import Product, ProductCategory, ProductCategoryRelation, ProductSku, SpecTemplate, StockLog


class ProductSkuInline(admin.TabularInline):
    model = ProductSku
    extra = 0


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "level", "sort", "is_show", "is_distribution")
    list_filter = ("level", "is_show", "is_distribution")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "sale_status", "price", "total_stock", "is_distribution")
    list_filter = ("sale_status", "is_distribution")
    search_fields = ("title",)
    inlines = [ProductSkuInline]


admin.site.register(ProductCategoryRelation)
admin.site.register(SpecTemplate)
admin.site.register(ProductSku)
admin.site.register(StockLog)

