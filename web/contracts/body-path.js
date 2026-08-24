// What a body's name says about where it stands.
//
// A BODY IS NAMED FOR THE BRANCH IT HANGS ON. The appliance holds the cold core as a real
// sub-assembly — `manifold-layout/enclosure-assembly.step` carries a `cold-core` node with the
// core's bodies inside it — and each of those bodies is called `cold-core/evap-coil`. The STEP
// carries the nesting and the name carries it too, because the two are the same fact and only
// one of them survives every reader: occt-import-js 0.0.23 reports a component node as
// CHILDLESS, so the tree does not reach the page through the STEP route whatever the file
// holds. It carries names faithfully, so the name is how the structure arrives.
//
// A SLASH IS AN INDEX ONLY WHEN DIGITS FOLLOW IT. `display/1` is the first solid of one body;
// `cold-core/evap-coil` is one body of the core; `cold-core/evap-coil/2` is both at once.
// Three places state that rule and this is the one they all read:
//   - viewer/step.js `bodyName` takes the index off a mesh name
//   - scripts/_cadq_export.py `_SOLID_INDEX_RE` groups a body's solids back together
//   - assembly/scenes/render_scenes.py `_LEAF_NAME` splits a payload leaf
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
