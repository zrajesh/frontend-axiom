type AvatarProps = { className?: string; children?: React.ReactNode };
export function Avatar({ className, children }: AvatarProps) {
  return <div className={className} data-component="Avatar">{children}</div>;
}
