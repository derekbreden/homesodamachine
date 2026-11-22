// The cut and its face-on profile share a plane fixed to the installed model.
import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { camera, renderer, scene, requestCadRender } from "./scene.js";
import { state } from "./state.js";
import { componentOwner } from "./component-units.js";
import { setSurfaceSection } from "./surface-query.js";
import { invalidateBlueprintVisibility } from "./xray.js";
import { sectionCurveAt, sectionRows, sectionCap } from "./section-geometry.js";

const node = (tag, cls, text) => {
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  if (text) el.textContent = text;
  return el;
};
function button(text, title, action) {
  const el = node("button", "", text);
  el.type = "button"; el.title = title; el.setAttribute("aria-label", title);
  el.addEventListener("click", action);
  return el;
}
const palette = ["#91bed0", "#b4b2df", "#9ac5a7", "#c6a1a8", "#c7bd97"];
function colorFor(name, selected) {
  let hash = 0;
  for (const c of name) hash = (hash * 31 + c.charCodeAt(0)) >>> 0;
  return selected ? "#ffb45f" : palette[hash % palette.length];
}
function optionsFor(pick) {
  const forward = camera.getWorldDirection(new THREE.Vector3()), opts = [];
  const curve = sectionCurveAt(pick), face = pick.face?.n || pick.normal;
  if (curve?.axis?.lengthSq()) opts.push(["Across curve", curve.axis, curve.radius]);
  if (pick.edge?.kind === "straight") opts.push(["Across edge", pick.edge.dir]);
  if (pick.face?.kind === "plane") {
    const along = forward.clone().addScaledVector(face, -forward.dot(face));
    if (along.lengthSq() < 0.04) {
      along.set(1, 0, 0).applyQuaternion(camera.quaternion);
      along.addScaledVector(face, -along.dot(face));
    }
    if (along.lengthSq() > 1e-8) opts.push(["Through face", along]);
    opts.push(["Parallel to face", face]);
  }
  opts.push(["Facing view", forward], ["X", new THREE.Vector3(1, 0, 0)],
    ["Y", new THREE.Vector3(0, 1, 0)], ["Z", new THREE.Vector3(0, 0, 1)]);
  return opts.map(([label, vector, radius]) => {
    const normal = vector.clone().normalize();
    if (normal.dot(forward) < 0) normal.negate();
    return { label, normal, radius };
  });
}

function cutMarks(row, color) {
  const { vertices, indices } = sectionCap(row.paths);
  const group = new THREE.Group();
  if (indices.length) {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    const material = new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide, toneMapped: false,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
    group.add(new THREE.Mesh(geometry, material));
  }
  const segments = [];
  for (const { points, closed } of row.paths) {
    for (let i = 0; i < points.length - (closed ? 0 : 1); i++) {
      const a = points[i], b = points[(i + 1) % points.length];
      segments.push(a.x, a.y, 0, b.x, b.y, 0);
    }
  }
  if (segments.length) {
    const edges = new THREE.BufferGeometry();
    edges.setAttribute("position", new THREE.Float32BufferAttribute(segments, 3));
    group.add(new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: "#e8eef2", toneMapped: false })));
  }
  return group;
}

