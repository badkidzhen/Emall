<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">{{ pageTitle }}</div>
        <el-tabs v-if="showTabs" v-model="active">
          <el-tab-pane label="池子" name="pools" />
          <el-tab-pane label="规则" name="rules" />
          <el-tab-pane label="发放记录" name="records" />
        </el-tabs>
      </div>
      <el-button v-if="active === 'pools'" type="primary" @click="openCreate">新增奖金池</el-button>
      <el-button v-if="active === 'rules'" type="primary" @click="openRuleCreate">新增规则</el-button>
    </div>

    <div class="page-card">
      <el-table v-if="active === 'pools'" :data="pools" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="pool_type" label="类型" width="150" />
        <el-table-column prop="amount" label="金额" width="120" />
        <el-table-column prop="min_performance" label="最低业绩" width="120" />
        <el-table-column prop="max_user_ratio" label="单人上限%" width="120" />
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.enabled" /></template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="warning" @click="distribute(row)">分配</el-button>
            <el-button link type="success" @click="markPaid(row)">标记发放</el-button>
            <el-button link type="danger" @click="removePool(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-table v-if="active === 'rules'" :data="rules" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="pool" label="池子ID" width="90" />
        <el-table-column prop="team_amount_weight" label="团队业绩权重" width="130" />
        <el-table-column prop="team_count_weight" label="团队人数权重" width="130" />
        <el-table-column prop="personal_amount_weight" label="个人业绩权重" width="130" />
        <el-table-column prop="rank_config" label="排名配置" min-width="220">
          <template #default="{ row }">{{ JSON.stringify(row.rank_config || {}) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editRule(row)">编辑</el-button>
            <el-button link type="danger" @click="removeRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-table v-if="active === 'records'" :data="records" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="pool" label="池子ID" width="90" />
        <el-table-column prop="user" label="用户ID" width="90" />
        <el-table-column prop="score" label="得分" width="120" />
        <el-table-column prop="amount" label="金额" width="120" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }"><StatusTag :value="row.status" :map="recordStatusMap" /></template>
        </el-table-column>
        <el-table-column prop="distributed_at" label="发放时间" min-width="180" />
      </el-table>
    </div>

    <el-dialog v-model="poolVisible" :title="poolMode === 'create' ? '新增奖金池' : '编辑奖金池'" width="720px">
      <el-form :model="poolForm" label-width="120px">
        <div class="form-grid">
          <el-form-item label="名称"><el-input v-model="poolForm.name" /></el-form-item>
          <el-form-item label="类型">
            <el-select v-model="poolForm.pool_type">
              <el-option label="平台全局池" value="global" />
              <el-option label="城市代理池" value="city_agent" />
              <el-option label="团队长池" value="team_leader" />
              <el-option label="分销精英池" value="distributor" />
              <el-option label="月度争霸池" value="monthly" />
            </el-select>
          </el-form-item>
          <el-form-item label="金额"><el-input v-model="poolForm.amount" /></el-form-item>
          <el-form-item label="最低业绩"><el-input v-model="poolForm.min_performance" /></el-form-item>
          <el-form-item label="单人上限%"><el-input v-model="poolForm.max_user_ratio" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="poolForm.enabled" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="poolVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPool">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="ruleVisible" :title="ruleMode === 'create' ? '新增奖金规则' : '编辑奖金规则'" width="720px">
      <el-form :model="ruleForm" label-width="130px">
        <div class="form-grid">
          <el-form-item label="奖金池">
            <el-select v-model="ruleForm.pool">
              <el-option v-for="item in pools" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="团队业绩权重"><el-input v-model="ruleForm.team_amount_weight" /></el-form-item>
          <el-form-item label="团队人数权重"><el-input v-model="ruleForm.team_count_weight" /></el-form-item>
          <el-form-item label="个人业绩权重"><el-input v-model="ruleForm.personal_amount_weight" /></el-form-item>
          <el-form-item label="排名配置JSON" class="full-width"><el-input v-model="ruleForm.rank_config" type="textarea" :rows="4" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="ruleVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRule">保存</el-button>
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
const active = ref(route.meta.rewardTab || "pools");
const showTabs = computed(() => !route.meta.rewardTab);
const pageTitle = computed(() => route.meta.title || "奖金池");
const pools = ref([]);
const rules = ref([]);
const records = ref([]);
const poolVisible = ref(false);
const ruleVisible = ref(false);
const poolMode = ref("create");
const ruleMode = ref("create");
const poolForm = reactive(defaultPool());
const ruleForm = reactive(defaultRule());
const recordStatusMap = {
  pending: { label: "待发放", type: "warning" },
  paid: { label: "已发放", type: "success" },
  canceled: { label: "已取消", type: "info" }
};

