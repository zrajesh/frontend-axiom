type ProgressBarProps = { className?: string; children?: React.ReactNode };
export function ProgressBar({ className, children }: ProgressBarProps) {
  return <div className={className} data-component="ProgressBar">{children}</div>;
}
