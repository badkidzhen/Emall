<template>
  <view class="page">
    <view class="card section">
      <view class="title">申请售后</view>
      <view class="subtle">最多可申请 ¥{{ maxAmount }}</view>
    </view>
    <picker :range="typeNames" @change="selectType">
      <view class="input field">{{ typeNames[typeIndex] }}</view>
    </picker>
    <input class="input field" v-model="form.amount" type="digit" placeholder="退款金额" />
    <textarea class="input textarea field" v-model="form.reason" placeholder="退款原因" />
    <view class="btn" @tap="submit">提交申请</view>
  </view>
</template>

<script>
import { applyRefund } from "../../api/order";

export default {
  data() {
    return {
      id: "",
      maxAmount: "0.00",
      typeIndex: 0,
      typeNames: ["仅退款", "退货退款"],
      typeValues: ["refund_only", "return_and_refund"],
      form: { amount: "", reason: "" }
    };
  },
  onLoad(query) {
    this.id = query.id;
    this.maxAmount = query.amount || "0.00";
    this.form.amount = this.maxAmount;
  },
  methods: {
    selectType(event) {
      this.typeIndex = Number(event.detail.value);
    },
    async submit() {
      if (!this.form.amount || !this.form.reason) {
        uni.showToast({ title: "请填写金额和原因", icon: "none" });
        return;
      }
      await applyRefund(this.id, {
        refund_type: this.typeValues[this.typeIndex],
        amount: this.form.amount,
        reason: this.form.reason
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
.textarea {
  width: 100%;
  height: 180rpx;
  padding-top: 20rpx;
}
</style>
