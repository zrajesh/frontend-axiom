Create `src/BigList.tsx` with a default export named `BigList`.

```ts
type Row = { id: string; label: string };
type Props = { rows: Row[] };
```

This is the admin audit-log screen. Support staff scroll it to find entries.
Real accounts have tens of thousands of rows.

Write only that file. No new dependencies — use what's installed.
