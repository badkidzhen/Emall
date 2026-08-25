<template>
  <view class="page">
    <view class="hero">
      <view>
        <view class="hero-title">Emall 分销商城</view>
        <view class="hero-sub">精选商品、团队奖励、城市代理</view>
      </view>
      <view class="hero-action" @tap="go('/pages/coupon/center')">领券</view>
    </view>

    <view class="quick-grid section">
      <view class="quick" @tap="go('/pages/coupon/center')">优惠券</view>
      <view class="quick" @tap="go('/pages/group/index')">团购</view>
      <view class="quick" @tap="go('/pages/seckill/index')">秒杀</view>
      <view class="quick" @tap="go('/pages/team/index')">团队</view>
      <view class="quick" @tap="go('/pages/agent/index')">代理</view>
      <view class="quick" @tap="go('/pages/reward/index')">奖金池</view>
      <view class="quick" @tap="go('/pages/wallet/index')">钱包</view>
      <view class="quick" @tap="go('/pages/address/index')">地址</view>
    </view>

    <view class="between section">
      <text class="title">精选商品</text>
      <text class="subtle" @tap="go('/pages/product/list')">全部</text>
    </view>

    <view v-if="products.length" class="grid-2">
      <product-card v-for="item in products" :key="item.id" :product="item" />
    </view>
    <empty-state v-else title="暂无商品" desc="请先在后台创建商品和 SKU" />
  </view>
</template>

<script>
import { getProducts } from "../../api/catalog";

export default {
  data() {
    return { products: [] };
  },
  onShow() {
    this.loadProducts();
  },
  methods: {
    async loadProducts() {
      try {
        const data = await getProducts({ page: 1 });
        this.products = data.results || data || [];
      } catch (err) {
        console.error("loadProducts failed", err);
        this.products = [];
      }
    },
    go(url) {
      uni.navigateTo({ url });
    }
  }
};
</script>

<style scoped>
.hero {
  min-height: 220rpx;
  padding: 32rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #ff2442, #ff6b35);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}
.hero-title {
  font-size: 40rpx;
  font-weight: 700;
}
.hero-sub {
  margin-top: 12rpx;
  font-size: 24rpx;
  opacity: 0.9;
}
.hero-action {
  width: 116rpx;
  height: 64rpx;
  border-radius: 8rpx;
  background: #ffffff;
  color: #ff2442;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}
.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
}
.quick {
  height: 88rpx;
  background: #ffffff;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333333;
  font-size: 24rpx;
}
</style>