function makeSection(wrapper, pick) {
  const root = state.currentGroup, stage = wrapper.closest(".cad-stage");
  const options = optionsFor(pick);
  const selected = componentOwner(pick.object?.name) || pick.ownerName || "";
  const plane = new THREE.Plane(), normal = new THREE.Vector3(), right = new THREE.Vector3(), up = new THREE.Vector3();
  const center = new THREE.Vector3(), frame = new THREE.Matrix4(), pan = new THREE.Vector2();
  const caps = new THREE.Group();
  caps.name = "Section cut"; caps.matrixAutoUpdate = false;
  const previousPlanes = renderer.clippingPlanes;
  renderer.clippingPlanes = [...previousPlanes, plane];
  setSurfaceSection(root, plane);
  scene.add(caps);
  const controller = new AbortController(), { signal } = controller;
  let rows = [], flipped = false, offset = 0, scale, timer, job = 0, closed = false;
  const initialFocus = document.activeElement;

  const panel = node("section", "section-profile");
  panel.setAttribute("aria-label", "Section profile");
  const title = node("h2", "", "Section profile");
  const canvas = node("canvas", "section-profile-canvas");
  canvas.setAttribute("role", "img"); canvas.setAttribute("aria-label", "Face-on cross section through the picked point");
  const plot = node("div", "section-plot"), legend = node("div", "section-legend");
  const status = node("span", "section-status");
  status.setAttribute("role", "status");
  plot.append(canvas, status);
  const zoom = node("div", "section-zoom");
  zoom.append(button("−", "Zoom out of the profile", () => zoomBy(1.6)),
    button("+", "Zoom in on the profile", () => zoomBy(1 / 1.6)));
  const heading = node("header", "section-profile-head"); heading.append(title, zoom);
  panel.append(heading, plot, legend);

  const bar = node("div", "section-bar"), views = node("div", "section-panes");
  const cut = button("3D cut", "3D cut", () => setPane(false));
  const profile = button("Section profile", "Section profile", () => setPane(true));
  views.setAttribute("role", "group"); views.setAttribute("aria-label", "Section view"); views.append(cut, profile);
  function setPane(show) {
    stage.classList.toggle("section-profile-open", show);
    cut.setAttribute("aria-pressed", String(!show));
    profile.setAttribute("aria-pressed", String(show));
    if (show) redraw();
  }
  const axisLabel = node("label", "section-plane");
  const axis = node("select"); axis.setAttribute("aria-label", "Section plane");
  options.forEach(({ label }, i) => axis.add(new Option(label, i)));
  axisLabel.append(node("span", "", "Plane"), axis);
  const flip = button("Flip", "Keep the other side", () => {
    flipped = !flipped; flip.setAttribute("aria-pressed", String(flipped)); movePlane();
  });
  flip.setAttribute("aria-pressed", "false");
  const offsetLabel = node("label", "section-offset");
  const slider = node("input"); slider.type = "range"; slider.value = "0";
  const offsetText = node("span", "", "Offset"); offsetText.append(node("span", "section-wide-word", " from pick"));
  offsetLabel.append(offsetText, slider); slider.setAttribute("aria-label", "Section offset from picked point");
  const numberBox = node("label", "section-number"), number = node("input");
  number.type = "number"; number.step = "any"; number.value = "0"; number.setAttribute("aria-label", "Offset from pick in millimeters");
  numberBox.append(number, " mm");
  const done = button("Close section", "Close section", close);
  done.replaceChildren("Close", node("span", "section-wide-word", " section"));
  bar.append(views, axisLabel, flip, offsetLabel, numberBox, done);
  stage.classList.add("section-open");
  stage.append(panel, bar);
  setPane(false);

  const visibleSpan = 2 * camera.position.distanceTo(pick.point) * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const box = new THREE.Box3().setFromObject(pick.object || root);
  const partSpan = box.getSize(new THREE.Vector3()).length();
  const startSpan = Math.max(0.5, options[0].radius > 0 ? options[0].radius * 9 :
    Math.min(visibleSpan * 0.65, partSpan * 1.15) || 20);
  let span = startSpan;
  const baselineRange = Math.max(1, startSpan / 2);
  function range() {
    const extent = Math.ceil(Math.max(Math.abs(offset), baselineRange));
    slider.min = String(-extent); slider.max = String(extent); slider.step = extent > 100 ? "0.5" : "0.1";
    slider.value = String(offset);
    slider.setAttribute("aria-valuetext", offset + " millimeters from pick");
    number.value = String(offset);
  }
  function setOffset(value) {
    if (!Number.isFinite(value)) return;
    offset = value; range(); movePlane();
  }
  slider.addEventListener("input", () => setOffset(slider.valueAsNumber));
  number.addEventListener("input", () => { if (Number.isFinite(number.valueAsNumber)) { offset = number.valueAsNumber; movePlane(); } });
  number.addEventListener("change", () => { range(); });
  axis.addEventListener("change", () => {
    pan.set(0, 0); offset = 0; range(); orient();
  });

  function orient() {
    normal.copy(options[Number(axis.value)].normal);
    up.set(0, 0, 1);
    if (Math.abs(up.dot(normal)) > 0.98) up.set(0, 1, 0).applyQuaternion(camera.quaternion);
    if (Math.abs(up.dot(normal)) > 0.98) up.set(0, 1, 0);
    right.crossVectors(normal, up).normalize(); up.crossVectors(right, normal).normalize();
    movePlane();
  }
  function emptyMarks() {
    caps.traverse(o => { o.geometry?.dispose(); o.material?.dispose(); });
    caps.clear(); rows = [];
  }
  function movePlane() {
    center.copy(pick.point).addScaledVector(normal, offset);
    plane.setFromNormalAndCoplanarPoint(normal, center);
    if (flipped) plane.negate();
    frame.makeBasis(right, up, normal).setPosition(center);
    caps.matrix.copy(frame);
    caps.matrix.setPosition(center.clone().addScaledVector(plane.normal, 0.0004));
    caps.matrixWorldNeedsUpdate = true;
    emptyMarks(); redraw(); refresh();
    invalidateBlueprintVisibility();
    requestCadRender();
  }
  function zoomBy(factor) {
    span = THREE.MathUtils.clamp(span * factor, startSpan / 128, Math.max(partSpan, startSpan) * 4);
    redraw();
  }
  const ctx = canvas.getContext("2d");
  function metrics() {
    const w = plot.clientWidth || Math.min(stage.clientWidth, 360), h = plot.clientHeight || wrapper.clientHeight;
    scale = Math.max(1, Math.min(w, h)) / span;
    return { w, h };
  }
  function profileWindow(padding = 0.5) {
    const { w, h } = metrics();
    const half = new THREE.Vector2(w, h).multiplyScalar(padding / scale);
    return new THREE.Box2(pan.clone().sub(half), pan.clone().add(half));
  }
  function syncCaps() {
    for (const row of rows) {
      row.mark.visible = row.mesh.visible;
      for (const o of row.mark.children) o.layers.mask = row.mesh.layers.mask;
    }
  }
  let previousLegend;
  function redraw() {
    if (!ctx) return;
    const { w, h } = metrics(), dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (!w || !h) return;
    if (canvas.width !== Math.round(w * dpr)) canvas.width = Math.round(w * dpr);
    if (canvas.height !== Math.round(h * dpr)) canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
    ctx.translate(w / 2 - pan.x * scale, h / 2 + pan.y * scale); ctx.scale(scale, -scale);
    ctx.lineWidth = 1.25 / scale; ctx.lineJoin = "round";
    const shown = profileWindow(), names = new Map();
    for (const row of rows) {
      if (!row.mesh.visible || !row.box.intersectsBox(shown)) continue;
      ctx.fillStyle = row.color; ctx.strokeStyle = row.color;
      ctx.globalAlpha = 0.47; ctx.fill(row.fill, "evenodd");
      ctx.globalAlpha = 1; ctx.stroke(row.outline);
      names.set(row.name, row.color);
    }
    const cross = 5 / scale;
    ctx.beginPath(); ctx.strokeStyle = "#fff"; ctx.lineWidth = 1 / scale;
    ctx.moveTo(-cross, 0); ctx.lineTo(cross, 0); ctx.moveTo(0, -cross); ctx.lineTo(0, cross); ctx.stroke();
    const sorted = [...names].sort(([a], [b]) => Number(b === selected) - Number(a === selected) || a.localeCompare(b));
    const key = JSON.stringify(sorted);
    if (key !== previousLegend) {
      previousLegend = key;
      legend.replaceChildren(...sorted.map(([name, color]) => {
        const label = node("span", "", name);
        label.style.setProperty("--swatch", color);
        return label;
      }));
    }
    status.textContent = names.size ? "" : panel.getAttribute("aria-busy") === "true" ? "Updating section…" : "No material crosses this window.";
  }
  function install(row) {
    row.name = componentOwner(row.mesh.name) || row.mesh.name || "Solid";
    row.color = colorFor(row.name, row.name === selected);
    row.fill = new Path2D(); row.outline = new Path2D(); row.box = new THREE.Box2();
    for (const { points, closed } of row.paths) {
      const path = new Path2D();
      path.moveTo(points[0].x, points[0].y);
      row.box.expandByPoint(points[0]);
      for (let i = 1; i < points.length; i++) { path.lineTo(points[i].x, points[i].y); row.box.expandByPoint(points[i]); }
      if (closed) { path.closePath(); row.fill.addPath(path); }
      row.outline.addPath(path);
    }
    row.mark = cutMarks(row, row.color);
    row.mark.visible = row.mesh.visible;
    for (const o of row.mark.children) o.layers.mask = row.mesh.layers.mask;
    caps.add(row.mark); rows.push(row);
  }
  function refresh() {
    if (closed) return;
    const ticket = ++job;
    clearTimeout(timer);
    syncCaps();
    panel.setAttribute("aria-busy", "true"); redraw();
    timer = setTimeout(() => {
      if (state.currentGroup !== root) { close(); return; }
      emptyMarks();
      const iterator = sectionRows(root, frame.clone().invert(), profileWindow(0.6));
      function next() {
        if (closed || job !== ticket) return;
        const until = performance.now() + 5;
        let added = false;
        do {
          const step = iterator.next();
          if (step.done) {
            panel.setAttribute("aria-busy", "false"); redraw(); requestCadRender();
            return;
          }
          if (step.value) { install(step.value); added = true; }
        } while (performance.now() < until);
        if (added) { redraw(); requestCadRender(); }
        timer = setTimeout(next, 0);
      }
      next();
    }, 70);
  }

  let drag = null;
  canvas.addEventListener("pointerdown", e => {
    drag = { id: e.pointerId, x: e.clientX, y: e.clientY, pan: pan.clone() }; canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener("pointermove", e => {
    if (!drag || e.pointerId !== drag.id) return;
    pan.set(drag.pan.x - (e.clientX - drag.x) / scale, drag.pan.y + (e.clientY - drag.y) / scale); redraw();
  });
  canvas.addEventListener("lostpointercapture", () => { drag = null; });
  canvas.addEventListener("wheel", e => { e.preventDefault(); zoomBy(Math.exp(Math.sign(e.deltaY) * 0.15)); }, { passive: false });

  // A responsive pane switch can resize the renderer and the profile together.
  let resizeFrame = 0;
  const resize = new ResizeObserver(() => {
    if (resizeFrame) return;
    resizeFrame = requestAnimationFrame(() => {
      resizeFrame = 0;
      stage.classList.toggle("section-narrow", stage.clientWidth < 680);
      redraw();
    });
  });
  resize.observe(stage); resize.observe(plot);
  window.addEventListener(HSM_EVENTS.BLUEPRINT_VISIBILITY, syncCaps, { signal });
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, refresh, { signal });
  window.addEventListener(HSM_EVENTS.FAUCET_OPTIONS, refresh, { signal });
  function close() {
    if (closed) return false;
    closed = true; job++; clearTimeout(timer); resize.disconnect(); cancelAnimationFrame(resizeFrame); controller.abort();
    renderer.clippingPlanes = previousPlanes;
    setSurfaceSection(null, null); emptyMarks(); caps.removeFromParent();
    stage.classList.remove("section-open", "section-narrow", "section-profile-open");
    bar.remove(); panel.remove(); invalidateBlueprintVisibility(); requestCadRender();
    if (initialFocus?.isConnected && initialFocus.getClientRects().length) initialFocus.focus({ preventScroll: true });
    return true;
  }
  stage.classList.toggle("section-narrow", stage.clientWidth < 680);
  range(); orient();
  done.focus({ preventScroll: true });
  return { close, refresh, get closed() { return closed; } };
}

export function createSectionView({ wrapper }) {
  let active;
  const canUse = pick => !!(state.currentGroup && wrapper.closest(".cad-stage") && pick?.point?.isVector3 &&
    pick.point.toArray().every(Number.isFinite));
  return {
    canUse,
    start(pick) {
      if (!canUse(pick)) return false;
      active?.close(); active = makeSection(wrapper, pick);
      return true;
    },
    refresh() { if (active && !active.closed) active.refresh(); },
    close() { return active?.close() || false; },
    dispose() { active?.close(); active = null; },
  };
}
