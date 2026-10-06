# Printed parts

## Publish loop

    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py
    tools/cad-venv/bin/python tools/publish_now.py

The piece's own generator cuts its STEP, STL and payload (the pump cartridge has the dedicated
materializer above); `publish_now.py` grafts the changed payload into both viewer hosts — the
enclosure aggregate and the appliance assembly — and tells the site.

After the publish is live — never before, and never as a gate in the build path — lint the
piece you changed and justify or fix what it flags while Derek is already looking:

    tools/cad-venv/bin/python hardware/scripts/geometry_lint.py <piece>.stl

Findings print as pick text: paste one into the /3d Find box, or feed it to `pick_read.py`.
A finding that is intentional is answered in `<piece>.lint-answers` beside the STL — a
`[class] reason` line, one `click:` per instance (format in `geometry_lint.py`). A defect
fixed at one station usually has siblings; the lint's job is to find them before Derek does.

## What each file shows

The physical print is the part. The files answer different questions about it:

- CadQuery source and `.step` — the exact B-rep construction and analytic faces. On pieces
  with a mesh-only show skin the STEP is a smooth body.
- `.stl` — the tessellated geometry the slicer reads: the closest file to the print.
- `.step.mesh` — the payload `/3d` draws, cut from the STL at the viewer's tolerance
  (`hardware/scripts/flute_payload.py`). Picks arrive in this frame, and the pick's `file:`
  line names it, with what the reduction cost and the digest it descends from.
- `hardware/scripts/pick_text.py` composes pick text from geometry;
  `hardware/scripts/pick_read.py` answers pasted pick text off all three surfaces at once,
  nearest first, and says which of them hold the window.

That last reading is a LOCATION AND NOT A VERDICT. The payload's tolerance is a distance
bound, so a feature shorter than it is collapsed and bridged while the reading never leaves
budget: a coordinate can be real on the payload alone and still be a real defect — that is the
payload reporting geometry it could not draw, and what cannot be drawn at that scale usually
cannot be printed at it either. A surface comparison says where a thing shows up. It never
settles whether what somebody saw in the viewer was there.

## Supports

Prefer simple solid stock and broad flat interior walls with few face breaks.
Set one wall plane that preserves the required hardware clearance and backing
thickness. Add a curve, step or local recess only for a named fit, bearing,
drainage or access requirement. Do not contour the wall around every available
void to gain volume; quantify any useful capacity tradeoff against the simpler
wall before choosing the boundary.

Every printable piece in the enclosure assembly follows **Support-removal strategy** in
[`enclosure/enclosure/README.md`](enclosure/enclosure/README.md#support-removal-strategy).

Use a 0.20 mm first bed layer and normal 0.24 mm layers above it. Expanding
print-down show rounds use an additive chamfer tangent to their retained taper,
following `cadlib/overhang_round.py`: 0.5 mm outward per millimetre of build rise.
Use six walls locally through that transition band, saved speeds and wall-first order,
15% infill/wall overlap, and no supports on that exterior transition. Derek's accepted
tee-carrier surface is recorded in
[`enclosure/tee-carrier/physical-acceptance.json`](enclosure/tee-carrier/physical-acceptance.json).

Retain 0.08 mm for inward/top show rounds. Functional flat lifting ceilings, sliding
seats and retention bearings keep their required shape and receive accessible supports
where needed. Check emitted first/second-layer bead overlap and support contacts;
small bodies without interface labels count. A fine layer band alone excludes no support.
Other parts using the shared geometry still require their own native slice and physical
surface check before claiming the tee result transfers to them.

## Filament use

Derek wants every spool used fully, with reloading during a print as needed. Remaining
spool quantity is not a launch condition: do not ask for its weight or an estimate, or
hold a ready print for a quantity confirmation. Use the correct material mapping and
ask for reloading only when an actual runout requires it.

## Printer allocation

Read [bed placement guidance](../../tools/bambu-printers.md#placement-on-unseasoned-plates)
before laying out a plate. On unseasoned outer regions, keep model/support/brim
beads at least 20 mm inside the usable bed boundary; center small coupon plates
and aim for 80 mm where the complete test fits. Verify the native full-bead
envelope, not only the CAD bounds.

Derek's request to start a print on a printer confirms that its bed is clear.
Do not ask for a separate bed-clear confirmation.

When both printers are loaded with suitable material, have clear beds and are ready,
distribute the authorized test parts across both printers. Derek prefers using both
ready machines to leaving one loaded and idle while combining everything on a single
plate. Preserve each printer's own profile, nozzle mapping and Z trim, and keep the
startup spacing below.

For a single job that either ready printer can handle, prefer the printer that
has been idle with suitable filament loaded longer. Compare the idle-and-loaded
period, not idle time alone. A printer without the required material loaded is
not an equivalent candidate; both printers are not always loaded with PET-GF.

## Printer startup spacing

H2C and Mark2 share a circuit. Wait at least **three minutes after one printer accepts
a job before starting or resuming a job on the other**. Apply this to power-loss
recovery too, checking for an already-running job before sending anything. This is
Derek's trial interval for the reported startup breaker trips. The sender serializes
app access but does not enforce the interval. Record both launch times; see
[`tools/bambu-printers.md`](../../tools/bambu-printers.md#shared-circuit-startup-spacing).
