export async function getNotifications() { return fetch('/notifications').then(r => r.json()); }
