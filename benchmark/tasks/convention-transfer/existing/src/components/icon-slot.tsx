import { titleCase } from "../lib/format";

interface IconSlotProps {
  label: string;
  tone?: string;
}

export function IconSlot({ label, tone }: IconSlotProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
