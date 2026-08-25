<template>
  <view class="page">
    <view v-if="orders.length">
      <view v-for="order in orders" :key="order.id" class="order-card" @tap="open(order)">
        <view class="between">
          <text class="no">{{ order.order_no }}</text>
          <text class="status">{{ statusText(order.status) }}</text>
        </view>
        <view class="between footer">
          <text class="subtle">{{ formatTime(order.created_at) }}</text>
          <text class="price">￥{{ order.pay_amount }}</text>
        </view>
      </view>
    </view>
    <empty-state v-else title="暂无订单" />
  </view>
</template>

<script>
import { getOrders } from "../../api/order";
import { formatDateTime } from "../../common/format";

export default {
  data() {
    return { orders: [] };
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getOrders();
      this.orders = data.results || data || [];
    },
    open(order) {
      uni.navigateTo({ url: `/pages/order/detail?id=${order.id}` });
    },
    formatTime(value) {
      return formatDateTime(value);
    },
    statusText(status) {
      const map = {
        pending_payment: "待付款",
        pending_shipment: "待发货",
        pending_receipt: "待收货",
        completed: "已完成",
        refunding: "售后中",
        refunded: "已退款",
        closed: "已关闭"
      };
      return map[status] || status;
    }
  }
};
</script>

<style scoped>
.order-card {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 18rpx;
}
.no {
  font-size: 24rpx;
  color: #333333;
}
.status {
  color: #ff2442;
  font-size: 24rpx;
}
.footer {
  margin-top: 22rpx;
}
</style>

