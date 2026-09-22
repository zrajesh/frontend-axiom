import { titleCase } from "../lib/format";

interface AvatarStackProps {
  label: string;
  tone?: string;
}

export function AvatarStack({ label, tone }: AvatarStackProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
