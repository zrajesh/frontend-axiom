type InputProps = { className?: string; children?: React.ReactNode };
export function Input({ className, children }: InputProps) {
  return <div className={className} data-component="Input">{children}</div>;
}
