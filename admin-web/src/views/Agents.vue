<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">{{ pageTitle }}</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="page-card">
      <el-tabs v-if="showTabs" v-model="active">
        <el-tab-pane label="代理申请" name="applications">
          <el-table :data="applications" border stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="user" label="用户ID" width="90" />
            <el-table-column prop="region_name" label="区域" min-width="160" />
            <el-table-column prop="region_code" label="区域编码" width="120" />
            <el-table-column prop="level" label="等级" width="90" />
            <el-table-column prop="contact_name" label="联系人" width="120" />
            <el-table-column prop="contact_phone" label="联系电话" width="140" />
            <el-table-column label="状态" width="120">
              <template #default="{ row }"><StatusTag :value="row.status" :map="applicationStatusMap" /></template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" :disabled="row.status !== 'pending'" @click="openApprove(row)">通过</el-button>
                <el-button link type="danger" :disabled="row.status !== 'pending'" @click="reject(row)">拒绝</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="已生效代理" name="agents">
          <el-table :data="agents" border stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="user" label="用户ID" width="90" />
            <el-table-column prop="region_name" label="区域" min-width="160" />
            <el-table-column prop="level" label="等级" width="90" />
            <el-table-column prop="commission_rate" label="抽成比例" width="120" />
            <el-table-column label="启用" width="90">
              <template #default="{ row }"><StatusTag :value="row.enabled" /></template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" min-width="180" />
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <el-table v-if="!showTabs && active === 'applications'" :data="applications" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column prop="region_name" label="区域" min-width="160" />
        <el-table-column prop="region_code" label="区域编码" width="120" />
        <el-table-column prop="level" label="等级" width="90" />
        <el-table-column prop="contact_name" label="联系人" width="120" />
        <el-table-column prop="contact_phone" label="联系电话" width="140" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }"><StatusTag :value="row.status" :map="applicationStatusMap" /></template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :disabled="row.status !== 'pending'" @click="openApprove(row)">通过</el-button>
            <el-button link type="danger" :disabled="row.status !== 'pending'" @click="reject(row)">拒绝</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-table v-if="!showTabs && active === 'agents'" :data="agents" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column prop="region_name" label="区域" min-width="160" />
        <el-table-column prop="region_code" label="区域编码" width="120" />
        <el-table-column prop="level" label="等级" width="90" />
        <el-table-column prop="commission_rate" label="抽成比例" width="120" />
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.enabled" /></template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
      </el-table>
    </div>

    <el-dialog v-model="approveVisible" title="通过代理申请" width="520px">
      <el-form :model="auditForm" label-width="110px">
        <el-form-item label="抽成比例%"><el-input v-model="auditForm.commission_rate" /></el-form-item>
        <el-form-item label="审核备注"><el-input v-model="auditForm.remark" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveVisible = false">取消</el-button>
        <el-button type="primary" @click="approve">通过</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const route = useRoute();
const active = ref(route.meta.agentTab || "applications");
const showTabs = computed(() => !route.meta.agentTab);
const pageTitle = computed(() => route.meta.title || "城市代理");
const applications = ref([]);
const agents = ref([]);
const approveVisible = ref(false);
const current = ref(null);
const auditForm = reactive({ commission_rate: "3.00", remark: "审核通过" });
const applicationStatusMap = {
  pending: { label: "待审核", type: "warning" },
  approved: { label: "已通过", type: "success" },
  rejected: { label: "已拒绝", type: "danger" }
};

async function load() {
  const [applicationData, agentData] = await Promise.all([
    http.get("/agents/applications/?page=1"),
    http.get("/agents/?page=1")
  ]);
  applications.value = applicationData.results || [];
  agents.value = agentData.results || [];
}

function openApprove(row) {
  current.value = row;
  Object.assign(auditForm, { commission_rate: "3.00", remark: "审核通过" });
  approveVisible.value = true;
}

async function approve() {
  await http.post(`/agents/applications/${current.value.id}/approve/`, {
    commission_rate: auditForm.commission_rate,
    remark: auditForm.remark
  });
  ElMessage.success("代理申请已通过");
  approveVisible.value = false;
  await load();
}

async function reject(row) {
  await ElMessageBox.confirm(`确认拒绝 ${row.region_name} 的代理申请？`, "提示", { type: "warning" });
  await http.post(`/agents/applications/${row.id}/reject/`, { remark: "审核拒绝" });
  ElMessage.success("代理申请已拒绝");
  await load();
}

onMounted(async () => {
  active.value = route.meta.agentTab || "applications";
  await load();
});

watch(
  () => route.meta.agentTab,
  async (tab) => {
    if (tab) {
      active.value = tab;
      await load();
    }
  }
);
</script>
