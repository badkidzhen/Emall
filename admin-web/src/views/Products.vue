<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">商品管理</div>
        <el-input v-model="query.search" clearable placeholder="搜索商品" style="width: 220px" @keyup.enter="search" />
        <el-select v-model="query.sale_status" clearable placeholder="销售状态" style="width: 140px" @change="search">
          <el-option label="草稿" value="draft" />
          <el-option label="上架" value="on_sale" />
          <el-option label="下架" value="off_sale" />
        </el-select>
      </div>
      <el-button type="primary" @click="openCreate">新增商品</el-button>
    </div>

    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="220" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }"><StatusTag :value="row.sale_status" :map="saleStatusMap" /></template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="120" />
        <el-table-column prop="total_stock" label="库存" width="100" />
        <el-table-column label="分销" width="90">
          <template #default="{ row }"><StatusTag :value="row.is_distribution" /></template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="edit(row)">编辑</el-button>
            <el-button link type="success" @click="openSku(row)">SKU</el-button>
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
        :current-page="query.page"
        @current-change="changePage"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增商品' : '编辑商品'" width="820px">
      <el-form :model="form" label-width="110px">
        <div class="form-grid">
          <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
          <el-form-item label="副标题"><el-input v-model="form.sub_title" /></el-form-item>
          <el-form-item label="展示价"><el-input v-model="form.price" /></el-form-item>
          <el-form-item label="划线价"><el-input v-model="form.market_price" /></el-form-item>
          <el-form-item label="销售状态">
            <el-select v-model="form.sale_status">
              <el-option label="草稿" value="draft" />
              <el-option label="上架" value="on_sale" />
              <el-option label="下架" value="off_sale" />
            </el-select>
          </el-form-item>
          <el-form-item label="总库存"><el-input v-model="form.total_stock" /></el-form-item>
          <el-form-item label="参与分销"><el-switch v-model="form.is_distribution" /></el-form-item>
          <el-form-item label="佣金类型">
            <el-select v-model="form.commission_type" clearable placeholder="选择佣金类型">
              <el-option v-for="item in commissionTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="一级佣金%"><el-input v-model="form.commission_rate_lv1" /></el-form-item>
          <el-form-item label="二级佣金%"><el-input v-model="form.commission_rate_lv2" /></el-form-item>
          <el-form-item label="商品分类" class="full-width">
            <el-select v-model="form.categories" multiple clearable placeholder="选择分类">
              <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="封面" class="full-width"><AdminImageUpload v-model="form.cover" /></el-form-item>
          <el-form-item label="详情" class="full-width"><el-input v-model="form.detail" type="textarea" :rows="4" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="skuVisible" :title="`SKU 管理 - ${currentProduct?.title || ''}`" width="900px">
      <div class="toolbar">
        <div class="muted">当前商品 SKU：{{ skus.length }}</div>
        <el-button type="primary" @click="generatorVisible = true">生成 SKU</el-button>
      </div>
      <el-table :data="skus" border stripe>
        <el-table-column prop="sku_code" label="SKU 编码" min-width="180" />
        <el-table-column prop="specs" label="规格" min-width="180">
          <template #default="{ row }">{{ formatSpecs(row.specs) }}</template>
        </el-table-column>
        <el-table-column prop="price" label="售价" width="100" />
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column prop="locked_stock" label="锁定" width="100" />
        <el-table-column prop="is_active" label="启用" width="90" />
      </el-table>
    </el-dialog>

    <el-dialog v-model="generatorVisible" title="批量生成 SKU" width="900px">
      <el-alert
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 16px"
        title="按行维护规格名称，按列维护规格值。系统会自动组合生成 SKU。"
      />
      <el-form :model="skuForm" label-width="110px">
        <el-form-item label="规格配置" class="full-width">
          <div class="spec-builder">
            <div class="spec-header">
              <span>规格名称</span>
              <span>规格值</span>
              <span>操作</span>
            </div>
            <div v-for="(spec, specIndex) in skuForm.spec_options" :key="spec.localId" class="spec-row">
              <el-input v-model="spec.name" placeholder="如：颜色 / 尺码 / 镜头" />
              <div class="value-list">
                <div v-for="(value, valueIndex) in spec.values" :key="valueIndex" class="value-item">
                  <el-input v-model="spec.values[valueIndex]" placeholder="规格值" />
                  <el-button text type="danger" @click="removeSpecValue(specIndex, valueIndex)">删除</el-button>
                </div>
                <el-button plain size="small" @click="addSpecValue(specIndex)">新增规格值</el-button>
              </div>
              <el-button text type="danger" @click="removeSpecRow(specIndex)">删除行</el-button>
            </div>
            <div class="spec-actions">
              <el-button type="primary" plain @click="addSpecRow">新增规格行</el-button>
              <span class="muted">预计生成 {{ skuCombinationCount }} 个 SKU</span>
            </div>
          </div>
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="售价"><el-input v-model="skuForm.price" /></el-form-item>
          <el-form-item label="划线价"><el-input v-model="skuForm.market_price" /></el-form-item>
          <el-form-item label="库存"><el-input v-model="skuForm.stock" /></el-form-item>
          <el-form-item label="预警库存"><el-input v-model="skuForm.warning_stock" /></el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="generatorVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSku">生成并覆盖</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import AdminImageUpload from "../components/AdminImageUpload.vue";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const rows = ref([]);
