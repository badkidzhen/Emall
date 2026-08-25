<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="title">Emall 管理后台</div>
      <el-form :model="form" class="form" @keyup.enter="submit">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" show-password placeholder="密码" />
        </el-form-item>
        <el-button type="primary" class="login-btn" :loading="loading" @click="submit">登录</el-button>
      </el-form>
      <div class="hint">测试账号：demo_admin / demoAdmin123456</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import http from "../utils/http";
import { useAuthStore } from "../store/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const form = ref({
  username: "demo_admin",
  password: "demoAdmin123456"
});

async function submit() {
  loading.value = true;
  try {
    const data = await http.post("/auth/token/", form.value);
    auth.setTokens(data.access, data.refresh);
    const me = await http.get("/users/me/");
    auth.setUser(me);
    router.push("/dashboard");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef2ff, #f8fafc);
}
.login-card {
  width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
}
.title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
}
.login-btn {
  width: 100%;
}
.hint {
  margin-top: 16px;
  color: #94a3b8;
  font-size: 12px;
}
</style>

