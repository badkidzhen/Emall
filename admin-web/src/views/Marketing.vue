<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">{{ pageTitle }}</div>
        <el-tabs v-if="showTabs" v-model="active" @tab-change="load">
          <el-tab-pane label="优惠券" name="coupon" />
          <el-tab-pane label="团购" name="group" />
          <el-tab-pane label="秒杀" name="seckill" />
          <el-tab-pane label="购买记录" name="record" />
        </el-tabs>
      </div>
      <el-button v-if="active !== 'record'" type="primary" @click="openCreate">新增{{ activeLabel }}</el-button>
    </div>

    <div v-if="showTabs" class="summary-grid" style="margin-bottom: 16px">
      <div class="summary-card"><div class="muted">优惠券模板</div><div class="summary-value">{{ couponCount }}</div></div>
      <div class="summary-card"><div class="muted">团购活动</div><div class="summary-value">{{ groupCount }}</div></div>
      <div class="summary-card"><div class="muted">秒杀活动</div><div class="summary-value">{{ seckillCount }}</div></div>
      <div class="summary-card"><div class="muted">购买记录</div><div class="summary-value">{{ recordCount }}</div></div>
    </div>

    <div class="page-card">
      <el-table v-if="active === 'coupon'" :data="coupons" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="coupon_type" label="类型" width="140" />
        <el-table-column prop="threshold_amount" label="门槛" width="100" />
        <el-table-column prop="discount_amount" label="减免" width="100" />
        <el-table-column prop="discount_rate" label="折扣" width="100" />
        <el-table-column prop="total_quantity" label="总量" width="100" />
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editCoupon(row)">编辑</el-button>
            <el-button link type="danger" @click="remove('/marketing/coupon-templates/', row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-table v-if="active === 'group'" :data="groups" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="sku" label="SKU ID" width="100" />
        <el-table-column prop="group_price" label="团购价" width="120" />
        <el-table-column prop="min_members" label="成团人数" width="110" />
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.enabled" /></template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editGroup(row)">编辑</el-button>
            <el-button link type="danger" @click="remove('/marketing/groups/', row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-table v-if="active === 'seckill'" :data="seckills" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="sku" label="SKU ID" width="100" />
        <el-table-column prop="seckill_price" label="秒杀价" width="120" />
        <el-table-column prop="per_user_limit" label="限购" width="100" />
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column label="启用" width="90">
          <template #default="{ row }"><StatusTag :value="row.enabled" /></template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editSeckill(row)">编辑</el-button>
            <el-button link type="danger" @click="remove('/marketing/seckills/', row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-table v-if="active === 'record'" :data="records" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user" label="用户ID" width="100" />
        <el-table-column prop="activity_type" label="活动类型" width="120" />
        <el-table-column prop="activity_id" label="活动ID" width="100" />
        <el-table-column prop="order" label="订单ID" width="100" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="created_at" label="创建时间" min-width="180" />
      </el-table>
      <el-pagination
        class="table-pagination"
        background
        layout="total, prev, pager, next"
        :total="currentTotal"
        :page-size="pageSize"
        :current-page="pages[active]"
        @current-change="changePage"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="820px">
      <el-form :model="form" label-width="120px">
        <div v-if="dialogType === 'coupon'" class="form-grid">
          <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="类型">
            <el-select v-model="form.coupon_type">
              <el-option label="满减券" value="full_reduction" />
              <el-option label="折扣券" value="discount" />
              <el-option label="新人券" value="new_user" />
              <el-option label="指定商品券" value="product" />
              <el-option label="指定分类券" value="category" />
            </el-select>
          </el-form-item>
          <el-form-item label="门槛"><el-input v-model="form.threshold_amount" /></el-form-item>
          <el-form-item label="减免"><el-input v-model="form.discount_amount" /></el-form-item>
          <el-form-item label="折扣"><el-input v-model="form.discount_rate" /></el-form-item>
          <el-form-item label="总量"><el-input v-model="form.total_quantity" /></el-form-item>
          <el-form-item label="每人限领"><el-input v-model="form.per_user_limit" /></el-form-item>
          <el-form-item label="有效天数"><el-input v-model="form.valid_days" /></el-form-item>
          <el-form-item label="开始时间"><el-date-picker v-model="form.started_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss+08:00" /></el-form-item>
          <el-form-item label="结束时间"><el-date-picker v-model="form.ended_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss+08:00" /></el-form-item>
        </div>

        <div v-if="dialogType === 'group'" class="form-grid">
          <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="SKU">
            <el-select v-model="form.sku" filterable placeholder="选择 SKU">
              <el-option v-for="item in skus" :key="item.id" :label="`${item.sku_code} / ${item.price}`" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="团购价"><el-input v-model="form.group_price" /></el-form-item>
          <el-form-item label="成团人数"><el-input v-model="form.min_members" /></el-form-item>
          <el-form-item label="库存"><el-input v-model="form.stock" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
          <el-form-item label="开始时间"><el-date-picker v-model="form.started_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss+08:00" /></el-form-item>
          <el-form-item label="结束时间"><el-date-picker v-model="form.ended_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss+08:00" /></el-form-item>
        </div>

        <div v-if="dialogType === 'seckill'" class="form-grid">
          <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="SKU">
            <el-select v-model="form.sku" filterable placeholder="选择 SKU">
              <el-option v-for="item in skus" :key="item.id" :label="`${item.sku_code} / ${item.price}`" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="秒杀价"><el-input v-model="form.seckill_price" /></el-form-item>
          <el-form-item label="每人限购"><el-input v-model="form.per_user_limit" /></el-form-item>
          <el-form-item label="库存"><el-input v-model="form.stock" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
          <el-form-item label="开始时间"><el-date-picker v-model="form.started_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss+08:00" /></el-form-item>
          <el-form-item label="结束时间"><el-date-picker v-model="form.ended_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss+08:00" /></el-form-item>
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
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const route = useRoute();
const active = ref(route.meta.marketingTab || "coupon");
const coupons = ref([]);
const groups = ref([]);
const seckills = ref([]);
const records = ref([]);
const skus = ref([]);
const couponCount = ref(0);
const groupCount = ref(0);
const seckillCount = ref(0);
const recordCount = ref(0);
const pageSize = 20;
const pages = reactive({ coupon: 1, group: 1, seckill: 1, record: 1 });
const dialogVisible = ref(false);
const dialogMode = ref("create");
const dialogType = ref("coupon");
const form = reactive({});

