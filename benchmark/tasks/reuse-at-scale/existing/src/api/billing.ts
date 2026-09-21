export async function getInvoices() { return fetch('/invoices').then(r => r.json()); }
