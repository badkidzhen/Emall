import { post, get } from "../common/request";

export function login(username, password) {
  return post("/auth/token/", { username, password });
}

export function getMe() {
  return get("/users/me/");
}

