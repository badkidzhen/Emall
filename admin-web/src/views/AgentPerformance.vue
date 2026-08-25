<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">区域业绩</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="summary-grid" style="margin-bottom: 16px">
      <div class="summary-card"><div class="muted">生效代理</div><div class="summary-value">{{ agentCount }}</div></div>
      <div class="summary-card"><div class="muted">代理区域</div><div class="summary-value">{{ regionCount }}</div></div>
      <div class="summary-card"><div class="muted">代理用户</div><div class="summary-value">{{ agentUserCount }}</div></div>
      <div class="summary-card"><div class="muted">待审核申请</div><div class="summary-value">{{ pendingCount }}</div></div>
    </div>
    <div class="page-card">
      <el-table :data="agents" border stripe>
        <el-table-column prop="region_name" label="区域" min-width="160" />
        <el-table-column prop="region_code" label="区域编码" width="120" />
        <el-table-column prop="level" label="代理等级" width="120" />
        <el-table-column prop="user" label="代理用户ID" width="120" />
        <el-table-column prop="commission_rate" label="抽成比例%" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><StatusTag :value="row.enabled" /></template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const agents = ref([]);
const agentCount = ref(0);
const regionCount = ref(0);
const agentUserCount = ref(0);
const pendingCount = ref(0);

async function load() {
  const [agentData, userData, pendingData] = await Promise.all([
    http.get("/agents/?page=1"),
    http.get("/users/?role=city_agent&page=1"),
    http.get("/agents/applications/?status=pending&page=1")
  ]);
  agents.value = agentData.results || [];
  agentCount.value = agentData.count || 0;
  regionCount.value = new Set(agents.value.map((item) => item.region_code)).size;
  agentUserCount.value = userData.count || 0;
  pendingCount.value = pendingData.count || 0;
}

onMounted(load);
</script>
