# Full enclosure print readiness

The complete enclosure trial prints the four shell quadrants (front-top, front-bottom,
back-top, back-bottom) and the separate parts that go into them: the tee carrier plate and its
two window covers, the pump cartridge and cap, the machine display cover and the two G Ganen
cold-core mounting parts.

Every reviewed print archive, the printer and settings it is sliced for, the geometry it binds
by hash and its support-removal review are in the
[slice reviews](tee-readiness/full-enclosure-print/native-slice-reviews/README.md). What
printed, when and on which machine is in the [print log](enclosure/print-log.md).

Derek's print request is the go and the plate-clear: send the named reviewed archive with the
black PET-GF mapping. There is no print order. A productive print keeps running while checks
proceed; a concretely defective one is cancelled and replaced.

New jobs use the saved [PET-GF profile](../petgf.3mf): black PET-GF on the fixed left 0.4 mm
nozzle and `auto_brim`. H2C uses +0.18 mm requested trim (+0.16 mm emitted for Textured PEI);
Mark2 uses +0.04 mm (+0.02 mm emitted). Both configured printable areas are 325 × 320 mm, with
at least 15 mm model border. Each slice prints 0.08 mm layers consistently through the entire
height of every curve on a surface the user sees that meets a top or bottom face in its print
orientation, from where the curve leaves the wall to where it levels into the face, and 0.24 mm
elsewhere. Interior curves nobody sees are not held to it. Each actual slice reports
emitted brim and support paths, and every support contact has an accessible removal lane before
hardware installation, following the
[support-removal strategy](enclosure/README.md#support-removal-strategy).

Those visible 0.08 mm rounded surfaces print without support contacts, including back-top's
roof edges. Keep supports for separate functional features and use face-specific blockers on
the rounds. Inspect all emitted support paths, including short bodies without labelled
interfaces, against the rounded surfaces before sending a slice. Previously prepared archives
also require this check; their 0.08 mm layer-band checks alone do not establish it.

Measure each required visible curve's print-Z span on the STEP, then run
`hardware/scripts/verify_round_layer_band.py` on the exported `.gcode.3mf` for that object and
span. The emitted wall layers must cover the full span at 0.08 mm; the range setting in the
project alone does not establish this. A curve beginning at the bed also needs a 0.08 mm first
layer.

Every spool is used fully, with reloading during a print as needed; remaining filament
quantity is not a launch condition ([filament-use policy](tee-readiness/full-enclosure-print/filament-use-policy.json)).

## Accepted physical evidence

| Part or interface | Established result and current use |
| --- | --- |
| Tee-carrier visible rounds | Derek reports that the unsupported curve on the Mark2 v11 print is turning out beautifully. Use unsupported 0.08 mm visible rounds elsewhere, including enclosure back-top. This is an in-progress surface observation. [Physical record](tee-carrier/physical-acceptance.json). |
| Kamoer cartridge and cap | Derek confirms both pumps are firmly held with screws tightened and no vertical play. The current cap keeps the broad fitted contact geometry; its surrounding crown reaches the cartridge top while motor ends and spade-terminal wells remain open. The raised crown and four-tube operation are checked in the full trial. [Physical record](../../reference/kamoer-kphm400/physical-fit.json). |
| Beduan sockets | The production-profile socket fit is easy and accepted, with some retention during loose inverted shaking. Preserve the Ø7.2 sockets and use zip ties for positive retention. Installed tie access remains a full-assembly observation. [Physical record](../fixtures/valve-socket-fit/physical-acceptance.json). |
| Faucet lever | The flat-sided lever with the 9 mm cylinder channel has accepted fit and function. Reuse it. [Physical record](../faucet/lever-replica/physical-acceptance.json). |
| Faucet display cover | Its broad, substantial flexing walls and retaining lips work in PET-GF. This is Derek's accepted simple snap-fit example. [Physical record](../faucet/faucet-display-cover/physical-acceptance.json). |
| Machine display cover | The current cover has the short, nameplate-style snaps with every catch open underneath; it is the v3 print, face down on Mark2, and takes the current front-top. The 34 mm-skirt v4 print fits only the front-top printed on 09-21. Seating on the machine is unconfirmed. |
| Nameplate | Appearance, QR readability and snap fit are accepted. Reuse the print. Its complexity is not the preferred design example. [Physical record](nameplate/physical-acceptance.json). |
| C14 inlet and cord | Derek accepts the printed inlet/C13-cord station. Its fitted pocket and screw stations are preserved; the reference uses the measured flange outline and R6 corners. [Native interface evidence](tee-readiness/full-enclosure-print/hard-contact-review/README.md). |
| G Ganen feet and flow | Derek identifies four identical flexible rubber feet with approximately 7 mm pads; they slide fore/aft independently and can be removed. Captured scan positions are not a fixed bolt pattern. Discharge is enclosure −X, corresponding to reference +Y at +90° yaw. Actual screw passage, washer seating and loaded rubber behavior remain assembly observations. [Sample authority](../../reference/g-ganen-pump/scan-evidence.json). |

## Tee and release face

The registered tee envelope uses a conservative Ø16.5 fixed collar and Ø17.0 journal,
leaving 0.25 mm radial running air. Derek's run span is 42.5 mm extended / 39.2 mm pressed,
with 1.65 mm travel per run end. The branch measures **30.5 mm extended / 29.0 mm pressed**,
with **1.5 mm travel**; only the small outermost ring moves. The branch face stations
22.35 / 20.85 mm use the nominal Ø16.3 back-collar datum. The conservative clearance
envelope is a separate dimension. [Measurements](../../reference/jg-pp0208e-tee/branch-operating-measurements.json).

The Ø8.5 circular release aperture retains annular bearing against the observed terminal
face. The [terminal-bearing review](../../reference/jg-pp0208e-tee/terminal-bearing-review.json)
supports the full trial without another ring scan or caliper reading. Simultaneous contact,
release and relocking of all four actual rings remain physical checks.

## What the trial establishes

The complete printed assembly establishes valve tie installation; four-tube insertion,
capture, release and relocking; pump mounting, connectors and primed operation; and shell
closure. G Ganen screw/washer seating and rubber compression, DIGITEN arrow orientation, and
actual made-up gas-fitting fit are direct assembly observations. They do not require another
scan or a separate coupon before the trial. Production LLDPE routes retain nominal ¼-inch and
⅜-inch outside diameters.

Complete enclosure fit is an **outcome of this trial**, not a prerequisite to printing it.
