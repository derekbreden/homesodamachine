// Stock operations record physical work atomically so stock movements and measured effort stay together.
import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { materialIndex, bomItems } from "../contracts/materials.js";
import { readMaterialCatalog } from "./material-catalog.js";
import {
  readMaterialStock,
  convertStock,
  stockMaterialUnit,
} from "./material-stock.js";
import { projectStock, materialKey } from "./stock-ledger.js";

const run = promisify(execFile);
const repoRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../..",
);
const positive = (value) =>
  typeof value === "number" && Number.isFinite(value) && value > 0;
const finite = (value) =>
  typeof value === "number" && Number.isFinite(value) && value >= 0;
const clone = (value) => structuredClone(value);

export function materialHasFinish(catalog, id, seen = new Set()) {
  if (seen.has(id)) return false;
  if ((catalog.stock.inputs[id] || []).some((input) => input.finish))
    return true;
  return (materialIndex(catalog).get(id)?.bom?.items || []).some(
    (item) =>
      item.when?.finish ||
      materialHasFinish(catalog, item.material, new Set([...seen, id])),
  );
}

export function stockTarget(catalog, material, finish) {
  const item = materialIndex(catalog).get(material);
  if (!item) throw new Error("Unknown material");
  if (item.kind === "purchased") {
    const inputs = (catalog.stock.inputs[material] || []).filter(
      (input) => !input.finish || input.finish === finish,
    );
    const keys = new Set(inputs.map((input) => input.resource));
    if (
      keys.size === 1 &&
      inputs.every((input) => input.quantity != null && input.mode !== "kit") &&
      Math.abs(inputs.reduce((sum, input) => sum + input.quantity, 0) - 1) <
        1e-8
    )
      return { resource: inputs[0].resource };
  }
  return {
    material,
    ...(finish && materialHasFinish(catalog, material) && { finish }),
  };
}

export function completionProposal(
  catalog,
  material,
  quantity = 1,
  finish = "white",
) {
  if (!Number.isSafeInteger(quantity) || quantity < 1)
    throw new Error("Choose a positive whole output quantity");
  const index = materialIndex(catalog),
    item = index.get(material);
  if (!item) throw new Error("Unknown material");
  if (item.kind === "purchased")
    throw new Error("Record a receipt or count for a purchased part");
  const inputs = new Map(),
    kit = new Map();
  function add(input) {
    const key = input.resource || materialKey(input.material, input.finish);
    const row = inputs.get(key);
    if (row)
      row.quantity =
        row.quantity == null || input.quantity == null
          ? null
          : row.quantity + input.quantity;
    else inputs.set(key, input);
  }
  for (const child of bomItems(item, { finish })) {
    const target = stockTarget(catalog, child.material, finish);
    const childStock =
      catalog.stock.materials[materialKey(child.material, finish)] ||
      catalog.stock.materials[child.material];
    const childInputs = (catalog.stock.inputs[child.material] || []).filter(
      (input) => !input.finish || input.finish === finish,
    );
    if (
      !target.resource &&
      !(childStock?.onHand > 0) &&
      childInputs.length &&
      childInputs.every((input) => input.mode === "kit")
    ) {
      for (const input of childInputs) {
        const group = kit.get(input.resource) || {};
        group[child.material] =
          (group[child.material] || 0) +
          child.quantity * quantity * input.quantity;
        kit.set(input.resource, group);
      }
    } else
      add({
        ...target,
        quantity: Number.isFinite(child.quantity)
          ? child.quantity * quantity
          : null,
        unit: target.resource
          ? catalog.stock.resources[target.resource].unit
          : child.unit || "ea",
      });
  }
  for (const input of (catalog.stock.inputs[material] || []).filter(
    (input) => !input.finish || input.finish === finish,
  ))
    add({
      resource: input.resource,
      quantity: input.quantity == null ? null : input.quantity * quantity,
      unit: catalog.stock.resources[input.resource].unit,
      estimated: Boolean(input.estimated),
    });
  for (const [resource, uses] of kit)
    add({
      resource,
      quantity: Math.max(...Object.values(uses)),
      unit: catalog.stock.resources[resource].unit,
    });
  return {
    id: randomUUID(),
    kind: "completion",
    output: {
      material,
      quantity,
      ...(materialHasFinish(catalog, material) && { finish }),
    },
    inputs: [...inputs.values()],
    attendedMinutes: null,
    note: "",
  };
}

