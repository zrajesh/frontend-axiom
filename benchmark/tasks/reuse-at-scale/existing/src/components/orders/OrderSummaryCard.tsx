type OrderSummaryCardProps = { className?: string; children?: React.ReactNode };
export function OrderSummaryCard({ className, children }: OrderSummaryCardProps) {
  return <div className={className} data-component="OrderSummaryCard">{children}</div>;
}
