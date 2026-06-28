/**
 * PCB Editor — drag-and-drop component positioning for a tscircuit board.
 *
 * Renders a simplified view of the board (component outlines + pins + labels)
 * at 15 SVG units per board millimetre, with Y flipped so +Y is up. PanZoom
 * handles pan/zoom; drag on a component shape writes its new position back
 * to the .tsx source file via the editor API.
 */

// Per-mm SVG scale (so a 128mm board → 1920 SVG units wide).
const U = 15;

// ---- SVG helpers ----------------------------------------------------------

const SVGNS = "http://www.w3.org/2000/svg";

function svgel(tag, attrs) {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v != null) el.setAttribute(k, String(v));
  }
  return el;
}

function svgXY(pt) {
  return { x: pt.x * U, y: -pt.y * U };
}

// ---- Component shape builders ---------------------------------------------

function buildOutline(outline) {
  if (!outline || outline.length < 2) return [];
  const d =
    "M" +
    outline
      .map((p) => {
        const { x, y } = svgXY(p);
        return `${x},${y}`;
      })
      .join("L") +
    "Z";
  return [svgel("path", { class: "board-outline", d })];
}

// ---- Silk layer (fences + text + paths) ------------------------------------

function buildSilk(silkItems) {
  if (!silkItems || !silkItems.length) return [];
  const els = [];

  for (const s of silkItems) {
    if (s.kind === "fence") {
      const { x, y } = svgXY(s);
      const w = s.w * U, h = s.h * U;
      els.push(
        svgel("rect", {
          class: "silk-fence",
          x: x - w / 2, y: y - h / 2, width: w, height: h,
          fill: "none", "stroke-width": s.strokeWidth * U,
          style: "stroke: var(--silk);",
        }),
      );
    } else if (s.kind === "text") {
      const { x: sx, y: sy } = svgXY(s);
      const fontSize = s.fontSize * U;
      const el = svgel("text", {
        class: "silk-text",
        x: sx, y: sy,
        "font-size": fontSize,
        "font-family": "monospace",
        "text-anchor": s.anchor === "center" ? "middle" : (s.anchor || "start"),
        style: "fill: var(--silk);",
      });
      el.textContent = s.text;
      if (s.rot && s.rot % 360 !== 0) {
        el.setAttribute("transform", `translate(${sx},${sy}) rotate(${-s.rot})`);
        el.setAttribute("x", 0);
        el.setAttribute("y", 0);
      }
      els.push(el);
    } else if (s.kind === "path") {
      if (s.points.length >= 2) {
        const d =
          "M" +
          s.points
            .map((p) => {
              const { x, y } = svgXY(p);
              return `${x},${y}`;
            })
            .join("L");
        els.push(
          svgel("path", {
            class: "silk-path",
            d,
            fill: "none",
            "stroke-width": s.strokeWidth * U,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            style: "stroke: var(--silk);",
          }),
        );
      }
    }
  }

  return els;
}

function buildGrid(bounds) {
  const els = [];
  const stepMinor = 1, stepMajor = 5;
  const xMin = Math.floor(bounds.minX / stepMinor) * stepMinor;
  const xMax = Math.ceil(bounds.maxX / stepMinor) * stepMinor;
  const yMin = Math.floor(bounds.minY / stepMinor) * stepMinor;
  const yMax = Math.ceil(bounds.maxY / stepMinor) * stepMinor;

  for (let bx = xMin; bx <= xMax; bx += stepMinor) {
    const sx = bx * U;
    els.push(
      svgel("line", {
        class: bx % stepMajor === 0 ? "grid-line major" : "grid-line",
        x1: sx, y1: -yMax * U, x2: sx, y2: -yMin * U,
      }),
    );
  }
  for (let by = yMin; by <= yMax; by += stepMinor) {
    const sy = -by * U;
    els.push(
      svgel("line", {
        class: by % stepMajor === 0 ? "grid-line major" : "grid-line",
        x1: xMin * U, y1: sy, x2: xMax * U, y2: sy,
      }),
    );
  }
  return els;
}

