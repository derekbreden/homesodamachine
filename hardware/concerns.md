# Concerns

Every concern raised about the machine, through each stage of its life: answered, with where
the evidence lives, or open, with what exists so far. Physical records and fastener
specifications are in [mechanical evidence and qualification](/hardware/mechanical-qualification/README.md),
the safety and regulatory basis is [`/business/regulatory.md`](/business/regulatory.md), and
the cabinet is [`/marketing/install-envelope.md`](/marketing/install-envelope.md). The figures
live in the documents each row links. Each assembly procedure keeps its own open items as
well; a row here points to them where they bear on a concern.

## Printed and assembled

Inserts are melted into fresh prints, foam is poured around the core and rises against printed
walls, copper is brazed beside printed parts, and the core is closed for good.

| Concern | Status | Where it stands |
| --- | --- | --- |
| Cartridge-contact hardware and tools | Open | One connector pair uses four M1.4 × 4 inserts and four M1.4 × 8 screws; both packs are on order for 2026-10-07 ([purchases](/hardware/ledger/purchases.md)). The Wiha 26313 hand-operated 1.3 mm driver is on order for 2026-10-05; its Amazon order is verified in [tools](/hardware/ledger/tools.md#shop--bench-infrastructure). Existing fine iron tips require the specified cold reach/depth check. |
| Foam pour heat and expansion | Open | The body is foamed in one open-top pour around both PETG reservoirs, close-fitting in their pockets, and the carbonator's foil-covered reeds and probes; the caps are separate pours, clamped by their screws ([cold core](/hardware/assembly/cold-core.md)). Its exotherm, peak temperature and confined pressure are not set against PETG's ~80 °C glass transition or the float's reed-distance limit; the foam's data sheet is an open item in the cold-core procedure. |
| Heat-set insert seats and the structure around them | Open | The ruthex table, the native insert audit and the seam stations are in [screw diameter and insert anchorage](/hardware/mechanical-qualification/README.md#screw-diameter-and-insert-anchorage); sparse infill inside loaded features is in [infill and deposited structure](/hardware/mechanical-qualification/README.md#infill-and-deposited-structure). |
| Reservoir watertightness | Open | An earlier reservoir held water for hours; the current trials have no water result ([accepted physical evidence](/hardware/mechanical-qualification/README.md#accepted-physical-evidence)). |
| The float's magnet through welding and passivation | Open | The RC62 is rated 80 °C, and the float's exposure during the build is unmeasured ([all-ASA float](/hardware/printed-parts/cold-core/magnetic-float/all-aero/README.md)). |
| The donor in the BOM and the compressor in CAD | Open | The BOM's donor is Unit B, whose electrical interface is unrecorded, while the CAD compressor is Unit A's HD48Y11A envelope ([ice maker](/hardware/reference/ice-maker/README.md), [wiring](/hardware/assembly/wiring.md)). |
| The carbonator's weld, penetrant and hydro criteria, the inlet jet and the tapping fixture | Open | Owed in [pressure vessel](/hardware/assembly/pressure-vessel.md) and [water-inlet jet](/hardware/assembly/water-inlet-jet.md). |
| Joints buried by the foam | Open | The CO2 joint is tug-tested before the pour; the water-in joint is laid before it without one, and the general push-fit tug check comes after the core is closed ([cold core](/hardware/assembly/cold-core.md), [internal plumbing](/hardware/assembly/internal-plumbing.md)). The relief valve's foaming-in is the accepted service boundary ([PRV shroud](/hardware/printed-parts/cold-core/prv-shroud/README.md)). |
| Braze heat beside printed parts | Answered | A wet-rag clamp at each braze, and the PETG plug face inspected afterward ([refrigerant loop](/hardware/assembly/refrigerant-loop.md)). |
| Hydrocarbon at the braze, and the drier's moisture | Answered | Argon flows through the opened loop from the first cut until vacuum ([refrigerant loop](/hardware/assembly/refrigerant-loop.md), [regulatory](/business/regulatory.md)). |
| Pogo connector fit and mating/compression | Answered | The founder reports successful test fit and mating/compression in the printed test piece on 2026-10-04 ([physical record](/hardware/reference/yyfkgcp-pogo-4p/physical-observations.json)). The drawing-based 0.046 mm additional closing allowance is conditional; the complete enclosure's dimensional stack remains unmeasured ([mounting audit](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md#seating-and-dimensional-allowance)). |
| Clashes in the populated enclosure | Answered | The saved CAD assembly reports no clashes and no unanswered pairs, and every routed line clears: `pack-closes` and `lines-clear` in the [assembly scorecard](/hardware/manifold-layout/enclosure-assembly.scorecard.json). Physical closure of the populated shell is an outcome of the full print trial ([print readiness](/hardware/printed-parts/enclosure/print-readiness.md)). |

## Packed, shipped and stored

The carton is dropped and stood on its corners, laid on its side by a carrier, and left in a
cold truck or garage with whatever burn-in water the drain left inside.

| Concern | Status | Where it stands |
| --- | --- | --- |
| Laid on its side | Open | The compressor runs upright on a gravity-fed oil pickup ([enclosure](/hardware/printed-parts/enclosure/README.md)); which orientations the donor tolerates in transit, and how long it stands before starting, are unspecified, and Secop's [shipment-position bulletin](https://www.secop.com/fileadmin/user_upload/technical-literature/product-bulletins/basics/shipment_positions_04-2024_desn000h66m.pdf) treats both as compressor-specific. The carton's TOP arrow is on its interior ([finish, pack and ship](/hardware/assembly/finish-pack-ship.md)), the [install guide](/hardware/install-guide/README.md)'s power step plugs in with no wait, and the compressor's first start follows the minimum off time ([`cold_policy.h`](/firmware/lib/machine_policy/cold_policy.h)). |
| Freezing in a truck, a garage or an unheated house | Open | Burn-in drains the carbonator through the dispense path and air-purges the flavor channels ([acceptance and burn-in](/hardware/assembly/acceptance-and-burn-in.md)). The tap branch — bulkhead, ASSE 1022 preventer, split, V-K, the G Ganen head, its check valve, the water-in line and the jet — and the V-A leg stay wet behind closed valves, where the drain-dry card's tilt-and-listen check does not reach. [Finish, pack and ship](/hardware/assembly/finish-pack-ship.md) records no water in any line; nothing covers temperatures below 0 °C. |
| The pump cartridge in transit | Open | The cartridge is retained by its magnet pair and its tubes ([magnet retention](/hardware/printed-parts/enclosure/enclosure/magnet-retention/README.md)); no separate transit restraint is specified. |
| Concentrate left in the flavor path | Open | Burn-in purges concentrate without a water rinse, and the drain-dry step's "open each reservoir cap" reaches caps that sit under the bolted cold-core top cap ([finish, pack and ship](/hardware/assembly/finish-pack-ship.md)). |
| Transit packaging | Open | Carton, foam end-caps and shipping mass are open in [finish, pack and ship](/hardware/assembly/finish-pack-ship.md) and [other choices to assess](/hardware/mechanical-qualification/README.md#other-choices-to-assess). |
| Refrigerant hazmat labelling | Answered | The planned charge falls under the 100 g exception; no DOT refrigerant label applies ([markings](/hardware/markings/README.md)). |

## Carried and installed

It is lifted by its handholds, set down hard, tilted over the face-frame lip onto a cabinet
floor that may be soft or wet, plugged into the outlet under the sink, tied into the cold
supply, and joined by a CO2 cylinder standing beside it.

| Concern | Status | Where it stands |
| --- | --- | --- |
| A 4–6 inch drop splitting the midsection | Open | The objective, the two top pieces' opposite release directions and the seam's insert seats are under short-drop retention in [mechanical evidence and qualification](/hardware/mechanical-qualification/README.md). No assembled drop result exists. |
| Lifting by the handholds | Open | Support removal and the receiver/cover fit are accepted on H2C and Mark2 ([grip covers](/hardware/printed-parts/enclosure/grip-cover/physical-acceptance.json)); loaded lifting, retention force and repeated flexing are unmeasured. The machine's mass is an estimate and its centre of mass is unstated ([finish, pack and ship](/hardware/assembly/finish-pack-ship.md)), and the install guide has no lifting step. |
| The disposal's switched outlet | Open | Sink cabinets often carry a split receptacle with one half on the disposal's wall switch. The [install guide](/hardware/install-guide/README.md) asks for a grounded 120 V outlet; on the switched half the machine loses chilling, refill and the gas alarm whenever that switch is off. |
| Pulled forward or pushed back | Open | The CO2 tether, about 12 in, is about the length of the umbilical's service loop ([install envelope](/marketing/install-envelope.md)). The cord's housing is its only strain relief, the water, CO2 and umbilical tails are bare push-fits without locking clips, and the signal plug holds by its own latch ([+Y wall](/hardware/printed-parts/enclosure/y-wall-of-back-top/README.md), [faucet and umbilical](/hardware/assembly/faucet-and-umbilical.md)). The water inlet's collet stands proud of the rear wall at line pressure, and the rear clearance is exactly its lead and bend. |
| The CO2 cylinder standing free | Open | The 5 lb cylinder stands upright beside the machine with no chain, strap or bracket, so a tip can land on the regulator and pull the push-fit tether. Which side of the machine it stands on is unspecified, so it can stand in a grille gap. The gas disconnection procedure is unpublished ([install guide](/hardware/install-guide/README.md)). |
| Level | Open | The install guide has no levelling step, and the float's qualification excludes tilted motion ([all-ASA float](/hardware/printed-parts/cold-core/magnetic-float/all-aero/README.md)). |
| Drilling a stone countertop | Open | A wet diamond bit is advised and the procedure is unverified ([install guide](/hardware/install-guide/README.md)). |
| Faucet countertop thickness and donor clamp engagement | Open | The rear tube/cable routing clears the purchased steel throughout a 19–38 mm geometric envelope. The modeled 50 mm shank leaves 12.476 mm below the plate at a 30 mm slab and 4.476 mm at 38 mm. Actual usable threads, the complete retained washer stack and nut engagement are unmeasured; maximum clampable thickness is not established by the routing check ([mount stack](/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md)). |
| Priming the flavors on first use | Open | The Prime hold drives a pump without applying a dispensing valve plan ([install guide](/hardware/install-guide/README.md)). |
| Width beside the disposal and the cylinder | Answered | The machine, its 40 mm side gaps and the cylinder fit a 30 in cabinet beside the disposal ([install envelope](/marketing/install-envelope.md)). |
| Fitting under the sink bowl | Answered | The machine ([enclosure](/hardware/printed-parts/enclosure/README.md)) is far shorter than the roughly 500–590 mm an 8–10 inch bowl leaves above the cabinet floor. Refill headroom is under Refill and clean. |
| The water connection | Answered | Two kits and no saddle valve: a push-fit tee into an existing 1/4 in line, or an angle-stop adapter with its own quarter-turn shutoff, found by tracing the kitchen faucet's cold hose ([BOM](/hardware/ledger/bom.md), [install guide](/hardware/install-guide/README.md)). |

## Running

It cools, refills and pours under a sink, in a cabinet whose doors are shut, day and night,
beside a faucet that is splashed every time the sink is used.

| Concern | Status | Where it stands |
| --- | --- | --- |
| Carbonation in the first and following glasses | Open | Never measured. Acceptance defines the test, and [Carbonation Plan B](/future/carbonation-plan-b.md) maps each shortfall, including the refill's pressure margin, the warm-up of successive glasses and the air the sealed headspace gathers from tap water, to a change ([acceptance and burn-in](/hardware/assembly/acceptance-and-burn-in.md)). |
| Flavor ratio | Open | Its tolerances are placeholders and the pumps' flow is unmeasured ([acceptance and burn-in](/hardware/assembly/acceptance-and-burn-in.md)). |
| The discharge line between an isolated compressor and a fixed condenser | Open | The compressor rides rubber grommets while the condenser is screwed to the enclosure, and the discharge leg is drawn as one straight run with the condenser's header redressed onto the stub's line ([`_lines.py`](/hardware/manifold-layout/_lines.py), `_refrig_1`). Secop's [field guidance](https://www.secop.com/fileadmin/user_upload/technical-literature/danfoss-lectures/operational_defects_in_hermetic_compressors_and_refrigerating_systems.pdf) gives the discharge line windings to take up compressor motion. The stations are envelope-derived, and the donor's own tube route is the starting point. |
| Condensation | Open | The carbonated-water riser is insulated in two pieces either side of the flow meter ([internal plumbing](/hardware/assembly/internal-plumbing.md)), and the umbilical's foam stops short at both ends ([faucet and umbilical](/hardware/assembly/faucet-and-umbilical.md)). The flow meter, the union and the bare tails can sweat, no condensate path is traced, and the umbilical has no drip loop where it lands beside the signal jack. |
| The faucet display over the sink | Open | No splash or ingress rating exists. The display cover's underside is open over the tubes, its lip sits just above the glass without a gasket, and the module is a bare ESP32-S3 board at the spout ([faucet display cover](/hardware/printed-parts/faucet/faucet-display-cover/README.md)). |
| Faucet display-cover fit on the 27 mm neck | Open | The vent-equipped neck is a constant 27 mm outside diameter. The cover's accepted PET-GF flexing and retention result keeps its recorded scope; assembled clearance, snap fit and appearance on the complete current shell remain physical observations ([cover record](/hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json), [vent print set](/hardware/printed-parts/faucet/vent-print-readiness/README.md)). |
| Noise at night | Open | The compressor's grommet squeeze has no strain basis ([other choices to assess](/hardware/mechanical-qualification/README.md#other-choices-to-assess)), and no sound level is stated for the compressor, the condenser fan or the diaphragm pump's refill runs. |
| Static at the faucet display | Open | The main board clamps and series-resists the faucet's UART lines at its own end; the faucet end's clamps are optional and its 5 V and ground are unclamped, so the display's immunity is unqualified ([faucet and umbilical](/hardware/assembly/faucet-and-umbilical.md)). |
| Cabinet doors shut | Answered | The condenser sheds its heat only while the compressor runs, and the cabinet carries the small average through the gaps it has; the Lillium carbonator under this project's sink has run six months behind closed doors ([enclosure](/hardware/printed-parts/enclosure/README.md)). Ventilation for the R-600a charge is under Standards and claims. |
| Condenser air through the enclosure | Answered | The condenser, fan, shroud and compressor keep the donor ice maker's arrangement, and the flank grilles are pierced more openly than the donor's (Derek's comparison with the donor units). The compressor body in CAD is a clearance envelope, its calipered section run straight through the shell's full height ([`compressor.py`](/hardware/reference/compressor/compressor.py)), so the gap it leaves at the condenser face is packing room, not the air passage ([vents](/hardware/printed-parts/enclosure/enclosure/README.md#the-condensers-vents)). |
| Fingers or rodents through the grilles | Answered | The openings are slots narrower than the 6 mm a mouse needs or the 12 mm test finger ([vents](/hardware/printed-parts/enclosure/enclosure/README.md#the-condensers-vents)). |
| Refill and pour at once | Answered | Firmware blocks a refill during a pour and holds at most three valves on; no hardware backstop exists ([firmware and commissioning](/hardware/assembly/firmware-and-commissioning.md)). |
| Valve-driver heat in a warm cabinet | Answered | The drivers are lower-loss TBD62083 parts ([driver note](/hardware/pcb/pcba/uln2803.md)). |
| Muting the gas alarm | Answered | The gas alarm cannot be muted, and automatic dispensing injects no flavor while it sounds; a held prime can still run a pump motor ([firmware and commissioning](/hardware/assembly/firmware-and-commissioning.md), [`machine.cpp`](/firmware/src_appliance/machine.cpp)). |
| Carbonic-acid backflow into the house supply | Answered | Simply having a 1022 already puts us ahead of most of these products. A 1022 that vents into the bowl at the faucet would be the only home arrangement I've found where the vent's discharge is defined, drained and visible. An ASSE 1022 beverage backflow preventer guards the inlet; its dedicated 4 mm DRAIN line terminates over the bowl near the faucet joint ([safety](/hardware/README.md#safety), [drain assembly](/hardware/assembly/asse-drain.md)). |

## Refill and clean

Concentrate is poured from a 440 mL bottle held upside down over an open funnel, a bottle per
flavor every week or two; the clean cycle runs tap water through the drink paths.

| Concern | Status | Where it stands |
| --- | --- | --- |
| Water and debris from above | Open | The [lift-off funnel cover](/hardware/printed-parts/zone-c/funnel-cover/README.md) places a solid plate over the mouth between fills, with a locating skirt and local silicone friction pads. Installed drip exclusion, retention and cleaning remain physically unqualified. Runoff reaches the surrounding roof; the brim ledge and front/back roof lap remain unsealed, and their water path to the mains splices, compressor relay, C14 inlet and main board is undefined ([assembly facts](/hardware/manifold-layout/enclosure-assembly.facts.json)). Anything entering while the cover is removed, or bypassing it, waits above normally closed V-B until the next fill or dry cycle ([fluid topology](/hardware/topology/fluid-topology.md)); concentrate can remain after an early full-reed stop or a short timed draw. |
| Refill headroom under the bowl | Open | The install guide's [bottle scene](/hardware/install-guide/_install_art.py) (`s_bottle_in_funnel`) upends the bottle with its base about 600 mm above the cabinet floor, as does the quick start's [fill scene](/tools/quickstart-codex/fill_scene.py), and the bottle stays upended until the display says Filled. An 8–10 inch bowl leaves roughly 500–590 mm, and the funnel sits under the bowl, behind the machine's front face. The [install envelope](/marketing/install-envelope.md) lists headroom over the top wall without a figure. |
| One flavor carried into the other | Open | The shared funnel path's flush between flavors is deferred ([fill-from-funnel plan](/hardware/snapshots/fill-from-funnel-plan-2026-08-19.md)). |
| The funnel's push-on drain seal | Open | Wet and dry retention and sealing of the silicone plug on the drain stub are unqualified ([funnel](/hardware/printed-parts/zone-c/funnel/README.md)). |
| Cleaning chemistry | Open | The clean cycle runs tap water only ([`machine_policy.h`](/firmware/lib/machine_policy/machine_policy.h)). No cleaner or sanitizer, concentration, contact time or temperature is chosen or checked against the PETG reservoirs, the ASA float, the valve elastomers and the pump tube. Each reservoir's threaded barrel and nut stand inside the wet cavity ([floor and bulkhead](/hardware/printed-parts/cold-core/reservoir/floor-and-bulkhead.md)), where repeated-fill cleanability is open. |
| Scale at the jet | Open | The ultrafiltration keeps dissolved minerals, and the jet is a 1/16 in drilled hole ([water-inlet jet](/hardware/assembly/water-inlet-jet.md)). No hardness range, inspection or descale step exists. |
| Overpour | Open | The funnel holds a little more than one 440 mL bottle ([funnel](/hardware/printed-parts/zone-c/funnel/README.md)), firmware stops the fill draw at the full reed or a time limit, and the install guide says to stop adding at Full. Where an overpour or a drain-seal leak runs, and what keeps it off the electronics, is not defined. |
| Water filtration | Answered | A Waterdrop 15UC-UF 0.01 µm inline filter upstream, replaced yearly without tools ([BOM](/hardware/ledger/bom.md)). |

## Faults and outages

Valves stick, floats jam, probes come loose, relays weld, power drops mid-cycle, CO2 runs out
and firmware hangs, sometimes while nobody is home.

| Concern | Status | Where it stands |
| --- | --- | --- |
| Water on the cabinet floor | Open | The floor slab sits flat on the cabinet floor with no feet, and its front/back lap is unsealed ([enclosure](/hardware/printed-parts/enclosure/enclosure/README.md)). The MQ-6 is the lowest electrical part, in the floor strip, and the compressor's terminal box hangs a few centimetres up ([assembly facts](/hardware/manifold-layout/enclosure-assembly.facts.json)). Nothing senses floor water. |
| A leak while nobody is home | Open | V-K is downstream of the water bulkhead, ASSE preventer and tee, so it cannot isolate leaks at those fittings or at the external filter and tube. The ASSE vent discharges visibly to the sink through the dedicated DRAIN line; that path does not detect or contain general cabinet leaks ([internal plumbing](/hardware/assembly/internal-plumbing.md), [drain assembly](/hardware/assembly/asse-drain.md)). |
| ASSE vent performance through the faucet drain | Open | The 4 mm OD / 2.5 mm ID vent line rises from the appliance to the faucet. Manufacturer confirmation and a discharge test must establish allowable backpressure, fault-flow capacity and the effect of a water-filled line before release. The outlet stays open; it carries no valve, cap or check valve ([drain assembly](/hardware/assembly/asse-drain.md)). |
| Faucet vent-cavity containment and seal life | Open | Two retained 85A bungs contain the round vent cavity around the continuous beverage tubes and insulated conductors. Native fit and insertion-tool clearance establish the modeled assembly. Wet containment, water migration along the conductors, splash, clogging, cleaning and seal aging require physical qualification of the finished parts ([vent evidence](/hardware/printed-parts/faucet/vent-qualification/README.md), [seal print set](/hardware/printed-parts/faucet/vent-print-readiness/README.md)). |
| Gas interlock polarity | Open | The board's U15 AND gate passes the compressor command only while the MQ-6 comparator output is high, and a pulldown makes a lost signal inhibit ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), U15). The appliance firmware sounds the gas alarm when that same output reads high ([`machine.cpp`](/firmware/src_appliance/machine.cpp), `gasService`). One of the two is inverted, and the fitted module's polarity is unconfirmed on the bench. The gas state shows on neither display while the machine is idle, and a trip clears shortly after the reading does. |
| Pump startup or jam current through the pogo contacts | Open | Contacts are specified for 2 A each. The current PCB grounds U11/U12 ISEN, disabling adjustable DRV8870 current regulation; its fault protection is not a 2 A limit. Normal pump current does not establish startup or jam current, and no installed current/resistance result is recorded ([current protection](/hardware/reference/yyfkgcp-pogo-4p/mounting-audit.md#current-protection), [TI data sheet](https://www.ti.com/lit/ds/symlink/drv8870.pdf)). |
| A welded compressor relay | Open | The compressor's AC goes through a Teyleten module rated 10 A at 250 VAC with no documented motor-load rating ([relay](/hardware/reference/teyleten-relay/README.md)), against a donor locked-rotor current of 5.7 A ([ice maker](/hardware/reference/ice-maker/README.md)). The freeze cutout and the gas interlock both act by opening that relay, so welded contacts leave the compressor running under neither. The thermal cutoff answers overheating only, the donor thermostat is discarded, and the status reports the commanded state. |
| A controller that hangs | Open | The interrupt watchdog and the idle-task watchdog cover some stalls. The loop that drives the valves, pumps and compressor command is not subscribed to a watchdog, and outputs hold their last state; the compressor keeps U15 and the thermal cutoff, while nothing shuts the water and flavor actuators down when the controller stops making progress. |
| A probe that loses contact | Open | Both probes are foil-taped and foamed in ([cold core](/hardware/assembly/cold-core.md)). Firmware rejects absent and corrupt readings, but its staleness guard sees a cached reading re-stamped every second, so a reading that stops updating is not caught ([`cold_policy.h`](/firmware/lib/machine_policy/cold_policy.h), [`onewire.cpp`](/firmware/src_appliance/onewire.cpp)). Nothing compares the wall and suction readings or bounds a continuous run: a loose wall probe reading cabinet air keeps cooling requested, and a loose suction probe reading warm removes the freeze cutout. |
| A reed that fails | Open | The carbonator's two reeds are foamed in under the coil; the reservoir columns can be withdrawn once the core's top cap is lifted, with no procedure ([level sensing](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)). With the low reed dead the carbonator never refills; with the high reed dead, each refill the low reed starts runs to the cumulative pumping limit and latches, and a reboot clears the latch ([`refill_policy.cpp`](/firmware/lib/machine_policy/refill_policy.cpp)). |
| The first fill, and power lost mid-refill | Open | A refill starts only when the low reed closes, and a drained carbonator can read both reeds open. The first-fill control the acceptance procedure expects is not exposed ([acceptance and burn-in](/hardware/assembly/acceptance-and-burn-in.md)), the install guide has no first-fill step, and a reset mid-refill returns to idle ([`refill_policy.cpp`](/firmware/lib/machine_policy/refill_policy.cpp)). |
| A flow meter that keeps pulsing | Open | The pour ceiling resets to idle, and continued pulses start the next pour on the following sample, so a chattering meter re-pours without a latched fault ([`pour_policy.cpp`](/firmware/lib/machine_policy/pour_policy.cpp)). |
| Tap pressure through an idle pump | Open | V-K closes the pump's suction whenever a refill is not running ([fluid topology](/hardware/topology/fluid-topology.md)). Most house supplies stand above the 43.5 psi gas feed ([pressure vessel](/hardware/assembly/pressure-vessel.md)), so V-K's seat alone holds tap water out: a leaking V-K drives water through the idle pump and jet, past CHI where nothing senses the level, until the headspace reaches house pressure. V-K's seat under water hammer and the CO2 check valve's reverse sealing are unverified ([internal plumbing](/hardware/assembly/internal-plumbing.md)); an inlet pressure limit is the conditional change in [Carbonation Plan B](/future/carbonation-plan-b.md). |
| CO2 running out | Open | Nothing in the firmware reads CO2; the machine keeps refilling and pouring flat water, and the only indication is the regulator gauge under the sink ([BOM](/hardware/ledger/bom.md)). |
| A mains dip | Open | The minimum off time covers firmware stops and boots ([`cold_policy.h`](/firmware/lib/machine_policy/cold_policy.h)). A dip that stops the compressor without resetting the board leaves the relay closed, and the compressor can restart without a fresh minimum off time. |
| The thermal cutoff's contact with the compressor cover | Open | The [fuse clamp](/hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py)'s channel is the cutoff's nominal diameter and takes its press from print tolerance, while the SEFUSE case is allowed ±0.2 mm; an undersize case can sit loose and read cabinet air. The case is live, so any added pressure keeps its insulation. |
| Mains and water together | Open | Class I bonding is specified for the carbonator, compressor body and under-counter plate ([regulatory](/business/regulatory.md)), but the under-counter plate's bond has no landing and no conductor ([wiring](/hardware/assembly/wiring.md)), and the production AC fuse is undecided ([AC wiring schedule](/hardware/wiring/ac-wiring-schedule.md)). An integrated GFCI is deferred to [pie-in-the-sky](/future/pie-in-the-sky/gfci.md). |
| An I/O expander that stops answering | Open | A failed write triggers best-effort parking ([appliance firmware](/firmware/src_appliance/README.md)), but a failed bus cannot confirm the outputs cleared, and with the expanders' reset tied high there is no independent reset. |
| Runaway carbonator fill | Answered | Every path is held by normally closed solenoids, V-K gates the carbonator fill ([fluid topology](/hardware/topology/fluid-topology.md)), the high reed stops a refill, and a cumulative pumping timeout latches ([`refill_policy.h`](/firmware/lib/machine_policy/refill_policy.h)). |
| Short-cycling after a firmware stop or a boot | Answered | Minimum off and on times hold the compressor ([`cold_policy.h`](/firmware/lib/machine_policy/cold_policy.h)). |
| Carbonator freeze-up with healthy probes | Answered | A cutout on the suction probe trips and recovers with hysteresis, and an invalid or missing reading parks the compressor ([firmware and commissioning](/hardware/assembly/firmware-and-commissioning.md)). |
| Where the relief valve discharges | Answered | Out of the appliance's west flank through a relief chase, into the sink cabinet ([PRV shroud](/hardware/printed-parts/cold-core/prv-shroud/README.md)). Installed relief capacity through the shroud, tube and chase is unqualified. |
| A power outage | Answered | The fill valve fails closed and the compressor stops; ride-through is a concept in [battery backup](/hardware/battery-backup/README.md). |
| 12 V supply faults | Answered | A reverse-polarity FET, a surge clamp and the supply's own current limit ([PCBA audit](/hardware/snapshots/pcba-audit-2026-07-13.md)). |

## Years under a sink

Plastic creeps beside a warm compressor, gaskets relax, moisture works into the foam, dust
settles on the condenser, and drain cleaners, bleach, aerosols and pests share the cabinet.

| Concern | Status | Where it stands |
| --- | --- | --- |
| Moisture into the foam | Open | No separate vapor barrier is specified; the procedure credits the closed-cell foam itself, inside printed shells and caps ([cold core](/hardware/assembly/cold-core.md)), while the coil runs below freezing inside a thin foam blanket. |
| Dust on the condenser | Open | The finstack sits behind the intake grille, and no cleaning step or interval exists for a machine that is never opened. |
| Drain cleaner, bleach and aerosols | Open | Nothing addresses the PET-GF enclosure's resistance to what is stored under a sink ([BOM](/hardware/ledger/bom.md) §7). The MQ-6 answers to propane and isobutane, the propellants aerosol cans use. |
| The MQ-6 over years | Open | Winsen's [MQ-6 manual](https://www.winsen-sensor.com/d/files/manual/mq-6.pdf) gives 48 h initial conditioning and longer after storage, a 10-year life, and permanent sensitivity loss from silicone vapor. Commissioning allows a short warm-up, and nothing reads the sensor's health or catches a drift toward a false clear. |
| Cycle life of contacts and flexures | Open | The pogo contacts, grips, covers and lever have no cycle result ([accepted physical evidence](/hardware/mechanical-qualification/README.md#accepted-physical-evidence)). |
| Warning labels under heat, moisture and cleaning | Open | A production check is owed ([markings](/hardware/markings/README.md)). |
| Retained clamp force, gasket relaxation, compressor isolation, screw corrosion, insulation thickness, endurance | Open | Each has its current basis and missing evidence in [other choices to assess](/hardware/mechanical-qualification/README.md#other-choices-to-assess). |

## Service and return

The cartridge comes out for a pump swap, the machine is pulled forward for a plumber, and a
unit is boxed and shipped back.

| Concern | Status | Where it stands |
| --- | --- | --- |
| The pump swap as a customer procedure | Open | Simultaneous release of all four collets and support cleanup are unproven ([pump replacement](/hardware/service/pump-replacement.md)). |
| Pump contact closing allowance | Open | Little additional closing remains before the pins' stroke limit at the coupon flushness criterion ([pump cartridge magnetic contacts](/hardware/mechanical-qualification/README.md#pump-cartridge-magnetic-contacts)). |
| Pump tube wear and running dry | Open | The tube is a consumable, and wear from running dry is uncharacterised ([pump replacement](/hardware/service/pump-replacement.md)). |
| Flavor A tube restraint | Open | A long run goes unsupported after its post, and `tube-anchored` in the [assembly scorecard](/hardware/manifold-layout/enclosure-assembly.scorecard.json) leaves one tube loose ([tube shapes](/hardware/manifold-layout/tube-shapes.md)). |
| Shipping a unit back | Open | No customer drain or depressurization procedure exists for a return, and the pump swap leaves the carbonator charged ([pump replacement](/hardware/service/pump-replacement.md)); refrigerant work on a returned unit needs flammable-rated recovery ([refrigerant loop](/hardware/assembly/refrigerant-loop.md)). |
| Who the owner calls | Open | No support contact is configured ([install guide](/hardware/install-guide/README.md)). |
| Draining before a swap | Open | The dry cycle runs from Settings → Pump Service through the installed pumps ([appliance firmware](/firmware/src_appliance/README.md)); a pump that has failed cannot run it, and no branch covers removing a dead head ([pump replacement](/hardware/service/pump-replacement.md)). |
| What can be serviced | Answered | One operation, the pump swap; every other fault is answered by shipping a replacement ([design pressures](/hardware/design-pressures.md)). |
| Pulling the cartridge | Answered | The fixed plate carries the removal reaction, braced by a hand, a foot or the machine's own weight ([design pressures](/hardware/design-pressures.md)). |
| Zip-tied pump tube joints | Answered | The tie is treated as load-bearing and each joint is tug-tested ([pump replacement](/hardware/service/pump-replacement.md)). |
| Replacing the thermal cutoff | Answered | At the factory it slides out along its clamp channel ([SF76E](/hardware/reference/sf76e-thermal-fuse/README.md)); the customer's only service is the pump swap. |

## What the drink touches

Water, concentrate and carbonated water wet every material between the inlet and the glass.

| Concern | Status | Where it stands |
| --- | --- | --- |
| Carbonated water through the faucet valve | Open | The soda enters the donor Westbrass at its lower compression port, through a brass stiffener inside the tube, and rises through the valve body and past its poppet seat before LLDPE carries it to the tip ([faucet and umbilical](/hardware/assembly/faucet-and-umbilical.md), [BOM](/hardware/ledger/bom.md)). The FDA Food Code, a model code for retail food service, bars copper alloys such as brass from contact with food below pH 6 and from fittings between a backflow preventer and a carbonator ([§4-101.14](https://www.fda.gov/media/184685/download)); carbonated water is carbonic acid. What applies to a household appliance is not established here. [Touch-Flo](/hardware/reference/touch-flo-faucet/README.md) calls the wet path LLDPE end to end, and [faucet shell material](/hardware/printed-parts/faucet/faucet-shell/MATERIAL.md) includes the donor metal body. |
| The ASA Aero float | Open | One ASA body sits directly in the carbonator and both reservoirs ([all-ASA float](/hardware/printed-parts/cold-core/magnetic-float/all-aero/README.md)), and Bambu's [ASA Aero guide](https://wiki.bambulab.com/en/filament-acc/filament/asa-aero-printing-guide) says it is not food-contact grade. Pressure life and liquid compatibility are unqualified. |
| Migration and cleanability of the printed reservoirs | Open | Migration and sensory-taint screening is planned ([wetted-surface test](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md)); finished food contact and repeated-fill cleanability have no recorded acceptance. |
| Glass fiber in contact with concentrate | Answered | The reservoir bodies and lids are PETG Translucent; PET-GF is the core's shells and caps around them ([cold core](/hardware/assembly/cold-core.md)). |

## Standards and claims

What the machine is built to, what its labels say, and what has not been tested against them.

| Concern | Status | Where it stands |
| --- | --- | --- |
| The 60335 safety tests | Open | Not performed, and the donor's results do not transfer to the custom evaporator and enclosure ([regulatory](/business/regulatory.md), [markings](/hardware/markings/README.md)). |
| The donor terminal cover as a fire enclosure | Open | Its qualification is owed before a 60335 fire-enclosure claim ([regulatory](/business/regulatory.md)). |
| Ventilation and clearance for the R-600a charge | Open | [Regulatory](/business/regulatory.md) records the installation instructions' ventilation and clearance requirements as still owed. |
| The carbonator's pressure rating | Open | No rating exists; the hydro is a proof test ([pressure vessel](/hardware/assembly/pressure-vessel.md)). |
| The rating label | Open | The install guide's current and power figures are unverified, and the label's values come from the build record ([markings](/hardware/markings/README.md), [finish, pack and ship](/hardware/assembly/finish-pack-ship.md)). |
| Food-contact posture | Open | The reservoir test and the silicone notes credit a food-contact posture to [regulatory](/business/regulatory.md), which has no such section ([wetted-surface test](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md)). |
| Radio emissions, Prop 65 and lead-free rules for potable-water parts | Open | Not addressed in [regulatory](/business/regulatory.md). |
| R-600a end use and charge | Answered | Household refrigeration under SNAP and UL 60335-2-24 second edition, whose limit is 150 g per circuit, is the project's reasoned classification rather than an EPA determination; the expected charge sits well under that limit ([regulatory](/business/regulatory.md)). |
| Listing and federal duties | Answered | No UL or ETL listing is held or sought, the CPSC's general duty applies, and the AIM Act does not ([regulatory](/business/regulatory.md)). |
