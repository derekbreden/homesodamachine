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

// A text's search words. Case, accents and subscripts fold away (CO₂ is co2),
// a size reads the same with or without its space (16awg is 16 AWG, m3x8 is
// M3 × 8) and a plural reads as its singular.
export function searchWords(text) {
  return String(text ?? "").normalize("NFKD").toLowerCase().replace(/\p{M}/gu, "").replace(/×/g, " x ")
    .replace(/(\d)\.(?=\d)/g, "$1\0").replace(/[^a-z0-9\0]+/g, " ")
    .replace(/(\d)(?=[a-z])/g, "$1 ").replace(/([a-z])(?=\d)/g, "$1 ").replace(/\0/g, ".")
    .split(" ").filter(Boolean).map((word) => /^[a-z]{4,}$/.test(word) && /[^s]s$/.test(word) ? word.slice(0, -1) : word);
}

// Words the build records use interchangeably. Each group's spellings find one another.
const SEARCH_SYNONYMS = [["earth", "ground"], ["zip tie", "cable tie"], ["ptfe", "teflon", "thread tape"],
  ["push to connect", "push connect", "push fit", "quick connect"], ["screw", "bolt"], ["r600a", "isobutane"],
  ["psu", "power supply"], ["o ring", "oring"], ["braze", "brazing", "silver solder"]].map((group) => group.map(searchWords));

// A query is a list of terms, each a set of alternative word runs. A typed word
// is one run, so "16awg" reads as 16 AWG in that order; a synonym phrase
// spanning whole typed words brings in its group's other spellings. A word of
// three or more letters matches the start of a word, numbers and shorter words
// match whole, and the query's last word matches as a prefix while it is typed.
export function searchTerms(query) {
  const typed = String(query ?? "").trim().split(/\s+/).map(searchWords).filter((run) => run.length);
  const phraseEnd = (start, run) => {
    for (let end = start, words = []; end < typed.length && words.length < run.length; end++) {
      words.push(...typed[end]);
      if (words.length === run.length && words.every((word, i) => word === run[i])) return end;
    }
    return -1;
  };
  const terms = [];
  for (let start = 0; start < typed.length;) {
    let end = start, group = null, spelled = null;
    for (const spellings of SEARCH_SYNONYMS) for (const run of spellings) {
      const last = phraseEnd(start, run);
      if (last >= end && (!group || last > end)) { end = last; group = spellings; spelled = run; }
    }
    const typing = end === typed.length - 1;
    const runs = group ? [spelled, ...group.filter((run) => run !== spelled)] : [typed[start]];
    terms.push(runs.map((run, r) => Object.assign(run.map((word, i) =>
      ({ word, prefix: (typing && i === run.length - 1) || (word.length >= 3 && /^[a-z]+$/.test(word)) })), { synonym: r > 0 })));
    start = end + 1;
  }
  return terms;
}

// The first of a term's runs found in the words: the spelling typed, then its synonyms.
const runIn = (term, words) => term.find((run) => words.some((_, at) => run.every(({ word, prefix }, i) =>
  words[at + i] === word || (prefix && words[at + i]?.startsWith(word)))));

export function termsMatch(terms, words) {
  return terms.length > 0 && terms.every((term) => runIn(term, words));
}

// What search reads, built once per served catalog. A material is found by its
// own names first, then by the listing it is bought as, then by its model
// files. Stock and supplies have no part number of their own; their ledger
// lines, costed on the parts and assemblies that use them, are results too.
const searchIndexes = new WeakMap();
function searchIndex(catalog) {
  if (searchIndexes.has(catalog)) return searchIndexes.get(catalog);
  const direct = catalog.costs?.direct || {};
  const asin = (href) => href?.match(/\/dp\/([A-Z0-9]{10})/)?.[1] || "";
  const materials = (catalog.materials || []).map((material) => ({
    material,
    fields: [
      { weight: 3, words: searchWords([material.id, material.description, material.manufacturer_number, ...(material.aliases || [])].join(" ")) },
      { weight: 2, words: searchWords((direct[material.id]?.elements || []).filter((element) => element.kind === "price")
        .map((element) => `${element.label} ${asin(element.href)}`).join(" ")) },
      { weight: 1, words: searchWords((material.models || []).map((model) => model.file).join(" ")) },
    ],
  }));
  const lines = new Map();
  for (const [id, cost] of Object.entries(direct)) for (const element of cost.elements || []) {
    if (!["price", "stock", "supplies"].includes(element.kind)) continue;
    const line = lines.get(element.label) || { label: element.label, href: element.href || null, kinds: new Set(), holders: [] };
    line.kinds.add(element.kind);
    line.holders.push({ id, usd: element.usd || 0 });
    lines.set(element.label, line);
  }
  const index = {
    materials,
    lines: [...lines.values()].filter((line) => !line.kinds.has("price")).map((line) => ({
      ...line, holders: line.holders.sort((a, b) => b.usd - a.usd), words: searchWords(`${line.label} ${asin(line.href)}`),
    })),
  };
  searchIndexes.set(catalog, index);
  return index;
}

// Hits ranked by where each term matched: a material's own names outrank a
// ledger line, which outranks a model file path, and a synonym ranks below the
// spelling typed. A line costed only on parts already found is left out.
export function searchCatalog(catalog, query) {
  const terms = searchTerms(query);
  if (!catalog || !terms.length) return [];
  const index = searchIndex(catalog), hits = [];
  const scored = (fields) => {
    let score = 0;
    const found = terms.every((term) => fields.some(({ weight, words }) => {
      const run = runIn(term, words);
      if (run) score += weight - (run.synonym ? 0.5 : 0);
      return run;
    }));
    return found ? score : 0;
  };
  for (const { material, fields } of index.materials) {
    const score = scored(fields);
    if (score) hits.push({ material, score });
  }
  const found = new Set(hits.map((hit) => hit.material.id));
  for (const line of index.lines) {
    const score = line.holders.every((holder) => found.has(holder.id)) ? 0 : scored([{ weight: 2, words: line.words }]);
    if (score) hits.push({ line, score });
  }
  return hits.sort((a, b) => b.score - a.score || !!a.line - !!b.line);
}

export function searchMaterials(catalog, query) {
  return searchCatalog(catalog, query).filter((hit) => hit.material).map((hit) => hit.material);
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
