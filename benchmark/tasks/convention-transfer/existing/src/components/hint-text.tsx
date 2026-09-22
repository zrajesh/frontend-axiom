import { titleCase } from "../lib/format";

interface HintTextProps {
  label: string;
  tone?: string;
}

export function HintText({ label, tone }: HintTextProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
