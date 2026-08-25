<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">实名认证</div>
        <el-select v-model="query.realname_status" clearable placeholder="认证状态" style="width: 160px" @change="search">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>

    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="用户ID" width="90" />
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="mobile" label="手机号" min-width="140" />
        <el-table-column prop="realname" label="真实姓名" width="130" />
        <el-table-column prop="id_card" label="身份证号" min-width="190" show-overflow-tooltip />
        <el-table-column label="状态" width="130">
          <template #default="{ row }"><StatusTag :value="row.realname_status" :map="statusMap" /></template>
        </el-table-column>
        <el-table-column prop="realname_remark" label="备注" min-width="160" show-overflow-tooltip />
        <el-table-column prop="realname_verified_at" label="通过时间" min-width="180" />
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :disabled="row.realname_status !== 'pending'" @click="audit(row, true)">通过</el-button>
            <el-button link type="danger" :disabled="row.realname_status !== 'pending'" @click="audit(row, false)">拒绝</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        class="table-pagination"
        background
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="query.page"
        @current-change="changePage"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Refresh } from "@element-plus/icons-vue";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const rows = ref([]);
const total = ref(0);
const pageSize = 20;
const query = reactive({ page: 1, realname_status: "pending" });

const statusOptions = [
  { label: "未认证", value: "unverified" },
  { label: "待审核", value: "pending" },
  { label: "已通过", value: "verified" },
  { label: "已拒绝", value: "rejected" }
];

const statusMap = {
  unverified: { label: "未认证", type: "info" },
  pending: { label: "待审核", type: "warning" },
  verified: { label: "已通过", type: "success" },
  rejected: { label: "已拒绝", type: "danger" }
};

async function load() {
  const params = new URLSearchParams({ page: String(query.page) });
  if (query.realname_status) params.set("realname_status", query.realname_status);
  const data = await http.get(`/users/?${params.toString()}`);
  rows.value = data.results || [];
  total.value = data.count || 0;
}

function search() {
  query.page = 1;
  load();
}

async function audit(row, approved) {
  const action = approved ? "通过" : "拒绝";
  await ElMessageBox.confirm(`确认${action}用户 ${row.username} 的实名认证？`, "提示", { type: "warning" });
  await http.post(`/users/${row.id}/audit-realname/`, {
    approved,
    remark: approved ? "后台审核通过" : "后台审核拒绝"
  });
  ElMessage.success(`实名认证已${action}`);
  await load();
}

function changePage(value) {
  query.page = value;
  load();
}

onMounted(load);
</script>
