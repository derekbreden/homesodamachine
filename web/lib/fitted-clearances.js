// Pair the surfaces named by a fit trial with the dimensions of the production parts.
import fs from "node:fs";
import path from "node:path";
import { componentLocation } from "../contracts/step-locations.js";

const json = (root, file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const github = "https://github.com/derekbreden/homesodamachine/blob/";
const evidence = (label, file, revision = "main") => ({ label, href: github + revision + "/hardware/" + file });
const enclosure = "printed-parts/enclosure/enclosure";
const lidRegions = "printed-parts/cold-core/foam-cap/fore-snap-print-regions.json";
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
      ["Blind stop", mouth > 0 ? x0 : x1, y, z],
    ],
  };
}

function wagoPockets(hardwareDir, { wago_trials: trials }) {
  const envelopes = json(hardwareDir, "reference/wago-221/replica-evidence.json").preserved_envelopes;
  const junctions = json(hardwareDir, "manifold-layout/junctions.json").junctions;
  const placements = new Map(junctions.map(junction => [junction.name, junction]));
  const materials = { "413": "HSM-0050", "415": "HSM-0053", "420": "HSM-0052" };
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
      const junction = placements.get(site.name);
      const sku = file === lidRegions ? "413" : junction?.size;
      if (!materials[sku]) continue;
      const [x0, x1, y0, y1, z0, z1] = region.bounds_source_mm;
      const [short, long, depth] = [y1 - y0, z1 - z0, x1 - x0].map(mm => Number(mm.toFixed(3)));
      const [width, bodyDepth, height] = envelopes[sku];
      // The lid wells grip the centered rear half. The enclosure banks retain their wiring placements.
      const zCenter = junction?.translation_mm[2] ?? (z0 + z1) / 2;
      const lower = zCenter - width / 2 - z0, upper = z1 - zCenter - width / 2;
      const [floor, roof] = region.print_up_source[2] > 0 ? [lower, upper] : [upper, lower];
      const stopX = region.mouth_direction_source[0] > 0 ? x0 : x1;
      const stop = (junction ? Math.abs(stopX - junction.translation_mm[0]) : depth) - bodyDepth / 2;
      const key = [sku, short, long, depth, floor.toFixed(3), roof.toFixed(3), stop.toFixed(3)].join("/");
      if (groups.has(key)) { groups.get(key).hostSites.push(site); continue; }
      const coupon = trials?.accepted[sku];
      const stacked = sku === "420";
      const shortFaces = stacked ? "Opposed closed levers" : "Base and closed lever";
      const fit = {
        host, mate: materials[sku], title: "WAGO 221-" + sku + " pocket", hostSites: [site],
        hostSurface: "Pocket walls and blind stop", mateSurface: "Connector faces",
        mateSites: [{ view: [32, 24], faces: [
          ["Housing side", -width / 2, -3, height / 2], ["Housing side", width / 2, -3, height / 2],
          [stacked ? "Closed lever" : "Base", stacked ? -2.2 : 0, -2, 0], ["Closed lever", 2.2, -2, height],
          ["Back of housing", 0, -bodyDepth / 2, height / 2],
        ] }],
        motion: "static",
        dimensions: [
          { label: "Between cheeks", reference: shortFaces, nominal: height, chosen: short },
          { label: "Floor to roof", reference: "Across housing sides", nominal: width, chosen: long, supported: 1 },
        ],
        faceGaps: [
          { label: "At each cheek", chosen: (short - height) / 2, faces: 1 },
          { label: "At printed floor", chosen: floor, faces: 1, places: 3 },
          { label: "At supported roof", chosen: roof, faces: 1, supported: 1, places: 3 },
          { label: "At blind stop", chosen: stop, faces: 1 },
        ],
        support: "the supported pocket roof", note: `Insertion depth ${depth.toFixed(2)} mm.`,
        sources: [evidence("Production pocket", file)],
      };
      if (coupon?.cad_mm.every((mm, i) => mm === [short, long, depth][i])) {
        const [x, y] = coupon.sliced_mm;
        fit.note += ` The accepted Mark2 coupon has a sliced opening of ${x.toFixed(2)} × ${y.toFixed(2)} mm.`;
        fit.sources.push(evidence(...trials.record));
      } else if (sku === "415" && trials?.five_way) {
        const trial = trials.five_way;
        const span = dims => dims.slice(0, 2).map(mm => mm.toFixed(2)).join(" × ");
        fit.note += ` The 27 Nov production-size trial felt slightly loose in both directions. The follow-up coupon was ${span(trial.cad_mm)} mm in CAD and ${span(trial.sliced_mm)} mm in the slice.`;
        fit.sources.push(evidence(...trial.production_trial), evidence(...trial.follow_up));
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

// Mark only the outside skin touching the bore, over the length of the printed part.
function tubeWall(body, x, y, radius, bottom, top) {
  return {
    file: componentLocation(faucet, body), view: [18, 10],
    band: { label: "Tube outer wall", lo: [x + radius - 0.18, y - radius, bottom], hi: [x + radius + 0.04, y + radius, top] },
  };
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
      return { label, ...tubeWall(body, x, y, diameter / 2, -98, -88) };
    }),
    dimensions: [{ label: "Bore diameter", reference: "Tube OD", nominal: diameter, chosen }],
    note, sources: [evidence("Bore fit trials", file), evidence("Production bores", "printed-parts/faucet/umbilical-organizer/numbers.rs")],
  }));
}

