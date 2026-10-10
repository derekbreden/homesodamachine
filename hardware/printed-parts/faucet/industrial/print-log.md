# Industrial faucet print log

## Complete 0.12 mm shoulder faucet — held 2026-10-09, Mark2

- [Complete five-part plate](prints/2026-10-09-shoulders012-wing050-drip4-mark2/README.md),
  including the side-down lever, corrected continuous six-wall solid foot,
  base Arachne and 15% infill/wall overlap.
- 0.20 mm first bed layers and normal 0.24 mm layers; the base alone uses
  0.12 mm at print Z13.40–29.00 and Z55.16–68.12 mm.
- Industrial cover wings extend 0.50 mm with matching arch headroom;
  retaining-lip datum and engagement are preserved. Physical seating is
  unassessed. The shared tip uses an unsealed pocket and a round Ø4 mm
  underside drip hole with no drain bungs or insertion tool.
- Derek requested: "Apologies, pause on that print". No import or Send was
  attempted for the held candidate. Its launch plan retains the hold and
  needs a separate go-ahead before fresh printer gates and one Send.
- Native and physical scope are recorded in the selection and exact job
  records. Beautiful 0.08 mm finish remains accepted only on its identified
  earlier complete article; 0.12 mm finish, corrected exterior and new drip
  behavior require observation.

## Complete variable-layer recipe — selected 2026-10-09

- Derek selects the earlier successful complete five-part print: base, shared
  tip, industrial display cover, counter plate and side-down lever. The
  [frozen recipe](prints/2026-10-09-two-shoulders008-with-lever-mark2/preparation.json) binds the archive and source
  hashes for Mark2 task/job `1322285082`.
- 0.20 mm first bed layer, 0.24 mm normal layers, and 0.08 mm on the base in
  print Z13.40–29.00 and Z55.16–68.12 mm only. Native estimate: 6 h 13 min 4 s.
- The [reported physical result](prints/2026-10-09-two-shoulders008-with-lever-mark2/physical-result/physical-result.json)
  accepts beautiful fine-band finish and removal of their few thin-layer
  supports. Lines/defects beside the screw points remain documented on this
  exact article. No further complete faucet is submitted by this selection.
- Variable layer height is the accepted shipping compromise; further
  whole-faucet 0.08 mm iteration and research are deferred. Selection does not
  establish structural strength, endurance or complete product qualification.

## Tip starting-band complete faucet — failed 2026-10-09, Mark2

- Exact accepted task/job `1324374637`,
  `2026-10-09-industrial-faucet-complete008-tip-root024-petgf-left04-z004-v6-mark2.gcode.3mf`.
  Archive SHA-256: `3dfb53e7a76e024790d88a4fbcfee1696c2c9e5a76e51989a1040cfeeb798c01`.
  The [physical record and five photographs](prints/2026-10-09-tip-root024-mark2/physical-result/physical-result.json)
  retain the exact G-code hash, original acceptance and process.
- Complete five-part black PET-GF plate, fixed left hardened 0.4 mm nozzle,
  Textured PEI, Mark2 +0.04 mm requested/+0.02 mm emitted trim. A 0.20 mm first
  bed layer is followed by 0.08 mm model layers except for the tip's eight
  0.24 mm starting layers through Z2.12, returning to 0.08 mm at Z2.20.
  Saved temperatures, speeds, tree supports and normal motion settings are
  retained. Base reinforcement is the continuous six-wall solid foot with
  Arachne and 15% infill/wall overlap.
- Derek reports failure of the tip and wing after they gained more height,
  noting their small XY footprint relative to Z. Tip photos show localized
  ragged/raised bands and loose strands. The rectangular display-cover wing
  region shows an uneven/separated edge and loose extrusion above standing
  supports. Loose debris is visible on the plate; the still photos do not
  establish whether a piece tipped, shifted or contacted the nozzle.
- Possible print-head dragging, potentially worsened by layer lifting, is
  the operator's hypothesis. The initiating event and failure height are
  unmeasured. No timelapse causal diagnosis is made for this article.
- A fresh matching-job reading at 2026-10-10 03:25:28 UTC reports `FAILED`,
  layer 0, print error 0 and no HMS entries. The terminal layer counter is
  not the photographed failure height; telemetry does not assess physical
  finish or identify the initiating event.

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
