type TextareaProps = { className?: string; children?: React.ReactNode };
export function Textarea({ className, children }: TextareaProps) {
  return <div className={className} data-component="Textarea">{children}</div>;
}
