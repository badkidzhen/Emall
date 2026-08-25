<template>
  <view class="category-page">
    <view class="left">
      <view
        v-for="item in categories"
        :key="item.id"
        class="left-item"
        :class="{ active: current && current.id === item.id }"
        @tap="select(item)"
      >
        {{ item.name }}
      </view>
    </view>
    <view class="right">
      <image v-if="current && current.banner" class="banner" :src="current.banner" mode="aspectFill" />
      <view v-if="current" class="section-title">{{ current.name }}</view>
      <view v-for="child in children" :key="child.id" class="category-card" @tap="openList(child)">
        <view>
          <view class="name">{{ child.name }}</view>
          <view class="subtle">{{ (child.children || []).length }} 个子分类</view>
        </view>
        <text class="arrow">›</text>
      </view>
      <view class="btn" @tap="openList(current)">查看商品</view>
    </view>
  </view>
</template>

<script>
import { getCategoryTree } from "../../api/catalog";

export default {
  data() {
    return { categories: [], current: null };
  },
  onShow() {
    this.load();
  },
  computed: {
    children() {
      return (this.current && this.current.children) || [];
    }
  },
  methods: {
    async load() {
      this.categories = await getCategoryTree();
      this.current = this.categories[0] || null;
    },
    select(item) {
      this.current = item;
    },
    openList(item) {
      if (!item) return;
      uni.navigateTo({ url: `/pages/product/list?category=${item.id}&title=${item.name}` });
    }
  }
};
</script>

<style scoped>
.category-page {
  min-height: 100vh;
  display: flex;
  background: #f5f5f5;
}
.left {
  width: 190rpx;
  background: #ffffff;
}
.left-item {
  min-height: 92rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666666;
  font-size: 26rpx;
}
.left-item.active {
  color: #ff2442;
  background: #fff5f5;
  font-weight: 700;
}
.right {
  flex: 1;
  padding: 24rpx;
}
.banner {
  width: 100%;
  height: 180rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}
.section-title {
  font-size: 32rpx;
  font-weight: 700;
  margin-bottom: 20rpx;
}
.category-card {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 18rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.name {
  font-size: 28rpx;
  font-weight: 600;
}
.arrow {
  font-size: 42rpx;
  color: #999999;
}
</style>
