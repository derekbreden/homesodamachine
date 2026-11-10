// What a body's name says about where it stands.
//
// A body path retains the branches that hold it: `cold-core/evap-coil` names the coil
// inside the cold core. Native scene payloads preserve that identity with the part's
// placement; the browser's STEP fallback also carries it in the mesh name.
//
// A SLASH IS AN INDEX ONLY WHEN DIGITS FOLLOW IT. `display/1` is the first solid of one body;
// `cold-core/evap-coil` is one body of the core; `cold-core/evap-coil/2` is both at once.
// viewer/step.js `bodyName` removes a numeric solid suffix before these helpers read
// the body path. Native readers follow the same rule in tools/hsm/geometry/src/scene.rs
// and hardware/assembly/scenes/model_export/payload.rs.
//
// Held by web/tests/body-path.test.js.

/** The body's own name, out of everything holding it. `cold-core/evap-coil` -> `evap-coil`. */
export function leafOf(name) {
  const s = String(name ?? "");
  return s.slice(s.lastIndexOf("/") + 1);
}

/**
 * The sub-assemblies above `name`, outermost first.
 *
 * `cold-core/evap-coil` -> `["cold-core"]`. A body at the top of a machine has none, which is
 * what makes a machine with no sub-assembly in it read exactly as it did before there were any.
 */
export function heldBy(name) {
  const parts = String(name ?? "").split("/");
  return parts.slice(0, -1).map((_p, i) => parts.slice(0, i + 1).join("/"));
}

/** Whether `name` is `group` or stands anywhere inside it. */
export function standsIn(name, group) {
  if (!group) return false;
  const s = String(name ?? "");
  return s === group || s.startsWith(group + "/");
}
