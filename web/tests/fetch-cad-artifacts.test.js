// Run the real fetcher in an isolated tree with an authenticated-store boundary.
// The public route can be broken while the service's R2 credentials still work.

import { test } from "node:test";
import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { gzipSync } from "node:zlib";

const run = promisify(execFile);
const hash = (bytes) => createHash("sha256").update(bytes).digest("hex");
const member = Buffer.from("ISO-10303-21;\ncurrent published member\n");
const memberPath = "hardware/part.step";

async function fixture(t, { held = true, old = false, networkWorks = false,
  objectBytes = gzipSync(member), bundleMembers = null, extraWanted = {} } = {}) {
  const root = await mkdtemp(path.join(tmpdir(), "cad-direct-r2-"));
  t.after(() => rm(root, { recursive: true, force: true }));
  for (const dir of ["hardware", "bucket", "web/scripts", "web/lib", "web/contracts"]) {
    await mkdir(path.join(root, dir), { recursive: true });
  }
  await writeFile(path.join(root, "package.json"), '{"type":"module"}\n');
  for (const relative of ["scripts/fetch-cad-artifacts.mjs", "contracts/documents.js"]) {
    await copyFile(new URL("../" + relative, import.meta.url), path.join(root, "web", relative));
  }
  // Fake only the authenticated R2 adapter; the fetcher's routing, gzip and hash
  // validation are the production implementation copied above.
  await writeFile(path.join(root, "web/lib/store.js"), `
    import { createReadStream } from "node:fs";
    import { appendFile } from "node:fs/promises";
    export async function storeFromEnv() {
      return { kind: "r2", async readStream(name) {
        await appendFile(new URL("../../r2-reads.log", import.meta.url), name + "\\n");
        return createReadStream(new URL("../../bucket/" + name, import.meta.url));
      } };
    }
  `);
  const name = `s-${hash(member)}.gz`;
  if (held) await writeFile(path.join(root, "bucket", name), objectBytes);
  if (old) await writeFile(path.join(root, memberPath), "older published member");
  let bundleBytes = null;
  if (bundleMembers) {
    const dir = path.join(root, "archive-input");
    for (const [rel, bytes] of Object.entries(bundleMembers)) {
      await mkdir(path.dirname(path.join(dir, rel)), { recursive: true });
      await writeFile(path.join(dir, rel), bytes);
    }
    const file = path.join(root, "bundle.tar.gz");
    await run("tar", ["-czf", file, "-C", dir, "--", ...Object.keys(bundleMembers)]);
    bundleBytes = await readFile(file);
  }
  const requests = [];
  const server = createServer((req, res) => {
    requests.push(req.url);
    if (req.url === "/release/bundle.tar.gz" && bundleBytes) {
      res.writeHead(200, { "content-type": "application/gzip" });
      res.end(bundleBytes);
    } else if (networkWorks) {
      res.writeHead(200, { "content-type": "application/gzip" });
      res.end(gzipSync(member));
    } else {
      res.writeHead(502);
      res.end("the live object's public hostname is unavailable");
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const storeUrl = `http://127.0.0.1:${server.address().port}/objects/`;
  await writeFile(path.join(root, "hardware/cad-artifacts.json"), JSON.stringify({
    store: { url: storeUrl, objects: "s-" },
    solids: { [memberPath]: hash(member), ...extraWanted },
    ...(bundleBytes ? {
      release: { url: `http://127.0.0.1:${server.address().port}/release/bundle.tar.gz`, asset: "bundle.tar.gz" },
      bundle: { sha256: hash(bundleBytes), bytes: bundleBytes.length },
    } : {}),
  }));
  const fetch = (args = [], env = {}) => run(process.execPath,
    [path.join(root, "web/scripts/fetch-cad-artifacts.mjs"), ...args], {
      cwd: path.join(root, "web"),
      env: { ...process.env, RENDER_GIT_COMMIT: "", OBJECTS_DIR: "", ...env },
    });
  return { root, fetch, name, requests };
}

test("authenticated R2 hydration succeeds without reaching the broken public route", async (t) => {
  const f = await fixture(t);
  const { stdout } = await f.fetch();
  assert.match(stdout, /1 of 1 solid\(s\) in place/);
  assert.deepEqual(await readFile(path.join(f.root, memberPath)), member);
  assert.equal(await readFile(path.join(f.root, "r2-reads.log"), "utf8"), f.name + "\n");
  assert.deepEqual(f.requests, [], "no live-site redirect or archive was required");
});

test("a failed authenticated read falls back to the existing network object route", async (t) => {
  const f = await fixture(t, { held: false, networkWorks: true });
  await f.fetch();
  assert.deepEqual(await readFile(path.join(f.root, memberPath)), member);
  assert.deepEqual(f.requests, ["/objects/" + f.name]);
});

test("Render startup replaces a cached older member without an explicit adopt flag", async (t) => {
  const f = await fixture(t, { old: true });
  const { stdout } = await f.fetch([], { RENDER_GIT_COMMIT: "deployed-commit" });
  assert.match(stdout, /1 solid\(s\) hold older bytes/);
  assert.deepEqual(await readFile(path.join(f.root, memberPath)), member);
  assert.deepEqual(f.requests, []);
});

test("local startup retains a differing local cut until adoption is requested", async (t) => {
  const f = await fixture(t, { old: true });
  const { stdout } = await f.fetch();
  assert.match(stdout, /left as they are/);
  assert.equal(await readFile(path.join(f.root, memberPath), "utf8"), "older published member");
  await assert.rejects(readFile(path.join(f.root, "r2-reads.log")), { code: "ENOENT" });
  await f.fetch(["--adopt"]);
  assert.deepEqual(await readFile(path.join(f.root, memberPath)), member);
  assert.deepEqual(f.requests, []);
});

for (const [failure, objectBytes] of [
  ["corrupt gzip", Buffer.from("not a gzip stream")],
  ["wrong member hash", gzipSync(Buffer.from("bytes belonging to a different model"))],
]) {
  test(`${failure} does not replace the previously served model`, async (t) => {
    const f = await fixture(t, { old: true, objectBytes });
    await assert.rejects(f.fetch(["--adopt"]));
    assert.equal(await readFile(path.join(f.root, memberPath), "utf8"), "older published member");
  });
}

test("a fallback archive with a wrong member hash leaves the existing model unchanged", async (t) => {
  const f = await fixture(t, { held: false, old: true,
    bundleMembers: { [memberPath]: Buffer.from("an older archive member") } });
  const { stderr } = await f.fetch(["--adopt"]);
  assert.match(stderr, /not the pointed-at bytes/);
  assert.equal(await readFile(path.join(f.root, memberPath), "utf8"), "older published member");
  await assert.rejects(f.fetch(["--adopt", "--check"]));
});

test("a partial fallback extraction never reaches the served directory", async (t) => {
  const f = await fixture(t, { held: false, old: true,
    bundleMembers: { [memberPath]: member },
    extraWanted: { "hardware/not-in-bundle.step": hash(Buffer.from("absent")) } });
  const { stderr } = await f.fetch(["--adopt"]);
  assert.match(stderr, /not-in-bundle\.step/);
  assert.equal(await readFile(path.join(f.root, memberPath), "utf8"), "older published member");
});

test("a verified fallback archive member replaces the old model", async (t) => {
  const f = await fixture(t, { held: false, old: true, bundleMembers: { [memberPath]: member } });
  await f.fetch(["--adopt"]);
  assert.deepEqual(await readFile(path.join(f.root, memberPath)), member);
  await f.fetch(["--adopt", "--check"]);
});
