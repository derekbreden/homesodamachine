// The catalog opens its existing model and material workspace through URL fragments.
export const PARTS_PATH = "/parts";

export function isViewerHash(hash) {
  const raw = hash.replace(/^#/, "");
  if (/^(material|step|dxf|glb):/.test(raw)) return true;
  try { return /\.step(?:\?|$)/i.test(decodeURIComponent(raw)); }
  catch { return false; }
}
