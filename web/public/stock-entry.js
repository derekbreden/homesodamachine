// The local stock form records actual inputs, finished stock and hands-on work through a single completion.
const host = document.querySelector(".stock-workbench");
if (host) {
  const status = host.querySelector(".stock-record-status"),
    list = host.querySelector("#stock-input-list");
  const completion = host.querySelector("#stock-completion"),
    countForm = host.querySelector("#stock-count");
  const retry = host.querySelector("#stock-publish-retry"),
    another = host.querySelector("#stock-another");
  let data,
    completionId,
    countId = crypto.randomUUID(),
    busy = false;
  const localNow = () => {
    const date = new Date();
    return new Date(date - date.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);
  };
  const key = (target) => JSON.stringify(target);
  const describe = (target) =>
    data.targets.find((item) => key(item.target) === key(target));
  const amount = (quantity, unit) =>
    quantity == null ? "Unknown" : Number(quantity.toFixed(6)) + " " + unit;
  function options(select, chosen = null) {
    select.replaceChildren();
    for (const groupName of ["Parts and assemblies", "Stock and supplies"]) {
      const group = document.createElement("optgroup");
      group.label = groupName;
      for (const item of data.targets
        .filter((item) => item.group === groupName)
        .sort((a, b) => a.label.localeCompare(b.label))) {
        const option = document.createElement("option");
        option.value = key(item.target);
        option.textContent = item.label;
        if (chosen && key(item.target) === key(chosen)) option.selected = true;
        group.append(option);
      }
      select.append(group);
    }
  }
  function updateCount() {
    host.querySelector("#stock-input-count").textContent = list.children.length;
  }
  function addInput(input = {}) {
    const row = document.createElement("div");
    row.className = "stock-input";
    row.dataset.estimated = String(Boolean(input.estimated));
    const select = document.createElement("select");
    select.setAttribute("aria-label", "Input stock item");
    const target = input.resource
      ? { resource: input.resource }
      : input.material
        ? {
            material: input.material,
            ...(input.finish && { finish: input.finish }),
          }
        : null;
    options(select, target);
    const quantity = document.createElement("input");
    quantity.type = "number";
    quantity.min = "0";
    quantity.step = "any";
    quantity.required = true;
    quantity.setAttribute("aria-label", "Actual input quantity");
    quantity.value =
      input.quantity == null ? "" : String(Number(input.quantity.toFixed(6)));
    const unit = document.createElement("span");
    unit.className = "stock-input-unit";
    const balance = document.createElement("small");
    balance.className = "stock-input-balance";
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      row.remove();
      updateCount();
    });
    function sync() {
      const item = describe(JSON.parse(select.value));
      unit.textContent = item?.unit || input.unit || "ea";
      balance.textContent =
        "Available " +
        amount(item?.available, item?.unit || "ea") +
        (item?.estimated ? " · estimate" : "") +
        (row.dataset.estimated === "true" ? " · usage estimate" : "");
    }
    select.addEventListener("change", () => {
      row.dataset.estimated = "false";
      sync();
    });
    quantity.addEventListener("input", () => {
      row.dataset.estimated = "false";
      sync();
    });
    row.addEventListener("stock-balance", sync);
    row.append(select, quantity, unit, remove, balance);
    list.append(row);
    sync();
    updateCount();
  }
  async function load() {
    const params = new URLSearchParams({
      material: host.dataset.material,
      quantity: host.dataset.quantity,
      finish: host.dataset.finish,
    });
    const response = await fetch("/api/stock/entry?" + params, {
      cache: "no-store",
    });
    data = await response.json();
    if (!response.ok) throw new Error(data.error);
    options(host.querySelector("#stock-count-target"), data.selectedTarget);
    updateCountUnit();
    completion.hidden = !data.proposal;
    if (!data.proposal) {
      host.querySelector(".stock-count-panel").open = true;
      return;
    }
    completionId = data.proposal.id;
    list.replaceChildren();
    for (const input of data.proposal.inputs) addInput(input);
    host.querySelector(".stock-output").textContent =
      host.dataset.quantity +
      " × " +
      document.querySelector(".build-plan h2").textContent;
    host.querySelector("#stock-completed-at").value = localNow();
    host.querySelector("#stock-minutes").value = "";
    host.querySelector("#stock-work-note").value = "";
    completion.querySelector("button[type=submit]").disabled = false;
    another.hidden = true;
  }
  async function refreshPlan() {
    const response = await fetch(location.href, { cache: "no-store" });
    const html = new DOMParser().parseFromString(
      await response.text(),
      "text/html",
    );
    const next = html.querySelector(".build-plan");
    if (next) document.querySelector(".build-plan").replaceWith(next);
  }
  async function send(payload) {
    const response = await fetch("/api/stock/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    status.textContent =
      result.published === false
        ? result.publishError
        : "Recorded. Stock, buildability and purchasing use the updated record.";
    retry.hidden = result.published !== false;
    await refreshPlan();
    const selected = JSON.parse(
      host.querySelector("#stock-count-target").value,
    );
    const params = new URLSearchParams({
      material: host.dataset.material,
      quantity: host.dataset.quantity,
      finish: host.dataset.finish,
    });
    const updated = await fetch("/api/stock/entry?" + params, {
      cache: "no-store",
    });
    if (updated.ok) {
      data.targets = (await updated.json()).targets;
      options(host.querySelector("#stock-count-target"), selected);
      updateCountUnit();
      for (const row of list.children)
        row.dispatchEvent(new Event("stock-balance"));
    }
    return result;
  }
  function updateCountUnit() {
    const item = describe(
      JSON.parse(host.querySelector("#stock-count-target").value),
    );
    host.querySelector("#stock-count-unit").textContent = "(" + item.unit + ")";
  }
  completion.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy) return;
    busy = true;
    const button = completion.querySelector("button[type=submit]");
    button.disabled = true;
    try {
      const inputs = [...list.children].map((row) => ({
        ...JSON.parse(row.querySelector("select").value),
        quantity: Number(row.querySelector("input").value),
        unit: row.querySelector(".stock-input-unit").textContent,
        ...(row.dataset.estimated === "true" && { estimated: true }),
      }));
      const minutes = host.querySelector("#stock-minutes").value;
      status.textContent = "Recording physical work…";
      await send({
        ...data.proposal,
        id: completionId,
        occurredAt: new Date(
          host.querySelector("#stock-completed-at").value,
        ).toISOString(),
        inputs,
        attendedMinutes: minutes === "" ? null : Number(minutes),
        note: host.querySelector("#stock-work-note").value,
      });
      another.hidden = false;
    } catch (error) {
      status.textContent = error.message;
      button.disabled = false;
    } finally {
      busy = false;
    }
  });
  countForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy) return;
    busy = true;
    const button = countForm.querySelector("button[type=submit]");
    button.disabled = true;
    try {
      await send({
        id: countId,
        kind: host.querySelector("#stock-count-kind").value,
        ...JSON.parse(host.querySelector("#stock-count-target").value),
        quantity: Number(host.querySelector("#stock-count-quantity").value),
        note: host.querySelector("#stock-count-note").value,
      });
      countId = crypto.randomUUID();
      host.querySelector("#stock-count-quantity").value = "";
    } catch (error) {
      status.textContent = error.message;
    } finally {
      busy = false;
      button.disabled = false;
    }
  });
  host
    .querySelector("#stock-add-input")
    .addEventListener("click", () => addInput());
  host
    .querySelector("#stock-count-target")
    .addEventListener("change", updateCountUnit);
  another.addEventListener("click", () =>
    load().catch((error) => (status.textContent = error.message)),
  );
  retry.addEventListener("click", async () => {
    try {
      const response = await fetch("/api/stock/publish", { method: "POST" });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error);
      retry.hidden = true;
      status.textContent = "Published.";
    } catch (error) {
      status.textContent = error.message;
    }
  });
  load().catch((error) => (status.textContent = error.message));
}
