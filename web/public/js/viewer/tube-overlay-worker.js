import { relaxTube } from "./tube-relaxation.js";
import { createTubeContactIndex, screenTubeContacts } from "./tube-contacts.js";

let contactIndex = null;
let bodyNames = [];
const bodyName = (name) => (name || "").replace(/\/\d+$/, "");

function matchingNames(name) {
  name = bodyName(name);
  const matches = bodyNames.filter((body) => body === name || body.endsWith(`/${name}`));
  return matches.length ? matches : [name];
}

self.onmessage = ({ data }) => {
  if (data.type === "init") {
    contactIndex = createTubeContactIndex(data.meshes);
    bodyNames = [...new Set(data.meshes.map((mesh) => bodyName(mesh.name)))];
    return;
  }
  const { id, run, options } = data;
  try {
    const contactRun = {
      radiusMm: run.radiusMm,
      radiusRanges: run.radiusRanges || [],
      excludeNames: (run.excludeNames || [run.id]).filter(Boolean).flatMap(matchingNames),
      allowedContacts: (run.allowedContacts || []).filter((site) => !site.holdId || site.holdId !== options.omitHoldId)
        .flatMap((site) => matchingNames(site.name).map((name) => ({ ...site, name }))),
    };
    const nominalContacts = contactIndex ? screenTubeContacts(contactIndex, { ...contactRun, points: run.points, arcLengths: run.arcLengths }, { maxContacts: 2000 }) : null;
    const results = {};
    for (const scenario of ["straight", "coil-positive", "coil-negative"]) {
      const result = relaxTube(run, { ...options, scenario });
      if (contactIndex) {
        result.contactScreen = screenTubeContacts(contactIndex, { ...contactRun, points: result.points, arcLengths: result.arcLengths }, { maxContacts: 2000 });
        result.diagnostics.contacts = "surface-screened";
      }
      results[scenario] = result;
    }
    self.postMessage({ id, results, nominalContacts });
  } catch (error) {
    self.postMessage({ id, error: error.message || String(error) });
  }
};
