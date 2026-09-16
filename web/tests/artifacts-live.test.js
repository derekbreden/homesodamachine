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
import { copyFile, mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { execFile } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { pathToFileURL } from "node:url";

import { pointersMoved, refreshArtifacts, retireSolids } from "../lib/artifacts-live.js";

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
test("a pointer file whose members moved under the same bundle is a look worth taking", () => {
  const have = { bundle: { sha256: "b" }, solids: { "a.step": "1", "b.step": "2" } };
  assert.equal(pointersMoved(have, structuredClone(have)), false, "the same pointer file moves nothing");
  assert.equal(pointersMoved(have, { ...have, solids: { ...have.solids, "b.step": "3" } }), true,
    "a member re-pointed under the bundle left behind");
  assert.equal(pointersMoved(have, { ...have, solids: { ...have.solids, "c.step": "4" } }), true,
    "a member the disk has never held");
  assert.equal(pointersMoved(have, { ...have, bundle: { sha256: "c" } }), true,
    "a whole cut still moves on its digest");
  assert.equal(pointersMoved(null, have), true, "no pointer file on disk is behind by definition");
});

test("retired parts leave the viewer's directory while current and local files remain", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "hsm-retired-solids-"));
  try {
    const names = ["old-insert.step", "old-insert.step.mesh", "body.step", "local.step"];
    await mkdir(path.join(root, "hardware"));
    for (const name of names) await writeFile(path.join(root, "hardware", name), name);
    const have = { solids: Object.fromEntries(names.slice(0, 3).map(name => [`hardware/${name}`, "hash"])) };
    const next = { solids: { "hardware/body.step": "new-hash" } };
    assert.equal(pointersMoved(have, next), true);
    assert.deepEqual(await retireSolids(root, have, next), [
      "hardware/old-insert.step", "hardware/old-insert.step.mesh",
    ]);
    for (const name of names.slice(0, 2)) {
      await assert.rejects(readFile(path.join(root, "hardware", name)), { code: "ENOENT" });
    }
    for (const name of names.slice(2)) {
      assert.equal(await readFile(path.join(root, "hardware", name), "utf8"), name);
    }
    await retireSolids(root, have, next); // A retry also works after the old paths are absent.
    await assert.rejects(retireSolids(root, { solids: { "web/server.js": "hash" } }, next),
      /outside hardware/);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("CAD adoption and retirement keep the committed install guide", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "hsm-committed-guide-"));
  try {
    const names = ["install-guide.pdf", "install-guide.cover.png", "install-guide.pdf.json"];
    await mkdir(path.join(root, "hardware/install-guide"), { recursive: true });
    for (const name of names) await writeFile(path.join(root, "hardware/install-guide", name), "new edition");
    const have = { solids: Object.fromEntries(names.map(name => [`hardware/install-guide/${name}`, "old-hash"])) };
    await writeFile(path.join(root, "hardware/cad-artifacts.json"), JSON.stringify(have));
    await writeFile(path.join(root, "package.json"), '{"type":"module"}');
    for (const relative of ["scripts/fetch-cad-artifacts.mjs", "lib/store.js", "contracts/documents.js"]) {
      const destination = path.join(root, "web", relative);
      await mkdir(path.dirname(destination), { recursive: true });
      await copyFile(new URL("../" + relative, import.meta.url), destination);
    }
    const { stdout } = await promisify(execFile)(process.execPath,
      [path.join(root, "web/scripts/fetch-cad-artifacts.mjs"), "--adopt", "--check"]);
    assert.match(stdout, /0 solid\(s\) at the pointed-at hash/);
    assert.deepEqual(await retireSolids(root, have, { solids: {} }), []);
    for (const name of names) {
      assert.equal(await readFile(path.join(root, "hardware/install-guide", name), "utf8"), "new edition");
    }
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

for (const failure of ["download-error", "stale-success"]) {
  test(`CAD adoption backs off after ${failure} and verifies recovery`, async (t) => {
    const root = await mkdtemp(path.join(tmpdir(), "hsm-adoption-retry-"));
    const realFetch = globalThis.fetch;
    t.mock.timers.enable({ apis: ["Date"], now: 60_000 });
    try {
      for (const dir of ["hardware", "web/scripts", "web/public", "web/lib", "web/contracts"]) {
        await mkdir(path.join(root, dir), { recursive: true });
      }
      await writeFile(path.join(root, "package.json"), '{"type":"module"}');
      for (const relative of ["lib/artifacts-live.js", "contracts/documents.js", "contracts/scorecard-sidecar.js"]) {
        await copyFile(new URL("../" + relative, import.meta.url), path.join(root, "web", relative));
      }
      const have = {
        bundle: { sha256: "bundle" },
        release: { url: "https://github.com/derekbreden/homesodamachine/releases/download/cad-artifacts/bundle.gz" },
        solids: { "hardware/body.step": "old" },
      };
      let next = { ...have, solids: { "hardware/body.step": "new" } };
      const pointerPath = path.join(root, "hardware/cad-artifacts.json");
      await writeFile(pointerPath, JSON.stringify(have));
      await writeFile(path.join(root, "hardware/body.step"), "old");
      await writeFile(path.join(root, "mode"), failure);
      await writeFile(path.join(root, "web/scripts/fetch-cad-artifacts.mjs"), `
        import { readFileSync, writeFileSync, appendFileSync } from 'node:fs';
        const root = new URL('../../', import.meta.url);
        const check = process.argv.includes('--check');
        appendFileSync(new URL('calls', root), check ? 'check\\n' : 'download\\n');
        const mode = readFileSync(new URL('mode', root), 'utf8');
        const body = new URL('hardware/body.step', root);
        if (check) process.exit(readFileSync(body, 'utf8') === 'new' ? 0 : 1);
        if (mode === 'download-error') process.exit(1);
        if (mode === 'recovered') writeFileSync(body, 'new');
      `);
      globalThis.fetch = async (url) => {
        const value = String(url).includes("cad-artifacts.json") ? next : { checks: [] };
        return new Response(JSON.stringify({
          encoding: "base64", content: Buffer.from(JSON.stringify(value)).toString("base64"),
        }));
      };
      const module = await import(pathToFileURL(path.join(root, "web/lib/artifacts-live.js")));
      const events = [];
      const context = {
        broadcast(event) { events.push(event); }, setRecent() {}, commit: "fixture",
        hardwareDir: path.join(root, "hardware"), detect: [async () => ["body.step"]],
      };
      const failed = await module.refreshArtifacts(context, { force: true });
      assert.ok(failed.error, "failed download or stale bytes must not complete adoption");
      assert.deepEqual(JSON.parse(await readFile(pointerPath, "utf8")), have);
      assert.equal(events.length, 0, "the viewer is not told to load an unverified adoption");

      // Both an explicit post and the ordinary poll keep checking the publication,
      // but neither launches a child process until its retry delay expires.
      for (const delay of [120_000, 240_000, 480_000, 960_000, 1_800_000]) {
        const before = await readFile(path.join(root, "calls"), "utf8");
        const held = await module.refreshArtifacts(context, { force: true });
        assert.equal(held.retryAt, Date.now() + delay);
        t.mock.timers.tick(delay - 1);
        const early = await module.refreshArtifacts(context);
        assert.equal(early.retryAt, held.retryAt);
        assert.equal(await readFile(path.join(root, "calls"), "utf8"), before,
          "a repeated failure does not hash the tree during backoff");
        assert.deepEqual(JSON.parse(await readFile(pointerPath, "utf8")), have);
        t.mock.timers.tick(1);
        assert.ok((await module.refreshArtifacts(context, { force: true })).error);
      }

      const capped = await module.refreshArtifacts(context, { force: true });
      assert.equal(capped.retryAt, Date.now() + 1_800_000, "the delay stays capped at 30 minutes");

      // New pointer bytes get an immediate attempt even while the previous
      // publication is backing off, and start their own delay on failure.
      next = { ...next, bundle: { sha256: "another-bundle" } };
      assert.ok((await module.refreshArtifacts(context, { force: true })).error);
      const fresh = await module.refreshArtifacts(context, { force: true });
      assert.equal(fresh.retryAt, Date.now() + 120_000);

      await writeFile(path.join(root, "mode"), "recovered");
      t.mock.timers.tick(120_000);
      const beforeRecovery = (await readFile(path.join(root, "calls"), "utf8")).trim().split("\n");
      const recovered = await module.refreshArtifacts(context, { force: true });
      assert.equal(recovered.moved, true, "the same publication is retried after storage recovers");
      assert.deepEqual(JSON.parse(await readFile(pointerPath, "utf8")), next);
      assert.equal(await readFile(path.join(root, "hardware/body.step"), "utf8"), "new");
      assert.equal(events.length, 1);
      const afterRecovery = (await readFile(path.join(root, "calls"), "utf8")).trim().split("\n");
      assert.deepEqual(afterRecovery.slice(beforeRecovery.length), ["download", "check"]);
      assert.deepEqual(await module.refreshArtifacts(context, { force: true }),
        { moved: false, scorecards: 0 }, "success clears the retry state");
      assert.equal((await readFile(path.join(root, "calls"), "utf8")).trim().split("\n").length,
        afterRecovery.length, "an adopted publication requires no further child processes");
    } finally {
      globalThis.fetch = realFetch;
      await rm(root, { recursive: true, force: true });
    }
  });
}
