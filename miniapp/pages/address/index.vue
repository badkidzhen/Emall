<template>
  <view class="page">
    <view v-for="item in addresses" :key="item.id" class="card section address-card" @tap="select(item)">
      <view class="between">
        <view>
          <text class="name">{{ item.receiver_name }}</text>
          <text class="mobile">{{ item.receiver_mobile }}</text>
        </view>
        <text v-if="item.is_default" class="tag">默认</text>
      </view>
      <view class="address-text">{{ fullAddress(item) }}</view>
      <view class="actions">
        <text @tap.stop="edit(item)">编辑</text>
        <text class="danger" @tap.stop="remove(item)">删除</text>
      </view>
    </view>
    <empty-state v-if="!addresses.length" title="暂无收货地址" desc="添加地址后下单更方便" />
    <view class="bottom-bar">
      <view class="btn" @tap="create">新增地址</view>
    </view>
  </view>
</template>

<script>
import { deleteAddress, getAddresses } from "../../api/order";

export default {
  data() {
    return { mode: "", addresses: [] };
  },
  onLoad(query) {
    this.mode = query.mode || "";
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getAddresses();
      this.addresses = data.results || data || [];
    },
    fullAddress(item) {
      return [item.province, item.city, item.district, item.address_detail].filter(Boolean).join(" ");
    },
    select(item) {
      if (this.mode !== "select") return;
      uni.setStorageSync("emall_selected_address", item);
      uni.navigateBack();
    },
    create() {
      uni.navigateTo({ url: "/pages/address/edit" });
    },
    edit(item) {
      uni.setStorageSync("emall_edit_address", item);
      uni.navigateTo({ url: `/pages/address/edit?id=${item.id}` });
    },
    async remove(item) {
      uni.showModal({
        title: "提示",
        content: "确认删除该地址？",
        success: async (res) => {
          if (!res.confirm) return;
          await deleteAddress(item.id);
          uni.showToast({ title: "已删除" });
          this.load();
        }
      });
    }
  }
};
</script>

<style scoped>
.page {
  padding-bottom: 120rpx;
}
.address-card {
  position: relative;
}
.name {
  font-weight: 700;
  margin-right: 16rpx;
}
.mobile {
  color: #666;
}
.tag {
  padding: 6rpx 12rpx;
  border-radius: 6rpx;
  background: #fff5f5;
  color: #ff2442;
  font-size: 22rpx;
}
.address-text {
  margin-top: 16rpx;
  color: #333;
  line-height: 42rpx;
}
.actions {
  margin-top: 18rpx;
  display: flex;
  justify-content: flex-end;
  gap: 28rpx;
  color: #1677ff;
  font-size: 24rpx;
}
.danger {
  color: #ff2442;
}
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 16rpx 24rpx;
  background: #fff;
}
</style>

