import fs from "node:fs";
import path from "node:path";
import { materialHash } from "../contracts/material-tabs.js";

// Associates published board views with their material workspaces.
const PCB_MATERIALS = new Map([["HSM-0048", "pcb/pcba/pcba.tsx"]]);

export function readMaterialCatalog(hardwareDir) {
  const catalog = JSON.parse(fs.readFileSync(path.join(hardwareDir, "ledger/materials.json"), "utf8"));
  for (const material of catalog.materials) {
    const board = PCB_MATERIALS.get(material.id);
    if (board) material.pcb = board;
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

export function pcbMaterialHash(source) {
  for (const [id, board] of PCB_MATERIALS) {
    if (!source || source === board) return materialHash(id, { view: "pcb" });
  }
  return null;
}
