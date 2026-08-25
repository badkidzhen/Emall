<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">售后退款</div>
        <el-select v-model="query.status" clearable placeholder="退款状态" style="width: 160px" @change="search">
          <el-option v-for="item in refundStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>

    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="refund_no" label="退款单号" min-width="210" />
        <el-table-column prop="order" label="订单ID" width="90" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column label="类型" width="130">
          <template #default="{ row }"><StatusTag :value="row.refund_type" :map="refundTypeMap" /></template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="110" />
        <el-table-column label="状态" width="130">
          <template #default="{ row }"><StatusTag :value="row.status" :map="refundStatusMap" /></template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" min-width="180" show-overflow-tooltip />
        <el-table-column prop="gateway_refund_no" label="第三方退款号" min-width="160" show-overflow-tooltip />
        <el-table-column prop="created_at" label="申请时间" min-width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :disabled="row.status !== 'pending'" @click="approve(row)">通过</el-button>
            <el-button link type="danger" :disabled="row.status !== 'pending'" @click="reject(row)">拒绝</el-button>
            <el-button link type="warning" :disabled="row.status !== 'approved'" @click="requestGateway(row)">请求退款</el-button>
            <el-button link type="success" :disabled="!['approved', 'refunding'].includes(row.status)" @click="markRefunded(row)">完成</el-button>
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

const refundStatusOptions = [
  { label: "待审核", value: "pending" },
  { label: "已通过", value: "approved" },
  { label: "已拒绝", value: "rejected" },
  { label: "退款中", value: "refunding" },
  { label: "已退款", value: "refunded" },
  { label: "已关闭", value: "closed" }
];

const refundStatusMap = {
  pending: { label: "待审核", type: "warning" },
  approved: { label: "已通过", type: "primary" },
  rejected: { label: "已拒绝", type: "danger" },
  refunding: { label: "退款中", type: "warning" },
  refunded: { label: "已退款", type: "success" },
  closed: { label: "已关闭", type: "info" }
};

const refundTypeMap = {
  refund_only: { label: "仅退款", type: "primary" },
  return_and_refund: { label: "退货退款", type: "warning" }
};

async function load() {
  const params = new URLSearchParams({ page: String(query.page) });
  if (query.status) params.set("status", query.status);
  const data = await http.get(`/orders/refunds/?${params.toString()}`);
  rows.value = data.results || [];
  total.value = data.count || 0;
}

function search() {
  query.page = 1;
  load();
}

async function approve(row) {
  await ElMessageBox.confirm(`确认通过退款申请 ${row.refund_no}？`, "提示", { type: "warning" });
  await http.post(`/orders/refunds/${row.id}/approve/`, { remark: "后台审核通过" });
  ElMessage.success("退款申请已通过");
  await load();
}

async function reject(row) {
  await ElMessageBox.confirm(`确认拒绝退款申请 ${row.refund_no}？`, "提示", { type: "warning" });
  await http.post(`/orders/refunds/${row.id}/reject/`, { remark: "后台审核拒绝" });
  ElMessage.success("退款申请已拒绝");
  await load();
}

async function requestGateway(row) {
  await ElMessageBox.confirm(`确认向第三方提交退款 ${row.refund_no}？`, "提示", { type: "warning" });
  await http.post(`/orders/refunds/${row.id}/request-gateway/`, {});
  ElMessage.success("已提交退款请求");
  await load();
}

async function markRefunded(row) {
  await ElMessageBox.confirm(`确认退款 ${row.refund_no} 已完成？`, "提示", { type: "warning" });
  await http.post(`/orders/refunds/${row.id}/mark-refunded/`, { remark: "后台确认退款完成" });
  ElMessage.success("退款已标记完成");
  await load();
}

function changePage(value) {
  query.page = value;
  load();
}

onMounted(load);
</script>
