type ActionButtonProps = { tone: "primary" | "destructive" | "quiet"; onPress: () => void; children: React.ReactNode; busy?: boolean };
export function ActionButton({ tone, onPress, children, busy = false }: ActionButtonProps) {
  return (
    <button type="button" data-tone={tone} disabled={busy} onClick={onPress}>
      {children}
    </button>
  );
}
