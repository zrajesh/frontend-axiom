type SpinnerProps = { className?: string; children?: React.ReactNode };
export function Spinner({ className, children }: SpinnerProps) {
  return <div className={className} data-component="Spinner">{children}</div>;
}
