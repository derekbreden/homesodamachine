# Touch-Flo TPU O-ring print log

Iteration record for the printed TPU sealing thimble. Captures what
was printed, what happened, what was deduced, **and what's queued to
try next** — Derek 2026-05-24: "perhaps some sort of print log
should capture all this, and disregard any notion of the print log
not capturing advice, because I want this captured in the repo." So
forward-looking notes live here too, not just historical attempts.

This part iterates differently from the touch-flo-shell — there's no
PET-CF / nozzle / temp / scarf surface to tune. The variables are
purely **TPU hardness**, **CAD interference values**, and **install
technique**. Print settings are stock Bambu profiles for whichever
TPU SKU is loaded.

## v1 — open-ended sleeve (commit `e10ce99`, 2026-05-22)

Geometry: 8 mm tall, Outer Ø 10.20 mm, Inner Ø 9.45 mm, wall 0.375 mm.
Open both ends — water flows through the LLDPE inside, TPU seals
radially between LLDPE OD and body port ID.

**Slicer rejection** in Bambu Studio:

> Error: The following object(s) have empty initial layer and can't
> be printed. Please cut the bottom or enable supports.

Cause: Bambu's 0.4-nozzle TPU profile uses a ~0.5 mm first-layer line
width (wider than the 0.42 mm normal-layer line, for bed adhesion).
Our 0.375 mm wall is below what a 0.5 mm first-layer extrusion can
fill, so the slicer can't lay any first-layer path. The 0.4-nozzle
TPU profile is also the only Bambu-supported TPU profile — selecting
the 0.2-nozzle profile (which could handle the wall) loses TPU
filament selection.

### v1 with raft workaround (no CAD change)

Derek added a raft in Bambu Studio. Slicer accepted it.

**Why:** with a raft, the part doesn't have a "first layer of print"
— it has a raft underneath, and the part starts at raft_height +
raft_air_gap. The part's first layer then uses *normal* layer
settings (0.42 mm line width with Arachne thin-wall), which CAN
handle a 0.375 mm wall as a single variable-width perimeter. Nothing
about the wall geometry actually changed — the raft sidestepped the
first-layer width check.

Not printed in this configuration; the v2 redesign (below) supersedes
the workaround.

## v2 — thimble with cap (commit `57850a8`, 2026-05-24)

Geometry: 15 mm total height = 1.5 mm cap + 13.5 mm cylinder. Outer
Ø 10.20 mm, Cylinder ID 9.45 mm, wall 0.375 mm (unchanged), cap hole
Ø 6.5 mm. Closed bottom (cap) with a centered hole sized between
LLDPE ID (6.35 mm) and LLDPE OD (9.525 mm).

**Why thimble:** two improvements over v1.
- **Solves the first-layer rejection** by printing cap-down — first
  layer is a solid annular disk (the cap), not a thin ring. Arachne
  picks up the thin wall from layer 2 on top of an already-established
  base.
- **Adds a face seal** in series with the radial seal — LLDPE's
  square-cut bottom end bottoms out on the cap's top face,
  pressure-energized by water below pushing it harder onto the cap.
  Cap hole positively defines insertion depth (tube can't pass
  through).

**Print attempt: TPU 95A**, Bambu stock profile. Sliced cleanly
without a raft, printed without issue.

Derek said after first fit-up attempt:

- "Fits just fine around the LLDPE tube, barely any force required."
- "Fits just fine into the touch-flo bore, barely any force required
  there either."
- "But attempting both at the same time? Nah, not happening."

**Diagnosis** (Claude, 2026-05-24):

Either interface alone is close to a slip fit in 95A — FDM tolerance
has eaten most of the designed interference (0.0375 mm radial on
LLDPE + 0.10 mm radial in bore = 0.1375 mm total designed squeeze).
When you push the LLDPE through the thimble's ID alone, the wall has
somewhere to flex outward (into the bore-empty space). When you push
the thimble into the bore alone, the wall flexes inward (into the
LLDPE-empty cavity). **Doing both at once gives the wall nowhere to
go** — and 95A TPU at 0.375 mm wall thickness isn't compliant enough
to compress through that combined load. The dual-compression locks up.

## v3 — 85A, seats successfully (2026-05-30, settings per [`touch-flo-tpu-o-ring-85A-6mm.3mf`](touch-flo-tpu-o-ring-85A-6mm.3mf))

Derek said:
- New print in 85A; "got it to successfully seat with the tube in the touch-flow metal body, like actually inserted with the TPU, for the first time."

First successful dual-interface seat (LLDPE tube through the thimble **and** the thimble in the Westbrass body port, together) — the lockup diagnosed on the 95A v2 print. Confirms queued fix #1 (drop to 85A). The 85A spool was dried before this run (v2 notes had both 90A/85A undried).

