from django.contrib import admin

from .models import (
    CartItem,
    InvoiceApplication,
    LogisticsRecord,
    Order,
    OrderAddress,
    OrderItem,
    PaymentRecord,
    RefundApplication,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_no", "user", "status", "pay_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("order_no", "user__mobile", "user__username")
    inlines = [OrderItemInline]


admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(PaymentRecord)
admin.site.register(OrderAddress)
admin.site.register(InvoiceApplication)
admin.site.register(LogisticsRecord)
admin.site.register(RefundApplication)
