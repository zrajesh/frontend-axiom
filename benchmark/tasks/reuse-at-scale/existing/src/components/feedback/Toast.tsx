type ToastProps = { className?: string; children?: React.ReactNode };
export function Toast({ className, children }: ToastProps) {
  return <div className={className} data-component="Toast">{children}</div>;
}