function defaultPool() {
  return { id: null, name: "", pool_type: "global", amount: 0, min_performance: 0, max_user_ratio: 20, enabled: true };
}

function defaultRule() {
  return { id: null, pool: null, team_amount_weight: 0, team_count_weight: 0, personal_amount_weight: 0, rank_config: "{}" };
}

async function load() {
  const [poolData, ruleData, recordData] = await Promise.all([
    http.get("/rewards/pools/?page=1"),
    http.get("/rewards/rules/?page=1"),
    http.get("/rewards/records/?page=1")
  ]);
  pools.value = poolData.results || [];
  rules.value = ruleData.results || [];
  records.value = recordData.results || [];
}

function openCreate() {
  Object.assign(poolForm, defaultPool());
  poolMode.value = "create";
  poolVisible.value = true;
}

function edit(row) {
  Object.assign(poolForm, defaultPool(), row);
  poolMode.value = "edit";
  poolVisible.value = true;
}

function buildPoolPayload() {
  return {
    name: poolForm.name,
    pool_type: poolForm.pool_type,
    amount: Number(poolForm.amount || 0),
    min_performance: Number(poolForm.min_performance || 0),
    max_user_ratio: Number(poolForm.max_user_ratio || 20),
    enabled: poolForm.enabled
  };
}

async function submitPool() {
  if (poolMode.value === "create") {
    await http.post("/rewards/pools/", buildPoolPayload());
    ElMessage.success("奖金池创建成功");
  } else {
    await http.put(`/rewards/pools/${poolForm.id}/`, buildPoolPayload());
    ElMessage.success("奖金池保存成功");
  }
  poolVisible.value = false;
  await load();
}

function openRuleCreate() {
  Object.assign(ruleForm, defaultRule());
  ruleMode.value = "create";
  ruleVisible.value = true;
}

function editRule(row) {
  Object.assign(ruleForm, defaultRule(), row, { rank_config: JSON.stringify(row.rank_config || {}, null, 2) });
  ruleMode.value = "edit";
  ruleVisible.value = true;
}

function buildRulePayload() {
  return {
    pool: ruleForm.pool,
    team_amount_weight: Number(ruleForm.team_amount_weight || 0),
    team_count_weight: Number(ruleForm.team_count_weight || 0),
    personal_amount_weight: Number(ruleForm.personal_amount_weight || 0),
    rank_config: JSON.parse(ruleForm.rank_config || "{}")
  };
}

async function submitRule() {
  let payload;
  try {
    payload = buildRulePayload();
  } catch (error) {
    ElMessage.error("排名配置 JSON 格式不正确");
    return;
  }
  if (ruleMode.value === "create") {
    await http.post("/rewards/rules/", payload);
    ElMessage.success("奖金规则创建成功");
  } else {
    await http.put(`/rewards/rules/${ruleForm.id}/`, payload);
    ElMessage.success("奖金规则保存成功");
  }
  ruleVisible.value = false;
  await load();
}

async function removePool(row) {
  await ElMessageBox.confirm(`确认删除奖金池 ${row.name}？`, "提示", { type: "warning" });
  await http.delete(`/rewards/pools/${row.id}/`);
  ElMessage.success("奖金池已删除");
  await load();
}

async function removeRule(row) {
  await ElMessageBox.confirm(`确认删除奖金规则 #${row.id}？`, "提示", { type: "warning" });
  await http.delete(`/rewards/rules/${row.id}/`);
  ElMessage.success("奖金规则已删除");
  await load();
}

async function distribute(row) {
  await ElMessageBox.confirm(`确认分配奖金池 ${row.name}？`, "提示", { type: "warning" });
  await http.post(`/rewards/pools/${row.id}/distribute/`, {});
  ElMessage.success("奖金池分配完成");
  await load();
}

async function markPaid(row) {
  await ElMessageBox.confirm(`确认标记奖金池 ${row.name} 已发放？`, "提示", { type: "warning" });
  await http.post(`/rewards/pools/${row.id}/mark-paid/`, {});
  ElMessage.success("奖金池已标记发放");
  await load();
}

onMounted(async () => {
  active.value = route.meta.rewardTab || "pools";
  await load();
});

watch(
  () => route.meta.rewardTab,
  async (tab) => {
    if (tab) {
      active.value = tab;
      await load();
    }
  }
);
</script>
