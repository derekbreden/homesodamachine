// Optional tube audit. Geometry is in the STEP's millimetres and +Z-up frame,
// in a scene sibling that the component and edge pickers never traverse.
import * as THREE from "three";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineGeometry } from "three/addons/lines/LineGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { scene, camera, controls, renderer, setExtraDepthBounds } from "./scene.js";
import { state } from "./state.js";
import { makePanelCollapse } from "./tool-rail.js";
import { closePickFind } from "./pick-find.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { newTubeContacts } from "./tube-contacts.js";

const SCENARIOS = {
  straight: "Straight stock",
  "coil-positive": "Coil set +",
  "coil-negative": "Coil set −",
};
const COLORS = { nominal: 0x55d8eb, straight: 0xffb44c, "coil-positive": 0xb7a0ff, "coil-negative": 0xf084bf, hold: 0x69e5aa, omitted: 0xff707b };
const COIL_NORMALS = { xy: [0, 0, 1], xz: [0, 1, 0], yz: [1, 0, 0] };
const bodyName = (name) => (name || "").replace(/\/\d+$/, "");
const finitePoint = (p) => Array.isArray(p) && p.length === 3 && p.every(Number.isFinite);
const mm = (v) => Number.isFinite(v) ? `${v.toFixed(1)} mm` : "—";

function el(tag, className, text) {
  const n = document.createElement(tag);
  if (className) n.className = className;
  if (text != null) n.textContent = text;
  return n;
}
function button(className, text, action) {
  const n = el("button", className, text);
  n.type = "button";
  n.addEventListener("click", action);
  return n;
}
function option(value, text) { const n = el("option", null, text); n.value = value; return n; }
function field(label, input) { const n = el("label", "tube-field"); n.append(el("span", null, label), input); return n; }

// The export adapter is the only place the viewer reads the sidecar's fields.
export function tubeRunsFrom(data) {
  if (!data || !Array.isArray(data.runs)) throw new Error("Tube route data is unavailable for this model.");
  return data.runs.filter((run) => /^lldpe(?:-|$)/i.test(run.material || "")).map((run) => ({
    ...run,
    bodies: (run.bodies || []).filter(Boolean),
    label: run.label || run.id,
    points: run.points,
    arcLengths: run.s,
    radiusMm: run.radius_mm,
    radiusRanges: (run.insulation || []).filter((sleeve) => sleeve.s_range?.length === 2)
      .map((sleeve) => ({ s0: sleeve.s_range[0], s1: sleeve.s_range[1], radiusMm: sleeve.radius_mm })),
    minBendRadiusMm: run.min_bend_radius_mm,
    from: run.ends?.[0]?.port,
    to: run.ends?.[1]?.port,
    endTangents: run.ends?.length === 2 ? [run.ends[0].tangent, run.ends[1].tangent.map((v) => -v)] : undefined,
    excludeNames: [...(run.bodies || []), ...(run.insulation || []).map((sleeve) => sleeve.body)].filter(Boolean),
    allowedContacts: [...(run.ends || []), ...(run.holds || [])].filter((site) => site.host && site.contact_s?.length === 2)
      .map((site) => ({ name: site.host, s0: site.contact_s[0], s1: site.contact_s[1], holdId: site.id })),
    holds: (run.holds || []).map((hold, i) => ({ ...hold,
      id: hold.id || `${run.id}-hold-${i}`, body: hold.host, kind: hold.type, clampLengthMm: hold.clamp_length_mm,
    })),
  })).filter((run) => run.id && Array.isArray(run.points) && run.points.length >= 2 && run.points.every(finitePoint));
}

function pointAt(points, distance) {
  let s = 0;
  for (let i = 1; i < points.length; i++) {
    const a = new THREE.Vector3(...points[i - 1]);
    const b = new THREE.Vector3(...points[i]);
    const length = a.distanceTo(b);
    if (s + length >= distance) return a.lerp(b, length ? (distance - s) / length : 0);
    s += length;
  }
  return new THREE.Vector3(...points.at(-1));
}

function disposeChildren(group) {
  for (const child of [...group.children]) {
    group.remove(child);
    child.traverse((n) => {
      n.geometry?.dispose();
      for (const material of Array.isArray(n.material) ? n.material : [n.material]) material?.dispose();
    });
  }
}

