<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">用户管理</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="mobile" label="手机号" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }"><StatusTag :value="row.role" :map="roleMap" /></template>
        </el-table-column>
        <el-table-column prop="level_name" label="会员等级" width="120" />
        <el-table-column label="分销商" width="100">
          <template #default="{ row }"><StatusTag :value="row.is_distributor" /></template>
        </el-table-column>
        <el-table-column prop="city_agent_level" label="代理等级" width="100" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        class="table-pagination"
        background
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @current-change="changePage"
      />
    </div>

    <el-dialog v-model="dialogVisible" title="编辑用户" width="760px">
      <el-form :model="form" label-width="100px">
        <div class="form-grid">
          <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
          <el-form-item label="手机号"><el-input v-model="form.mobile" /></el-form-item>
          <el-form-item label="昵称"><el-input v-model="form.nickname" /></el-form-item>
          <el-form-item label="真实姓名"><el-input v-model="form.realname" /></el-form-item>
          <el-form-item label="身份证号"><el-input v-model="form.id_card" /></el-form-item>
          <el-form-item label="角色">
            <el-select v-model="form.role">
              <el-option v-for="item in roleOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="会员等级">
            <el-select v-model="form.level" clearable>
              <el-option v-for="item in levels" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="上级ID"><el-input v-model="form.parent" /></el-form-item>
          <el-form-item label="代理编码"><el-input v-model="form.city_code" /></el-form-item>
          <el-form-item label="代理等级">
            <el-select v-model="form.city_agent_level">
              <el-option v-for="item in cityAgentLevelOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="分销商">
            <el-switch v-model="form.is_distributor" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
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

const rows = ref([]);
const levels = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const dialogVisible = ref(false);

const roleOptions = [
  { label: "普通用户", value: "normal" },
  { label: "会员", value: "member" },
  { label: "分销商", value: "distributor" },
  { label: "团队长", value: "team_leader" },
  { label: "城市代理", value: "city_agent" },
  { label: "平台管理员", value: "admin" }
];
const roleMap = Object.fromEntries(roleOptions.map((item) => [item.value, { label: item.label, type: item.value === "admin" ? "danger" : "info" }]));

const cityAgentLevelOptions = [
  { label: "无", value: 0 },
  { label: "区县级", value: 1 },
  { label: "市级", value: 2 },
  { label: "省级", value: 3 }
];

const form = reactive({
  id: null,
  username: "",
  mobile: "",
  nickname: "",
  realname: "",
  id_card: "",
  role: "normal",
  level: null,
  parent: null,
  city_code: "",
  is_distributor: false,
  city_agent_level: 0
});

async function load() {
  const [users, memberLevels] = await Promise.all([
    http.get(`/users/?page=${page.value}`),
    http.get("/users/levels/?page=1")
  ]);
  rows.value = users.results || [];
  total.value = users.count || 0;
  levels.value = memberLevels.results || [];
}

function edit(row) {
  Object.assign(form, {
    id: row.id,
    username: row.username || "",
    mobile: row.mobile || "",
    nickname: row.nickname || "",
    realname: row.realname || "",
    id_card: row.id_card || "",
    role: row.role || "normal",
    level: row.level || null,
    parent: row.parent || null,
    city_code: row.city_code || "",
    is_distributor: Boolean(row.is_distributor),
    city_agent_level: row.city_agent_level ?? 0
  });
  dialogVisible.value = true;
}

async function submit() {
  if (!form.username.trim()) {
    ElMessage.warning("请输入用户名");
    return;
  }
  const payload = {
    username: form.username,
    mobile: form.mobile || null,
    nickname: form.nickname,
    realname: form.realname,
    id_card: form.id_card,
    role: form.role,
    level: form.level || null,
    parent: form.parent || null,
    city_code: form.city_code || null,
    is_distributor: form.is_distributor,
    city_agent_level: Number(form.city_agent_level)
  };
  await http.put(`/users/${form.id}/`, payload);
  ElMessage.success("用户保存成功");
  dialogVisible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除用户 ${row.username} ?`, "提示", { type: "warning" });
  await http.delete(`/users/${row.id}/`);
  ElMessage.success("用户已删除");
  await load();
}

function changePage(value) {
  page.value = value;
  load();
}

onMounted(load);
</script>
