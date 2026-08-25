<template>
  <view class="product-card" @tap="openDetail">
    <image v-if="product.cover" class="cover" :src="product.cover" mode="aspectFill" />
    <view v-else class="cover cover-placeholder">Emall</view>
    <view class="info">
      <view class="name">{{ product.title }}</view>
      <view class="desc">{{ product.sub_title || "精选好物" }}</view>
      <view class="between">
        <text class="price">¥{{ product.price }}</text>
        <text class="stock">库存 {{ product.total_stock || 0 }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: "ProductCard",
  props: {
    product: { type: Object, required: true }
  },
  methods: {
    openDetail() {
      uni.navigateTo({ url: `/pages/product/detail?id=${this.product.id}` });
    }
  }
};
</script>

<style scoped>
.product-card {
  background: #ffffff;
  border-radius: 12rpx;
  overflow: hidden;
}
.cover {
  width: 100%;
  height: 240rpx;
  background: #f5f5f5;
}
.cover-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b8c0cc;
  font-size: 42rpx;
  font-weight: 700;
}
.info {
  padding: 18rpx;
}
.name {
  font-size: 28rpx;
  font-weight: 600;
  line-height: 38rpx;
  height: 76rpx;
  overflow: hidden;
}
.desc {
  margin-top: 8rpx;
  color: #666666;
  font-size: 22rpx;
  height: 32rpx;
  overflow: hidden;
}
.stock {
  color: #999999;
  font-size: 22rpx;
}
</style>
