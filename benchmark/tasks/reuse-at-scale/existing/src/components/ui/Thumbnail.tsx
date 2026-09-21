type ThumbnailProps = { className?: string; children?: React.ReactNode };
export function Thumbnail({ className, children }: ThumbnailProps) {
  return <div className={className} data-component="Thumbnail">{children}</div>;
}
