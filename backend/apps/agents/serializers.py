from rest_framework import serializers

from .models import CityAgent, CityAgentApplication


class CityAgentApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityAgentApplication
        fields = "__all__"
        read_only_fields = ["user", "status", "audit_remark"]


class CityAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityAgent
        fields = "__all__"


class AgentAuditSerializer(serializers.Serializer):
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, required=False, default=0)
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")
