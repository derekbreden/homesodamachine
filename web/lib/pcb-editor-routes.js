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
    let braceDepth = 0;
    let end = -1;
    for (let j = bodyStart; j < tsx.length - 1; j++) {
      const c = tsx[j];
      if (c === "{") braceDepth++;
      else if (c === "}") braceDepth--;
      else if (c === "/" && tsx[j + 1] === ">" && braceDepth === 0) {
        end = j;
        break;
      }
    }
    if (end === -1) {
      i = lt + 1;
      continue;
    }
    const body = tsx.slice(bodyStart, end).trim();
    elements.push({ tag: tagName, body });
    i = end + 2;
  }
  return elements;
}

const SKIP_TAGS = new Set([
  "trace", "copperpour", "silkscreentext", "silkscreenpath", "Outline", "board",
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

function parseBoardTsx(tsx) {
  const elements = findSelfClosingElements(tsx);
  const components = [];

  // Board outline from <board outline={[...]}>
  const boardMatch = tsx.match(/<board\s[^>]*\boutline=\{\[([^\]]*)\]/);
  let outline = null;
  if (boardMatch) {
    const pts = [...boardMatch[1].matchAll(/\{\s*x:\s*(-?[\d.]+)\s*,\s*y:\s*(-?[\d.]+)\s*\}/g)];
    outline = pts.map((m) => ({ x: parseFloat(m[1]), y: parseFloat(m[2]) }));
  }

  for (const { tag, body } of elements) {
    if (SKIP_TAGS.has(tag)) continue;

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

    // Footprint for passives
    let footprint = null;
    const fpMatch = body.match(/footprint=["{]([^"}]+)["}]/);
    if (fpMatch) footprint = fpMatch[1];

    // Pin count for connectors
    let count = null;
    const cntMatch = body.match(/\bcount=\{(\d+)\}/);
    if (cntMatch) count = parseInt(cntMatch[1], 10);

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
  }

  return { components, outline };
}

// ---- Write-back ------------------------------------------------------------

function fmtNum(n) {
  const s = Number(n).toFixed(2);
  return s.replace(/\.00$/, "").replace(/(\.[0-9])0$/, "$1");
}

function esc(s) {
  return String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function updatePositionInTsx(tsx, ref, oldX, oldY, newX, newY) {
  const newXS = fmtNum(newX);
  const newYS = fmtNum(newY);
  const oldXS = String(oldX);
  const oldYS = String(oldY);

  const lines = tsx.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.includes(`name="${ref}"`) && !line.includes(`name={${ref}}`)) continue;

    // at() spread
    if (line.includes("{...at(")) {
      const atRe = new RegExp(`(\\{\.\.\.at\\()${esc(oldXS)}, ${esc(oldYS)}(\\))`);
      if (atRe.test(line)) {
        lines[i] = line.replace(atRe, `$1${newXS}, ${newYS}$2`);
        return lines.join("\n");
      }
      // Try with more/less whitespace
      const atRe2 = new RegExp(`(\\{\.\.\.at\\()${esc(oldXS)},\\s*${esc(oldYS)}(\\))`);
      if (atRe2.test(line)) {
        lines[i] = line.replace(atRe2, `$1${newXS}, ${newYS}$2`);
        return lines.join("\n");
      }
    }

    // pcbX/pcbY
    if (line.includes("pcbX={") && line.includes("pcbY={")) {
      const pxRe = new RegExp(`\\bpcbX=\\{${esc(oldXS)}\\}`);
      const pyRe = new RegExp(`\\bpcbY=\\{${esc(oldYS)}\\}`);
      if (pxRe.test(line) && pyRe.test(line)) {
        lines[i] = line.replace(pxRe, `pcbX={${newXS}}`).replace(pyRe, `pcbY={${newYS}}`);
        return lines.join("\n");
      }
    }

    // x/y direct
    if (line.includes("x={") && line.includes("y={")) {
      const xRe = new RegExp(`\\bx=\\{${esc(oldXS)}\\}`);
      const yRe = new RegExp(`\\by=\\{${esc(oldYS)}\\}`);
      if (xRe.test(line) && yRe.test(line)) {
        lines[i] = line.replace(xRe, `x={${newXS}}`).replace(yRe, `y={${newYS}}`);
        return lines.join("\n");
      }
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
    const { components, outline } = parseBoardTsx(tsx);
    res.json({
      name,
      tsxPath: path.relative(hardwareDir, tsxPath),
      components,
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
