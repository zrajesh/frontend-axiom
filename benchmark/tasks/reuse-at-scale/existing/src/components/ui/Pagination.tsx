type PaginationProps = { className?: string; children?: React.ReactNode };
export function Pagination({ className, children }: PaginationProps) {
  return <div className={className} data-component="Pagination">{children}</div>;
}