function tubeCollars(hardwareDir, { collar_bores: sizes }) {
  if (!sizes) return [];
  const source = "printed-parts/faucet/tube-collar/";
  return [
    ["HSM-0099", "HSM-0575", "Soda", "quarter", ["soda_umbilical_tube", 0, 0]],
    ["HSM-0100", "HSM-0107", "Flavor A", "small", ["flavor_umbilical_tube_pos_x", 15.313, 13.652]],
    ["HSM-0101", "HSM-0107", "Flavor B", "small", ["flavor_umbilical_tube_neg_x", -15.313, 13.652]],
    ["HSM-0102", "HSM-0108", "Drain", "small", ["drain_tube", 0, -34.7]],
    ["HSM-0272", "HSM-0311", "Tap water", "quarter"],
    ["HSM-0273", "HSM-0312", "CO₂", "quarter"],
  ].map(([host, mate, name, size, tail]) => {
    const { nominal, chosen, tolerance } = sizes[size];
    return {
      host, mate, title: name + " identification collar", motion: "sliding",
      hostSurface: "Collar bore walls", mateSurface: "Tube outer wall",
      hostSites: [{ view: [72, 8], faces: [["Bore wall", chosen / 2, 15, 0], ["Opposing wall", -chosen / 2, 15, 0]] }],
      mateSites: tail ? [tubeWall(...tail, nominal / 2, -345, -315)] : [],
      tubeSection: !tail,
      dimensions: [{ label: "Bore across side walls", reference: "Tube OD", nominal, chosen, places: size === "small" ? 4 : 2 }],
      note: `The bore allows ${tolerance} mm for the tube’s upper diameter tolerance, 0.10 mm for crown sag and 0.10 mm for slip. The sag measurement came from a PETG collar. The slight bend in the tube holds the collar in place.`,
      sources: [evidence(...sizes.source), evidence("Print calibration", source + "README.md"), evidence("Hand-fit record", "ledger/fitted.json")],
    };
  });
}

function magnetPocket(hardwareDir) {
  const folder = "printed-parts/cold-core/magnetic-float/all-aero/";
  const { dimensions_mm: d, magnet } = json(hardwareDir, folder + "design.json");
  const cutaway = folder + "section.step";
  const ringTop = d.magnet_seat + magnet.thickness_mm;
  return [{
    host: "HSM-0033", mate: "HSM-0034", title: "Float magnet pocket", motion: "static",
    hostSurface: "Pocket walls and roof in section", mateSurface: "Ring magnet rim, bore and top",
    hostSites: [{ file: componentLocation(cutaway, "float-aero"), view: [92, 12], faces: [
      ["Pocket outer wall", 0, -d.pocket_od / 2, d.magnet_midplane],
      ["Center boss", 0, -d.pocket_id / 2, d.magnet_midplane], ["Pocket roof", 0, -7, d.pocket_roof],
    ] }],
    mateSites: [{ file: componentLocation(folder + "assembly.step", "RC62"), view: [32, 30], faces: [
      ["Magnet rim", magnet.od_mm / 2, 0, d.magnet_midplane], ["Magnet bore", -magnet.id_mm / 2, 0, d.magnet_midplane],
      ["Magnet top", 0, -7, ringTop],
    ] }],
    dimensions: [
      { label: "Pocket diameter", reference: "Magnet OD", nominal: magnet.od_mm, chosen: d.pocket_od },
      { label: "Center boss diameter", reference: "Magnet ID", nominal: magnet.id_mm, chosen: d.pocket_id, places: 3, external: true },
      { label: "Gap above seated magnet", chosen: d.pocket_roof - ringTop, places: 3, faces: 1, supported: 1 },
    ],
    support: "the pocket roof over the ring",
    note: "The RC62 seated during the print pause. The first layer over it was tight, so the current ASA Aero pocket adds 0.20 mm above the ring. The print observation applies to the earlier roof.",
    sources: [evidence("Pocket dimensions", folder + "design.json"), evidence("Paused-print observation", folder + "physical-observations.json")],
  }];
}

