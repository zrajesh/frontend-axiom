type OrderTimelineProps = { className?: string; children?: React.ReactNode };
export function OrderTimeline({ className, children }: OrderTimelineProps) {
  return <div className={className} data-component="OrderTimeline">{children}</div>;
}
