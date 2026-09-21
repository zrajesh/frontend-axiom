type NotificationTogglesProps = { className?: string; children?: React.ReactNode };
export function NotificationToggles({ className, children }: NotificationTogglesProps) {
  return <div className={className} data-component="NotificationToggles">{children}</div>;
}
