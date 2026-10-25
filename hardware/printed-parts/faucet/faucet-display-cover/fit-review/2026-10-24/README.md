# Lowered Sculpted cover and display-button relief

The [physical record](../../../industrial/prints/2026-10-24-sculpted-cover-uniform024-mark2/physical-result/physical-result.json)
identifies repeated Sculpted cover installation failure and a tight but repeatedly
working square Industrial cover on the same latest tip. Close photographs identify
the side switch housing bearing on the ledge beside a mounting-post recess.
The reported approximately 1 mm cover shortfall is a visual estimate.

## Button pockets

The two complete vendor switch shapes are retained in the
[display reference](../../../../../reference/touch-flo-faucet/display-reference/buttons.json).
Their housings and round actuators follow the measured PCB-height correction.
The [native reading](button-review.json) measures 0.40 mm of switch/ledge
interference and 4.52493 mm³ of intersecting material per switch at the intended
lowered display position.

The corrected tip has two local rectangular pockets, approximately 5.00 × 5.60 mm,
with 0.50 mm clearance around each switch envelope. Their floors are N7.10,
1.00 mm below the surrounding N8.10 ledge. Nominal clearance below each switch
is 0.60 mm; the complete actual switch shape has at least 0.57499 mm distance
from the corrected tip and zero intersecting volume. The four existing foot
bearings and N3.30–6.78 snap region have zero material change. The display retains
its 4.50 mm inward reduction and four 1 mm foot recesses.

## Cover reach

The [cover comparison](native-review.json) uses the failed Sculpted cover,
the working Industrial control and a corrected Sculpted candidate. The
Industrial control's bezel-to-lip reach is 0.50 mm greater, with the same 0.50 mm
offset of its circular neck cutout. The corrected Sculpted cover matches those
dimensions: nominal glass clearance 0.60 mm, arch-crown clearance 0.65 mm,
1.30 mm bezel thickness and fixed N3.30–6.30 lips. The extension and arch offset
are coordinated dimensions of one 0.50 mm correction; they do not sum to 1 mm.
The bezel crown is N19.35, matching the lowered Industrial cover, 1.82249 mm
above the uncut round tube crown. The module itself retains its lowered seat.

`measure.py` exports the cover alternatives; `button_relief.py` cuts the two
switch pockets into the exact lowered tip. The corrected relaxed cover STL
and corrected tip STL are embedded in the
[requested complete fit print](../../../industrial/prints/2026-10-24-buttons-sculpted-bands020-mark2/README.md).
Its native project retains 0.24 mm ordinary layers and uses 0.20 mm in the
two selected base bands. These are print-specific geometry variants. The
[identified print's physical record](../../../industrial/prints/2026-10-24-buttons-sculpted-bands020-mark2/physical-result/physical-result.json)
reports that the cover fits very well over the display, tubes and wiring.
The remaining front-corner opening has a
[cover-only overlap trial](../../corner-overlap-review/2026-10-25/README.md).
Numerical installation force and retention are unmeasured.

The nominal CAD placement shows the intended seated position. It does not show
elastic deformation or establish that the previously working Industrial cover
held the hardware at that exact position.
