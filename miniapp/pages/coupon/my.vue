<template>
  <view class="page">
    <view v-for="item in coupons" :key="item.id" class="card section">
      <view class="between">
        <text>{{ item.template_name || `优惠券 #${item.id}` }}</text>
        <text class="price">{{ statusText(item.status) }}</text>
      </view>
      <view class="subtle">有效期至 {{ item.valid_to }}</view>
    </view>
    <empty-state v-if="!coupons.length" title="暂无优惠券" />
  </view>
</template>

<script>
import { getMyCoupons } from "../../api/marketing";

export default {
  data() {
    return { coupons: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getMyCoupons();
      this.coupons = data.results || data || [];
    },
    statusText(value) {
      return { unused: "未使用", used: "已使用", expired: "已过期" }[value] || value;
    }
  }
};
</script>

