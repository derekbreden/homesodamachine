import {
  dollars, recoveryPlan, recoveryRange, recoverySummary, salesBalance, renderRecoveryChart,
} from "./cost-recovery.js";
import "./batch-forecast.js";

const panels = [...document.querySelectorAll(".cost-panel")];
const contents = [...document.querySelectorAll(".cost-contents a")];
function updateContents() {
  for (const link of contents) {
    const open = document.getElementById(link.getAttribute("aria-controls")).open;
    link.setAttribute("aria-expanded", String(open));
    if (open) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  }
}
function revealCostTarget(hash) {
  let target;
  try { target = document.getElementById(decodeURIComponent(hash.slice(1))); }
  catch { return; }
  const panel = target?.closest(".cost-panel");
  if (!panel) return;
  const ancestors = [];
  for (let element = target; element; element = element.parentElement) {
    if (element.tagName === "DETAILS") ancestors.unshift(element);
  }
  for (const element of ancestors) element.open = true;
  updateContents();
  const destination = contents.some(link => link.hash === hash) ? panel : target;
  requestAnimationFrame(() => destination.scrollIntoView({ block: "start" }));
}
for (const panel of panels) panel.addEventListener("toggle", updateContents);
document.addEventListener("click", event => {
  const link = event.target.closest('a[href^="#"]');
  if (link && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && event.button === 0) revealCostTarget(link.hash);
});
window.addEventListener("hashchange", () => revealCostTarget(location.hash));
updateContents();
if (location.hash) revealCostTarget(location.hash);

const section = document.querySelector("#recovery[data-unit-cost]");
if (section) {
  const cost = section.querySelector("#machine-cost");
  const units = section.querySelector("#sales-units");
  const inputs = {
    investment: Number(section.dataset.investment),
  };
  const set = (name, value) => { section.querySelector(`[data-recovery="${name}"]`).textContent = value; };
  function update() {
    const plan = recoveryPlan({ ...inputs, unitCost: Number(cost.value), units: Number(units.value) });
    document.querySelector('[data-recovery-overview="range"]').textContent = recoveryRange(plan);
    document.querySelector('[data-recovery-overview="label"]').textContent = plan.recordedUnits === null ? "At this per-machine cost" : "Machines to recover investment";
    set("range", recoveryRange(plan));
    set("unit-label", plan.recordedUnits === null ? "at this per-machine cost" : "machines");
    set("summary", recoverySummary(plan));
    set("contribution", dollars(plan.contribution));
    set("machine-cost", dollars(plan.unitCost));
    cost.setAttribute("aria-valuetext", `${dollars(plan.unitCost)} per machine`);
    set("units", units.value);
    set("sold", `${units.value} machines`);
    set("available", dollars(plan.available, 0));
    set("balance", salesBalance(plan));
    section.querySelector("[data-recovery='chart']").innerHTML = renderRecoveryChart(plan);
  }
  cost.addEventListener("input", update);
  units.addEventListener("input", update);
  // Controls are progressive enhancement; the complete default scenario is
  // server-rendered and readable when JavaScript is unavailable.
  section.querySelector(".recovery-controls").hidden = false;
}
