<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">会员等级</div>
      <el-button type="primary" @click="openCreate">新增等级</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="等级名称" min-width="140" />
        <el-table-column prop="upgrade_amount" label="消费升级金额" width="140" />
        <el-table-column prop="team_upgrade_amount" label="团队升级金额" width="140" />
        <el-table-column prop="commission_rate_lv1" label="一级佣金%" width="120" />
        <el-table-column prop="commission_rate_lv2" label="二级佣金%" width="120" />
        <el-table-column prop="discount" label="折扣" width="100" />
        <el-table-column prop="sort" label="排序" width="90" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="visible" :title="mode === 'create' ? '新增会员等级' : '编辑会员等级'" width="760px">
      <el-form :model="form" label-width="120px">
        <div class="form-grid">
          <el-form-item label="等级名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="消费升级金额"><el-input v-model="form.upgrade_amount" /></el-form-item>
          <el-form-item label="团队升级金额"><el-input v-model="form.team_upgrade_amount" /></el-form-item>
          <el-form-item label="一级佣金%"><el-input v-model="form.commission_rate_lv1" /></el-form-item>
          <el-form-item label="二级佣金%"><el-input v-model="form.commission_rate_lv2" /></el-form-item>
          <el-form-item label="折扣"><el-input v-model="form.discount" /></el-form-item>
          <el-form-item label="排序"><el-input v-model="form.sort" /></el-form-item>
        </div>
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
import http from "../utils/http";

const rows = ref([]);
const visible = ref(false);
const mode = ref("create");
const form = reactive(defaultForm());

function defaultForm() {
  return {
    id: null,
    name: "",
    upgrade_amount: 0,
    team_upgrade_amount: 0,
    commission_rate_lv1: 0,
    commission_rate_lv2: 0,
    discount: 1,
    sort: 0
  };
}

async function load() {
  const data = await http.get("/users/levels/?page=1");
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
    upgrade_amount: Number(form.upgrade_amount || 0),
    team_upgrade_amount: Number(form.team_upgrade_amount || 0),
    commission_rate_lv1: Number(form.commission_rate_lv1 || 0),
    commission_rate_lv2: Number(form.commission_rate_lv2 || 0),
    discount: Number(form.discount || 1),
    sort: Number(form.sort || 0)
  };
}

async function submit() {
  if (mode.value === "create") {
    await http.post("/users/levels/", payload());
  } else {
    await http.put(`/users/levels/${form.id}/`, payload());
  }
  ElMessage.success("会员等级已保存");
  visible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除会员等级 ${row.name}？`, "提示", { type: "warning" });
  await http.delete(`/users/levels/${row.id}/`);
  ElMessage.success("会员等级已删除");
  await load();
}

onMounted(load);
</script>
