// Preview a plane on the intact model before sharing it between the cut and its profile.
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
  const curve = pick && sectionCurveAt(pick), face = pick?.face?.n || pick?.normal;
  if (curve?.axis?.lengthSq()) opts.push(["Across curve", curve.axis, curve.radius]);
  if (pick?.edge?.kind === "straight") opts.push(["Across edge", pick.edge.dir]);
  if (pick?.face?.kind === "plane") {
    const along = forward.clone().addScaledVector(face, -forward.dot(face));
    if (along.lengthSq() < 0.04) {
      along.set(1, 0, 0).applyQuaternion(camera.quaternion);
      along.addScaledVector(face, -along.dot(face));
    }
    if (along.lengthSq() > 1e-8) opts.push(["Through face", along]);
    opts.push(["Parallel to face", face]);
  }
  opts.push(["X", new THREE.Vector3(1, 0, 0)], ["Y", new THREE.Vector3(0, 1, 0)],
    ["Z", new THREE.Vector3(0, 0, 1)], ["Facing view"]);
  return opts.map(([label, vector, radius]) => {
    if (!vector) return { label };
    const normal = vector.clone().normalize();
    if (normal.dot(forward) < 0) normal.negate();
    return { label, normal, radius };
  });
}

// Draw the plane and the direction of removal without changing any model material.
function makePlaneGuide(span) {
  const group = new THREE.Group();
  group.name = "Section plane preview";
  group.matrixAutoUpdate = false;
  const color = "#ffbd78";
  const sheet = new THREE.Mesh(new THREE.PlaneGeometry(span, span), new THREE.MeshBasicMaterial({
    color, side: THREE.DoubleSide, transparent: true, opacity: 0.16, depthTest: false, depthWrite: false, toneMapped: false,
  }));
  const half = span / 2;
  const corners = [[-half, -half], [half, -half], [half, half], [-half, half]].map(([x, y]) => new THREE.Vector3(x, y, 0));
  const outline = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(corners), new THREE.LineBasicMaterial({
    color, transparent: true, depthTest: false, depthWrite: false, toneMapped: false,
  }));
  const arrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, span * 0.34, 0), span * 0.26, color);
  sheet.renderOrder = 1100;
  outline.renderOrder = 1101;
  for (const child of arrow.children) {
    child.renderOrder = 1101;
    Object.assign(child.material, { transparent: true, depthTest: false, depthWrite: false, toneMapped: false });
  }
  group.add(sheet, outline, arrow);
  return {
    group,
    orient(frame, flipped) {
      group.matrix.copy(frame);
      group.matrixWorldNeedsUpdate = true;
      arrow.setDirection(new THREE.Vector3(0, 0, flipped ? 1 : -1));
    },
    dispose() {
      group.removeFromParent();
      for (const mark of [sheet, outline]) mark.geometry.dispose();
      group.traverse(mark => mark.material?.dispose());
    },
  };
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

