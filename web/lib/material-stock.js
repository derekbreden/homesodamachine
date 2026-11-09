// Material stock derives physical inputs from the BOM and joins them to the shared inventory ledger.
import { materialConfigurations } from "../contracts/material-quantities.js";
import { readBomLines, stripPack, plainMarkdown } from "./bom-lines.js";
import { readStockLedger } from "./stock-ledger.js";

export const normalStockUnit = (unit) =>
  ({
    pieces: "ea",
    piece: "ea",
    sets: "ea",
    set: "ea",
    caps: "ea",
    collars: "ea",
    rods: "ea",
    inches: "in",
  })[unit] || unit;
const units = {
  mm: ["length", 1],
  m: ["length", 1000],
  ft: ["length", 304.8],
  in: ["length", 25.4],
  kg: ["mass", 1000],
  g: ["mass", 1],
  ea: ["count", 1],
};
const identity = (value) =>
  String(value || "")
    .replace(/[?#].*$/, "")
    .replace(/\/$/, "");
const asin = (value) => String(value || "").match(/\bB0[A-Z0-9]{8}\b/)?.[0];
const stockName = (name) => stripPack(plainMarkdown(name)).toLowerCase();
export function convertStock(value, from, to) {
  from = normalStockUnit(from);
  to = normalStockUnit(to);
  if (from === to) return value;
  if (!units[from] || !units[to] || units[from][0] !== units[to][0])
    return null;
  return (value * units[from][1]) / units[to][1];
}

export function stockMaterialUnit(catalog, material) {
  const declared = catalog.materials.flatMap((item) =>
    (item.bom?.items || [])
      .filter((child) => child.material === material && child.unit)
      .map((child) => normalStockUnit(child.unit)),
  );
  const units = new Set(declared);
  return units.size === 1 ? [...units][0] : "ea";
}

export function readMaterialStock(hardwareDir, catalog) {
  const ledger = readStockLedger(hardwareDir),
    record = ledger.record;
  const resources = structuredClone(ledger.resources),
    inputs = {};
  const configs = materialConfigurations(catalog, catalog.cost_root),
    home = new Map();
  configs.forEach((config, c) => {
    for (const id of config.quantities.keys())
      if (!home.has(id)) home.set(id, c);
  });
  function match(id, line) {
    const binding = record.bindings?.[id];
    if (binding && resources[binding]) return resources[binding];
    const code = asin(line.href);
    const exact = Object.values(resources).filter((item) =>
      code
        ? item.id === code || asin(item.href) === code
        : line.href && identity(item.href) === identity(line.href),
    );
    const found = exact.length
      ? exact
      : Object.values(resources).filter(
          (item) => stockName(item.name) === stockName(line.name),
        );
    return found.length === 1 ? found[0] : null;
  }
  const add = (id, resource, quantity, extra = {}) =>
    (inputs[id] ||= []).push({ resource, quantity, ...extra });
  function filament(id, line, measure) {
    if (!/^(PET-GF|PETG)( |$)/.test(line.stock || "") || !measure) return false;
    const mass = convertStock(measure.value, measure.unit, "kg");
    if (mass == null) return false;
    const color = (key, fraction = 1, extra = {}) =>
      add(
        id,
        key,
        mass *
          fraction *
          (1 + (resources[key].planning?.materialAllowance || 0)),
        { estimated: true, ...extra },
      );
    if (line.stock.startsWith("PET-GF")) {
      if (record.printing.mixes[id])
        for (const [shade, fraction] of Object.entries(
          record.printing.mixes[id],
        ))
          color("petgf-" + shade, fraction);
      else if (record.printing.faucet.includes(id))
        for (const finish of ["black", "white"])
          color("petgf-" + finish, 1, { finish });
      else color("petgf-" + (record.printing.colors[id] || "black"));
    } else
      color(line.stock.includes("translucent") ? "petg-clear" : "petg-black");
    return true;
  }
  for (const line of readBomLines(hardwareDir))
    configs.forEach((config, c) => {
      const present = (line.targets || []).filter(
        (target) => config.quantities.get(target.id) > 0,
      );
      const weight = (target) =>
        target.weight ?? config.quantities.get(target.id);
      const total = present.reduce((sum, target) => sum + weight(target), 0);
      if (!total) return;
      for (const target of present) {
        if (home.get(target.id) !== c) continue;
        const id = target.id,
          share = weight(target) / total / config.quantities.get(id);
        const measure = line.measure && {
          value: line.measure.value * share,
          unit: line.measure.unit,
        };
        if (filament(id, line, measure)) continue;
        let item = match(id, line);
        const key = item?.id || "unrecorded:" + (line.href || line.name);
        if (!item)
          item = resources[key] ||= {
            id: key,
            name: line.name,
            unit: measure?.unit || "ea",
            href: line.href,
            onHand: null,
            incoming: 0,
            reserved: 0,
            estimated: false,
            asOf: null,
            note: "No usable balance for this stock is recorded",
            sources: [{ path: "hardware/ledger/bom.md" }],
          };
        item.category ||= line.category;
        let quantity = measure
          ? convertStock(measure.value, measure.unit, item.unit)
          : null;
        let allowance = false;
        if (
          quantity == null &&
          line.count != null &&
          normalStockUnit(item.unit) === "ea"
        )
          quantity = line.count * share;
        if (quantity == null && item.planning?.perUnit != null) {
          quantity = item.planning.perUnit * share;
          allowance = true;
        }
        if (item.unit === "coil cuts" && id === "HSM-0015") quantity = 1;
        const kit = record.kits?.[key]?.includes(id);
        add(id, key, kit ? 1 : quantity, {
          ...(kit && { mode: "kit" }),
          estimated: allowance || quantity == null,
        });
      }
    });
  return {
    opening: record.opening,
    resources,
    inputs,
    materials: ledger.materials,
    builds: ledger.builds,
    events: ledger.events,
    asOf: ledger.asOf,
  };
}
