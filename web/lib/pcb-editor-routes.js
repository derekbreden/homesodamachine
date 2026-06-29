/**
 * PCB editor routes — dev-server only. Provides board listing, TSX parsing,
 * and position write-back so the drag-to-reposition editor can read and update
 * component placements directly in the board source files.
 */
import fs from "fs";
import path from "path";

const PCB_DIR = "pcb";

// ---- Imported constant resolver --------------------------------------------

// Resolve simple exported const values from imported local files so that
// expressions like labels={[...ulnOUT].reverse()} can be expanded.
function resolveImportedConstants(tsx, boardDir) {
  const consts = {};

  // Parse import { A, B } from "./file" declarations for local files.
  const importRe = /import\s+\{([^}]+)\}\s+from\s+"(\.\/[^"]+)"/g;
  for (const m of tsx.matchAll(importRe)) {
    const names = m[1].split(",").map((s) => {
      const trim = s.trim();
      // Handle "as" renames: "Foo as Bar"
      const asMatch = trim.match(/^(\w+)\s+as\s+(\w+)$/);
      return asMatch ? { src: asMatch[1], alias: asMatch[2] } : { src: trim, alias: trim };
    });
    const filePath = path.join(boardDir, m[2]);
    // Try .tsx, .ts, then bare (for index files or files without explicit ext).
    const tryPaths = filePath.endsWith(".tsx") || filePath.endsWith(".ts")
      ? [filePath]
      : [filePath + ".tsx", filePath + ".ts", filePath];
    let fileSrc = null;
    for (const fp of tryPaths) {
      try { fileSrc = fs.readFileSync(fp, "utf-8"); break; } catch {}
    }
    if (!fileSrc) continue;

    for (const { src, alias } of names) {
      // export const Foo = [...]
      const arrRe = new RegExp(`export\\s+const\\s+${src.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*=\\s*\\[([^\\]]*)\\]`);
      const arrMatch = fileSrc.match(arrRe);
      if (arrMatch) {
        const items = [...arrMatch[1].matchAll(/"([^"]*)"/g)].map((x) => x[1]);
        consts[alias] = items;
        continue;
      }
      // export const Foo = "..."
      const strRe = new RegExp(`export\\s+const\\s+${src.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*=\\s*"([^"]*)"`);
      const strMatch = fileSrc.match(strRe);
      if (strMatch) {
        consts[alias] = strMatch[1];
      }
    }
  }

  return consts;
}

// ---- TSX parser -----------------------------------------------------------

function findSelfClosingElements(tsx) {
  const elements = [];
  let i = 0;
  while (i < tsx.length) {
    const lt = tsx.indexOf("<", i);
    if (lt === -1) break;
    if (tsx[lt + 1] === "/" || tsx[lt + 1] === "!") {
      i = lt + 1;
      continue;
    }
    const afterLt = tsx.slice(lt + 1);
    const tagMatch = afterLt.match(/^(\w+)/);
    if (!tagMatch) {
      i = lt + 1;
      continue;
    }
    const tagName = tagMatch[1];
    let bodyStart = lt + 1 + tagMatch[0].length;
    // Walk the tag's attributes tracking brace depth and quoted strings to find
    // where it ends. A `/>` at depth 0 closes a self-closing element (what we
    // collect); a bare `>` at depth 0 closes a NON-self-closing opening tag
    // (e.g. <board ...>) — we must stop there and resume scanning its children,
    // or the first self-closing child (BT1, the first component on the board)
    // gets swallowed into this tag's body and is never parsed. Quote tracking
    // keeps a `>` inside an attribute string (e.g. a trace's from=".U6 > .VBAT")
    // from being mistaken for the tag end.
    let braceDepth = 0;
    let quote = null;
    let end = -1, openEnd = -1;
    for (let j = bodyStart; j < tsx.length - 1; j++) {
      const c = tsx[j];
      if (quote) { if (c === quote) quote = null; continue; }
      if (c === '"' || c === "'") { quote = c; continue; }
      if (c === "{") { braceDepth++; continue; }
      if (c === "}") { braceDepth--; continue; }
      if (braceDepth === 0) {
        if (c === "/" && tsx[j + 1] === ">") { end = j; break; }
        if (c === ">") { openEnd = j; break; }
      }
    }
    if (end === -1) {
      // Non-self-closing: skip past an opening tag's `>` so its children get
      // scanned; otherwise (never terminated) inch forward and retry.
      i = openEnd !== -1 ? openEnd + 1 : lt + 1;
      continue;
    }
    const body = tsx.slice(bodyStart, end).trim();
    elements.push({ tag: tagName, body });
    i = end + 2;
  }
  return elements;
}

