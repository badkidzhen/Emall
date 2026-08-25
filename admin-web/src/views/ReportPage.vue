<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="page-title">{{ title }}</div>
      <el-button @click="load">刷新</el-button>
    </div>

    <div class="summary-grid" style="margin-bottom: 16px">
      <div v-for="item in cards" :key="item.label" class="summary-card">
        <div class="muted">{{ item.label }}</div>
        <div class="summary-value">{{ item.value }}</div>
      </div>
    </div>

    <div class="page-card">
      <el-table :data="rows" border stripe>
        <el-table-column prop="label" label="指标" min-width="180" />
        <el-table-column prop="value" label="数值" width="160" />
        <el-table-column prop="remark" label="说明" min-width="260" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import http from "../utils/http";

const route = useRoute();
const title = computed(() => route.meta.title || "数据报表");
const cards = ref([]);
const rows = ref([]);

const configs = {
  "/reports/users": {
    cards: [
      ["用户总数", "/users/?page=1"],
      ["会员等级", "/users/levels/?page=1"],
      ["待实名", "/users/?realname_status=pending&page=1"],
      ["分销商", "/users/?is_distributor=true&page=1"]
    ]
  },
  "/reports/sales": {
    cards: [
      ["订单总数", "/orders/?page=1"],
      ["商品总数", "/catalog/products/?page=1"],
      ["退款申请", "/orders/refunds/?page=1"],
      ["发票申请", "/orders/invoices/?page=1"]
    ]
  },
  "/reports/commissions": {
    cards: [
      ["佣金记录", "/distribution/commissions/?page=1"],
      ["团队统计", "/distribution/team-stats/?page=1"],
      ["奖金分配", "/rewards/records/?page=1"],
      ["奖金池", "/rewards/pools/?page=1"]
    ]
  },
  "/reports/marketing": {
    cards: [
      ["优惠券模板", "/marketing/coupon-templates/?page=1"],
      ["团购活动", "/marketing/groups/?page=1"],
      ["秒杀活动", "/marketing/seckills/?page=1"],
      ["购买记录", "/marketing/activity-records/?page=1"]
    ]
  },
  "/orders/statistics": {
    cards: [
      ["订单总数", "/orders/?page=1"],
      ["待付款", "/orders/?status=pending_payment&page=1"],
      ["待发货", "/orders/?status=pending_shipment&page=1"],
      ["已完成", "/orders/?status=completed&page=1"]
    ]
  }
};

async function load() {
  const config = configs[route.path] || configs["/reports/sales"];
  const results = await Promise.all(
    config.cards.map(async ([label, url]) => {
      const data = await http.get(url);
      return { label, value: data.count || 0, remark: "基于当前接口分页总数统计" };
    })
  );
  cards.value = results;
  rows.value = results;
}

watch(() => route.path, load);
onMounted(load);
</script>
