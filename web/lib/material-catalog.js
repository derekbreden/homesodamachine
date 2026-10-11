import fs from "node:fs";
import path from "node:path";

export function readMaterialCatalog(hardwareDir) {
  const catalog = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger/materials.json"), "utf8"));
  for (const material of catalog.materials) {
    const imported = material.bom?.imports;
    if (!imported) continue;
    const sourcePath = path.resolve(hardwareDir, imported.source);
    if (!sourcePath.startsWith(path.resolve(hardwareDir) + path.sep)) throw new Error("Invalid material source");
    const source = JSON.parse(fs.readFileSync(sourcePath, "utf8"));
    for (const group of ["parts", "hardware"]) for (const part of source[group] || []) {
      const mapping = imported[group]?.[part.name];
      if (!mapping) continue;
      const { relationship, ...binding } = mapping;
      const item = { ...binding, quantity: part.quantity, unit: "ea", note: part.role, source: imported.source };
      if (relationship) (material.relations ||= []).push({ ...item, kind: relationship });
      else material.bom.items.push(item);
    }
    delete material.bom.imports;
  }
  return catalog;
}
