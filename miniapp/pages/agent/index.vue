<template>
  <view class="page">
    <view class="agent-card section">
      <view class="title light">城市代理</view>
      <view class="subtle light">区域经营、区域抽成、代理收益</view>
    </view>
    <view class="btn section" @tap="goApply">申请成为代理</view>

    <view v-if="agents.length" class="title section">我的代理区域</view>
    <view v-for="item in agents" :key="item.id" class="card section">
      <view class="between">
        <text>{{ item.region_name }}</text>
        <text class="price">{{ item.enabled ? "生效中" : "已停用" }}</text>
      </view>
      <view class="subtle">级别 {{ item.level }} · 抽成 {{ item.commission_rate }}%</view>
    </view>

    <view class="title section">申请记录</view>
    <view v-for="item in applications" :key="item.id" class="card section">
      <view class="between">
        <text>{{ item.region_name }}</text>
        <text class="price">{{ item.status }}</text>
      </view>
      <view class="subtle">级别 {{ item.level }} · {{ item.contact_phone }}</view>
    </view>
    <empty-state v-if="!applications.length && !agents.length" title="暂无代理信息" />
  </view>
</template>

<script>
import { getAgentApplications, getMyAgents } from "../../api/user";

export default {
  data() {
    return { applications: [], agents: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const [applications, agents] = await Promise.all([getAgentApplications(), getMyAgents()]);
      this.applications = applications.results || applications || [];
      this.agents = agents.results || agents || [];
    },
    goApply() {
      uni.navigateTo({ url: "/pages/agent/apply" });
    }
  }
};
</script>

<style scoped>
.agent-card {
  background: linear-gradient(135deg, #1677ff, #69b1ff);
  color: #ffffff;
  border-radius: 12rpx;
  padding: 32rpx;
}
.light {
  color: #fff;
}
</style>

