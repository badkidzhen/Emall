<template>
  <view class="page">
    <view class="hero-card">
      <view>
        <view class="title light">{{ rootLabel }}</view>
        <view class="subtle light">以我为根节点查看团队层级</view>
      </view>
      <view class="hero-count">
        <view class="count">{{ totalCount }}</view>
        <view class="count-label">团队成员</view>
      </view>
    </view>

    <view v-if="root.id" class="tree-card section">
      <view class="tree-toolbar">
        <view>
          <view class="tree-title">团队树</view>
          <view class="tree-sub">点击成员可展开或收起下级</view>
        </view>
        <view class="toggle-all" @tap.stop="handleToggleAll">{{ allExpanded ? "全部收起" : "全部展开" }}</view>
      </view>

      <view
        v-for="node in visibleNodes"
        :key="node.id"
        class="tree-row"
        :class="{ root: node.level === 0 }"
        :style="{ marginLeft: node.indent }"
        @tap="handleToggleNode(node.id)"
      >
        <view class="line" v-if="node.level > 0"></view>
        <view class="node-main">
          <view class="node-left">
            <view class="expand-icon" :class="{ placeholder: !node.hasChildren }">
              <text v-if="node.hasChildren">{{ node.expanded ? "-" : "+" }}</text>
            </view>
            <view class="avatar">{{ node.avatar }}</view>
            <view class="node-info">
              <view class="node-name">
                {{ node.name }}
                <text v-if="node.level === 0" class="me-tag">我</text>
              </view>
              <view class="node-meta">ID {{ node.id }} · {{ node.mobile || "未填写手机号" }}</view>
            </view>
          </view>
          <view class="role-tag">{{ node.roleText }}</view>
        </view>
      </view>
    </view>

    <empty-state v-if="!loading && root.id && !totalCount" title="暂无团队成员" />
    <empty-state v-if="!loading && !root.id" title="请先登录后查看团队" />
  </view>
</template>

<script>
import { getTeamTree } from "../../api/user";

const roleMap = {
  normal: "普通用户",
  member: "会员",
  distributor: "分销商",
  team_leader: "团队长",
  city_agent: "城市代理",
  admin: "管理员"
};

export default {
  data() {
    return {
      root: {},
      expandedMap: {},
      visibleNodes: [],
      loading: false
    };
  },
  computed: {
    rootLabel() {
      return this.displayName(this.root) || "我的团队";
    },
    totalCount() {
      return this.countChildren(this.root);
    },
    allExpanded() {
      const ids = [];
      this.collectExpandableIds(this.root, ids);
      if (!ids.length) return false;
      return ids.every((id) => this.expandedMap[id]);
    }
  },
  onShow() {
    this.load();
  },
  methods: {
    async load() {
      this.loading = true;
      try {
        const data = await getTeamTree();
        this.root = data || {};
        this.expandedMap = {};
        this.expandAll(this.root);
        this.refreshVisibleNodes();
      } finally {
        this.loading = false;
      }
    },
    displayName(node) {
      if (!node) return "";
      return node.label || node.nickname || node.username || `用户${node.id}`;
    },
    avatarText(node) {
      const name = this.displayName(node);
      return name ? name.slice(0, 1) : "团";
    },
    roleLabel(role) {
      return roleMap[role] || role || "-";
    },
    hasChildren(node) {
      return !!(node && node.children && node.children.length);
    },
    refreshVisibleNodes() {
      const nodes = [];
      this.collectVisibleNodes(this.root, 0, nodes);
      this.visibleNodes = nodes;
    },
    collectVisibleNodes(node, level, nodes) {
      if (!node || !node.id) return;
      const hasChildren = this.hasChildren(node);
      const expanded = !!this.expandedMap[node.id];
      nodes.push({
        id: node.id,
        username: node.username,
        nickname: node.nickname,
        label: node.label,
        mobile: node.mobile,
        role: node.role,
        level,
        indent: `${level * 34}rpx`,
        hasChildren,
        expanded,
        avatar: this.avatarText(node),
        name: this.displayName(node),
        roleText: this.roleLabel(node.role)
      });
      if (hasChildren && expanded) {
        node.children.forEach((child) => this.collectVisibleNodes(child, level + 1, nodes));
      }
    },
    collectExpandableIds(node, ids) {
      if (!node || !node.id) return;
      if (this.hasChildren(node)) ids.push(node.id);
      (node.children || []).forEach((child) => this.collectExpandableIds(child, ids));
    },
    countChildren(node) {
      if (!node || !node.children) return 0;
      return node.children.reduce((total, child) => total + 1 + this.countChildren(child), 0);
    },
    expandAll(node) {
      if (!node || !node.id) return;
      if (this.hasChildren(node)) {
        this.$set(this.expandedMap, node.id, true);
      }
      (node.children || []).forEach((child) => this.expandAll(child));
    },
    collapseAll(node) {
      if (!node || !node.id) return;
      if (this.hasChildren(node)) {
        this.$set(this.expandedMap, node.id, false);
      }
      (node.children || []).forEach((child) => this.collapseAll(child));
    },
    handleToggleAll() {
      if (this.allExpanded) {
        this.collapseAll(this.root);
      } else {
        this.expandAll(this.root);
      }
      this.refreshVisibleNodes();
    },
    handleToggleNode(nodeId) {
      const node = this.findNode(this.root, nodeId);
      if (!this.hasChildren(node)) return;
      this.$set(this.expandedMap, nodeId, !this.expandedMap[nodeId]);
      this.refreshVisibleNodes();
    },
    findNode(node, nodeId) {
      if (!node || !node.id) return null;
      if (node.id === nodeId) return node;
      const children = node.children || [];
      for (let index = 0; index < children.length; index += 1) {
        const found = this.findNode(children[index], nodeId);
        if (found) return found;
      }
      return null;
    }
  }
};
</script>