// Pin positions for common SOIC footprints (millimetres in chip-local space).
const SOIC_PIN_SPACING = {
  soic8: 1.27,
  "soic16_w7.5mm_p1.27mm": 1.27,
  "soic18_w7.5mm_p1.27mm": 1.27,
  "soic28_w7.5mm_p1.27mm": 1.27,
};
function pinCountForFootprint(fp) {
  const m = /soic(\d+)/i.exec(fp || "");
  return m ? parseInt(m[1], 10) : 0;
}
function pinSpacingForFootprint(fp) {
  return SOIC_PIN_SPACING[fp] || 1.27;
}

function buildCompShape(comp) {
  const { x, y, rot } = comp;
  const svg = svgXY({ x, y });
  const { cat, size } = comp;
  const g = svgel("g", {
    class: `comp-shape cat-${cat}`,
    "data-ref": comp.ref,
    "data-x": String(x),
    "data-y": String(y),
    "data-rot": String(rot),
    "data-poskind": comp.posKind || "",
    transform: `translate(${svg.x},${svg.y}) rotate(${-rot})`,
  });

  const w = size.w * U, h = size.h * U;

  if (cat === "connector") {
    // Body rectangle with pin markers along the inside edge.
    g.appendChild(svgel("rect", {
      class: "shape", x: -w / 2, y: -h / 2, width: w, height: h, rx: 0.3 * U,
    }));
    // Pin dots along the connector's length (x-axis at rot=0).
    const pinPitch = 2.5 * U;
    const count = comp.count || 1;
    const dotR = 0.4 * U;
    for (let i = 0; i < count; i++) {
      const px = (i - (count - 1) / 2) * pinPitch;
      g.appendChild(svgel("circle", { class: "shape", cx: px, cy: 0, r: dotR }));
    }
    // Label: ref + connector name
    const lbl = comp.ref;
    g.appendChild(svgel("text", {
      class: "label", x: 0, y: h / 2 + 2.5 * U,
      "text-anchor": "middle", "font-size": 1.5 * U,
      textContent: lbl,
    }));
  } else if (cat === "chip") {
    // Body rectangle + pin ticks on left/right edges.
    g.appendChild(svgel("rect", {
      class: "shape", x: -w / 2, y: -h / 2, width: w, height: h, rx: 0.2 * U,
    }));
    // Pin ticks
    const sidePins = Math.floor(pinCountForFootprint(comp.footprint) / 2) || 0;
    if (sidePins > 0) {
      const pitch = (h - 0.8 * U) / Math.max(sidePins - 1, 1);
      const tickW = 0.6 * U, tickH = 0.2 * U;
      for (let i = 0; i < sidePins; i++) {
        const py = -h / 2 + 0.4 * U + i * pitch;
        g.appendChild(svgel("rect", { class: "shape", x: -w / 2 - tickW, y: py - tickH / 2, width: tickW, height: tickH }));
        g.appendChild(svgel("rect", { class: "shape", x: w / 2, y: py - tickH / 2, width: tickW, height: tickH }));
      }
    }
    // Pin-1 dot
    g.appendChild(svgel("circle", {
      class: "shape", cx: -w / 2 + 0.5 * U, cy: -h / 2 + 0.5 * U,
      r: 0.3 * U, fill: "#7ec8e3",
    }));
    // Label
    const lbl = comp.ref;
    g.appendChild(svgel("text", {
      class: "label", x: 0, y: h / 2 + 2.5 * U,
      "text-anchor": "middle", "font-size": 1.5 * U,
      textContent: lbl,
    }));
  } else if (cat === "module") {
    // Larger rectangle with castellated edge hints.
    g.appendChild(svgel("rect", {
      class: "shape", x: -w / 2, y: -h / 2, width: w, height: h, rx: 0.1 * U,
    }));
    // Castellations: small notches along the edges
    const notchR = 0.35 * U, gap = 1.8 * U;
    for (const side of [-1, 1]) {
      const sx = (side * w) / 2;
      for (let py = -h / 2 + gap; py < h / 2; py += gap) {
        g.appendChild(svgel("circle", {
          class: "shape", cx: sx, cy: py, r: notchR,
          fill: "#0d0d1a", stroke: "none",
        }));
      }
    }
    const lbl = comp.ref;
    g.appendChild(svgel("text", {
      class: "label", x: 0, y: h / 2 + 2.5 * U,
      "text-anchor": "middle", "font-size": 1.5 * U,
      textContent: lbl,
    }));
  } else if (cat === "capacitor" || cat === "resistor") {
    // Small rectangle.
    g.appendChild(svgel("rect", {
      class: "shape", x: -w / 2, y: -h / 2, width: w, height: h,
    }));
    // Pads at ends
    const padW = 0.2 * U;
    g.appendChild(svgel("rect", { class: "shape", x: -w / 2 - padW, y: -h / 2, width: padW * 2, height: h }));
    g.appendChild(svgel("rect", { class: "shape", x: w / 2 - padW, y: -h / 2, width: padW * 2, height: h }));
    // Label: ref + value
    const lbl = [comp.ref, comp.extra].filter(Boolean).join(" ");
    g.appendChild(svgel("text", {
      class: "label", x: 0, y: -h / 2 - 1.5 * U,
      "text-anchor": "middle", "font-size": 1.3 * U,
      textContent: lbl,
    }));
  } else if (cat === "coincell" || cat === "electrolytic" || cat === "buzzer") {
    // Circle.
    const r = size.r * U;
    g.appendChild(svgel("circle", { class: "shape", cx: 0, cy: 0, r }));
    if (cat === "coincell") {
      // Inner circle (pole)
      g.appendChild(svgel("circle", { class: "shape", cx: 0, cy: 0, r: r * 0.65, fill: "none" }));
    }
    const lbl = cat === "electrolytic" ? `${comp.ref} ${comp.extra || ""}`.trim() : comp.ref;
    g.appendChild(svgel("text", {
      class: "label", x: 0, y: r + 2.5 * U,
      "text-anchor": "middle", "font-size": 1.5 * U,
      textContent: lbl,
    }));
  } else {
    // Unknown — gray rectangle with dashed border.
    g.appendChild(svgel("rect", {
      class: "shape", x: -w / 2, y: -h / 2, width: w, height: h,
      "stroke-dasharray": `${0.5 * U},${0.3 * U}`,
    }));
    const lbl = `${comp.ref} (${comp.tag})`;
    g.appendChild(svgel("text", {
      class: "label", x: 0, y: h / 2 + 2.5 * U,
      "text-anchor": "middle", "font-size": 1.3 * U,
      textContent: lbl,
    }));
  }

  return g;
}

