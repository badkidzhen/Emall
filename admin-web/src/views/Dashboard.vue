<template>
  <div class="page-shell">
    <div class="page-title">数据看板</div>
    <div class="summary-grid">
      <div v-for="item in cards" :key="item.label" class="summary-card">
        <div class="muted">{{ item.label }}</div>
        <div class="summary-value">{{ item.value }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import http from "../utils/http";

const cards = ref([
  { label: "用户数", value: 0 },
  { label: "商品数", value: 0 },
  { label: "订单数", value: 0 },
  { label: "佣金记录", value: 0 }
]);

async function load() {
  const [users, products, orders, commissions] = await Promise.all([
    http.get("/users/?page=1"),
    http.get("/catalog/products/?page=1"),
    http.get("/orders/?page=1"),
    http.get("/distribution/commissions/?page=1")
  ]);
  cards.value = [
    { label: "用户数", value: users.count || 0 },
    { label: "商品数", value: products.count || 0 },
    { label: "订单数", value: orders.count || 0 },
    { label: "佣金记录", value: commissions.count || 0 }
  ];
}

onMounted(load);
</script>

