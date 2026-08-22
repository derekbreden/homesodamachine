// The one local CAD fast lane.  It is a dev-only composition beside the production artifact
// graph: an enclosure-source save gets a current back-top bench view before the exact wave
// starts, and no other source is claimed here.

import path from "path";


export const LOCAL_BACK_TOP = Object.freeze({
  source: path.join(
    "hardware", "printed-parts", "enclosure", "enclosure", "enclosure.py",
  ),
  script: path.join("hardware", "assembly", "scenes", "_local_service.py"),
  output: path.join("hardware", "assembly", "scenes", "out", "local-back-top.glb"),
});


function sameFile(a, b) {
  return path.resolve(a) === path.resolve(b);
}


export function localServiceForChange(projectRoot, changedPath) {
  const sourcePath = path.join(projectRoot, LOCAL_BACK_TOP.source);
  if (!sameFile(changedPath, sourcePath)) return null;
  return {
    sourcePath,
    scriptPath: path.join(projectRoot, LOCAL_BACK_TOP.script),
    outputPath: path.join(projectRoot, LOCAL_BACK_TOP.output),
  };
}


// Keep the ordering itself outside server.js's chokidar callback so it is executable as a
// unit test.  A superseded preview belongs to an older save and must not start that save's
// exact wave; the newer callback will run its own preview and then the coalescing wave.
export async function runLocalServiceFirst(
  projectRoot,
  changedPath,
  runLocalService,
  runExactWave,
) {
  const job = localServiceForChange(projectRoot, changedPath);
  if (job === null) {
    await runExactWave();
    return "not-applicable";
  }
  const status = await runLocalService(job);
  if (status !== "superseded") await runExactWave();
  return status;
}
