// The models beside a part that the walk cannot reach — the map the 3D viewer's
// Related rail offers (web/public/js/viewer/related-nav.js).
//
// The drill-down (component-sources.js) walks INTO an assembly: a click on a
// solid opens the file that solid was modelled in, so everything it reaches is
// something an assembly holds. No assembly holds a mold. It is the negative of
// a part, printed to cast it, and it stands outside the machine.
//
// WHAT RELATED MEANS HERE IS A DIRECTORY NAMED FOR ANOTHER DIRECTORY. The funnel
// is modelled in `printed-parts/zone-c/funnel/` and its mold in
// `printed-parts/zone-c/funnel-mold/` — siblings, one leaf extending the other
// at a `-` boundary. That is the whole rule, and it reads both ways, so the
// funnel offers its mold and each mold half offers the funnel back.
//
// It also offers the other models in a part's own directory, which is how the
// reed bridge reaches its setting gauge.
//
// AN ASSEMBLY-BUILT TUBE HAS NO FILE OF ITS OWN, but it can still lead to the
// customer tool made for it. `relatedStepsForComponent` recognises the named
// 1/4-inch LLDPE bodies in the enclosure, cold core and faucet assemblies and
// offers the collet press. This is a relation, not a source claim: the tube was
// modelled in its assembly, while the button opens a different useful model.
//
// THIS IS A CONVENTION AND NOT A DECLARATION. A mold parked somewhere that does
// not name the part it casts is a mold this cannot find, and nothing here will
// say so — web/tests/related-steps.test.js holds every `-mold` directory in the
// tree to a part it resolves against, which is where a break announces itself.
//
// Paths are root-relative to `hardware/`, the same form `/api/steps` returns.

// `out` is where this repository puts what a tool wrote: the cut scenes under
// `assembly/scenes/out/`, the twelve frames of each quickstart study. They share
// a directory with each other and nothing else.
const isGenerated = (file) => file.split("/").includes("out");

const dirOf = (file) => file.slice(0, file.lastIndexOf("/"));
const leafOf = (dir) => dir.slice(dir.lastIndexOf("/") + 1);
const parentOf = (dir) => (dir.includes("/") ? dir.slice(0, dir.lastIndexOf("/")) : "");

// One leaf extending the other at a separator, which is what keeps `foam-cap`
// and `foam-assembly` apart while joining `funnel` to `funnel-mold`.
const extendsAt = (longer, shorter) =>
  longer.startsWith(shorter + "-") || longer.startsWith(shorter + "_");

// A FIXTURE IS DECLARED, NOT NAMED. The rule above reads directory names, and
// between a part and the equipment that makes it there is no name to read: the
// weld rotator stands in `printed-parts/fixtures/` because it is shop equipment
// and not a body of the machine, and the steel it welds stands in
// `cut-parts/carbonation/`. Neither path says the other, and neither should — so
// the pairing is written down here, and like a mold it reads both ways.
//
// A declaration costs the build nothing. It pairs two models that are already cut
// independently; it does not graft one into the other, and no payload grows.
//
// Keyed by the fixture, valued by the parts it makes.
export const FIXTURES = {
  "printed-parts/fixtures/weld-rotator/weld-rotator-assembly.step": [
    "cut-parts/carbonation/carbonator-tube/carbonator-tube.step",
    "cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step",
  ],
};

export const COLLET_PRESS = "printed-parts/collet-press/collet-press.step";

// The assembly-only tube names that are 1/4-inch OD and meet push-connect
// collets. Refrigerant copper, the 3/8-inch tube inside the faucet, foam and the
// atmospheric PRV vent are deliberately absent: this jaw does not fit them.
const COLLET_PRESS_TUBES = [
  /^tube-(?:carb|co2|customer|fluid|water)-/,
  /^(?:turn|step)-fluid-/,
  /^line-(?:carb-water-out|co2-in|reservoir-[ab](?:-fill)?|water-in)$/,
  /^flavor_tube_(?:neg|pos)_x$/,
  /^soda_umbilical_tube$/,
];

export const label = (file) =>
  file.slice(file.lastIndexOf("/") + 1).replace(/\.step$/i, "");

/**
 * Models useful with a named assembly component that has no STEP of its own.
 *
 * @param {string} name       assembly component name, optionally below a node
 * @param {string[]} allFiles every STEP path the site knows
 * @returns {{file: string, kind: "used-with"}[]}
 */
export function relatedStepsForComponent(name, allFiles) {
  if (!name || !Array.isArray(allFiles)) return [];
  const leaf = String(name).slice(String(name).lastIndexOf("/") + 1);
  if (!COLLET_PRESS_TUBES.some((pattern) => pattern.test(leaf))) return [];
  return allFiles.includes(COLLET_PRESS)
    ? [{ file: COLLET_PRESS, kind: "used-with" }]
    : [];
}

/**
 * The models related to `file`, nearest kind first.
 *
 * @param {string} file      root-relative `.step` path, as `/api/steps` returns
 * @param {string[]} allFiles  every such path the site knows
 * @param {string[]} [exclude]  models already standing in the walk
 * @returns {{file: string, kind: "beside"|"from"|"of"|"makes"|"made-on"}[]}
 *   `beside`  — another model in this part's own directory
 *   `from`    — a directory named for this one: the mold of this part
 *   `of`      — the directory this one is named for: the part this mold casts
 *   `makes`   — a part this fixture is built to make (declared, see FIXTURES)
 *   `made-on` — the fixture this part is made on (declared, see FIXTURES)
 */
export function relatedSteps(file, allFiles, exclude = []) {
  if (!file || !Array.isArray(allFiles) || isGenerated(file)) return [];
  const here = dirOf(file);
  const leaf = leafOf(here);
  const parent = parentOf(here);
  const skip = new Set([file, ...exclude]);

  const out = [];
  for (const other of allFiles) {
    if (skip.has(other) || isGenerated(other) || !/\.step$/i.test(other)) continue;
    const dir = dirOf(other);
    if (dir === here) { out.push({ file: other, kind: "beside" }); continue; }
    if (parentOf(dir) !== parent) continue;
    const otherLeaf = leafOf(dir);
    if (extendsAt(otherLeaf, leaf)) out.push({ file: other, kind: "from" });
    else if (extendsAt(leaf, otherLeaf)) out.push({ file: other, kind: "of" });
  }

  // The declared pairs, both directions, held to what the tree actually carries.
  // A fixture the build has not cut is simply not offered.
  const held = new Set(allFiles);
  for (const part of FIXTURES[file] || []) {
    if (!skip.has(part) && held.has(part)) out.push({ file: part, kind: "makes" });
  }
  for (const [fixture, made] of Object.entries(FIXTURES)) {
    if (fixture === file || !made.includes(file)) continue;
    if (!skip.has(fixture) && held.has(fixture)) out.push({ file: fixture, kind: "made-on" });
  }

  const order = { beside: 0, from: 1, of: 2, "made-on": 3, makes: 4 };
  out.sort((a, b) => order[a.kind] - order[b.kind] || a.file.localeCompare(b.file));
  return out;
}

// What the rail writes above each run of chips. KEY ORDER IS RENDER ORDER —
// related-nav.js walks these keys, so a kind added here draws itself and a kind
// added without a caption draws nothing.
export const KIND_CAPTIONS = {
  "used-with": "Used with",
  beside: "Beside it",
  from: "Made for it",
  of: "Casts",
  "made-on": "Made on",
  makes: "Makes",
};
