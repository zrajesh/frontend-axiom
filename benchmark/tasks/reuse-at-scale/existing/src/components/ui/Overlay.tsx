type OverlayProps = { isOpen: boolean; onDismiss: () => void; heading: string; children: React.ReactNode };
export function Overlay({ isOpen, onDismiss, heading, children }: OverlayProps) {
  if (!isOpen) return null;
  return (
    <div role="dialog" aria-modal="true" aria-label={heading}>
      <h2>{heading}</h2>
      {children}
      <button type="button" onClick={onDismiss}>Dismiss</button>
    </div>
  );
}
