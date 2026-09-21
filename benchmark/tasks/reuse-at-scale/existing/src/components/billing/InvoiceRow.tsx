type InvoiceRowProps = { className?: string; children?: React.ReactNode };
export function InvoiceRow({ className, children }: InvoiceRowProps) {
  return <div className={className} data-component="InvoiceRow">{children}</div>;
}
