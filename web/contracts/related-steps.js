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

export const label = (file) =>
  file.slice(file.lastIndexOf("/") + 1).replace(/\.step$/i, "");

/**
 * The models related to `file`, nearest kind first.
 *
 * @param {string} file      root-relative `.step` path, as `/api/steps` returns
 * @param {string[]} allFiles  every such path the site knows
 * @param {string[]} [exclude]  models already standing in the walk
 * @returns {{file: string, kind: "beside"|"from"|"of"}[]}
 *   `beside` — another model in this part's own directory
 *   `from`   — a directory named for this one: the mold of this part
 *   `of`     — the directory this one is named for: the part this mold casts
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

  const order = { beside: 0, from: 1, of: 2 };
  out.sort((a, b) => order[a.kind] - order[b.kind] || a.file.localeCompare(b.file));
  return out;
}

// What the rail writes above each run of chips.
export const KIND_CAPTIONS = {
  beside: "Beside it",
  from: "Made for it",
  of: "Casts",
};
