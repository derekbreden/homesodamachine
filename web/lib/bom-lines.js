// BOM lines expose the authored physical quantities and prices to manufacturing and costing.
import fs from "node:fs";
import path from "node:path";

const PARTS_RE = /<!--parts\s+([\s\S]*?)-->/;
const TARGET_RE = /HSM-\d{4,}(?::\d+(?:\.\d+)?)?/g;
const CATEGORY_RE = /<!--@([a-z][a-z-]*)-->/;
const MONEY_RE = /\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)/;
const COMMENT_RE = /<!--[\s\S]*?-->/g;

// Every cell the ledgers hold is prose off a markdown table, and their numbers
// are docgen markers — `[value](NAME)`. Strip the marker syntax back to the
// value, and the emphasis around it, so a cell reads as prose.
export function plainMarkdown(text) {
  return String(text)
    .replace(COMMENT_RE, "")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/\*\*([^*]*)\*\*/g, "$1")
    .replace(/~~([^~]*)~~/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

// Drop purchase pack sizes from display names; retain ASINs, part numbers and dimensions.
export function stripPack(name) {
  return name
    .replace(
      /\s*\([^()]*\b(?:pk|pack|pcs?|ct|sets?|pieces?|count|bag)\b[^()]*\)/gi,
      "",
    )
    .replace(/,\s*\d+\s*(?:pc|pcs|pk|pack)\b/gi, "")
    .replace(/\s{2,}/g, " ")
    .replace(/\s*,\s*$/g, "")
    .trim();
}

export const cellsOf = (row) =>
  row
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
export const isSeparator = (cells) =>
  cells.every((cell) => /^[-:\s]*$/.test(cell));
const parseMoney = (cell) => {
  const match = String(cell).replace(COMMENT_RE, "").match(MONEY_RE);
  return match ? parseFloat(match[1].replace(/,/g, "")) : 0;
};

export function parseTargets(text) {
  const tag = String(text).match(PARTS_RE);
  if (!tag) return null;
  return [...tag[1].matchAll(TARGET_RE)].map(([token]) => {
    const [id, weight] = token.split(":");
    return { id, weight: weight == null ? null : Number(weight) };
  });
}

// Quantity cells expose a discrete piece count when they are not measures or fractions.
function parseCount(cell) {
  const text = plainMarkdown(cell);
  if (
    /[/]|\b(ft|kg|g|m|in|inches|oz|roll|pair|set|sets|collars?|columns?)\b/i.test(
      text,
    )
  )
    return null;
  const match = text.match(/^~?\s*(\d+)\b/);
  return match ? parseInt(match[1], 10) : null;
}

// A quantity cell → { value, unit } when it is a length or a mass per build.
function parseMeasure(cell) {
  const match = plainMarkdown(cell).match(
    /^~?\s*([0-9]+(?:\.[0-9]+)?)\s*(ft|m|mm|in|inches|g|kg)\b/i,
  );
  if (!match) return null;
  const unit =
    match[2].toLowerCase() === "inches" ? "in" : match[2].toLowerCase();
  return { value: Number(match[1]), unit };
}

export function readBomLines(hardwareDir) {
  const text = fs.readFileSync(
    path.join(hardwareDir, "ledger", "bom.md"),
    "utf-8",
  );
  const lines = [];
  let section = null;
  for (const raw of text.split("\n")) {
    if (raw.startsWith("## ")) {
      const match = raw.match(/^## (\d+)\.\s*(.+?)\s*$/);
      section = match ? { n: Number(match[1]), name: match[2] } : null;
      continue;
    }
    if (!section || !raw.startsWith("|")) continue;
    const category = raw.match(CATEGORY_RE)?.[1];
    if (!category) continue; // a data row is one that carries a category
    const cells = cellsOf(raw);
    if (isSeparator(cells)) continue;
    // Printed-part tables carry stock and mass; other tables carry quantity and unit price.
    const printed = section.n === 7;
    const qty = printed ? cells[1] : cells[cells.length - 3];
    lines.push({
      section: section.n,
      sectionName: section.name,
      name: printed
        ? plainMarkdown(cells[0])
        : stripPack(plainMarkdown(cells[0])),
      href: cells[0].match(/\]\((https?:[^)\s]+)\)/)?.[1] || null,
      qty: plainMarkdown(qty || ""),
      count: parseCount(qty || ""),
      measure: printed
        ? { value: Number(plainMarkdown(cells[3])), unit: "kg" }
        : parseMeasure(qty || ""),
      stock: printed
        ? plainMarkdown(cells[2]).replace(/\s*\([^)]*[×,][^)]*\)/g, "")
        : null,
      usd: parseMoney(cells[cells.length - 1]),
      category,
      targets: parseTargets(raw),
    });
  }
  return lines;
}
