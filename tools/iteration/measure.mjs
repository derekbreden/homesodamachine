#!/usr/bin/env node
// measure.mjs records a requested change's milestones and observes matching geometry drawn by the live viewer.
import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const MARKS = new Set(["source-edit", "review", "local-view", "live-view", "published", "complete"]);
const HELP = `On-demand request-to-view measurement; nothing installs a watcher or joins a build.

  node tools/iteration/measure.mjs start --received-at ISO --request TEXT [--run NAME]
  node tools/iteration/measure.mjs mark RECORD PHASE [--at ISO] [--note TEXT] [--artifact PATH ...]
  tools/run -- node tools/iteration/measure.mjs watch RECORD --mesh PATH --part NAME [--part NAME ...]
  node tools/iteration/measure.mjs report RECORD [--json]

PHASE: source-edit, review, local-view, live-view, published, complete
watch: --source PATH selects imported bodies instead of --part; --next waits for selected local geometry to change.
       --delivery records website notifications, member URLs and target mounting alongside the draw.
       --url URL overrides the published model link; --timeout SECONDS bounds observation.
Receipt time is the original user-message timestamp, including investigation before this tool starts.
`;

export function timestamp(value, label = "timestamp") {
  if (!value || !/(?:Z|[+-]\d\d:\d\d)$/i.test(value) || !Number.isFinite(Date.parse(value))) {
    throw new Error(`${label} must be an ISO timestamp with a timezone`);
  }
  return new Date(value).toISOString();
}