// ---- State ----------------------------------------------------------------

let pz = null; // PanZoom instance
let boardName = null;
let components = []; // { ref, x, y, rot, ... }
let rawTsx = null; // for reference, not write-back
let snapMm = 0.05;
let dragging = null; // { ref, g, startX, startY, startClientX, startClientY }

// ---- Coordinate conversion -------------------------------------------------

// Client pixels → board mm, using PanZoom's CSS transform.
function clientToMm(clientX, clientY) {
  if (!pz) return null;
  const svgEl = document.getElementById("edit-svg");
  if (!svgEl) return null;
  const wrap = document.getElementById("canvas-wrap");
  const wr = wrap.getBoundingClientRect();
  const t = pz.getTransform();
  // PanZoom applies: scale * element + translate, transform-origin: 0 0.
  // screen = wr.left + svgCoord * scale + panX
  // svgCoord = (screen - wr.left - panX) / scale
  const vx = (clientX - wr.left - t.panX) / t.scale;
  const vy = (clientY - wr.top - t.panY) / t.scale;
  // SVG → board mm: SVG Y is flipped
  return { x: vx / U, y: -vy / U };
}

// ---- Drag handlers ---------------------------------------------------------

function onPointerDown(e) {
  const g = e.target.closest(".comp-shape");
  if (!g) return;
  if (e.button !== undefined && e.button !== 0) return; // primary button only

  e.stopPropagation();
  e.preventDefault();

  const ref = g.getAttribute("data-ref");
  const sx = parseFloat(g.getAttribute("data-x"));
  const sy = parseFloat(g.getAttribute("data-y"));

  dragging = {
    ref,
    g,
    startX: sx,
    startY: sy,
    startClientX: e.clientX,
    startClientY: e.clientY,
  };

  g.classList.add("dragging");
  g.setPointerCapture(e.pointerId);
}

