// Pick text format — the shared language between the edge picker's copy
// blobs, the find box's paste-to-highlight, and the agent on the other
// side of the clipboard. One module owns formatting, parsing, and match
// scoring so a blob copied out of the viewer (or composed by the agent
// from CAD coordinates) round-trips back into a highlighted entity.
//
// The same box also takes a NAME — `fluid-17`, `seaflo-pump` — because a
// coordinate is what you have after you've found the thing, and a name is
// what you have before. Names need no format: they are matched on letters
// and digits alone (parseNames / matchNames).
//
// Deliberately dependency-free: points are plain {x, y, z} objects
// (THREE.Vector3 satisfies the shape), so node:test can exercise parsing
// and matching without a browser or three.js.

export function fnum(n) {
  const s = n.toFixed(3);
  return s === "-0.000" ? "0.000" : s;
}
export function fpt(v) {
  return `x=${fnum(v.x)} y=${fnum(v.y)} z=${fnum(v.z)}`;
}

// --- face record -> display text ---
// plane    · n x=… y=… z=… · thru x=… y=… z=…
// cylinder · r=… · axis x=… y=… z=… · dir x=… y=… z=…
// curved   · near x=… y=… z=…   (swept / b-spline — no compact params)
export function formatFace(face) {
  if (!face) return "";
  if (face.kind === "plane") return `plane · n ${fpt(face.n)} · thru ${fpt(face.thru)}`;
  if (face.kind === "cylinder") {
    return `cylinder · r=${face.r.toFixed(3)} · axis ${fpt(face.axis)} · dir ${fpt(face.dir)}`;
  }
  return `curved · near ${fpt(face.near)}`;
}

// --- parsing ---
// Accepts the copy-all blob format, individual rows, or any mix — one
// pick per line. Labels ("edge:", "faceA:", "click:", …) are optional;
// lines are recognized by content. Returns { picks, files, names } where
// picks carry a `kind` and a `line` (the trimmed source text for status
// UI) and names are the typed component names (parseNames).
const TRIPLE_RE = /x=(-?\d+(?:\.\d+)?)\s+y=(-?\d+(?:\.\d+)?)\s+z=(-?\d+(?:\.\d+)?)/g;
const NUM = "(-?\\d+(?:\\.\\d+)?)";

function triples(text) {
  const out = [];
  for (const m of text.matchAll(TRIPLE_RE)) {
    out.push({ x: parseFloat(m[1]), y: parseFloat(m[2]), z: parseFloat(m[3]) });
  }
  return out;
}
function tripleAfter(text, label) {
  const i = text.indexOf(label);
  if (i < 0) return null;
  const t = triples(text.slice(i));
  return t.length ? t[0] : null;
}
function numAfter(text, re) {
  const m = text.match(re);
  return m ? parseFloat(m[1]) : null;
}

// Copy-all `file:` lines carry an edition's content root (`hardware/`,
// `hardware/`); the viewer's own paths are what is left after it. The roots come from lib/editions.js, mirrored into the page
// pre-paint by lib/shell.js — `roots` is the seam node:test comes in through.
// Longest first, so `hardware` is never shortened by `hardware`.
export function pickFileToViewerPath(file, roots) {
  const s = String(file).trim();
  const dirs = roots || Object.values(globalThis.__hsmEditionDirs || {});
  for (const d of [...dirs].sort((a, b) => b.length - a.length)) {
    if (s.startsWith(d + "/")) return s.slice(d.length + 1);
  }
  return s;
}

// A line carrying no coordinates at all is a name — what the user typed
// instead of pasted. It counts as one only if every word on it is shaped
// like a name (word characters and the separators names actually use: `-`,
// `_`, `+`, `.`) and there are few enough of them to be a list. Prose fails
// on its punctuation or its length, so pasting a whole agent message still
// highlights only the picks in it.
//
// The line is then cut on COMMAS alone, not on spaces: a space is as likely
// to be a typed separator inside one name (`fluid 17`) as between two, and
// matchNames is the half that can tell — it knows what the model holds.
const NAME_WORD = /^[A-Za-z0-9][A-Za-z0-9_+.-]*$/;
const NAME_WORD_MAX = 4;

export function parseNames(body) {
  const line = String(body || "").trim();
  const words = line.split(/[\s,]+/).filter(Boolean);
  if (!words.length || words.length > NAME_WORD_MAX) return [];
  if (!words.every((w) => NAME_WORD.test(w))) return [];
  return line.split(",").map((q) => q.trim()).filter(Boolean);
}

