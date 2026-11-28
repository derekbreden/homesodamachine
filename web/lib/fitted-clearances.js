// Pair the surfaces named by a fit trial with the dimensions of the production parts.
import fs from "node:fs";
import path from "node:path";

const json = (root, file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const github = "https://github.com/derekbreden/homesodamachine/blob/";
const evidence = (label, file, revision = "main") => ({ label, href: github + revision + "/hardware/" + file });
const enclosure = "printed-parts/enclosure/enclosure";
const lidRegions = "printed-parts/cold-core/foam-cap/fore-snap-print-regions.json";
const wagoTrials = "print-tests/wago-pocket-support/prints/";

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
  const trials = json(hardwareDir, acceptance);
  const results = [];
  for (const [host, file] of [
    ["HSM-0079", enclosure + "/enclosure-front-top.print-features.json"],
    ["HSM-0081", enclosure + "/enclosure-back-top.print-features.json"],
    ["HSM-0020", lidRegions],
  ]) {
    const regions = json(hardwareDir, file).removable_support_stock.filter(region => region.shape === "pocket_floor_tree");
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
      const accepted = trials.accepted_pockets.find(pocket => pocket.connector === "221-" + sku
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
        const trial = json(hardwareDir, followUp).objects["fit-d-415"];
        const span = dims => dims.slice(0, 2).map(mm => mm.toFixed(2)).join(" × ");
        fit.note += ` The 27 Nov follow-up coupon was ${span(trial.cad_opening_short_long_depth_mm)} mm in CAD and ${span(trial.sliced_clear_xy_mm)} mm in the slice.`;
        fit.sources.push(evidence("Production-size trial", wagoTrials + "2026-11-27-front-mark1/physical-result.json", "8d658db2372283bf4328344265ebe6deb925d694"),
          evidence("Follow-up coupon", followUp, "8d658db2372283bf4328344265ebe6deb925d694"));
      }
      groups.set(key, fit);
    }
    results.push(...groups.values());
  }
  return results;
}

export function readFittedClearances(hardwareDir) {
  const { slip, sliding_extra, supported_surface } = json(hardwareDir, "../tools/hsm/shared-data/catalog/scalars.json").fits;
  return {
    allowance: { static: slip, sliding: slip + sliding_extra, supported: supported_surface },
    guidance: evidence("Clearance guidance", "printed-parts/enclosure/clearance-audit.md").href,
    records: wagoPockets(hardwareDir),
  };
}
