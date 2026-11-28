// Pair the surfaces named by a fit trial with the dimensions of the production parts.
import fs from "node:fs";
import path from "node:path";
import { componentLocation } from "../contracts/step-locations.js";

const json = (root, file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const github = "https://github.com/derekbreden/homesodamachine/blob/";
const evidence = (label, file, revision = "main") => ({ label, href: github + revision + "/hardware/" + file });
const enclosure = "printed-parts/enclosure/enclosure";
const lidRegions = "printed-parts/cold-core/foam-cap/fore-snap-print-regions.json";
const wagoTrials = "print-tests/wago-pocket-support/prints/";
const faucet = "faucet-layout/faucet-assembly.step";

function optionalJson(root, file) {
  try { return json(root, file); }
  catch (error) { if (error.code !== "ENOENT") throw error; return null; }
}

// Each site is expressed in the standalone model's own frame, which the viewer's face picker reads.
function pocketSite(region) {
  const [x0, x1, y0, y1, z0, z1] = region.bounds_source_mm;
  const [x, y, z] = [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2];
  const mouth = region.mouth_direction_source[0];
  const floorDown = region.print_up_source[2] > 0;
  const name = region.name.split(" ")[0];
  return {
    name, label: name.replace(/^(wago-|wiring-junction-)/, "").replaceAll("-", " ").toUpperCase(),
    view: [mouth > 0 ? 12 : 168, 6],
    faces: [
      ["Cheek", x, y0, z], ["Cheek", x, y1, z],
      ["Floor", x, y, floorDown ? z0 : z1], ["Roof", x, y, floorDown ? z1 : z0],
    ],
  };
}

function wagoPockets(hardwareDir) {
  const envelopes = json(hardwareDir, "reference/wago-221/replica-evidence.json").preserved_envelopes;
  const junctions = json(hardwareDir, "manifold-layout/junctions.json").junctions;
  const sizes = new Map(junctions.map(junction => [junction.name, junction.size]));
  const materials = { "413": "HSM-0050", "415": "HSM-0053", "420": "HSM-0052" };
  const acceptance = wagoTrials + "2026-11-27-fit-c-mark2/physical-result.json";
  const trials = optionalJson(hardwareDir, acceptance);
  const results = [];
  for (const [host, file] of [
    ["HSM-0079", enclosure + "/enclosure-front-top.print-features.json"],
    ["HSM-0081", enclosure + "/enclosure-back-top.print-features.json"],
    ["HSM-0020", lidRegions],
  ]) {
    const regions = (optionalJson(hardwareDir, file)?.removable_support_stock || []).filter(region => region.shape === "pocket_floor_tree");
    const groups = new Map();
    for (const region of regions) {
      const site = pocketSite(region);
      const sku = file === lidRegions ? "413" : sizes.get(site.name);
      if (!materials[sku]) continue;
      const [x0, x1, y0, y1, z0, z1] = region.bounds_source_mm;
      const [short, long, depth] = [y1 - y0, z1 - z0, x1 - x0].map(mm => Number(mm.toFixed(3)));
      const key = [sku, short, long, depth].join("/");
      if (groups.has(key)) { groups.get(key).hostSites.push(site); continue; }
      const [width, , height] = envelopes[sku];
      const accepted = trials?.accepted_pockets.find(pocket => pocket.connector === "221-" + sku
        && pocket.nominal_short_long_depth_mm.every((mm, i) => mm === [short, long, depth][i]));
      const stacked = sku === "420";
      const shortFaces = stacked ? "Opposed closed levers" : "Base and closed lever";
      const fit = {
        host, mate: materials[sku], title: "WAGO 221-" + sku + " pocket", hostSites: [site],
        hostSurface: "Pocket cheeks, floor and roof", mateSurface: "Connector faces",
        mateSites: [{ view: [32, 24], faces: [
          ["Housing side", -width / 2, -3, height / 2], ["Housing side", width / 2, -3, height / 2],
          [stacked ? "Closed lever" : "Base", stacked ? -2.2 : 0, -2, 0], ["Closed lever", 2.2, -2, height],
        ] }],
        motion: "static",
        dimensions: [
          { label: "Between cheeks", reference: shortFaces, nominal: height, chosen: short },
          { label: "Floor to roof", reference: "Across housing sides", nominal: width, chosen: long, supported: 1 },
        ],
        support: "the supported pocket roof", note: `Insertion depth ${depth.toFixed(2)} mm.`,
        sources: [evidence("Production pocket", file)],
      };
      if (accepted) {
        const [x, y] = accepted.sliced_clear_short_long_mm;
        fit.note += ` The accepted Mark2 coupon has a sliced opening of ${x.toFixed(2)} × ${y.toFixed(2)} mm.`;
        fit.sources.push(evidence("Coupon fit", acceptance, "8d658db2372283bf4328344265ebe6deb925d694"));
      } else if (sku === "415") {
        const followUp = wagoTrials + "2026-11-27-fit-d-mark2/fit-toolpaths.json";
        const trial = optionalJson(hardwareDir, followUp)?.objects["fit-d-415"];
        const span = dims => dims.slice(0, 2).map(mm => mm.toFixed(2)).join(" × ");
        if (trial) fit.note += ` The 27 Nov follow-up coupon was ${span(trial.cad_opening_short_long_depth_mm)} mm in CAD and ${span(trial.sliced_clear_xy_mm)} mm in the slice.`;
        fit.sources.push(evidence("Production-size trial", wagoTrials + "2026-11-27-front-mark1/physical-result.json", "8d658db2372283bf4328344265ebe6deb925d694"),
          evidence("Follow-up coupon", followUp, "8d658db2372283bf4328344265ebe6deb925d694"));
      }
      groups.set(key, fit);
    }
    results.push(...groups.values());
  }
  return results;
}

// The chip width includes the bench-selected trim. The rail faces give the full available span.
function portPlates(hardwareDir) {
  const folder = "printed-parts/enclosure/rear-identification/";
  const plateFile = folder + "rear-identification.numbers.json";
  const { width, side_clearance, thick } = json(hardwareDir, plateFile);
  const { fluid_grid } = json(hardwareDir, "manifold-layout/above-core.json");
  const plates = { "bulkhead-water": "HSM-0062", "bulkhead-carb": "HSM-0063", "bulkhead-flavor-a": "HSM-0064",
    "bulkhead-flavor-b": "HSM-0065", "co2-inlet": "HSM-0066", "bulkhead-drain": "HSM-0067" };
  // Opposing X faces of each back-top channel, picked at Y470.4 in the installed rail roots.
  const channels = [[7.65, 49.95], [55.35, 97.65]];
  return fluid_grid.assignment.flatMap((row, r) => row.map((port, c) => {
    const [left, right] = channels[c], z = fluid_grid.rows_z_mm[r];
    return {
      host: plates[port], mate: "HSM-0081", title: "Identification plate in rear rails",
      hostSurface: "Plate edges", mateSurface: "Retaining channel faces",
      hostSites: [{ view: [25, 15], faces: [["Left edge", -width / 2, thick / 2, 0], ["Right edge", width / 2, thick / 2, 0]] }],
      mateSites: [{ view: [75, 28], faces: [["Left rail", left, 470.4, z], ["Right rail", right, 470.4, z]] }],
      motion: "sliding", dimensions: [
        { label: "Plate width", reference: "Between rails", nominal: right - left, chosen: width, external: true },
        { label: "Gap per edge, centered", chosen: (right - left - width) / 2, faces: 1 },
      ],
      note: `The CO₂ trials set the trim at ${side_clearance.toFixed(2)} mm off each edge of the blank. All six plates use it.`,
      sources: [evidence("Plate dimensions", plateFile),
        evidence("CO₂ width trial", folder + "prints/2026-11-09-co2-width-mark1/physical-result.json", "eca139d1b8d5b45c1e6e73a818144b5683fae003")],
    };
  }));
}

// The organizer's two tested bores and the pair that inherits the drain bore on black flavor stock.
function organizerBores(hardwareDir) {
  const file = "printed-parts/faucet/umbilical-organizer/physical-acceptance.json";
  const { geometry } = json(hardwareDir, file);
  const axes = geometry.faucet_axes_xy_mm;
  const [fx, fy] = axes.F1;
  const centerY = (fx * fx + fy * fy) / (2 * fy);
  const beverage = geometry.quarter_inch_bore_diameter_mm, drain = geometry.drain_bore_diameter_mm;
  return [
    ["HSM-0575", "Soda tube bore", [["S", "soda_umbilical_tube"]], 6.35, beverage, "Derek chose sample A for the blue quarter-inch tube."],
    ["HSM-0108", "Drain tube bore", [["D", "drain_tube"]], 4, drain, "Derek chose sample B for the white 4 mm drain tube."],
    ["HSM-0107", "Flavor tube bores", [["F1", "flavor_tube_pos_x"], ["F2", "flavor_tube_neg_x"]], 4, drain,
      "Both bores use the size selected on the white drain tube. The black flavor stock still awaits its own sliding-fit trial."],
  ].map(([mate, title, passages, diameter, chosen, note]) => ({
    host: "HSM-0098", mate, title, motion: "sliding", hostSurface: "Organizer bore wall", mateSurface: "Tube outer wall",
    hostSites: passages.map(([label]) => {
      const [x, y] = axes[label];
      return { label, view: [130, 67], faces: [["Bore wall", x + chosen / 2, y - centerY, geometry.length_mm / 2]] };
    }),
    mateSites: passages.map(([label, body]) => {
      const [x, y] = axes[label];
      return { label, file: componentLocation(faucet, body), view: [20, 12],
        band: { label: "Tube at organizer", lo: [x - diameter, y - diameter, -98], hi: [x + diameter, y + diameter, -88] } };
    }),
    dimensions: [{ label: "Bore diameter", reference: "Tube OD", nominal: diameter, chosen }],
    note, sources: [evidence("Bore fit trials", file), evidence("Production bores", "printed-parts/faucet/umbilical-organizer/numbers.rs")],
  }));
}

// Installed points isolate the two bodies even where the seated surfaces coincide.
function fittedSections(hardwareDir) {
  const { sections } = json(hardwareDir, "ledger/fitted-clearance-surfaces.json");
  return sections.map(({ title, dimension, assembly = "manifold-layout/enclosure-assembly.step", host, mate, axis, motion, note, sources }) => {
    const site = ([, body, label, point, view]) => [{ file: componentLocation(assembly, body), faces: [[label, ...point]], view }];
    const coordinate = "XYZ".indexOf(axis[1]);
    const gap = (mate[3][coordinate] - host[3][coordinate]) * (axis[0] === "-" ? -1 : 1);
    return {
      host: host[0], mate: mate[0], title, hostSurface: host[2], mateSurface: mate[2], hostSites: site(host), mateSites: site(mate),
      motion, dimensions: [{ label: dimension, chosen: gap, faces: 1 }], note,
      sources: sources.map(source => evidence(...source)),
    };
  });
}

export function readFittedClearances(hardwareDir, materials) {
  const { slip, sliding_extra, supported_surface } = json(hardwareDir, "../tools/hsm/shared-data/catalog/scalars.json").fits;
  const ids = new Set(materials.map(material => material.id));
  // Trial folders may have been archived, or an older checkout may predate a family of parts.
  const records = [wagoPockets, portPlates, organizerBores, fittedSections].flatMap(read => {
    try { return read(hardwareDir); }
    catch (error) { if (error.code !== "ENOENT") throw error; return []; }
  }).filter(fit => ids.has(fit.host) && ids.has(fit.mate));
  return {
    allowance: { static: slip, sliding: slip + sliding_extra, supported: supported_surface },
    guidance: evidence("Clearance guidance", "printed-parts/enclosure/clearance-audit.md").href,
    records,
  };
}
