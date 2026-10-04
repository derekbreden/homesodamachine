// Display names mirror hardware/scripts/_bom_categories.py.
export const CATEGORY_NAMES = {
  sensors: "Sensors",
  wiring: "Wires & wire connectors",
  plumbing: "Tubes, connectors, adapters & safety",
  "solenoid-valves": "Solenoid valves",
  pumps: "Pumps",
  electronics: "Electronics",
  printed: "FDM printed parts",
  "cut-parts": "SendCutSend cut parts",
  pipes: "Pipes",
  refrigeration: "Refrigeration",
  "water-filter": "Water filter",
  insulation: "Insulation & foam",
  faucet: "Faucet",
  fasteners: "Fasteners",
  consumables: "Fab consumables",
  "funnel-casting": "Funnel casting",
  "ac-mains": "AC-mains hardware",
  carbonation: "Carbonation (sparge stone)",
  "cable-mgmt": "Cable management",
  "vent-filter": "Vent filter",
  welding: "Welding filler",
  "cold-kit": "Cold kit",
  supplies: "Other supplies",
};

export function categoryName(tag) {
  return CATEGORY_NAMES[tag] || tag.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}