function commit() {
  return execFileSync("git", ["-C", ROOT, "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
}

function load(record) {
  const file = path.resolve(record);
  const data = JSON.parse(fs.readFileSync(file, "utf8"));
  if (data.schema !== "hsm-request-iteration") throw new Error("Not a request-iteration record");
  return { file, data, events: `${file.slice(0, -path.extname(file).length)}.events.jsonl` };
}

async function fingerprint(file) {
  const absolute = path.resolve(ROOT, file);
  const hash = createHash("sha256");
  let bytes = 0;
  for await (const chunk of fs.createReadStream(absolute)) { hash.update(chunk); bytes += chunk.length; }
  return { path: path.relative(ROOT, absolute), sha256: hash.digest("hex"), bytes };
}

async function append(record, phase, { at = new Date().toISOString(), note, artifacts = [], evidence } = {}) {
  const { data, events } = load(record);
  at = timestamp(at);
  if (Date.parse(at) < Date.parse(data.request.received_at)) throw new Error("A milestone cannot precede the request");
  const row = { phase, at, recorded_at: new Date().toISOString(), source_commit: commit() };
  if (note) row.note = note;
  if (artifacts.length) row.artifacts = await Promise.all(artifacts.map(fingerprint));
  if (evidence) row.evidence = evidence;
  // A single append keeps independent marks made while a browser observes the request.
  fs.appendFileSync(events, JSON.stringify(row) + "\n");
  return row;
}

export function summarize(record, events, now = new Date().toISOString()) {
  const received = Date.parse(record.request.received_at);
  const ordered = [...events].sort((a, b) => Date.parse(a.at) - Date.parse(b.at));
  const milestones = {};
  for (const row of ordered) if (!milestones[row.phase]) milestones[row.phase] = {
    at: row.at, seconds_from_request: (Date.parse(row.at) - received) / 1000,
    ...(row.note ? { note: row.note } : {}), ...(row.evidence ? { evidence: row.evidence } : {}),
  };
  return {
    purpose: record.purpose, request: record.request,
    elapsed_seconds: (Date.parse(milestones.complete?.at || now) - received) / 1000,
    review_iterations: ordered.filter((row) => row.phase === "review").length,
    milestones, events: ordered,
  };
}

function sceneSnapshot(file) {
  const bytes = fs.readFileSync(file);
  if (bytes.length < 4 || bytes.readUInt32LE() > bytes.length - 4) throw new Error("Truncated mesh header");
  const head = JSON.parse(bytes.subarray(4, 4 + bytes.readUInt32LE()).toString());
  if (head.v !== 4 || !Array.isArray(head.meshes)) throw new Error("Watch requires a shared assembly .step.mesh header");
  return { head, artifact: { path: path.relative(ROOT, file), sha256: createHash("sha256").update(bytes).digest("hex"), bytes: bytes.length } };
}

export function partKey(node) {
  return node.entries.map((entry, index) => `${node.asset}:${index}:${JSON.stringify(node.transform || null)}:${JSON.stringify(entry.color)}`).join("|");
}

function expectation(head, names, source) {
  const nodes = source ? head.meshes.filter((node) => node.source === source) : names.map((name) => {
    const node = head.meshes.find((node) => node.name === name);
    if (!node) throw new Error(`Expected part is absent from the local assembly: ${name}`);
    return node;
  });
  if (!nodes.length) throw new Error("No local bodies match the requested source or names");
  return { revision: head.src, parts: nodes.map((node) => ({
    name: node.name, key: partKey(node), asset: node.asset,
    source: node.source, source_sha256: node.source_sha256,
  })) };
}

// This function runs in the reference browser; a manifest alone never establishes a drawn part.
export async function observeExpectedFrame(expected, timeoutMs) {
  const h = window.__hsm;
  if (!h?.renderer || !h.currentGroup || !h.THREE) throw new Error("The reference viewer is not ready");
  const original = h.renderer.render;
  let timer;
  const frames = [];
  const submitted = [];
  const observed = new Set();
  let completed = false;
  const started = Date.now();
  const clip = new h.THREE.Matrix4(), frustum = new h.THREE.Frustum();
  const depth = new h.THREE.Matrix4(), vertex = new h.THREE.Vector3();
  const clippedBy = (plane, box) => {
    vertex.set(plane.normal.x < 0 ? box.min.x : box.max.x,
      plane.normal.y < 0 ? box.min.y : box.max.y, plane.normal.z < 0 ? box.min.z : box.max.z);
    return plane.distanceToPoint(vertex) < 0;
  };
  const canvasEligible = () => {
    const canvas = h.renderer.domElement;
    const rect = canvas.getBoundingClientRect();
    if (!(rect.width > 0 && rect.height > 0)) return false;
    for (let element = canvas; element; element = element.parentElement) {
      const style = window.getComputedStyle(element);
      if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) return false;
    }
    return true;
  };
  const solidEligible = (solid, scene, camera) => {
    let inScene = false;
    for (let object = solid; object; object = object.parent) {
      if (!object.visible) return false;
      if (object === scene) { inScene = true; break; }
    }
    if (!inScene || !camera.layers.test(solid.layers) || !solid.geometry?.attributes.position.count
      || solid.geometry.drawRange?.count === 0) return false;
    const geometry = solid.geometry;
    if (!geometry.boundingBox) geometry.computeBoundingBox();
    if (!geometry.boundingBox || geometry.boundingBox.isEmpty()) return false;
    const world = geometry.boundingBox.clone().applyMatrix4(solid.matrixWorld);
    if (!frustum.intersectsBox(world)) return false;
    depth.multiplyMatrices(camera.matrixWorldInverse, solid.matrixWorld);
    const cameraBox = geometry.boundingBox.clone().applyMatrix4(depth);
    // A target whose depth bounds cross the clipping planes cannot establish an intact draw.
    const epsilon = Math.max(1, camera.far) * 1e-7;
    if (-cameraBox.max.z < camera.near - epsilon || -cameraBox.min.z > camera.far + epsilon) return false;
    if ((h.renderer.clippingPlanes || []).some((plane) => clippedBy(plane, world))) return false;
    const materials = Array.isArray(solid.material) ? solid.material : [solid.material];
    return materials.some((material) => {
      if (!material || !material.visible || material.opacity <= 0 || !material.colorWrite) return false;
      const planes = h.renderer.localClippingEnabled ? material.clippingPlanes || [] : [];
      const clipped = planes.map((plane) => clippedBy(plane, world));
      return !clipped.length || !(material.clipIntersection ? clipped.every(Boolean) : clipped.some(Boolean));
    });
  };
  try {
    return await new Promise((resolve, reject) => {
      timer = setTimeout(() => reject(new Error(`Expected geometry was not drawn before the observation timeout; matched ${[...observed].join(", ") || "none"}`)), timeoutMs);
      h.renderer.render = function (scene, camera) {
        const result = original.apply(this, arguments);
        if (completed || scene !== h.scene || camera !== h.camera) return result;
        const group = h.currentGroup;
        const head = group?.userData.sharedHead;
        const parts = group?.userData.parts;
        if (!group?.visible || !head || !parts || !canvasEligible()) return result;
        clip.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
        frustum.setFromProjectionMatrix(clip);
        const ready = expected.parts.filter((part) => {
          const node = head.meshes.find((node) => node.name === part.name);
          const mounted = parts.get(part.name);
          return node?.asset === part.asset && mounted?.key === part.key
            && mounted.solids?.some((solid) => solidEligible(solid, scene, camera));
        }).map((part) => part.name);
        const allReady = ready.length === expected.parts.length;
        if (!allReady && !ready.some((name) => !observed.has(name))) return result;
        // Completion of this WebGL draw is observable; a human device's presentation is not.
        this.getContext().finish();
        for (const name of ready) observed.add(name);
        frames.push({ at: new Date().toISOString(), matched: ready, revision: head.src,
          seconds_from_observer: (Date.now() - started) / 1000,
          scene_loading: !!group.userData.sceneLoading,
          eligibility: "Matching mounted geometry has visible ancestors and materials, intersects the camera frustum and lies within its depth bounds; occlusion is not established." });
        if (window.__hsmIterationFrame) {
          submitted.push(Promise.resolve(window.__hsmIterationFrame(frames.at(-1))).catch(reject));
        }
        if (allReady) {
          completed = true;
          Promise.all(submitted).then(() => resolve({ frames, failed_parts: group.userData.failedParts || [] }));
        }
        return result;
      };
    });
  } finally {
    clearTimeout(timer);
    h.renderer.render = original;
  }
}

async function watch(record, values) {
  if (!values.mesh) throw new Error("watch needs --mesh with the local installed assembly header");
  const file = path.resolve(ROOT, values.mesh);
  const names = values.part || [];
  const source = values.source?.replaceAll("\\", "/");
  if (!!source === !!names.length) throw new Error("Select --part names or an imported --source path");
  let snapshot = sceneSnapshot(file);
  let target = expectation(snapshot.head, names, source);
  const requestedNames = target.parts.map((part) => part.name);
  const timeoutMs = Number(values.timeout || 180) * 1000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) throw new Error("Observation timeout must be positive");
  const { launchBrowser, closeBrowser } = await import("../render/browser.js");
  let browser;
  const opened = new Date().toISOString();
  const relative = path.relative(path.join(ROOT, "hardware"), file).replaceAll("\\", "/").replace(/\.mesh$/, "");
  const url = values.url || `https://homesodamachine.com/3d#step:${encodeURIComponent(relative)}?find=${encodeURIComponent(target.parts.map((part) => `solid: ${part.name}`).join("\n"))}`;
  try {
    browser = await launchBrowser({ protocolTimeout: timeoutMs + 30000 });
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(String(error)));
    if (values.delivery) {
      const delivery = (stage, detail, at = new Date().toISOString()) => append(record, "delivery-event", {
        at, evidence: { kind: "reference-browser-delivery", stage, file: relative, ...detail },
      });
      await page.exposeFunction("__hsmIterationDelivery", (stage, detail, at) => delivery(stage, detail, at));
      await page.evaluateOnNewDocument(({ file, names }) => {
        const send = (stage, detail) => {
          window.__hsmIterationDelivery?.(stage, detail, new Date().toISOString()).catch(() => {});
        };
        window.addEventListener("hsm:files-changed", (event) => {
          if (event.detail?.files?.includes(file)) send("server-change-received", { files: event.detail.files });
        });
        window.addEventListener("hsm:step-mounted", (event) => {
          const detail = event.detail;
          if (detail?.file === file && (!detail.part || names.includes(detail.part))) send("target-mounted", detail);
        });
      }, { file: relative, names: requestedNames });
      page.on("response", (response) => {
        if (new URL(response.url()).pathname !== "/api/objects" || response.status() !== 200) return;
        const at = new Date().toISOString();
        response.json().then(data => {
          const address = data.objects?.[relative + ".mesh"];
          return delivery("member-urls-received", {
            ...(address ? { member_url: new URL(address, url).origin + new URL(address, url).pathname } : {}),
          }, at);
        }).catch(() => {});
      });
    }
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
    await page.waitForFunction(() => window.__hsm?.currentGroup?.userData?.parts?.size, { timeout: timeoutMs });
    const ready = await append(record, "observer-ready", { evidence: { kind: "reference-browser", url, opened_at: opened, next: !!values.next } });
    console.error(`Reference viewer ready at ${ready.at}${values.next ? "; waiting for selected local geometry to change" : ""}`);
    if (values.next) {
      const before = JSON.stringify(target.parts.map(({ name, key }) => [name, key]));
      const old = new Map(target.parts.map(({ name, key }) => [name, key]));
      const deadline = Date.now() + timeoutMs;
      while (Date.now() < deadline) {
        await new Promise((resolve) => setTimeout(resolve, 100));
        const currentSnapshot = sceneSnapshot(file);
        const current = expectation(currentSnapshot.head, names, source);
        if (JSON.stringify(current.parts.map(({ name, key }) => [name, key])) !== before) {
          target = { ...current, parts: current.parts.filter((part) => part.key !== old.get(part.name)) };
          snapshot = currentSnapshot;
          if (values.delivery) await append(record, "delivery-event", { evidence: {
            kind: "local-producer-update", stage: "local-update", artifact: snapshot.artifact,
            parts: target.parts.map(({ name, asset, key }) => ({ name, asset, key })),
          } });
          break;
        }
      }
      if (JSON.stringify(target.parts.map(({ name, key }) => [name, key])) === before) throw new Error("Selected local geometry did not change before the observation timeout");
    }
    const artifact = snapshot.artifact;
    const selection = { mode: values.next ? "next-local-update" : "current-local-snapshot",
      requested_names: requestedNames, observed_names: target.parts.map((part) => part.name),
      ...(source ? { source } : {}),
      scope: values.next ? "Only bodies changed in the first selected local producer update are observed; later producer updates are outside this observation."
        : "Only the selected bodies in this local artifact snapshot are observed." };
    let frameCount = 0;
    await page.exposeFunction("__hsmIterationFrame", async (frame) => {
      await append(record, frameCount++ ? "live-view-progress" : "live-view", {
        at: frame.at, evidence: { kind: "reference-browser-draw-eligibility", url, expected_artifact: artifact, expected_parts: target.parts, selection,
          ...frame, page_errors: [...errors],
          scope: "Matching mounted geometry is eligible for this completed reference draw. Unobstructed pixels, occlusion and the user's device paint are not established." },
      });
    });
    const evidence = await page.evaluate(observeExpectedFrame, target, timeoutMs);
    await append(record, "all-live-view", { at: evidence.frames.at(-1).at,
      evidence: { kind: "reference-browser-draw-eligibility", names: target.parts.map((part) => part.name), expected_artifact: artifact, selection,
        failed_parts: evidence.failed_parts, page_errors: errors } });
    console.log(JSON.stringify({ record: path.resolve(record), frames: evidence.frames, selection, expected_artifact: artifact }, null, 2));
  } catch (error) {
    await append(record, "observer-error", { note: String(error.message || error) });
    throw error;
  } finally { await closeBrowser(browser); }
}

