from django.contrib import admin

from .activity_models import ActivityPurchaseRecord
from .models import CouponTemplate, GroupBuyingActivity, SeckillActivity, UserCoupon

admin.site.register(CouponTemplate)
admin.site.register(UserCoupon)
admin.site.register(GroupBuyingActivity)
admin.site.register(SeckillActivity)
admin.site.register(ActivityPurchaseRecord)
