// Material quantities and configurations describe the physical contents shared by planning and costing.
import { materialIndex, bomItems } from "./materials.js";
import { FAUCET_FINISHES } from "./faucet-options.js";

// Total pieces of each material in one unit, through every assembly level.
// `swap` replaces a material with its variant wherever it occurs.
export function unitQuantities(catalog, rootId, options, swap = null) {
  const index = materialIndex(catalog);
  const totals = new Map([[rootId, 1]]);
  (function visit(id, quantity, seen) {
    if (seen.has(id)) return;
    const next = new Set([...seen, id]);
    for (const item of bomItems(index.get(id), options)) {
      if (typeof item.quantity !== "number") continue;
      const child = swap?.get(item.material) || item.material;
      const pieces = quantity * item.quantity;
      totals.set(child, (totals.get(child) || 0) + pieces);
      visit(child, pieces, next);
    }
  })(rootId, 1, new Set());
  return totals;
}

// The default build first — the first faucet finish and the faucet style the
// unit names — then each other finish, then each variant of a part in the unit.
export function materialConfigurations(catalog, rootId) {
  const [first, ...others] = FAUCET_FINISHES.map((finish) => finish.id);
  const base = { options: { finish: first }, swap: null };
  const configs = [
    base,
    ...others.map((finish) => ({ options: { finish }, swap: null })),
  ];
  const present = unitQuantities(catalog, rootId, base.options);
  for (const material of catalog.materials)
    for (const relation of present.has(material.id)
      ? material.relations || []
      : [])
      if (relation.kind === "variant" && !present.has(relation.material))
        configs.push({
          options: base.options,
          swap: new Map([[material.id, relation.material]]),
        });
  return configs.map((config) => ({
    ...config,
    quantities: unitQuantities(catalog, rootId, config.options, config.swap),
  }));
}
