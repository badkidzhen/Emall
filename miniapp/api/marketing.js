import { get, post } from "../common/request";

export function getCouponTemplates(params = {}) {
  return get("/marketing/coupon-templates/", params);
}

export function claimCoupon(id) {
  return post(`/marketing/coupon-templates/${id}/claim/`, {});
}

export function getMyCoupons(params = {}) {
  return get("/marketing/user-coupons/", params);
}

export function getGroups() {
  return get("/marketing/groups/");
}

export function purchaseGroup(id, quantity) {
  return post(`/marketing/groups/${id}/purchase/`, { quantity });
}

export function getSeckills() {
  return get("/marketing/seckills/");
}

export function purchaseSeckill(id, quantity) {
  return post(`/marketing/seckills/${id}/purchase/`, { quantity });
}

