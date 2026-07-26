import path from "path";
import puppeteer from "puppeteer";
import sharp from "sharp";
import { start } from "/Users/derekbredensteiner/Developer/homesodamachine/web/server.js";

const REPO = "/Users/derekbredensteiner/Developer/homesodamachine";
const rel = process.argv[2];
const t0 = Date.now();
const { server } = await start({ port: 0, dev: false, hardwareDir: path.join(REPO, "hardware") });
const port = server.address().port;
const t1 = Date.now();
const browser = await puppeteer.launch({ headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
const page = await browser.newPage();
const t2 = Date.now();
await page.goto(`http://localhost:${port}/3d`, { waitUntil: "domcontentloaded", timeout: 60000 });
await page.waitForFunction(() => !!window.__hsm, { timeout: 30000 });
const t3 = Date.now();
// force occt wasm ready (the CDN fetch + wasm compile) before timing the parse
await page.evaluate(async () => { const m = await import("/js/viewer/step.js"); await m.occtPromise; });
const t4 = Date.now();

const phases = await page.evaluate(async (file) => {
  const m = await import("/js/viewer/step.js");
  const THREE = await import("three");
  const { applyXray } = await import("/js/viewer/xray.js");
  const a = performance.now();
  const resp = await fetch(`/steps/${file}`);
  const buf = new Uint8Array(await resp.arrayBuffer());
  const b = performance.now();
  const occt = await m.occtPromise;
  const result = occt.ReadStepFile(buf, null);
  const c = performance.now();
  // rebuild mesh via the module's own path by calling renderThumbnail after clearing cache
  const d0 = performance.now();
  const url = await m.renderThumbnail(file);
  const d = performance.now();
  return { bytes: buf.length, meshes: result.meshes.length,
           tris: result.meshes.reduce((s,x)=>s+(x.index?x.index.array.length/3:0),0),
           fetch_ms: b-a, occtParse_ms: c-b, fullRenderThumbnail_ms: d-d0, urlLen: url ? url.length : 0 };
}, rel);
const t5 = Date.now();
await browser.close();
await new Promise((r) => server.close(() => r()));
console.log(JSON.stringify({
  serverBoot_ms: t1-t0, puppeteerLaunch_ms: t2-t1, pageLoad_ms: t3-t2, occtWasmReady_ms: t4-t3,
  inPage_total_ms: t5-t4, ...phases, grandTotal_ms: Date.now()-t0
}, null, 2));
