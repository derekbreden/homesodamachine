// Dispense A, in the coordinates of the loaded enclosure. Reuse the mounted
// tube surfaces, including the draw line inside the cold core; no second route
// or tube-audit sidecar can drift away from the assembly being inspected.
import * as THREE from "three";
import { scene, camera, controls, resetCamera } from "./scene.js";
import { state } from "./state.js";
import { isXrayEnabled, setXrayEnabled } from "./xray.js";
import { makeToolChip, makePanelCollapse } from "./tool-rail.js";
import { HSM_EVENTS } from "/contracts/client-events.js";

const ASSEMBLY = "manifold-layout/enclosure-assembly.step";
// The order follows fluid-topology.md's Dispense A operation: V-E and V-G
// open, pump A forward. The source and fitting bodies provide context at the
// joints; the six numbered tube runs and core draw are the routed surfaces.
const STOPS = [
  { label: "Reservoir A", detail: "Draw from the bottom bulkhead", bodies: ["cold-core/reservoir-a", "cold-core/bulkhead-reservoir-a"] },
  { label: "Pickup → cold-core cap", detail: "Internal draw line → fluid-16", bodies: ["cold-core/line-reservoir-a", "tube-fluid-16"] },
  { label: "V-E → inlet tee Y-C", detail: "Open inlet gate → fluid-10 → tee", bodies: ["valve-v-e", "tube-fluid-10", "tee-y-c"] },
  { label: "Pump A", detail: "fluid-11 → pump head → fluid-12", bodies: ["tube-fluid-11", "pump-a-head", "tube-fluid-12"] },
  { label: "Outlet tee Y-D → V-G", detail: "Tee → fluid-17 hairpin → open outlet gate", bodies: ["tee-y-d", "tube-fluid-17", "valve-v-g"] },
  { label: "Rear flavor A connection", detail: "fluid-18 → rear bulkhead", bodies: ["tube-fluid-18", "bulkhead-flavor-a"] },
];
const TUBES = new Set(STOPS.flatMap(s => s.bodies).filter(n => n.includes("line-reservoir-a") || n.startsWith("tube-")));
const COLOR = 0xffa733;

