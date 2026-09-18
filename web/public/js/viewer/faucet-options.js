// Faucet choices live with the model. Style loads the printable assembly;
// finish swaps only its PET-GF materials and takes no network round trip.
import { FAUCET_STYLES, FAUCET_FINISHES, faucetStyleFor, hasFaucetFinish } from "/contracts/faucet-options.js";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { state } from "./state.js";
import { setFaucetFinish } from "./step.js";
import { switchStepVariant } from "./step-nav.js";

export function mountFaucetOptions(wrapper) {
  const panel = document.createElement("details");
  panel.className = "faucet-options";
  panel.setAttribute("aria-label", "Faucet options");
  const mobile = matchMedia("(max-width: 600px)");
  const compact = () => { panel.open = !mobile.matches; };
  compact();
  mobile.addEventListener("change", compact);
  const summary = document.createElement("summary");
  summary.textContent = "Style and finish";
  const current = document.createElement("span");
  summary.appendChild(current);
  panel.appendChild(summary);
  const radios = new Map();
  function choices(legend, name, options, change) {
    const fieldset = document.createElement("fieldset");
    const caption = document.createElement("legend");
    caption.textContent = legend;
    fieldset.appendChild(caption);
    const row = document.createElement("div");
    row.className = "faucet-choice-row";
    for (const option of options) {
      const label = document.createElement("label");
      label.className = "faucet-choice";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = name;
      input.value = option.id;
      input.addEventListener("change", () => { if (input.checked) change(option); });
      label.appendChild(input);
      const text = document.createElement("span");
      if (name === "faucet-finish") {
        const swatch = document.createElement("i");
        swatch.className = `faucet-swatch faucet-swatch-${option.id}`;
        swatch.setAttribute("aria-hidden", "true");
        text.appendChild(swatch);
      }
      text.appendChild(document.createTextNode(option.label));
      label.appendChild(text);
      if (option.description) label.title = option.description;
      row.appendChild(label);
      radios.set(`${name}:${option.id}`, input);
    }
    fieldset.appendChild(row);
    panel.appendChild(fieldset);
    return fieldset;
  }

  let pending = false;
  const styleChoices = choices("Faucet style", "faucet-style", FAUCET_STYLES, async (style) => {
    if (pending || state.mountedDetail?.file === style.assembly) return;
    pending = true;
    status.textContent = `Loading ${style.label}…`;
    for (const input of styleChoices.querySelectorAll("input")) input.disabled = true;
    const moved = await switchStepVariant(style.assembly);
    pending = false;
    if (!wrapper.isConnected) return;
    status.textContent = moved ? "" : `Couldn't load ${style.label}. Please try again.`;
    sync();
    if (moved && mobile.matches) panel.open = false;
  });
  const description = document.createElement("p");
  description.className = "faucet-style-description";
  panel.appendChild(description);
  choices("Finish", "faucet-finish", FAUCET_FINISHES, (finish) => {
    setFaucetFinish(finish.id);
    sync();
    if (mobile.matches) panel.open = false;
  });
  const status = document.createElement("p");
  status.className = "faucet-options-status";
  status.setAttribute("role", "status");
  panel.appendChild(status);
  wrapper.appendChild(panel);

  function sync() {
    const file = state.currentDetail?.file;
    const style = faucetStyleFor(file);
    panel.hidden = !hasFaucetFinish(file);
    styleChoices.hidden = !style;
    description.hidden = !style;
    description.textContent = style?.description || "";
    current.textContent = `${style?.label || "Faucet"} · ${FAUCET_FINISHES.find((f) => f.id === state.faucetFinish).label}`;
    for (const option of FAUCET_STYLES) {
      const input = radios.get(`faucet-style:${option.id}`);
      input.checked = option.id === style?.id;
      input.disabled = pending || state.mountedDetail?.file !== file;
    }
    for (const finish of FAUCET_FINISHES) {
      radios.get(`faucet-finish:${finish.id}`).checked = finish.id === state.faucetFinish;
    }
  }
  window.addEventListener(HSM_EVENTS.STEP_MOUNTED, sync);
  window.addEventListener(HSM_EVENTS.FAUCET_OPTIONS, sync);
  sync();
  return () => {
    mobile.removeEventListener("change", compact);
    window.removeEventListener(HSM_EVENTS.STEP_MOUNTED, sync);
    window.removeEventListener(HSM_EVENTS.FAUCET_OPTIONS, sync);
  };
}
