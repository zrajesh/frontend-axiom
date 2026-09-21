type DrawerProps = { className?: string; children?: React.ReactNode };
export function Drawer({ className, children }: DrawerProps) {
  return <div className={className} data-component="Drawer">{children}</div>;
}