export function mountFlavorPath(wrapper, chips) {
  let enabled = new URLSearchParams(location.search).get("flow") === "flavor-a";
  let oldXray = null;
  let mountedGroup = null;
  let focusToken = 0;
  const overlay = new THREE.Group();
  overlay.name = "flavor-a-path";
  scene.add(overlay);

  const panel = document.createElement("section");
  panel.className = "flavor-path-panel";
  panel.setAttribute("aria-label", "Flavor A dispense path");
  const head = document.createElement("div");
  head.className = "edge-panel-head";
  const title = document.createElement("span");
  title.className = "edge-panel-title";
  title.textContent = "Flavor A · flow direction ↓";
  head.append(title, makePanelCollapse(panel, "flavor-path-collapsed", {
    defaultCollapsed: matchMedia("(max-width: 600px)").matches,
  }));
  panel.append(head);
  const list = document.createElement("ol");
  const buttons = STOPS.map((stop, index) => {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = stop.label;
    button.title = stop.detail;
    button.addEventListener("click", () => focus(index));
    const detail = document.createElement("small");
    detail.textContent = stop.detail;
    button.append(detail);
    item.append(button);
    list.append(item);
    return button;
  });
  const whole = document.createElement("button");
  whole.type = "button";
  whole.className = "flavor-path-whole";
  whole.textContent = "Whole enclosure";
  whole.addEventListener("click", () => { focusToken++; resetCamera(state.currentGroup); select(null); });
  const note = document.createElement("p");
  note.className = "flavor-path-note";
  note.textContent = "Amber follows the dispense path. The pump head is highlighted; its internal squeeze tube is not modeled.";
  panel.append(list, whole, note);
  wrapper.append(panel);

  function select(index) {
    buttons.forEach((button, i) => button.setAttribute("aria-pressed", String(i === index)));
  }

  function focus(index) {
    select(index);
    const wanted = new Set(STOPS[index].bodies);
    const box = new THREE.Box3();
    for (const mesh of state.currentGroup?.children || []) {
      if (mesh.userData.side === "front" && wanted.has(mesh.name)) box.expandByObject(mesh);
    }
    if (box.isEmpty()) return;
    const target = box.getCenter(new THREE.Vector3());
    const direction = camera.position.clone().sub(controls.target).normalize();
    const distance = Math.max(box.getSize(new THREE.Vector3()).length(), 70) * 2.6;
    const position = target.clone().addScaledVector(direction, distance);
    const from = camera.position.clone(), fromTarget = controls.target.clone();
    const started = performance.now(), token = ++focusToken;
    const duration = matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 350;
    function frame() {
      if (token !== focusToken || !enabled) return;
      const t = duration ? Math.min((performance.now() - started) / duration, 1) : 1;
      const ease = t * (2 - t);
      camera.position.lerpVectors(from, position, ease);
      controls.target.lerpVectors(fromTarget, target, ease);
      controls.update();
      if (t < 1) requestAnimationFrame(frame);
    }
    frame();
  }

  function clear() {
    focusToken++;
    for (const object of [...overlay.children]) {
      overlay.remove(object);
      // Tube shells borrow the live model's geometry; only edges belong here.
      if (object.isLineSegments) object.geometry.dispose();
      object.material.dispose();
    }
    overlay.userData.bodies = [];
  }

  function refresh() {
    const supported = (state.mountedDetail?.file || state.currentDetail?.file) === ASSEMBLY;
    chip.hidden = !supported;
    panel.hidden = !supported || !enabled;
    chip.refresh();
    clear();
    if (!supported && oldXray !== null) {
      if (oldXray === false && isXrayEnabled()) setXrayEnabled(false, { persist: false });
      wrapper.querySelector(".xray-toggle")?.refresh();
      oldXray = null;
    }
    if (!supported || !enabled || !state.currentGroup) return;
    if (oldXray === null) oldXray = isXrayEnabled();
    if (!isXrayEnabled()) setXrayEnabled(true, { persist: false });
    wrapper.querySelector(".xray-toggle")?.refresh();
    mountedGroup = state.currentGroup;
    const wanted = new Set(STOPS.flatMap(s => s.bodies));
    const found = new Set();
    for (const mesh of mountedGroup.children) {
      if (mesh.userData.side !== "front" || !wanted.has(mesh.name)) continue;
      found.add(mesh.name);
      const tube = TUBES.has(mesh.name);
      const shell = new THREE.Mesh(mesh.geometry, new THREE.MeshBasicMaterial({
        color: COLOR, transparent: true, opacity: tube ? 1 : 0.20,
        depthTest: false, depthWrite: false, side: THREE.DoubleSide,
      }));
      shell.name = mesh.name;
      shell.renderOrder = tube ? 992 : 990;
      overlay.add(shell);
      if (!tube) {
        const edge = new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry, 30),
          new THREE.LineBasicMaterial({ color: COLOR, transparent: true, opacity: 0.8, depthTest: false, depthWrite: false }));
        edge.renderOrder = 991;
        overlay.add(edge);
      }
    }
    overlay.userData.bodies = [...found];
    const missing = [...wanted].filter(name => !found.has(name));
    note.textContent = missing.length
      ? `This model is missing part of the path: ${missing.join(", ")}.`
      : "Amber follows the dispense path. The pump head is highlighted; its internal squeeze tube is not modeled.";
    select(null);
  }

  const chip = makeToolChip({
    className: "flavor-path-toggle", label: "Flavor A",
    title: "Trace reservoir A through its draw line, pump and rear outlet",
    read: () => enabled,
    write(on) {
      enabled = on;
      const url = new URL(location.href);
      if (on) url.searchParams.set("flow", "flavor-a");
      else url.searchParams.delete("flow");
      history.replaceState(history.state, "", url);
      if (!on && oldXray !== null) {
        if (oldXray === false && isXrayEnabled()) setXrayEnabled(false, { persist: false });
        wrapper.querySelector(".xray-toggle")?.refresh();
        oldXray = null;
      }
      refresh();
    },
  });
  chips.append(chip);
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, refresh);
  // A gesture always wins over a pending stop's camera animation.
  const cancelFocus = () => { focusToken++; };
  controls.addEventListener("start", cancelFocus);
  refresh();
  return () => {
    window.removeEventListener(HSM_EVENTS.STEP_MOUNTED, refresh);
    controls.removeEventListener("start", cancelFocus);
    clear();
    scene.remove(overlay);
    if (oldXray === false && isXrayEnabled() && state.currentGroup === mountedGroup) setXrayEnabled(false, { persist: false });
    chip.remove();
    panel.remove();
  };
}
