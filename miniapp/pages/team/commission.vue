<template>
  <view class="page">
    <view v-for="item in records" :key="item.id" class="card section">
      <view class="between">
        <text>{{ item.status }}</text>
        <text class="price">￥{{ item.amount }}</text>
      </view>
      <view class="subtle">订单 {{ item.order }} · {{ item.level }} 级佣金 · {{ formatTime(item.created_at) }}</view>
    </view>
    <empty-state v-if="!records.length" title="暂无佣金记录" />
  </view>
</template>

<script>
import { getCommissions } from "../../api/user";
import { formatDateTime } from "../../common/format";

export default {
  data() {
    return { records: [] };
  },
  async onShow() {
    const data = await getCommissions();
    this.records = data.results || data || [];
  },
  methods: {
    formatTime(value) {
      return formatDateTime(value);
    }
  }
};
</script>

