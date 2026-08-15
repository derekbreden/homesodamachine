// The one control over what a click on the model does. Three modes reach it —
// the component picker (component-picker.js), the edge/face picker
// (edge-picker.js), and the dev-only editor (component-edit.js) — and they are
// already exclusive: each announces itself over HSM_EVENTS.STEP_TOOL on arming
// and the others stand down. So the state this control shows is one of `off`,
// `component`, `edge`, `edit`, and picking a segment is arming that mode.
//
// Each module still owns its own state; this reads it back through the
// is*Enabled getters and registers `sync` as the refresh they call when
// something else in the room changed the mode.

import { makeToolSeg } from "./tool-rail.js";
import {
  setEdgePickEnabled, isEdgePickEnabled, setEdgeToggleRefresh,
} from "./edge-picker.js";
import {
  setComponentPickEnabled, isComponentPickEnabled, setComponentToggleRefresh,
} from "./component-picker.js";
import {
  setComponentEditEnabled, isComponentEditEnabled, setEditToggleRefresh, probeEditor,
} from "./component-edit.js";

const MODES = [
  { id: "off", label: "Off", icon: "pick-off", title: "Clicks orbit the model" },
  { id: "component", label: "Component", icon: "pick-component", title: "Click a solid to select the component it belongs to" },
  { id: "edge", label: "Edge", icon: "pick-edge", title: "Click an edge or a face to read its geometry" },
];
// Appended only once the step-editor API answers for this file.
const EDIT_MODE = { id: "edit", label: "Edit", icon: "pick-edit", className: "edit", title: "Drag a component to a new place in the source" };

function currentMode() {
  if (isComponentEditEnabled()) return "edit";
  if (isComponentPickEnabled()) return "component";
  if (isEdgePickEnabled()) return "edge";
  return "off";
}

function armMode(id) {
  // Arming disarms the others through STEP_TOOL; disarming is per-module, so
  // `off` says so to whichever one is holding the click.
  if (id === "component") setComponentPickEnabled(true);
  else if (id === "edge") setEdgePickEnabled(true);
  else if (id === "edit") setComponentEditEnabled(true);
  else {
    setComponentPickEnabled(false);
    setEdgePickEnabled(false);
    setComponentEditEnabled(false);
  }
}

export function makePickModeControl(file) {
  const seg = makeToolSeg(MODES, (id) => { armMode(id); seg.sync(currentMode()); });
  const sync = () => seg.sync(currentMode());
  setEdgeToggleRefresh(sync);
  setComponentToggleRefresh(sync);
  setEditToggleRefresh(sync);
  sync();

  probeEditor(file).then((ok) => {
    if (!ok || !seg.isConnected) return;
    seg.addOption(EDIT_MODE, () => { armMode(EDIT_MODE.id); sync(); });
    sync();
  });

  return seg;
}
