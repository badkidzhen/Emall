<template>
  <view class="page">
    <view v-for="(item, index) in stats" :key="item.id" class="card section">
      <view class="between">
        <text>#{{ index + 1 }} 用户 {{ item.user }}</text>
        <text class="price">￥{{ item.team_order_amount }}</text>
      </view>
      <view class="subtle">团队 {{ item.team_count }} 人 · 佣金 {{ item.team_commission }}</view>
    </view>
    <empty-state v-if="!stats.length" title="暂无排行数据" />
  </view>
</template>

<script>
import { getTeamStats } from "../../api/user";

export default {
  data() {
    return { stats: [] };
  },
  async onShow() {
    const data = await getTeamStats();
    this.stats = (data.results || data || []).sort((a, b) => Number(b.team_order_amount || 0) - Number(a.team_order_amount || 0));
  }
};
</script>

