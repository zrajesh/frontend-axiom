import { titleCase } from "../lib/format";

interface StackRowProps {
  label: string;
  tone?: string;
}

export function StackRow({ label, tone }: StackRowProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
