// Engineering identities and relationships. Files are representations of materials;
// neither file names nor CAD solid counts allocate identities or quantities.
export function materialIndex(catalog) {
  return new Map((catalog?.materials || []).map((material) => [material.id, material]));
}

export function materialForFile(catalog, file) {
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
