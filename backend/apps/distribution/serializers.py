from rest_framework import serializers

from .models import CommissionRecord, DistributionConfigModel, UserTeamStat


class UserTeamStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTeamStat
        fields = "__all__"


class DistributionConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionConfigModel
        fields = "__all__"


class CommissionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRecord
        fields = "__all__"


class BindParentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    parent_id = serializers.IntegerField(min_value=1)


class BindMineParentSerializer(serializers.Serializer):
    parent_id = serializers.IntegerField(min_value=1)
