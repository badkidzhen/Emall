<template>
  <view class="page">
    <view class="card login-card">
      <view class="title">登录</view>
      <input class="input field" v-model="username" placeholder="用户名" />
      <input class="input field" v-model="password" placeholder="密码" password />
      <view class="btn" @tap="submit">测试账号登录</view>
      <view class="btn secondary wx-btn" @tap="wechatLogin">微信登录</view>
      <view class="subtle tip">微信登录接口后续再接入；当前按钮先获取小程序 code 作为占位。</view>
    </view>
  </view>
</template>

<script>
import { login } from "../../api/auth";
import { setTokens } from "../../common/auth";

export default {
  data() {
    return { username: "", password: "" };
  },
  methods: {
    async submit() {
      const data = await login(this.username, this.password);
      setTokens(data.access, data.refresh);
      uni.showToast({ title: "登录成功" });
      setTimeout(() => uni.switchTab({ url: "/pages/user/index" }), 300);
    },
    wechatLogin() {
      uni.login({
        provider: "weixin",
        success: (res) => {
          uni.showModal({
            title: "微信登录占位",
            content: `已获取 code：${res.code || "空"}。后续接入后端微信登录接口时会在这里完成 JWT 换取。`,
            showCancel: false
          });
        },
        fail: () => uni.showToast({ title: "微信登录不可用", icon: "none" })
      });
    }
  }
};
</script>

<style scoped>
.login-card {
  margin-top: 160rpx;
}
.field {
  margin-top: 24rpx;
}
.btn {
  margin-top: 32rpx;
}
.wx-btn {
  margin-top: 20rpx;
}
.tip {
  margin-top: 20rpx;
  line-height: 38rpx;
}
</style>
