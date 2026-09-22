import { titleCase } from "../lib/format";

interface ToneDotProps {
  label: string;
  tone?: string;
}

export function ToneDot({ label, tone }: ToneDotProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
