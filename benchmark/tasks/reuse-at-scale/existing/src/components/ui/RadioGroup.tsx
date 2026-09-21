type RadioGroupProps = { className?: string; children?: React.ReactNode };
export function RadioGroup({ className, children }: RadioGroupProps) {
  return <div className={className} data-component="RadioGroup">{children}</div>;
}
