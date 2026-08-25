<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">佣金明细</div>
        <el-select v-model="status" clearable placeholder="状态" style="width: 140px" @change="load">
          <el-option label="冻结中" value="frozen" />
          <el-option label="已结算" value="settled" />
          <el-option label="已取消" value="canceled" />
        </el-select>
      </div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="受益用户" width="100" />
        <el-table-column prop="source_user" label="来源用户" width="100" />
        <el-table-column prop="order" label="订单ID" width="100" />
        <el-table-column prop="level" label="级别" width="90" />
        <el-table-column prop="rate" label="佣金比例%" width="120" />
        <el-table-column prop="amount" label="佣金金额" width="120" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }"><StatusTag :value="row.status" :map="statusMap" /></template>
        </el-table-column>
        <el-table-column prop="settle_at" label="预计结算时间" min-width="180" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const rows = ref([]);
const status = ref("");
const statusMap = {
  frozen: { label: "冻结中", type: "warning" },
  settled: { label: "已结算", type: "success" },
  canceled: { label: "已取消", type: "info" }
};

async function load() {
  const params = new URLSearchParams({ page: "1" });
  if (status.value) params.set("status", status.value);
  const data = await http.get(`/distribution/commissions/?${params.toString()}`);
  rows.value = data.results || [];
}

onMounted(load);
</script>
