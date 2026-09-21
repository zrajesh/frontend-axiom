export async function search(q: string) { return fetch(`/search?q=${q}`).then(r => r.json()); }
