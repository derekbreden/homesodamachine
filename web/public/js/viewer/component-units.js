// Resolve each drawn body to its selectable component in the mounted model.
import { materialForView } from "/contracts/materials.js";
import { componentGroupsInModel, componentUnitsInScene } from "/contracts/material-instances.js";
import { instanceBody, splitFeatureKey } from "/contracts/features.js";
import { heldBy } from "/contracts/body-path.js";
import { state } from "./state.js";

export const mountedFile = () =>
  state.currentGroup?.userData.sharedFile || (state.mountedDetail?.type === "step" ? state.mountedDetail.file : null);
const namingOptions = () => ({ finish: state.faucetFinish });
// Index authored placements once per scene/catalog/finish, including parts still arriving.
let unitsCache = null;
export function installedUnits() {
  const group = state.currentGroup, catalog = state.materialCatalog, file = mountedFile();
  if (!group || !file) return null;
  const head = group.userData.sharedHead, finish = state.faucetFinish;
  if (!unitsCache || unitsCache.group !== group || unitsCache.catalog !== catalog
      || unitsCache.file !== file || unitsCache.head !== head || unitsCache.finish !== finish
      || (!head && unitsCache.count !== group.children.length)) {
    const material = materialForView(catalog, file, namingOptions());
    const names = head ? head.meshes.flatMap(node => node.entries?.map(entry => entry.name) || [node.name])
      : group.children.filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name);
    const units = componentUnitsInScene(catalog, material?.id, names, namingOptions());
    const groups = componentGroupsInModel(catalog, file, names);
    const paths = new Set();
    for (const raw of names) {
      const body = instanceBody(raw);
      paths.add(body);
      for (const parent of heldBy(body)) paths.add(parent);
    }
    const byBody = new Map(), groupByBody = new Map(), groupByName = new Map();
    for (const unit of units) for (const body of unit.bodies) byBody.set(body, unit);
    for (const component of groups) {
      groupByName.set(component.name, component);
      for (const body of component.bodies) groupByBody.set(body, component);
    }
    unitsCache = { group, catalog, file, head, finish, count: group.children.length, paths, byBody, groupByBody, groupByName };
  }
  return unitsCache;
}

// Physical placements stay addressable from Materials and from existing saved views.
export function unitForKey(name, units = installedUnits()) {
  return units?.groupByName.get(name) || units?.byBody.get(name);
}
export function componentUnit(name, includeGroups = true) {
  if (!name || splitFeatureKey(name)) return null;
  const units = installedUnits();
  return (includeGroups && units?.groupByBody.get(name)) || unitForKey(name, units);
}
export const componentOwner = name => componentUnit(name)?.name || name;
