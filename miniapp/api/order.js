import { del, get, patch, post, put } from "../common/request";

export function getCartItems() {
  return get("/orders/cart-items/");
}

export function addCartItem(data) {
  return post("/orders/cart-items/add/", data);
}

export function updateCartItem(id, data) {
  return patch(`/orders/cart-items/${id}/`, data);
}

export function deleteCartItem(id) {
  return del(`/orders/cart-items/${id}/`);
}

export function createOrder(data) {
  return post("/orders/create/", data);
}

export function getOrders(params = {}) {
  return get("/orders/", params);
}

export function getOrder(id) {
  return get(`/orders/${id}/`);
}

export function cancelOrder(id, reason = "") {
  return post(`/orders/${id}/cancel/`, { reason });
}

export function receiveOrder(id) {
  return post(`/orders/${id}/receive/`, {});
}

export function getAddresses() {
  return get("/orders/addresses/");
}

export function createAddress(data) {
  return post("/orders/addresses/", data);
}

export function updateAddress(id, data) {
  return put(`/orders/addresses/${id}/`, data);
}

export function deleteAddress(id) {
  return del(`/orders/addresses/${id}/`);
}

export function createPayment(id, data = {}) {
  return post(`/orders/${id}/create-payment/`, data);
}

export function applyRefund(id, data) {
  return post(`/orders/${id}/apply-refund/`, data);
}

export function getRefunds(params = {}) {
  return get("/orders/refunds/", params);
}

export function applyInvoice(id, data) {
  return post(`/orders/${id}/apply-invoice/`, data);
}

export function getInvoices(params = {}) {
  return get("/orders/invoices/", params);
}