function fillTubeSnap(hardwareDir) {
  const file = enclosure + "/enclosure-back-top.print-features.json";
  const seat = json(hardwareDir, file).removable_support_stock.find(region => region.shape === "tube_wing_strips");
  if (!seat) return [];
  const [x, y, z] = seat.centre_source_mm, r = seat.bore_radius_mm;
  const diameter = json(hardwareDir, "manifold-layout/reservoir-a-routes.json").tube_od_mm;
  const lift = seat.upper_wing_lift_mm;
  return [{
    host: "HSM-0081", mate: "HSM-0307", title: "Reservoir fill tube in east-wall clip", motion: "static",
    hostSurface: "Fixed and spring jaws", mateSurface: "Fill tube outer wall",
    hostSites: [{ view: [170, -4], faces: [["Fixed jaw", x, y, z + r], ["Relieved jaw", x, y, z - r - lift]] }],
    mateSites: [{ file: componentLocation("manifold-layout/enclosure-assembly.step", "tube-fluid-14"), view: [170, -12],
      band: { label: "Tube at the jaw", lo: [x - r - 0.1, seat.span_y_mm[0], z - diameter / 2 - 0.04],
        hi: [x + r + 0.1, seat.span_y_mm[1], z - diameter / 2 + 0.18] } }],
    dimensions: [
      { label: "Span between jaws", reference: "Tube OD", nominal: diameter, chosen: 2 * r + lift, supported: 1 },
      { label: "Gap at fixed jaw", chosen: r - diameter / 2, faces: 1 },
      { label: "Gap at spring jaw", chosen: r + lift - diameter / 2, faces: 1, supported: 1 },
    ], support: "the supported spring jaw",
    note: "The east-wall clip holds the tube stationary after insertion. Its free jaw is offset from the fixed half of the bore. Derek accepted the tube fit in the printed back-top crop.",
    sources: [evidence("Production clip", file), evidence("Hand-fit trial", "print-tests/tube-snap-corbel/prints/2026-11-20-mark1-upper-wing-support/physical-result/physical-result.json", "f15bb9b4dbab8cd2046ea8e1e8e08d13539381d2")],
  }];
}

// These four tube bends bear on upright walls. Their points are picks in the installed assembly.
function curvedTubeSeats(hardwareDir, { tube_seats: seats = [] }) {
  const diameter = json(hardwareDir, "manifold-layout/reservoir-a-routes.json").tube_od_mm;
  return seats.map(({ title, host, mate, span_mm, note, source, trial }) => {
    const site = ([, body, inner, outer], label) => [{
      file: componentLocation("manifold-layout/enclosure-assembly.step", body), view: [125, 35],
      faces: [["Inside of bend · " + label, ...inner], ["Outside of bend · " + label, ...outer]],
    }];
    return {
      host: host[0], mate: mate[0], title, motion: "static", hostSurface: "Seated jaw faces", mateSurface: "Tube outer wall",
      hostSites: site(host, "jaw"), mateSites: site(mate, "tube"),
      dimensions: [{ label: "Span between seated jaws", reference: "Tube OD", nominal: diameter, chosen: span_mm }], note,
      sources: [evidence("Production jaws", source), evidence(...trial)],
    };
  });
}

// Installed points isolate the two bodies even where the seated surfaces coincide.
function fittedSections(hardwareDir, { sections = [] }) {
  return sections.map(({ title, dimension, assembly = "manifold-layout/enclosure-assembly.step", host, mate, axis, motion, supported, support, note, sources }) => {
    const site = ([, body, label, point, view]) => [{ file: componentLocation(assembly, body), faces: [[label, ...point]], view }];
    const coordinate = "XYZ".indexOf(axis[1]);
    const gap = (mate[3][coordinate] - host[3][coordinate]) * (axis[0] === "-" ? -1 : 1);
    return {
      host: host[0], mate: mate[0], title, hostSurface: host[2], mateSurface: mate[2], hostSites: site(host), mateSites: site(mate),
      motion, dimensions: [{ label: dimension, chosen: gap, faces: 1, supported }], support, note,
      sources: sources.map(source => evidence(...source)),
    };
  });
}

export function readFittedClearances(hardwareDir, materials) {
  const { slip, sliding_extra, supported_surface } = json(hardwareDir, "../tools/hsm/shared-data/catalog/scalars.json").fits;
  const measurements = optionalJson(hardwareDir, "ledger/fitted-clearances.json") || {};
  const ids = new Set(materials.map(material => material.id));
  // Trial folders may have been archived, or an older checkout may predate a family of parts.
  const records = [wagoPockets, portPlates, organizerBores, tubeCollars, fillTubeSnap, curvedTubeSeats, magnetPocket, fittedSections].flatMap(read => {
    try { return read(hardwareDir, measurements); }
    catch (error) { if (error.code !== "ENOENT") throw error; return []; }
  }).filter(fit => ids.has(fit.host) && ids.has(fit.mate));
  return {
    allowance: { static: slip, sliding: slip + sliding_extra, supported: supported_surface },
    guidance: evidence("Clearance guidance", "printed-parts/enclosure/clearance-audit.md").href,
    records,
  };
}
