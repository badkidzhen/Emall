<template>
  <view class="page">
    <view v-for="item in seckills" :key="item.id" class="card section">
      <view class="between">
        <view class="title">{{ item.name }}</view>
        <text class="price">￥{{ item.seckill_price }}</text>
      </view>
      <view class="subtle">限购 {{ item.per_user_limit }} · 库存 {{ item.stock }}</view>
      <view class="subtle">{{ item.started_at }} - {{ item.ended_at }}</view>
      <view class="btn section action" @tap="purchase(item)">立即秒杀</view>
    </view>
    <empty-state v-if="!seckills.length" title="暂无秒杀活动" />
  </view>
</template>

<script>
import { getSeckills, purchaseSeckill } from "../../api/marketing";

export default {
  data() {
    return { seckills: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getSeckills();
      this.seckills = data.results || data || [];
    },
    async purchase(item) {
      const order = await purchaseSeckill(item.id, 1);
      uni.navigateTo({ url: `/pages/order/detail?id=${order.order}` });
    }
  }
};
</script>

<style scoped>
.action {
  margin-top: 20rpx;
}
</style>

