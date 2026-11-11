// Location browsing reuses the open canvas to preview each installed unit and its assembly.
import { state } from "./state.js";
import { camera, controls } from "./scene.js";
import { previewStep } from "./step-nav.js";
import { clearHighlight, scenePartNames } from "./part-highlight.js";
import { clearComponentSelection } from "./component-picker.js";
import { clearInstancePreview, enterInstance } from "./instance-view.js";
import { matchesBody } from "/contracts/materials.js";
import { instanceBody } from "/contracts/features.js";

const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

export function makeMaterialLocations({ material, beforeScene, onEnter }) {
  const origin = { file: state.currentDetail?.file, position: camera.position.clone(),
    target: controls.target.clone(), up: camera.up.clone() };
  const node = el("section", "material-locations");
  node.setAttribute("aria-label", "Installed locations");
  node.dataset.material = material;
  const title = el("h3", "", "Locations"), assembly = el("select", "location-assembly");
  assembly.setAttribute("aria-label", "Preview assembly"); assembly.hidden = true;
  const controlsRow = el("div", "location-controls");
  const previous = el("button", "location-previous", "←"), position = el("span", "location-position"), next = el("button", "location-next", "→");
  previous.setAttribute("aria-label", "Previous location"); next.setAttribute("aria-label", "Next location");
  const all = el("button", "location-all", "All locations"); all.setAttribute("aria-pressed", "false");
  for (const button of [previous, next, all]) button.type = "button";
  controlsRow.append(previous, position, next, all); controlsRow.hidden = true;
  const label = el("strong", "location-label"), path = el("p", "material-path location-path");
  const go = el("a", "location-go", "Go to location →"); go.hidden = true;
  const note = el("p", "material-scope", "Finding installed locations…"); note.setAttribute("role", "status");
  node.append(title, assembly, controlsRow, label, path, go, note);
  let groups = [], groupIndex = 0, at = 0, disposed = false, generation = 0, framed = 0;
  let viewedGroup = null;
  let ready = Promise.resolve(false), finishPreview = () => {};
  const current = () => groups[groupIndex];
  const selection = () => current() && at >= 0 ? { group: current(), instance: current().instances[at] } : null;
  const bodies = () => current() ? (at < 0 ? current().instances : [current().instances[at]]).flatMap(instance => instance.bodies) : [];

  function describe() {
    const group = current(), item = selection()?.instance;
    if (!group) return;
    const count = group.instances.length;
    controlsRow.hidden = false;
    previous.disabled = next.disabled = count < 2;
    all.hidden = count < 2;
    all.setAttribute("aria-pressed", String(at < 0));
    position.textContent = at < 0 ? `All ${count}` : `${at + 1} / ${count}`;
    label.textContent = item?.label || "All locations";
    path.textContent = [group.label, ...(item?.path || [])].join(" › ");
    go.hidden = !item;
    if (item) go.href = item.url;
    node.dataset.instance = item?.name || "";
  }

  function draw() {
    const group = current();
    if (disposed || !group || state.mountedDetail?.file !== group.file) return;
    if (framed === generation && viewedGroup === state.currentGroup) return;
    const mounted = scenePartNames();
    const bindings = bodies();
    const manifest = state.currentGroup?.userData.sharedHead;
    const available = manifest ? manifest.meshes.flatMap(node =>
      node.entries?.map(entry => instanceBody(entry.name)) || [node.name]) : [...mounted];
    const names = [...new Set(available.filter(name => bindings.some(body => matchesBody(name, body))))];
    if (!names.length || !names.every(name => mounted.has(name))) return;
    const locations = at < 0 ? group.instances.map(instance =>
      names.filter(name => instance.bodies.some(body => matchesBody(name, body)))) : [names];
    enterInstance(null, { members: names, locations, fly: framed !== generation, preview: true });
    framed = generation;
    viewedGroup = state.currentGroup;
    note.textContent = "";
    finishPreview(true);
  }

  async function preview() {
    const group = current();
    if (disposed || !group) return;
    const run = ++generation;
    finishPreview(false);
    ready = new Promise(resolve => { finishPreview = resolve; });
    describe();
    note.textContent = "Loading location preview…";
    clearComponentSelection();
    beforeScene(group.file);
    draw();
    if (framed === run) return;
    const names = bodies(), sameFile = state.mountedDetail?.file === group.file;
    if (!sameFile || state.currentGroup?.userData.sceneLoading) {
      await previewStep(group.file, { target: { bodies: names }, retarget: sameFile });
    }
    if (disposed || run !== generation) return;
    draw();
    if (framed !== run) {
      note.textContent = "The location model could not be loaded.";
      finishPreview(false);
    }
  }

  const requestPreview = () => preview();
  previous.addEventListener("click", () => { at = at <= 0 ? current().instances.length - 1 : at - 1; requestPreview(); });
  next.addEventListener("click", () => { at = (at + 1) % current().instances.length; requestPreview(); });
  all.addEventListener("click", () => { at = at < 0 ? 0 : -1; requestPreview(); });
  assembly.addEventListener("change", () => { groupIndex = Number(assembly.value); at = 0; requestPreview(); });
  async function enter() {
    const run = generation;
    if (!await ready) return;
    const chosen = selection();
    if (!disposed && run === generation && chosen) onEnter(chosen.group, chosen.instance);
  }
  go.addEventListener("click", event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    enter();
  });

  async function discover() {
    try {
      const response = await fetch(`/api/material-instances/${encodeURIComponent(material)}?finish=${encodeURIComponent(state.faucetFinish)}`);
      if (!response.ok) throw new Error("Installed locations unavailable");
      const result = await response.json();
      if (disposed) return;
      groups = result.groups;
      if (!groups.length) { note.textContent = "No installed locations drawn in an assembly."; return; }
      groupIndex = Math.max(0, groups.findIndex(group => group.file === state.mountedDetail?.file));
      for (const [index, group] of groups.entries()) {
        const option = el("option", "", group.label); option.value = index; assembly.append(option);
      }
      assembly.value = groupIndex; assembly.hidden = groups.length < 2;
      await requestPreview();
    } catch {
      if (disposed) return;
      note.textContent = "Installed locations could not be loaded. ";
      const retry = el("button", "location-retry", "Retry"); retry.type = "button";
      retry.addEventListener("click", () => { note.textContent = "Finding installed locations…"; discover(); });
      note.append(retry);
    }
  }
  discover();
  return { material, node, selection, bodies, enter, sync: draw,
    async dispose({ restore = false, keepView = false } = {}) {
      if (disposed) return;
      disposed = true; generation++;
      finishPreview(false);
      clearHighlight({ owner: "materials" });
      if (!keepView) clearInstancePreview();
      if (!restore || !origin.file || state.currentDetail?.file !== current()?.file) return;
      beforeScene(origin.file);
      await previewStep(origin.file);
      if (state.mountedDetail?.file !== origin.file || state.currentDetail?.file !== origin.file) return;
      camera.position.copy(origin.position); camera.up.copy(origin.up); controls.target.copy(origin.target);
      controls.update();
    },
  };
}
