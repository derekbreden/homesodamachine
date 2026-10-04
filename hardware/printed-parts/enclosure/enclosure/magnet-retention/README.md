# Centered cartridge retention pair

The pump-cartridge lower cradle and front-top each contain **one K&J RC62**.
Both ring axes point along Y, the cartridge insertion direction. Their centers
are at **X0, Z186.174 mm**, on the four tube axes and **92.350 mm below the pogo
row**. Attraction acts at tube height to help seat and retain the cartridge.
The existing tube stops, guide datums and pogo seats set its final position.
The pump cap contains the female pogo half; this retention ring belongs to the
lower cradle.

The [native geometry check](geometry-check.json) verifies both pockets, the
maximum-tolerance ring fit, a vertical insertion sweep, surrounding stock and
unchanged tube/pogo placement. [Section view](https://homesodamachine.com/3d?file=printed-parts/enclosure/enclosure/magnet-retention/section.step)
shows the pair and its covers in the assembled machine frame.

## Pocket and load path

The [RC62 manufacturer specification](https://www.kjmagnetics.com/rc62-neodymium-ring-magnet)
is 19.05 mm OD, 9.525 mm ID and 3.175 mm thick, axially magnetized N42, with
±0.1 mm dimensional tolerance. Each cavity is 19.45 mm wide and 3.575 mm deep.
Its lower half is a circular seat; its upper mouth keeps the full diameter clear
until the printed roof closes. There is no center post obstructing insertion.

Each mating face has a continuous **1.20 mm PET-GF cover**, supported around its
perimeter by the ordinary stock. This is a local cover section chosen to limit
magnetic separation. Backing remains at least 3 mm and the nearest tube/collar
bore retains 4.125 mm of web. At the nominal 0.246 mm frame gap the attracting
ring faces are **2.646 mm apart**. The pair's installed force and the printed
cover's capacity are unmeasured; the manufacturer's pull-to-steel figure does
not specify this covered magnet-to-magnet arrangement.

Force passes through the two covers into the cradle and front-top bulkhead.
The cartridge floor and fitted pump wells carry weight. Tube insertion stops
and collets locate and capture the four tubes; the existing guides resist tilt.
The [pogo mounting audit](../../../../reference/yyfkgcp-pogo-4p/mounting-audit.md)
retains its spring-compression and installed-gap limits. Stronger attraction
does not establish correct contact compression or tube insertion depth.

## Print and insertion

Both owning parts print in their production +Z orientation using black PET-GF
on the fixed left hardened standard-flow 0.4 mm nozzle. The separate sources are
[pump-cartridge-pause.3mf](v3/pump-cartridge-pause.3mf) for Mark2 and
[front-top-pause.3mf](v3/front-top-pause.3mf) for H2C. Each has one native `M400 U1`
insertion pause before the centered pocket's closing layer. They retain each
printer's saved trim, tree supports, show-surface exclusions and fine layer bands.
The pocket roof has a local support blocker; functional seats and lifting
ceilings elsewhere retain their accessible supports.

The [host/root specification](../heat-set-review/print-regions.json) adds local
100% infill through the clamp spines, pogo hosts and blind caps, upper Y seam
socket roots and Z rail/stop roots. The native archives retain every modifier
at its exact placement. Their emitted rows are checked against their actual
bead widths, with representative layers through each region and checks of
wider intervals against the current native material. The two jobs check 52,336
and 37,208 adjacent infill-row intervals respectively, with no uncovered material
witnesses. General infill stays at 15%. These are nominal deposition checks;
printed density, joint strength and drop survival remain unmeasured.

The flat pocket roof is at machine Z196.179 mm, 30.984 mm above the cartridge
bed face and 36.179 mm above the front-top bed face. The nominal seated ring has
0.48 mm roof air; the conservative maximum-diameter ring has at least 0.38 mm.
The [native check](v3/native-check.json) records the actual emitted pauses, completed
open rims, short closing bridges and exclusion of internal supports.
[Preparation](v3/preparation.json) binds the source, native archive and G-code
hashes. These jobs have not been submitted.
[Queue](queue.json) keeps the two jobs independent and requires a new start
request for either printer.

| Part / printer | Pause before print Z | Completed open rim | First closing layer |
| --- | --- | --- | --- |
| Lower cradle / Mark2 | 31.16 mm | 30.92 mm | 31.16 mm |
| Front-top / H2C | 36.44 mm | 36.20 mm | 36.44 mm |

The emitted first closing beads leave at least 0.316 mm and 0.401 mm respectively
above the conservative maximum-size ring. These are native path clearances;
printed sag and magnet seating error remain physical observations.

Before either print, pair the two rings in their attracting orientation and mark
the mating faces. The installed faces must present opposite poles to each other;
both rings' north vectors then point along the same machine Y direction. Keep
the cartridge and front-top labels with the pair when separating it.

At the print's pause, insert its labeled ring upright from above, with its axis
along Y. Seat it at the bottom of the D-shaped cavity, against the cover toward
its future mate. It must lie fully below the completed rims, with the tube
passages clear. Resume only after insertion and toolhead clearance are checked.
Both printers share the circuit: a separately authorized start or resume must
be at least 180 seconds after the other printer accepts a start or resume.

RC62 has an **80 °C maximum continuous-service rating**. These saved PET-GF jobs
use an 80 °C bed and 280 °C nozzle with chamber heating off. Local magnet
temperature during sealing and retained magnet strength after printing are
unmeasured. The successful paused ASA Aero float insertion in the
[float record](../../../cold-core/magnetic-float/all-aero/physical-observations.json)
establishes that float's observation; it does not qualify this upright PET-GF
retention pair.

## Assembly evidence

[Physical observations](physical-observations.json) retains the evidence limits.
The customer outcome is four fully seated, captured tubes and reliable pogo
contact without the cartridge creeping out. The existing full-assembly trial
provides the relevant check: compare marked tube insertion depths with and
without the pair, confirm all four tubes bottom, the guides settle without
tilt, each pin stays within its stated stroke, and withdrawal releases normally
after the collets are operated. Check the finished pockets for roof sag and
the printed magnets against an untouched RC62 in the same gap/orientation fixture.
No automatic seating, retention force, thermal exposure or lifetime is accepted
from CAD or printer completion alone.

## Reproduce

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/magnet-retention/audit.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/magnet-retention/audit_prints.py --revision 3
```

The preparation reads saved local production projects identified in its record.
It checks the current STEP/STL against the geometry record before preparing a
candidate. The audit reads the native archives; neither script sends a job or
communicates with a printer.
To prepare a fresh candidate, run `prepare_prints.py` with `--slice` and an unused
`--revision` number. Projects and archives named in a preparation record are
immutable. The current queue selects only the passing v3 jobs.
