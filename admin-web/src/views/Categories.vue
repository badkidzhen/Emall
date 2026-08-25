<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">分类管理</div>
      <el-button type="primary" @click="openCreate">新增分类</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe row-key="id">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column prop="parent" label="父级ID" width="100" />
        <el-table-column prop="level" label="层级" width="90" />
        <el-table-column prop="sort" label="排序" width="90" />
        <el-table-column label="展示" width="90">
          <template #default="{ row }"><StatusTag :value="row.is_show" /></template>
        </el-table-column>
        <el-table-column label="分销" width="90">
          <template #default="{ row }"><StatusTag :value="row.is_distribution" /></template>
        </el-table-column>
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.is_active" /></template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        class="table-pagination"
        background
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @current-change="changePage"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增分类' : '编辑分类'" width="720px">
      <el-form :model="form" label-width="110px">
        <div class="form-grid">
          <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="父级ID"><el-input v-model="form.parent" placeholder="一级分类留空" /></el-form-item>
          <el-form-item label="层级"><el-input v-model="form.level" /></el-form-item>
          <el-form-item label="排序"><el-input v-model="form.sort" /></el-form-item>
          <el-form-item label="展示"><el-switch v-model="form.is_show" /></el-form-item>
          <el-form-item label="参与分销"><el-switch v-model="form.is_distribution" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
          <el-form-item label="图标" class="full-width"><AdminImageUpload v-model="form.icon" /></el-form-item>
          <el-form-item label="Banner" class="full-width"><AdminImageUpload v-model="form.banner" /></el-form-item>
          <el-form-item label="SEO标题"><el-input v-model="form.seo_title" /></el-form-item>
          <el-form-item label="SEO关键词"><el-input v-model="form.seo_keywords" /></el-form-item>
          <el-form-item label="SEO描述" class="full-width"><el-input v-model="form.seo_description" type="textarea" :rows="3" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import AdminImageUpload from "../components/AdminImageUpload.vue";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const rows = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const dialogVisible = ref(false);
const dialogMode = ref("create");
const form = reactive(defaultCategory());

function defaultCategory() {
  return {
    id: null,
    name: "",
    parent: "",
    level: 1,
    sort: 0,
    icon: "",
    banner: "",
    is_show: true,
    is_distribution: true,
    is_active: true,
    seo_title: "",
    seo_keywords: "",
    seo_description: ""
  };
}

async function load() {
  const data = await http.get(`/catalog/categories/?page=${page.value}`);
  rows.value = data.results || [];
  total.value = data.count || 0;
}

function openCreate() {
  Object.assign(form, defaultCategory());
  dialogMode.value = "create";
  dialogVisible.value = true;
}

function edit(row) {
  Object.assign(form, defaultCategory(), row);
  dialogMode.value = "edit";
  dialogVisible.value = true;
}

function buildPayload() {
  return {
    name: form.name,
    parent: form.parent || null,
    level: Number(form.level || 1),
    sort: Number(form.sort || 0),
    icon: form.icon || "",
    banner: form.banner || "",
    is_show: form.is_show,
    is_distribution: form.is_distribution,
    is_active: form.is_active,
    seo_title: form.seo_title || "",
    seo_keywords: form.seo_keywords || "",
    seo_description: form.seo_description || ""
  };
}

async function submit() {
  if (!form.name.trim()) {
    ElMessage.warning("请输入分类名称");
    return;
  }
  if (dialogMode.value === "create") {
    await http.post("/catalog/categories/", buildPayload());
    ElMessage.success("分类创建成功");
  } else {
    await http.put(`/catalog/categories/${form.id}/`, buildPayload());
    ElMessage.success("分类保存成功");
  }
  dialogVisible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除分类 ${row.name} ?`, "提示", { type: "warning" });
  await http.delete(`/catalog/categories/${row.id}/`);
  ElMessage.success("分类已删除");
  await load();
}

function changePage(value) {
  page.value = value;
  load();
}

onMounted(load);
</script>
