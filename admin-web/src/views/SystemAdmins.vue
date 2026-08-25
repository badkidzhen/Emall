<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">管理员管理</div>
        <el-input v-model="search" clearable placeholder="搜索管理员" style="width: 220px" @keyup.enter="load" />
      </div>
      <el-button type="primary" @click="openCreate">新增管理员</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="mobile" label="手机号" min-width="140" />
        <el-table-column prop="nickname" label="昵称" min-width="140" />
        <el-table-column label="员工" width="90">
          <template #default="{ row }"><StatusTag :value="row.is_staff" /></template>
        </el-table-column>
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.is_active" /></template>
        </el-table-column>
        <el-table-column prop="date_joined" label="创建时间" min-width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="visible" :title="mode === 'create' ? '新增管理员' : '编辑管理员'" width="700px">
      <el-form :model="form" label-width="100px">
        <div class="form-grid">
          <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
          <el-form-item label="密码"><el-input v-model="form.password" type="password" placeholder="留空则不修改" /></el-form-item>
          <el-form-item label="手机号"><el-input v-model="form.mobile" /></el-form-item>
          <el-form-item label="昵称"><el-input v-model="form.nickname" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
          <el-form-item label="超级管理员"><el-switch v-model="form.is_superuser" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const search = ref("");
const rows = ref([]);
const visible = ref(false);
const mode = ref("create");
const form = reactive(defaultForm());

function defaultForm() {
  return { id: null, username: "", password: "", mobile: "", nickname: "", role: "admin", is_staff: true, is_active: true, is_superuser: false };
}

async function load() {
  const params = new URLSearchParams({ role: "admin", page: "1" });
  if (search.value) params.set("search", search.value);
  const data = await http.get(`/users/?${params.toString()}`);
  rows.value = data.results || [];
}

function openCreate() {
  Object.assign(form, defaultForm());
  mode.value = "create";
  visible.value = true;
}

function edit(row) {
  Object.assign(form, defaultForm(), row, { password: "" });
  mode.value = "edit";
  visible.value = true;
}

function payload() {
  const data = {
    username: form.username,
    mobile: form.mobile || null,
    nickname: form.nickname,
    role: "admin",
    is_staff: true,
    is_active: form.is_active,
    is_superuser: form.is_superuser
  };
  if (form.password) data.password = form.password;
  return data;
}

async function submit() {
  if (mode.value === "create") await http.post("/users/", payload());
  else await http.patch(`/users/${form.id}/`, payload());
  ElMessage.success("管理员已保存");
  visible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除管理员 ${row.username}？`, "提示", { type: "warning" });
  await http.delete(`/users/${row.id}/`);
  ElMessage.success("管理员已删除");
  await load();
}

onMounted(load);
</script>
