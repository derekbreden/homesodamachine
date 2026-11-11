// Installed locations bind BOM occurrences to the bodies already present in each model.
import { explodeBom, occurrenceBodies, materialIndex, materialForFile, materialForComponent, matchesBody } from "./materials.js";
import { instanceBody, instanceLabel } from "./features.js";

function rowInstances(catalog, row, names, index, options) {
  const bound = occurrenceBodies(catalog, row.path, names, options);
  if (!bound.length) return [];
  const bind = bodies => [...new Set(bodies.flatMap(body => occurrenceBodies(catalog,
    [...row.path.slice(0, -1), { bodies: [body] }], names, options)))];
  let groups;
  if (row.item.placements) {
    groups = row.item.placements.map(placement => ({ label: placement.label, bodies: bind(placement.bodies || []) }));
  } else {
    const byBinding = (row.item.bodies || []).map(body => bind([body]));
    const ordered = [...new Set([...byBinding.flat(), ...bound])];
    let bodies = [ordered];
    const repeated = (!row.item.unit || row.item.unit === "ea") && Number.isSafeInteger(row.item.quantity) && row.item.quantity > 1;
    if (repeated && ordered.length === row.item.quantity) bodies = ordered.map(name => [name]);
    else if (repeated && byBinding.length === row.item.quantity && byBinding.every(group => group.length)
      && new Set(byBinding.flat()).size === byBinding.flat().length) bodies = byBinding;
    groups = bodies.map(bodies => ({ bodies }));
  }
  return groups.filter(group => group.bodies.length).map(({ bodies, label }) => ({
    name: bodies[0], bodies, label: label || instanceLabel(bodies[0]),
    path: row.path.slice(0, -1).map(item => index.get(item.material)?.description).filter(Boolean),
  }));
}

export function instancesInScene(catalog, assembly, material, names, options = {}) {
  names = [...new Set(names.map(instanceBody))];
  const index = materialIndex(catalog), seen = new Set(), instances = [];
  for (const row of explodeBom(catalog, assembly, options).filter(row => row.material.id === material)) {
    for (const instance of rowInstances(catalog, row, names, index, options)) {
      const { bodies } = instance;
      const key = [...bodies].sort().join("\n");
      if (seen.has(key)) continue;
      seen.add(key);
      instances.push(instance);
    }
  }
  return instances;
}

// Component clicks use the same physical copies as Location. Opening a part exposes its
// own bodies; assembly records and unallocated stock lengths do not become a single part.
export function componentUnitsInScene(catalog, assembly, names, options = {}) {
  names = [...new Set(names.map(instanceBody))];
  const index = materialIndex(catalog), units = [], seen = new Set();
  if (index.get(assembly)?.kind !== "assembly") return units;
  for (const row of explodeBom(catalog, assembly, options)) {
    if (row.material.kind === "assembly") continue;
    const { item } = row;
    if (!item.placements?.length && (item.unit && item.unit !== "ea"
      || !Number.isSafeInteger(item.quantity) || item.quantity < 1)) continue;
    const instances = rowInstances(catalog, row, names, index, options);
    if (!item.placements?.length && item.quantity > 1 && instances.length !== item.quantity) continue;
    for (const instance of instances) {
      if (instance.bodies.length < 2) continue;
      const key = [...instance.bodies].sort().join("\n");
      if (seen.has(key)) continue;
      seen.add(key);
      units.push({ ...instance, material: row.material.id });
    }
  }
  return units;
}

export function unitForBody(units, name) {
  return units.find(unit => unit.bodies.some(body => matchesBody(name, body))) || null;
}

// The same installed unit drives both its request order and its on-screen selection.
export function membersOfInstance(catalog, file, name, names, options = {}) {
  const owner = materialForFile(catalog, file);
  const material = materialForComponent(catalog, file, name, options);
  const available = [...new Set(names.map(instanceBody))];
  const unit = owner && material && instancesInScene(catalog, owner.id, material.id, available, options)
    .find(instance => instance.bodies.includes(name));
  return unit?.bodies || available.filter(body => matchesBody(body, name));
}

export function instanceMaterialHash(assembly, name) {
  return `material:${encodeURIComponent(assembly)}?instance=${encodeURIComponent(name)}`;
}
