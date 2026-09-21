type BannerProps = { className?: string; children?: React.ReactNode };
export function Banner({ className, children }: BannerProps) {
  return <div className={className} data-component="Banner">{children}</div>;
}