const showTabs = computed(() => !route.meta.marketingTab);
const pageTitle = computed(() => route.meta.title || "营销管理");
const activeLabel = computed(() => ({ coupon: "优惠券", group: "团购", seckill: "秒杀" }[active.value] || ""));
const dialogTitle = computed(() => `${dialogMode.value === "create" ? "新增" : "编辑"}${activeLabel.value}`);
const currentTotal = computed(() => ({ coupon: couponCount.value, group: groupCount.value, seckill: seckillCount.value, record: recordCount.value }[active.value] || 0));

function couponForm() {
  return { id: null, name: "", coupon_type: "full_reduction", threshold_amount: 0, discount_amount: 0, discount_rate: 1, total_quantity: 0, per_user_limit: 1, valid_days: 7, started_at: "", ended_at: "" };
}

function groupForm() {
  return { id: null, name: "", sku: null, group_price: 0, min_members: 2, stock: 0, started_at: "", ended_at: "", enabled: true };
}

function seckillForm() {
  return { id: null, name: "", sku: null, seckill_price: 0, per_user_limit: 1, stock: 0, started_at: "", ended_at: "", enabled: true };
}

async function load() {
  const [a, b, c, d] = await Promise.all([
    http.get(`/marketing/coupon-templates/?page=${pages.coupon}`),
    http.get(`/marketing/groups/?page=${pages.group}`),
    http.get(`/marketing/seckills/?page=${pages.seckill}`),
    http.get(`/marketing/activity-records/?page=${pages.record}`)
  ]);
  coupons.value = a.results || [];
  groups.value = b.results || [];
  seckills.value = c.results || [];
  records.value = d.results || [];
  couponCount.value = a.count || 0;
  groupCount.value = b.count || 0;
  seckillCount.value = c.count || 0;
  recordCount.value = d.count || 0;
}

