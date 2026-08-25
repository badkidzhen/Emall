import { get, post } from "../common/request";

export function getCategoryTree() {
  return get("/catalog/categories/tree/");
}

export function getProducts(params = {}) {
  return get("/catalog/products/", params);
}

export function getProduct(id) {
  return get(`/catalog/products/${id}/`);
}

export function generateSkus(productId, data) {
  return post(`/catalog/products/${productId}/generate-skus/`, data);
}