const SKIP_TAGS = new Set([
  "trace", "copperpour", "board",
]);

const SHAPES = {
  Wroom:              { cat: "module",       size: { w: 18, h: 25.5 } },
  Ds3231Smd:          { cat: "chip",         size: { w: 7.5, h: 10.3 } },
  Uln2803:            { cat: "chip",         size: { w: 7.5, h: 11.7 } },
  Mcp23017:           { cat: "chip",         size: { w: 7.5, h: 18.0 } },
  Thvd1426:           { cat: "chip",         size: { w: 3.9, h: 4.9 } },
  Sm712:              { cat: "chip",         size: { w: 2.8, h: 2.9 } },
  Ams1117_33:         { cat: "chip",         size: { w: 3.5, h: 6.7 } },
  S8050:              { cat: "chip",         size: { w: 2.8, h: 2.9 } },
  CoinCell:           { cat: "coincell",     size: { r: 10.0 } },
  MLT_5020:           { cat: "buzzer",       size: { r: 6.0 } },
  NXB_25V470_10_12_5: { cat: "electrolytic", size: { r: 6.25 } },
};

const FP_SIZES = {
  "0805": { w: 2.0, h: 1.25 },
  "0603": { w: 1.6, h: 0.8 },
  "0402": { w: 1.0, h: 0.5 },
  "1206": { w: 3.2, h: 1.6 },
};

function componentShape(tag, footprint, count) {
  if (tag === "Jst" || tag === "pinheader") {
    const n = Math.max(count || 1, 1);
    return { cat: "connector", size: { w: n * 2.5 + 3, h: 6 } };
  }
  const s = SHAPES[tag];
  if (s) return { ...s };
  if (tag === "capacitor" || tag === "resistor") {
    const fp = FP_SIZES[footprint] || { w: 2.0, h: 1.25 };
    return { cat: tag === "capacitor" ? "capacitor" : "resistor", size: fp };
  }
  return { cat: "unknown", size: { w: 5, h: 5 } };
}

// Jst connector silk generation — replicates the layout math in carrier_parts.tsx
// so the editor can draw the fence + labels without expanding the component.
function jstSilk({ x, y, count, labels, rot, name, label }) {
  const silk = [];
  const vertical = rot % 180 !== 0;
  const pitch = 2.5, padR = 0.825;
  const bigHalf = 0.42, smHalf = 0.24;
  const G = 0.45, M = 0.6;
  const perpDir = vertical ? -1 : 1;
  const bigOff = padR + G + bigHalf;
  const labelOff = padR + G + smHalf;
  const refOff = labelOff + smHalf + G + smHalf;
  const uc = ((bigOff + bigHalf) - (refOff + smHalf)) / 2;
  const dep = (bigOff + bigHalf) + (refOff + smHalf) + 2 * M + 0.2;
  const len = (count - 1) * pitch + 2 * (padR + M + 0.1);
  const [w, h] = vertical ? [dep, len] : [len, dep];
  const P = (u, v) => (vertical ? [perpDir * u, v] : [v, perpDir * u]);
  const [bdx, bdy] = P(bigOff, 0);
  const [rdx, rdy] = P(-refOff, 0);
  const [fdx, fdy] = P(uc, 0);

  // Fence rectangle
  silk.push({
    kind: "fence",
    x: x + fdx, y: y + fdy, w, h, rot: 0,
    strokeWidth: 0.2,
  });

  // Pin labels
  for (let i = 0; i < labels.length; i++) {
    const [dx, dy] = P(-labelOff, (i - (count - 1) / 2) * pitch);
    silk.push({
      kind: "text", text: labels[i], fontSize: 0.8,
      x: x + dx, y: y + dy, rot,
      anchor: null,
    });
  }

  // Function label
  silk.push({
    kind: "text", text: label, fontSize: 1.4,
    x: x + bdx, y: y + bdy, rot,
    anchor: null,
  });

  // Ref-des label
  silk.push({
    kind: "text", text: name, fontSize: 0.8,
    x: x + rdx, y: y + rdy, rot,
    anchor: null,
  });

  return silk;
}

