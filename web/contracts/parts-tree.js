// The parts tree — what /3d is a browse of.
//
// THE PAGE IS THE MACHINE'S THREE ASSEMBLIES, one thumbnail each:
//
//   Enclosure assembly    manifold-layout/enclosure-assembly.step
//   Cold core assembly    cold-core-layout/cold-core-assembly.step
//   Faucet assembly       faucet-layout/faucet-assembly.step
//
// A PART INSIDE AN ASSEMBLY IS REACHED BY SELECTING IT THERE. Open the assembly,
// arm Select → Component, click the solid: the panel names the component and
// offers the file it was modelled in, which loads into the same modal with the
// trail back (contracts/component-sources.js, viewer/component-picker.js,
// viewer/step-nav.js). The page lists neither those parts nor the purchased
// geometry the assemblies place.
//
// WHAT NO ASSEMBLY HANDS OVER STANDS ON A SHELF UNDER THE THREE — the moulds,
// mandrels, gauges and print coupons a bench makes in order to make the machine;
// the soft parts modelled beside their host without a seat in it; the bench
// scenes, each a picture of a group of bodies rather than a body; and the two cut
// plates, whose shape an assembly does place and whose file is a `.dxf` the
// drill-down does not open.
//
// EVERY FILE THE WALKERS OFFER IS CLAIMED: `LOOSE.holds` takes the shelf,
// `INSIDE_DIRS` names the directories an assembly places from, and a directory in
// neither comes back in `unseated`, which the page names.
//
// A PART IS A NAME, NOT A FILE. `endcap-circular-2hole` is a `.step` solid and the
// `.dxf` the laser reads, and it is one part with two representations —
// `seatParts` folds files sharing a stem in a directory into one card carrying
// both.
//
// Produced from web/lib/walk.js's file lists by way of /api/{steps,dxf,glbs};
// consumed by web/public/js/viewer/parts.js; pinned by web/tests/parts-tree.test.js.
//
// EVERY PICTURE THIS REPOSITORY DRAWS COMES THROUGH THE PAGE THIS BUILDS. The
// render family in tools/render/ — render-step.js, render-step-posed.js (which
// hardware/assembly/scenes/render_scenes.py drives), render-dxf.js,
// render-view.js, render-step-side-by-side.js, render-thumbnails.js,
// screenshot-site.js — each stands the server and opens `/3d`, and `main.js`
// runs `applyInitialRoute` only after `buildGrid`. So a throw in `seatParts` or
// in `parts.js` never reaches a browser a person is looking at: it reaches a CAD
// build, as a mount that never happens and a two-minute timeout on a scene.

// `assembly/scenes/out/` is where render_scenes.py lays a scene down on its way
// to the GLB beside it. .gitignore holds it; a machine that has rendered scenes
// carries it and the repository does not.
export const EXCLUDED_DIRS = ["assembly/scenes/out"];

// Scene GLBs are named one by one rather than by their directory, so a scene added
// in hardware/assembly/scenes/_scenes.py is a line owed here — that file says so,
// and the unseated gate is what enforces it.
const SCENES = "assembly/scenes/glb";

export const ASSEMBLIES = [
  {
    id: "enclosure-assembly",
    label: "Enclosure assembly",
    model: "manifold-layout/enclosure-assembly.step",
    note: "The packed appliance — the refrigeration stratum, the flavor manifold standing " +
          "on it, and the printed box around them. It places the cold core as one solid; " +
          "the core's own pieces are in the assembly below.",
  },
  {
    id: "cold-core",
    label: "Cold core assembly",
    model: "cold-core-layout/cold-core-assembly.step",
    note: "The core as the bench sees it — the vessel that fills it, the coil wound on that, " +
          "both reservoirs in their pockets, every fitting made up, and the lines among them.",
  },
  {
    id: "faucet",
    label: "Faucet assembly",
    model: "faucet-layout/faucet-assembly.step",
    note: "The column the counter is clamped in: the printed stack around the harvested " +
          "Westbrass body, the display on the tip, and the three tubes running down past " +
          "the cut plate into the umbilical.",
  },
];

