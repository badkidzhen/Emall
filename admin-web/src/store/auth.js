import { defineStore } from "pinia";

const ACCESS_KEY = "emall_admin_access";
const REFRESH_KEY = "emall_admin_refresh";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: localStorage.getItem(ACCESS_KEY) || "",
    refreshToken: localStorage.getItem(REFRESH_KEY) || "",
    user: null
  }),
  actions: {
    init() {
      this.accessToken = localStorage.getItem(ACCESS_KEY) || "";
      this.refreshToken = localStorage.getItem(REFRESH_KEY) || "";
    },
    setTokens(access, refresh) {
      this.accessToken = access;
      this.refreshToken = refresh;
      localStorage.setItem(ACCESS_KEY, access);
      localStorage.setItem(REFRESH_KEY, refresh);
    },
    setUser(user) {
      this.user = user;
    },
    logout() {
      this.accessToken = "";
      this.refreshToken = "";
      this.user = null;
      localStorage.removeItem(ACCESS_KEY);
      localStorage.removeItem(REFRESH_KEY);
    }
  }
});

