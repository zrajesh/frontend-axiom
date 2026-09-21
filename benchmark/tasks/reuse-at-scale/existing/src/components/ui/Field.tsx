type FieldProps = { className?: string; children?: React.ReactNode };
export function Field({ className, children }: FieldProps) {
  return <div className={className} data-component="Field">{children}</div>;
}
