type ButtonProps = {
  variant: "primary" | "danger" | "ghost";
  size?: "sm" | "md";
  onClick: () => void;
  children: React.ReactNode;
};
export function Button({ variant, size = "md", onClick, children }: ButtonProps) {
  return <button type="button" data-variant={variant} data-size={size} onClick={onClick}>{children}</button>;
}
