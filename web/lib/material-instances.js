// Location discovery reads existing scene headers without loading geometry or starting a build.
import path from "node:path";
import { materialIndex, modelForMaterial } from "../contracts/materials.js";
import { stepLocation } from "../contracts/step-locations.js";
import { instancesInScene, instanceMaterialHash } from "../contracts/material-instances.js";
import { readMeshHeader } from "./feature-catalog.js";

export function materialInstances(hardwareDir, catalog, material, options = {}) {
  const index = materialIndex(catalog), headers = new Map(), groups = [];
  for (const assembly of catalog.roots || []) {
    if (assembly === material) continue;
    const model = modelForMaterial(catalog, assembly);
    if (!model) continue;
    const { file } = stepLocation(model.file);
    try {
      if (!headers.has(file)) headers.set(file, readMeshHeader(path.join(hardwareDir, file + ".mesh")));
      const head = headers.get(file);
      const instances = instancesInScene(catalog, assembly, material, head.meshes.map(node => node.name), options);
      if (!instances.length) continue;
      groups.push({ assembly, label: index.get(assembly).description, file, revision: head.src,
        instances: instances.map(instance => ({ ...instance,
          url: "/3d#" + instanceMaterialHash(assembly, instance.name) })) });
    } catch (error) { if (error.code !== "ENOENT") throw error; }
  }
  return { material, groups };
}
