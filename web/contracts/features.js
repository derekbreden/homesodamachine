// Construction identities select existing triangle ranges in browsers and geometry tools.
export const featureKey = (body, id) => `${body}::${id}`;
export function splitFeatureKey(value) {
  const at = String(value || "").lastIndexOf("::");
  return at < 0 ? null : { body: value.slice(0, at), id: value.slice(at + 2) };
}
export const instanceBody = (name) => String(name || "").replace(/\/\d+$/, "");
export function instanceLabel(name) {
  const roles = { "wago-h": "Mains live Wago", "wago-g": "Mains earth Wago", "wago-n": "Mains neutral Wago" };
  const leaf = instanceBody(name).split("/").at(-1);
  return roles[leaf] || leaf.replace(/[-_]+/g, " ").replace(/^./, s => s.toUpperCase());
}

export function validFeatures(features, triangles) {
  return Array.isArray(features) ? features.filter(f => f && typeof f.id === "string" && f.id
    && typeof f.label === "string" && Array.isArray(f.triangles) && f.triangles.length
    && f.triangles.every((r, i, ranges) => Array.isArray(r) && r.length === 2 && r.every(Number.isSafeInteger)
      && r[0] >= 0 && r[0] <= r[1] && r[1] < triangles
      && (!i || ranges[i - 1][1] < r[0]))) : [];
}

export function containsTriangle(feature, triangle) {
  let lo = 0, hi = feature.triangles.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (feature.triangles[mid][1] < triangle) lo = mid + 1;
    else hi = mid;
  }
  return lo < feature.triangles.length && feature.triangles[lo][0] <= triangle;
}

export function featureIndices(indices, feature) {
  const count = feature.triangles.reduce((n, [a, b]) => n + (b - a + 1) * 3, 0);
  const result = new Uint32Array(count);
  let offset = 0;
  for (const [a, b] of feature.triangles) {
    const chunk = indices.subarray(a * 3, (b + 1) * 3);
    result.set(chunk, offset); offset += chunk.length;
  }
  return result;
}

export function matchFeatures(query, features) {
  const normalize = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const needle = normalize(query.replace(/^feature\s*:\s*/i, ""));
  if (!needle) return [];
  const exact = features.filter(f => [f.key, f.id, f.label].some(s => normalize(s) === needle));
  if (exact.length) return exact;
  const words = needle.split(/\s+/).map(word =>
    ({ grip: "handhold", grips: "handhold", handholds: "handhold" })[word] || word);
  return features.filter(f => {
    const haystack = normalize([f.body, f.id, f.label, ...(f.related || []),
      ...(f.related || []).map(instanceLabel)].join(" "));
    return words.every(word => haystack.includes(word));
  });
}

export function objectFeatures(node, object) {
  return (node.entries || []).flatMap((entry, i) => (object.meshes?.[i]?.features || []).map(feature => ({
    ...feature, body: instanceBody(entry.name), key: featureKey(instanceBody(entry.name), feature.id),
    transform: node.transform || null, asset: node.asset, source_model: node.source || null,
  })));
}
