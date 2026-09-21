type BadgeProps = { className?: string; children?: React.ReactNode };
export function Badge({ className, children }: BadgeProps) {
  return <div className={className} data-component="Badge">{children}</div>;
}
