type TableProps = { className?: string; children?: React.ReactNode };
export function Table({ className, children }: TableProps) {
  return <div className={className} data-component="Table">{children}</div>;
}
