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
