<template>
  <view class="page">
    <input class="input field" v-model="form.receiver_name" placeholder="收货人" />
    <input class="input field" v-model="form.receiver_mobile" placeholder="手机号" />
    <picker mode="region" :value="regionValue" @change="regionChanged">
      <view class="input field region-field">
        <text :class="{ placeholder: !regionLabel }">{{ regionLabel || "省 / 市 / 区县" }}</text>
      </view>
    </picker>
    <input class="input field" v-model="form.address_detail" placeholder="详细地址" />
    <input class="input field" v-model="form.postal_code" placeholder="邮编，可选" />
    <view class="card section between">
      <text>设为默认地址</text>
      <switch :checked="form.is_default" @change="form.is_default = $event.detail.value" />
    </view>
    <view class="btn submit" @tap="submit">保存地址</view>
  </view>
</template>

<script>
import { createAddress, updateAddress } from "../../api/order";

export default {
  data() {
    return {
      id: "",
      form: {
        receiver_name: "",
        receiver_mobile: "",
        province: "",
        city: "",
        district: "",
        address_detail: "",
        postal_code: "",
        is_default: false
      },
      regionValue: [],
      regionLabel: ""
    };
  },
  onLoad(query) {
    this.id = query.id || "";
    if (this.id) {
      const saved = uni.getStorageSync("emall_edit_address");
      if (saved && String(saved.id) === String(this.id)) Object.assign(this.form, saved);
    }
    this.syncRegion();
  },
  methods: {
    syncRegion() {
      this.regionValue = [this.form.province, this.form.city, this.form.district].filter(Boolean);
      this.regionLabel = this.regionValue.join(" / ");
    },
    regionChanged(event) {
      const [province = "", city = "", district = ""] = event.detail.value || [];
      this.form.province = province;
      this.form.city = city;
      this.form.district = district;
      this.regionValue = event.detail.value || [];
      this.regionLabel = this.regionValue.join(" / ");
    },
    async submit() {
      if (!this.form.receiver_name || !this.form.receiver_mobile || !this.form.address_detail) {
        uni.showToast({ title: "请填写收货人、手机号和地址", icon: "none" });
        return;
      }
      if (!this.form.province || !this.form.city || !this.form.district) {
        uni.showToast({ title: "请选择省市区县", icon: "none" });
        return;
      }
      if (this.id) {
        await updateAddress(this.id, this.form);
      } else {
        await createAddress(this.form);
      }
      uni.removeStorageSync("emall_edit_address");
      uni.showToast({ title: "已保存" });
      setTimeout(() => uni.navigateBack(), 300);
    }
  }
};
</script>

<style scoped>
.field {
  margin-bottom: 20rpx;
}
.region-field {
  display: flex;
  align-items: center;
  color: #333;
}
.placeholder {
  color: #999;
}
.submit {
  margin-top: 30rpx;
}
</style>
