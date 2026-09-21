type BreadcrumbProps = { className?: string; children?: React.ReactNode };
export function Breadcrumb({ className, children }: BreadcrumbProps) {
  return <div className={className} data-component="Breadcrumb">{children}</div>;
}
