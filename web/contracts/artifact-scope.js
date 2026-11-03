// The website projects numbered catalog files from the complete build store.
// Legacy pointer files have one inventory; current writers also name the site projection.
export function websitePointers(pointers) {
  if (!pointers?.website) return pointers;
  return { ...pointers, solids: pointers.website.solids ?? {}, sidecars: pointers.website.sidecars ?? {} };
}
