type OrderStatusPillProps = { className?: string; children?: React.ReactNode };
export function OrderStatusPill({ className, children }: OrderStatusPillProps) {
  return <div className={className} data-component="OrderStatusPill">{children}</div>;
}
