// The parts tree — what /3d is a browse of.
//
// THE PAGE IS THE MACHINE'S TWO UNITS, one thumbnail each:
//
//   Enclosure assembly       manifold-layout/enclosure-assembly.step
//   Faucet and umbilical     faucet-layout/faucet-assembly.step
//
// Those two are what ship as separate bodies. Everything else the machine is
// made of stands inside one of them, and is reached by opening it.
//
// AN ASSEMBLY MAY HOLD AN ASSEMBLY. `children` is that nesting: the cold core is
// one component of the enclosure, and opening that component is how its carbonator,
// coil, reservoirs, fittings and lines are reached. The nesting is what the page
// browses and what the drill-down walks, and the two agree because both read
// this file.
//
// A PART INSIDE AN ASSEMBLY IS REACHED BY SELECTING IT THERE. Open the assembly,
// arm Select → Component, click the solid: the panel names the component and
// offers the file it was modelled in, which loads into the same modal with the
// trail back (contracts/component-sources.js, viewer/component-picker.js,
// viewer/step-nav.js). That drill recurses — an assembly reached this way offers
// its own components the same way — so depth is a property of the model, not a
// limit of the page. The page itself lists no part and no purchased geometry.
//
// EVERY FILE THE WALKERS OFFER IS CLAIMED. An assembly's `holds` names the
// directories it places from, `PURCHASED` takes the bought bodies, and `TOOLING`
// takes what makes the machine without being part of it. A directory in
// none of them comes back in `unseated`, which the page names. Nothing below the
// two cards is drawn, so what those three lists produce is read by the gate and
// by nothing else.
//
// A PART IS A NAME, NOT A FILE. `endcap-circular-2hole` is a `.step` solid and the
// `.dxf` the laser reads, and it is one part with two representations, so
// `seatParts` folds files sharing a stem in a directory into one. That fold is
// what lets the claim be stated as parts — the vocabulary the gate reads in, and
// the two roots' own models.
//
// Produced from web/lib/walk.js's file lists by way of /api/{steps,dxf,glbs};
// consumed by web/public/js/viewer/parts.js; pinned by web/tests/parts-tree.test.js.
//
// EVERY PICTURE THIS REPOSITORY DRAWS COMES THROUGH THE PAGE THIS BUILDS. The
// render family in tools/render/ — render-step.js, render-step-posed.js (which
// hardware/assembly/scenes/render_scenes.py drives), render-dxf.js,
// render-view.js, render-step-side-by-side.js, screenshot-site.js — each stands
// the server and opens `/3d`, and `main.js`
// runs `applyInitialRoute` only after `buildGrid`. So a throw in `seatParts` or
// in `parts.js` never reaches a browser a person is looking at: it reaches a CAD
// build, as a mount that never happens and a two-minute timeout on a scene.

// WHERE A BUILD PUTS ITS WORKINGS. `assembly/scenes/out/` is where
// render_scenes.py lays a scene down on its way to the GLB beside it, and
// `quickstart/out/` is where the mount studies land. .gitignore holds both; a
// machine that has run either carries it and the repository does not.
export const EXCLUDED_DIRS = ["assembly/scenes/out", "quickstart/out"];

export const ASSEMBLIES = [
  {
    id: "enclosure-assembly",
    label: "Enclosure assembly",
    model: "manifold-layout/enclosure-assembly.step",
    note: "The whole appliance — the refrigeration stratum, the cold core standing on it, the " +
          "flavor manifold over that, and the printed box around them all.",
    // The directories the enclosure alone places from.
    holds: [
      "manifold-layout",
      "pcb",
      "printed-parts/electronics",
      "printed-parts/enclosure",
      "printed-parts/refrigeration",
      "printed-parts/valve-seat",
      "printed-parts/zone-c",
    ],
    children: [
      {
        id: "cold-core-assembly",
        label: "Cold core assembly",
        model: "cold-core-layout/cold-core-assembly.step",
        note: "One component of the enclosure, and a stack in its own right: the carbonator that " +
              "fills it, the coil wound on that, both reservoirs in their pockets, every " +
              "fitting made up, and the lines among them. The machine places its foam; this " +
              "is the same body one frame in.",
        holds: [
          "cold-core-layout",
          "cut-parts/carbonation",
          "printed-parts/cold-core",
        ],
      },
    ],
  },
  {
    id: "faucet-assembly",
    label: "Faucet and umbilical",
    model: "faucet-layout/faucet-assembly.step",
    note: "The one unit that leaves the box: the column the counter is clamped in — the " +
          "printed stack around the harvested Westbrass body and the display on its tip — and " +
          "the three tubes running down past the cut plate into the braided umbilical.",
    holds: [
      "cut-parts/faucet",
      "faucet-layout",
      "printed-parts/faucet",
    ],
  },
];

