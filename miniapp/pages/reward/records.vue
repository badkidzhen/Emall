<template>
  <view class="page">
    <view v-for="item in records" :key="item.id" class="card section">
      <view class="between">
        <text>奖励 #{{ item.id }}</text>
        <text class="price">楼{{ item.amount }}</text>
      </view>
      <view class="subtle">寰楀垎 {{ item.score }} 路 {{ item.status }}</view>
      <view class="subtle">{{ formatTime(item.created_at) }}</view>
    </view>
    <empty-state v-if="!records.length" title="暂无奖励记录" />
  </view>
</template>

<script>
import { getRewardRecords } from "../../api/user";
import { formatDateTime } from "../../common/format";

export default {
  data() {
    return { records: [] };
  },
  async onShow() {
    const data = await getRewardRecords();
    this.records = data.results || data || [];
  },
  methods: {
    formatTime(value) {
      return formatDateTime(value);
    }
  }
};
</script>

