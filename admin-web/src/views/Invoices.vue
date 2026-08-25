<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">发票管理</div>
        <el-select v-model="query.status" clearable placeholder="发票状态" style="width: 160px" @change="search">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>

    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order" label="订单ID" width="90" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }"><StatusTag :value="row.invoice_type" :map="typeMap" /></template>
        </el-table-column>
        <el-table-column prop="title" label="抬头" min-width="180" show-overflow-tooltip />
        <el-table-column prop="tax_no" label="税号" min-width="170" show-overflow-tooltip />
        <el-table-column prop="amount" label="金额" width="110" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }"><StatusTag :value="row.status" :map="statusMap" /></template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="created_at" label="申请时间" min-width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :disabled="row.status !== 'pending'" @click="issue(row)">开票</el-button>
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
const query = reactive({ page: 1, status: "" });

const statusOptions = [
  { label: "待开票", value: "pending" },
  { label: "已开票", value: "issued" },
  { label: "已拒绝", value: "rejected" }
];

const statusMap = {
  pending: { label: "待开票", type: "warning" },
  issued: { label: "已开票", type: "success" },
  rejected: { label: "已拒绝", type: "danger" }
};

const typeMap = {
  personal: { label: "个人", type: "info" },
  company: { label: "企业", type: "primary" }
};

async function load() {
  const params = new URLSearchParams({ page: String(query.page) });
  if (query.status) params.set("status", query.status);
  const data = await http.get(`/orders/invoices/?${params.toString()}`);
  rows.value = data.results || [];
  total.value = data.count || 0;
}

function search() {
  query.page = 1;
  load();
}

async function issue(row) {
  await ElMessageBox.confirm(`确认发票 #${row.id} 已开具？`, "提示", { type: "warning" });
  await http.post(`/orders/invoices/${row.id}/issue/`, { audit_remark: "后台确认开票" });
  ElMessage.success("发票已标记开具");
  await load();
}

function changePage(value) {
  query.page = value;
  load();
}

onMounted(load);
</script>
