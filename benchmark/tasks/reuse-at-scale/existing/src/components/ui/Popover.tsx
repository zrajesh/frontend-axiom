type PopoverProps = { className?: string; children?: React.ReactNode };
export function Popover({ className, children }: PopoverProps) {
  return <div className={className} data-component="Popover">{children}</div>;
}
