type InlineErrorProps = { className?: string; children?: React.ReactNode };
export function InlineError({ className, children }: InlineErrorProps) {
  return <div className={className} data-component="InlineError">{children}</div>;
}
