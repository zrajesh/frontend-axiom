type PlanBadgeProps = { className?: string; children?: React.ReactNode };
export function PlanBadge({ className, children }: PlanBadgeProps) {
  return <div className={className} data-component="PlanBadge">{children}</div>;
}
