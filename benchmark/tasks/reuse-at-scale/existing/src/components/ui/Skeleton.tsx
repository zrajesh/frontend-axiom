type SkeletonProps = { className?: string; children?: React.ReactNode };
export function Skeleton({ className, children }: SkeletonProps) {
  return <div className={className} data-component="Skeleton">{children}</div>;
}
