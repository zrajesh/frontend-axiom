type LabelProps = { className?: string; children?: React.ReactNode };
export function Label({ className, children }: LabelProps) {
  return <div className={className} data-component="Label">{children}</div>;
}
