<template>
  <view class="page">
    <picker :range="typeNames" @change="selectType">
      <view class="input field">{{ typeNames[typeIndex] }}</view>
    </picker>
    <input class="input field" v-model="form.title" placeholder="发票抬头" />
    <input class="input field" v-model="form.tax_no" placeholder="税号，企业发票填写" />
    <input class="input field" v-model="form.email" placeholder="接收邮箱" />
    <input class="input field" v-model="form.content" placeholder="发票内容" />
    <view class="btn" @tap="submit">提交发票申请</view>
  </view>
</template>

<script>
import { applyInvoice } from "../../api/order";

export default {
  data() {
    return {
      id: "",
      typeIndex: 0,
      typeNames: ["个人", "企业"],
      typeValues: ["personal", "company"],
      form: { title: "", tax_no: "", email: "", content: "商品明细" }
    };
  },
  onLoad(query) {
    this.id = query.id;
  },
  methods: {
    selectType(event) {
      this.typeIndex = Number(event.detail.value);
    },
    async submit() {
      if (!this.form.title) {
        uni.showToast({ title: "请填写发票抬头", icon: "none" });
        return;
      }
      await applyInvoice(this.id, {
        ...this.form,
        invoice_type: this.typeValues[this.typeIndex]
      });
      uni.showToast({ title: "已提交" });
      setTimeout(() => uni.navigateBack(), 300);
    }
  }
};
</script>

<style scoped>
.field {
  margin-bottom: 20rpx;
}
</style>
