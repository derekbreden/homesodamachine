// The tube audit is loaded only when its chip is opened. This module carries
// the small hooks shared by the CAD modal, STEP reload and component visibility.
import { state } from "./state.js";
import { makeToolChip } from "./tool-rail.js";

const MODELS = new Set(["manifold-layout/enclosure-assembly.step"]);
let mounted = null;

function refresh() {
  if (!mounted) return;
  const file = state.mountedDetail?.file || state.currentDetail?.file;
  const supported = MODELS.has(file);
  mounted.chip.hidden = !supported;
  if (!supported) {
    mounted.enabled = false;
    mounted.controller?.setEnabled(false);
  }
  mounted.chip.refresh();
}

async function setEnabled(on) {
  const own = mounted;
  if (!own) return;
  own.enabled = !!on;
  own.chip.refresh();
  if (!on) { own.controller?.setEnabled(false); return; }
  try {
    own.chip.setAttribute("aria-busy", "true");
    const version = state.codeVersion;
    const mod = await import(`./tube-overlay.js${version ? `?v=${encodeURIComponent(version)}` : ""}`);
    if (mounted !== own || !own.enabled) return;
    if (!own.controller) own.controller = mod.createTubeOverlay({
      wrapper: own.wrapper,
      onClose: () => setEnabled(false),
    });
    own.controller.setEnabled(true);
    await own.controller.loadModel(state.mountedDetail?.file || state.currentDetail?.file);
  } catch (error) {
    if (mounted !== own) return;
    own.enabled = false;
    own.chip.title = `Tube review could not open: ${error.message}`;
    own.chip.refresh();
    console.warn("tube review:", error);
  } finally {
    if (mounted === own) own.chip.removeAttribute("aria-busy");
  }
}

export function mountTubeTool(wrapper, chips) {
  clearTubeTool();
  const own = { wrapper, enabled: false, controller: null, chip: null };
  own.chip = makeToolChip({
    className: "tube-toggle", label: "Tubes",
    title: "Compare the drawn tube route with illustrative shapes between its real holds",
    read: () => own.enabled,
    write: setEnabled,
  });
  mounted = own;
  chips.appendChild(own.chip);
  refresh();
}

export function onTubeModelLoaded(file) {
  refresh();
  if (mounted?.enabled) mounted.controller?.loadModel(file, { reload: true });
}

export function syncTubeVisibility() { mounted?.controller?.syncVisibility(); }
export function cancelTubeFocus() { mounted?.controller?.cancelFocus(); }

export function closeTubeTool() {
  if (!mounted?.enabled) return false;
  setEnabled(false);
  return true;
}

export function clearTubeTool() {
  const own = mounted;
  mounted = null;
  own?.controller?.dispose();
  own?.chip.remove();
}
