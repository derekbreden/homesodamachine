// These on-demand tests verify receipt timing and distinguish mounted geometry from updated manifests.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import { summarize, timestamp } from "./measure.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

test("request latency includes investigation before the recorder starts", () => {
  const record = { purpose: "fixture", request: { received_at: "2026-11-08T10:00:00Z", words: "Adjust the nameplate" }, created_at: "2026-11-08T10:04:00Z" };
  const events = [
    { phase: "review", at: "2026-11-08T10:07:00Z" },
    { phase: "local-view", at: "2026-11-08T10:05:00Z" },
    { phase: "review", at: "2026-11-08T10:06:00Z" },
    { phase: "live-view", at: "2026-11-08T10:08:00Z" },
    { phase: "complete", at: "2026-11-08T10:10:00Z" },
  ];
  const result = summarize(record, events, "2026-11-08T11:00:00Z");
  assert.equal(result.milestones["local-view"].seconds_from_request, 300);
  assert.equal(result.milestones["live-view"].seconds_from_request, 480);
  assert.equal(result.review_iterations, 2);
  assert.equal(result.elapsed_seconds, 600);
  assert.throws(() => timestamp("2026-11-08T10:00:00"), /timezone/);
});

test("independent CLI marks preserve their artifact binding and original receipt time", () => {
  const name = `iteration-tool-test-${process.pid}`;
  const directory = path.join(ROOT, ".cache/runs", name);
  const cli = path.join(ROOT, "tools/iteration/measure.mjs");
  const invoke = (args) => execFileSync(process.execPath, [cli, ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
  try {
    const record = invoke(["start", "--received-at", "2026-11-08T10:00:00Z", "--request", "Inspect the changed nameplate", "--run", name]);
    invoke(["mark", record, "review", "--at", "2026-11-08T10:03:00Z", "--note", "First evaluation", "--artifact", "tools/iteration/measure.mjs"]);
    invoke(["mark", record, "review", "--at", "2026-11-08T10:04:00Z", "--note", "Second evaluation"]);
    const result = JSON.parse(invoke(["report", record, "--json"]));
    assert.equal(result.milestones.review.seconds_from_request, 180);
    assert.equal(result.review_iterations, 2);
    assert.match(result.events[0].artifacts[0].sha256, /^[a-f0-9]{64}$/);
    assert.equal(result.events[0].artifacts[0].path, "tools/iteration/measure.mjs");
    assert.throws(() => invoke(["mark", record, "source-edit", "--at", "2026-11-08T09:00:00Z"]));
  } finally { fs.rmSync(directory, { recursive: true, force: true }); }
});

test("manual and backdated live observations identify when current evidence was captured", () => {
  const name = `iteration-manual-test-${process.pid}`;
  const directory = path.join(ROOT, ".cache/runs", name);
  const cli = path.join(ROOT, "tools/iteration/measure.mjs");
  const invoke = (args) => execFileSync(process.execPath, [cli, ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
  try {
    const record = invoke(["start", "--received-at", "2026-11-08T10:00:00Z", "--request", "Verify the material search", "--run", name]);
    assert.throws(() => invoke(["mark", record, "live-view"]), /manual live-view mark needs/);
    const mark = JSON.parse(invoke(["mark", record, "live-view", "--at", "2026-11-08T10:02:00Z", "--note", "Asserted the search candidates in the live browser", "--artifact", "tools/iteration/measure.mjs"]));
    assert.equal(mark.at, "2026-11-08T10:02:00.000Z");
    assert.ok(Date.parse(mark.recorded_at) > Date.parse(mark.at));
    assert.equal(mark.evidence.kind, "manual-observation");
    const result = JSON.parse(invoke(["report", record, "--json"]));
    assert.equal(result.milestones["live-view"].seconds_from_request, 120);
    assert.equal(result.events[0].recorded_at, mark.recorded_at);
    assert.match(invoke(["report", record]), /\[manual-observation\]/);
    fs.appendFileSync(record.replace(/\.json$/, ".events.jsonl"), JSON.stringify({ phase: "all-live-view", at: "2026-11-08T10:03:00Z",
      evidence: { kind: "reference-browser-draw-eligibility", selection: { mode: "next-local-update", requested_names: ["a", "b"], observed_names: ["a"] } } }) + "\n");
    assert.match(invoke(["report", record]), /all-live-view \(first selected local update only\)/);
    assert.deepEqual(JSON.parse(invoke(["report", record, "--json"])).milestones["all-live-view"].evidence.selection.observed_names, ["a"]);
  } finally { fs.rmSync(directory, { recursive: true, force: true }); }
});
