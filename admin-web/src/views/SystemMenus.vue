<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">菜单管理</div>
        <el-input v-model="search" clearable placeholder="搜索菜单/权限/路径" style="width: 240px" @keyup.enter="load" />
      </div>
      <el-button type="primary" @click="openCreate">新增菜单</el-button>
    </div>
    <div class="page-card">
      <el-table :data="treeRows" row-key="id" border default-expand-all>
        <el-table-column prop="name" label="菜单名称" min-width="180" />
        <el-table-column prop="code" label="菜单编码" min-width="220" show-overflow-tooltip />
        <el-table-column prop="icon" label="图标" width="120" />
        <el-table-column prop="path" label="路由路径" min-width="220" show-overflow-tooltip />
        <el-table-column prop="permission" label="权限标识" min-width="180" show-overflow-tooltip />
        <el-table-column prop="sort" label="排序" width="90" />
        <el-table-column label="显示" width="90">
          <template #default="{ row }"><StatusTag :value="row.is_show" /></template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="visible" :title="mode === 'create' ? '新增菜单' : '编辑菜单'" width="760px">
      <el-form :model="form" label-width="110px">
        <div class="form-grid">
          <el-form-item label="父级菜单">
            <el-select v-model="form.parent" clearable placeholder="一级菜单留空">
              <el-option v-for="item in parentOptions" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="菜单名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="菜单编码"><el-input v-model="form.code" /></el-form-item>
          <el-form-item label="图标"><el-input v-model="form.icon" /></el-form-item>
          <el-form-item label="路由路径"><el-input v-model="form.path" /></el-form-item>
          <el-form-item label="组件路径"><el-input v-model="form.component" /></el-form-item>
          <el-form-item label="权限标识"><el-input v-model="form.permission" /></el-form-item>
          <el-form-item label="排序"><el-input v-model="form.sort" /></el-form-item>
          <el-form-item label="层级"><el-input v-model="form.level" /></el-form-item>
          <el-form-item label="显示"><el-switch v-model="form.is_show" /></el-form-item>
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
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const rows = ref([]);
const search = ref("");
const visible = ref(false);
const mode = ref("create");
const form = reactive(defaultForm());

const parentOptions = computed(() => rows.value.filter((item) => !item.parent || item.level === 1));
const treeRows = computed(() => {
  const map = new Map();
  const roots = [];
  rows.value.forEach((item) => map.set(item.id, { ...item, children: [] }));
  map.forEach((item) => {
    if (item.parent && map.has(item.parent)) map.get(item.parent).children.push(item);
    else roots.push(item);
  });
  return roots.sort((a, b) => b.sort - a.sort);
});

function defaultForm() {
  return {
    id: null,
    parent: null,
    name: "",
    code: "",
    icon: "",
    path: "",
    component: "",
    permission: "",
    sort: 0,
    level: 1,
    is_show: true
  };
}

async function load() {
  const params = new URLSearchParams();
  if (search.value) params.set("search", search.value);
  const data = await http.get(`/system/menu-items/?${params.toString()}`);
  rows.value = data.results || data || [];
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
    parent: form.parent || null,
    name: form.name,
    code: form.code,
    icon: form.icon || "",
    path: form.path || "",
    component: form.component || "",
    permission: form.permission || "",
    sort: Number(form.sort || 0),
    level: Number(form.level || (form.parent ? 2 : 1)),
    is_show: form.is_show
  };
}

async function submit() {
  if (mode.value === "create") await http.post("/system/menu-items/", payload());
  else await http.put(`/system/menu-items/${form.id}/`, payload());
  ElMessage.success("菜单已保存");
  visible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除菜单 ${row.name}？子菜单也会一并删除。`, "提示", { type: "warning" });
  await http.delete(`/system/menu-items/${row.id}/`);
  ElMessage.success("菜单已删除");
  await load();
}

onMounted(load);
</script>
