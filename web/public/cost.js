import {
  dollars, recoveryPlan, recoveryRange, recoverySummary, salesBalance, renderRecoveryChart,
} from "./cost-recovery.js";
import "./batch-forecast.js";

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
