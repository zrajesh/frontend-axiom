type ProfileFormProps = { className?: string; children?: React.ReactNode };
export function ProfileForm({ className, children }: ProfileFormProps) {
  return <div className={className} data-component="ProfileForm">{children}</div>;
}
