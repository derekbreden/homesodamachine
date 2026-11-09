// Stock planning expands a requested material through its BOM and shares each supply balance across the whole request.
import { bomItems, materialIndex } from "./materials.js";

const EPSILON = 1e-8;

export function planMaterial(catalog, id, quantity = 1, options = {}) {
  options = { ...options, finish: options.finish || catalog.costs?.options?.finish || "black" };
  if (!Number.isSafeInteger(quantity) || quantity < 1) throw new RangeError("Choose a positive whole quantity");
  const index = materialIndex(catalog);
  if (!index.has(id)) throw new RangeError("Unknown material");
  const stock = catalog.stock || {}, materials = new Map(), resources = new Map();
  const balances = new Map(), estimatedMaterials = new Set();
  for (const [key, value] of Object.entries(stock.materials || {})) {
    if (value.finish && value.finish !== options.finish) continue;
    const material = value.material || key;
    balances.set(material, (balances.get(material) || 0) + Math.max(0, (value.onHand ?? 0) - (value.reserved || 0)));
    if (value.estimated) estimatedMaterials.add(material);
  }
  const gaps = [];

  function need(materialId, count, path) {
    const material = index.get(materialId);
    const row = materials.get(materialId) || { material: materialId, needed: 0, fromStock: 0, make: 0 };
    materials.set(materialId, row);
    row.needed += count;
    const available = balances.get(materialId) || 0, used = Math.min(count, available);
    row.fromStock += used;
    balances.set(materialId, available - used);
    const remaining = count - used;
    if (remaining <= EPSILON) return;
    if (!material || path.has(materialId)) {
      gaps.push({ material: materialId, reason: material ? "Assembly contents need review" : "Material record missing" });
      return;
    }
    const inputs = (stock.inputs?.[materialId] || []).filter(input => !input.finish || input.finish === options.finish);
    const children = bomItems(material, options);
    if (!children.length && !inputs.length) {
      gaps.push({ material: materialId, quantity: remaining, reason: "No usable stock or manufacturing input recorded" });
      return;
    }
    if (material.kind !== "purchased") row.make += remaining;
    for (const input of inputs) {
      if (input.quantity === 0) continue;
      const resource = stock.resources?.[input.resource];
      const resourceRow = resources.get(input.resource) || {
        resource: input.resource, needed: 0, kit: {}, quantityKnown: true, uses: new Set(), estimated: false,
      };
      resources.set(input.resource, resourceRow);
      resourceRow.uses.add(materialId);
      resourceRow.estimated ||= Boolean(input.estimated);
      if (Number.isFinite(input.quantity) && input.quantity >= 0) {
        if (input.mode === "kit") resourceRow.kit[materialId] = (resourceRow.kit[materialId] || 0) + remaining * input.quantity;
        else resourceRow.needed += remaining * input.quantity;
      }
      else resourceRow.quantityKnown = false;
      if (!resource) resourceRow.quantityKnown = false;
    }
    const next = new Set([...path, materialId]);
    for (const child of children) {
      if (!Number.isFinite(child.quantity) || child.quantity <= 0) {
        gaps.push({ material: child.material, reason: "Required quantity is not recorded" });
      } else need(child.material, remaining * child.quantity, next);
    }
  }
  need(id, quantity, new Set());
  const supplies = [...resources.values()].map(row => {
    const resource = stock.resources[row.resource] || {};
    row.needed += Math.max(0, ...Object.values(row.kit));
    if (["ea", "pieces", "piece", "sets", "set", "caps", "collars", "rods", "coil cuts"].includes(resource.unit))
      row.needed = Math.ceil(row.needed - EPSILON);
    const available = Number.isFinite(resource.onHand) ? Math.max(0, resource.onHand - (resource.reserved || 0)) : null;
    const short = row.quantityKnown && available != null ? Math.max(0, row.needed - available) : null;
    return { ...row, uses: [...row.uses], available, short,
      status: !row.quantityKnown || available == null ? "unknown" : short > EPSILON ? "short" : "covered",
      estimated: row.estimated || Boolean(resource.estimated),
    };
  });
  const short = supplies.filter(row => row.status === "short");
  const unknown = supplies.filter(row => row.status === "unknown");
  const estimated = supplies.some(row => row.estimated) || [...materials.values()].some(row =>
    row.fromStock && estimatedMaterials.has(row.material));
  return { material: id, quantity, options, materials: [...materials.values()], resources: supplies, gaps,
    short: short.length, unknown: unknown.length + gaps.length, estimated,
    status: short.length ? "short" : unknown.length || gaps.length ? "unknown" : estimated ? "estimate" : "covered" };
}

export function stockSummary(plan) {
  if (plan.status === "short") return "Stock is short";
  if (plan.status === "unknown") return "Stock records needed";
  if (plan.status === "estimate") return "Materials covered · estimate";
  return "Materials covered";
}

export function materialCapacity(catalog, id, options = {}) {
  const first = planMaterial(catalog, id, 1, options);
  if (first.short) return { quantity: 0, estimated: first.estimated };
  if (first.unknown) return null;
  let low = 1, high = 2;
  while (high < Number.MAX_SAFE_INTEGER / 2) {
    const plan = planMaterial(catalog, id, high, options);
    if (plan.unknown) return null;
    if (plan.short) break;
    low = high; high *= 2;
  }
  if (high >= Number.MAX_SAFE_INTEGER / 2) return null;
  while (high - low > 1) {
    const middle = Math.floor((low + high) / 2);
    if (planMaterial(catalog, id, middle, options).short) high = middle; else low = middle;
  }
  return { quantity: low, estimated: first.estimated };
}
