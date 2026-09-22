import { titleCase } from "../lib/format";

interface CountPillProps {
  label: string;
  tone?: string;
}

export function CountPill({ label, tone }: CountPillProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
