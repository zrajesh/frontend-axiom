export async function getProfile() { return fetch('/profile').then(r => r.json()); }
