<template>
  <view class="empty">
    <view class="empty-title">{{ title }}</view>
    <view v-if="desc" class="empty-desc">{{ desc }}</view>
  </view>
</template>

<script>
export default {
  name: "EmptyState",
  props: {
    title: { type: String, default: "暂无数据" },
    desc: { type: String, default: "" }
  }
};
</script>

<style scoped>
.empty {
  padding: 80rpx 24rpx;
  text-align: center;
  color: #999999;
}
.empty-title {
  font-size: 28rpx;
}
.empty-desc {
  margin-top: 12rpx;
  font-size: 24rpx;
}
</style>

