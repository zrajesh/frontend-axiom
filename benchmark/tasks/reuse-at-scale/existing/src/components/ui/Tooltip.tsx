type TooltipProps = { className?: string; children?: React.ReactNode };
export function Tooltip({ className, children }: TooltipProps) {
  return <div className={className} data-component="Tooltip">{children}</div>;
}
