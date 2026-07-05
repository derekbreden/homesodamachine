/**
 * PCB editor routes — dev-server only. Provides board listing, TSX parsing,
 * and position write-back so the drag-to-reposition editor can read and update
 * component placements directly in the board source files.
 */
import fs from "fs";
import path from "path";

const PCB_DIR = "pcb";

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

// A Jst's orientation isn't a free rotation — it's `side`, the board edge its
// opening faces, from which carrier_parts.tsx derives the wafer's real (per-part)
// angle. The editor rotates a Jst by cycling `side`; these map a side to its
// opening-facing angle (matching the helper's `wantAngle`), so a generic +90°
// rotate steps to the next edge and wraps: S→E→N→W→S.
const JST_SIDE_ANGLE = { E: 0, N: 90, W: 180, S: 270 };
const JST_ANGLE_SIDE = { 0: "E", 90: "N", 180: "W", 270: "S" };

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

function parseBoardTsx(tsx) {
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

    // Pin count for connectors
    let count = null;
    const cntMatch = body.match(/\bcount=\{(\d+)\}/);
    if (cntMatch) count = parseInt(cntMatch[1], 10);

    // Orientation. A Jst has no free rotation — it faces a board edge (`side`),
    // and carrier_parts.tsx derives the wafer's real angle from that. Report the
    // side's opening-facing angle, so the editor's model matches the board and a
    // 90° rotate steps to the next edge. Everything else reads its rotation literal.
    let side = null, rot = 0;
    if (tag === "Jst") {
      const sideMatch = body.match(/\bside="([NSEW])"/);
      if (sideMatch) side = sideMatch[1];
      if (side != null && JST_SIDE_ANGLE[side] != null) rot = JST_SIDE_ANGLE[side];
    } else {
      const rotMatch = body.match(/(?:pcbRotation|rot)=\{(-?\d+)\}/);
      if (rotMatch) rot = parseInt(rotMatch[1], 10);
    }

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
      rot, side, posKind, cat, size, footprint, count, extra,
    });
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

// Set a component's rotation in the source TSX. A Jst is special: it has no free
// rotation — its pose is `side` (the board edge it faces) — so a rotate rewrites
// `side`, mapping the requested angle to the matching edge. Everything else edits
// a rotation literal: pcbRotation, else the Cap `rot` shorthand; when a component
// carries none yet (e.g. a bare `{...at()}`) one is inserted before the `/>` (the
// Cap wrapper takes `rot`; builtins and ChipProps imports take `pcbRotation`).
// Matched by ref alone, so it composes after a position rewrite of the same line.
export function updateRotationInTsx(tsx, ref, newRot) {
  const r = ((Math.round(Number(newRot)) % 360) + 360) % 360;
  const lines = tsx.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.includes(`name="${ref}"`) && !line.includes(`name={${ref}}`)) continue;

    const tagM = line.match(/<\s*(\w+)/);
    const tag = tagM ? tagM[1] : "";

    // A Jst faces a board edge; its pose is `side`, not a rotation literal. Map the
    // requested angle to the edge whose opening points that way and rewrite `side`.
    if (tag === "Jst") {
      const side = JST_ANGLE_SIDE[r];
      if (!side) throw new Error(`Jst ${ref}: ${r}° is not a cardinal edge`);
      if (!/\bside="[NSEW]"/.test(line)) throw new Error(`Jst ${ref} has no side= to rotate`);
      lines[i] = line.replace(/\bside="[NSEW]"/, `side="${side}"`);
      return lines.join("\n");
    }

    if (/\bpcbRotation=\{-?\d+\}/.test(line)) {
      lines[i] = line.replace(/\bpcbRotation=\{-?\d+\}/, `pcbRotation={${r}}`);
      return lines.join("\n");
    }
    if (/\brot=\{-?\d+\}/.test(line)) {
      lines[i] = line.replace(/\brot=\{-?\d+\}/, `rot={${r}}`);
      return lines.join("\n");
    }

    const prop = tag === "Cap" ? "rot" : "pcbRotation";
    const tail = line.match(/\s*\/>\s*$/);
    if (tail) {
      lines[i] = line.slice(0, tail.index) + ` ${prop}={${r}} />`;
      return lines.join("\n");
    }
  }

  throw new Error(`Could not find component ${ref} to set rotation in TSX`);
}

// ---- Route mounting (dev-server only) -------------------------------------

// Locate a board's .tsx by name under the PCB root, restricted to boards that
// also have a rendered overlay (so the viewer can actually show them). Shared by
// the parse and write-back routes.
function findBoardTsx(pcbRoot, name) {
  let found = null;
  (function walk(dir) {
    if (found) return;
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (e.name.startsWith(".") || e.name === "node_modules") continue;
      const full = path.join(dir, e.name);
      if (e.isDirectory()) { walk(full); continue; }
      if (e.name === `${name}.tsx` && fs.existsSync(path.join(dir, "out", `${name}.overlay.svg`))) {
        found = full;
        return;
      }
    }
  })(pcbRoot);
  return found;
}

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

    const tsxPath = findBoardTsx(pcbRoot, name);
    if (!tsxPath) return res.status(404).json({ error: `Board not found: ${name}` });

    const tsx = fs.readFileSync(tsxPath, "utf-8");
    const { components, silk, outline } = parseBoardTsx(tsx);
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

    const tsxPath = findBoardTsx(pcbRoot, name);
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

  // Set a component's rotation (degrees) in the source TSX. Rotation is matched
  // by ref alone, so it composes with a position rewrite of the same line — a
  // group rotate moves and re-orients each part in two write-backs.
  app.post("/api/pcb-editor/board/:name/update-rotation", (req, res) => {
    const { name } = req.params;
    if (!/^[a-zA-Z0-9_-]+$/.test(name)) return res.status(400).json({ error: "Invalid board name" });
    const { ref, rot } = req.body || {};
    if (!ref || rot == null) {
      return res.status(400).json({ error: "Missing required fields: ref, rot" });
    }

    const tsxPath = findBoardTsx(pcbRoot, name);
    if (!tsxPath) return res.status(404).json({ error: `Board not found: ${name}` });

    const tsx = fs.readFileSync(tsxPath, "utf-8");
    let updated;
    try {
      updated = updateRotationInTsx(tsx, ref, rot);
    } catch (e) {
      return res.status(400).json({ error: e.message });
    }

    fs.writeFileSync(tsxPath, updated, "utf-8");
    res.json({ ok: true, ref, rot });
  });
}
