import { titleCase } from "../lib/format";

interface DividerRuleProps {
  label: string;
  tone?: string;
}

export function DividerRule({ label, tone }: DividerRuleProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
