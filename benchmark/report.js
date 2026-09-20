#!/usr/bin/env node
/**
 * Renders benchmark/results/<stamp>/summary.tsv.
 *
 * Lives in its own file rather than inline `node -e` because bash expands
 * ${...} inside a double-quoted heredoc before node sees it — which silently
 * corrupted both the shell variables and every JS template literal.
 *
 * Usage: node report.js <summary.tsv>
 */
const fs = require("fs");

const file = process.argv[2];
if (!file || !fs.existsSync(file)) {
  console.error("usage: report.js <summary.tsv>");
  process.exit(2);
}

const rows = fs
  .readFileSync(file, "utf8")
  .trim()
  .split("\n")
  .filter(Boolean)
  .map((l) => l.split("\t"));

const by = {};
for (const [task, arm, p, t, pct, valid] of rows) {
  (by[task] ||= {})[arm] = { p: +p, t: +t, pct: +pct, valid: +valid };
}

const pad = (s, n) => String(s).padEnd(n);
console.log(
  pad("TASK", 24) + pad("TREATMENT", 12) + pad("CONTROL", 12) + pad("DELTA", 9) + "VALID RUNS"
);

let sum = 0;
let counted = 0;
const excluded = [];

for (const [task, a] of Object.entries(by)) {
  const tv = (a.treatment && a.treatment.valid) || 0;
  const cv = (a.control && a.control.valid) || 0;
  const tr = (a.treatment && a.treatment.pct) || 0;
  const ct = (a.control && a.control.pct) || 0;
  const d = tr - ct;

  // A task that lost an entire arm has no comparison to make. Averaging it in
  // would let an outage masquerade as a result.
  const usable = tv > 0 && cv > 0;
  if (usable) {
    sum += d;
    counted++;
  } else {
    excluded.push(task);
  }

  console.log(
    pad(task, 24) +
      pad(tr.toFixed(2), 12) +
      pad(ct.toFixed(2), 12) +
      pad((d >= 0 ? "+" : "") + d.toFixed(2), 9) +
      "t:" + tv + " c:" + cv +
      (usable ? "" : "  <- EXCLUDED, no valid comparison")
  );
}

console.log("");
if (counted > 0) {
  const mean = sum / counted;
  console.log(
    "mean delta (valid tasks only): " +
      (mean >= 0 ? "+" : "") +
      mean.toFixed(3) +
      "  [" + counted + " task(s)]"
  );
} else {
  console.log("NO VALID RESULT — every task lost an arm to invalid runs.");
}
if (excluded.length) console.log("excluded: " + excluded.join(", "));