export function createTubeOverlay({ wrapper, onClose }) {
  let enabled = false, disposed = false, file = null, data = null, runs = [], run = null;
  let worker = null, workerBusy = false, job = 0, fetchJob = 0, debounce = null, flyJob = 0;
  let results = null, selectedHold = null, contactResults = null;
  let fetchAbort = null;
  const overlay = new THREE.Group();
  overlay.name = "tube-overlay";
  overlay.visible = false;
  overlay.renderOrder = 990;
  scene.add(overlay);
  const panel = el("section", "tube-panel");
  panel.setAttribute("aria-label", "Tube shape review");
  panel.hidden = true;
  panel.dataset.state = "loading";
  const head = el("div", "edge-panel-head");
  head.append(el("span", "edge-panel-title", "Tube shapes"));
  const collapse = makePanelCollapse(panel, "tube-panel-collapsed");
  head.append(collapse);
  const close = button("edge-panel-close", "×", onClose);
  close.setAttribute("aria-label", "Close tube review");
  head.append(close);
  panel.append(head);
  const body = el("div", "tube-panel-body");
  const note = el("p", "tube-note", "Illustrative LLDPE shapes between real holds. These are assumptions for review, not a measured prediction.");
  body.append(note);

  const runSelect = el("select", "tube-run");
  body.append(field("Tube run", runSelect));
  const runDescription = el("p", "tube-route-description");
  body.append(runDescription);
  const runActions = el("div", "tube-actions");
  runActions.append(button("tube-focus-run", "Show run", () => {
    if (!run) return;
    const points = [...run.points];
    for (const [id, result] of Object.entries(results || {})) {
      if ((id === scenarioSelect.value || variants.checked) && result.diagnostics?.status !== "infeasible") points.push(...result.points);
    }
    focusPoints(points);
  }));
  runActions.append(button("tube-reset", "Reset assumptions", reset));
  body.append(runActions);

  const scenarioSelect = el("select", "tube-scenario");
  for (const [id, name] of Object.entries(SCENARIOS)) scenarioSelect.append(option(id, name));
  body.append(field("Stock assumption", scenarioSelect));
  const coilRadius = el("input", "tube-coil-radius");
  coilRadius.type = "number"; coilRadius.min = "75"; coilRadius.max = "1000"; coilRadius.step = "25"; coilRadius.value = "250";
  const coilField = field("Assumed coil radius (mm)", coilRadius);
  body.append(coilField);
  const coilPlane = el("select", "tube-coil-plane");
  for (const [id, name] of [["xy", "XY (horizontal)"], ["xz", "XZ (vertical)"], ["yz", "YZ (vertical)"]]) coilPlane.append(option(id, name));
  const planeField = field("Assumed coil plane", coilPlane); body.append(planeField);
  const variants = el("input", "tube-variants"); variants.type = "checkbox";
  body.append(field("Compare all three assumptions", variants));
  const omit = el("select", "tube-omit");
  body.append(field("Temporarily omit a hold", omit));
  const whatIf = el("p", "tube-what-if");
  body.append(whatIf);

  const legend = el("div", "tube-legend");
  for (const [kind, label] of [["nominal", "CAD route"], ["straight", "Assumed shape"], ["hold", "Real hold"]]) {
    const item = el("span", `tube-key ${kind}`, label); legend.append(item);
  }
  body.append(legend);
  const status = el("p", "tube-status", "Loading tube routes…");
  status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
  body.append(status);
  const diagnostics = el("div", "tube-diagnostics"); body.append(diagnostics);
  const holdsSection = el("details", "tube-holds"); holdsSection.open = true;
  holdsSection.append(el("summary", null, "Fittings and real holds"));
  const holdsList = el("div", "tube-hold-list"); holdsSection.append(holdsList); body.append(holdsSection);
  const spansSection = el("details", "tube-spans");
  spansSection.append(el("summary", null, "Unsupported spans"));
  const spansList = el("div", "tube-span-list"); spansSection.append(spansList); body.append(spansSection);
  const assumptions = el("details", "tube-assumptions");
  assumptions.append(el("summary", null, "What this view assumes"));
  assumptions.append(el("p", null, "Lines mark tube centerlines. The modeled length and fitting exits are retained. Each retained hold fixes the same tube section in position and direction across its seat width; sliding is not modeled. The path can relax between those holds. The coil radius and plane are assumptions; + and − bend in opposite senses. Gravity, friction, pressure, material stiffness and insulation stiffness are not modeled. Contacts are reported separately; the tube does not push against surrounding parts."));
  body.append(assumptions);
  panel.append(body);
  wrapper.append(panel);
  for (const type of ["pointerdown", "pointermove", "pointerup", "wheel"]) panel.addEventListener(type, (e) => e.stopPropagation());
  const resize = new ResizeObserver(updateLineSizes); resize.observe(wrapper);
  const onOtherTool = () => { if (enabled && !panel.classList.contains("collapsed")) collapse.click(); };
  window.addEventListener(HSM_EVENTS.STEP_TOOL, onOtherTool);
  const onChromeClick = (event) => {
    if (event.target.closest(".pick-find-toggle")) onOtherTool();
  };
  wrapper.addEventListener("click", onChromeClick);
  const cancelFocus = () => { flyJob++; };
  controls.addEventListener("start", cancelFocus);
  controls.addEventListener("change", updateMarkerSizes);

  function stateMessage(kind, text) { panel.dataset.state = kind; status.textContent = text; }
  function controlsReady(ready) {
    for (const input of [runSelect, scenarioSelect, coilRadius, coilPlane, variants, omit, ...runActions.querySelectorAll("button")]) input.disabled = !ready;
  }
  function updateLineSizes() {
    const size = renderer.getDrawingBufferSize(new THREE.Vector2());
    overlay.traverse((n) => { if (n.material?.resolution) n.material.resolution.copy(size); });
    updateMarkerSizes();
  }
  function updateMarkerSizes() {
    const height = Math.max(1, renderer.domElement.clientHeight);
    const perPixel = 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) / height;
    for (const child of overlay.children) {
      if (child.userData.markerPixels) child.scale.setScalar(child.userData.markerPixels * perPixel * child.position.distanceTo(camera.position));
    }
  }
  function makeLine(points, color, { dashed = false, opacity = 1, width = 3 } = {}) {
    const geometry = new LineGeometry().setPositions(points.flat());
    const material = new LineMaterial({ color, linewidth: width, transparent: true, opacity,
      depthTest: false, depthWrite: false, toneMapped: false, fog: false, dashed, dashSize: 4, gapSize: 2 });
    material.resolution.copy(renderer.getDrawingBufferSize(new THREE.Vector2()));
    const line = new Line2(geometry, material);
    line.computeLineDistances();
    line.renderOrder = 991;
    return line;
  }
  function marker(point, { omitted = false, endpoint = false, selected = false } = {}) {
    const geometry = endpoint ? new THREE.BoxGeometry(1, 1, 1) : new THREE.SphereGeometry(0.5, 12, 8);
    const material = new THREE.MeshBasicMaterial({ color: omitted ? COLORS.omitted : endpoint ? 0xe3e8ef : COLORS.hold,
      transparent: true, depthTest: false, depthWrite: false, toneMapped: false, fog: false, wireframe: omitted });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(point); mesh.renderOrder = 993;
    mesh.userData.markerPixels = selected ? 14 : endpoint ? 8 : 10;
    return mesh;
  }
  function visibleBody(name) {
    if (!name || !state.currentGroup) return true;
    name = bodyName(name);
    const meshes = state.currentGroup.children.filter((m) => m.isMesh && !m.userData.isXrayEdge && (bodyName(m.name) === name || bodyName(m.name).endsWith(`/${name}`)));
    return !meshes.length || meshes.some((m) => m.visible);
  }
  function syncVisibility() {
    overlay.visible = enabled && !!run && state.mountedDetail?.file === file && (run.bodies || [run.id]).some(visibleBody);
    if (run) panel.classList.toggle("tube-run-hidden", !overlay.visible);
    for (const child of overlay.children) if (child.userData.holdBody) child.visible = visibleBody(child.userData.holdBody);
    setExtraDepthBounds("tube-overlay", overlay.visible ? new THREE.Box3().setFromObject(overlay) : null);
  }
  function draw() {
    disposeChildren(overlay);
    syncLegend();
    if (!run) { syncVisibility(); return; }
    overlay.userData = { runId: run.id, scenario: scenarioSelect.value, omitHoldId: omit.value || null,
      coilPlane: coilPlane.value, coilRadiusMm: Math.min(1000, Math.max(75, Number(coilRadius.value) || 250)), results };
    const nominal = makeLine(run.points, COLORS.nominal, { dashed: true, width: 2 });
    nominal.name = "tube-nominal"; overlay.add(nominal);
    if (results) for (const [id, result] of Object.entries(results)) {
      const selected = scenarioSelect.value === id;
      if (!selected && !variants.checked) continue;
      if (result.diagnostics?.status === "infeasible") continue;
      if (!Array.isArray(result.points) || !result.points.every(finitePoint)) continue;
      const unfinished = result.diagnostics?.converged === false;
      const line = makeLine(result.points, unfinished ? 0xb5b8c9 : COLORS[id], { dashed: unfinished, width: selected ? 4 : 2, opacity: selected ? 1 : 0.55 });
      line.name = `tube-estimate-${id}`; overlay.add(line);
    }
    overlay.add(marker(new THREE.Vector3(...run.points[0]), { endpoint: true }));
    overlay.add(marker(new THREE.Vector3(...run.points.at(-1)), { endpoint: true }));
    for (const hold of run.holds) {
      const point = finitePoint(hold.point) ? new THREE.Vector3(...hold.point) : pointAt(run.points, hold.s);
      const mark = marker(point, { omitted: hold.id === omit.value, selected: hold.id === selectedHold });
      mark.name = `tube-hold-${hold.id}`;
      mark.userData.holdBody = hold.body || hold.component;
      overlay.add(mark);
    }
    updateMarkerSizes(); syncVisibility();
  }
  function syncLegend() {
    for (const key of legend.querySelectorAll(".tube-alt-key")) key.remove();
    const unfinished = results?.[scenarioSelect.value]?.diagnostics?.converged === false;
    const selected = legend.querySelector(".tube-key.straight");
    selected.textContent = unfinished ? "Unfinished solve" : SCENARIOS[scenarioSelect.value];
    selected.style.setProperty("--tube-estimate-color", unfinished ? "#b5b8c9" : `#${COLORS[scenarioSelect.value].toString(16)}`);
    if (variants.checked) for (const [id, name] of Object.entries(SCENARIOS)) {
      if (id === scenarioSelect.value) continue;
      const pending = results?.[id]?.diagnostics?.converged === false;
      const key = el("span", "tube-key tube-alt-key", `${name}${pending ? " (unfinished)" : ""}`);
      key.style.setProperty("--tube-key-color", pending ? "#b5b8c9" : `#${COLORS[id].toString(16)}`);
      legend.append(key);
    }
  }
  function focusPoints(points) {
    if (!points?.length) return;
    if (wrapper.clientWidth <= 600 && !panel.classList.contains("collapsed")) collapse.click();
    const box = new THREE.Box3().setFromPoints(points.map((p) => new THREE.Vector3(...p)));
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const radius = Math.max(size.length() / 2, 12.5);
    const vertical = THREE.MathUtils.degToRad(camera.fov) / 2;
    const horizontal = Math.atan(Math.tan(vertical) * camera.aspect);
    const distance = radius / Math.sin(Math.min(vertical, horizontal)) * 1.15;
    const direction = camera.position.clone().sub(controls.target).normalize();
    const startPosition = camera.position.clone(), startTarget = controls.target.clone();
    const destination = center.clone().addScaledVector(direction, distance);
    const token = ++flyJob, start = performance.now();
    function frame() {
      if (disposed || !enabled || token !== flyJob) return;
      const t = Math.min(1, (performance.now() - start) / 350), ease = t * (2 - t);
      camera.position.lerpVectors(startPosition, destination, ease);
      controls.target.lerpVectors(startTarget, center, ease); camera.lookAt(controls.target); controls.update();
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  function showHolds() {
    holdsList.replaceChildren();
    const endpoints = [{ id: "start", label: run.from || "Start fitting", point: run.points[0] },
      ...run.holds, { id: "end", label: run.to || "End fitting", point: run.points.at(-1) }];
    for (const hold of endpoints) {
      const name = hold.label || hold.id;
      const b = button("tube-hold-focus", name, () => {
        selectedHold = hold.id; draw();
        const p = finitePoint(hold.point) ? hold.point : pointAt(run.points, hold.s).toArray();
        focusPoints([p]);
      });
      b.dataset.holdId = hold.id;
      if (hold.id === omit.value) b.classList.add("omitted");
      b.append(el("small", null, hold.id === omit.value ? "Omitted in this what-if" : hold.kind || (Number.isFinite(hold.s) ? `At ${mm(hold.s)} along tube` : "Fitting exit")));
      holdsList.append(b);
    }
  }
  function showResults() {
    const result = results?.[scenarioSelect.value];
    diagnostics.replaceChildren(); spansList.replaceChildren();
    if (!result) return;
    const d = result.diagnostics || {};
    const solveStatus = d.status || (d.converged === false ? "iteration-limit" : "converged");
    const values = [["Largest shift from CAD", mm(d.maxDisplacementMm)], ["Tube length error", mm(Math.abs(d.lengthErrorMm))], ["Tightest resulting radius", mm(d.minRadiusMm)]];
    for (const [label, value] of values) { const row = el("div", "tube-metric"); row.append(el("span", null, label), el("strong", null, value)); diagnostics.append(row); }
    const warnings = [...(result.warnings || [])];
    if (d.converged === false) warnings.unshift(solveStatus === "infeasible"
      ? "The stated length, holds and fitting exits cannot be satisfied by this solve. No alternate shape is shown."
      : `Unfinished solve (${solveStatus === "iteration-limit" ? "iteration limit" : "stalled"}). The dashed result is a numerical intermediate, not a proposed tube shape.`);
    const invalid = !result.points?.every(finitePoint) || Math.abs(d.lengthErrorMm || 0) > Math.max(0.5, (d.lengthMm || 0) * 0.005);
    if (invalid) warnings.push("Tube length is not sufficiently preserved; this estimate cannot support an anchor decision.");
    omit.disabled = invalid || d.converged === false || !run.holds.length;
    stateMessage("ready", warnings.length ? warnings.join(" ") : "Estimate ready. Review the assumptions and possible contacts before judging a hold.");
    panel.dataset.solveStatus = solveStatus;
    syncLegend();
    status.classList.toggle("tube-warning", !!warnings.length);
    const contactBlock = el("div", "tube-contact-status"); diagnostics.append(contactBlock);
    if (run.radiusRanges.length) contactBlock.append(el("p", null, "Contact screening includes the insulation envelope along each sleeved stretch."));
    if (d.converged === false) contactBlock.append(el("p", null, "Contact locations belong to an unfinished solve and cannot establish the need for an anchor."));
    renderContacts(contactBlock, result.contactScreen);
    for (const [index, span] of (result.spans || []).entries()) {
      const b = button("tube-span-focus", `Span ${index + 1} · ${mm(span.lengthMm)} between holds`, () => {
        const pts = result.points.filter((_, i) => result.arcLengths?.[i] >= span.startS && result.arcLengths?.[i] <= span.endS);
        focusPoints(pts.length ? pts : result.points);
      });
      b.dataset.spanIndex = index;
      b.append(el("small", null, `${mm(span.slackMm)} beyond the straight chord · largest shift ${mm(span.maxDisplacementMm)}`));
      spansList.append(b);
    }
  }
  function renderContacts(node, report) {
    if (!report) { node.textContent = "Contacts are not screened. Shapes can cross surrounding parts."; return; }
    const contacts = report.contacts || [], nominal = contactResults?.contacts || [];
    const result = results?.[scenarioSelect.value];
    const arc = result?.arcLengths || [];
    const fresh = newTubeContacts(contactResults, report, { nominalArcLengths: run.arcLengths, arcLengths: arc });
    const names = new Set(fresh.map((c) => c.name));
    node.append(el("p", names.size ? "tube-contact-warning" : null, names.size
      ? `${names.size} part${names.size === 1 ? " has" : "s have"} possible new surface contact. The estimated tube passes through these parts.`
      : contacts.length ? "Contact candidates fall within the CAD route's sampled contact segments." : "No surface contact found for this assumption."));
    const details = el("details", "tube-contact-details");
    details.append(el("summary", null, `${report.totalContacts ?? contacts.length} estimated / ${contactResults?.totalContacts ?? nominal.length} CAD contact samples`));
    details.append(el("p", null, "Includes hidden parts. Surface screening does not detect tube self-contact or guarantee clearance for a tube wholly inside a solid."));
    for (const name of [...new Set(contacts.map((c) => c.name))]) {
      const found = contacts.filter((c) => c.name === name);
      const b = button("tube-contact-focus", `${name}${names.has(name) ? " · new location" : " · CAD contact location"}`, () => focusPoints(found.map((c) => c.point)));
      details.append(b);
    }
    if (report.truncated || contactResults?.truncated) details.append(el("p", null, "The contact list is incomplete; additional locations may be omitted from this comparison."));
    node.append(details);
  }
  function terminate() { worker?.terminate(); worker = null; workerBusy = false; job++; }
  function buildWorker() {
    const version = state.codeVersion;
    const workerUrl = new URL(`./tube-overlay-worker.js${version ? `?v=${encodeURIComponent(version)}` : ""}`, import.meta.url);
    worker = new Worker(workerUrl, { type: "module" });
    const meshes = [], transfer = [];
    state.currentGroup?.updateMatrixWorld(true);
    for (const mesh of state.currentGroup?.children || []) {
      if (!mesh.isMesh || mesh.userData.isXrayEdge) continue;
      const source = mesh.geometry.getAttribute("position");
      if (!source) continue;
      const positions = new Float32Array(source.count * 3);
      const point = new THREE.Vector3();
      for (let i = 0; i < source.count; i++) {
        point.fromBufferAttribute(source, i).applyMatrix4(mesh.matrixWorld);
        point.toArray(positions, i * 3);
      }
      const indices = mesh.geometry.index ? new Uint32Array(mesh.geometry.index.array) : Uint32Array.from({ length: source.count }, (_, i) => i);
      meshes.push({ name: mesh.name, positions, indices }); transfer.push(positions.buffer, indices.buffer);
    }
    worker.postMessage({ type: "init", meshes }, transfer);
  }
  function solve() {
    clearTimeout(debounce); debounce = null;
    if (!enabled || disposed || !run) return;
    if (workerBusy) terminate();
    results = null; contactResults = null; draw();
    diagnostics.replaceChildren(); spansList.replaceChildren();
    stateMessage("solving", "Relaxing the tube between its real holds…");
    status.classList.remove("tube-warning");
    const own = ++job;
    try { if (!worker) buildWorker(); }
    catch (error) { stateMessage("error", `Tube review could not start: ${error.message}`); return; }
    worker.onmessage = ({ data: reply }) => {
      if (disposed || !enabled || own !== job || reply.id !== own) return;
      workerBusy = false;
      if (reply.error) { stateMessage("error", `Could not calculate this tube: ${reply.error}`); return; }
      results = reply.results; contactResults = reply.nominalContacts; draw(); showResults();
    };
    worker.onerror = (error) => { if (own === job) stateMessage("error", `Tube calculation stopped: ${error.message}`); };
    workerBusy = true;
    worker.postMessage({ id: own, run, options: { omitHoldId: omit.value || undefined, coilRadiusMm: Math.min(1000, Math.max(75, Number(coilRadius.value) || 250)), coilNormal: COIL_NORMALS[coilPlane.value], sampleSpacingMm: 6, maxIterations: 800 } });
  }
  function schedule() {
    if (workerBusy) terminate();
    results = null; contactResults = null; draw();
    diagnostics.replaceChildren(); spansList.replaceChildren();
    stateMessage("solving", "Updating the assumed shape…");
    clearTimeout(debounce); debounce = setTimeout(solve, 180);
    whatIf.textContent = omit.value ? "What-if only: the selected hold is omitted from the calculation. CAD and assembly instructions are unchanged." : "All listed holds are retained.";
    showHolds();
  }
  function chooseRun(id) {
    cancelFocus();
    run = runs.find((r) => r.id === id) || runs[0] || null;
    if (!run) { stateMessage("error", "This model has no supported tube routes."); return; }
    controlsReady(true);
    runSelect.value = run.id; selectedHold = null;
    runDescription.textContent = [run.from, run.to].filter(Boolean).join(" → ");
    if (Number.isFinite(run.unsupported_span_authored_mm)) runDescription.append(el("span", "tube-run-span", `Longest span between holds: ${mm(run.unsupported_span_authored_mm)}.`));
    omit.replaceChildren(option("", "Keep every hold"));
    for (const hold of run.holds) omit.append(option(hold.id, hold.label || hold.id));
    omit.disabled = !run.holds.length;
    whatIf.textContent = "All listed holds are retained.";
    showHolds(); solve();
  }
  function reset() {
    scenarioSelect.value = "straight"; coilRadius.value = "250"; coilPlane.value = "xy"; variants.checked = false; omit.value = "";
    coilField.hidden = planeField.hidden = true; selectedHold = null; chooseRun(run?.id);
  }
  runSelect.addEventListener("change", () => chooseRun(runSelect.value));
  scenarioSelect.addEventListener("change", () => { coilField.hidden = planeField.hidden = scenarioSelect.value === "straight" && !variants.checked; draw(); showResults(); });
  variants.addEventListener("change", () => { coilField.hidden = planeField.hidden = scenarioSelect.value === "straight" && !variants.checked; draw(); });
  coilRadius.addEventListener("input", schedule);
  coilPlane.addEventListener("change", schedule);
  omit.addEventListener("change", schedule);
  coilField.hidden = planeField.hidden = true;
  controlsReady(false);

  async function loadModel(nextFile, { reload = false } = {}) {
    if (disposed || (!reload && file === nextFile && data)) return;
    const previousRunId = run?.id;
    file = nextFile; data = null; run = null;
    terminate(); fetchAbort?.abort(); fetchAbort = new AbortController();
    const own = ++fetchJob;
    controlsReady(false);
    stateMessage("loading", "Loading tube routes…");
    results = null; draw();
    try {
      const response = await fetch(`/api/tube-routes/${nextFile}`, { cache: "no-cache", signal: fetchAbort.signal });
      if (!response.ok) throw new Error(`No tube review data for this model (${response.status}).`);
      const incoming = await response.json();
      if (disposed || own !== fetchJob) return;
      if (state.mountedDetail?.surface !== "mesh" || !state.mountedDetail?.payloadSha256) {
        throw new Error("Tube review requires a verified assembly mesh. Reopen this assembly in a browser with secure Web Crypto support.");
      }
      if (!incoming.source?.payload_sha256 || incoming.source.payload_sha256 !== state.mountedDetail.payloadSha256) {
        throw new Error("Tube data does not match the displayed assembly surface. Reload the assembly after its tube export is rebuilt.");
      }
      if (incoming.status !== "current" || (incoming.source?.payload_src && state.mountedDetail?.src && incoming.source.payload_src !== state.mountedDetail.src)) {
        throw new Error(`Tube data does not match the displayed assembly. ${incoming.staleReasons?.join(" ") || "The route export needs to be rebuilt."}`);
      }
      data = incoming; runs = tubeRunsFrom(incoming);
      runSelect.replaceChildren();
      for (const r of runs) runSelect.append(option(r.id, `${r.id}${r.label !== r.id ? ` · ${r.label}` : ""}`));
      chooseRun(runs.some((r) => r.id === previousRunId) ? previousRunId : runs.some((r) => r.id === "fluid-18") ? "fluid-18" : runs[0]?.id);
    } catch (error) {
      if (disposed || own !== fetchJob || error.name === "AbortError") return;
      data = null; run = null; draw(); controlsReady(false); stateMessage("error", error.message);
    }
  }
  function setEnabled(on) {
    enabled = !!on; panel.hidden = !enabled;
    if (!enabled) { terminate(); clearTimeout(debounce); flyJob++; }
    else { closePickFind(); if (run && !results) solve(); }
    syncVisibility();
  }
  function dispose() {
    disposed = true; enabled = false; terminate(); clearTimeout(debounce); fetchAbort?.abort(); flyJob++;
    resize.disconnect(); window.removeEventListener(HSM_EVENTS.STEP_TOOL, onOtherTool);
    wrapper.removeEventListener("click", onChromeClick);
    controls.removeEventListener("start", cancelFocus);
    controls.removeEventListener("change", updateMarkerSizes);
    setExtraDepthBounds("tube-overlay", null);
    disposeChildren(overlay); scene.remove(overlay); panel.remove();
  }
  return { loadModel, setEnabled, syncVisibility, cancelFocus, dispose };
}
