const section = document.querySelector("#batch-forecast");
if (section) {
  const controls = section.querySelector(".forecast-controls");
  const supplier = section.querySelector("#forecast-supplier");
  const grouping = section.querySelector("#forecast-group");
  const showStock = section.querySelector("#forecast-show-stock");
  const result = section.querySelector(".forecast-result");
  const money = cents => "$" + (cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const plans = [...section.querySelectorAll(".forecast-plan")].map(element => ({
    element,
    rows: [...element.querySelectorAll(".forecast-part")].sort((a, b) => Number(b.dataset.cents) - Number(a.dataset.cents)),
    views: [...element.querySelectorAll(".forecast-groups")],
  }));
  const empty = document.createElement("p");
  empty.className = "forecast-result";
  empty.textContent = "No new purchases for this supplier. Include parts covered by stock to see inventory credits.";

  function update() {
    const units = controls.querySelector('input[name="forecast-units"]:checked').value;
    const plan = plans.find(plan => plan.element.dataset.units === units);
    for (const other of plans) {
      other.element.hidden = other !== plan;
      other.element.open = true;
    }
    for (const card of section.querySelectorAll("[data-card-units]")) card.dataset.selected = String(card.dataset.cardUnits === units);

    const view = plan.views.find(view => view.dataset.groupBy === grouping.value);
    for (const other of plan.views) other.hidden = other !== view;
    const groups = [...view.querySelectorAll(".forecast-group")];
    for (const row of plan.rows) {
      const key = grouping.value === "supplier" ? row.dataset.supplier : row.dataset.category;
      groups.find(group => group.dataset.groupId === key).querySelector(".forecast-group-items").append(row);
      row.hidden = (!showStock.checked && row.dataset.purchase !== "true") || (supplier.value !== "all" && supplier.value !== row.dataset.supplier);
    }

    const visible = plan.rows.filter(row => !row.hidden);
    const buying = visible.filter(row => row.dataset.purchase === "true").length;
    const credits = visible.length - buying;
    const total = visible.reduce((sum, row) => sum + Number(row.dataset.cents), 0);
    for (const group of groups) {
      const rows = [...group.querySelectorAll(".forecast-part")].filter(row => !row.hidden);
      group.hidden = rows.length === 0;
      group.dataset.cents = rows.reduce((sum, row) => sum + Number(row.dataset.cents), 0);
      group.querySelector(".forecast-group-cost").textContent = money(Number(group.dataset.cents));
      group.querySelector(".forecast-group-percent").textContent = total ? (Number(group.dataset.cents) / total * 100).toFixed(1) + "%" : "0%";
    }
    groups.sort((a, b) => Number(b.dataset.cents) - Number(a.dataset.cents));
    const maximum = Math.max(...groups.map(group => Number(group.dataset.cents)), 1);
    for (const group of groups) {
      group.querySelector(".cost-bf").style.width = (Number(group.dataset.cents) / maximum * 100).toFixed(1) + "%";
      group.open = group === groups.find(group => !group.hidden);
      view.append(group);
    }
    empty.hidden = visible.length > 0;
    view.append(empty);
    result.textContent = `${money(total)}* · ${buying} purchase line${buying === 1 ? "" : "s"}${credits ? ` · ${credits} stock credit${credits === 1 ? "" : "s"}` : ""} for ${units} machines · freight and tax separate`;
  }

  controls.addEventListener("change", update);
  update();
  section.dataset.enhanced = "";
  controls.hidden = false;
  result.hidden = false;
}
