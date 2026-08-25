<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">{{ pageTitle }}</div>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>

    <div v-if="showTabs" class="summary-grid" style="margin-bottom: 16px">
      <div class="summary-card">
        <div class="muted">钱包数量</div>
        <div class="summary-value">{{ walletCount }}</div>
      </div>
      <div class="summary-card">
        <div class="muted">资金流水</div>
        <div class="summary-value">{{ flowCount }}</div>
      </div>
      <div class="summary-card">
        <div class="muted">提现申请</div>
        <div class="summary-value">{{ withdrawCount }}</div>
      </div>
      <div class="summary-card">
        <div class="muted">待审核</div>
        <div class="summary-value">{{ pendingCount }}</div>
      </div>
    </div>

    <div class="page-card">
      <el-tabs v-if="showTabs" v-model="active">
        <el-tab-pane label="提现审核" name="withdrawals">
          <el-table :data="withdrawals" border stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="user" label="用户ID" width="90" />
            <el-table-column prop="amount" label="金额" width="120" />
            <el-table-column label="通道" width="110">
              <template #default="{ row }"><StatusTag :value="row.channel" :map="channelMap" /></template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }"><StatusTag :value="row.status" :map="withdrawStatusMap" /></template>
            </el-table-column>
            <el-table-column prop="account_name" label="账户名" min-width="140" />
            <el-table-column prop="account_no" label="账号" min-width="160" show-overflow-tooltip />
            <el-table-column prop="payout_no" label="打款单号" min-width="170" show-overflow-tooltip />
            <el-table-column prop="created_at" label="申请时间" min-width="180" />
            <el-table-column label="操作" width="300" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" :disabled="row.status !== 'pending'" @click="approve(row)">通过</el-button>
                <el-button link type="danger" :disabled="row.status !== 'pending'" @click="reject(row)">拒绝</el-button>
                <el-button link type="warning" :disabled="row.status !== 'approved'" @click="submitPayout(row)">提交打款</el-button>
                <el-button link type="success" :disabled="!['approved', 'paying'].includes(row.status)" @click="paid(row)">完成</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="钱包" name="wallets">
          <el-table :data="wallets" border stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="user" label="用户ID" width="90" />
            <el-table-column prop="balance" label="可用余额" width="120" />
            <el-table-column prop="frozen_balance" label="冻结余额" width="120" />
            <el-table-column prop="total_income" label="累计收入" width="120" />
            <el-table-column prop="total_withdraw" label="累计提现" width="120" />
            <el-table-column prop="updated_at" label="更新时间" min-width="180" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="流水" name="flows">
          <el-table :data="flows" border stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="user" label="用户ID" width="90" />
            <el-table-column label="类型" width="120">
              <template #default="{ row }"><StatusTag :value="row.flow_type" :map="flowTypeMap" /></template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120" />
            <el-table-column prop="balance_after" label="变动后余额" width="130" />
            <el-table-column prop="biz_type" label="业务类型" width="130" />
            <el-table-column prop="biz_id" label="业务ID" width="120" />
            <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" min-width="180" />
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <el-table v-if="!showTabs && active === 'withdrawals'" :data="withdrawals" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column prop="amount" label="金额" width="120" />
        <el-table-column label="通道" width="110">
          <template #default="{ row }"><StatusTag :value="row.channel" :map="channelMap" /></template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }"><StatusTag :value="row.status" :map="withdrawStatusMap" /></template>
        </el-table-column>
        <el-table-column prop="account_name" label="账户名" min-width="140" />
        <el-table-column prop="account_no" label="账号" min-width="160" show-overflow-tooltip />
        <el-table-column prop="payout_no" label="打款单号" min-width="170" show-overflow-tooltip />
        <el-table-column prop="created_at" label="申请时间" min-width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :disabled="row.status !== 'pending'" @click="approve(row)">通过</el-button>
            <el-button link type="danger" :disabled="row.status !== 'pending'" @click="reject(row)">拒绝</el-button>
            <el-button link type="warning" :disabled="row.status !== 'approved'" @click="submitPayout(row)">提交打款</el-button>
            <el-button link type="success" :disabled="!['approved', 'paying'].includes(row.status)" @click="paid(row)">完成</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-table v-if="!showTabs && active === 'flows'" :data="flows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }"><StatusTag :value="row.flow_type" :map="flowTypeMap" /></template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120" />
        <el-table-column prop="balance_after" label="变动后余额" width="130" />
        <el-table-column prop="biz_type" label="业务类型" width="130" />
        <el-table-column prop="biz_id" label="业务ID" width="120" />
        <el-table-column prop="remark" label="备注" min-width="180" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" min-width="180" />
      </el-table>

      <el-table v-if="!showTabs && active === 'wallets'" :data="wallets" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column prop="balance" label="可用余额" width="120" />
        <el-table-column prop="frozen_balance" label="冻结余额" width="120" />
        <el-table-column prop="total_income" label="累计收入" width="120" />
        <el-table-column prop="total_withdraw" label="累计提现" width="120" />
        <el-table-column prop="updated_at" label="更新时间" min-width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Refresh } from "@element-plus/icons-vue";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const route = useRoute();