// The shelf. A mixed directory is named file by file:
// `printed-parts/cold-core/reservoir` holds four parts the cold core seats and
// three soft ones it does not.
export const LOOSE = {
  id: "loose",
  label: "Not reachable from an assembly",
  note: "What none of the three above hands over: the moulds, mandrels, gauges and print " +
        "coupons a bench makes in order to make the machine; the gaskets, washers and rings " +
        "modelled beside their host without a seat in it; the bench scenes, each a picture of " +
        "a group of bodies rather than a body; and the two cut plates, which an assembly " +
        "places as a shape and keeps as a drawing.",
  holds: [
    // Tooling and test prints — made to make the machine, never part of it.
    "printed-parts/cold-core/coil-mandrel",
    "printed-parts/cold-core/reed-bridge/reed-bridge-setting-gauge.step",
    "printed-parts/enclosure/texture-coupon-vent",
    "printed-parts/enclosure/texture-coupons",
    "printed-parts/zone-c/hopper-funnel-mold",
    // Modelled beside their host and seated in no assembly. The assemblies build
    // their own washers and seals as primitives; the routes solid and the pcba
    // tray stand beside the stacks rather than in them.
    "printed-parts/cold-core/foam-assembly/internal-routes.step",
    "printed-parts/cold-core/foam-cap/foam-cap-gasket.step",
    "printed-parts/cold-core/reservoir/reservoir-bulkhead-seal-dry.step",
    "printed-parts/cold-core/reservoir/reservoir-gasket.step",
    "printed-parts/cold-core/reservoir/reservoir-retaining-ring.step",
    "printed-parts/electronics/pcba-tray/pcba-assembly.step",
    // The cut plates. Their shape stands in an assembly — `collet-plate` in the
    // enclosure, `under_counter_plate` in the faucet — and the file the laser
    // reads is a `.dxf`, which the drill-down out of a STEP does not open.
    "cut-parts/faucet/touch-flo-under-counter-plate",
    "manifold-layout/collet-plate.dxf",
    // Bench scenes — one unit per picture, as it stands on the bench that builds
    // it. hardware/assembly/scenes/_scenes.py states each scene's roots.
    `${SCENES}/back-half.glb`, `${SCENES}/back-top.glb`, `${SCENES}/cap-lid.glb`,
    `${SCENES}/cap-lid-fill.glb`, `${SCENES}/cold-core.glb`, `${SCENES}/cold-core-open.glb`,
    `${SCENES}/en04-stratum.glb`, `${SCENES}/en06-column.glb`, `${SCENES}/front-top.glb`,
    `${SCENES}/hopper-drain.glb`, `${SCENES}/pump-cartridge.glb`,
  ],
};

// The directories the three assemblies place from — the printed and cut parts,
// the sub-layouts, the board, and the purchased geometry under `reference/` that
// hardware/README.md describes. The page lists none of it; a part is reached by
// selecting its solid in the assembly that stands it up. A directory nobody has
// placed anywhere is in neither this list nor the shelf, and comes back unseated.
export const INSIDE_DIRS = [
  "cold-core-layout",
  "cut-parts/carbonation",
  "faucet-layout",
  "manifold-layout",
  "off-the-shelf-parts",
  "pcb",
  "printed-parts/cold-core/copper-plugs",
  "printed-parts/cold-core/foam-assembly",
  "printed-parts/cold-core/foam-cap",
  "printed-parts/cold-core/foam-shell",
  "printed-parts/cold-core/prv-shroud",
  "printed-parts/cold-core/reed-bridge",
  "printed-parts/cold-core/reservoir",
  "printed-parts/electronics",
  "printed-parts/enclosure",
  "printed-parts/faucet/touch-flo-mounting-gasket",
  "printed-parts/faucet/touch-flo-mounting-plate",
  "printed-parts/faucet/touch-flo-shell",
  "printed-parts/faucet/touch-flo-tpu-o-ring",
  "printed-parts/faucet/tube-collar",
  "printed-parts/refrigeration",
  "printed-parts/valve-seat",
  "printed-parts/zone-c",
  "reference",
];

