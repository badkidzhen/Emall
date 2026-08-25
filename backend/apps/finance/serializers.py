from rest_framework import serializers

from .models import FundFlow, Wallet, WithdrawApplication


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


class FundFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundFlow
        fields = "__all__"


class WithdrawApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawApplication
        fields = "__all__"
        read_only_fields = ["user", "status", "audit_remark", "audited_at", "paid_at"]


class ApplyWithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    channel = serializers.ChoiceField(choices=WithdrawApplication.Channel.choices, required=False, default=WithdrawApplication.Channel.MANUAL)
    account_name = serializers.CharField(max_length=100)
    account_no = serializers.CharField(max_length=100)


class WithdrawAuditSerializer(serializers.Serializer):
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")


class WithdrawPayoutSerializer(serializers.Serializer):
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")
