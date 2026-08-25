<template>
  <view class="page">
    <view v-for="item in records" :key="item.id" class="card section">
      <view class="between">
        <text>提现 #{{ item.id }}</text>
        <text class="price">楼{{ item.amount }}</text>
      </view>
      <view class="subtle">{{ channelText(item.channel) }} / {{ statusText(item.status) }}</view>
      <view class="subtle">{{ formatTime(item.created_at) }}</view>
    </view>
    <empty-state v-if="!records.length" title="暂无提现记录" />
  </view>
</template>

<script>
import { getWithdrawals } from "../../api/user";
import { formatDateTime } from "../../common/format";

export default {
  data() {
    return { records: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getWithdrawals();
      this.records = data.results || data || [];
    },
    channelText(value) {
      return { manual: "手动打款", wechat: "微信提现", bank: "银行卡" }[value] || value;
    },
    statusText(value) {
      return { pending: "待审核", approved: "已通过", paying: "打款中", rejected: "已拒绝", paid: "已打款" }[value] || value;
    },
    formatTime(value) {
      return formatDateTime(value);
    }
  }
};
</script>

