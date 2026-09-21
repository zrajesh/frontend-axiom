export async function upload(f: File) { return fetch('/uploads', { method: 'POST', body: f }); }
