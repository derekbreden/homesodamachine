// What a machine's published facts say it is missing.
//
// The installed machine's facts (<model>.facts.json, a published file beside its STEP) list
// every run the plumbing needs — a tube, a mate, a threaded joint — with the two ports it joins
// and whether the machine as built completes it. This reads the runs it does not complete, for
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
 * @property {string} why         why the build left a tube out, where the facts say; else empty
 */

// The names a run row lists under `key`.
function listed(run, key) {
  return Array.isArray(run[key]) ? run[key].filter((name) => typeof name === "string") : [];
}

/**
 * The runs `facts` lists that the machine does not complete, in the facts' order, each with the
 * tubes and fittings its row names as absent.
 * @returns {MissingRun[]}
 */
export function missingRuns(facts) {
  const runs = Array.isArray(facts?.runs) ? facts.runs : [];
  return runs
    .filter((run) => run && typeof run.id === "string" && run.status !== "complete")
    .map((run) => ({
      id: run.id,
      from: String(run.frm ?? ""),
      to: String(run.to ?? ""),
      tubes: listed(run, "missing_native_routes"),
      fittings: listed(run, "missing_fittings"),
      why: typeof run.why === "string" ? run.why : "",
    }));
}

/**
 * What a missing run lacks, in words: each tube and fitting its facts name as absent. A run
 * whose facts name neither is only said to be not complete.
 * @param {MissingRun} run
 * @returns {string}
 */
export function lacks(run) {
  const parts = [
    ...(run.tubes ?? []).map((name) => `no tube ${name}`),
    ...(run.fittings ?? []).map((name) => `no fitting ${name}`),
  ];
  return parts.length ? parts.join(", ") : "not complete";
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
  if (name === "foam-assembly") return [...held].filter((n) => n.startsWith("cold-core/foam-"));
  return [];
}
