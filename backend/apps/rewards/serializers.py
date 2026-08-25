from rest_framework import serializers

from .models import RewardDistributionRecord, RewardPool, RewardPoolRule


class RewardPoolRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardPoolRule
        fields = "__all__"


class RewardPoolSerializer(serializers.ModelSerializer):
    rules = RewardPoolRuleSerializer(many=True, read_only=True)

    class Meta:
        model = RewardPool
        fields = "__all__"


class RewardDistributionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardDistributionRecord
        fields = "__all__"


class RewardPoolDistributeSerializer(serializers.Serializer):
    pass
