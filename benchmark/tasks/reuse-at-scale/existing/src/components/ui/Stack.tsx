type StackProps = { className?: string; children?: React.ReactNode };
export function Stack({ className, children }: StackProps) {
  return <div className={className} data-component="Stack">{children}</div>;
}
