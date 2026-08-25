from django.db import models

from apps.core.models import StatusModel, TimeStampedModel


class ProductCategory(StatusModel):
    parent = models.ForeignKey(
        "self",
        verbose_name="父级分类",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    name = models.CharField("分类名称", max_length=100)
    icon = models.URLField("分类图标", max_length=500, blank=True, default="")
    banner = models.URLField("分类横幅", max_length=500, blank=True, default="")
    sort = models.PositiveIntegerField("排序", default=0)
    level = models.PositiveSmallIntegerField("层级", default=1)
    path = models.CharField("层级路径", max_length=255, blank=True, default="")
    is_show = models.BooleanField("是否展示", default=True)
    is_distribution = models.BooleanField("是否参与分销", default=True)
    seo_title = models.CharField("SEO 标题", max_length=200, blank=True, default="")
    seo_keywords = models.CharField("SEO 关键词", max_length=255, blank=True, default="")
    seo_description = models.CharField("SEO 描述", max_length=500, blank=True, default="")

    class Meta:
        db_table = "product_category"
        ordering = ["-sort", "id"]
        indexes = [
            models.Index(fields=["parent"], name="idx_category_parent"),
            models.Index(fields=["path"], name="idx_category_path"),
            models.Index(fields=["is_show", "sort"], name="idx_category_show_sort"),
        ]
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Product(StatusModel):
    class SaleStatus(models.TextChoices):
        DRAFT = "draft", "草稿"
        ON_SALE = "on_sale", "上架"
        OFF_SALE = "off_sale", "下架"

    title = models.CharField("商品标题", max_length=200)
    sub_title = models.CharField("副标题", max_length=255, blank=True, default="")
    cover = models.URLField("封面图", max_length=500, blank=True, default="")
    detail = models.TextField("商品详情", blank=True, default="")
    sale_status = models.CharField("销售状态", max_length=20, choices=SaleStatus.choices, default=SaleStatus.DRAFT)
    price = models.DecimalField("展示价", max_digits=12, decimal_places=2, default=0)
    market_price = models.DecimalField("划线价", max_digits=12, decimal_places=2, default=0)
    total_stock = models.IntegerField("总库存", default=0)
    is_distribution = models.BooleanField("是否参与分销", default=True)
    commission_type = models.CharField("佣金类型", max_length=20, blank=True, default="")
    commission_rate_lv1 = models.DecimalField("一级佣金比例", max_digits=5, decimal_places=2, default=0)
    commission_rate_lv2 = models.DecimalField("二级佣金比例", max_digits=5, decimal_places=2, default=0)
    categories = models.ManyToManyField(ProductCategory, through="ProductCategoryRelation", related_name="products")

    class Meta:
        db_table = "product"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sale_status"], name="idx_product_sale_status"),
            models.Index(fields=["is_distribution"], name="idx_product_distribution"),
        ]
        verbose_name = "商品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ProductCategoryRelation(models.Model):
    product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, verbose_name="分类", on_delete=models.CASCADE)
    is_main = models.BooleanField("是否主分类", default=True)

    class Meta:
        db_table = "product_category_relation"
        constraints = [
            models.UniqueConstraint(fields=["product", "category"], name="uk_product_category"),
        ]
        verbose_name = "商品分类关联"
        verbose_name_plural = verbose_name


class SpecTemplate(TimeStampedModel):
    name = models.CharField("模板名称", max_length=100)
    spec_names = models.JSONField("规格维度", default=list, blank=True)

    class Meta:
        db_table = "spec_template"
        verbose_name = "规格模板"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ProductSku(StatusModel):
    product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE, related_name="skus")
    sku_code = models.CharField("SKU 编码", max_length=64, unique=True)
    specs = models.JSONField("规格快照", default=dict, blank=True)
    price = models.DecimalField("售价", max_digits=12, decimal_places=2)
    market_price = models.DecimalField("划线价", max_digits=12, decimal_places=2, default=0)
    stock = models.IntegerField("可售库存", default=0)
    locked_stock = models.IntegerField("锁定库存", default=0)
    warning_stock = models.IntegerField("预警库存", default=0)
    image = models.URLField("SKU 图片", max_length=500, blank=True, default="")

    class Meta:
        db_table = "product_sku"
        indexes = [
            models.Index(fields=["product"], name="idx_sku_product"),
            models.Index(fields=["sku_code"], name="idx_sku_code"),
        ]
        verbose_name = "商品 SKU"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku_code


class StockLog(TimeStampedModel):
    class ChangeType(models.TextChoices):
        IN = "in", "入库"
        OUT = "out", "出库"
        LOCK = "lock", "锁定"
        UNLOCK = "unlock", "解锁"
        ROLLBACK = "rollback", "回滚"

    sku = models.ForeignKey(ProductSku, verbose_name="SKU", on_delete=models.CASCADE, related_name="stock_logs")
    change_type = models.CharField("变更类型", max_length=20, choices=ChangeType.choices)
    quantity = models.IntegerField("变更数量")
    before_stock = models.IntegerField("变更前库存")
    after_stock = models.IntegerField("变更后库存")
    remark = models.CharField("备注", max_length=255, blank=True, default="")

    class Meta:
        db_table = "stock_log"
        ordering = ["-created_at"]
        verbose_name = "库存变更日志"
        verbose_name_plural = verbose_name

