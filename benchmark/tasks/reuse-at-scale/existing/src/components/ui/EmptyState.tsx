type EmptyStateProps = { className?: string; children?: React.ReactNode };
export function EmptyState({ className, children }: EmptyStateProps) {
  return <div className={className} data-component="EmptyState">{children}</div>;
}
