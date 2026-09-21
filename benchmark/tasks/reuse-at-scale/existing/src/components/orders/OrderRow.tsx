type OrderRowProps = { className?: string; children?: React.ReactNode };
export function OrderRow({ className, children }: OrderRowProps) {
  return <div className={className} data-component="OrderRow">{children}</div>;
}
