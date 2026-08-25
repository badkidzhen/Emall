from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True


class StatusModel(TimeStampedModel):
    is_active = models.BooleanField("是否启用", default=True)

    class Meta:
        abstract = True


class AdminMenu(TimeStampedModel):
    parent = models.ForeignKey(
        "self",
        verbose_name="父级菜单",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    name = models.CharField("菜单名称", max_length=50)
    code = models.CharField("菜单编码", max_length=80, unique=True)
    icon = models.CharField("图标", max_length=50, blank=True, default="")
    path = models.CharField("路由路径", max_length=255, blank=True, default="")
    component = models.CharField("组件路径", max_length=255, blank=True, default="")
    permission = models.CharField("权限标识", max_length=100, blank=True, default="")
    sort = models.IntegerField("排序", default=0)
    level = models.PositiveSmallIntegerField("层级", default=1)
    is_show = models.BooleanField("是否显示", default=True)

    class Meta:
        db_table = "admin_menu"
        ordering = ["-sort", "id"]
        indexes = [
            models.Index(fields=["parent"], name="idx_admin_menu_parent"),
            models.Index(fields=["is_show", "sort"], name="idx_admin_menu_show_sort"),
        ]
        verbose_name = "后台菜单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
