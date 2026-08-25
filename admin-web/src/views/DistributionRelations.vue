<template>
  <div class="page-shell">
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="page-title">分销关系</div>
        <el-input
          v-model="search"
          clearable
          placeholder="搜索用户/手机号"
          style="width: 220px"
          @keyup.enter="load"
        />
      </div>
      <el-button :loading="loading" @click="load">查询</el-button>
    </div>

    <div class="page-card">
      <el-table v-loading="loading" :data="rows" border stripe>
        <el-table-column prop="id" label="用户ID" width="90" />
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="name">{{ displayName(row) }}</span>
              <span class="sub">账号：{{ row.username || "-" }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="mobile" label="手机号" min-width="140" />
        <el-table-column label="上级用户" min-width="180">
          <template #default="{ row }">
            <div v-if="row.parent" class="user-cell">
              <span class="name">{{ row.parent_display || `ID ${row.parent}` }}</span>
              <span class="sub">{{ row.parent_mobile || "未填写手机号" }}</span>
            </div>
            <el-tag v-else type="info" effect="light">无上级</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关系链" min-width="280">
          <template #default="{ row }">
            <div v-if="row.relation_chain?.length" class="chain">
              <template v-for="(item, index) in row.relation_chain" :key="item.id">
                <el-tag :type="index === row.relation_chain.length - 1 ? 'success' : 'info'" effect="light">
                  {{ item.label }}
                </el-tag>
                <span v-if="index < row.relation_chain.length - 1" class="chain-arrow">></span>
              </template>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="团队人数" width="150">
          <template #default="{ row }">
            <div class="stats-cell">
              <span>直属 {{ row.direct_count || 0 }}</span>
              <span>全部 {{ row.team_count || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分销商" width="100">
          <template #default="{ row }"><StatusTag :value="row.is_distributor" /></template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openTree(row)">查看团队</el-button>
            <el-button link type="primary" @click="openBind(row)">绑定上级</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="visible" title="绑定分销上级" width="460px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="当前用户">
          <el-input :model-value="form.user_label" disabled />
        </el-form-item>
        <el-form-item label="上级ID">
          <el-input v-model="form.parent_id" placeholder="请输入上级用户ID" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">保存</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="treeVisible" :title="treeTitle" size="560px" class="relation-tree-drawer">
      <el-empty v-if="!teamTree" description="暂无团队数据" />
      <el-tree
        v-else
        class="relation-tree"
        :data="[teamTree]"
        :props="treeProps"
        node-key="id"
        :indent="28"
        default-expand-all
      >
        <template #default="{ data }">
          <div class="tree-node">
            <div>
              <span class="tree-name">{{ data.label }}</span>
              <span class="tree-sub">ID {{ data.id }} · {{ data.mobile || "未填写手机号" }}</span>
            </div>
            <el-tag size="small" effect="light">{{ roleLabel(data.role) }}</el-tag>
          </div>
        </template>
      </el-tree>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import StatusTag from "../components/StatusTag.vue";
import http from "../utils/http";

const roleMap = {
  normal: "普通用户",
  member: "会员",
  distributor: "分销商",
  team_leader: "团队长",
  city_agent: "城市代理",
  admin: "平台管理员"
};

const search = ref("");
const rows = ref([]);
const loading = ref(false);
const saving = ref(false);
const visible = ref(false);
const treeVisible = ref(false);
const teamTree = ref(null);
const treeTitle = ref("团队关系");
const treeProps = { label: "label", children: "children" };
const form = reactive({ user_id: null, user_label: "", parent_id: "" });

function displayName(row) {
  return row.nickname || row.username || `用户${row.id}`;
}

function roleLabel(role) {
  return roleMap[role] || role || "-";
}

async function load() {
  loading.value = true;
  try {
    const params = new URLSearchParams({ page: "1" });
    if (search.value) params.set("search", search.value);
    const data = await http.get(`/users/?${params.toString()}`);
    rows.value = data.results || [];
  } finally {
    loading.value = false;
  }
}

function openBind(row) {
  form.user_id = row.id;
  form.user_label = `${displayName(row)}（ID ${row.id}）`;
  form.parent_id = row.parent || "";
  visible.value = true;
}

async function submit() {
  if (!form.parent_id) {
    ElMessage.warning("请填写上级用户ID");
    return;
  }
  saving.value = true;
  try {
    await http.post("/distribution/configs/bind-parent/", {
      user_id: Number(form.user_id),
      parent_id: Number(form.parent_id)
    });
    ElMessage.success("分销关系已更新");
    visible.value = false;
    await load();
  } finally {
    saving.value = false;
  }
}

async function openTree(row) {
  treeTitle.value = `${displayName(row)} 的团队关系`;
  teamTree.value = null;
  treeVisible.value = true;
  teamTree.value = await http.get(`/distribution/team-stats/tree/?user_id=${row.id}`);
}

onMounted(load);
</script>

<style scoped>
.user-cell {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 2px;
}

.name {
  color: #1f2937;
  font-weight: 600;
}

.sub {
  color: #8a95a6;
  font-size: 12px;
}

.chain {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.chain-arrow {
  color: #94a3b8;
  font-size: 12px;
}

.stats-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #4b5563;
  font-size: 13px;
}

.tree-node {
  display: flex;
  width: 100%;
  min-width: 0;
  min-height: 44px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-right: 8px;
}

.tree-node > div {
  min-width: 0;
}

.tree-name {
  display: block;
  color: #1f2937;
  font-weight: 600;
  line-height: 1.4;
}

.tree-sub {
  display: block;
  color: #8a95a6;
  font-size: 12px;
  line-height: 1.4;
}

.relation-tree {
  padding: 4px 2px 16px;
  background: transparent;
}

.relation-tree :deep(.el-tree-node__content) {
  height: auto;
  min-height: 56px;
  align-items: center;
  margin: 4px 0;
  padding: 6px 8px;
  border-radius: 8px;
}

.relation-tree :deep(.el-tree-node__content:hover) {
  background: #f5f7fb;
}

.relation-tree :deep(.el-tree-node__expand-icon) {
  flex: 0 0 auto;
  color: #94a3b8;
}

.relation-tree :deep(.el-tree-node__label) {
  flex: 1;
  min-width: 0;
}

.relation-tree :deep(.el-tree-node__children) {
  border-left: 1px dashed #d8e0eb;
  margin-left: 12px;
  padding-left: 8px;
}

:deep(.relation-tree-drawer .el-drawer__header) {
  margin-bottom: 8px;
  padding: 24px 28px 12px;
  color: #1f2937;
  font-size: 18px;
  font-weight: 700;
}

:deep(.relation-tree-drawer .el-drawer__body) {
  padding: 8px 28px 28px;
}
</style>
