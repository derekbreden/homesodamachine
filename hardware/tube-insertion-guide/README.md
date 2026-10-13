# Tube insertion jig build guide

Twenty-six Letter pages with one CAD view per assembly or operating action. The guide
covers the printed T handle and common guided carrier, cap-support puck, two complete
BESSEY GSCC2.506 metal screw clamps, sleeve fitting and sleeved-tube insertion.
The [fixture](../printed-parts/fixtures/tube-insertion/README.md) is bench tooling.

The accepted faucet lever attaches to the bare Touch-Flo before the tube or shell.
It remains down at unpressed rest during sleeve fitting and donor insertion. The
TPU thimble goes evenly onto the square-cut LLDPE tube outside the donor and reaches
its annular cap before the sleeved end enters the empty metal port. The
[operator observations](../printed-parts/faucet/lever-replica/assembly-observations.json)
and [faucet procedure](../assembly/faucet-and-umbilical.md) establish that sequence.

The later shell insertion belongs to the
[faucet assembly guide](../faucet-assembly-guide/README.md). The attached faucet
lever flips up for entry, the shell pushes it forward as the donor seats, and it
snaps down to unpressed rest. The shell prevents the seated lever from reaching
that flipped-up entry pose.

## Parts and contacts

The seven printed pieces are A base/reaction block, B guided carrier, D lower jaw,
E upper jaw, two F preformed TPU liners and G cap-support puck. Purchased clamps
C1/C2 are complete BESSEY GSCC2.506 metal screw clamps, each with a 6-inch opening
and 2.5-inch throat. The
[verified Amazon Prime listing](https://www.amazon.com/dp/B000FA0BL8) is $10.99 each,
quantity two, checked 2026-10-10. The stocked hardware is two M5 x 50 socket-head grip screws, two
M5 x 20 DIN 7991 countersunk carrier screws, four M5 square nuts and two
25 mm OD M5 fender washers. Two owned 4-inch steel C-clamps hold the base to the
bench so both hands can operate the insertion screws.

The lower jaw bolts to B before the joined assembly enters A's guides. It lifts
out for sleeve fitting with the T handle still attached. The two F liners are
thick finished half-channel blocks with 28 mm contact length and 5.125 mm minimum
backing. Their manufacturing pose puts the tube axis vertically on an 9 x 20 mm
footprint. Rotate each finished block into its 8 mm deep rigid jaw pocket for use. Each
liner stands 1 mm proud. Both closure screws share the liner's axial centre.

Page 3 exposes both outboard screw-pad contacts and both complete metal force
loops in a top view. Each fixed clamp pad bears on the rear of the donor reaction
block, and each screw pad bears on the rear jaw face at tube height. Both screws
advance one grip, which stays square in its guides. The metal donor annulus bears
against the reaction block; the arches, plunger and accepted faucet lever remain
clear. Two pressure points establish their positions, without establishing equal
force sharing or a load rating.

Secure the base for two-handed screw operation. Set the unloaded screw travel,
check all four factory pad faces and clear both wooden handles before applying
load. Advance both handles together when convenient, or make one very small
advance and immediately take up the opposite pad's gap before advancing again.
Keep the common grip square; unload if a gap or skew grows. Stop at the first seating witness or travel-stop contact,
and unload both screws for disagreement, skew, visible flex, tube bowing or
slippage, sleeve folding, or an advance that produces no tube movement.

Mark the rear grip face at the jaw seam, 18 mm inward from each outer edge of
the 100 mm-wide grip. On the 120 mm reaction block's rear face, mark both fixed-pad centres
30 mm above the base underside: the near mark is 36.75 mm from the front (-Y)
edge and the far mark is 19.25 mm from the back (+Y) edge. Before assembly,
remove all four generated support bodies from D's underside key pockets and
side-entry square-nut pockets. Their native presence and access do not establish
physical removal effort.

The guide uses the actual port depth D and two tube marks to locate the grip.
The guided travel is 20 mm. For D greater than 20 mm, start the sleeve by D - 20 mm
using both T wings evenly before seating the carrier at its retracted guide
position. This does not require a prior complete seating in the donor.

## Files and visual conventions

| File | Purpose |
| --- | --- |
| `NN-name.html` | Authored pages in numbered order. |
| `style.css` | Letter page system, following the weld-rotator guide. |
| `art/*.png` | Fixture CAD and wet-path sections. |
| `tube-insertion-guide.pdf` | Bound guide. |
| `tube-insertion-guide.cover.png` | Cover thumbnail for the drawings shelf. |
| `tube-insertion-guide.pdf.json` | Drawings shelf metadata. |
| `out/` | Ignored page renders and temporary STEP scenes. |
| `../../output/pdf/tube-insertion-guide.pdf` | Identical delivery copy. |
| `../../output/pdf/tube-insertion-guide.sources.json` | Manual source, artwork and print-project hash receipt. |

Coral identifies the part or fastener added or moved on a page. Existing printed
structure is black, threaded nuts are brass, metal is grey, and alignment tools or
marks are blue. Fasteners float off their holes along their insertion axes.

The clamp frames, factory pads and wooden handles use a nominal catalogue form,
not a measured capture of the purchased clamp. Check actual pad seating, unloaded
travel and clearance. The thimble and accepted faucet lever retain their source
geometry. A section opens the actual wet-path shapes; it is not a dimensional
solution for elastic deformation. The nominal jig views omit the accepted
installed faucet-lever pose because no measured rigid transform is recorded;
local captions preserve its attached, unpressed state.

The centred grip is a candidate with physical grip acceptance pending. The
[load basis](../printed-parts/fixtures/tube-insertion/load-basis.md) and
[geometry review](../printed-parts/fixtures/tube-insertion/geometry-review.json)
describe the design and evidence scope. CAD and offline slices do not establish
insertion force, grip, seating, equal load sharing, fixture strength or endurance.
A supplier clamp specification does not rate this complete assembly.

## Manual regeneration

```bash
tools/cad-venv/bin/python tools/tube-insertion-guide/insertion_art.py
tools/cad-venv/bin/python tools/tube-insertion-guide/build.py
```

The art script accepts individual scene names; `--list` lists them. The binder
renders the HTML leaves, checks their authored page bounds and joins them in
numbered order, then writes the identical delivery copy and source receipt.
These scripts run by hand. No build target, hook, watcher or recurring check
invokes them. The HTML, artwork, PDF, cover and metadata are committed artifacts.
