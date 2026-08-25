<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">操作日志</div>
        <el-input v-model="search" clearable placeholder="搜索用户/对象/变更" style="width: 240px" @keyup.enter="load" />
      </div>
      <el-button @click="load">查询</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="action_time" label="时间" min-width="180" />
        <el-table-column prop="username" label="操作人" width="130" />
        <el-table-column prop="action_label" label="动作" width="100" />
        <el-table-column prop="content_type_label" label="对象类型" min-width="160" />
        <el-table-column prop="object_repr" label="对象" min-width="180" show-overflow-tooltip />
        <el-table-column prop="change_message" label="变更内容" min-width="260" show-overflow-tooltip />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import http from "../utils/http";

const rows = ref([]);
const search = ref("");

async function load() {
  const params = new URLSearchParams({ page: "1" });
  if (search.value) params.set("search", search.value);
  const data = await http.get(`/system/logs/?${params.toString()}`);
  rows.value = data.results || [];
}

onMounted(load);
</script>
