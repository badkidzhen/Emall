<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">规格模板</div>
      <el-button type="primary" @click="openCreate">新增模板</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="模板名称" min-width="180" />
        <el-table-column label="规格维度" min-width="260">
          <template #default="{ row }">{{ (row.spec_names || []).join(" / ") }}</template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="visible" :title="mode === 'create' ? '新增规格模板' : '编辑规格模板'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="模板名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="规格维度"><el-input v-model="form.specText" placeholder="例如：颜色,尺码" /></el-form-item>
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
const form = reactive({ id: null, name: "", specText: "" });

async function load() {
  const data = await http.get("/catalog/spec-templates/?page=1");
  rows.value = data.results || [];
}

function openCreate() {
  Object.assign(form, { id: null, name: "", specText: "" });
  mode.value = "create";
  visible.value = true;
}

function edit(row) {
  Object.assign(form, { id: row.id, name: row.name, specText: (row.spec_names || []).join(",") });
  mode.value = "edit";
  visible.value = true;
}

async function submit() {
  const payload = {
    name: form.name,
    spec_names: form.specText.split(/[,，]/).map((item) => item.trim()).filter(Boolean)
  };
  if (mode.value === "create") {
    await http.post("/catalog/spec-templates/", payload);
  } else {
    await http.put(`/catalog/spec-templates/${form.id}/`, payload);
  }
  ElMessage.success("规格模板已保存");
  visible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除规格模板 ${row.name}？`, "提示", { type: "warning" });
  await http.delete(`/catalog/spec-templates/${row.id}/`);
  ElMessage.success("规格模板已删除");
  await load();
}

onMounted(load);
</script>
