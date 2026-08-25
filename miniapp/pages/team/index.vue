<template>
  <view class="page">
    <view class="stat-card">
      <view class="title light">团队中心</view>
      <view class="subtle light">团队业绩与分销统计</view>
    </view>

    <view class="quick-grid section">
      <view class="quick" @tap="go('/pages/team/tree')">团队树</view>
      <view class="quick" @tap="go('/pages/team/commission')">佣金明细</view>
      <view class="quick" @tap="go('/pages/team/rank')">团队排行</view>
    </view>

    <view v-for="item in stats" :key="item.user" class="card section">
      <view class="grid">
        <view>
          <view class="num">{{ item.team_count }}</view>
          <view class="subtle">团队人数</view>
        </view>
        <view>
          <view class="num">{{ item.direct_count }}</view>
          <view class="subtle">直推人数</view>
        </view>
        <view>
          <view class="num">{{ item.team_order_amount }}</view>
          <view class="subtle">团队业绩</view>
        </view>
        <view>
          <view class="num">{{ item.team_commission }}</view>
          <view class="subtle">团队佣金</view>
        </view>
      </view>
    </view>
    <empty-state v-if="!stats.length" title="暂无团队统计" />
  </view>
</template>

<script>
import { getTeamStats } from "../../api/user";

export default {
  data() {
    return { stats: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getTeamStats();
      this.stats = data.results || data || [];
    },
    go(url) {
      uni.navigateTo({ url });
    }
  }
};
</script>

<style scoped>
.stat-card {
  background: linear-gradient(135deg, #722ed1, #b37feb);
  color: #ffffff;
  border-radius: 12rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
}
.light {
  color: #fff;
}
.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}
.quick {
  height: 84rpx;
  background: #fff;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24rpx;
}
.num {
  font-size: 34rpx;
  font-weight: 700;
  color: #1a1a1a;
}
</style>

