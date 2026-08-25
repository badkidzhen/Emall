<template>
  <view class="page">
    <picker :range="channelNames" @change="selectChannel">
      <view class="input field">{{ channelNames[channelIndex] }}</view>
    </picker>
    <input class="input field" v-model="form.amount" type="digit" placeholder="提现金额" />
    <input class="input field" v-model="form.account_name" placeholder="账户姓名" />
    <input class="input field" v-model="form.account_no" placeholder="收款账号 / OpenID / 银行卡号" />
    <view class="subtle section">真实微信打款或银行卡 API 参数后续配置；当前可提交申请，由后台审核打款。</view>
    <view class="btn submit" @tap="submit">提交提现</view>
  </view>
</template>

<script>
import { applyWithdraw } from "../../api/user";

export default {
  data() {
    return {
      channelIndex: 0,
      channelNames: ["手动打款", "微信提现", "银行卡"],
      channelValues: ["manual", "wechat", "bank"],
      form: { amount: "", account_name: "", account_no: "" }
    };
  },
  methods: {
    selectChannel(event) {
      this.channelIndex = Number(event.detail.value);
    },
    async submit() {
      await applyWithdraw({ ...this.form, channel: this.channelValues[this.channelIndex] });
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
.submit {
  margin-top: 30rpx;
}
</style>
