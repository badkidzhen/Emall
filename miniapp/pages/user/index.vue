<template>
  <view class="page">
    <view class="profile">
      <view>
        <view class="title">{{ user.nickname || user.username || "未登录" }}</view>
        <view class="subtle">{{ user.level_name || "普通用户" }} · {{ realnameText }}</view>
      </view>
      <view v-if="!loggedIn" class="login-btn" @tap="go('/pages/user/login')">登录</view>
      <view v-else class="logout-btn" @tap="logout">切换账号</view>
    </view>

    <view class="menu">
      <view class="menu-item" @tap="go('/pages/order/list')">我的订单</view>
      <view class="menu-item" @tap="go('/pages/coupon/my')">我的优惠券</view>
      <view class="menu-item" @tap="go('/pages/address/index')">收货地址</view>
      <view class="menu-item" @tap="go('/pages/user/realname')">实名认证</view>
      <view class="menu-item" @tap="go('/pages/team/index')">团队中心</view>
      <view class="menu-item" @tap="go('/pages/agent/index')">代理中心</view>
      <view class="menu-item" @tap="go('/pages/reward/index')">奖金池</view>
      <view class="menu-item" @tap="go('/pages/wallet/index')">钱包提现</view>
    </view>
  </view>
</template>

<script>
import { getMe } from "../../api/auth";
import { clearTokens, isLoggedIn } from "../../common/auth";

export default {
  data() {
    return { user: {}, loggedIn: false };
  },
  computed: {
    realnameText() {
      return {
        unverified: "未实名",
        pending: "实名审核中",
        verified: "已实名",
        rejected: "实名被拒"
      }[this.user.realname_status] || "未实名";
    }
  },
  onShow() {
    this.loggedIn = isLoggedIn();
    if (this.loggedIn) this.load();
    else this.user = {};
  },
  methods: {
    async load() {
      this.user = await getMe();
    },
    go(url) {
      uni.navigateTo({ url });
    },
    logout() {
      uni.showModal({
        title: "提示",
        content: "确定退出当前账号并切换到登录页吗？",
        success: (res) => {
          if (!res.confirm) return;
          clearTokens();
          uni.removeStorageSync("emall_selected_address");
          uni.removeStorageSync("emall_edit_address");
          this.user = {};
          this.loggedIn = false;
          uni.reLaunch({ url: "/pages/user/login" });
        }
      });
    }
  }
};
</script>

<style scoped>
.profile {
  background: #ffffff;
  border-radius: 12rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}
.login-btn,
.logout-btn {
  min-width: 120rpx;
  height: 64rpx;
  padding: 0 20rpx;
  border-radius: 8rpx;
  background: #ff2442;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.menu {
  background: #ffffff;
  border-radius: 12rpx;
  overflow: hidden;
}
.menu-item {
  height: 96rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  border-bottom: 1rpx solid #e8e8e8;
}
.menu-item:last-child {
  border-bottom: 0;
}
</style>
