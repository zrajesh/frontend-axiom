import { titleCase } from "../lib/format";

interface UserBadgeRowProps {
  label: string;
  tone?: string;
}

export function UserBadgeRow({ label, tone }: UserBadgeRowProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
