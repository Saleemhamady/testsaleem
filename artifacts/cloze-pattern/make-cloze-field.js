#!/usr/bin/env node
// Generates the partial-credit Cloze NUMERICAL field for a game worth N points.
//
// A single {1:NUMERICAL:=N:tol} answer is graded right/wrong: it cannot scale
// the mark with the score. This emits one accepted answer per attainable
// score, each carrying its own percentage, so Moodle autogrades the game play
// proportionally.
//
//   node make-cloze-field.js 10          -> 0..10 in whole points
//   node make-cloze-field.js 20 2        -> 0..20 in steps of 2
const max = Number(process.argv[2] || 10);
const step = Number(process.argv[3] || 1);

if (!isFinite(max) || max <= 0) {
  console.error('usage: node make-cloze-field.js <maxScore> [step]');
  process.exit(1);
}

const parts = [];
for (let s = max; s >= 0; s -= step) {
  const pct = Math.round((s / max) * 100);
  // The highest-scoring answer uses "=" (100%); the rest carry an explicit
  // percentage. Tolerance is 0 because the score is always an exact value.
  parts.push(s === max ? `=${s}:0` : `%${pct}%${s}:0`);
}

console.log(`<span id="hidden-score" style="display:none">{1:NUMERICAL:${parts.join('~')}}</span>`);
