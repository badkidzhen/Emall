<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">库存管理</div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="sku" label="SKU ID" width="100" />
        <el-table-column prop="change_type" label="变更类型" width="120" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="before_stock" label="变更前" width="110" />
        <el-table-column prop="after_stock" label="变更后" width="110" />
        <el-table-column prop="remark" label="备注" min-width="220" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" min-width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import http from "../utils/http";

const rows = ref([]);
async function load() {
  const data = await http.get("/catalog/stock-logs/?page=1");
  rows.value = data.results || [];
}
onMounted(load);
</script>
