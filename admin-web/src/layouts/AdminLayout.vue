<template>
  <el-container class="layout">
    <el-aside class="aside" width="220px">
      <div class="logo">
        <div class="logo-title">Emall</div>
        <div class="muted">管理后台</div>
      </div>
      <el-menu
        :default-active="route.path"
        :default-openeds="defaultOpeneds"
        router
        unique-opened
        class="menu"
        background-color="#111827"
        text-color="#cbd5e1"
        active-text-color="#ffffff"
      >
        <el-sub-menu v-for="section in menuSections" :key="section.id" :index="section.id">
          <template #title>
            <el-icon><component :is="section.icon" /></el-icon>
            <span>{{ section.title }}</span>
          </template>
          <el-menu-item v-for="item in section.children" :key="item.index" :index="item.index">
            <span class="menu-dot" />
            <span>{{ item.title }}</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container class="content-layout">
      <el-header class="header">
        <div>
          <div class="header-title">{{ currentTitle }}</div>
          <div class="muted">分销商城运营后台</div>
        </div>
        <div class="header-actions">
          <span class="muted">{{ auth.user?.username || "admin" }}</span>
          <el-button size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  DataAnalysis,
  Goods,
  Tickets,
  User,
  Share,
  Location,
  Trophy,
  Present,
  Wallet,
  Lock
} from "@element-plus/icons-vue";
import { useAuthStore } from "../store/auth";
import http from "../utils/http";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const iconMap = { DataAnalysis, Goods, Tickets, User, Share, Location, Trophy, Present, Wallet, Lock };

const defaultMenuSections = [
  {
    id: "data-center",
    title: "数据中心",
    icon: DataAnalysis,
    children: [
      { title: "数据看板", index: "/dashboard" },
      { title: "用户趋势", index: "/reports/users" },
      { title: "销售报表", index: "/reports/sales" },
      { title: "佣金报表", index: "/reports/commissions" },
      { title: "营销数据", index: "/reports/marketing" }
    ]
  },
  {
    id: "product-center",
    title: "商品中心",
    icon: Goods,
    children: [
      { title: "商品列表", index: "/products" },
      { title: "商品分类", index: "/categories" },
      { title: "SKU 管理", index: "/products/skus" },
      { title: "规格模板", index: "/products/spec-templates" },
      { title: "库存管理", index: "/products/stocks" }
    ]
  },
  {
    id: "order-service",
    title: "订单售后",
    icon: Tickets,
    children: [
      { title: "订单列表", index: "/orders" },
      { title: "售后管理", index: "/orders/aftersales" },
      { title: "退款管理", index: "/refunds" },
      { title: "发票管理", index: "/invoices" },
      { title: "订单统计", index: "/orders/statistics" }
    ]
  },
  {
    id: "user-member",
    title: "用户会员",
    icon: User,
    children: [
      { title: "用户列表", index: "/users" },
      { title: "会员等级", index: "/users/levels" },
      { title: "实名认证审核", index: "/realname" },
      { title: "分销关系", index: "/users/distribution-relations" }
    ]
  },
  {
    id: "distribution-team",
    title: "分销团队",
    icon: Share,
    children: [
      { title: "分销配置", index: "/distribution/config" },
      { title: "佣金明细", index: "/distribution/commissions" },
      { title: "团队管理", index: "/distribution/teams" },
      { title: "分销统计", index: "/distribution/statistics" }
    ]
  },
  {
    id: "city-agent",
    title: "城市代理",
    icon: Location,
    children: [
      { title: "代理申请审核", index: "/agents/applications" },
      { title: "代理列表", index: "/agents" },
      { title: "区域业绩", index: "/agents/performance" },
      { title: "代理佣金", index: "/agents/commissions" }
    ]
  },
  {
    id: "reward-pool",
    title: "奖金池",
    icon: Trophy,
    children: [
      { title: "池子管理", index: "/rewards" },
      { title: "权重配置", index: "/rewards/rules" },
      { title: "分配记录", index: "/rewards/records" },
      { title: "模拟测算", index: "/rewards/simulator" }
    ]
  },
  {
    id: "marketing-center",
    title: "营销中心",
    icon: Present,
    children: [
      { title: "优惠券模板", index: "/marketing/coupons" },
      { title: "团购活动", index: "/marketing/groups" },
      { title: "秒杀活动", index: "/marketing/seckills" }
    ]
  },
  {
    id: "finance-settlement",
    title: "财务结算",
    icon: Wallet,
    children: [
      { title: "提现审核", index: "/finance/withdrawals" },
      { title: "资金流水", index: "/finance/flows" },
      { title: "平台收支", index: "/finance/income-expense" },
      { title: "税务报表", index: "/finance/tax-reports" }
    ]
  },
  {
    id: "permission-system",
    title: "权限系统",
    icon: Lock,
    children: [
      { title: "管理员管理", index: "/system/admins" },
      { title: "角色管理", index: "/system/roles" },
      { title: "菜单管理", index: "/system/menus" },
      { title: "操作日志", index: "/system/logs" }
    ]
  }
];