const total = ref(0);
const pageSize = 20;
const categories = ref([]);
const skus = ref([]);
const currentProduct = ref(null);
const dialogVisible = ref(false);
const dialogMode = ref("create");
const skuVisible = ref(false);
const generatorVisible = ref(false);

const query = reactive({ page: 1, search: "", sale_status: "" });
const saleStatusMap = {
  draft: { label: "草稿", type: "info" },
  on_sale: { label: "上架", type: "success" },
  off_sale: { label: "下架", type: "warning" }
};
const commissionTypeOptions = [
  { label: "按比例返佣", value: "percent" },
  { label: "固定金额返佣", value: "fixed" }
];
const form = reactive(defaultProduct());
const skuForm = reactive({
  spec_options: defaultSpecOptions(),
  price: "0",
  market_price: "0",
  stock: 0,
  warning_stock: 0
});

const skuCombinationCount = computed(() => {
  const options = normalizeSpecOptions({ silent: true });
  if (!options.length) return 0;
  return options.reduce((total, option) => total * option.values.length, 1);
});

function defaultProduct() {
  return {
    id: null,
    title: "",
    sub_title: "",
    cover: "",
    detail: "",
    sale_status: "draft",
    price: 0,
    market_price: 0,
    total_stock: 0,
    is_distribution: true,
    commission_type: "percent",
    commission_rate_lv1: 0,
    commission_rate_lv2: 0,
    categories: []
  };
}

function defaultSpecOptions() {
  return [
    { localId: Date.now() + 1, name: "规格", values: ["默认"] }
  ];
}

async function load() {
  const params = new URLSearchParams({ page: String(query.page) });
  if (query.search) params.set("search", query.search);
  if (query.sale_status) params.set("sale_status", query.sale_status);
  const data = await http.get(`/catalog/products/?${params.toString()}`);
  rows.value = data.results || [];
  total.value = data.count || 0;
}

function search() {
  query.page = 1;
  load();
}

async function loadCategories() {
  const data = await http.get("/catalog/categories/?page=1");
  categories.value = data.results || [];
}

function openCreate() {
  Object.assign(form, defaultProduct());
  dialogMode.value = "create";
  dialogVisible.value = true;
}

function edit(row) {
  Object.assign(form, defaultProduct(), {
    ...row,
    categories: Array.isArray(row.categories) ? row.categories : []
  });
  dialogMode.value = "edit";
  dialogVisible.value = true;
}

function buildPayload() {
  return {
    title: form.title,
    sub_title: form.sub_title,
    cover: form.cover,
    detail: form.detail,
    sale_status: form.sale_status,
    price: Number(form.price || 0),
    market_price: Number(form.market_price || 0),
    total_stock: Number(form.total_stock || 0),
    is_distribution: form.is_distribution,
    commission_type: form.commission_type,
    commission_rate_lv1: Number(form.commission_rate_lv1 || 0),
    commission_rate_lv2: Number(form.commission_rate_lv2 || 0),
    categories: form.categories
  };
}

