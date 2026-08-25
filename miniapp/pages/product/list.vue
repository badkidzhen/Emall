<template>
  <view class="page">
    <view class="search-row section">
      <input class="input search-input" v-model="keyword" placeholder="搜索商品" confirm-type="search" @confirm="load" />
      <view class="search-btn" @tap="load">搜索</view>
    </view>
    <view v-if="products.length" class="grid-2">
      <product-card v-for="item in products" :key="item.id" :product="item" />
    </view>
    <empty-state v-else title="暂无商品" />
  </view>
</template>

<script>
import { getProducts } from "../../api/catalog";

export default {
  data() {
    return { category: "", keyword: "", products: [] };
  },
  onLoad(query) {
    this.category = query.category || "";
    if (query.title) uni.setNavigationBarTitle({ title: query.title });
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      const params = {};
      if (this.category) params.category = this.category;
      if (this.keyword) params.search = this.keyword;
      const data = await getProducts(params);
      this.products = data.results || data || [];
    }
  }
};
</script>

<style scoped>
.search-row {
  display: flex;
  gap: 16rpx;
}
.search-input {
  flex: 1;
}
.search-btn {
  width: 120rpx;
  height: 80rpx;
  border-radius: 8rpx;
  background: #ff2442;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