function parseBoardTsx(tsx, consts) {
  const elements = findSelfClosingElements(tsx);
  const components = [];
  const silk = [];

  // Board outline from <board outline={[...]}>
  const boardMatch = tsx.match(/<board\s[^>]*\boutline=\{\[([^\]]*)\]/);
  let outline = null;
  if (boardMatch) {
    const pts = [...boardMatch[1].matchAll(/\{\s*x:\s*(-?[\d.]+)\s*,\s*y:\s*(-?[\d.]+)\s*\}/g)];
    outline = pts.map((m) => ({ x: parseFloat(m[1]), y: parseFloat(m[2]) }));
  }

  for (const { tag, body } of elements) {
    if (SKIP_TAGS.has(tag)) continue;

    // Standalone silkscreen text
    if (tag === "silkscreentext") {
      const textMatch = body.match(/\btext=\{?`([^`]*)`\}?|\btext="([^"]*)"|\btext=\{([^}]*)\}/);
      const px = body.match(/\bpcbX=\{(-?[\d.]+)\}/);
      const py = body.match(/\bpcbY=\{(-?[\d.]+)\}/);
      const fs = body.match(/\bfontSize=["{]([^"}]+)["}]/);
      const rotMatch = body.match(/\bpcbRotation=\{(-?\d+)\}/);
      const anchorMatch = body.match(/\banchorAlignment=["{]([^"}]+)["}]/);
      if (textMatch && px && py) {
        const textVal = (textMatch[1] || textMatch[2] || textMatch[3] || "").replace(/^"(.*)"$/, "$1");
        silk.push({
          kind: "text",
          text: textVal,
          fontSize: fs ? parseFloat(fs[1]) : 1,
          x: parseFloat(px[1]),
          y: parseFloat(py[1]),
          rot: rotMatch ? parseInt(rotMatch[1], 10) : 0,
          anchor: anchorMatch ? anchorMatch[1] : null,
        });
      }
      continue;
    }

    // Standalone silkscreen paths
    if (tag === "silkscreenpath") {
      const swMatch = body.match(/strokeWidth=["{]([^"}]+)["}]/);
      const routeMatch = body.match(/route=\{\[([^\]]+)\]/);
      if (routeMatch) {
        const pts = [...routeMatch[1].matchAll(/\{\s*x:\s*(-?[\d.]+)\s*,\s*y:\s*(-?[\d.]+)\s*\}/g)];
        if (pts.length >= 2) {
          silk.push({
            kind: "path",
            strokeWidth: swMatch ? parseFloat(swMatch[1]) : 0.15,
            points: pts.map((m) => ({ x: parseFloat(m[1]), y: parseFloat(m[2]) })),
          });
        }
      }
      continue;
    }

    const nameMatch = body.match(/name=["{]([^"}]+)["}]/);
    if (!nameMatch) continue;
    const ref = nameMatch[1];

    let x = null, y = null, posKind = null;

    // Spread at() pattern
    const atMatch = body.match(/\.\.\.at\((-?[\d.]+),\s*(-?[\d.]+)\)/);
    if (atMatch) {
      x = parseFloat(atMatch[1]);
      y = parseFloat(atMatch[2]);
      posKind = "at";
    }

    // pcbX/pcbY pattern
    if (x === null) {
      const px = body.match(/\bpcbX=\{(-?[\d.]+)\}/);
      const py = body.match(/\bpcbY=\{(-?[\d.]+)\}/);
      if (px && py) { x = parseFloat(px[1]); y = parseFloat(py[1]); posKind = "pcb"; }
    }

    // x/y pattern
    if (x === null) {
      const xm = body.match(/\bx=\{(-?[\d.]+)\}/);
      const ym = body.match(/\by=\{(-?[\d.]+)\}/);
      if (xm && ym) { x = parseFloat(xm[1]); y = parseFloat(ym[1]); posKind = "x"; }
    }

    if (x === null) continue;

    // Rotation
    let rot = 0;
    const rotMatch = body.match(/(?:pcbRotation|rot)=\{(-?\d+)\}/);
    if (rotMatch) rot = parseInt(rotMatch[1], 10);

    // Pin count for connectors
    let count = null;
    const cntMatch = body.match(/\bcount=\{(\d+)\}/);
    if (cntMatch) count = parseInt(cntMatch[1], 10);

    // Connector labels
    let labels = null, jstLabel = null;
    const labelsMatch = body.match(/\blabels=\{(\[[^\]]*\])(?:\.[^}\s]+)?\}/) || body.match(/\blabels=\{\[([^\]]*)\]\}/);
    if (labelsMatch) {
      const raw = labelsMatch[1] || labelsMatch[2] || "";
      labels = [...raw.matchAll(/"([^"]*)"/g)].map((m) => m[1]);
    }
    // Fall back to resolving imported-constant spreads, e.g. [...ulnOUT].reverse()
    if ((!labels || !labels.length) && consts && count) {
      const spreadMatch = body.match(/labels=\{\.\.\.(\w+)\}/) || body.match(/labels=\{\[\.\.\.(\w+)\]\.reverse\(\)\}/);
      if (spreadMatch && consts[spreadMatch[1]]) {
        const arr = consts[spreadMatch[1]];
        labels = body.includes(".reverse()") ? [...arr].reverse() : [...arr];
      }
    }
    const labelMatch = body.match(/\blabel=["{]([^"}]+)["}]/);
    if (labelMatch) jstLabel = labelMatch[1];

    // Footprint for passives
    let footprint = null;
    const fpMatch = body.match(/footprint=["{]([^"}]+)["}]/);
    if (fpMatch) footprint = fpMatch[1];

    // Extra descriptor for passives
    let extra = null;
    const capMatch = body.match(/capacitance=["{]([^"}]+)["}]/);
    if (capMatch) extra = capMatch[1];
    const resMatch = body.match(/resistance=["{]([^"}]+)["}]/);
    if (resMatch) extra = resMatch[1];

    const { cat, size } = componentShape(tag, footprint, count);

    components.push({
      tag, ref, x: Math.round(x * 100) / 100, y: Math.round(y * 100) / 100,
      rot, posKind, cat, size, footprint, count, extra,
    });

    // Generate silk for Jst connectors
    if ((tag === "Jst" || tag === "pinheader") && jstLabel && count) {
      silk.push(...jstSilk({ x, y, count, labels: labels || [], rot, name: ref, label: jstLabel }));
    }
  }

  return { components, silk, outline };
}

// ---- Write-back ------------------------------------------------------------

function fmtNum(n) {
  const s = Number(n).toFixed(2);
  return s.replace(/\.00$/, "").replace(/(\.[0-9])0$/, "$1");
}

// Match a source literal against the client's old value by NUMBER, not string —
// the parser rounds positions to 2 decimals (so a source `-25.0` arrives as
// `-25`, `15.420` as `15.42`), and an exact-string match would miss those. The
// 0.01 window comfortably covers that rounding while staying well under the
// snap grid, so it can't collide with a different placement.
function numClose(a, b) {
  return Math.abs(Number(a) - Number(b)) < 0.01;
}

export function updatePositionInTsx(tsx, ref, oldX, oldY, newX, newY) {
  const newXS = fmtNum(newX);
  const newYS = fmtNum(newY);

  const lines = tsx.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.includes(`name="${ref}"`) && !line.includes(`name={${ref}}`)) continue;

    // {...at(x, y)} spread
    const at = line.match(/\{\.\.\.at\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)/);
    if (at && numClose(at[1], oldX) && numClose(at[2], oldY)) {
      lines[i] = line.slice(0, at.index) + `{...at(${newXS}, ${newYS})` + line.slice(at.index + at[0].length);
      return lines.join("\n");
    }

    // pcbX={x} pcbY={y}
    const px = line.match(/\bpcbX=\{(-?[\d.]+)\}/);
    const py = line.match(/\bpcbY=\{(-?[\d.]+)\}/);
    if (px && py && numClose(px[1], oldX) && numClose(py[1], oldY)) {
      lines[i] = line
        .replace(/\bpcbX=\{-?[\d.]+\}/, `pcbX={${newXS}}`)
        .replace(/\bpcbY=\{-?[\d.]+\}/, `pcbY={${newYS}}`);
      return lines.join("\n");
    }

    // x={x} y={y} direct
    const xm = line.match(/\bx=\{(-?[\d.]+)\}/);
    const ym = line.match(/\by=\{(-?[\d.]+)\}/);
    if (xm && ym && numClose(xm[1], oldX) && numClose(ym[1], oldY)) {
      lines[i] = line
        .replace(/\bx=\{-?[\d.]+\}/, `x={${newXS}}`)
        .replace(/\by=\{-?[\d.]+\}/, `y={${newYS}}`);
      return lines.join("\n");
    }
  }

  throw new Error(
    `Could not find position for ${ref} at (${oldX}, ${oldY}) in TSX`,
  );
}

// ---- Route mounting (dev-server only) -------------------------------------

export function mountPcbEditorRoutes(app, hardwareDir) {
  const pcbRoot = path.join(hardwareDir, PCB_DIR);

  // List boards that have both a .tsx source and rendered views.
  app.get("/api/pcb-editor/boards", (_req, res) => {
    const boards = [];
    function walk(dir) {
      let entries;
      try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
      for (const e of entries) {
        if (e.name.startsWith(".") || e.name === "node_modules") continue;
        const full = path.join(dir, e.name);
        if (e.isDirectory()) { walk(full); continue; }
        if (!e.name.endsWith(".tsx")) continue;
        const name = e.name.replace(/\.tsx$/, "");
        if (!fs.existsSync(path.join(dir, "out", `${name}.overlay.svg`))) continue;
        const relDir = path.relative(pcbRoot, dir);
        boards.push({
          name,
          dir: relDir,
          tsxPath: path.join(dir, e.name),
        });
      }
    }
    walk(pcbRoot);
    boards.sort((a, b) => a.name.localeCompare(b.name));
    res.json(boards);
  });

  // Parse and return component data for a board.
  app.get("/api/pcb-editor/board/:name", (req, res) => {
    const { name } = req.params;
    if (!/^[a-zA-Z0-9_-]+$/.test(name)) return res.status(400).json({ error: "Invalid board name" });

    // Find the TSX file
    let tsxPath = null;
    function find(dir) {
      if (tsxPath) return;
      let entries;
      try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
      for (const e of entries) {
        if (e.name.startsWith(".") || e.name === "node_modules") continue;
        const full = path.join(dir, e.name);
        if (e.isDirectory()) { find(full); continue; }
        if (e.name === `${name}.tsx` && fs.existsSync(path.join(dir, "out", `${name}.overlay.svg`))) {
          tsxPath = full;
          return;
        }
      }
    }
    find(pcbRoot);
    if (!tsxPath) return res.status(404).json({ error: `Board not found: ${name}` });

    const tsx = fs.readFileSync(tsxPath, "utf-8");
    const consts = resolveImportedConstants(tsx, path.dirname(tsxPath));
    const { components, silk, outline } = parseBoardTsx(tsx, consts);
    res.json({
      name,
      tsxPath: path.relative(hardwareDir, tsxPath),
      components,
      silk,
      outline,
      rawTsx: tsx,
    });
  });

  // Update a component's position in the source TSX.
  app.post("/api/pcb-editor/board/:name/update-position", (req, res) => {
    const { name } = req.params;
    if (!/^[a-zA-Z0-9_-]+$/.test(name)) return res.status(400).json({ error: "Invalid board name" });
    const { ref, oldX, oldY, newX, newY } = req.body || {};
    if (!ref || oldX == null || oldY == null || newX == null || newY == null) {
      return res.status(400).json({ error: "Missing required fields: ref, oldX, oldY, newX, newY" });
    }

    // Find the TSX file
    let tsxPath = null;
    function find(dir) {
      if (tsxPath) return;
      let entries;
      try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
      for (const e of entries) {
        if (e.name.startsWith(".") || e.name === "node_modules") continue;
        const full = path.join(dir, e.name);
        if (e.isDirectory()) { find(full); continue; }
        if (e.name === `${name}.tsx` && fs.existsSync(path.join(dir, "out", `${name}.overlay.svg`))) {
          tsxPath = full;
          return;
        }
      }
    }
    find(pcbRoot);
    if (!tsxPath) return res.status(404).json({ error: `Board not found: ${name}` });

    const tsx = fs.readFileSync(tsxPath, "utf-8");
    let updated;
    try {
      updated = updatePositionInTsx(tsx, ref, oldX, oldY, newX, newY);
    } catch (e) {
      return res.status(400).json({ error: e.message });
    }

    fs.writeFileSync(tsxPath, updated, "utf-8");
    res.json({ ok: true, ref, x: newX, y: newY });
  });
}
