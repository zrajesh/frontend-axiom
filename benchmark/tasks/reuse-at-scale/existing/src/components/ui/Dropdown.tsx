type DropdownProps = { className?: string; children?: React.ReactNode };
export function Dropdown({ className, children }: DropdownProps) {
  return <div className={className} data-component="Dropdown">{children}</div>;
}
