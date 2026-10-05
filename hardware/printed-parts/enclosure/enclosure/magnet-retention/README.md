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

Both magnet-owning parts print in their production +Z orientation using black
PET-GF on the fixed left hardened standard-flow 0.4 mm nozzle. Mark2's
[combined source](v4/pump-cartridge-cap-pause.3mf) prints the lower cartridge
cradle and its current pump cap together on one plate. The cap prints
crown-down, with its recessed female pogo seat and complete solid insert hosts.
H2C uses the independent [front-top source](v3/front-top-pause.3mf).
Each job has one native `M400 U1` insertion pause before its centered pocket's
closing layer. They retain each printer's saved trim, tree supports,
show-surface exclusions and fine layer bands.
The pocket roof has a local support blocker; functional seats and lifting
ceilings elsewhere retain their accessible supports.

The [host/root specification](../heat-set-review/print-regions.json) adds local
100% infill through the clamp spines, pogo hosts and blind caps, upper Y seam
socket roots and Z rail/stop roots. The native archives retain every modifier
at its exact placement. Their emitted rows are checked against their actual
bead widths, with representative layers through each region and checks of
wider intervals against the current native material. The Mark2 plate checks
52,336 adjacent infill-row intervals in the cradle and 1,734 in the cap;
H2C checks 37,208. None has uncovered material witnesses. General infill stays
at 15%. These are nominal deposition checks;
printed density, joint strength and drop survival remain unmeasured.

The flat pocket roof is at machine Z196.179 mm, 30.984 mm above the cartridge
bed face and 36.179 mm above the front-top bed face. The nominal seated ring has
0.48 mm roof air; the conservative maximum-diameter ring has at least 0.38 mm.
The [Mark2 native check](v4/native-check.json) and
[H2C native check](v3/native-check.json) record the actual emitted pauses,
completed open rims, short closing bridges and exclusion of internal supports.
The [Mark2 preparation](v4/preparation.json) and
[H2C preparation](v3/preparation.json) bind the source, native archive and G-code
hashes. The combined Mark2 job 1307633211 is complete; Derek confirmed magnet
insertion and manual resume. Its [physical result](v4/physical-result.json)
reports a sealed ring that rattles and a wonky first layer above it. The
independent reviewed H2C retention job remains unsubmitted. The Mark2
[support review](v4/support-lanes.json) includes the cap's crown grooves,
motor-terminal wells, screw counterbores and open pogo mouth; clear those
supports before installing any hardware.
[Queue](queue.json) keeps the two jobs independent. The insertion follow-up is
paused, automatic resume is disabled, and the old H2C source has no start
authorization. The [open fit samples](fit-coupons/README.md) compare X and Y
grip before selecting a tighter production pocket. Their preferred fit and
the cartridge's roof quality remain unqualified.

| Part / printer | Pause before print Z | Completed open rim | First closing layer |
| --- | --- | --- | --- |
| Lower cradle with cap / Mark2 | 31.16 mm | 30.92 mm | 31.16 mm |
| Front-top / H2C | 36.44 mm | 36.20 mm | 36.44 mm |

The combined Mark2 plate estimates **15 h 11 min**, with magnet insertion
about **6 h 35 min after starting** (native layer 344, 43% progress).
Its emitted countdown starts at 394 minutes to the pause; the native total
minus 516 minutes remaining at the pause gives 6 h 34 min 47 sec.
These minute-rounded slicer estimates include startup and exclude the
operator's pause duration. Only the lower cradle receives an RC62 on this plate.

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
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/magnet-retention/audit_cartridge_pair.py --revision 4
```

The preparation reads saved local production projects identified in its record.
It checks the current STEP/STL against the geometry record before preparing a
candidate. The audit reads the native archives; neither script sends a job or
communicates with a printer.
To prepare a fresh combined Mark2 candidate, run `prepare_cartridge_pair.py`
with `--slice` and an unused `--revision` number. `prepare_prints.py` prepares
independent single-part candidates. Projects and archives named in a preparation
record are immutable. The queue selects the passing combined Mark2 v4 and
independent front-top H2C v3 jobs.
