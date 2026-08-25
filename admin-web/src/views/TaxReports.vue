<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">税务报表</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="label" label="项目" min-width="180" />
        <el-table-column prop="value" label="数量/金额" width="160" />
        <el-table-column prop="remark" label="说明" min-width="300" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import http from "../utils/http";

const rows = ref([]);

async function load() {
  const [invoices, withdrawals, flows] = await Promise.all([
    http.get("/orders/invoices/?page=1"),
    http.get("/finance/withdrawals/?status=paid&page=1"),
    http.get("/finance/flows/?flow_type=income&page=1")
  ]);
  rows.value = [
    { label: "发票申请数", value: invoices.count || 0, remark: "用于后续对接真实开票和税务系统" },
    { label: "已打款提现数", value: withdrawals.count || 0, remark: "可作为个人所得相关统计依据" },
    { label: "收入流水数", value: flows.count || 0, remark: "当前为接口统计数量，后续可扩展金额汇总" }
  ];
}

onMounted(load);
</script>