function onPointerMove(e) {
  if (!dragging) return;

  const dx = e.clientX - dragging.startClientX;
  const dy = e.clientY - dragging.startClientY;
  if (Math.abs(dx) < 2 && Math.abs(dy) < 2) return; // dead zone

  const t = pz.getTransform();
  const mmDx = dx / t.scale / U;
  const mmDy = -dy / t.scale / U; // SVG Y flip

  let newX = dragging.startX + mmDx;
  let newY = dragging.startY + mmDy;

  if (snapMm > 0) {
    newX = Math.round(newX / snapMm) * snapMm;
    newY = Math.round(newY / snapMm) * snapMm;
  }

  // Update the visual position
  const svg = svgXY({ x: newX, y: newY });
  const rot = parseInt(dragging.g.getAttribute("data-rot"), 10);
  dragging.g.setAttribute(
    "transform",
    `translate(${svg.x},${svg.y}) rotate(${-rot})`,
  );
  dragging.g.setAttribute("data-x", String(newX));
  dragging.g.setAttribute("data-y", String(newY));

  updateCoords(newX, newY, dragging.ref);
}

function onPointerUp(e) {
  if (!dragging) return;

  const g = dragging.g;
  const newX = parseFloat(g.getAttribute("data-x"));
  const newY = parseFloat(g.getAttribute("data-y"));
  const moved = newX !== dragging.startX || newY !== dragging.startY;

  g.classList.remove("dragging");
  g.releasePointerCapture(e.pointerId);

  const ref = dragging.ref;
  const oldX = dragging.startX;
  const oldY = dragging.startY;
  dragging = null;

  if (moved) {
    writePosition(ref, oldX, oldY, newX, newY);
  }
}

// ---- Write-back ------------------------------------------------------------

async function writePosition(ref, oldX, oldY, newX, newY) {
  setStatus(`${ref}: saving…`);
  try {
    const resp = await fetch(
      `/api/pcb-editor/board/${boardName}/update-position`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ref, oldX, oldY, newX, newY }),
      },
    );
    if (resp.ok) {
      setStatus(`${ref}: ${fmtNum(oldX)},${fmtNum(oldY)} → ${fmtNum(newX)},${fmtNum(newY)} ✓`);
      // Update the stored component position so a subsequent drag starts from
      // the new value (the Tsx was written back, dev server will re-render).
      const comp = components.find((c) => c.ref === ref);
      if (comp) { comp.x = newX; comp.y = newY; }
    } else {
      const err = await resp.json().catch(() => ({}));
      setStatus(`Save failed: ${err.error || resp.status}`, true);
      // Revert visual position
      const svg = svgXY({ x: oldX, y: oldY });
      const g = document.querySelector(`.comp-shape[data-ref="${CSS.escape(ref)}"]`);
      if (g) {
        const rot = parseInt(g.getAttribute("data-rot"), 10);
        g.setAttribute("transform", `translate(${svg.x},${svg.y}) rotate(${-rot})`);
        g.setAttribute("data-x", String(oldX));
        g.setAttribute("data-y", String(oldY));
      }
    }
  } catch (e) {
    setStatus(`Network error: ${e.message}`, true);
  }
}

// ---- UI helpers ------------------------------------------------------------

function fmtNum(n) {
  return Number(n).toFixed(2);
}

function updateCoords(x, y, ref) {
  const el = document.getElementById("coords");
  if (el) el.textContent = `${ref}  x=${fmtNum(x)}  y=${fmtNum(y)}`;
}

function setStatus(msg, isError) {
  const el = document.getElementById("status");
  if (el) {
    el.textContent = msg;
    el.style.color = isError ? "var(--red)" : "var(--dim)";
  }
}

// ---- Board loading ----------------------------------------------------------

function computeBounds(outline, comps) {
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  if (outline) {
    for (const p of outline) {
      minX = Math.min(minX, p.x);
      maxX = Math.max(maxX, p.x);
      minY = Math.min(minY, p.y);
      maxY = Math.max(maxY, p.y);
    }
  }
  for (const c of comps) {
    const r = Math.max(c.size.w || c.size.h || 5, c.size.r || 0) + 2;
    minX = Math.min(minX, c.x - r);
    maxX = Math.max(maxX, c.x + r);
    minY = Math.min(minY, c.y - r);
    maxY = Math.max(maxY, c.y + r);
  }
  const pad = 5;
  minX -= pad;
  maxX += pad;
  minY -= pad;
  maxY += pad;
  return { minX, maxX, minY, maxY, width: maxX - minX, height: maxY - minY };
}

