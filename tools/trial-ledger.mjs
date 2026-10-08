// SPDX-License-Identifier: MIT
// tools/trial-ledger.mjs: GEPA-shaped trial ledger (skillworks, public repo).
//
// Shape ideas only from gepa-ai/gepa (MIT, https://github.com/gepa-ai/gepa):
// a seed candidate, child trials graded on a small sampled valset, a running
// count of metric calls against a fixed budget, and a Pareto-kept set where a
// child survives only when no other trial beats it on both score and cost.
// No donor code is copied. Stdlib only, offline, no model calls, no network.
//
// Rules enforced here:
// - every graded valset holds 3-5 task scores (GEPA samples a few, not all)
// - the whole ledger spends at most 50 metric calls (one call per task score)
// - Pareto keep: dominated trials leave the kept set (history stays for audit)
// - seed vs best: the ledger always reports the seed mean beside the best mean
//
// A missing ledger file loads as null (skip cleanly) so machine readers never
// crash on a path that is not there yet.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { pathToFileURL } from "node:url";

export const MIN_VALSET = 3;
export const MAX_VALSET = 5;
export const MAX_METRIC_CALLS = 50;
export const LIFT_GATE = 0.3;
export const VERSION = 1;

const stamp = () => new Date().toISOString().slice(0, 16) + "Z";

export function mean(xs) {
  if (!Array.isArray(xs) || xs.length === 0) return 0;
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}

function round4(n) {
  return Math.round(n * 10000) / 10000;
}

export function validateScores(scores) {
  if (!Array.isArray(scores)) throw new Error("scores must be an array");
  if (scores.length < MIN_VALSET || scores.length > MAX_VALSET) {
    throw new Error(
      `valset must hold ${MIN_VALSET}-${MAX_VALSET} tasks, got ${scores.length}`,
    );
  }
  for (const s of scores) {
    if (typeof s !== "number" || Number.isNaN(s) || s < 0 || s > 1) {
      throw new Error("each score must be a number in 0..1");
    }
  }
  return true;
}

function checkLedger(ledger) {
  if (!ledger || typeof ledger !== "object") throw new Error("bad ledger");
  if (!ledger.seed || typeof ledger.seed.text !== "string") {
    throw new Error("bad ledger: seed text missing");
  }
  if (!Array.isArray(ledger.history) || !Array.isArray(ledger.kept)) {
    throw new Error("bad ledger: history/kept missing");
  }
  if (typeof ledger.metricCalls !== "number") throw new Error("bad ledger: metricCalls missing");
}

export function createLedger(seedText, seedScores = []) {
  if (typeof seedText !== "string" || !seedText.trim()) {
    throw new Error("seedText must be a non-empty string");
  }
  const scores = [...seedScores];
  if (scores.length > 0) validateScores(scores);
  if (scores.length > MAX_METRIC_CALLS) throw new Error("budget exhausted at seed");
  const m = round4(mean(scores));
  return {
    version: VERSION,
    seed: { text: seedText, scores, mean: m, cost: scores.length },
    history: [],
    kept: [],
    metricCalls: scores.length,
    at: stamp(),
  };
}

// A dominates B when it is no worse on both axes and better on at least one:
// higher mean score, lower cost (fewer valset tasks spent).
export function dominates(a, b) {
  const scoreOk = a.mean >= b.mean;
  const costOk = a.cost <= b.cost;
  const strictly = a.mean > b.mean || a.cost < b.cost;
  return scoreOk && costOk && strictly;
}

export function paretoFront(ledger) {
  checkLedger(ledger);
  const front = [];
  for (const cand of ledger.history) {
    let beaten = false;
    for (const other of ledger.history) {
      if (other !== cand && dominates(other, cand)) {
        beaten = true;
        break;
      }
    }
    if (!beaten) front.push({ ...cand });
  }
  return front;
}

function nextId(ledger) {
  return `t${ledger.history.length + 1}`;
}

