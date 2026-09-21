type ModalProps = { isOpen: boolean; onClose: () => void; title: string; children: React.ReactNode };
export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  if (!isOpen) return null;
  return (
    <div role="dialog" aria-modal="true" aria-label={title}>
      <h2>{title}</h2>
      {children}
      <Button variant="ghost" onClick={onClose}>Close</Button>
    </div>
  );
}
import { Button } from "./Button";
