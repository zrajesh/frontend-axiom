// The only order-related endpoints that exist.
export async function cancelOrder(orderId: string): Promise<void> {
  await fetch(`/orders/${orderId}/cancel`, { method: "POST", credentials: "include" });
}
export async function getOrder(orderId: string) {
  return fetch(`/orders/${orderId}`, { credentials: "include" }).then((r) => r.json());
}
