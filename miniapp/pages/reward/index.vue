<template>
  <view class="page">
    <view class="reward-head section">
      <view class="title">奖金池</view>
      <view class="subtle">团队业绩、分销精英、月度奖励</view>
    </view>
    <view class="btn secondary section" @tap="goRecords">我的奖励</view>
    <view v-for="item in pools" :key="item.id" class="card section">
      <view class="between">
        <text class="pool-name">{{ item.name }}</text>
        <text class="price">￥{{ item.amount }}</text>
      </view>
      <view class="subtle">{{ item.pool_type }} · 门槛 {{ item.min_performance }}</view>
    </view>
    <empty-state v-if="!pools.length" title="暂无奖金池" />
  </view>
</template>

<script>
import { getRewardPools } from "../../api/user";

export default {
  data() {
    return { pools: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getRewardPools();
      this.pools = data.results || data || [];
    },
    goRecords() {
      uni.navigateTo({ url: "/pages/reward/records" });
    }
  }
};
</script>

<style scoped>
.reward-head {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 32rpx;
}
.pool-name {
  font-weight: 700;
}
</style>