<style scoped>
.hero-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
  min-height: 132rpx;
  padding: 32rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #ff2442, #ff7a45);
  color: #ffffff;
}

.light {
  color: #ffffff;
}

.hero-count {
  flex: 0 0 128rpx;
  padding: 16rpx 0;
  border-radius: 14rpx;
  background: rgba(255, 255, 255, 0.18);
  text-align: center;
}

.count {
  font-size: 38rpx;
  font-weight: 700;
  line-height: 1.1;
}

.count-label {
  margin-top: 8rpx;
  font-size: 22rpx;
  opacity: 0.88;
}

.tree-card {
  padding: 24rpx;
  border-radius: 16rpx;
  background: #ffffff;
}

.tree-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 18rpx;
}

.tree-title {
  color: #111827;
  font-size: 32rpx;
  font-weight: 700;
}

.tree-sub {
  margin-top: 6rpx;
  color: #8a95a6;
  font-size: 24rpx;
}

.toggle-all {
  flex: 0 0 auto;
  padding: 12rpx 20rpx;
  border-radius: 999rpx;
  background: #f3f6fb;
  color: #2563eb;
  font-size: 24rpx;
}

.tree-row {
  position: relative;
  padding: 8rpx 0;
}

.tree-row.root {
  margin-left: 0 !important;
}

.line {
  position: absolute;
  left: -18rpx;
  top: 0;
  bottom: 0;
  width: 1px;
  border-left: 1px dashed #d8e0eb;
}

.node-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  min-height: 88rpx;
  padding: 16rpx;
  border: 1px solid #edf1f7;
  border-radius: 14rpx;
  background: #ffffff;
}

.tree-row.root .node-main {
  border-color: #ffd6dd;
  background: #fff6f8;
}

.node-left {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 14rpx;
}

.expand-icon {
  display: flex;
  flex: 0 0 42rpx;
  width: 42rpx;
  height: 42rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #eef4ff;
  color: #2563eb;
  font-size: 30rpx;
  font-weight: 700;
}

.expand-icon.placeholder {
  background: transparent;
}

.avatar {
  display: flex;
  flex: 0 0 56rpx;
  width: 56rpx;
  height: 56rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #111827;
  color: #ffffff;
  font-size: 26rpx;
  font-weight: 700;
}

.node-info {
  min-width: 0;
}

.node-name {
  overflow: hidden;
  color: #1f2937;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-meta {
  overflow: hidden;
  margin-top: 6rpx;
  color: #8a95a6;
  font-size: 22rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.me-tag {
  margin-left: 10rpx;
  padding: 2rpx 10rpx;
  border-radius: 999rpx;
  background: #ff2442;
  color: #ffffff;
  font-size: 20rpx;
  font-weight: 500;
}

.role-tag {
  flex: 0 0 auto;
  max-width: 136rpx;
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #eef4ff;
  color: #2563eb;
  font-size: 22rpx;
  line-height: 1.2;
}
</style>

