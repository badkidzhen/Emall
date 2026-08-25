<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">分销统计</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="summary-grid" style="margin-bottom: 16px">
      <div class="summary-card"><div class="muted">佣金记录</div><div class="summary-value">{{ commissionCount }}</div></div>
      <div class="summary-card"><div class="muted">团队统计</div><div class="summary-value">{{ teamCount }}</div></div>
      <div class="summary-card"><div class="muted">分销商</div><div class="summary-value">{{ distributorCount }}</div></div>
      <div class="summary-card"><div class="muted">待结算佣金</div><div class="summary-value">{{ pendingCount }}</div></div>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="label" label="指标" min-width="180" />
        <el-table-column prop="value" label="数量" width="160" />
        <el-table-column prop="remark" label="说明" min-width="260" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import http from "../utils/http";

const commissionCount = ref(0);
const teamCount = ref(0);
const distributorCount = ref(0);
const pendingCount = ref(0);
const rows = ref([]);

async function load() {
  const [commissions, teams, distributors, pending] = await Promise.all([
    http.get("/distribution/commissions/?page=1"),
    http.get("/distribution/team-stats/?page=1"),
    http.get("/users/?is_distributor=true&page=1"),
    http.get("/distribution/commissions/?status=frozen&page=1")
  ]);
  commissionCount.value = commissions.count || 0;
  teamCount.value = teams.count || 0;
  distributorCount.value = distributors.count || 0;
  pendingCount.value = pending.count || 0;
  rows.value = [
    { label: "佣金记录", value: commissionCount.value, remark: "全部分销佣金明细记录" },
    { label: "团队统计", value: teamCount.value, remark: "已生成团队统计的用户数" },
    { label: "分销商", value: distributorCount.value, remark: "当前具备分销身份的用户数" },
    { label: "冻结中佣金", value: pendingCount.value, remark: "等待结算任务处理的佣金记录" }
  ];
}

onMounted(load);
</script>
