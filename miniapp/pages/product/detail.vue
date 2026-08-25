<template>
  <view class="detail">
    <image v-if="coverImage" class="cover" :src="coverImage" mode="aspectFill" />
    <view v-else class="cover cover-placeholder">Emall</view>

    <view class="card product-info">
      <view class="title">{{ product.title }}</view>
      <view class="subtle">{{ product.sub_title }}</view>
      <view class="price-line">¥{{ currentPrice }}</view>
      <view class="subtle">库存 {{ currentStock }}</view>
    </view>

    <view class="card section">
      <view class="block-title">规格</view>
      <view class="sku-list">
        <view
          v-for="(sku, index) in skuList"
          :key="sku.id"
          class="sku"
          :class="{ active: selectedSku && selectedSku.id === sku.id }"
          :data-index="index"
          @tap="selectSku"
        >
          {{ skuText(sku) }}
        </view>
      </view>
    </view>

    <view class="card section">
      <view class="between">
        <view class="block-title">数量</view>
        <view class="stepper">
          <text @tap="changeQty(-1)">-</text>
          <text class="qty">{{ quantity }}</text>
          <text @tap="changeQty(1)">+</text>
        </view>
      </view>
    </view>

    <view class="card section">
      <view class="block-title">详情</view>
      <view class="detail-text">{{ product.detail || "暂无详情" }}</view>
    </view>

    <view class="bottom-bar">
      <view class="bar-btn secondary" @tap="addCart">加入购物车</view>
      <view class="bar-btn" @tap="buyNow">立即购买</view>
    </view>
  </view>
</template>

<script>
import { getProduct } from "../../api/catalog";
import { addCartItem } from "../../api/order";

export default {
  data() {
    return {
      id: "",
      product: {},
      selectedSku: null,
      quantity: 1
    };
  },
  computed: {
    skuList() {
      return Array.isArray(this.product.skus) ? this.product.skus : [];
    },
    coverImage() {
      return (this.selectedSku && this.selectedSku.image) || this.product.cover || "";
    },
    currentPrice() {
      return (this.selectedSku && this.selectedSku.price) || this.product.price || "0.00";
    },
    currentStock() {
      if (this.selectedSku && this.selectedSku.stock !== undefined && this.selectedSku.stock !== null) {
        return this.selectedSku.stock;
      }
      return this.product.total_stock || 0;
    }
  },
  onLoad(query) {
    this.id = query.id;
    this.load();
  },
  methods: {
    async load() {
      this.product = await getProduct(this.id);
      this.selectedSku = this.skuList[0] || null;
    },
    selectSku(event) {
      const index = Number(event.currentTarget.dataset.index);
      this.selectedSku = this.skuList[index] || null;
    },
    changeQty(delta) {
      this.quantity = Math.max(1, this.quantity + delta);
    },
    skuText(sku) {
      const specs = sku.specs || {};
      const text = Object.keys(specs).map((key) => specs[key]).join(" / ");
      return text || sku.sku_code;
    },
    ensureSku() {
      if (!this.selectedSku) {
        uni.showToast({ title: "请选择规格", icon: "none" });
        return false;
      }
      if (Number(this.selectedSku.stock || 0) < this.quantity) {
        uni.showToast({ title: "库存不足", icon: "none" });
        return false;
      }
      return true;
    },
    async addCart() {
      if (!this.ensureSku()) return;
      await addCartItem({ sku: this.selectedSku.id, quantity: this.quantity });
      uni.showToast({ title: "已加入购物车" });
    },
    buyNow() {
      if (!this.ensureSku()) return;
      const skuText = encodeURIComponent(this.skuText(this.selectedSku));
      const title = encodeURIComponent(this.product.title || "");
      uni.navigateTo({
        url: `/pages/order/create?sku=${this.selectedSku.id}&quantity=${this.quantity}&sku_text=${skuText}&product_title=${title}`
      });
    }
  }
};
</script>

<style scoped>
.detail {
  padding-bottom: 120rpx;
}
.cover {
  width: 100%;
  height: 520rpx;
  background: #f5f5f5;
}
.cover-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b8c0cc;
  font-size: 64rpx;
  font-weight: 700;
}
.product-info {
  margin: 24rpx;
}
.price-line {
  margin-top: 18rpx;
  color: #ff2442;
  font-size: 40rpx;
  font-weight: 700;
}
.block-title {
  font-size: 30rpx;
  font-weight: 700;
}
.sku-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-top: 18rpx;
}
.sku {
  padding: 14rpx 22rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  color: #333333;
  font-size: 24rpx;
}
.sku.active {
  background: #fff5f5;
  color: #ff2442;
  border: 1rpx solid #ff2442;
}
.stepper {
  display: flex;
  align-items: center;
  border: 1rpx solid #e8e8e8;
  border-radius: 8rpx;
  overflow: hidden;
}
.stepper text {
  min-width: 58rpx;
  height: 52rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.qty {
  border-left: 1rpx solid #e8e8e8;
  border-right: 1rpx solid #e8e8e8;
}
.detail-text {
  margin-top: 18rpx;
  color: #666666;
  line-height: 44rpx;
}
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 108rpx;
  background: #ffffff;
  padding: 16rpx 24rpx;
  box-sizing: border-box;
  display: flex;
  gap: 18rpx;
}
.bar-btn {
  flex: 1;
  border-radius: 8rpx;
  background: #ff2442;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bar-btn.secondary {
  background: #fff5f5;
  color: #ff2442;
}
</style>
