<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">代理佣金</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="用户ID" width="100" />
        <el-table-column prop="region_name" label="代理区域" min-width="160" />
        <el-table-column prop="level" label="代理等级" width="120" />
        <el-table-column prop="commission_rate" label="抽成比例%" width="120" />
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.enabled" /></template>
        </el-table-column>
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
async function load() {
  const data = await http.get("/agents/?page=1");
  rows.value = data.results || [];
}
onMounted(load);
</script>
