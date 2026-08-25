<template>
  <view class="page">
    <view class="card section" @tap="chooseAddress">
      <view class="between">
        <view class="title">收货地址</view>
        <text class="subtle">选择</text>
      </view>
      <view v-if="address.id" class="address">
        <view>{{ address.receiver_name }} {{ address.receiver_mobile }}</view>
        <view class="subtle">{{ fullAddress(address) }}</view>
      </view>
      <view v-else class="subtle address">请选择收货地址</view>
    </view>

    <view class="card section">
      <view class="title">商品信息</view>
      <view v-if="fromCart">
        <view v-for="item in cartItems" :key="item.id" class="line">
          <view class="between">
            <text>{{ item.product_title }}</text>
            <text>x {{ item.quantity }}</text>
          </view>
          <view class="subtle">{{ item.spec_text || item.sku_code }}</view>
        </view>
      </view>
      <view v-else>
        <view class="line product-line">
          <view class="name">{{ productTitle || "商品" }}</view>
          <view class="subtle">{{ skuText || `SKU #${sku}` }}</view>
        </view>
        <view class="between line">
          <text>数量</text>
          <text>{{ quantity }}</text>
        </view>
      </view>
    </view>

    <view class="card section">
      <view class="between">
        <view class="title">优惠券</view>
        <picker :range="couponNames" @change="selectCoupon">
          <text class="subtle">{{ selectedCoupon ? selectedCoupon.template_name || `优惠券 #${selectedCoupon.id}` : "不使用优惠券" }}</text>
        </picker>
      </view>
    </view>

    <view class="card section">
      <textarea class="remark" v-model="remark" placeholder="订单备注，可选" />
    </view>

    <view class="btn" @tap="submit">提交订单</view>
  </view>
</template>

<script>
import { getMyCoupons } from "../../api/marketing";
import { createOrder, getAddresses, getCartItems } from "../../api/order";

export default {
  data() {
    return {
      sku: "",
      skuText: "",
      productTitle: "",
      quantity: 1,
      fromCart: false,
      cartItems: [],
      address: {},
      coupons: [],
      selectedCoupon: null,
      remark: ""
    };
  },
  onLoad(query) {
    this.sku = query.sku || "";
    this.skuText = query.sku_text ? decodeURIComponent(query.sku_text) : "";
    this.productTitle = query.product_title ? decodeURIComponent(query.product_title) : "";
    this.quantity = Number(query.quantity || 1);
    this.fromCart = query.from_cart === "1";
  },
  onShow() {
    this.loadAddress();
    this.loadCoupons();
    if (this.fromCart) this.loadCartItems();
  },
  computed: {
    couponNames() {
      return ["不使用优惠券"].concat(this.coupons.map((item) => item.template_name || `优惠券 #${item.id}`));
    }
  },
  methods: {
    async loadAddress() {
      const selected = uni.getStorageSync("emall_selected_address");
      if (selected && selected.id) {
        this.address = selected;
        return;
      }
      const data = await getAddresses();
      const list = data.results || data || [];
      this.address = list.find((item) => item.is_default) || list[0] || {};
    },
    async loadCoupons() {
      const data = await getMyCoupons({ status: "unused" });
      this.coupons = data.results || data || [];
    },
    async loadCartItems() {
      const data = await getCartItems();
      this.cartItems = (data.results || data || []).filter((item) => item.selected);
    },
    fullAddress(item) {
      return [item.province, item.city, item.district, item.address_detail].filter(Boolean).join(" ");
    },
    chooseAddress() {
      uni.navigateTo({ url: "/pages/address/index?mode=select" });
    },
    selectCoupon(event) {
      const index = Number(event.detail.value);
      this.selectedCoupon = index > 0 ? this.coupons[index - 1] : null;
    },
    async submit() {
      if (!this.address.id) {
        uni.showToast({ title: "请选择收货地址", icon: "none" });
        return;
      }
      const payload = {
        from_cart: this.fromCart,
        address_id: this.address.id,
        coupon_id: this.selectedCoupon ? this.selectedCoupon.id : null,
        remark: this.remark
      };
      if (!this.fromCart) {
        payload.items = [{ sku_id: Number(this.sku), quantity: this.quantity }];
      }
      const order = await createOrder(payload);
      uni.removeStorageSync("emall_selected_address");
      uni.redirectTo({ url: `/pages/order/detail?id=${order.id}` });
    }
  }
};
</script>

<style scoped>
.line {
  margin-top: 18rpx;
}
.product-line {
  line-height: 42rpx;
}
.name {
  color: #333;
  font-weight: 600;
}
.address {
  margin-top: 18rpx;
  line-height: 42rpx;
}
.remark {
  width: 100%;
  height: 140rpx;
  font-size: 28rpx;
}
</style>
