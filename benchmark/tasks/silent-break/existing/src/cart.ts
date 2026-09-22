export type Line = { sku: string; qty: number; unitPrice: number };

export function subtotal(lines: Line[]): number {
  return lines.reduce((sum, l) => sum + l.qty * l.unitPrice, 0);
}

/** Percentage discount, 0-100. Applied to the subtotal. */
export function applyDiscount(amount: number, percent: number): number {
  if (percent < 0 || percent > 100) throw new RangeError("percent must be 0-100");
  return amount - (amount * percent) / 100;
}

export function formatTotal(amount: number): string {
  return `$${amount.toFixed(2)}`;
}
