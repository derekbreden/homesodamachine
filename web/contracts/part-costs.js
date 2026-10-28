// Part-number costs: each material's own cost and its roll-up through the BOM.
// web/lib/part-costs.js allocates bom.md's delivered dollars and labor.md's
// attended minutes to part numbers and serves the result as `costs` beside the
// catalog (/api/materials). Each material's `direct` cost is per piece: its
// purchase price, the stock and supplies it consumes, and the labor spent on it.
// A roll-up adds every child's roll-up, multiplied by its quantity, so an
// assembly costs its contents plus its own work, at every level.
import { bomItems, materialIndex } from "./materials.js";

export function directCost(catalog, id) {
  return catalog?.costs?.direct?.[id] || null;
}

export function laborUsd(catalog, minutes) {
  return minutes * (catalog?.costs?.rate || 0) / 60;
}

// { usd, parts, labor, minutes, costed } per piece of `id`. `parts` is every
// purchased, stock and supplies dollar under it; `labor` prices its minutes at
// the ledger's rate. `costed` is false where nothing under it carries a cost.
export function rollupCost(catalog, id, options = {}, memo = new Map(), seen = new Set()) {
  const key = id;
  if (memo.has(key)) return memo.get(key);
  const empty = { usd: 0, parts: 0, labor: 0, minutes: 0, costed: false };
  if (!catalog?.costs || seen.has(id)) return empty;
  const material = materialIndex(catalog).get(id);
  const own = directCost(catalog, id);
  let parts = own?.usd || 0, minutes = own?.minutes || 0, costed = Boolean(own);
  const nextSeen = new Set([...seen, id]);
  for (const item of bomItems(material, options)) {
    if (typeof item.quantity !== "number") continue;
    const child = rollupCost(catalog, item.material, options, memo, nextSeen);
    parts += item.quantity * child.parts;
    minutes += item.quantity * child.minutes;
    costed ||= child.costed;
  }
  const labor = laborUsd(catalog, minutes);
  const result = { usd: parts + labor, parts, labor, minutes, costed };
  memo.set(key, result);
  return result;
}

// Kinds a material's own cost elements fall into, in display order.
export const COST_KINDS = [
  { id: "price", label: "Purchase" },
  { id: "stock", label: "Material" },
  { id: "supplies", label: "Supplies" },
  { id: "labor", label: "Labor" },
  { id: "unallocated", label: "Not yet on a part" },
];

export function money(usd, { cents = true } = {}) {
  if (usd == null || Number.isNaN(usd)) return "—";
  const digits = cents || Math.abs(usd) < 100 ? 2 : 0;
  return "$" + usd.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

// Minutes the way a person says them: 45 m, 2 h, 1 h 15 m. A share of a shared
// operation keeps a tenth below ten minutes, and seconds below one, where
// rounding would misstate the work.
export function duration(minutes) {
  if (!minutes) return "0 m";
  if (minutes < 1) return minutes * 60 < 0.5 ? "<1 s" : `${Math.round(minutes * 60)} s`;
  if (minutes < 10 && Math.abs(minutes - Math.round(minutes)) >= 0.05) return `${minutes.toFixed(1)} m`;
  const total = Math.round(minutes);
  const h = Math.floor(total / 60), m = total % 60;
  return !h ? `${m} m` : m ? `${h} h ${m} m` : `${h} h`;
}

// A labor operation's run, read off its labor.md Run cell the way
// hardware/scripts/_labor_totals.py reads it:
// `15 m setup a plate of 30 · 30 s a float · 3 a machine`. `a batch` is one
// setup for every machine built together.
const RUN_RE = /^([0-9][0-9 hms]*?) setup an? ([a-z][a-z-]*)(?: of ([0-9]+))? · ([0-9][0-9 hms]*?) an? ([a-z][a-z -]*?) · ([0-9]+) an? machine$/;
const RUN_DURATION_RE = /^(?:([0-9]+) h)? ?(?:([0-9]+) m)? ?(?:([0-9]+) s)?$/;

function runDuration(text) {
  const match = text.trim().match(RUN_DURATION_RE);
  if (!match || !match.slice(1).some(Boolean)) return null;
  const [h, m, s] = match.slice(1).map((n) => Number(n || 0));
  return h * 60 + m + s / 60;
}

export function parseRun(text) {
  const match = String(text || "").replace(/\s+/g, " ").trim().match(RUN_RE);
  if (!match) return null;
  const setup = runDuration(match[1]), each = runDuration(match[4]);
  const cap = match[3] ? Number(match[3]) : null;
  if (setup == null || each == null || (match[2] === "batch") !== (cap == null)) return null;
  return { setup, run: match[2], cap, each, piece: match[5], per: Number(match[6]) };
}

// Attended minutes a machine takes when `batch` machines are built together:
// every setup the batch's pieces need plus each piece's own time, to the tenth
// of a minute labor.md writes.
export function runMinutes(run, batch) {
  const pieces = batch * run.per;
  const runs = run.cap == null ? 1 : Math.ceil(pieces / run.cap);
  return Math.round((runs * run.setup + pieces * run.each) / batch * 10 + 1e-8) / 10;
}

// "Plate of 30 · 15 m setup + 30 s a float"; "Batch of 10 machines · …".
export function runText(run, batch) {
  const size = run.cap == null ? `Batch of ${batch} machines` : `${run.run[0].toUpperCase()}${run.run.slice(1)} of ${run.cap}`;
  return `${size} · ${duration(run.setup)} setup + ${duration(run.each)} a ${run.piece}`;
}
