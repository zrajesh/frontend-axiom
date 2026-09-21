type CardProps = { className?: string; children?: React.ReactNode };
export function Card({ className, children }: CardProps) {
  return <div className={className} data-component="Card">{children}</div>;
}