async function loadBoard(name) {
  boardName = name;
  setStatus("Loading…");
  document.getElementById("coords").textContent = "";

  const resp = await fetch(`/api/pcb-editor/board/${name}`);
  if (!resp.ok) {
    setStatus(`Failed to load ${name}`, true);
    return;
  }
  const data = await resp.json();
  components = data.components;
  rawTsx = data.rawTsx;

  const bounds = computeBounds(data.outline || data.components, data.components);

  // Build SVG
  const svgEl = document.getElementById("edit-svg");
  while (svgEl.firstChild) svgEl.removeChild(svgEl.firstChild);

  svgEl.setAttribute(
    "viewBox",
    `${bounds.minX * U} ${-bounds.maxY * U} ${bounds.width * U} ${bounds.height * U}`,
  );
  svgEl.setAttribute("width", bounds.width * U);
  svgEl.setAttribute("height", bounds.height * U);

  // Grid
  const gridGroup = svgel("g", { class: "grid-group" });
  for (const el of buildGrid(bounds)) gridGroup.appendChild(el);
  svgEl.appendChild(gridGroup);

  // Board outline
  if (data.outline) {
    const outlineGroup = svgel("g", { class: "outline-group" });
    for (const el of buildOutline(data.outline)) outlineGroup.appendChild(el);
    svgEl.appendChild(outlineGroup);
  }

  // Silk layer
  if (data.silk && data.silk.length) {
    const silkGroup = svgel("g", { class: "silk-group" });
    for (const el of buildSilk(data.silk)) silkGroup.appendChild(el);
    svgEl.appendChild(silkGroup);
  }

  // Components
  const compGroup = svgel("g", { class: "comp-group" });
  for (const comp of data.components) {
    compGroup.appendChild(buildCompShape(comp));
  }
  svgEl.appendChild(compGroup);

  // Pointer listeners for drag — on the SVG element so we can stopPropagation
  // before PanZoom's container listener sees the event.
  svgEl.addEventListener("pointerdown", onPointerDown, true);
  document.addEventListener("pointermove", onPointerMove);
  document.addEventListener("pointerup", onPointerUp);

  // PanZoom
  if (pz) {
    try { pz.destroy(); } catch {}
  }
  const wrap = document.getElementById("canvas-wrap");
  pz = PanZoom.wrap(svgEl, {
    container: wrap,
    initialFit: true,
    minScale: 0.01,
    maxScale: 200,
  });

  setStatus(`${name} — ${data.components.length} components`);
  document.getElementById("reload-btn").disabled = false;
}

// ---- Init ------------------------------------------------------------------

async function init() {
  const boardSelect = document.getElementById("board-select");
  const reloadBtn = document.getElementById("reload-btn");
  const snapInput = document.getElementById("snap-input");

  // Fetch board list
  let boards = [];
  try {
    const resp = await fetch("/api/pcb-editor/boards");
    if (resp.ok) boards = await resp.json();
  } catch {}
  for (const b of boards) {
    const opt = document.createElement("option");
    opt.value = b.name;
    opt.textContent = b.name;
    boardSelect.appendChild(opt);
  }

  boardSelect.addEventListener("change", () => {
    if (boardSelect.value) {
      history.replaceState(null, "", `/pcb-editor#${boardSelect.value}`);
      loadBoard(boardSelect.value);
    }
  });

  reloadBtn.addEventListener("click", () => {
    if (boardSelect.value) loadBoard(boardSelect.value);
  });

  snapInput.addEventListener("change", () => {
    snapMm = Math.max(0, parseFloat(snapInput.value) || 0);
    snapInput.value = snapMm;
  });
  snapMm = parseFloat(snapInput.value) || 0.05;

  // Deep-link: load board from URL hash
  const hash = location.hash.replace("#", "");
  if (hash && boards.some((b) => b.name === hash)) {
    boardSelect.value = hash;
    loadBoard(hash);
  } else if (hash) {
    // Board name from hash not in the list — still try to load it
    boardSelect.value = hash;
    loadBoard(hash);
  }
}

init();
