// THE LOCAL GEOMETRY SERVICE. On a machine with `hsm` installed (tools/hsm/README.md), /3d asks
// it what the payload it drew measures. server.js mounts this off Render only: the deployed site
// answers /api/hsm with a 404, and its viewer draws and picks as it always has.
//
//   GET  /api/hsm          { hsm }                  whether a query here has an hsm to answer it
//   POST /api/hsm          { file, op, ...fields }  one query against `<file>.mesh`, answered as
//                                                   hsm answers it: { ok, result | error }
//
// `file` is the model's `.step` under hardware/, the name the page opens it by, so a query reads
// the payload /meshes served the page. The daemon behind hsm re-reads a payload that moved, and
// none of this watches a file: the page asks /meshes whether its payload moved
// (public/js/viewer/hsm.js), and /meshes answers off a stat.

import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

// The fields each query takes, as the hsm socket protocol names them.
const OPS = {
  where: ["pattern"],
  gap: ["a", "b"],
  overlap: ["a", "b"],
  move: ["part", "by", "against", "min_volume"],
  section: ["part", "normal", "offset"],
  ray: ["origin", "direction", "max_distance"],
};

function findHsm() {
  if (process.env.HSM_BIN) return process.env.HSM_BIN;
  for (const dir of (process.env.PATH || "").split(path.delimiter)) {
    const candidate = path.join(dir, "hsm");
    try {
      fs.accessSync(candidate, fs.constants.X_OK);
      return candidate;
    } catch {}
  }
  return null;
}

export function mountHsmRoutes(app, { hardwareDir }) {
  // Looked up until found, so an hsm installed while the server runs answers the next ask.
  let bin = null;
  const hsm = () => (bin ??= findHsm());

  app.get("/api/hsm", (_req, res) => {
    res.set("Cache-Control", "no-store");
    res.json({ hsm: Boolean(hsm()) });
  });

  app.post("/api/hsm", (req, res) => {
    const { file, op } = req.body ?? {};
    const fields = Object.hasOwn(OPS, op) ? OPS[op] : null;
    if (!fields) return res.status(400).json({ ok: false, error: `no hsm query is called ${op}` });
    const scene = typeof file === "string" && !file.includes("..") && file.endsWith(".step")
      ? path.join(hardwareDir, file) + ".mesh" : null;
    if (!scene || !scene.startsWith(hardwareDir + path.sep)) {
      return res.status(400).json({ ok: false, error: "file is a .step under hardware/" });
    }
    const binary = hsm();
    if (!binary) return res.status(503).json({ ok: false, error: "hsm is not installed here" });
    const request = { scene, op };
    for (const field of fields) if (req.body[field] !== undefined) request[field] = req.body[field];
    // A cold scene loads in tens of seconds; hsm's own reply carries what went wrong.
    execFile(binary, ["--root", path.dirname(hardwareDir), "request", JSON.stringify(request)],
      { maxBuffer: 64 * 1024 * 1024, timeout: 600_000 }, (error, stdout, stderr) => {
        let reply = null;
        try { reply = JSON.parse(stdout); } catch {}
        if (reply) return res.json(reply);
        res.status(502).json({ ok: false, error: (stderr || error?.message || "hsm did not answer").trim() });
      });
  });
}
