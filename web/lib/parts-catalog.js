// The Parts page uses the shipped BOM and the registered tooling to select its part cards.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { materialHash } from "../contracts/material-tabs.js";
import { explodeBom, materialIndex, modelForMaterial } from "../contracts/materials.js";
import { FAUCET_FINISHES } from "../contracts/faucet-options.js";
import { readBomLines } from "./bom-lines.js";
import { readMaterialCatalog } from "./material-catalog.js";

export const partThumbnailDirectory = fileURLToPath(new URL("../public/parts-thumbnails/", import.meta.url));

// The per-unit sourcing record names the providers that deliver work made to the project's order.
const providers = [
  ["SendCutSend", /\bSendCutSend\b/i],
  ["JLCPCB", /\bJLCPCB\b/i],
  ["Lulu", /\bLulu\b/i],
  ["OnlineMetals", /\bOnlineMetals #12498\b/i],
];

export function selectCatalogParts(catalog, ledger) {
  const index = materialIndex(catalog);
  const options = { finish: FAUCET_FINISHES[0].id };
  const toolRoots = catalog.roots.filter(id => index.get(id)?.kind === "tooling");
  const subjects = (root) => explodeBom(catalog, root, options).map(({ material }) => material);
  const machine = subjects(catalog.cost_root);
  const tools = [...toolRoots.flatMap(subjects), ...catalog.materials.filter(material => material.kind === "equipment")];
  const sourcing = new Map();
  for (const line of ledger) {
    const provider = providers.find(([, pattern]) => pattern.test(line.name))?.[0];
    for (const { id } of line.targets || []) {
      if (!sourcing.has(id) || provider) sourcing.set(id, { provider, section: line.sectionName });
    }
  }

  function group(materials) {
    const parts = [...new Map(materials.map(material => [material.id, material])).values()]
      .map(material => ({ material, ...sourcing.get(material.id) }));
    const byName = (a, b) => a.material.description.localeCompare(b.material.description, "en", { numeric: true });
    return {
      madeToOrder: parts.filter(part => part.provider).sort((a, b) =>
        a.provider.localeCompare(b.provider) || byName(a, b)),
      offTheShelf: parts.filter(part => !part.provider && ["purchased", "equipment"].includes(part.material.kind)).sort(byName),
    };
  }
  return { machine: group(machine), tools: group(tools) };
}

export function readPartsCatalog(hardwareDir) {
  const catalog = readMaterialCatalog(hardwareDir);
  const groups = selectCatalogParts(catalog, readBomLines(hardwareDir));
  const images = new Set(fs.existsSync(partThumbnailDirectory) ? fs.readdirSync(partThumbnailDirectory) : []);
  const cards = (parts) => parts.map(({ material, provider, section }) => {
    const name = `${material.id}.webp`;
    return {
      id: material.id,
      name: material.description,
      href: provider === "Lulu" ? "/read/install-guide/install-guide.pdf"
        : `/parts#${materialHash(material.id, { view: material.pcb && "pcb" })}`,
      image: images.has(name) ? `/parts-thumbnails/${name}` : null,
      ...(provider && { provider }),
      ...(section && { section }),
    };
  });
  const result = Object.fromEntries(Object.entries(groups).map(([scope, entries]) => [scope, {
    madeToOrder: cards(entries.madeToOrder),
    offTheShelf: cards(entries.offTheShelf),
  }]));
  const index = materialIndex(catalog);
  result.tools.assemblies = catalog.roots.map(id => index.get(id))
    .filter(material => material?.kind === "tooling" && modelForMaterial(catalog, material.id))
    .map(({ id, description }) => ({ id, name: description, href: `/parts#${materialHash(id)}` }));
  return result;
}
