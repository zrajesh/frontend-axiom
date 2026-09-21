export async function getSession() { return fetch('/session').then(r => r.json()); }
