import { titleCase } from "../lib/format";

interface MetaLineProps {
  label: string;
  tone?: string;
}

export function MetaLine({ label, tone }: MetaLineProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
