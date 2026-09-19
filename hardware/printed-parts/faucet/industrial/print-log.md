# Industrial faucet print log

## Black PET-GF — 2026-09-18, Mark2

- Complete Industrial shell base, shared shell tip, Industrial display cover
  and Industrial above-counter plate. The gasket is a separate TPU print.
- CAD X rotations: base −15°, tip −105°, cover −50° bezel-up, plate 0°.
- Black Polymaker PET-GF loaded by Derek, with the existing PET-CF mapping
  on the left external spool and 0.4 mm nozzle. Right nozzle unused.
- The snap uses 1.25 mm inward preload per wing, 1.20 mm engagement,
  3.00 mm lips, 3.48 mm grooves, 0.48 mm roof clearance, 0.30 mm end
  clearance and 0.25 mm inner-edge relief. The shared tip and Industrial
  cover STL hashes match the passing 36-row cover-fit reading.
- The complete emitted profile matches the successful white Sculpted job:
  0.24 mm layers, 0.20 mm first layer, two walls, 15% grid infill, 265 °C
  first-layer / 280 °C later nozzle temperatures, and an 80 °C Textured PEI
  plate. Requested +0.18 mm Z trim emits `G29.1 Z0.16`.
- Native slice: 4 h 45 min 12 s, 131.23 g at the saved profile density,
  1,019 layers. Minimum toolpath bed margin 22.38 mm; separation 26.24 mm.
- Support reading: one base body/nine labelled islands, one shared-tip body
  with unlabelled interfaces, one cover body/two labelled islands and three
  plate counterbore bodies. No sampled cover outer-bezel or lip-bearing
  contact. Physical removal, finish and Industrial fit are not yet observed.
- Sent once through Bambu Connect as `industrial-black-z018-mark2.gcode.3mf`.
  Bed leveling On; timelapse Off; flow dynamic calibration and nozzle-offset
  calibration Auto.
- Telemetry at 2026-09-19 02:20:53 UTC confirms that exact job RUNNING,
  0/1,019 layers, 285 minutes remaining, no print error and no HMS entries.
- Native archive SHA-256:
  `e3abe2fe5eaf94d0c40a0c1fea98f7bac52f1fe052eb0a28154087b11ab5a3c3`.
  Project, source, profile, support and launch hashes are in the
  [readiness record](faucet-industrial-petgf.readiness.json) and
  `.cache/prints/2026-09-18-industrial-black-z018-mark2/readiness.json`.