// --- reading a file list into the tree ---------------------------------------

const KIND_RANK = { step: 0, dxf: 1, glb: 2 };

function dirOf(file) {
  const i = file.lastIndexOf("/");
  return i < 0 ? "" : file.slice(0, i);
}

function stemOf(file) {
  return file.slice(file.lastIndexOf("/") + 1).replace(/\.(step|dxf|glb)$/, "");
}

function under(file, dir) {
  return file === dir || file.startsWith(dir + "/");
}

// THE WHOLE OF A DIRECTORY LEADS IT: the file named for its own directory
// (`foam-shell/foam-shell.step`), or the one whose name ends in `-assembly`
// (`pcba-tray/pcba-assembly.step`). The pieces follow it, alphabetically.
export function isWhole(file) {
  const stem = stemOf(file);
  const dir = dirOf(file);
  return stem.endsWith("-assembly") || stem === dir.slice(dir.lastIndexOf("/") + 1);
}

function partOrder(a, b) {
  if (a.dir !== b.dir) return a.dir.localeCompare(b.dir);
  const wa = isWhole(a.primary.file) ? 0 : 1;
  const wb = isWhole(b.primary.file) ? 0 : 1;
  return wa - wb || a.name.localeCompare(b.name);
}

// Fold a flat list of `{file, type}` into parts: one per stem per directory,
// carrying every representation that stem has. The richest representation is
// what the card opens and draws its thumbnail from.
function toParts(entries) {
  const byKey = new Map();
  for (const e of entries) {
    const key = `${dirOf(e.file)}/${stemOf(e.file)}`;
    if (!byKey.has(key)) {
      byKey.set(key, { key, dir: dirOf(e.file), name: stemOf(e.file), kinds: [] });
    }
    byKey.get(key).kinds.push(e);
  }
  const parts = [];
  for (const p of byKey.values()) {
    p.kinds.sort((a, b) => KIND_RANK[a.type] - KIND_RANK[b.type]);
    p.primary = p.kinds[0];
    parts.push(p);
  }
  return parts.sort(partOrder);
}

/**
 * Seat every file the walkers offer into the tree.
 *
 * @param {{steps: string[], dxfs: string[], glbs: string[]}} files root-relative paths
 * @returns {{assemblies: Object[], loose: Object, inside: Object[], unseated: string[]}}
 *   `assemblies` each carry the `model` part the page draws; `loose` carries the
 *   shelf's `parts`; `inside` is what the assemblies place, which the page does
 *   not draw and the gate counts. `unseated` names every directory holding a file
 *   nothing claims — a gap the page shows rather than swallows.
 */
export function seatParts({ steps = [], dxfs = [], glbs = [] } = {}) {
  const pool = [
    ...steps.map((file) => ({ file, type: "step" })),
    ...dxfs.map((file) => ({ file, type: "dxf" })),
    ...glbs.map((file) => ({ file, type: "glb" })),
  ].filter((e) => !EXCLUDED_DIRS.some((d) => under(e.file, d)));

  const taken = new Set();
  const claim = (holds) => {
    const got = pool.filter((e) => !taken.has(e.file) && holds.some((d) => under(e.file, d)));
    for (const e of got) taken.add(e.file);
    return toParts(got);
  };

  // Order matters: each assembly's own model first, so it is the card and not one
  // of the parts under the directory it shares; then the shelf, which names files
  // inside directories the assemblies otherwise sweep whole.
  const assemblies = ASSEMBLIES.map((a) => ({ ...a, model: claim([a.model])[0] || null }));
  const loose = { ...LOOSE, parts: claim(LOOSE.holds) };
  const inside = claim(INSIDE_DIRS);

  const unseated = [...new Set(
    pool.filter((e) => !taken.has(e.file)).map((e) => dirOf(e.file)),
  )].sort();

  return { assemblies, loose, inside, unseated };
}
