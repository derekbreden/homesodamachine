// Engineering identities and relationships. Files are representations of materials;
// neither file names nor CAD solid counts allocate identities or quantities.
import { stepLocation } from "./step-locations.js";
export function materialIndex(catalog) {
  return new Map((catalog?.materials || []).map((material) => [material.id, material]));
}

export function materialForFile(catalog, file) {
  file = stepLocation(file).file;
  return catalog?.materials?.find((m) => m.models?.some((model) => model.file === file && !model.context)) || null;
}

// A context names an enclosing assembly to inspect, while the selected material
// retains its own identity and BOM. It does not claim the enclosing CAD file.
export function modelForMaterial(catalog, id, seen = new Set()) {
  if (seen.has(id)) return null;
  const material = materialIndex(catalog).get(id);
  const models = material?.models?.filter((m) => !m.type || m.type === "step") || [];
  const own = models.find((m) => !m.context) || models[0];
  if (own) return own;
  for (const context of material?.contexts || []) {
    const model = modelForMaterial(catalog, context.material, new Set([...seen, id]));
    if (model) return { ...model, context: true };
  }
  return null;
}

export function bomItems(material, options = {}) {
  return (material?.bom?.items || []).filter((item) =>
    !item.when || Object.entries(item.when).every(([key, value]) => !options[key] || options[key] === value));
}

export function searchMaterials(catalog, query) {
  const normalized = (text) => text.toLocaleLowerCase().replace(/×/g, "x");
  const words = normalized(query).trim().split(/\s+/).filter(Boolean);
  return (catalog?.materials || []).filter((m) => {
    const text = [m.id, m.description, m.manufacturer_number, ...(m.aliases || []),
      ...(m.models || []).map((model) => model.file.replace(/[-_/]/g, " "))].join(" ");
    return words.every((word) => normalized(text).includes(word));
  });
}

// Each occurrence keeps its full path, so a reused part can appear at multiple
// locations and its quantity is multiplied through those assembly levels.
export function explodeBom(catalog, id, options = {}) {
  const index = materialIndex(catalog), rows = [];
  function visit(parent, path, quantity, seen) {
    if (seen.has(parent)) return;
    const nextSeen = new Set([...seen, parent]);
    for (const [occurrence, item] of bomItems(index.get(parent), options).entries()) {
      const material = index.get(item.material);
      if (!material) continue;
      const rowPath = [...path, { ...item, occurrence }];
      const total = typeof quantity === "number" && typeof item.quantity === "number" ? quantity * item.quantity : null;
      rows.push({ material, item, path: rowPath, depth: path.length, quantity: total });
      visit(material.id, rowPath, total, nextSeen);
    }
  }
  visit(id, [], 1, new Set());
  return rows;
}

// Count tree entries. A row's physical quantity is listed separately in the BOM.
export function bomCounts(catalog, id, options = {}) {
  const rows = explodeBom(catalog, id, options);
  return { direct: rows.filter((row) => row.depth === 0).length, total: rows.length };
}

export function bomCountText({ direct, total }) {
  return `${direct} direct · ${total} total BOM item${total === 1 ? "" : "s"}`;
}

// A reader's documents are the PDFs of the material and its containing assemblies, one entry per path.
export function materialDocuments(catalog, id, options = {}) {
  const index = materialIndex(catalog), docs = new Map();
  function collect(material, inherited = false) {
    for (const doc of material?.documents || [])
      if (doc.path.endsWith(".pdf") && !docs.has(doc.path)) docs.set(doc.path, { ...doc, inherited, owner: material.description });
  }
  collect(index.get(id));
  for (const row of whereUsed(catalog, id, options)) collect(row.material, true);
  return [...docs.values()];
}

export function whereUsed(catalog, id, options = {}) {
  const index = materialIndex(catalog), parents = new Map(), result = [];
  for (const parent of index.values()) for (const item of bomItems(parent, options)) {
    if (!parents.has(item.material)) parents.set(item.material, []);
    parents.get(item.material).push({ parent, item });
  }
  function climb(child, path, quantity, seen) {
    for (const { parent, item } of parents.get(child) || []) {
      if (seen.has(parent.id)) continue;
      const ids = [parent.id, ...path];
      const total = typeof quantity === "number" && typeof item.quantity === "number" ? quantity * item.quantity : null;
      result.push({ material: parent, path: ids, quantity: total, unit: item.unit, direct: path.length === 1 });
      climb(parent.id, ids, total, new Set([...seen, parent.id]));
    }
  }
  climb(id, [id], 1, new Set([id]));
  return result;
}

export function materialUses(catalog, id, options = {}) {
  const materials = catalog?.materials || [];
  const incoming = (kind) => materials.filter((material) => material.relations?.some((relation) =>
    relation.material === id && relation.kind === kind));
  return { assemblies: whereUsed(catalog, id, options), tools: incoming("tool-for"), equipment: incoming("used-with") };
}

const normalizedBody = (name) => name.replace(/\/\d+$/, "");
export function matchesBody(name, binding) {
  const body = normalizedBody(name);
  return body === binding || body.startsWith(binding + "/");
}

// Bindings are relative to their assembly. Prefixes carry a subassembly's frame
// into its parent; compounds and text solids may all represent one material.
export function occurrenceBodies(catalog, path, availableNames, options = {}) {
  const index = materialIndex(catalog), bindings = [];
  let prefix = "";
  for (const item of path.slice(0, -1)) prefix += item.prefix || "";
  function collect(item, frame, seen) {
    bindings.push(...(item.bodies || []).map((name) => frame + name));
    if (seen.has(item.material)) return;
    for (const child of bomItems(index.get(item.material), options))
      collect(child, frame + (item.prefix || ""), new Set([...seen, item.material]));
  }
  if (path.length) collect(path.at(-1), prefix, new Set());
  return [...availableNames].filter((name) => bindings.some((binding) => matchesBody(name, binding)));
}

export function occurrenceForBody(catalog, root, name, options = {}) {
  // The most specific binding wins, including a nested cold-core component.
  return explodeBom(catalog, root, options).filter((row) =>
    occurrenceBodies(catalog, row.path, [name], options).length).sort((a, b) => b.depth - a.depth)[0] || null;
}

// A CAD body is an occurrence of a material. Its key still identifies the
// geometry; its description comes from the same record as search and the BOM.
export function materialForComponent(catalog, file, name, options = {}) {
  const parent = materialForFile(catalog, file);
  if (!parent || !name) return null;
  const rows = explodeBom(catalog, parent.id, options);
  const occurrence = occurrenceForBody(catalog, parent.id, name, options);
  if (occurrence) return occurrence.material;
  const branch = rows.find((row) => row.item.prefix &&
    row.path.map((item) => item.prefix || "").join("").replace(/\/$/, "") === name);
  if (branch) return branch.material;
  const relation = parent.relations?.find((item) =>
    item.bodies?.some((body) => matchesBody(name, body)));
  if (relation) return materialIndex(catalog).get(relation.material) || null;
  return rows.length ? null : parent;
}

export function materialForView(catalog, file, options = {}) {
  const location = stepLocation(file);
  return location.component ? materialForComponent(catalog, location.file, location.component, options)
    : materialForFile(catalog, location.file);
}
