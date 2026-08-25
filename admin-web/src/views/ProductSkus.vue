<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">SKU 管理</div>
        <el-input v-model="query.product" clearable placeholder="商品ID" style="width: 140px" @keyup.enter="load" />
      </div>
      <el-button @click="load">刷新</el-button>
    </div>
    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="product" label="商品ID" width="90" />
        <el-table-column prop="sku_code" label="SKU编码" min-width="180" />
        <el-table-column label="规格" min-width="220">
          <template #default="{ row }">{{ formatSpecs(row.specs) }}</template>
        </el-table-column>
        <el-table-column prop="price" label="售价" width="110" />
        <el-table-column prop="market_price" label="划线价" width="110" />
        <el-table-column prop="stock" label="库存" width="90" />
        <el-table-column prop="locked_stock" label="锁定" width="90" />
        <el-table-column prop="warning_stock" label="预警" width="90" />
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.is_active" /></template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="visible" title="编辑 SKU" width="720px">
      <el-form :model="form" label-width="110px">
        <div class="form-grid">
          <el-form-item label="SKU编码"><el-input v-model="form.sku_code" /></el-form-item>
          <el-form-item label="售价"><el-input v-model="form.price" /></el-form-item>
          <el-form-item label="划线价"><el-input v-model="form.market_price" /></el-form-item>
          <el-form-item label="库存"><el-input v-model="form.stock" /></el-form-item>
          <el-form-item label="锁定库存"><el-input v-model="form.locked_stock" /></el-form-item>
          <el-form-item label="预警库存"><el-input v-model="form.warning_stock" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
          <el-form-item label="规格" class="full-width">
            <div class="spec-editor">
              <div class="spec-editor-header">
                <span>规格名称</span>
                <span>规格值</span>
                <span>操作</span>
              </div>
              <div v-for="(item, index) in form.specRows" :key="item.localId" class="spec-editor-row">
                <el-input v-model="item.name" placeholder="如：颜色" />
                <el-input v-model="item.value" placeholder="如：红色" />
                <el-button text type="danger" @click="removeSpecRow(index)">删除</el-button>
              </div>
              <div class="spec-editor-actions">
                <el-button type="primary" plain @click="addSpecRow">新增规格</el-button>
              </div>
            </div>
          </el-form-item>
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
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const query = reactive({ product: "" });
const rows = ref([]);
const visible = ref(false);
const form = reactive({});

async function load() {
  const params = new URLSearchParams({ page: "1" });
  if (query.product) params.set("product", query.product);
  const data = await http.get(`/catalog/skus/?${params.toString()}`);
  rows.value = data.results || [];
}

function edit(row) {
  Object.assign(form, row, { specRows: specsToRows(row.specs || {}) });
  visible.value = true;
}

async function submit() {
  const specs = rowsToSpecs();
  if (!specs) return;
  await http.patch(`/catalog/skus/${form.id}/`, {
    sku_code: form.sku_code,
    specs,
    price: Number(form.price || 0),
    market_price: Number(form.market_price || 0),
    stock: Number(form.stock || 0),
    locked_stock: Number(form.locked_stock || 0),
    warning_stock: Number(form.warning_stock || 0),
    is_active: form.is_active
  });
  ElMessage.success("SKU 已保存");
  visible.value = false;
  await load();
}

function formatSpecs(specs) {
  if (!specs || !Object.keys(specs).length) return "-";
  return Object.entries(specs).map(([key, value]) => `${key}: ${value}`).join(" / ");
}

function specsToRows(specs) {
  const rows = Object.entries(specs).map(([name, value]) => ({
    localId: Date.now() + Math.random(),
    name,
    value
  }));
  return rows.length ? rows : [{ localId: Date.now(), name: "", value: "" }];
}

function addSpecRow() {
  form.specRows.push({ localId: Date.now() + Math.random(), name: "", value: "" });
}

function removeSpecRow(index) {
  if (form.specRows.length <= 1) {
    ElMessage.warning("至少保留一行规格");
    return;
  }
  form.specRows.splice(index, 1);
}

function rowsToSpecs() {
  const specs = {};
  for (const row of form.specRows || []) {
    const name = String(row.name || "").trim();
    const value = String(row.value || "").trim();
    if (!name && !value) continue;
    if (!name) {
      ElMessage.warning("请填写规格名称");
      return null;
    }
    if (!value) {
      ElMessage.warning(`请填写「${name}」的规格值`);
      return null;
    }
    if (specs[name]) {
      ElMessage.warning(`规格名称重复：${name}`);
      return null;
    }
    specs[name] = value;
  }
  return specs;
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除 SKU ${row.sku_code}？`, "提示", { type: "warning" });
  await http.delete(`/catalog/skus/${row.id}/`);
  ElMessage.success("SKU 已删除");
  await load();
}

onMounted(load);
</script>

<style scoped>
.spec-editor {
  width: 100%;
  border: 1px solid #e5eaf3;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.spec-editor-header,
.spec-editor-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 72px;
  gap: 12px;
  align-items: center;
}

.spec-editor-header {
  padding: 12px 14px;
  background: #f7f9fc;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.spec-editor-row {
  padding: 12px 14px;
  border-top: 1px solid #edf1f7;
}

.spec-editor-actions {
  padding: 12px 14px;
  border-top: 1px solid #edf1f7;
  background: #fbfcff;
}
</style>
