import { API_BASE_URL, TOKEN_KEY } from "./config";

export function request(options) {
  const token = uni.getStorageSync(TOKEN_KEY);
  const fullUrl = `${API_BASE_URL}${options.url}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.header || {})
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: fullUrl,
      method: options.method || "GET",
      data: options.data || {},
      header: headers,
      timeout: options.timeout || 15000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        if (res.statusCode === 401) {
          uni.navigateTo({ url: "/pages/user/login" });
        }
        const message = (res.data && (res.data.detail || res.data.message)) || "请求失败";
        console.error("request failed", {
          url: fullUrl,
          statusCode: res.statusCode,
          data: res.data
        });
        uni.showToast({ title: message, icon: "none" });
        reject(res);
      },
      fail: (err) => {
        const isTimeout = String(err.errMsg || "").includes("timeout");
        console.error("request failed", {
          url: fullUrl,
          method: options.method || "GET",
          error: err
        });
        uni.showToast({
          title: isTimeout ? `请求超时: ${options.url}` : `网络异常: ${err.errMsg || "request fail"}`,
          icon: "none"
        });
        reject(err);
      }
    });
  });
}

export function get(url, data) {
  return request({ url, data, method: "GET" });
}

export function post(url, data) {
  return request({ url, data, method: "POST" });
}

export function put(url, data) {
  return request({ url, data, method: "PUT" });
}

export function patch(url, data) {
  return request({ url, data, method: "PATCH" });
}

export function del(url, data) {
  return request({ url, data, method: "DELETE" });
}
