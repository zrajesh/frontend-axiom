type TabsProps = { className?: string; children?: React.ReactNode };
export function Tabs({ className, children }: TabsProps) {
  return <div className={className} data-component="Tabs">{children}</div>;
}
