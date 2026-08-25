from rest_framework import serializers

from .models import CouponTemplate, GroupBuyingActivity, SeckillActivity, UserCoupon
from .activity_models import ActivityPurchaseRecord


class CouponTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponTemplate
        fields = "__all__"


class UserCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCoupon
        fields = "__all__"


class GroupBuyingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBuyingActivity
        fields = "__all__"


class SeckillActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SeckillActivity
        fields = "__all__"


class ClaimCouponSerializer(serializers.Serializer):
    pass


class ActivityPurchaseSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, default=1)


class ActivityPurchaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPurchaseRecord
        fields = "__all__"
