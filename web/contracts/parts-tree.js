// The parts tree — what /3d is a browse of, and where each part stands in it.
//
// THREE ASSEMBLIES ARE THE TOP LEVEL, and everything the repository fabricates
// stands inside one of them:
//
//   Enclosure assembly   manifold-layout/enclosure-assembly.step
//   Cold core            cold-core-layout/cold-core-assembly.step
//   Faucet               faucet-layout/faucet-assembly.step
//
// with purchased geometry on a shelf of its own below them — hardware/README.md
// says what `reference/` is.
//
// EACH OF THE FOUR IS HEADED BY ONE MODEL, its `model`, claimed ahead of what
// stands under it so it leads rather than falling in among its own parts.
//
// A BRANCH'S GROUPS ARE THE READING ITS OWN DOC TAKES. The cold core's are
// hardware/future.md "Cold core (inside out)" — vessel, coil, shell, reservoirs,
// sensing; the enclosure's are hardware/printed-parts/enclosure/README.md "Where
// the pack stands"; the faucet's are the two halves of the stack `future.md`
// names in one sentence under "User-facing surfaces". A group's `holds` is
// directories, so a part added under one appears in it with no edit here — and
// single files only where one directory's contents belong to more than one
// assembly, which is `scenes/glb/` and nothing else. A directory no group claims
// comes back in `unseated` and the page names it.
//
// A PART IS A NAME, NOT A FILE. `endcap-circular-2hole` is a `.step` solid and
// the `.dxf` the laser reads, and it is one part with two representations —
// `seatParts` folds files sharing a stem in a directory into one card carrying
// both.
//
// Produced from web/lib/walk.js's file lists by way of /api/{steps,dxf,glbs};
// consumed by web/public/js/viewer/parts.js; pinned by web/tests/parts-tree.test.js.

// Scene GLBs stand under the assembly whose pieces they are a picture of.
// hardware/assembly/scenes/_scenes.py states each scene's `roots`, and the
// branch is which assembly those roots belong to.
const SCENES = "assembly/scenes/glb";

// `assembly/scenes/out/` is where render_scenes.py lays a scene down on its way
// to the GLB beside it. .gitignore holds it; a machine that has rendered scenes
// carries it and the repository does not.
export const EXCLUDED_DIRS = ["assembly/scenes/out"];

