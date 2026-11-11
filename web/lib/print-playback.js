// The material viewer opens a saved toolpath replay from the print archive.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { gunzipSync } from "node:zlib";
import { HSM_EVENTS } from "../contracts/client-events.js";

const archive = new URL("../../print-playbacks/", import.meta.url);
const published = new URL("https://raw.githubusercontent.com/derekbreden/homesodamachine/main/print-playbacks/");
const player = new URL("../../tools/gcode/playback-page.html", import.meta.url);
const theme = new URL("../../tools/viz/inline-mobile/assets/theme.js", import.meta.url);
const materialId = /^HSM-\d+$/;
const sha256 = /^[a-f0-9]{64}$/;
const maxReplayBytes = 8_000_000;
let liveCatalog;

function parseCatalog(text) {
  const entries = JSON.parse(text);
  if (!entries || typeof entries !== "object" || Array.isArray(entries) ||
      !Object.entries(entries).every(([id, entry]) => materialId.test(id) &&
        entry && typeof entry.title === "string" && typeof entry.sha256 === "string" && sha256.test(entry.sha256))) {
    throw new Error("Invalid print playback catalog");
  }
  return entries;
}

export function readPrintPlaybacks() {
  if (liveCatalog) return liveCatalog;
  try { return parseCatalog(readFileSync(new URL("catalog.json", archive), "utf8")); }
  catch { return {}; }
}

// The existing live publication poll adopts data-only updates from main.
export async function carryPrintPlaybacks() {
  const res = await fetch(new URL("catalog.json", published), { signal: AbortSignal.timeout(5000) });
  if (res.ok) liveCatalog = parseCatalog(await res.text());
}

async function readReplay(hash) {
  const filename = `${hash}.json.gz`;
  let compressed;
  try { compressed = await readFile(new URL(filename, archive)); }
  catch (error) {
    if (error.code !== "ENOENT" || !process.env.RENDER_GIT_COMMIT) throw error;
    const res = await fetch(new URL(filename, published), { signal: AbortSignal.timeout(8000) });
    if (!res.ok) throw new Error(`Print playback archive returned ${res.status}`);
    compressed = Buffer.from(await res.arrayBuffer());
  }
  const bytes = gunzipSync(compressed, { maxOutputLength: maxReplayBytes });
  if (createHash("sha256").update(bytes).digest("hex") !== hash) throw new Error("Print playback hash mismatch");
  const replay = JSON.parse(bytes.toString("utf8"));
  if (replay.version !== 1 || !replay.sampled) throw new Error("Unsupported print playback data");
  return replay;
}

const escapeText = value => value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

const styles = `
:root { color-scheme: dark; font: 16px system-ui, sans-serif; background: #10319c; color: white;
  --foreground: white; --muted-foreground: #dce6ff; --secondary: #1941a9;
  --viz-series-1: #ff9152; --viz-series-2: #94b8ff; --input: #6b8fe9;
  --primary: #ff9152; --primary-foreground: #10319c; }
* { box-sizing: border-box; }
body { --playback-padding: clamp(.75rem, 2vw, 1.5rem); margin: 0; padding: var(--playback-padding); }
body #hsm-motion-playback { max-width: 80rem; margin: auto; height: calc(100dvh - 2 * var(--playback-padding));
  grid-template-rows: auto auto minmax(11rem, 1fr) auto auto auto; }
body #hsm-motion-playback h2 { max-width: 100%; margin: 0; font-size: clamp(1rem, 2.5vw, 1.35rem); }
body #hsm-motion-playback .motion-stage { height: 100%; min-height: 0; max-height: none;
  aspect-ratio: auto; background: #0d2982; border-radius: .5rem; }
.motion-controls button, .motion-controls select { min-height: 44px; padding: .375rem .625rem; border: 1px solid var(--input);
  border-radius: .375rem; background: var(--secondary); color: var(--secondary-foreground); font: inherit; }
.motion-controls .btn-primary { border-color: var(--primary); background: var(--primary); color: var(--primary-foreground); }
.motion-scrubber input { min-height: 36px; margin: 0; accent-color: var(--primary); }
.text-small { font-size: .875rem; }
.text-muted { color: var(--muted-foreground); }
.tabular-nums { font-variant-numeric: tabular-nums; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); }
`;

export function mountPrintPlayback(app) {
  app.get("/print-playback/:material", async (req, res) => {
    const id = req.params.material;
    const entry = materialId.test(id) && readPrintPlaybacks()[id];
    if (!entry) return res.status(404).end();
    try {
      const [template, themeSource, replay] = await Promise.all([
        readFile(player, "utf8"), readFile(theme, "utf8"), readReplay(entry.sha256),
      ]);
      const title = escapeText(entry.title);
      const data = JSON.stringify({ ...replay, start_at_end: true }).replaceAll("<", "\\u003c");
      const substitutions = { "{{TITLE}}": title, "/*THEME*/": themeSource, "/*DATA*/": data };
      const body = template.replace(/\{\{TITLE\}\}|\/\*(THEME|DATA)\*\//g, token => substitutions[token]);
      res.set("Cache-Control", "no-cache");
      res.set("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'unsafe-inline'; frame-ancestors 'self'; base-uri 'none'");
      res.type("html").send(`<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title><style>${styles}</style></head><body>${body}
<script>addEventListener("keydown", event => {
  if (event.key === "Escape" && parent !== window) {
    parent.postMessage({ type: ${JSON.stringify(HSM_EVENTS.DOCUMENT_ESCAPE)} }, location.origin);
  }
});</script></body></html>`);
    } catch (error) {
      console.warn(`[print playback] ${id}: ${error.message}`);
      res.status(503).type("text").send("Print playback is temporarily unavailable.");
    }
  });
}
