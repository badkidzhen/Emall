<template>
  <view class="page">
    <view class="card section">
      <view class="title">实名认证</view>
      <view class="subtle">提现前建议先完成实名认证；后续可接入第三方实名 API。</view>
    </view>
    <input class="input field" v-model="form.realname" placeholder="真实姓名" />
    <input class="input field" v-model="form.id_card" placeholder="身份证号" />
    <view class="btn" @tap="submit">提交认证</view>
  </view>
</template>

<script>
import { getMe } from "../../api/auth";
import { submitRealname } from "../../api/user";

export default {
  data() {
    return { form: { realname: "", id_card: "" } };
  },
  async onShow() {
    const user = await getMe();
    this.form.realname = user.realname || "";
    this.form.id_card = user.id_card || "";
  },
  methods: {
    async submit() {
      await submitRealname(this.form);
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
