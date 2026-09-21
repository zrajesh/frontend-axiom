type CheckboxProps = { className?: string; children?: React.ReactNode };
export function Checkbox({ className, children }: CheckboxProps) {
  return <div className={className} data-component="Checkbox">{children}</div>;
}
