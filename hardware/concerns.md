# Concerns

Concerns that are already answered, by stage of the machine's life, each with where its answer
lives, so no one raises them again. Agents don't write their own concerns here: an agent tells
Derek the concern, and only an answer he gives is recorded. A concern that stands is work to do,
not a row. Physical records and fastener specifications are in
[mechanical evidence and qualification](/hardware/mechanical-qualification/README.md), the safety
and regulatory basis is [`/business/regulatory.md`](/business/regulatory.md), and the cabinet is
[`/marketing/install-envelope.md`](/marketing/install-envelope.md).

## Printed and assembled

| Concern | Answer |
| --- | --- |
| Earthing the faucet's under-counter plate | Derek: “Adding earth to carbonator only sounds good to me.” The faucet retains its single four-conductor modular display connection. The carbonator has the dedicated protective-earth bond specified in [wiring](/hardware/assembly/wiring.md#1-chassis-ground-bonds-single-point-ground-on-the-cold-core-lid). |
| Foam pour heat and expansion | Derek reports several earlier pours into PETG-printed foam shells in which nothing melted and no surface was too hot to touch ([cold core](/hardware/assembly/cold-core.md)). |
| Braze heat beside printed parts | A wet-rag clamp at each braze, and the PETG plug face inspected afterward ([refrigerant loop](/hardware/assembly/refrigerant-loop.md)). |
| Hydrocarbon at the braze, and the drier's moisture | Argon flows through the opened loop from the first cut until vacuum ([refrigerant loop](/hardware/assembly/refrigerant-loop.md), [regulatory](/business/regulatory.md)). |
| Making the pump tubes | Each prepared pump carries two straight tubes of the machine's own black 1/4" LLDPE in its tube ends, clamped by the pump head's housing and set at the factory with the printed tube setting jig so each bottoms in its tee; nothing is machined or custom ([pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md)). |
| Zip-tied pump tube joints | No pump tube joint is tied: the pump head's own housing clamps each straight tube in its tube end ([pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md)). |
| 1/4" LLDPE bent at its R14 floor | A printed PET-GF [tube bend holder](/future/tube-bend-holder-exploration/README.md), 2 mm wall with 3 mm straight legs on both sides of a 90° turn, holds it there; Derek reports it works pretty well ([physical result](/future/tube-bend-holder-exploration/prints/2026-10-23-legs-123-w2-petgf-left04-z018-mark1/physical-result.json)). |
| Straightening B-fill's outlet inside the reservoir | Only a short tube tip enters the reservoir. It can remain slightly bent or angled there; the cap needs no straight outlet leg to correct it. Derek: “that tube being slightly angled (because we didn't add a straight leg to correct it) instead of straight is *totally fine*.” |
| Printing B-fill's small bridge over the curved channel | Derek: “this small with this specific geometry is something that will print fine.” The [guide source](/hardware/printed-parts/cold-core/_reservoir_b_fill.py) adds the usual 0.25 mm finish allowance upward throughout the channel, including the curved cup roof. Both [local test sets](/hardware/printed-parts/cold-core/foam-cap/prints/2026-10-28-b-fill-local/README.md) retain it. |
| Valve spade terminals beside tubes | Derek: “please don’t worry about the spades like that, it is causing you to do very silly things. The tabs bend, and the connectors are not large.” |
| Elbows meeting while a quadrant closes | The push-fit and TPU elbows turn on their stems and barbs. Derek: “the yellow one bends up and the teal one bends down and the slide past each other and can then connect” and “Not flexing, rotating, they all can rotate 360 degrees, but we only need 45 degrees of rotation here.” |
| Aiming the bottom ports' fixed push-fit elbows | Each neoFit AME4-N2-E points where its acetal thread stops, within neoFit's 1.1 ft·lb allowance on a 1/4" NPT. Derek: “It is possible to aim it sufficiently for our needs. And we will figure out how.” ([pressure vessel](/hardware/assembly/pressure-vessel.md)) |
| V-A elbow beneath the pump head | Derek attests that the physical arrangement fits with “a 1 mm clearance or so” and identifies the scan/model as conservative there. The [physical fit record](/hardware/reference/g-ganen-pump/under-head-tube/flat-elbow-observation.json) carries his October 26 report. |
| Enclosure walls and infill | Two wall loops and 15% gyroid, with local solid reinforcement at loaded features ([infill and deposited structure](/hardware/mechanical-qualification/README.md#infill-and-deposited-structure)). Derek: “I don’t see why we need more walls or increased infill percent.” |
| Insulated wires touching a surface or another wire | Derek: “I think the rules are different for wires. It is true that I don't care if the wire is flat against something. That doesn't matter at all. But it would also be a problem if a wire is running through like a 1 millimeter channel, if it's restricted on all sides. So it's not that it has to be 1 millimeter away from everything in every dimension, but it needs some room to exist.” The [routing rule](/hardware/wiring/README.md#routing-and-assembly) follows this room requirement. |
| The cold core's seam-channel fold close to the PRV shroud | Derek: “If there's a reason we can't be right up against the PRV let me know.” The fold behind the [seam channel](/hardware/printed-parts/cold-core/foam-shell/README.md#seam-channel) stands about 0.7 mm off the shroud's end. |
| Where the ASSE outlet cap's wrench flats stand | The scan fits the outlet cap's flats even with the main wrench's: 0.6° apart, about 0.17 mm at a corner ([Multiplex ASSE 1022](/hardware/reference/multiplex-asse1022/README.md)). Derek: “We have the hex modeled, what is the part you don't know? It clearly has a turn in our model” |

## Packed, shipped and stored

| Concern | Answer |
| --- | --- |
| Refrigerant hazmat labelling | The planned charge falls under the 100 g exception; no DOT refrigerant label applies ([markings](/hardware/markings/README.md)). |

## Carried and installed

| Concern | Answer |
| --- | --- |
| Width beside the disposal and the cylinder | The machine, its 40 mm side gaps and the cylinder fit a 30 in cabinet beside the disposal ([install envelope](/marketing/install-envelope.md)). |
| Fitting under the sink bowl | The machine ([enclosure](/hardware/printed-parts/enclosure/README.md)) is far shorter than the roughly 500–590 mm an 8–10 inch bowl leaves above the cabinet floor. |
| The water connection | Two kits and no saddle valve: a push-fit tee into an existing 1/4 in line, or an angle-stop adapter with its own quarter-turn shutoff, found by tracing the kitchen faucet's cold hose ([BOM](/hardware/ledger/bom.md), [install guide](/hardware/install-guide/README.md)). |

## Running

| Concern | Answer |
| --- | --- |
| Cabinet doors shut | The condenser sheds its heat only while the compressor runs, and the cabinet carries the small average through the gaps it has; the Lillium carbonator under this project's sink has run six months behind closed doors ([enclosure](/hardware/printed-parts/enclosure/README.md)). |
| Condenser air through the enclosure | The condenser, fan, shroud and compressor keep the donor ice maker's arrangement, and the flank grilles are pierced more openly than the donor's (Derek's comparison with the donor units). The compressor body in CAD is a clearance envelope, its calipered section run straight through the shell's full height ([`compressor.py`](/hardware/reference/compressor/compressor.py)), so the gap it leaves at the condenser face is packing room, not the air passage ([vents](/hardware/printed-parts/enclosure/enclosure/README.md#the-condensers-vents)). |
| Fingers or rodents through the grilles | The openings are slots narrower than the 6 mm a mouse needs or the 12 mm test finger ([vents](/hardware/printed-parts/enclosure/enclosure/README.md#the-condensers-vents)). |
| Refill and pour at once | Firmware blocks a refill during a pour and holds at most three valves on ([firmware and commissioning](/hardware/assembly/firmware-and-commissioning.md)). |
| Valve-driver heat in a warm cabinet | The drivers are lower-loss TBD62083 parts ([driver note](/hardware/pcb/pcba/uln2803.md)). |
| Muting the gas alarm | The gas alarm cannot be muted, and automatic dispensing injects no flavor while it sounds ([firmware and commissioning](/hardware/assembly/firmware-and-commissioning.md), [`machine.cpp`](/firmware/src_appliance/machine.cpp)). |
| Carbonic-acid backflow into the house supply | Simply having a 1022 already puts us ahead of most of these products. A 1022 that vents into the bowl at the faucet would be the only home arrangement I've found where the vent's discharge is defined, drained and visible. An ASSE 1022 beverage backflow preventer guards the inlet; its dedicated 4 mm OVER line terminates over the bowl near the faucet joint ([safety](/hardware/README.md#safety), [drain assembly](/hardware/assembly/asse-drain.md)). |

## Refill and clean

| Concern | Answer |
| --- | --- |
| Overpour | Overpour is expected customer behavior. The funnel's continuous silicone apron carries it across the exposed frame joints to the exterior sides, with a broad, flat underside resting on the roof ([funnel](/hardware/printed-parts/zone-c/funnel/README.md), [overflow review](/hardware/printed-parts/zone-c/funnel/overflow-review/README.md)). |
| Pouring a bottle under a deep sink basin | Derek: “who is going to actually turn the bottle completely vertical, when one need only tip barely over the horizon for the bottle to empty.” |
| Water and debris from above | The [lift-off cover](/hardware/printed-parts/zone-c/funnel-cover/README.md) covers the mouth between fills. The funnel's integral silicone apron covers the exposed frame/roof joints and upper seam screw wells, reaches both exterior sides, and rests flat on the roof ([overflow review](/hardware/printed-parts/zone-c/funnel/overflow-review/README.md)). |
| The funnel cover staying seated | Derek: “I am skeptical of the utility of the small deformations in the face of the friction already present, plus the fact that this will always be held in by gravity during its service life.” |
| The funnel's push-on drain seal | Derek calls it “a witch hunt (silicone leak, may happen, may not, no solid evidence it will)”. |
| One flavor carried into the other | Both flavors fill through the one funnel, and tap water never reaches its drain, V-B or the run to Y-B ([fluid topology](/hardware/topology/fluid-topology.md)). A fill's planned draw follows its bottle with air unless the full reed stops it first, and the clean cycle opens by drawing whatever the funnel holds out through the faucet ([`machine_policy.h`](/firmware/lib/machine_policy/machine_policy.h)). |
| Water filtration | A Waterdrop 15UC-UF 0.01 µm inline filter upstream, replaced yearly without tools ([BOM](/hardware/ledger/bom.md)). |

## Faults and outages

| Concern | Answer |
| --- | --- |
| Runaway carbonator fill | Every path is held by normally closed solenoids, V-K gates the carbonator fill ([fluid topology](/hardware/topology/fluid-topology.md)), the high reed stops a refill, and a cumulative pumping timeout latches ([`refill_policy.h`](/firmware/lib/machine_policy/refill_policy.h)). |
| Short-cycling after a firmware stop or a boot | Minimum off and on times hold the compressor ([`cold_policy.h`](/firmware/lib/machine_policy/cold_policy.h)). |
| Carbonator freeze-up with healthy probes | A cutout on the suction probe trips and recovers with hysteresis, and an invalid or missing reading parks the compressor ([firmware and commissioning](/hardware/assembly/firmware-and-commissioning.md)). |
| Where the relief valve discharges | Out of the appliance's west flank through a relief chase, into the sink cabinet ([PRV shroud](/hardware/printed-parts/cold-core/prv-shroud/README.md)). |
| A power outage | The fill valve fails closed and the compressor stops ([fluid topology](/hardware/topology/fluid-topology.md)). |
| 12 V supply faults | A reverse-polarity FET, a surge clamp and the supply's own current limit ([PCBA audit](/hardware/snapshots/pcba-audit-2026-07-13.md)). |

## Service and return

| Concern | Answer |
| --- | --- |
| What can be serviced | Nothing; every physical fault is answered by shipping a replacement unit ([design pressures](/hardware/design-pressures.md)). |
| Replacing the thermal cutoff | On Derek's bench it slides out along its clamp channel ([SF76E](/hardware/reference/sf76e-thermal-fuse/README.md)); the customer services nothing. |

## What the drink touches

| Concern | Answer |
| --- | --- |
| Glass fiber in contact with concentrate | The reservoir bodies and lids are PETG Translucent; PET-GF is the core's shells and caps around them ([cold core](/hardware/assembly/cold-core.md)). |

## Standards and claims

| Concern | Answer |
| --- | --- |
| R-600a end use and charge | Household refrigeration under SNAP and UL 60335-2-24 second edition, whose limit is 150 g per circuit, is the project's reasoned classification rather than an EPA determination; the expected charge sits well under that limit ([regulatory](/business/regulatory.md)). |
| Listing and federal duties | No UL or ETL listing is held or sought, the CPSC's general duty applies, and the AIM Act does not ([regulatory](/business/regulatory.md)). |