export function recordTrial(ledger, trial) {
  checkLedger(ledger);
  if (!trial || typeof trial !== "object") throw new Error("trial must be an object");
  const { text, scores, reflection = "", parent = "seed", id = null } = trial;
  if (typeof text !== "string" || !text.trim()) {
    throw new Error("trial text must be a non-empty string");
  }
  validateScores(scores);
  if (ledger.metricCalls + scores.length > MAX_METRIC_CALLS) {
    throw new Error(
      `budget exhausted: ${ledger.metricCalls} used, ${scores.length} more exceeds ${MAX_METRIC_CALLS}`,
    );
  }
  const candId = id ?? nextId(ledger);
  if (ledger.history.some((c) => c.id === candId)) {
    throw new Error(`duplicate trial id ${JSON.stringify(candId)}`);
  }
  const cand = {
    id: candId,
    text,
    scores: [...scores],
    mean: round4(mean(scores)),
    cost: scores.length,
    reflection: String(reflection),
    parent: String(parent),
    at: stamp(),
  };
  ledger.history.push(cand);
  ledger.metricCalls += scores.length;
  ledger.kept = paretoFront(ledger);
  return { ...cand };
}

export function best(ledger) {
  checkLedger(ledger);
  const pool = [
    { kind: "seed", id: "seed", text: ledger.seed.text, mean: ledger.seed.mean, cost: ledger.seed.cost },
    ...ledger.kept.map((c) => ({ kind: "trial", ...c })),
  ];
  let top = pool[0];
  for (const cand of pool.slice(1)) {
    if (cand.mean > top.mean || (cand.mean === top.mean && cand.cost < top.cost)) {
      top = cand;
    }
  }
  return { ...top };
}

export function seedVsBest(ledger) {
  checkLedger(ledger);
  const top = best(ledger);
  const seedMean = ledger.seed.mean;
  const lift = round4(top.mean - seedMean);
  return {
    seedMean,
    bestKind: top.kind,
    bestId: top.id,
    bestMean: top.mean,
    lift,
    beaten: top.mean > seedMean,
    metricCalls: ledger.metricCalls,
    budget: MAX_METRIC_CALLS,
    verdict: lift >= LIFT_GATE ? "LIFT" : "HOLD",
  };
}

export function toJSON(ledger) {
  checkLedger(ledger);
  return JSON.stringify(ledger, null, 2) + "\n";
}

export function fromJSON(text) {
  const obj = JSON.parse(String(text));
  checkLedger(obj);
  return obj;
}

export function saveLedger(ledger, path) {
  checkLedger(ledger);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, toJSON(ledger), "utf8");
  return path;
}

// Missing path loads as null (skip cleanly); corrupt JSON still throws.
export function loadLedger(path) {
  try {
    return fromJSON(readFileSync(path, "utf8"));
  } catch (err) {
    if (err && err.code === "ENOENT") return null;
    throw err;
  }
}

function printHelp() {
  console.log("usage: node tools/trial-ledger.mjs demo|check <ledger.json>|help");
  console.log("  demo: run a 3-trial example and print seed vs best");
  console.log("  check <file>: print seed vs best for a saved ledger (SKIP when missing)");
}

function printReport(ledger) {
  const r = seedVsBest(ledger);
  console.log(`seed ${r.seedMean} vs best ${r.bestId} ${r.bestMean} (lift ${r.lift})`);
  console.log(`calls ${r.metricCalls}/${r.budget}, kept ${ledger.kept.length}/${ledger.history.length}`);
  console.log(`verdict ${r.verdict}`);
  return r;
}

function cmdDemo() {
  const ledger = createLedger("seed prompt", [0, 0, 1]);
  recordTrial(ledger, { text: "child one", scores: [1, 0, 1], reflection: "fixes task one" });
  recordTrial(ledger, { text: "child two", scores: [1, 1, 1], reflection: "fixes task two" });
  recordTrial(ledger, { text: "costly twin", scores: [1, 1, 1, 1, 1], reflection: "same mean, more cost" });
  const r = printReport(ledger);
  console.log(`RESULT ${r.verdict === "LIFT" ? "PASS" : "HOLD"}`);
  return 0;
}

function cmdCheck(file) {
  if (!file) {
    console.log("FAIL need a ledger file path");
    return 1;
  }
  const ledger = loadLedger(file);
  if (!ledger) {
    console.log(`SKIP clean: no ledger at ${file}`);
    return 0;
  }
  const r = printReport(ledger);
  console.log(`RESULT ${r.verdict === "LIFT" ? "PASS" : "HOLD"}`);
  return 0;
}

const invoked = process.argv[1] ?? "";
if (import.meta.url === pathToFileURL(invoked).href) {
  const [cmd, arg] = process.argv.slice(2);
  if (cmd === "demo") process.exitCode = cmdDemo();
  else if (cmd === "check") process.exitCode = cmdCheck(arg);
  else printHelp();
}
