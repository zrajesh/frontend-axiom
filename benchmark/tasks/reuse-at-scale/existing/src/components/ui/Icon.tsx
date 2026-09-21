type IconProps = { className?: string; children?: React.ReactNode };
export function Icon({ className, children }: IconProps) {
  return <div className={className} data-component="Icon">{children}</div>;
}
