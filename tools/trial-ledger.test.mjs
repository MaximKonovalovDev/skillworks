import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  MAX_METRIC_CALLS,
  createLedger,
  recordTrial,
  paretoFront,
  best,
  seedVsBest,
  saveLedger,
  loadLedger,
} from "./trial-ledger.mjs";

describe("valset holds 3-5 tasks", () => {
  it("rejects 2 and 6 scores, accepts 3, 4 and 5", () => {
    const ledger = createLedger("seed", [0, 0, 1]);
    assert.throws(() => recordTrial(ledger, { text: "tiny", scores: [1, 1] }), /3-5/);
    assert.throws(() => recordTrial(ledger, { text: "huge", scores: [1, 1, 1, 1, 1, 1] }), /3-5/);
    assert.equal(recordTrial(ledger, { text: "three", scores: [1, 1, 1] }).cost, 3);
    assert.equal(recordTrial(ledger, { text: "four", scores: [1, 1, 1, 1] }).cost, 4);
    assert.equal(recordTrial(ledger, { text: "five", scores: [1, 1, 1, 1, 1] }).cost, 5);
  });

  it("rejects a bad seed sheet the same way", () => {
    assert.throws(() => createLedger("seed", [1, 1]), /3-5/);
    assert.throws(() => createLedger("seed", [1, 1, 1, 1, 1, 1]), /3-5/);
  });
});

describe("max 50 metric calls", () => {
  it("stops the 51st call", () => {
    const ledger = createLedger("seed", [0, 0, 0, 0, 0]); // 5 used
    for (let i = 0; i < 9; i += 1) {
      recordTrial(ledger, { text: `child ${i}`, scores: [1, 1, 1, 1, 1] }); // +45
    }
    assert.equal(ledger.metricCalls, MAX_METRIC_CALLS);
    assert.throws(
      () => recordTrial(ledger, { text: "one more", scores: [1, 1, 1] }),
      /budget exhausted/,
    );
  });
});

describe("Pareto keep", () => {
  it("drops a trial beaten on both axes", () => {
    const ledger = createLedger("seed", [0, 0, 0]);
    recordTrial(ledger, { text: "strong", scores: [1, 1, 1] });
    recordTrial(ledger, { text: "weak", scores: [1, 0, 0] });
    const ids = paretoFront(ledger).map((c) => c.id);
    assert.ok(ids.includes("t1"));
    assert.ok(!ids.includes("t2"));
  });

  it("drops a same-score trial that costs more", () => {
    const ledger = createLedger("seed", [0, 0, 0]);
    recordTrial(ledger, { text: "cheap best", scores: [1, 1, 1] });
    recordTrial(ledger, { text: "costly twin", scores: [1, 1, 1, 1, 1] });
    assert.deepEqual(paretoFront(ledger).map((c) => c.id), ["t1"]);
  });

  it("keeps trials that trade score against cost", () => {
    const ledger = createLedger("seed", [0, 0, 0]);
    recordTrial(ledger, { text: "sharp", scores: [1, 1, 1, 1, 0] }); // 0.8, cost 5
    recordTrial(ledger, { text: "cheap", scores: [1, 1, 0] }); // 0.6667, cost 3
    assert.deepEqual(paretoFront(ledger).map((c) => c.id).sort(), ["t1", "t2"]);
  });
});

describe("seed vs best", () => {
  it("reports lift and the winning trial", () => {
    const ledger = createLedger("seed", [0, 0, 0]);
    recordTrial(ledger, { text: "child", scores: [1, 1, 1] });
    const top = best(ledger);
    assert.equal(top.id, "t1");
    const r = seedVsBest(ledger);
    assert.equal(r.seedMean, 0);
    assert.equal(r.bestMean, 1);
    assert.equal(r.lift, 1);
    assert.equal(r.verdict, "LIFT");
    assert.equal(r.beaten, true);
  });

  it("holds when nothing beats the seed", () => {
    const ledger = createLedger("seed", [1, 1, 1]);
    recordTrial(ledger, { text: "flat", scores: [1, 1, 0] });
    const r = seedVsBest(ledger);
    assert.equal(r.bestId, "seed");
    assert.equal(r.lift, 0);
    assert.equal(r.verdict, "HOLD");
  });
});

describe("ledger files", () => {
  it("loads a missing path as null (skip cleanly)", () => {
    const dir = mkdtempSync(join(tmpdir(), "ledger-"));
    assert.equal(loadLedger(join(dir, "nope.json")), null);
  });

  it("round-trips through save and load", () => {
    const dir = mkdtempSync(join(tmpdir(), "ledger-"));
    const file = join(dir, "trial-ledger.json");
    const ledger = createLedger("seed", [0, 0, 1]);
    recordTrial(ledger, { text: "child", scores: [1, 1, 1] });
    saveLedger(ledger, file);
    const back = loadLedger(file);
    assert.equal(back.seed.text, "seed");
    assert.equal(back.metricCalls, ledger.metricCalls);
    assert.deepEqual(seedVsBest(back), seedVsBest(ledger));
  });
});
