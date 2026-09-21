type CalloutProps = { className?: string; children?: React.ReactNode };
export function Callout({ className, children }: CalloutProps) {
  return <div className={className} data-component="Callout">{children}</div>;
}
