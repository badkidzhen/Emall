<template>
  <view class="page">
    <view v-for="item in groups" :key="item.id" class="card section">
      <view class="between">
        <view class="title">{{ item.name }}</view>
        <text class="price">￥{{ item.group_price }}</text>
      </view>
      <view class="subtle">库存 {{ item.stock }} · {{ item.started_at }} - {{ item.ended_at }}</view>
      <view class="btn section action" @tap="purchase(item)">团购下单</view>
    </view>
    <empty-state v-if="!groups.length" title="暂无团购活动" />
  </view>
</template>

<script>
import { getGroups, purchaseGroup } from "../../api/marketing";

export default {
  data() {
    return { groups: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getGroups();
      this.groups = data.results || data || [];
    },
    async purchase(item) {
      const order = await purchaseGroup(item.id, 1);
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

