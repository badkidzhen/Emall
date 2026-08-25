import axios from "axios";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../store/auth";

const http = axios.create({
  baseURL: "/api",
  timeout: 15000
});

http.interceptors.request.use((config) => {
  const auth = useAuthStore();
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const auth = useAuthStore();
    const status = error.response?.status;

    if (status === 401 && auth.refreshToken && !error.config._retry) {
      error.config._retry = true;
      try {
        const refresh = await axios.post("/api/auth/token/refresh/", {
          refresh: auth.refreshToken
        });
        auth.setTokens(refresh.data.access, auth.refreshToken);
        error.config.headers.Authorization = `Bearer ${refresh.data.access}`;
        return http(error.config);
      } catch (refreshError) {
        auth.logout();
      }
    }

    const message = normalizeError(error.response?.data) || error.message || "请求失败";
    ElMessage.error(message);
    return Promise.reject(error);
  }
);

function normalizeError(data) {
  if (!data) return "";
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  if (data.message) return data.message;
  if (typeof data === "object") {
    const firstKey = Object.keys(data)[0];
    const value = data[firstKey];
    if (Array.isArray(value)) return `${firstKey}: ${value.join("，")}`;
    if (typeof value === "string") return `${firstKey}: ${value}`;
  }
  return "";
}

export default http;
