// Installed locations bind BOM occurrences to the bodies already present in each model.
import { explodeBom, occurrenceBodies, materialIndex } from "./materials.js";
import { instanceBody, instanceLabel } from "./features.js";

export function instancesInScene(catalog, assembly, material, names, options = {}) {
  names = [...new Set(names.map(instanceBody))];
  const index = materialIndex(catalog), seen = new Set(), instances = [];
  for (const row of explodeBom(catalog, assembly, options).filter(row => row.material.id === material)) {
    const bound = occurrenceBodies(catalog, row.path, names, options);
    if (!bound.length) continue;
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
    for (const { bodies, label } of groups) {
      if (!bodies.length) continue;
      const key = [...bodies].sort().join("\n");
      if (seen.has(key)) continue;
      seen.add(key);
      instances.push({ name: bodies[0], bodies, label: label || instanceLabel(bodies[0]),
        path: row.path.slice(0, -1).map(item => index.get(item.material)?.description).filter(Boolean) });
    }
  }
  return instances;
}

export function instanceMaterialHash(assembly, name) {
  return `material:${encodeURIComponent(assembly)}?instance=${encodeURIComponent(name)}`;
}
