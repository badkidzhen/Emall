<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">分销配置</div>
      <div>
        <el-button @click="settle">结算到期佣金</el-button>
        <el-button type="primary" @click="openCreate">新增配置</el-button>
      </div>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="配置名称" min-width="180" />
        <el-table-column prop="default_rate_lv1" label="一级默认%" width="120" />
        <el-table-column prop="default_rate_lv2" label="二级默认%" width="120" />
        <el-table-column prop="settlement_delay_days" label="结算延迟天数" width="140" />
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.enabled" /></template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="visible" :title="mode === 'create' ? '新增分销配置' : '编辑分销配置'" width="620px">
      <el-form :model="form" label-width="130px">
        <el-form-item label="配置名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="一级默认%"><el-input v-model="form.default_rate_lv1" /></el-form-item>
        <el-form-item label="二级默认%"><el-input v-model="form.default_rate_lv2" /></el-form-item>
        <el-form-item label="结算延迟天数"><el-input v-model="form.settlement_delay_days" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const rows = ref([]);
const visible = ref(false);
const mode = ref("create");
const form = reactive(defaultForm());

function defaultForm() {
  return { id: null, name: "", default_rate_lv1: 10, default_rate_lv2: 5, settlement_delay_days: 7, enabled: true };
}

async function load() {
  const data = await http.get("/distribution/configs/?page=1");
  rows.value = data.results || [];
}

function openCreate() {
  Object.assign(form, defaultForm());
  mode.value = "create";
  visible.value = true;
}

function edit(row) {
  Object.assign(form, defaultForm(), row);
  mode.value = "edit";
  visible.value = true;
}

function payload() {
  return {
    name: form.name,
    default_rate_lv1: Number(form.default_rate_lv1 || 0),
    default_rate_lv2: Number(form.default_rate_lv2 || 0),
    settlement_delay_days: Number(form.settlement_delay_days || 0),
    enabled: form.enabled
  };
}

async function submit() {
  if (mode.value === "create") await http.post("/distribution/configs/", payload());
  else await http.put(`/distribution/configs/${form.id}/`, payload());
  ElMessage.success("分销配置已保存");
  visible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除分销配置 ${row.name}？`, "提示", { type: "warning" });
  await http.delete(`/distribution/configs/${row.id}/`);
  ElMessage.success("分销配置已删除");
  await load();
}

async function settle() {
  await http.post("/distribution/configs/settle-commissions/", {});
  ElMessage.success("已触发到期佣金结算");
}

onMounted(load);
</script>
