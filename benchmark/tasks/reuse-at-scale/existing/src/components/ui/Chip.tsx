type ChipProps = { className?: string; children?: React.ReactNode };
export function Chip({ className, children }: ChipProps) {
  return <div className={className} data-component="Chip">{children}</div>;
}
