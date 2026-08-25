<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">平台收支</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="summary-grid" style="margin-bottom: 16px">
      <div class="summary-card"><div class="muted">钱包数量</div><div class="summary-value">{{ walletCount }}</div></div>
      <div class="summary-card"><div class="muted">资金流水</div><div class="summary-value">{{ flowCount }}</div></div>
      <div class="summary-card"><div class="muted">提现申请</div><div class="summary-value">{{ withdrawCount }}</div></div>
      <div class="summary-card"><div class="muted">已打款</div><div class="summary-value">{{ paidCount }}</div></div>
    </div>
    <div class="page-card">
      <el-table :data="flows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column prop="flow_type" label="收支类型" width="120" />
        <el-table-column prop="amount" label="金额" width="120" />
        <el-table-column prop="balance_after" label="变动后余额" width="130" />
        <el-table-column prop="biz_type" label="业务类型" width="130" />
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" min-width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import http from "../utils/http";

const walletCount = ref(0);
const flowCount = ref(0);
const withdrawCount = ref(0);
const paidCount = ref(0);
const flows = ref([]);

async function load() {
  const [wallets, flowData, withdrawals, paid] = await Promise.all([
    http.get("/finance/wallets/?page=1"),
    http.get("/finance/flows/?page=1"),
    http.get("/finance/withdrawals/?page=1"),
    http.get("/finance/withdrawals/?status=paid&page=1")
  ]);
  walletCount.value = wallets.count || 0;
  flowCount.value = flowData.count || 0;
  withdrawCount.value = withdrawals.count || 0;
  paidCount.value = paid.count || 0;
  flows.value = flowData.results || [];
}

onMounted(load);
</script>