const menuSections = ref(defaultMenuSections);

const flatMenu = computed(() =>
  menuSections.value.flatMap((section) =>
    section.children.map((item) => ({ ...item, sectionId: section.id }))
  )
);

const defaultOpeneds = computed(() => {
  const current = flatMenu.value.find((item) => item.index === route.path);
  return current ? [current.sectionId] : ["data-center"];
});

const currentTitle = computed(() => {
  const current = flatMenu.value.find((item) => item.index === route.path);
  return current?.title || "数据看板";
});

function normalizeMenuSections(rows) {
  return (rows || [])
    .filter((section) => section.is_show !== false)
    .map((section) => ({
      id: section.code || String(section.id),
      title: section.name || section.title,
      icon: iconMap[section.icon] || iconMap.DataAnalysis,
      children: (section.children || [])
        .filter((item) => item.is_show !== false && item.path)
        .map((item) => ({
          title: item.name || item.title,
          index: item.path
        }))
    }))
    .filter((section) => section.children.length);
}

async function loadMenus() {
  try {
    const data = await http.get("/system/menus/");
    const normalized = normalizeMenuSections(data);
    if (normalized.length) menuSections.value = normalized;
  } catch (error) {
    menuSections.value = defaultMenuSections;
  }
}

function logout() {
  auth.logout();
  router.push("/login");
}

onMounted(loadMenus);
</script>

<style scoped>
.layout {
  height: 100vh;
  overflow: hidden;
}

.aside {
  height: 100vh;
  overflow: hidden;
  background: #111827;
}

.logo {
  height: 72px;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-title {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
}

.menu {
  height: calc(100vh - 72px);
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  border-right: 0;
  padding: 8px 10px 16px;
}

.menu::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.menu :deep(.el-sub-menu__title),
.menu :deep(.el-menu-item) {
  height: 42px;
  line-height: 42px;
  border-radius: 8px;
}

.menu :deep(.el-sub-menu__title) {
  margin: 2px 0;
  font-weight: 600;
}

.menu :deep(.el-menu-item) {
  min-width: 0;
  margin: 2px 0;
  padding-left: 42px !important;
}

.menu :deep(.el-sub-menu .el-menu) {
  background: transparent;
}

.menu :deep(.el-menu-item.is-active) {
  background: #ff2442;
}

.menu-dot {
  width: 5px;
  height: 5px;
  margin-right: 10px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.72;
}

.content-layout {
  height: 100vh;
  min-width: 0;
  overflow: hidden;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eef2f7;
  height: 60px;
}

.header-title {
  color: #111827;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.3;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main {
  height: calc(100vh - 60px);
  padding: 0;
  overflow-x: hidden;
  overflow-y: auto;
  background: #f5f7fb;
}
</style>
