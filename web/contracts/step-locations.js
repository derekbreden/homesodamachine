// A component view reads its owning model and displays that named body or branch.
// It is a view of existing geometry, not a second CAD or printable part.
export function stepLocation(value) {
  const [file, query = ""] = String(value || "").split("?");
  return { file, component: new URLSearchParams(query).get("component") };
}

export function componentLocation(owner, name) {
  return stepLocation(owner).file + "?component=" + encodeURIComponent(name);
}

export function stepLabel(value) {
  const { file, component } = stepLocation(value);
  return component?.split("/").at(-1) || file.split("/").at(-1).replace(/\.step$/i, "");
}
