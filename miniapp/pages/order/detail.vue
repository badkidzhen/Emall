<template>
  <view class="page detail-page">
    <view class="card section">
      <view class="between">
        <text class="title">{{ statusText(order.status) }}</text>
        <text class="price">¥{{ order.pay_amount }}</text>
      </view>
      <view class="subtle order-no">{{ order.order_no }}</view>
    </view>

    <view class="card section">
      <view class="block-title">收货信息</view>
      <view>{{ order.receiver_name || "-" }} {{ order.receiver_mobile || "" }}</view>
      <view class="subtle">{{ addressText }}</view>
    </view>

    <view v-if="order.logistics" class="card section">
      <view class="block-title">物流信息</view>
      <view>{{ order.logistics.company || "-" }} {{ order.logistics.tracking_no || "" }}</view>
      <view class="subtle">{{ formatTime(order.logistics.shipped_at) }}</view>
    </view>

    <view class="card section">
      <view class="block-title">商品明细</view>
      <view v-for="item in order.items || []" :key="item.id" class="item">
        <view class="name">{{ item.product_title }}</view>
        <view class="between">
          <text class="subtle">{{ item.spec_text || item.sku_code }}</text>
          <text>x {{ item.quantity }}</text>
        </view>
      </view>
    </view>

    <view v-if="(order.refund_applications || []).length" class="card section">
      <view class="block-title">售后记录</view>
      <view v-for="item in order.refund_applications" :key="item.id" class="record">
        <text>{{ item.refund_no }}</text>
        <text class="price">{{ refundStatusText(item.status) }} ¥{{ item.amount }}</text>
      </view>
    </view>

    <view v-if="order.invoice" class="card section">
      <view class="block-title">发票信息</view>
      <view>{{ order.invoice.title }} / {{ invoiceStatusText(order.invoice.status) }}</view>
      <view class="subtle">{{ order.invoice.email }}</view>
    </view>

    <view class="action-grid section">
      <view v-if="order.status === 'pending_payment'" class="btn" @tap="pay">去支付</view>
      <view v-if="order.status === 'pending_payment'" class="btn secondary" @tap="cancel">取消订单</view>
      <view v-if="order.status === 'pending_receipt'" class="btn" @tap="receive">确认收货</view>
      <view v-if="canRefund" class="btn secondary" @tap="goRefund">申请售后</view>
      <view v-if="canInvoice" class="btn secondary" @tap="goInvoice">申请发票</view>
    </view>
  </view>
</template>

<script>
import { cancelOrder, createPayment, getOrder, receiveOrder } from "../../api/order";
import { formatDateTime } from "../../common/format";

export default {
  data() {
    return { id: "", order: {} };
  },
  computed: {
    addressText() {
      const order = this.order || {};
      return [order.province, order.city, order.district, order.address_detail].filter(Boolean).join(" ") || "-";
    },
    canRefund() {
      return ["pending_shipment", "pending_receipt", "completed"].includes(this.order.status);
    },
    canInvoice() {
      return this.order.status && this.order.status !== "pending_payment" && !this.order.invoice;
    }
  },
  onLoad(query) {
    this.id = query.id;
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      this.order = await getOrder(this.id);
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
    },
    refundStatusText(status) {
      const map = { pending: "待审核", approved: "已通过", rejected: "已拒绝", refunding: "退款中", refunded: "已退款" };
      return map[status] || status;
    },
    invoiceStatusText(status) {
      const map = { pending: "待开票", issued: "已开票", rejected: "已拒绝" };
      return map[status] || status;
    },
    formatTime(value) {
      return formatDateTime(value);
    },
    async pay() {
      uni.showActionSheet({
        itemList: ["模拟支付", "微信支付"],
        success: async (res) => {
          const channel = res.tapIndex === 1 ? "wechat" : "mock";
          const data = await createPayment(this.id, { channel });
          if (channel === "wechat" && data.pay_params && data.pay_params.pay_params && data.pay_params.pay_params.timeStamp) {
            uni.requestPayment({
              ...data.pay_params.pay_params,
              success: () => uni.showToast({ title: "支付成功" }),
              fail: () => uni.showToast({ title: "支付未完成", icon: "none" })
            });
            return;
          }
          uni.showModal({
            title: "支付请求已创建",
            content: channel === "mock" ? "当前为模拟支付，请在后台确认支付。" : "微信支付参数待商户配置后即可发起。",
            showCancel: false
          });
        }
      });
    },
    async cancel() {
      await cancelOrder(this.id, "user_cancel");
      await this.load();
    },
    async receive() {
      await receiveOrder(this.id);
      await this.load();
    },
    goRefund() {
      uni.navigateTo({ url: `/pages/order/refund?id=${this.id}&amount=${this.order.pay_amount}` });
    },
    goInvoice() {
      uni.navigateTo({ url: `/pages/order/invoice?id=${this.id}` });
    }
  }
};
</script>

<style scoped>
.detail-page {
  padding-bottom: 40rpx;
}
.order-no {
  margin-top: 12rpx;
}
.block-title {
  font-weight: 700;
  margin-bottom: 16rpx;
}
.item {
  padding: 18rpx 0;
  border-bottom: 1rpx solid #e8e8e8;
}
.item:last-child {
  border-bottom: 0;
}
.name {
  font-weight: 600;
  margin-bottom: 10rpx;
}
.record {
  display: flex;
  justify-content: space-between;
  padding: 10rpx 0;
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}
</style>
