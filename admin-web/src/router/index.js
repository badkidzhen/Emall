import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";
import Login from "../views/Login.vue";
import AdminLayout from "../layouts/AdminLayout.vue";
import Dashboard from "../views/Dashboard.vue";
import Users from "../views/Users.vue";
import Categories from "../views/Categories.vue";
import Products from "../views/Products.vue";
import Orders from "../views/Orders.vue";
import Refunds from "../views/Refunds.vue";
import Invoices from "../views/Invoices.vue";
import Marketing from "../views/Marketing.vue";
import Realname from "../views/Realname.vue";
import Agents from "../views/Agents.vue";
import Rewards from "../views/Rewards.vue";
import Finance from "../views/Finance.vue";
import ReportPage from "../views/ReportPage.vue";
import ProductSkus from "../views/ProductSkus.vue";
import SpecTemplates from "../views/SpecTemplates.vue";
import StockLogs from "../views/StockLogs.vue";
import MemberLevels from "../views/MemberLevels.vue";
import DistributionRelations from "../views/DistributionRelations.vue";
import DistributionConfig from "../views/DistributionConfig.vue";
import CommissionRecords from "../views/CommissionRecords.vue";
import TeamStats from "../views/TeamStats.vue";
import DistributionStats from "../views/DistributionStats.vue";
import AgentPerformance from "../views/AgentPerformance.vue";
import AgentCommissions from "../views/AgentCommissions.vue";
import RewardSimulator from "../views/RewardSimulator.vue";
import FinanceSummary from "../views/FinanceSummary.vue";
import TaxReports from "../views/TaxReports.vue";
import SystemAdmins from "../views/SystemAdmins.vue";
import SystemRoles from "../views/SystemRoles.vue";
import SystemMenus from "../views/SystemMenus.vue";
import SystemLogs from "../views/SystemLogs.vue";

function page(path, component, title, meta = {}) {
  return { path, component, meta: { title, ...meta } };
}

const routes = [
  { path: "/login", component: Login },
  {
    path: "/",
    component: AdminLayout,
    redirect: "/dashboard",
    children: [
      page("dashboard", Dashboard, "数据看板"),
      page("reports/users", ReportPage, "用户趋势"),
      page("reports/sales", ReportPage, "销售报表"),
      page("reports/commissions", ReportPage, "佣金报表"),
      page("reports/marketing", ReportPage, "营销数据"),

      page("products", Products, "商品列表"),
      page("categories", Categories, "商品分类"),
      page("products/skus", ProductSkus, "SKU 管理"),
      page("products/spec-templates", SpecTemplates, "规格模板"),
      page("products/stocks", StockLogs, "库存管理"),

      page("orders", Orders, "订单列表"),
      page("orders/aftersales", Refunds, "售后管理"),
      page("refunds", Refunds, "退款管理"),
      page("invoices", Invoices, "发票管理"),
      page("orders/statistics", ReportPage, "订单统计"),

      page("users", Users, "用户列表"),
      page("users/levels", MemberLevels, "会员等级"),
      page("realname", Realname, "实名认证审核"),
      page("users/distribution-relations", DistributionRelations, "分销关系"),

      page("distribution/config", DistributionConfig, "分销配置"),
      page("distribution/commissions", CommissionRecords, "佣金明细"),
      page("distribution/teams", TeamStats, "团队管理"),
      page("distribution/statistics", DistributionStats, "分销统计"),

      page("agents/applications", Agents, "代理申请审核", { agentTab: "applications" }),
      page("agents", Agents, "代理列表", { agentTab: "agents" }),
      page("agents/performance", AgentPerformance, "区域业绩"),
      page("agents/commissions", AgentCommissions, "代理佣金"),

      page("rewards", Rewards, "池子管理", { rewardTab: "pools" }),
      page("rewards/rules", Rewards, "权重配置", { rewardTab: "rules" }),
      page("rewards/records", Rewards, "分配记录", { rewardTab: "records" }),
      page("rewards/simulator", RewardSimulator, "模拟测算"),

      page("marketing", Marketing, "营销管理"),
      page("marketing/coupons", Marketing, "优惠券模板", { marketingTab: "coupon" }),
      page("marketing/groups", Marketing, "团购活动", { marketingTab: "group" }),
      page("marketing/seckills", Marketing, "秒杀活动", { marketingTab: "seckill" }),

      page("finance", Finance, "财务管理"),
      page("finance/withdrawals", Finance, "提现审核", { financeTab: "withdrawals" }),
      page("finance/flows", Finance, "资金流水", { financeTab: "flows" }),
      page("finance/income-expense", FinanceSummary, "平台收支"),
      page("finance/tax-reports", TaxReports, "税务报表"),

      page("system/admins", SystemAdmins, "管理员管理"),
      page("system/roles", SystemRoles, "角色管理"),
      page("system/menus", SystemMenus, "菜单管理"),
      page("system/logs", SystemLogs, "操作日志")
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.path !== "/login" && !auth.accessToken) {
    return "/login";
  }
  if (to.path === "/login" && auth.accessToken) {
    return "/dashboard";
  }
});

export default router;
