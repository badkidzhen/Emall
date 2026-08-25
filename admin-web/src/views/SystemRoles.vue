<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">角色管理</div>
      <el-button type="primary" @click="openCreate">新增角色</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" min-width="180" />
        <el-table-column prop="permission_count" label="权限数量" width="120" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="visible" :title="mode === 'create' ? '新增角色' : '编辑角色'" width="760px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="角色名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="权限">
          <el-select v-model="form.permissions" multiple filterable collapse-tags collapse-tags-tooltip style="width: 100%">
            <el-option v-for="item in permissions" :key="item.id" :label="item.label" :value="item.id" />
          </el-select>
        </el-form-item>
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
const permissions = ref([]);
const visible = ref(false);
const mode = ref("create");
const form = reactive({ id: null, name: "", permissions: [] });

async function load() {
  const [roleData, permissionData] = await Promise.all([
    http.get("/system/roles/?page=1"),
    http.get("/system/permissions/?page_size=1000")
  ]);
  rows.value = roleData.results || [];
  permissions.value = permissionData.results || permissionData || [];
}

function openCreate() {
  Object.assign(form, { id: null, name: "", permissions: [] });
  mode.value = "create";
  visible.value = true;
}

function edit(row) {
  Object.assign(form, { id: row.id, name: row.name, permissions: row.permissions || [] });
  mode.value = "edit";
  visible.value = true;
}

async function submit() {
  const payload = { name: form.name, permissions: form.permissions };
  if (mode.value === "create") await http.post("/system/roles/", payload);
  else await http.put(`/system/roles/${form.id}/`, payload);
  ElMessage.success("角色已保存");
  visible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除角色 ${row.name}？`, "提示", { type: "warning" });
  await http.delete(`/system/roles/${row.id}/`);
  ElMessage.success("角色已删除");
  await load();
}

onMounted(load);
</script>
