<template>
  <view class="page cart-page">
    <view v-if="items.length">
      <view v-for="item in items" :key="item.id" class="cart-item">
        <checkbox :checked="item.selected" color="#ff2442" @tap.stop="toggle(item)" />
        <view class="item-main">
          <view class="name">{{ item.product_title }}</view>
          <view class="subtle">{{ item.spec_text || item.sku_code }}</view>
          <view class="between">
            <text class="price">￥{{ item.price }}</text>
            <view class="stepper">
              <text @tap.stop="changeQty(item, -1)">-</text>
              <text class="qty">{{ item.quantity }}</text>
              <text @tap.stop="changeQty(item, 1)">+</text>
            </view>
          </view>
        </view>
        <text class="delete" @tap.stop="remove(item)">删除</text>
      </view>
    </view>
    <empty-state v-else title="购物车为空" desc="去挑选一些商品吧" />
    <view class="bottom-bar">
      <view>
        <view class="subtle">已选 {{ selectedCount }} 件</view>
        <view class="price total">￥{{ total }}</view>
      </view>
      <view class="btn checkout" @tap="checkout">结算</view>
    </view>
  </view>
</template>

<script>
import { deleteCartItem, getCartItems, updateCartItem } from "../../api/order";

export default {
  data() {
    return { items: [] };
  },
  computed: {
    selectedItems() {
      return this.items.filter((item) => item.selected);
    },
    selectedCount() {
      return this.selectedItems.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
    },
    total() {
      return this.selectedItems.reduce((sum, item) => sum + Number(item.price || 0) * item.quantity, 0).toFixed(2);
    }
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const data = await getCartItems();
      this.items = data.results || data || [];
    },
    async toggle(item) {
      item.selected = !item.selected;
      await updateCartItem(item.id, { selected: item.selected });
    },
    async changeQty(item, delta) {
      const quantity = Math.max(1, Number(item.quantity || 1) + delta);
      item.quantity = quantity;
      await updateCartItem(item.id, { quantity });
    },
    async remove(item) {
      uni.showModal({
        title: "提示",
        content: "确认删除该商品？",
        success: async (res) => {
          if (!res.confirm) return;
          await deleteCartItem(item.id);
          this.load();
        }
      });
    },
    async checkout() {
      if (!this.selectedItems.length) {
        uni.showToast({ title: "请选择商品", icon: "none" });
        return;
      }
      uni.navigateTo({ url: "/pages/order/create?from_cart=1" });
    }
  }
};
</script>

<style scoped>
.cart-page {
  padding-bottom: 130rpx;
}
.cart-item {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 18rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
}
.item-main {
  flex: 1;
  min-width: 0;
}
.name {
  font-weight: 700;
  margin-bottom: 8rpx;
}
.stepper {
  display: flex;
  align-items: center;
  border: 1rpx solid #e8e8e8;
  border-radius: 8rpx;
  overflow: hidden;
}
.stepper text {
  min-width: 54rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.qty {
  border-left: 1rpx solid #e8e8e8;
  border-right: 1rpx solid #e8e8e8;
}
.delete {
  color: #ff2442;
  font-size: 24rpx;
}
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 116rpx;
  padding: 16rpx 24rpx;
  background: #ffffff;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.total {
  font-size: 34rpx;
}
.checkout {
  width: 240rpx;
}
</style>

