// Material stock joins the current BOM's physical inputs to dated inventory evidence for the website and agents.
import fs from "node:fs";
import path from "node:path";
import { explodeBom } from "../contracts/materials.js";
import { readBomLines, readPartCosts, stripPack, plainMarkdown } from "./part-costs.js";

const normalUnit = unit => ({ pieces: "ea", piece: "ea", sets: "ea", set: "ea", caps: "ea", collars: "ea", rods: "ea", inches: "in" })[unit] || unit;
const units = { mm: ["length", 1], m: ["length", 1000], ft: ["length", 304.8], in: ["length", 25.4], kg: ["mass", 1000], g: ["mass", 1], ea: ["count", 1] };
const identity = value => String(value || "").replace(/[?#].*$/, "").replace(/\/$/, "");
const asin = value => String(value || "").match(/\bB0[A-Z0-9]{8}\b/)?.[0];
const stockName = name => stripPack(plainMarkdown(name)).toLowerCase();

function convert(value, from, to) {
  from = normalUnit(from); to = normalUnit(to);
  if (from === to) return value;
  if (!units[from] || !units[to] || units[from][0] !== units[to][0]) return null;
  return value * units[from][1] / units[to][1];
}

export function readMaterialStock(hardwareDir, catalog) {
  const record = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger/stock.json"), "utf8"));
  const forecast = JSON.parse(fs.readFileSync(path.join(hardwareDir, record.opening.source), "utf8"));
  const costs = catalog.costs || readPartCosts(hardwareDir, catalog);
  const inputs = {}, resources = {}, materials = {};
  const lines = readBomLines(hardwareDir);
  const quantities = new Map([[catalog.cost_root, 1]]);
  for (const row of explodeBom(catalog, catalog.cost_root, costs.options))
    quantities.set(row.material.id, (quantities.get(row.material.id) || 0) + (row.quantity || 0));
  const update = key => Object.assign(resources[key], ...record.observations.filter(value => value.resource === key));
  for (const definition of record.resources || []) { resources[definition.id] = { ...definition }; update(definition.id); }

  function resource(item) {
    const key = item.id;
    if (!resources[key]) resources[key] = {
      id: key, name: item.name, unit: item.unit, href: item.sourceUrl || null,
      onHand: item.inventory?.basis === "unknown" ? null : item.inventory?.onHand ?? null, incoming: item.inventory?.incoming ?? 0, reserved: 0,
      estimated: item.inventory?.estimated !== false, asOf: item.inventory?.asOf || record.opening.asOf,
      note: item.inventory?.note || "No usable stock count recorded", sources: item.inventory?.sources || [],
    };
    update(key);
    return key;
  }
  function match(id, element) {
    const binding = record.bindings?.[id];
    if (binding) {
      const bound = forecast.items.find(item => item.id === binding);
      if (bound) return bound;
      if (resources[binding]) return { ...resources[binding], inventory: resources[binding] };
    }
    const code = asin(element.href);
    const byIdentity = forecast.items.filter(item => code ? asin(item.sourceUrl) === code || item.id === code
      : element.href && identity(item.sourceUrl) === identity(element.href));
    const found = byIdentity.length ? byIdentity : forecast.items.filter(item => stockName(item.name) === stockName(element.label));
    return found.length === 1 ? found[0] : null;
  }
  function add(id, key, quantity, extra = {}) {
    (inputs[id] ||= []).push({ resource: key, quantity, ...extra });
  }
  function filament(id, element) {
    if (!/^(PET-GF|PETG)( |$)/.test(element.label) || !element.measure) return false;
    const mass = convert(element.measure.value, element.measure.unit, "kg");
    if (mass == null) return false;
    const addColor = (key, fraction = 1, extra = {}) => {
      const item = forecast.items.find(item => item.id === key);
      add(id, resource(item), mass * fraction * (1 + (item.materialAllowance || 0)), { estimated: true, ...extra });
    };
    if (element.label.startsWith("PET-GF")) {
      if (record.printing.mixes[id]) for (const [color, fraction] of Object.entries(record.printing.mixes[id])) addColor("petgf-" + color, fraction);
      else if (record.printing.faucet.includes(id)) for (const finish of ["black", "white"]) addColor("petgf-" + finish, 1, { finish });
      else addColor("petgf-" + (record.printing.colors[id] || "black"));
    } else addColor(element.label.includes("translucent") ? "petg-clear" : "petg-black");
    return true;
  }

  for (const [id, cost] of Object.entries(costs.direct)) for (const element of cost.elements) {
    if (element.kind === "labor" || element.kind === "unallocated") continue;
    if (filament(id, element)) continue;
    const item = match(id, element);
    const candidates = lines.filter(line => line.name === element.label && identity(line.href) === identity(element.href)
      && `${line.section}. ${line.sectionName}` === element.section && line.targets?.some(target => target.id === id)
      && Math.abs(line.usd - element.of) < 1e-8);
    const physical = line => JSON.stringify([line.targets, line.count, line.measure, line.qty]);
    const line = candidates.length && candidates.every(candidate => physical(candidate) === physical(candidates[0])) ? candidates[0] : null;
    const key = item ? resource(item) : "unrecorded:" + (element.href || element.label);
    if (!resources[key]) resources[key] = {
      id: key, name: element.label, unit: element.measure?.unit || "ea", href: element.href,
      onHand: null, incoming: 0, reserved: 0, estimated: false, asOf: null,
      note: "No usable balance for this stock is recorded", sources: [{ path: "hardware/ledger/bom.md" }],
    };
    update(key);
    let quantity = null;
    if (element.measure) quantity = convert(element.measure.value, element.measure.unit, resources[key].unit);
    const present = (line?.targets || []).filter(target => quantities.get(target.id) > 0);
    const totalWeight = present.reduce((sum, target) => sum + (target.weight ?? quantities.get(target.id)), 0);
    const target = present.find(target => target.id === id);
    const share = target && totalWeight > 0 ? (target.weight ?? quantities.get(id)) / totalWeight / quantities.get(id) : null;
    if (quantity == null && line?.count != null && share != null && normalUnit(resources[key].unit) === "ea")
      quantity = line.count * share;
    else if (quantity == null && line && element.kind === "price" && normalUnit(resources[key].unit) === "ea" && line.count == null)
      quantity = 1;
    // A forecast's build allowance remains an estimate; it carries no measurement of an individual operation.
    else if (quantity == null && item && normalUnit(item.unit) === normalUnit(resources[key].unit) && share != null)
      quantity = item.perUnit * share;
    if (item?.unit === "coil cuts" && id === "HSM-0015") quantity = 1;
    const kit = record.kits?.[key]?.includes(id);
    add(id, key, kit ? 1 : quantity, { ...(kit && { mode: "kit" }), estimated: quantity == null || Boolean(item?.inventory?.estimated) });
  }

  // Observations replace a balance; reserved stock is retained separately from the physical count.
  for (const observation of record.observations) {
    const target = observation.resource ? resources[observation.resource]
      : (materials[observation.material + (observation.finish ? ":" + observation.finish : "")] ||= {});
    if (target) Object.assign(target, observation);
  }
  return { opening: record.opening, resources, inputs, materials, builds: record.builds };
}
