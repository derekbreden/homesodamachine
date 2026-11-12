// What a machine's published facts say it is missing.
//
// The installed machine's facts (<model>.facts.json, a published file beside its STEP) list
// every run the plumbing needs — a tube, a mate, a threaded joint — with the two ports it joins
// and whether the machine as built completes it, and the wires the build left out as not
// routed. This reads the runs it does not complete and those wires, for
// the check or x the 3D viewer marks the model with (public/js/viewer/missing-parts.js). The site
// reads the published file when a model is opened; the build does nothing for it.

export const FACTS_SUFFIX = ".facts.json";

// A STEP path -> the facts beside it (both root-relative).
export function factsPathFor(stepPath) {
  return stepPath.replace(/\.step$/, FACTS_SUFFIX);
}

/**
 * @typedef {Object} MissingRun
 * @property {string} id          the run's connection id, such as "fluid-26"
 * @property {string} from        the port it leaves, "body.port"
 * @property {string} to          the port it reaches, "body.port"
 * @property {string[]} tubes     the tubes of the run that the machine does not hold
 * @property {string[]} fittings  the fittings of the run that the machine does not hold
 * @property {boolean} wiring     true for a wire, a termination or a jacket the wiring is without
 * @property {string} why         the error that ended a tube or a wire, where the facts give it
 */

// The names a run row lists under `key`.
function listed(run, key) {
  return Array.isArray(run[key]) ? run[key].filter((name) => typeof name === "string") : [];
}

/**
 * The runs `facts` lists that the machine does not complete, in the facts' order, each with the
 * tubes and fittings its row names as absent; then what the facts list the wiring as built
 * without.
 * @returns {MissingRun[]}
 */
export function missingRuns(facts) {
  const runs = Array.isArray(facts?.runs) ? facts.runs : [];
  const wires = Array.isArray(facts?.wiring_not_routed) ? facts.wiring_not_routed : [];
  const entry = (row, wiring) => ({
    id: row.id,
    from: String(row.frm ?? ""),
    to: String(row.to ?? ""),
    tubes: wiring ? [] : listed(row, "missing_native_routes"),
    fittings: wiring ? [] : listed(row, "missing_fittings"),
    wiring,
    why: typeof row.why === "string" ? row.why : "",
  });
  return [
    ...runs
      .filter((run) => run && typeof run.id === "string" && run.status !== "complete")
      .map((run) => entry(run, false)),
    ...wires.filter((wire) => wire && typeof wire.id === "string").map((wire) => entry(wire, true)),
  ];
}

/**
 * What is so of a missing run, in words: each tube its facts name is not routed and each
 * fitting is not in the machine; a wire with its two terminals is not routed, and anything else
 * of the wiring is not in the machine. A run whose facts name nothing is only not complete.
 * @param {MissingRun} run
 * @returns {string}
 */
export function lacks(run) {
  if (run.wiring) return run.from || run.to ? "wire is not routed" : "not in the machine";
  const parts = [
    ...(run.tubes ?? []).map((name) => `tube ${name} is not routed`),
    ...(run.fittings ?? []).map((name) => `fitting ${name} is not in the machine`),
  ];
  return parts.length ? parts.join(", ") : "not complete";
}

/**
 * One missing run as the list says it: its name, the two ends it would join where it has them,
 * and what is so of it.
 * @param {MissingRun} run
 * @returns {string}
 */
export function said(run) {
  const ends = run.from || run.to ? ` — ${run.from} to ${run.to}` : "";
  return `${run.id}${ends}: ${lacks(run)}`;
}

// The body a port is on: "valve-v-h.inlet" -> "valve-v-h".
export function bodyOf(port) {
  return String(port ?? "").split(".")[0];
}

/**
 * The bodies in a scene that stand for the body `name`, among the scene's `names`: the body
 * itself, the same body carried by the cold core, or the cold core's casing for the foam
 * assembly.
 * @param {string} name
 * @param {Iterable<string>} names
 * @returns {string[]}
 */
export function sceneBodies(name, names) {
  const held = new Set(names);
  if (held.has(name)) return [name];
  if (held.has(`cold-core/${name}`)) return [`cold-core/${name}`];
  if (held.has(`terminal-${name}`)) return [`terminal-${name}`];
  if (name === "foam-assembly") return [...held].filter((n) => n.startsWith("cold-core/foam-"));
  return [];
}
