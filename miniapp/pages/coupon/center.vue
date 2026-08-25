<template>
  <view class="page">
    <view v-for="item in coupons" :key="item.id" class="coupon-card">
      <view>
        <view class="title">{{ item.name }}</view>
        <view class="subtle">{{ couponText(item) }}</view>
      </view>
      <view class="claim" @tap="claim(item)">领取</view>
    </view>
    <empty-state v-if="!coupons.length" title="暂无优惠券" />
  </view>
</template>

<script>
import { claimCoupon, getCouponTemplates } from "../../api/marketing";

export default {
  data() {
    return { coupons: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getCouponTemplates();
      this.coupons = data.results || data || [];
    },
    couponText(item) {
      if (item.coupon_type === "discount") return `满${item.threshold_amount} 可打 ${Number(item.discount_rate || 1) * 10} 折`;
      return `满${item.threshold_amount} 减${item.discount_amount}`;
    },
    async claim(item) {
      await claimCoupon(item.id);
      uni.showToast({ title: "领取成功" });
    }
  }
};
</script>

<style scoped>
.coupon-card {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 18rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.claim {
  width: 112rpx;
  height: 58rpx;
  background: #ff2442;
  color: #ffffff;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
}
</style>

