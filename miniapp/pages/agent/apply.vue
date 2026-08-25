<template>
  <view class="page">
    <picker :range="levelNames" @change="selectLevel">
      <view class="input field">{{ levelNames[levelIndex] }}</view>
    </picker>
    <input class="input field" v-model="form.region_code" placeholder="区域编码" />
    <input class="input field" v-model="form.region_name" placeholder="区域名称" />
    <input class="input field" v-model="form.contact_name" placeholder="联系人" />
    <input class="input field" v-model="form.contact_phone" placeholder="联系电话" />
    <view class="btn submit" @tap="submit">提交申请</view>
  </view>
</template>

<script>
import { applyAgent } from "../../api/user";

export default {
  data() {
    return {
      levelIndex: 1,
      levelNames: ["区县级", "市级", "省级"],
      levelValues: [1, 2, 3],
      form: {
        level: 2,
        region_code: "",
        region_name: "",
        contact_name: "",
        contact_phone: ""
      }
    };
  },
  methods: {
    selectLevel(event) {
      this.levelIndex = Number(event.detail.value);
      this.form.level = this.levelValues[this.levelIndex];
    },
    async submit() {
      await applyAgent(this.form);
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