export async function main(argv = process.argv.slice(2)) {
  const { values, positionals } = parseArgs({ args: argv, allowPositionals: true, options: {
    "received-at": { type: "string" }, request: { type: "string" }, run: { type: "string" },
    at: { type: "string" }, note: { type: "string" }, artifact: { type: "string", multiple: true },
    mesh: { type: "string" }, part: { type: "string", multiple: true }, source: { type: "string" },
    url: { type: "string" }, timeout: { type: "string" }, next: { type: "boolean" }, delivery: { type: "boolean" },
    json: { type: "boolean" }, help: { type: "boolean", short: "h" },
  } });
  const [command, record, phase] = positionals;
  if (!command || values.help) { console.log(HELP); return; }
  if (command === "start") {
    if (!values.request?.trim()) throw new Error("start needs --request with the user's words");
    const received = timestamp(values["received-at"], "--received-at");
    const name = values.run || `iteration-${new Date().toISOString().replace(/[-:.]/g, "")}`;
    if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(name)) throw new Error("--run must name a run directory");
    const file = path.join(ROOT, ".cache/runs", name, "iteration.json");
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify({ schema: "hsm-request-iteration",
      purpose: "This record measures a request through source edits, agent reviews and observed website geometry.",
      request: { received_at: received, words: values.request }, created_at: new Date().toISOString(), source_commit: commit(),
    }, null, 2) + "\n", { flag: "wx" });
    console.log(file);
    return;
  }
  if (!record) throw new Error(`${command} needs the record path printed by start`);
  if (command === "mark") {
    if (!MARKS.has(phase)) throw new Error(`Unknown milestone: ${phase || "(missing)"}`);
    if (phase === "live-view" && !values.note?.trim()) throw new Error("A manual live-view mark needs --note describing what was observed");
    console.log(JSON.stringify(await append(record, phase, { at: values.at, note: values.note, artifacts: values.artifact || [],
      ...(phase === "live-view" ? { evidence: { kind: "manual-observation", scope: "The note records the observer's assertion; this mark contains no instrumented geometry-draw timing." } } : {}),
    }), null, 2));
  } else if (command === "watch") await watch(record, values);
  else if (command === "report") {
    const { data, events } = load(record);
    const rows = fs.existsSync(events) ? fs.readFileSync(events, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [];
    const result = summarize(data, rows);
    if (values.json) console.log(JSON.stringify(result, null, 2));
    else {
      console.log(`Request received: ${result.request.received_at}`);
      for (const [phase, row] of Object.entries(result.milestones)) {
        const scope = row.evidence?.selection?.mode === "next-local-update" ? " (first selected local update only)" : "";
        console.log(`${phase}${scope}: ${row.seconds_from_request.toFixed(3)} s${row.note ? ` — ${row.note}` : ""}${row.evidence?.kind ? ` [${row.evidence.kind}]` : ""}`);
      }
      console.log(`Review iterations: ${result.review_iterations}`);
      console.log(`${result.milestones.complete ? "Completed" : "Elapsed"}: ${result.elapsed_seconds.toFixed(3)} s`);
    }
  } else throw new Error(`Unknown command: ${command}`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => { console.error(error.message || error); process.exitCode = 1; });
}
