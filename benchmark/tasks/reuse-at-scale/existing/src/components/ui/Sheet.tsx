type SheetProps = { className?: string; children?: React.ReactNode };
export function Sheet({ className, children }: SheetProps) {
  return <div className={className} data-component="Sheet">{children}</div>;
}
