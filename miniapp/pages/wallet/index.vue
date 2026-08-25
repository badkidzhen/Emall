<template>
  <view class="page">
    <view class="wallet-card section">
      <view class="subtle">可用余额</view>
      <view class="balance">¥{{ wallet.balance || "0.00" }}</view>
      <view class="wallet-row">
        <text>冻结 {{ wallet.frozen_balance || "0.00" }}</text>
        <text>累计提现 {{ wallet.total_withdraw || "0.00" }}</text>
      </view>
    </view>
    <view class="btn section" @tap="goWithdraw">申请提现</view>
    <view class="btn secondary section" @tap="goRecords">提现记录</view>
    <view class="title section">资金流水</view>
    <view v-for="item in flows" :key="item.id" class="card section">
      <view class="between">
        <text>{{ flowText(item.flow_type) }}</text>
        <text class="price">{{ item.amount }}</text>
      </view>
      <view class="subtle">{{ item.remark }}</view>
    </view>
  </view>
</template>

<script>
import { getFlows, getWallet } from "../../api/user";

export default {
  data() {
    return { wallet: {}, flows: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      this.wallet = await getWallet();
      const data = await getFlows();
      this.flows = data.results || data || [];
    },
    flowText(value) {
      return { income: "收入", withdraw: "提现", freeze: "冻结", unfreeze: "解冻", adjust: "调整" }[value] || value;
    },
    goWithdraw() {
      uni.navigateTo({ url: "/pages/wallet/withdraw" });
    },
    goRecords() {
      uni.navigateTo({ url: "/pages/wallet/records" });
    }
  }
};
</script>

<style scoped>
.wallet-card {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 32rpx;
}
.balance {
  font-size: 56rpx;
  font-weight: 700;
  color: #ff2442;
  margin: 16rpx 0;
}
.wallet-row {
  display: flex;
  justify-content: space-between;
  color: #666666;
  font-size: 24rpx;
}
</style>