// WHAT THIS PROJECT DOES NOT FABRICATE — the harvested and purchased bodies
// hardware/README.md describes, standing under whichever unit needs one and
// under both where both do: the Waveshare display is on the faucet's tip and
// behind the enclosure's cover. Naming an owner would pick one of the two, so
// this list owns them instead, and a part here is reached by selecting its solid
// in whichever assembly stands it up.
export const PURCHASED = [
  "off-the-shelf-parts",
  "reference",
];

// MADE IN ORDER TO MAKE THE MACHINE, OR A PICTURE OF IT — never part of it. The
// moulds, mandrels and gauges a bench works from; the soft parts modelled beside
// their host without a seat in it; and the bench scenes, each a picture of a group
// of bodies rather than a body. Claimed ahead of the sweep, so a tooling directory
// standing inside a part directory comes out of it.
export const TOOLING = [
  "assembly/scenes/glb",
  "printed-parts/cold-core/coil-mandrel",
  "printed-parts/zone-c/funnel-mold",
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

// Directory, then name. Nothing renders a seated part, so this is here to make
// the claim the same on every machine and legible where the gate prints it.
function partOrder(a, b) {
  return a.dir.localeCompare(b.dir) || a.name.localeCompare(b.name);
}

// Fold a flat list of `{file, type}` into parts: one per stem per directory,
// carrying every representation that stem has. `primary` is the richest of them,
// and on an assembly's own model it is what the card opens and draws.
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

// Every assembly of the tree, flattened, outermost first. What keeps a nested
// assembly's own model out of its parent's sweep is the PHASE it is claimed in —
// `seatParts` takes every model before any `holds` — and not this order; each
// claim here names one exact file, so nothing in the walk can collide.
export function walkAssemblies(nodes = ASSEMBLIES) {
  return nodes.flatMap((a) => [a, ...walkAssemblies(a.children || [])]);
}

/**
 * Seat every file the walkers offer into the tree.
 *
 * @param {{steps: string[], dxfs: string[], glbs: string[]}} files root-relative paths
 * @returns {{assemblies: Object[], purchased: Object[], tooling: Object[], unseated: string[]}}
 *   `assemblies` is the nesting `ASSEMBLIES` states, each node carrying the
 *   `model` part the page draws, the `inside` its own `holds` claimed, and its
 *   `children` seated the same way. `purchased` and `tooling` are what no one
 *   assembly owns. None of the three is drawn — the page is the two roots.
 *   `unseated` names every directory holding a file nothing claims, which the
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

  // Order is the whole of the seating. Every model first, innermost included, so
  // an assembly's own file is its card and not a part of the directory it shares
  // with its parent; then the tooling, which stands inside directories an
  // assembly otherwise sweeps whole; then each assembly's own sweep, innermost
  // first; and last the bought geometry, which is what is left.
  const models = new Map();
  for (const a of walkAssemblies()) models.set(a.id, claim([a.model])[0] || null);
  const tooling = claim(TOOLING);

  // A CHILD SWEEPS BEFORE ITS PARENT, so a parent holding a directory a child
  // holds a corner of leaves that corner to the child rather than swallowing it.
  const seat = (nodes) => nodes.map((a) => {
    const children = seat(a.children || []);
    return { ...a, model: models.get(a.id), inside: claim(a.holds || []), children };
  });
  const assemblies = seat(ASSEMBLIES);
  const purchased = claim(PURCHASED);

  const unseated = [...new Set(
    pool.filter((e) => !taken.has(e.file)).map((e) => dirOf(e.file)),
  )].sort();

  return { assemblies, purchased, tooling, unseated };
}
