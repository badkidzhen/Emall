import { REFRESH_TOKEN_KEY, TOKEN_KEY } from "./config";

export function setTokens(access, refresh) {
  uni.setStorageSync(TOKEN_KEY, access);
  uni.setStorageSync(REFRESH_TOKEN_KEY, refresh);
}

export function clearTokens() {
  uni.removeStorageSync(TOKEN_KEY);
  uni.removeStorageSync(REFRESH_TOKEN_KEY);
}

export function isLoggedIn() {
  return Boolean(uni.getStorageSync(TOKEN_KEY));
}

