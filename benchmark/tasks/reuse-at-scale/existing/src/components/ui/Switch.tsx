type SwitchProps = { className?: string; children?: React.ReactNode };
export function Switch({ className, children }: SwitchProps) {
  return <div className={className} data-component="Switch">{children}</div>;
}