const active = ref(route.meta.financeTab || "withdrawals");
const showTabs = computed(() => !route.meta.financeTab);
const pageTitle = computed(() => route.meta.title || "财务管理");
const walletCount = ref(0);
const flowCount = ref(0);
const withdrawCount = ref(0);
const pendingCount = ref(0);
const withdrawals = ref([]);
const wallets = ref([]);
const flows = ref([]);

const withdrawStatusMap = {
  pending: { label: "待审核", type: "warning" },
  approved: { label: "已通过", type: "primary" },
  paying: { label: "打款中", type: "warning" },
  rejected: { label: "已拒绝", type: "danger" },
  paid: { label: "已打款", type: "success" }
};

const channelMap = {
  manual: { label: "手动", type: "info" },
  wechat: { label: "微信", type: "success" },
  bank: { label: "银行卡", type: "primary" }
};

const flowTypeMap = {
  income: { label: "收入", type: "success" },
  withdraw: { label: "提现", type: "warning" },
  freeze: { label: "冻结", type: "primary" },
  unfreeze: { label: "解冻", type: "info" },
  adjust: { label: "调整", type: "danger" }
};

async function load() {
  const [walletData, flowData, withdrawData] = await Promise.all([
    http.get("/finance/wallets/?page=1"),
    http.get("/finance/flows/?page=1"),
    http.get("/finance/withdrawals/?page=1")
  ]);
  walletCount.value = walletData.count || 0;
  flowCount.value = flowData.count || 0;
  withdrawCount.value = withdrawData.count || 0;
  wallets.value = walletData.results || [];
  flows.value = flowData.results || [];
  withdrawals.value = withdrawData.results || [];
  pendingCount.value = withdrawals.value.filter((item) => item.status === "pending").length;
}

async function approve(row) {
  await ElMessageBox.confirm(`确认通过提现申请 #${row.id}？`, "提示", { type: "warning" });
  await http.post(`/finance/withdrawals/${row.id}/approve/`, { remark: "后台审核通过" });
  ElMessage.success("提现申请已通过");
  await load();
}

async function reject(row) {
  await ElMessageBox.confirm(`确认拒绝提现申请 #${row.id}？`, "提示", { type: "warning" });
  await http.post(`/finance/withdrawals/${row.id}/reject/`, { remark: "后台审核拒绝" });
  ElMessage.success("提现申请已拒绝");
  await load();
}

async function submitPayout(row) {
  await ElMessageBox.confirm(`确认提交提现申请 #${row.id} 到打款通道？`, "提示", { type: "warning" });
  await http.post(`/finance/withdrawals/${row.id}/submit-payout/`, { remark: "后台提交打款" });
  ElMessage.success("已提交打款");
  await load();
}

async function paid(row) {
  await ElMessageBox.confirm(`确认提现申请 #${row.id} 已完成打款？`, "提示", { type: "warning" });
  await http.post(`/finance/withdrawals/${row.id}/mark-paid/`, { remark: "后台确认打款完成" });
  ElMessage.success("提现已标记打款");
  await load();
}

onMounted(async () => {
  active.value = route.meta.financeTab || "withdrawals";
  await load();
});

watch(
  () => route.meta.financeTab,
  async (tab) => {
    if (tab) {
      active.value = tab;
      await load();
    }
  }
);
</script>
