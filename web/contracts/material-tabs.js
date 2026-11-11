// Material tabs group relationship and resource records while retaining subsection links.
const tabs = new Set(["structure", "stock-cost", "location", "docs"]);
const sections = {
  bom: { tab: "structure", section: "bom" },
  used: { tab: "structure", section: "used" },
  stock: { tab: "stock-cost", section: "stock" },
  cost: { tab: "stock-cost", section: "cost" },
};

export function materialTab(value) {
  return Object.hasOwn(sections, value) ? sections[value] : { tab: tabs.has(value) ? value : null, section: null };
}

export function materialHash(id, { tab = null, panel = null, instance = null } = {}) {
  const query = new URLSearchParams();
  if (materialTab(tab).tab) query.set("tab", tab);
  if (panel === "materials") query.set("panel", panel);
  if (instance) query.set("instance", instance);
  return "material:" + encodeURIComponent(id) + (query.size ? "?" + query : "");
}
