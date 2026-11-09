// The stock ledger projects shared balances and physical work from opening evidence and recorded activity.
import fs from "node:fs";
import path from "node:path";

export const materialKey = (material, finish) => material + (finish ? ":" + finish : "");
export const availableStock = balance => Number.isFinite(balance?.onHand) ? Math.max(0, balance.onHand - (balance.reserved || 0)) : null;

export function projectStock(record) {
  const resources = Object.fromEntries((record.resources || []).map(resource => [resource.id, structuredClone(resource)]));
  const materials = {}, builds = [];
  const balance = (entry, create = true) => {
    if (entry.resource) return resources[entry.resource];
    const key = materialKey(entry.material, entry.finish);
    if (!materials[key] && create) materials[key] = { material: entry.material, ...(entry.finish && { finish: entry.finish }), onHand: null, reserved: 0 };
    return materials[key];
  };
  for (const observation of record.observations || []) {
    const target = balance(observation);
    if (target) Object.assign(target, observation);
  }
  for (const event of record.events || []) {
    if (event.kind === "count") {
      const target = balance(event);
      if (target) Object.assign(target, { onHand: event.quantity, estimated: Boolean(event.estimated), asOf: event.occurredAt, note: event.note, sources: event.sources || [] },
        ...(event.incoming == null ? [] : [{ incoming: event.incoming }]), ...(event.reserved == null ? [] : [{ reserved: event.reserved }]));
    }
    if (event.kind === "receipt") {
      const target = balance(event);
      if (target) {
        target.onHand = (target.onHand ?? 0) + event.quantity;
        target.incoming = Math.max(0, (target.incoming || 0) - event.quantity);
        target.asOf = event.occurredAt;
      }
    }
    if (event.kind === "completion") {
      for (const input of event.inputs) {
        const target = balance(input);
        if (target && Number.isFinite(target.onHand)) target.onHand -= input.quantity;
        if (target) target.asOf = event.occurredAt;
      }
      const output = balance(event.output);
      if (output) {
        output.onHand = (output.onHand ?? 0) + event.output.quantity;
        output.asOf = event.occurredAt;
      }
      builds.push({ ...event, ...event.output, completedAt: event.occurredAt });
    }
  }
  for (const item of [...Object.values(resources), ...Object.values(materials)]) item.available = availableStock(item);
  const dates = [...Object.values(resources), ...Object.values(materials)].map(item => item.asOf).filter(Boolean).sort();
  return { opening: record.opening, resources, materials, builds, events: record.events || [], asOf: dates.at(-1) || record.opening?.asOf };
}

export function readStockLedger(hardwareDir) {
  const record = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger/stock.json"), "utf8"));
  return { record, ...projectStock(record) };
}
