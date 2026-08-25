<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">订单管理</div>
        <el-input v-model="query.search" clearable placeholder="订单号/用户" style="width: 220px" @keyup.enter="search" />
        <el-select v-model="query.status" clearable placeholder="订单状态" style="width: 160px" @change="search">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>

    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="order-detail">
              <div class="detail-block">
                <div class="detail-title">商品明细</div>
                <el-table :data="row.items || []" border size="small">
                  <el-table-column prop="product_title" label="商品" min-width="180" />
                  <el-table-column prop="sku_code" label="SKU" width="160" />
                  <el-table-column prop="price" label="单价" width="100" />
                  <el-table-column prop="quantity" label="数量" width="90" />
                  <el-table-column prop="total_amount" label="小计" width="110" />
                </el-table>
              </div>

              <div class="detail-grid">
                <div class="detail-block">
                  <div class="detail-title">收货信息</div>
                  <div class="muted">{{ row.receiver_name || "-" }} {{ row.receiver_mobile || "" }}</div>
                  <div>{{ [row.province, row.city, row.district, row.address_detail].filter(Boolean).join(" ") || "-" }}</div>
                </div>
                <div class="detail-block">
                  <div class="detail-title">物流信息</div>
                  <div>{{ row.logistics?.company || "-" }} {{ row.logistics?.tracking_no || "" }}</div>
                  <div class="muted">{{ row.logistics?.shipped_at || "" }}</div>
                </div>
                <div class="detail-block">
                  <div class="detail-title">支付记录</div>
                  <div v-for="payment in row.payment_records || []" :key="payment.id">
                    {{ payment.channel }} / {{ payment.status }} / {{ payment.amount }}
                  </div>
                  <div v-if="!(row.payment_records || []).length" class="muted">暂无支付记录</div>
                </div>
                <div class="detail-block">
                  <div class="detail-title">退款记录</div>
                  <div v-for="refund in row.refund_applications || []" :key="refund.id">
                    {{ refund.refund_no }} / {{ refund.status }} / {{ refund.amount }}
                  </div>
                  <div v-if="!(row.refund_applications || []).length" class="muted">暂无退款记录</div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="order_no" label="订单号" min-width="230" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column label="状态" width="140">
          <template #default="{ row }"><StatusTag :value="row.status" :map="statusMap" /></template>
        </el-table-column>
        <el-table-column prop="total_amount" label="商品总额" width="120" />
        <el-table-column prop="discount_amount" label="优惠" width="100" />
        <el-table-column prop="pay_amount" label="实付金额" width="120" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button link type="warning" :disabled="row.status !== 'pending_payment'" @click="confirmPaid(row)">确认支付</el-button>
            <el-button link type="primary" :disabled="row.status !== 'pending_shipment'" @click="openShip(row)">发货</el-button>
            <el-button link type="success" :disabled="!['pending_shipment', 'pending_receipt'].includes(row.status)" @click="complete(row)">完成</el-button>
            <el-button link type="danger" :disabled="row.status !== 'pending_payment'" @click="cancel(row)">取消</el-button>
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

    <el-dialog v-model="shipDialogVisible" title="订单发货" width="520px">
      <el-form :model="shipForm" label-width="90px">
        <el-form-item label="物流公司">
          <el-input v-model="shipForm.company" placeholder="例如：顺丰速运" />
        </el-form-item>
        <el-form-item label="物流单号">
          <el-input v-model="shipForm.tracking_no" placeholder="请输入物流单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitShip">确认发货</el-button>
      </template>
    </el-dialog>
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
const query = reactive({ page: 1, search: "", status: "" });
const shipDialogVisible = ref(false);
const currentOrder = ref(null);
const shipForm = reactive({ company: "", tracking_no: "" });

const statusOptions = [
  { label: "待付款", value: "pending_payment" },
  { label: "待发货", value: "pending_shipment" },
  { label: "待收货", value: "pending_receipt" },
  { label: "已完成", value: "completed" },
  { label: "售后中", value: "refunding" },
  { label: "已退款", value: "refunded" },
  { label: "已关闭", value: "closed" }
];

const statusMap = {
  pending_payment: { label: "待付款", type: "warning" },
  pending_shipment: { label: "待发货", type: "primary" },
  pending_receipt: { label: "待收货", type: "primary" },
  completed: { label: "已完成", type: "success" },
  refunding: { label: "售后中", type: "danger" },
  refunded: { label: "已退款", type: "info" },
  closed: { label: "已关闭", type: "info" }
};

async function load() {
  const params = new URLSearchParams({ page: String(query.page) });
  if (query.search) params.set("search", query.search);
  if (query.status) params.set("status", query.status);
  const data = await http.get(`/orders/?${params.toString()}`);
  rows.value = data.results || [];
  total.value = data.count || 0;
}

function search() {
  query.page = 1;
  load();
}

function openShip(row) {
  currentOrder.value = row;
  shipForm.company = row.logistics?.company || "";
  shipForm.tracking_no = row.logistics?.tracking_no || "";
  shipDialogVisible.value = true;
}

async function submitShip() {
  await http.post(`/orders/${currentOrder.value.id}/ship/`, {
    company: shipForm.company,
    tracking_no: shipForm.tracking_no,
    traces: []
  });
  ElMessage.success("订单已发货");
  shipDialogVisible.value = false;
  await load();
}

async function complete(row) {
  await ElMessageBox.confirm(`确认完成订单 ${row.order_no}？`, "提示", { type: "warning" });
  await http.post(`/orders/${row.id}/complete/`, {});
  ElMessage.success("订单已完成");
  await load();
}

async function confirmPaid(row) {
  await ElMessageBox.confirm(`使用模拟支付确认订单 ${row.order_no}？`, "提示", { type: "warning" });
  await http.post(`/orders/${row.id}/confirm-paid/`, {
    payment_no: `ADMIN-${row.id}-${Date.now()}`,
    paid_amount: row.pay_amount,
    channel: "mock"
  });
  ElMessage.success("订单已确认支付");
  await load();
}

async function cancel(row) {
  await ElMessageBox.confirm(`确认取消订单 ${row.order_no}？`, "提示", { type: "warning" });
  await http.post(`/orders/${row.id}/cancel/`, { reason: "admin_cancel" });
  ElMessage.success("订单已取消");
  await load();
}

function changePage(page) {
  query.page = page;
  load();
}

onMounted(load);
</script>

<style scoped>
.order-detail {
  display: grid;
  gap: 14px;
  padding: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.detail-block {
  min-width: 0;
}

.detail-title {
  margin-bottom: 6px;
  font-weight: 700;
}
</style>
