// Which parts Derek has tried in hand and said yes to.
//
// hardware/ledger/fitted.json holds a row for each time he tried a made part and said something
// affirmative about it: the part's material number, the date, his words, what he tried and
// where the fuller record is. The catalog the site serves carries those rows and the materials
// a print file is published for (catalog.fitted, from web/lib/fitted.js). The materials pane
// says fitted or not fitted yet on a printed part, and the list behind the machine's mark names
// its printed parts that are not fitted yet. Nothing here measures a part: it reflects the
// record.

/**
 * @typedef {Object} FittedRow
 * @property {string} date    the day he said it, YYYY-MM-DD
 * @property {string} said    his words
 * @property {string} tried   what he tried, in a few words
 * @property {string} [record] where the fuller record is: a path of the repository or a link
 */

/**
 * @typedef {Object} Fitted
 * @property {string[]} printed                 the materials a print file is published for
 * @property {Object<string, FittedRow[]>} rows  each material's rows, latest first
 */

// The materials a print file is published for: a model of theirs has an STL beside its STEP.
// `printFiles` are those STLs' paths under hardware/, without the extension. A bought part is
// not one of them, whatever files its reference model has.
export function printedMaterials(catalog, printFiles) {
  const files = new Set(printFiles);
  return (catalog?.materials || [])
    .filter((m) => m.kind !== "purchased")
    .filter((m) => (m.models || []).some((model) => model.file?.endsWith(".step") && files.has(model.file.slice(0, -5))))
    .map((m) => m.id);
}

// The record's rows by material, each material's latest first.
export function fittedRows(record) {
  const rows = {};
  for (const row of Array.isArray(record?.fitted) ? record.fitted : []) {
    if (!row || typeof row.material !== "string" || typeof row.said !== "string") continue;
    (rows[row.material] ||= []).push({
      date: String(row.date ?? ""),
      said: row.said,
      tried: String(row.tried ?? ""),
      ...(row.record ? { record: String(row.record) } : {}),
    });
  }
  for (const list of Object.values(rows)) list.sort((a, b) => b.date.localeCompare(a.date));
  return rows;
}

/**
 * What the record says of the material `id`: null for a part with no print file and no row,
 * else whether it is fitted and its rows, latest first.
 * @param {Fitted | null | undefined} fitted
 * @returns {null | {fitted: boolean, rows: FittedRow[]}}
 */
export function fittedState(fitted, id) {
  const rows = fitted?.rows?.[id] || [];
  const printed = Boolean(fitted?.printed?.includes(id));
  if (!printed && !rows.length) return null;
  return { fitted: rows.length > 0, rows };
}

// The printed materials among `ids` that have no row, once each, in the order given.
export function notFitted(fitted, ids) {
  const printed = new Set(fitted?.printed || []);
  const out = [];
  for (const id of ids) {
    if (printed.has(id) && !fitted.rows?.[id]?.length && !out.includes(id)) out.push(id);
  }
  return out;
}
