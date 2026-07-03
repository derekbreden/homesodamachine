// The parts sidecar — <part>.step.json / <part>.dxf.json beside a STEP or DXF, carrying the
// fabrication metadata that isn't in the geometry. Authored with the part (see hardware/README.md);
// read by web/lib/viewer-routes.js (surfaced on /api/dxf) and used by web/public/js/viewer/dxf.js
// to extrude a flat outline to its real thickness.

/**
 * @typedef {Object} Sidecar
 * @property {number} [thickness_mm]  material thickness (mm) — the DXF extrusion depth
 * @property {string} [material]      e.g. "G90 galvanized steel"
 * @property {string} [process]       e.g. "laser-cut + bent"
 * @property {string} [notes]         free-form authoring note
 */

// The fields the viewer surfaces from a sidecar; the rest is authoring context. Each is null when
// the part has no sidecar or the field is absent/mistyped — the viewer then draws it flat.
export function sidecarFields(meta) {
  const m = meta || {};
  return {
    thickness_mm: typeof m.thickness_mm === "number" ? m.thickness_mm : null,
    material: typeof m.material === "string" ? m.material : null,
  };
}
