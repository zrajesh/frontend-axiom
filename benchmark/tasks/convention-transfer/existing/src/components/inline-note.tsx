import { titleCase } from "../lib/format";

interface InlineNoteProps {
  label: string;
  tone?: string;
}

export function InlineNote({ label, tone }: InlineNoteProps) {
  return <span data-tone={tone}>{titleCase(label)}</span>;
}