export function parsePicks(text) {
  const picks = [];
  const files = [];
  const names = [];
  const solids = [];
  for (const raw of String(text || "").split("\n")) {
    const line = raw.trim();
    if (!line) continue;
    // strip one leading "label:" (file:, solid:, edge:, faceA:, click:, …)
    const m = line.match(/^([A-Za-z][\w-]*)\s*:\s*(.*)$/);
    const label = m ? m[1].toLowerCase() : null;
    const body = m ? m[2] : line;

    if (label === "file") { files.push(body.trim()); continue; }
    if (label === "solid") { solids.push(...parseNames(body)); continue; }

    if (/circle\s*[⌀ø]/i.test(body)) {
      const d = numAfter(body, new RegExp(`[⌀ø]\\s*${NUM}`));
      const center = tripleAfter(body, "center");
      const axis = tripleAfter(body, "axis");
      if (d != null && center) picks.push({ kind: "circle", d, center, axis, line });
      continue;
    }
    if (body.includes("→")) {
      const pts = triples(body.split("·")[0]); // endpoints live before the first ·
      if (pts.length < 2) continue;
      const len = numAfter(body, new RegExp(`len\\s+${NUM}`));
      if (/\barc\b/.test(body)) {
        picks.push({
          kind: "edge-arc", a: pts[0], b: pts[1], len,
          r: numAfter(body, new RegExp(`r=${NUM}`)),
          center: tripleAfter(body, "center"),
          axis: tripleAfter(body, "axis"),
          line,
        });
      } else {
        // straight and unclassified curves match the same way: by endpoints
        picks.push({ kind: "edge", a: pts[0], b: pts[1], len, line });
      }
      continue;
    }
    if (/\bplane\b/.test(body)) {
      const n = tripleAfter(body, "n ");
      const thru = tripleAfter(body, "thru");
      if (n && thru) picks.push({ kind: "face-plane", n, thru, line });
      continue;
    }
    if (/\bcylinder\b/.test(body)) {
      const r = numAfter(body, new RegExp(`r=${NUM}`));
      const axis = tripleAfter(body, "axis");
      const dir = tripleAfter(body, "dir");
      if (r != null && axis && dir) picks.push({ kind: "face-cylinder", r, axis, dir, line });
      continue;
    }
    // anything else holding coordinate triples: point markers
    // (click:, old endpoints: rows, curved-face "near" lines, bare points)
    const pts = triples(body);
    if (pts.length) {
      for (const p of pts) picks.push({ kind: "point", p, line });
      continue;
    }
    names.push(...parseNames(body));
  }
  // A copy-all blob's `solid:` line names the body its picks came off — the
  // container, not the target, so it stands only when nothing else does. A
  // paste of just that one line is someone asking for the whole part.
  if (!picks.length) names.push(...solids);
  return { picks, files, names };
}

// --- name matching ---
// Case and separators are noise: `fluid-17`, `Fluid 17` and `FLUID_17` are
// one query, and so is a scorecard's `fluid-17` inside `tee-y-d.Y-D-3`.
export function normalizeName(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]/g, "");
}

// An exact hit stands alone — `fluid-1` is fluid-1, not fluid-1 and the ten
// runs it prefixes. Only when nothing is exact does the query widen to every
// name containing it, which is what makes `fluid` mean all of them and `tee`
// mean the seven Y-junctions. Widening needs two characters to go on: one
// letter is a hand still typing, and it would sweep most of an assembly.
const WIDEN_MIN = 2;

function lookup(query, entries) {
  const k = normalizeName(query);
  if (!k) return [];
  const exact = entries.filter(([norm]) => norm === k);
  if (exact.length) return exact.map(([, raw]) => raw);
  if (k.length < WIDEN_MIN) return [];
  return entries.filter(([norm]) => norm.includes(k)).map(([, raw]) => raw);
}

// A dotted query missing whole falls back to its head, so the scorecard's own
// `<component>.<port>` vocabulary (`tee-y-d.Y-D-3`) pastes straight in and
// lands on the component.
function resolve(query, entries) {
  const hits = lookup(query, entries);
  if (hits.length || !query.includes(".")) return hits;
  return lookup(query.split(".")[0], entries);
}

