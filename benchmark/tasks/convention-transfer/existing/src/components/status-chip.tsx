import { titleCase } from "../lib/format";

interface StatusChipProps {
  label: string;
  tone?: string;
}

export function StatusChip({ label, tone }: StatusChipProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
