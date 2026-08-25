import http from "./http";

export async function uploadImage(file) {
  const data = new FormData();
  data.append("file", file);
  return http.post("/uploads/images/", data);
}
