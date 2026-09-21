type DividerProps = { className?: string; children?: React.ReactNode };
export function Divider({ className, children }: DividerProps) {
  return <div className={className} data-component="Divider">{children}</div>;
}
