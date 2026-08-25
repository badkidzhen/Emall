<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">模拟测算</div>
      <el-button type="primary" @click="calculate">开始测算</el-button>
    </div>

    <div class="page-card" style="margin-bottom: 16px">
      <el-form :model="form" label-width="120px">
        <div class="form-grid">
          <el-form-item label="奖金池">
            <el-select v-model="form.poolId" placeholder="选择奖金池">
              <el-option v-for="item in pools" :key="item.id" :label="`${item.name} / ${item.amount}`" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="测算人数"><el-input v-model="form.limit" /></el-form-item>
        </div>
      </el-form>
    </div>

    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="rank" label="排名" width="90" />
        <el-table-column prop="user" label="用户ID" width="100" />
        <el-table-column prop="score" label="测算得分" width="140" />
        <el-table-column prop="amount" label="预计金额" width="140" />
        <el-table-column prop="remark" label="说明" min-width="260" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../utils/http";

const pools = ref([]);
const teamStats = ref([]);
const rows = ref([]);
const form = reactive({ poolId: null, limit: 10 });

async function load() {
  const [poolData, teamData] = await Promise.all([
    http.get("/rewards/pools/?page=1"),
    http.get("/distribution/team-stats/?page=1")
  ]);
  pools.value = poolData.results || [];
  teamStats.value = teamData.results || [];
  if (!form.poolId && pools.value.length) form.poolId = pools.value[0].id;
}

function calculate() {
  const pool = pools.value.find((item) => item.id === form.poolId);
  if (!pool) {
    ElMessage.warning("请选择奖金池");
    return;
  }
  const limit = Number(form.limit || 10);
  const candidates = [...teamStats.value]
    .map((item) => ({
      user: item.user,
      score: Number(item.team_order_amount || 0) * 0.7 + Number(item.team_count || 0) * 10 + Number(item.team_commission || 0) * 0.3
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
  const totalScore = candidates.reduce((sum, item) => sum + item.score, 0) || 1;
  rows.value = candidates.map((item, index) => ({
    rank: index + 1,
    user: item.user,
    score: item.score.toFixed(2),
    amount: ((Number(pool.amount || 0) * item.score) / totalScore).toFixed(2),
    remark: "前端模拟测算，不写入真实分配记录"
  }));
}

onMounted(async () => {
  await load();
  calculate();
});
</script>