export function startSectionPreview({ wrapper, toggle, pick }) {
  const root = state.currentGroup, stage = wrapper.closest(".cad-stage");
  const box = new THREE.Box3();
  root.updateWorldMatrix(true, false);
  root.traverseVisible(mesh => {
    if (mesh.isMesh && mesh.userData.side === "front") box.expandByObject(mesh);
  });
  if (box.isEmpty()) return null;
  const boxCenter = box.getCenter(new THREE.Vector3()), boxSize = box.getSize(new THREE.Vector3());
  const anchor = pick?.point?.isVector3 && pick.point.toArray().every(Number.isFinite) ? pick.point.clone() : boxCenter;
  const reference = anchor === boxCenter ? "model center" : "picked point";
  const options = optionsFor(pick);
  const selected = componentOwner(pick?.object?.name) || pick?.ownerName || "";
  const visibleSpan = 2 * camera.position.distanceTo(anchor) * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const partSpan = (pick?.object ? new THREE.Box3().setFromObject(pick.object).getSize(new THREE.Vector3()) : boxSize).length();
  const startSpan = Math.max(0.5, options[0].radius > 0 ? options[0].radius * 9 :
    Math.min(visibleSpan * 0.65, partSpan * 1.15) || 20);
  const guide = makePlaneGuide(Math.max(0.5, Math.min(boxSize.length() * 1.15, visibleSpan * 0.86)));
  const plane = new THREE.Plane(), normal = new THREE.Vector3(), right = new THREE.Vector3(), up = new THREE.Vector3();
  const center = new THREE.Vector3(), frame = new THREE.Matrix4(), pan = new THREE.Vector2();
  const caps = new THREE.Group();
  caps.name = "Section cut"; caps.matrixAutoUpdate = false;
  const previousPlanes = renderer.clippingPlanes;
  scene.add(guide.group);
  const controller = new AbortController(), { signal } = controller;
  let rows = [], flipped = false, offset = 0, scale, timer, job = 0, closed = false, applied = false;
  let span = startSpan;

  const panel = node("section", "section-profile");
  panel.hidden = true;
  panel.setAttribute("aria-label", "Section profile");
  const title = node("h2", "", "Section profile");
  const canvas = node("canvas", "section-profile-canvas");
  canvas.setAttribute("role", "img"); canvas.setAttribute("aria-label", "Face-on cross section");
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
  bar.setAttribute("role", "region");
  bar.setAttribute("aria-label", "Section controls");
  const cut = button("3D cut", "3D cut", () => setPane(false));
  const profile = button("Profile", "Section profile", () => setPane(true));
  views.setAttribute("role", "group"); views.setAttribute("aria-label", "Section view"); views.append(cut, profile);
  views.hidden = true;
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
  offsetLabel.append(node("span", "", "Offset"), slider);
  slider.setAttribute("aria-label", `Section offset from ${reference}`);
  const numberBox = node("label", "section-number"), number = node("input");
  number.type = "number"; number.step = "any"; number.value = "0";
  number.setAttribute("aria-label", `Offset from ${reference} in millimeters`);
  numberBox.append(number, " mm");
  const previewNote = node("span", "section-preview-note", "Preview · Arrow shows the side to remove");
  const apply = button("Apply cut", "Apply cut", () => setApplied(!applied));
  apply.className = "section-apply";
  const done = button("Close section", "Close section", () => close());
  done.replaceChildren("Close", node("span", "section-wide-word", " section"));
  const planeControls = node("div", "section-plane-controls"), commands = node("div", "section-commands");
  planeControls.append(axisLabel, flip, offsetLabel, numberBox);
  commands.append(apply, done);
  bar.append(previewNote, views, planeControls, commands);
  stage.classList.add("section-active");
  stage.append(panel, bar);
  toggle.setAttribute("aria-expanded", "true");
  setPane(false);

  function setApplied(value) {
    applied = value;
    panel.hidden = views.hidden = !applied;
    previewNote.hidden = applied;
    guide.group.visible = !applied;
    stage.classList.toggle("section-open", applied);
    const label = applied ? "Preview plane" : "Apply cut";
    apply.textContent = label;
    apply.title = label;
    apply.setAttribute("aria-label", label);
    renderer.clippingPlanes = applied ? [...previousPlanes, plane] : previousPlanes;
    setSurfaceSection(applied ? root : null, applied ? plane : null);
    if (applied) {
      scene.add(caps);
      refresh();
    } else {
      job++; clearTimeout(timer);
      emptyMarks();
      caps.removeFromParent();
      setPane(false);
    }
    invalidateBlueprintVisibility();
    requestCadRender();
  }

  function range() {
    const midpoint = normal.dot(boxCenter) - normal.dot(anchor);
    const reach = (Math.abs(normal.x) * boxSize.x + Math.abs(normal.y) * boxSize.y + Math.abs(normal.z) * boxSize.z) / 2;
    const min = Math.min(offset, 0, Math.floor(midpoint - reach)), max = Math.max(offset, 0, Math.ceil(midpoint + reach));
    slider.min = String(min); slider.max = String(max); slider.step = max - min > 200 ? "0.5" : "0.1";
    slider.value = String(offset);
    slider.setAttribute("aria-valuetext", `${offset} millimeters from ${reference}`);
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
    pan.set(0, 0); offset = 0; orient();
  });

  function orient() {
    const option = options[Number(axis.value)];
    if (option.normal) normal.copy(option.normal);
    else camera.getWorldDirection(normal);
    up.set(0, 0, 1);
    if (Math.abs(up.dot(normal)) > 0.98) up.set(0, 1, 0).applyQuaternion(camera.quaternion);
    if (Math.abs(up.dot(normal)) > 0.98) up.set(0, 1, 0);
    right.crossVectors(normal, up).normalize(); up.crossVectors(right, normal).normalize();
    range();
    movePlane();
  }
  function emptyMarks() {
    caps.traverse(o => { o.geometry?.dispose(); o.material?.dispose(); });
    caps.clear(); rows = [];
  }
  function movePlane() {
    center.copy(anchor).addScaledVector(normal, offset);
    plane.setFromNormalAndCoplanarPoint(normal, center);
    if (flipped) plane.negate();
    frame.makeBasis(right, up, normal).setPosition(center);
    guide.orient(frame, flipped);
    caps.matrix.copy(frame);
    caps.matrix.setPosition(center.clone().addScaledVector(plane.normal, 0.0004));
    caps.matrixWorldNeedsUpdate = true;
    if (applied) {
      emptyMarks();
      refresh();
      invalidateBlueprintVisibility();
    }
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
    if (state.currentGroup !== root) { close(false); return; }
    if (!applied) return;
    const ticket = ++job;
    clearTimeout(timer);
    syncCaps();
    panel.setAttribute("aria-busy", "true"); redraw();
    timer = setTimeout(() => {
      if (state.currentGroup !== root) { close(false); return; }
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
      if (applied) redraw();
    });
  });
  resize.observe(stage); resize.observe(plot);
  window.addEventListener(HSM_EVENTS.BLUEPRINT_VISIBILITY, syncCaps, { signal });
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, refresh, { signal });
  window.addEventListener(HSM_EVENTS.FAUCET_OPTIONS, refresh, { signal });
  function close(restoreFocus = true) {
    if (closed) return false;
    closed = true; job++; clearTimeout(timer); resize.disconnect(); cancelAnimationFrame(resizeFrame); controller.abort();
    renderer.clippingPlanes = previousPlanes;
    setSurfaceSection(null, null); emptyMarks(); caps.removeFromParent();
    guide.dispose();
    stage.classList.remove("section-active", "section-open", "section-narrow", "section-profile-open");
    toggle.setAttribute("aria-expanded", "false");
    bar.remove(); panel.remove(); invalidateBlueprintVisibility(); requestCadRender();
    const focus = toggle.closest(".tool-drawer.compact:not([open])")?.querySelector("summary") || toggle;
    if (restoreFocus && focus.getClientRects().length) focus.focus({ preventScroll: true });
    return true;
  }
  stage.classList.toggle("section-narrow", stage.clientWidth < 680);
  orient();
  axis.focus({ preventScroll: true });
  return { close, refresh };
}