Geometry as printed (per the current `touch_flo_tpu_o_ring.py` / `README.md`): inner Ø 9.2 mm, outer Ø 10.44 mm, wall 0.62 mm, cap hole Ø 6.5 mm, cap 2.1 mm, cylinder 13.5 mm, total 15.6 mm. (Wall is up from the v2-logged 0.375 mm; the part is now a 0.62 mm single Arachne wall.)

Settings observed in the 3mf:
- Printer: Bambu Lab H2C, `nozzle_diameter` `[0.6, 0.6]`; `print_settings_id` `0.18mm Balanced Quality @BBL H2C 0.6 nozzle`. Textured plate.
- Filament: `Bambu TPU 85A @BBL H2C`, `filament_type` TPU. `nozzle_temperature` 225 °C, `hot_plate_temp` 35 °C, `filament_flow_ratio` 1.0, `filament_max_volumetric_speed` 2.2 mm³/s.
- Process: `layer_height` 0.18 mm, `initial_layer_print_height` 0.3 mm, `line_width` 0.62 mm, `wall_loops` 1, `wall_generator` classic, `detect_thin_wall` 0, `sparse_infill_density` 0 %, `raft_layers` 0, `brim_type` auto_brim, `enable_support` 0.
- Object: one, `touch-flo-tpu-o-ring.step`, printed cap-down (per README). The 3mf is saved + printed-from; `slice_info.config` header-only.

## Queued for the next session (forward-looking advice)

In recommended order — try one change at a time, simplest first:

### 1. Print v2 in **TPU 85A**, current geometry unchanged

Most likely fix. 85A's elastic modulus is roughly half of 95A — same
geometry produces ~half the compression force at any given strain,
and the wall has ~2× the compliance to swallow combined FDM tolerance
+ designed interference. This part is in a low-pressure dispense
path, not a pumped line — sealing pressure comes from water acting
on the LLDPE end face and modest radial squeeze, not from needing
the TPU to be structurally firm. 85A is the right hardness for a
seal in this application.

Skip 90A and go directly to 85A — Derek noted both are in stock; the
hardness change is the dominant variable so go to the softest
available in one step.

### 2. If 85A alone doesn't go together, **reverse install order**

Currently the assembly procedure is: thimble cap-down into body port
first, then push LLDPE down through the open top. **Try instead:**
slip the thimble onto the LLDPE tube *outside* the body (LLDPE
through the cap from above, bottoms on the cap), then push the
LLDPE+thimble assembly into the port as a single unit.

**Why this might help:** with LLDPE already through the thimble,
the bushing OD is pre-stretched to its loaded diameter. The
remaining install motion is just one compression event — TPU
squeezing radially into the bore around the already-stretched ID —
instead of two simultaneous compressions (LLDPE pushing TPU inward
+ bore pushing TPU inward at the same time). TPU handles pure
circumferential stretch around the LLDPE more compliantly than
dual-compression-between-rigid-walls.

### 3. Wet-lube the OD during install

A wipe of water on the bushing's outer cylindrical surface drops
sliding friction at the bore. Standard plumbing trick for rubber
o-rings; works just as well for TPU. No silicone grease, no other
additives — just water.

### 4. If 85A + reversed-order + wet-lube *still* won't seat: CAD changes

Bigger guns, in roughly increasing intrusiveness:

- **Lead-in chamfer on the bottom outer edge** (0.5 mm × 30°). Lets
  the bushing start into the bore at a smaller-than-OD diameter and
  reach full OD only partway in. Gradual radial compression instead
  of full-OD all at once.
- **Drop the outer Ø nominal** from 10.20 to 10.10 or even 10.05.
  Trades static sealing pressure for ease of assembly. Soft TPU
  pressure-energizes pretty well; the seal doesn't need a lot of
  static squeeze.
- **Drop the wall to 0.30 mm** (already below current 0.375). With
  the cap providing the first layer, Arachne handles this. Thinner
  wall = more compliance per unit radial deformation. Need to
  re-check Bambu's actual thin-wall limit on the loaded TPU SKU
  before committing.

## Material on hand (2026-05-24)

- **TPU 95A** — in stock, dried, has printed v2.
- **TPU 90A** — in stock, not dried.
- **TPU 85A** — in stock, not dried.

Both 90A and 85A spools need a dry cycle before the next iteration.
Printing is paused until then.

## Open questions

- Does the printed v2 *actually* measure 10.20 OD / 9.45 ID, or has
  FDM brought both inside their nominal? A caliper pass on the 95A
  v2 print would confirm the diagnosis above and inform whether any
  CAD nominal needs bumping independent of the hardness change.