// Match every parsed name against the scene's component names (a Set or
// array). Returns one result per query: { query, names: [...] }, empty when
// the model holds nothing by that name. A query holding spaces is tried
// WHOLE first — `fluid 17` is one name typed loosely — and only then as
// separate names, which is what makes `fluid-17 water-3` two.
export function matchNames(queries, sceneNames) {
  const entries = [...(sceneNames || [])]
    .filter(Boolean)
    .map((raw) => [normalizeName(raw), raw])
    .sort((a, b) => a[1].localeCompare(b[1], undefined, { numeric: true }));
  return (queries || []).map((query) => {
    let names = resolve(query, entries);
    if (!names.length && /\s/.test(query)) {
      names = [...new Set(query.split(/\s+/).flatMap((w) => resolve(w, entries)))];
    }
    return { query, names };
  });
}

// --- match scoring (lower is better; Infinity = not a candidate) ---
function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
}
function dot(a, b) { return a.x * b.x + a.y * b.y + a.z * b.z; }

// Perpendicular distance between a point and the line (point `p0`, dir `d`).
function lineDist(p, p0, d) {
  const v = { x: p.x - p0.x, y: p.y - p0.y, z: p.z - p0.z };
  const t = dot(v, d);
  return Math.hypot(v.x - t * d.x, v.y - t * d.y, v.z - t * d.z);
}

// Viewer edges carry {kind: "straight"|"arc"|"curve"|"loop", a, b,
// length, center?, radius?, axis?} (edge-picker's records).
export function scoreEdge(pick, edge) {
  if (pick.kind === "circle") {
    if (edge.kind !== "loop") return Infinity;
    return dist(pick.center, edge.center) + Math.abs(pick.d / 2 - edge.radius);
  }
  if (edge.kind === "loop") return Infinity;
  const ends = Math.min(
    dist(pick.a, edge.a) + dist(pick.b, edge.b),
    dist(pick.a, edge.b) + dist(pick.b, edge.a),
  ) / 2;
  let s = ends;
  if (pick.len != null) s += 0.25 * Math.abs(pick.len - edge.length);
  if (pick.kind === "edge-arc") {
    if (edge.kind === "straight") return Infinity;
    if (pick.r != null && edge.radius != null) s += 0.5 * Math.abs(pick.r - edge.radius);
    if (pick.center && edge.center) s += 0.5 * dist(pick.center, edge.center);
  }
  return s;
}

// Classified faces carry {kind: "plane"|"cylinder"|"curved", n?, thru?,
// r?, axis?, dir?, near?} (edge-picker's classifyFace records).
export function scoreFace(pick, face) {
  if (pick.kind === "face-plane") {
    if (face.kind !== "plane") return Infinity;
    const align = 1 - Math.abs(dot(pick.n, face.n)); // 0 parallel, allows flip
    const off = Math.abs(dot(
      { x: pick.thru.x - face.thru.x, y: pick.thru.y - face.thru.y, z: pick.thru.z - face.thru.z },
      face.n,
    ));
    return align * 50 + off;
  }
  if (pick.kind === "face-cylinder") {
    if (face.kind !== "cylinder") return Infinity;
    const align = 1 - Math.abs(dot(pick.dir, face.dir));
    return align * 50 + Math.abs(pick.r - face.r) + lineDist(pick.axis, face.axis, face.dir);
  }
  return Infinity;
}

export const MATCH_TOLERANCE = 0.5;

// Match every parsed pick against the viewer's entities. `edges` and
// `faces` are arrays of records as above; faces may be omitted. Points
// always "match" (they render as markers). Returns one result per pick:
// { pick, type: "edge"|"face"|"point"|null, index?, score? }.
export function matchPicks(picks, edges, faces) {
  return picks.map((pick) => {
    if (pick.kind === "point") return { pick, type: "point" };
    if (pick.kind === "face-plane" || pick.kind === "face-cylinder") {
      let best = -1, bestScore = Infinity;
      (faces || []).forEach((f, i) => {
        const s = f ? scoreFace(pick, f) : Infinity;
        if (s < bestScore) { bestScore = s; best = i; }
      });
      return bestScore <= MATCH_TOLERANCE
        ? { pick, type: "face", index: best, score: bestScore }
        : { pick, type: null };
    }
    let best = -1, bestScore = Infinity;
    (edges || []).forEach((e, i) => {
      const s = scoreEdge(pick, e);
      if (s < bestScore) { bestScore = s; best = i; }
    });
    return bestScore <= MATCH_TOLERANCE
      ? { pick, type: "edge", index: best, score: bestScore }
      : { pick, type: null };
  });
}
