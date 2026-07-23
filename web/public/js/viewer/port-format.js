// Port face format — the shared reading of `scorecard.py`'s `Port.face`, which is
// either one of the six body faces by name or, where a fitting is clocked off the
// world axes, the exit axis given directly as a vector. `_routing.normal_of` and
// `face_name` are the CAD side of the same two forms.
//
// Deliberately dependency-free, like pick-format.js: the marker overlay imports
// three.js at load, so the reading lives here where node:test can exercise it
// against the sidecar's own two shapes.

// Body face a port exits -> its outward normal.
export const FACE_NORMAL = {
  "x-": [-1, 0, 0], "x+": [1, 0, 0],
  "y-": [0, -1, 0], "y+": [0, 1, 0],
  "z-": [0, 0, -1], "z+": [0, 0, 1],
};

// The unit normal a port exits along, or null when the face is neither form — a
// marker with no readable direction is drawn as bad rather than aimed somewhere
// plausible.
export function faceNormal(face) {
  if (typeof face === "string") return FACE_NORMAL[face] ?? null;
  if (!Array.isArray(face) || face.length !== 3) return null;
  if (!face.every((c) => typeof c === "number" && Number.isFinite(c))) return null;
  const m = Math.hypot(face[0], face[1], face[2]);
  return m > 1e-9 ? [face[0] / m, face[1] / m, face[2] / m] : null;
}

// A port's face for display, mirroring scorecard.py's face_name.
export function faceLabel(face) {
  if (typeof face === "string") return face.replace("-", "−");
  const n = faceNormal(face);
  return n ? `(${n.map((c) => (c < 0 ? "−" : "+") + Math.abs(c).toFixed(3)).join(", ")})` : "?";
}
