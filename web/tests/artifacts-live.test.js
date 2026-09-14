// The rate floor under `/api/artifacts/refresh` (web/lib/artifacts-live.js) holds a look it
// cannot take yet. It must not throw one away.
//
// WHY THIS BREAKS SILENTLY. A refused post costs nothing visible: the container keeps serving
// the solids it already has and says so to nobody. The cut that was refused then waits for the
// 120s poll — twelve times the 10s floor it was refused for — and the only symptom is the human
// watching homesodamachine.com for geometry that published two minutes ago. Four sessions commit
// into this checkout and `.githooks/post-commit` fires `publish_now.py` on every commit, so a
// post landing inside another post's floor is the resting state, not a burst.
//
// `fetch` is replaced so `adopt()` fails at its first call: nothing is written, no bundle is
// fetched, and the run still exercises the floor, which is the whole subject here. The clock is
// mocked because the floor is 10 real seconds and this test is not worth ten of them.

import { test, mock } from "node:test";
import assert from "node:assert/strict";

import { lockMoved, refreshArtifacts } from "../lib/artifacts-live.js";

// Never reached — `adopt()` throws at `lockOnMain()`, before any of these are read.
const ctx = { broadcast() {}, setRecent() {}, commit: "0000000", hardwareDir: ".", detect: [] };

test("a look refused by the floor is held for the rest of it, not dropped", async () => {
  const realFetch = globalThis.fetch;
  let looks = 0;
  globalThis.fetch = async () => {
    looks += 1;
    throw new Error("no network in this test");
  };
  mock.timers.enable({ apis: ["setTimeout", "Date"] });
  try {
    // Past the floor from the module's `lastLook = 0`, so the first look is one that runs.
    mock.timers.tick(60_000);
    await refreshArtifacts(ctx);
    const after_first = looks;
    assert.ok(after_first > 0, "the first look should have reached fetch");

    // Same instant: inside the floor. This is the post that used to be thrown away.
    const held = refreshArtifacts(ctx);
    const PENDING = Symbol("pending");
    assert.equal(
      await Promise.race([held, Promise.resolve(PENDING)]), PENDING,
      "a look inside the floor must be held, not resolved as skipped",
    );
    assert.equal(looks, after_first, "and it must not have looked yet");

    // A second post inside the same floor rides the one already held rather than adding a look.
    assert.equal(refreshArtifacts(ctx), held, "one held look serves every post in the gap");

    mock.timers.tick(10_000);
    await held;
    assert.ok(looks > after_first, "the held look must run once the floor is out");
  } finally {
    mock.timers.reset();
    globalThis.fetch = realFetch;
  }
});

// A HELD PUBLISH MOVES MEMBERS UNDER A BUNDLE THAT STAYS. `pack.py --write --publish-held`
// sends the objects that moved and names the bundle it already had, so a detector reading the
// bundle's digest alone sees nothing and the geometry waits for the reconciler's whole cut.
test("a lock whose members moved under the same bundle is a look worth taking", () => {
  const have = { bundle: { sha256: "b" }, solids: { "a.step": "1", "b.step": "2" } };
  assert.equal(lockMoved(have, structuredClone(have)), false, "the same lock moves nothing");
  assert.equal(lockMoved(have, { ...have, solids: { ...have.solids, "b.step": "3" } }), true,
    "a member re-pinned under the bundle left behind");
  assert.equal(lockMoved(have, { ...have, solids: { ...have.solids, "c.step": "4" } }), true,
    "a member the disk has never held");
  assert.equal(lockMoved(have, { ...have, bundle: { sha256: "c" } }), true,
    "a whole cut still moves on its digest");
  assert.equal(lockMoved(null, have), true, "no lock on disk is behind by definition");
});