export const BRANCHES = [
  {
    id: "enclosure-assembly",
    label: "Enclosure assembly",
    model: "manifold-layout/enclosure-assembly.step",
    note: "The packed appliance — the refrigeration stratum, the flavor manifold standing " +
          "on it, and the printed box around them. It places the cold core as one solid; " +
          "the core's own pieces are the branch below.",
    groups: [
      { id: "box", label: "Enclosure", holds: ["printed-parts/enclosure"],
        note: "Four telescoping pieces, the faces let into them, and the ports through them." },
      { id: "manifold", label: "Flavor manifold", holds: ["manifold-layout"],
        note: "The valve-and-pump pack that sets down on the refrigeration stratum's crown." },
      { id: "flavor", label: "Flavor", holds: ["printed-parts/flavor"],
        note: "The case a peristaltic head runs in, and the tube it squeezes." },
      { id: "hopper", label: "Hopper", holds: ["printed-parts/zone-c"],
        note: "The funnel concentrate is poured into, and the mold it is cast in." },
      { id: "electronics", label: "Electronics", holds: ["printed-parts/electronics", "pcb"],
        note: "The controller carrier and the tray it stands on." },
      { id: "refrigeration", label: "Refrigeration", holds: ["printed-parts/refrigeration"],
        note: "The clamp holding the thermal fuse on the compressor's AC primary." },
      { id: "valve-seats", label: "Valve seats", holds: ["printed-parts/valve-seat"],
        note: "How a valve is held on a printed face." },
      { id: "scenes", label: "Bench scenes",
        holds: [`${SCENES}/back-top.glb`, `${SCENES}/front-top.glb`,
                `${SCENES}/back-half.glb`, `${SCENES}/hopper-drain.glb`],
        note: "One finished unit per picture, as it stands on the bench that builds it." },
    ],
  },
  {
    id: "cold-core",
    label: "Cold core",
    model: "cold-core-layout/cold-core-assembly.step",
    note: "The core as the bench sees it — the vessel that fills it, the coil wound on that, " +
          "both reservoirs in their pockets, every fitting made up, and the lines among them.",
    groups: [
      { id: "vessel", label: "Vessel",
        holds: ["cut-parts/carbonation", "printed-parts/cold-core/copper-plugs",
                "printed-parts/cold-core/prv-shroud"],
        note: "The carbonator: its cut end caps, the plugs in its ports, the relief shroud." },
      { id: "coil", label: "Evaporator coil", holds: ["printed-parts/cold-core/coil-mandrel"],
        note: "The mandrel the copper is wound on." },
      { id: "shell", label: "Foam shell",
        holds: ["printed-parts/cold-core/foam-shell", "printed-parts/cold-core/foam-cap",
                "printed-parts/cold-core/foam-assembly"],
        note: "The five printed pieces the pour goes into, and the outside faces the " +
              "enclosure loads." },
      { id: "reservoirs", label: "Reservoirs", holds: ["printed-parts/cold-core/reservoir"],
        note: "Two vented printed vessels, nested in the foam where they pre-chill." },
      { id: "sensing", label: "Level sensing", holds: ["printed-parts/cold-core/reed-bridge"],
        note: "The reed carrier that reads a float through a wall, and its setting gauge." },
      { id: "scenes", label: "Bench scenes",
        holds: [`${SCENES}/cold-core.glb`, `${SCENES}/cold-core-open.glb`,
                `${SCENES}/cap-lid.glb`, `${SCENES}/cap-lid-fill.glb`],
        note: "The core at the stages its own bench hands on." },
    ],
  },
  {
    id: "faucet",
    label: "Faucet",
    model: "faucet-layout/faucet-assembly.step",
    note: "The column the counter is clamped in: the printed stack around the harvested " +
          "Westbrass body, the display on the tip, and the three tubes running down past " +
          "the cut plate into the umbilical.",
    groups: [
      { id: "shell", label: "Shell", holds: ["printed-parts/faucet/touch-flo-shell"],
        note: "The dispense head, whole and in the three pieces it prints as." },
      { id: "mount", label: "Mount",
        holds: ["printed-parts/faucet/touch-flo-mounting-plate",
                "printed-parts/faucet/touch-flo-mounting-gasket",
                "printed-parts/faucet/touch-flo-tpu-o-ring", "cut-parts/faucet"],
        note: "Plate, gasket and o-ring above the counter; the cut plate below it." },
    ],
  },
];

// Purchased geometry, on its own shelf, ungrouped — each card carries its own
// directory. hardware/README.md: imported / harvested reference STEPs.
//
// The shelf takes a `model` the way a branch does, and the ASSE 1022 backflow
// chain is what stands in it: three purchased fittings made up into one body, so
// it is the shelf's own subject matter in one picture. It does not contain the
// rest of the shelf the way the three assemblies contain their branches.
export const REFERENCE = {
  id: "reference",
  label: "Reference",
  model: "reference/asse1022-assembly/asse1022-assembly.step",
  holds: ["reference", "off-the-shelf-parts"],
  note: "Purchased parts, modelled so the assemblies can place them. Nothing here is made " +
        "by this project.",
};

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
 * @returns {{branches: Object[], reference: Object, unseated: string[]}}
 *   `unseated` names every directory holding a file no group claims — a gap the
 *   page shows rather than swallows.
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

  const branches = BRANCHES.map((b) => {
    // The branch's own model is claimed before its groups, so the assembly
    // leads the branch rather than falling into the group that shares its
    // directory (`enclosure-assembly.step` sits beside `manifold-layout.step`).
    const hero = b.model ? claim([b.model])[0] || null : null;
    return { ...b, hero, groups: b.groups.map((g) => ({ ...g, parts: claim(g.holds) })) };
  });

  // Same order as a branch: the shelf's model is claimed first, so it heads the
  // shelf instead of standing again among the parts alphabetically below it.
  const referenceHero = REFERENCE.model ? claim([REFERENCE.model])[0] || null : null;
  const reference = { ...REFERENCE, hero: referenceHero, parts: claim(REFERENCE.holds) };

  const unseated = [...new Set(
    pool.filter((e) => !taken.has(e.file)).map((e) => dirOf(e.file)),
  )].sort();

  return { branches, reference, unseated };
}
