type SelectProps = { className?: string; children?: React.ReactNode };
export function Select({ className, children }: SelectProps) {
  return <div className={className} data-component="Select">{children}</div>;
}