function canonicalTarget(catalog, entry) {
  if (entry.resource && catalog.stock.resources[entry.resource])
    return { resource: entry.resource };
  if (entry.material) {
    if (
      materialHasFinish(catalog, entry.material) &&
      !["white", "black"].includes(entry.finish)
    )
      throw new Error("Record the actual finish for this material");
    return stockTarget(catalog, entry.material, entry.finish);
  }
  throw new Error("Choose a recorded stock resource or material");
}
function normalize(catalog, payload, existing) {
  const id = payload.id || randomUUID();
  if (typeof id !== "string" || id.length > 200)
    throw new Error("Invalid record identity");
  const occurredAt =
    payload.occurredAt || existing?.occurredAt || new Date().toISOString();
  if (!Number.isFinite(Date.parse(occurredAt)))
    throw new Error("Choose a valid work date");
  const event = {
    id,
    kind: payload.kind,
    occurredAt: new Date(occurredAt).toISOString(),
    note: String(payload.note || ""),
    sources: Array.isArray(payload.sources) ? payload.sources : [],
  };
  if (event.kind === "completion") {
    const output = payload.output;
    if (
      !materialIndex(catalog).has(output?.material) ||
      !Number.isSafeInteger(output.quantity) ||
      output.quantity < 1
    )
      throw new Error("Choose a material and a positive whole output quantity");
    if (materialIndex(catalog).get(output.material).kind === "purchased")
      throw new Error("Record a receipt or count for a purchased part");
    if (!Array.isArray(payload.inputs) || !payload.inputs.length)
      throw new Error("Record the actual inputs used");
    const finish = output.finish || "white";
    if (materialHasFinish(catalog, output.material) && !output.finish)
      throw new Error("Record the actual output finish");
    if (!["white", "black"].includes(finish))
      throw new Error("Choose a supported finish");
    event.output = {
      material: output.material,
      quantity: output.quantity,
      ...(materialHasFinish(catalog, output.material) && { finish }),
    };
    event.inputs = payload.inputs.map((input) => {
      const target = canonicalTarget(catalog, input);
      if (!positive(input.quantity))
        throw new Error(
          "Enter the actual quantity for every input, or remove unused inputs",
        );
      if (target.material === output.material)
        throw new Error("A completion cannot consume its own output");
      const unit = target.resource
        ? catalog.stock.resources[target.resource].unit
        : stockMaterialUnit(catalog, target.material);
      const quantity = convertStock(input.quantity, input.unit || unit, unit);
      if (!positive(quantity))
        throw new Error("Input units do not match the recorded stock");
      return {
        ...target,
        quantity,
        unit,
        ...(input.estimated && { estimated: true }),
      };
    });
    if (payload.attendedMinutes != null && !finite(payload.attendedMinutes))
      throw new Error("Hands-on minutes must be a nonnegative number");
    event.attendedMinutes = payload.attendedMinutes ?? null;
  } else if (event.kind === "receipt" || event.kind === "count") {
    Object.assign(event, canonicalTarget(catalog, payload));
    if (
      !(event.kind === "count"
        ? finite(payload.quantity)
        : positive(payload.quantity))
    )
      throw new Error("Enter a valid stock quantity");
    event.quantity = payload.quantity;
    for (const field of ["incoming", "reserved"])
      if (payload[field] != null) {
        if (!finite(payload[field]))
          throw new Error("Stock quantities must be nonnegative");
        event[field] = payload[field];
      }
    event.estimated = Boolean(payload.estimated);
  } else throw new Error("Choose completion, receipt or count");
  return event;
}

export function recordStockEvent(hardwareDir, payload) {
  const file = path.join(hardwareDir, "ledger/stock.json"),
    lock = file + ".lock";
  let descriptor;
  // The stock write lock serializes ledger edits from the local workbench and agent commands.
  try {
    descriptor = fs.openSync(lock, "wx");
  } catch (error) {
    if (error.code !== "EEXIST") throw error;
    let stale = false;
    try {
      const owner = JSON.parse(fs.readFileSync(lock, "utf8"));
      if (owner.pid)
        try {
          process.kill(owner.pid, 0);
        } catch (e) {
          stale = e.code === "ESRCH";
        }
    } catch {}
    if (!stale) throw new Error("Stock is being recorded; retry in a moment");
    fs.rmSync(lock);
    descriptor = fs.openSync(lock, "wx");
  }
  let temporary;
  try {
    fs.writeFileSync(descriptor, JSON.stringify({ pid: process.pid }));
    const record = JSON.parse(fs.readFileSync(file, "utf8"));
    const catalog = readMaterialCatalog(hardwareDir);
    catalog.stock = readMaterialStock(hardwareDir, catalog);
    const existing = (record.events || []).find(
      (event) => event.id === payload.id,
    );
    const event = normalize(catalog, payload, existing);
    if (existing) {
      const { recordedAt, ...prior } = existing;
      if (JSON.stringify(prior) !== JSON.stringify(event))
        throw new Error(
          "This record identity already belongs to different work",
        );
      return { event: existing, duplicate: true };
    }
    for (const entry of [event, ...(event.inputs || [])])
      if (
        entry.resource &&
        !record.resources.some((resource) => resource.id === entry.resource)
      )
        record.resources.push(clone(catalog.stock.resources[entry.resource]));
    event.recordedAt = new Date().toISOString();
    (record.events ||= []).push(event);
    projectStock(record);
    temporary = file + "." + randomUUID() + ".tmp";
    const output = fs.openSync(temporary, "wx", 0o644);
    try {
      fs.writeFileSync(output, JSON.stringify(record, null, 2) + "\n");
      fs.fsyncSync(output);
    } finally {
      fs.closeSync(output);
    }
    fs.renameSync(temporary, file);
    temporary = null;
    return { event, duplicate: false };
  } finally {
    if (temporary) fs.rmSync(temporary, { force: true });
    fs.closeSync(descriptor);
    fs.rmSync(lock, { force: true });
  }
}

// Publication commits the recorded stock facts and pushes the shared checkout to the website.
export async function publishStockLedger(hardwareDir, event = null) {
  if (path.resolve(hardwareDir) !== path.join(repoRoot, "hardware"))
    throw new Error("Only the shared checkout publishes stock");
  const file = "hardware/ledger/stock.json";
  const changed = await run(
    "git",
    ["diff", "--name-only", "HEAD", "--", file],
    { cwd: repoRoot },
  );
  if (changed.stdout.trim()) {
    const folder = path.join(
      repoRoot,
      ".cache/runs",
      "stock-publication-" + randomUUID(),
    );
    fs.mkdirSync(folder, { recursive: true });
    const body = path.join(folder, "commit.txt");
    fs.writeFileSync(
      body,
      "Record physical stock activity\n\nSave the shared stock and measured-work record.\n\nSession: ERP\n",
    );
    try {
      await run("git", ["commit", "--file", body, "--", file], {
        cwd: repoRoot,
      });
    } finally {
      fs.rmSync(folder, { recursive: true, force: true });
    }
  }
  await run("git", ["push", "origin", "main"], { cwd: repoRoot });
  return { published: true };
}
