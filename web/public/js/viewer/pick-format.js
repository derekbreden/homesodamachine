// Pick text format — the shared language between the edge picker's copy
// blobs, the find box's paste-to-highlight, and the agent on the other
// side of the clipboard. One module owns formatting, parsing, and match
// scoring so a blob copied out of the viewer (or composed by the agent
// from CAD coordinates) round-trips back into a highlighted entity.
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
// lines are recognized by content. Returns { picks, files } where picks
// carry a `kind` and a `line` (the trimmed source text for status UI).
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

// Copy-all `file:` lines are repo-prefixed (hardware/… or the lite
// edition root); the viewer's own paths are edition-root-relative.
export function pickFileToViewerPath(file) {
  return String(file).trim().replace(/^(pie-in-the-sky\/lite|hardware)\//, "");
}

export function parsePicks(text) {
  const picks = [];
  const files = [];
  for (const raw of String(text || "").split("\n")) {
    const line = raw.trim();
    if (!line) continue;
    // strip one leading "label:" (file:, solid:, edge:, faceA:, click:, …)
    const m = line.match(/^([A-Za-z][\w-]*)\s*:\s*(.*)$/);
    const label = m ? m[1].toLowerCase() : null;
    const body = m ? m[2] : line;

    if (label === "file") { files.push(body.trim()); continue; }
    if (label === "solid") continue;

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
    for (const p of triples(body)) picks.push({ kind: "point", p, line });
  }
  return { picks, files };
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
