import { get, post } from "../common/request";

export function getTeamStats() {
  return get("/distribution/team-stats/");
}

export function getTeamTree() {
  return get("/distribution/team-stats/tree/");
}

export function getCommissions(params = {}) {
  return get("/distribution/commissions/", params);
}

export function bindMineParent(parentId) {
  return post("/distribution/configs/bind-mine/", { parent_id: parentId });
}

export function getRewardPools() {
  return get("/rewards/pools/");
}

export function getRewardRecords(params = {}) {
  return get("/rewards/records/", params);
}

export function getAgentApplications() {
  return get("/agents/applications/");
}

export function getMyAgents() {
  return get("/agents/");
}

export function applyAgent(data) {
  return post("/agents/applications/", data);
}

export function getWallet() {
  return get("/finance/wallets/mine/");
}

export function getFlows() {
  return get("/finance/flows/");
}

export function applyWithdraw(data) {
  return post("/finance/withdrawals/", data);
}

export function getWithdrawals(params = {}) {
  return get("/finance/withdrawals/", params);
}

export function submitRealname(data) {
  return post("/users/submit-realname/", data);
}