async function submit() {
  if (!form.title.trim()) {
    ElMessage.warning("请输入商品标题");
    return;
  }
  if (dialogMode.value === "create") {
    await http.post("/catalog/products/", buildPayload());
    ElMessage.success("商品创建成功");
  } else {
    await http.put(`/catalog/products/${form.id}/`, buildPayload());
    ElMessage.success("商品保存成功");
  }
  dialogVisible.value = false;
  await load();
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除商品 ${row.title} ?`, "提示", { type: "warning" });
  await http.delete(`/catalog/products/${row.id}/`);
  ElMessage.success("商品已删除");
  await load();
}

async function openSku(row) {
  currentProduct.value = row;
  skuVisible.value = true;
  resetSkuForm(row);
  await loadSkus(row.id);
}

async function loadSkus(productId) {
  const data = await http.get(`/catalog/skus/?product=${productId}`);
  skus.value = data.results || [];
}

function formatSpecs(specs) {
  if (!specs) return "-";
  return Object.entries(specs).map(([key, value]) => `${key}: ${value}`).join(" / ");
}

function resetSkuForm(product = {}) {
  skuForm.spec_options = defaultSpecOptions();
  skuForm.price = product.price || "0";
  skuForm.market_price = product.market_price || "0";
  skuForm.stock = product.total_stock || 0;
  skuForm.warning_stock = 0;
}

function addSpecRow() {
  skuForm.spec_options.push({
    localId: Date.now() + Math.random(),
    name: "",
    values: [""]
  });
}

function removeSpecRow(index) {
  if (skuForm.spec_options.length <= 1) {
    ElMessage.warning("至少保留一行规格");
    return;
  }
  skuForm.spec_options.splice(index, 1);
}

function addSpecValue(specIndex) {
  skuForm.spec_options[specIndex].values.push("");
}

function removeSpecValue(specIndex, valueIndex) {
  const values = skuForm.spec_options[specIndex].values;
  if (values.length <= 1) {
    ElMessage.warning("每行至少保留一个规格值");
    return;
  }
  values.splice(valueIndex, 1);
}

function normalizeSpecOptions({ silent = false } = {}) {
  const names = new Set();
  const options = [];
  for (const spec of skuForm.spec_options) {
    const name = String(spec.name || "").trim();
    const values = (spec.values || []).map((value) => String(value || "").trim()).filter(Boolean);
    if (!name && !values.length) continue;
    if (!name) {
      if (!silent) ElMessage.warning("请填写规格名称");
      return [];
    }
    if (names.has(name)) {
      if (!silent) ElMessage.warning(`规格名称重复：${name}`);
      return [];
    }
    if (!values.length) {
      if (!silent) ElMessage.warning(`请为「${name}」填写至少一个规格值`);
      return [];
    }
    names.add(name);
    options.push({ name, values: Array.from(new Set(values)) });
  }
  if (!options.length && !silent) {
    ElMessage.warning("请至少配置一组规格");
  }
  return options;
}

async function submitSku() {
  const specOptions = normalizeSpecOptions();
  if (!specOptions.length) return;
  await http.post(`/catalog/products/${currentProduct.value.id}/generate-skus/`, {
    spec_options: specOptions,
    price: skuForm.price,
    market_price: skuForm.market_price,
    stock: Number(skuForm.stock),
    warning_stock: Number(skuForm.warning_stock),
    overwrite: true
  });
  generatorVisible.value = false;
  ElMessage.success("SKU 生成成功");
  await loadSkus(currentProduct.value.id);
  await load();
}

function changePage(page) {
  query.page = page;
  load();
}

onMounted(async () => {
  await Promise.all([load(), loadCategories()]);
});
</script>

<style scoped>
.spec-builder {
  width: 100%;
  border: 1px solid #e5eaf3;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.spec-header,
.spec-row {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr) 88px;
  gap: 12px;
  align-items: flex-start;
}

.spec-header {
  padding: 12px 14px;
  background: #f7f9fc;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.spec-row {
  padding: 14px;
  border-top: 1px solid #edf1f7;
}

.value-list {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 10px;
}

.value-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 54px;
  gap: 8px;
  align-items: center;
}

.spec-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-top: 1px solid #edf1f7;
  background: #fbfcff;
}
</style>
