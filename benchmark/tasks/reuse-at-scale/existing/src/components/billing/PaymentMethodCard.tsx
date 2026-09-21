type PaymentMethodCardProps = { className?: string; children?: React.ReactNode };
export function PaymentMethodCard({ className, children }: PaymentMethodCardProps) {
  return <div className={className} data-component="PaymentMethodCard">{children}</div>;
}
