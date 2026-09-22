import { titleCase } from "../lib/format";

interface LabelTagProps {
  label: string;
  tone?: string;
}

export function LabelTag({ label, tone }: LabelTagProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
