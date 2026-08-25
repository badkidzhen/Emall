<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">团队管理</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="user" label="用户ID" width="100" />
        <el-table-column prop="team_count" label="团队人数" width="120" />
        <el-table-column prop="direct_count" label="直属人数" width="120" />
        <el-table-column prop="indirect_count" label="间接人数" width="120" />
        <el-table-column prop="team_order_amount" label="团队订单额" width="140" />
        <el-table-column prop="team_commission" label="团队佣金" width="140" />
        <el-table-column prop="updated_at" label="更新时间" min-width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="sync(row)">同步</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import http from "../utils/http";

const rows = ref([]);

async function load() {
  const data = await http.get("/distribution/team-stats/?page=1");
  rows.value = data.results || [];
}

async function sync(row) {
  await http.post("/distribution/team-stats/sync/", { user_id: row.user });
  ElMessage.success("团队统计已同步");
  await load();
}

onMounted(load);
</script>