async function loadSkus() {
  const data = await http.get("/catalog/skus/?page=1");
  skus.value = data.results || [];
}

function openCreate() {
  dialogType.value = active.value;
  dialogMode.value = "create";
  Object.assign(form, dialogType.value === "coupon" ? couponForm() : dialogType.value === "group" ? groupForm() : seckillForm());
  dialogVisible.value = true;
}

function editCoupon(row) {
  dialogType.value = "coupon";
  dialogMode.value = "edit";
  Object.assign(form, couponForm(), row);
  dialogVisible.value = true;
}

function editGroup(row) {
  dialogType.value = "group";
  dialogMode.value = "edit";
  Object.assign(form, groupForm(), row);
  dialogVisible.value = true;
}

function editSeckill(row) {
  dialogType.value = "seckill";
  dialogMode.value = "edit";
  Object.assign(form, seckillForm(), row);
  dialogVisible.value = true;
}

function buildPayload() {
  if (dialogType.value === "coupon") {
    return {
      name: form.name,
      coupon_type: form.coupon_type,
      threshold_amount: Number(form.threshold_amount || 0),
      discount_amount: Number(form.discount_amount || 0),
      discount_rate: Number(form.discount_rate || 1),
      total_quantity: Number(form.total_quantity || 0),
      per_user_limit: Number(form.per_user_limit || 1),
      valid_days: Number(form.valid_days || 7),
      started_at: form.started_at,
      ended_at: form.ended_at
    };
  }
  if (dialogType.value === "group") {
    return {
      name: form.name,
      sku: form.sku,
      group_price: Number(form.group_price || 0),
      min_members: Number(form.min_members || 2),
      stock: Number(form.stock || 0),
      started_at: form.started_at,
      ended_at: form.ended_at,
      enabled: form.enabled
    };
  }
  return {
    name: form.name,
    sku: form.sku,
    seckill_price: Number(form.seckill_price || 0),
    per_user_limit: Number(form.per_user_limit || 1),
    stock: Number(form.stock || 0),
    started_at: form.started_at,
    ended_at: form.ended_at,
    enabled: form.enabled
  };
}

function endpoint() {
  return {
    coupon: "/marketing/coupon-templates/",
    group: "/marketing/groups/",
    seckill: "/marketing/seckills/"
  }[dialogType.value];
}

async function submit() {
  if (!form.name?.trim()) {
    ElMessage.warning("请输入名称");
    return;
  }
  const url = endpoint();
  if (dialogMode.value === "create") {
    await http.post(url, buildPayload());
    ElMessage.success("创建成功");
  } else {
    await http.put(`${url}${form.id}/`, buildPayload());
    ElMessage.success("保存成功");
  }
  dialogVisible.value = false;
  await load();
}

async function remove(url, row) {
  await ElMessageBox.confirm(`确认删除 ${row.name} ?`, "提示", { type: "warning" });
  await http.delete(`${url}${row.id}/`);
  ElMessage.success("删除成功");
  await load();
}

function changePage(page) {
  pages[active.value] = page;
  load();
}

onMounted(async () => {
  active.value = route.meta.marketingTab || "coupon";
  await Promise.all([load(), loadSkus()]);
});

watch(
  () => route.meta.marketingTab,
  async (tab) => {
    if (tab) {
      active.value = tab;
      await load();
    }
  }
);
</script>
