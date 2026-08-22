import { test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  LOCAL_BACK_TOP,
  localServiceForChange,
  runLocalServiceFirst,
} from "../dev-server/local-service.js";
import { isRunnableScript } from "../dev-server/deps.js";


const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const enclosure = path.join(REPO_ROOT, LOCAL_BACK_TOP.source);


test("the enclosure source maps only to a distinct ignored local scene", () => {
  const job = localServiceForChange(REPO_ROOT, enclosure);
  assert.ok(job);
  assert.equal(job.scriptPath, path.join(REPO_ROOT, LOCAL_BACK_TOP.script));
  assert.equal(job.outputPath, path.join(REPO_ROOT, LOCAL_BACK_TOP.output));
  assert.match(LOCAL_BACK_TOP.script, /[/\\]_local_service\.py$/);
  assert.equal(isRunnableScript(job.scriptPath), false, "the exact wave must not run it again");
  assert.match(LOCAL_BACK_TOP.output, /[/\\]scenes[/\\]out[/\\]local-back-top\.glb$/);
  assert.doesNotMatch(LOCAL_BACK_TOP.output, /[/\\]scenes[/\\]glb[/\\]back-top\.glb$/);

  const assemblySource = path.join(REPO_ROOT, "hardware", "manifold-layout", "enclosure_assembly.py");
  assert.equal(localServiceForChange(REPO_ROOT, assemblySource), null);
});


test("the local service finishes before the exact wave starts", async () => {
  const calls = [];
  const status = await runLocalServiceFirst(
    REPO_ROOT,
    enclosure,
    async (job) => {
      calls.push(["local", job.outputPath]);
      await Promise.resolve();
      calls.push(["local-done", job.outputPath]);
      return "done";
    },
    async () => { calls.push(["exact"]); },
  );
  assert.equal(status, "done");
  assert.deepEqual(calls.map(([name]) => name), ["local", "local-done", "exact"]);
});


test("a superseded local view does not launch its older exact wave", async () => {
  let exact = 0;
  assert.equal(
    await runLocalServiceFirst(
      REPO_ROOT,
      enclosure,
      async () => "superseded",
      async () => { exact += 1; },
    ),
    "superseded",
  );
  assert.equal(exact, 0);

  const other = path.join(REPO_ROOT, "hardware", "some-part.py");
  assert.equal(
    await runLocalServiceFirst(
      REPO_ROOT,
      other,
      async () => assert.fail("unmapped source must not run a local service producer"),
      async () => { exact += 1; },
    ),
    "not-applicable",
  );
  assert.equal(exact, 1);
});
