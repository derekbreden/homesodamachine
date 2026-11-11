// The selection control reflects the component and edge pickers' shared click mode.

import { makeToolSeg } from "./tool-rail.js";
import {
  setEdgePickEnabled, isEdgePickEnabled, setEdgeToggleRefresh,
} from "./edge-picker.js";
import {
  setComponentPickEnabled, isComponentPickEnabled, setComponentToggleRefresh,
} from "./component-picker.js";

const MODES = [
  { id: "off", label: "Off", icon: "pick-off", title: "Clicks orbit the model" },
  { id: "component", label: "Component", icon: "pick-component", title: "Click a solid to select the component it belongs to" },
  { id: "edge", label: "Edge", icon: "pick-edge", title: "Click an edge or a face to read its geometry" },
];

function currentMode() {
  if (isComponentPickEnabled()) return "component";
  if (isEdgePickEnabled()) return "edge";
  return "off";
}

function armMode(id) {
  // Arming disarms the others through STEP_TOOL; disarming is per-module, so
  // `off` says so to whichever one is holding the click.
  if (id === "component") setComponentPickEnabled(true);
  else if (id === "edge") setEdgePickEnabled(true);
  else {
    setComponentPickEnabled(false);
    setEdgePickEnabled(false);
  }
}

export function makePickModeControl() {
  const seg = makeToolSeg(MODES, (id) => { armMode(id); seg.sync(currentMode()); });
  const sync = () => seg.sync(currentMode());
  setEdgeToggleRefresh(sync);
  setComponentToggleRefresh(sync);
  sync();

  return seg;
}
