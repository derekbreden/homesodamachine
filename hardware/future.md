This file describes the appliance, subsystem by subsystem. It is the design narrative — the place to understand what the machine is, and the doorway into the companion docs and part directories that specify it. It does not carry the specifics; it points at where each one lives.

The appliance is an integrated under-counter machine. It packs the carbonator, its refrigeration loop, both flavor reservoirs, the pumps and valves, and the electronics into one enclosure behind a single 120 VAC cord, with the tap-water inlet at the rear and the CO2 cylinder standing beside the appliance on a short tether. The prototype under the counter has proven the dispense path — two flavors of Pepsi-made concentrate injected into cold carbonated water, press the lever and soda comes out. What this build adds is the cold carbonated water itself: the machine carbonates and refrigerates its own. What stays above the counter is a faucet and a small display; the rest is under the sink.

Read the machine from its cold center outward and from its back wall forward. A **cold core** sits against the back of the enclosure — a stainless carbonator vessel, an evaporator coil wound around it, and the two flavor reservoirs nested in foam around it, where they pre-chill. Forward of the core are the compressor and the pumps and valves; above it, the electronics; the flavor funnel. The carbonated-water line runs straight up through the countertop to the faucet. The sections below take the cold core **inside out** and the enclosure **back to front**.

This is the hardware narrative — one dimension of the project. The folder map and the part-metadata convention are in [`/hardware/README.md`](/hardware/README.md); the CAD idioms its generators follow are in [`touch_flo_shell.md`](/hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.md) and [`cadlib/`](/hardware/printed-parts/cadlib/); point-in-time history is frozen in [`/hardware/snapshots/`](/hardware/snapshots/).

**Carbonation.**

The carbonator is a custom 316L stainless vessel standing vertically, with four NPT ports. CO2 enters through an internal sparge stone and dissolves as the bubbles rise; filtered tap water is pumped in against the CO2 back-pressure; carbonated water leaves from the bottom; a pressure-relief valve guards the top. Carbonation is set by the CO2 supply pressure. The water level inside is read without piercing the vessel — a magnet rides on an internal rod and external reed switches see it through the wall.

Vessel fabrication, the hydro-test, the passivation, and the working pressure are in [`/hardware/assembly/pressure-vessel.md`](/hardware/assembly/pressure-vessel.md), with the end-cap cut parts in [`/hardware/cut-parts/carbonation/`](/hardware/cut-parts/carbonation/). The full water and CO2 plumbing — every fitting, the check valves, the beverage backflow preventer, the two-stage CO2 regulation and its setpoint — is in [`/hardware/assembly/cold-core.md`](/hardware/assembly/cold-core.md) and the valve-and-fluid topology in [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md). The parts themselves, and their order status, are in [`/hardware/ledger/`](/hardware/ledger/).

**Refrigeration.**

The cold comes from a refrigeration loop harvested from a countertop ice maker — its compressor, condenser, fan, capillary tube, and drier kept in service, with a copper coil wound around the carbonator vessel doing the evaporator's work. Firmware cycles the compressor against temperatures read at the tank wall and the coil, with a freeze cutout. The refrigerant is a natural hydrocarbon, vented and recharged through a permanent service valve.

The teardown, the recharge and its charge mass, and the brazing safety are in [`/hardware/assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md); the donor units and the keep-or-discard plan in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md); the coil winding in [`/hardware/printed-parts/cold-core/coil-mandrel/`](/hardware/printed-parts/cold-core/coil-mandrel/). The refrigerant's regulatory standing is in [`/business/regulatory.md`](/business/regulatory.md).

**Cold core (inside out).**

Read it inside out: the carbonator vessel; the evaporator coil bonded to its outside; an inner printed shell foamed against the coil; the two flavor reservoirs nested in that foam, where they pre-chill in the gradient between the near-freezing core and the cabinet air; an outer printed shell, foamed again. The reservoirs are vented printed parts, not pressure vessels — sized for a refill of concentrate, and level-sensed the same way the carbonator is.

The layered build is in [`/hardware/assembly/cold-core.md`](/hardware/assembly/cold-core.md). The shells and the pour-in-place foam are in [`/hardware/printed-parts/cold-core/foam-shell/`](/hardware/printed-parts/cold-core/foam-shell/), with [`foam-cap/`](/hardware/printed-parts/cold-core/foam-cap/) and [`foam-assembly/`](/hardware/printed-parts/cold-core/foam-assembly/). The reservoirs — their floor and bulkhead, their filtered vent, their reed-and-float level column, their watertight printing — are in [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/). The relief-valve shroud is in [`prv-shroud/`](/hardware/printed-parts/cold-core/prv-shroud/).

**Flavor.**

Two peristaltic pumps draw flavor from the chilled reservoirs and inject it at the dispense nozzle alongside the carbonated water; each flavor is primed and valve-locked between pours. The pumps run forward only, and a valve manifold selects the fill, dispense, and clean-in-place paths. Each reservoir fills from a hopper on top for pouring concentrate. The clean cycle runs in software.

The canonical valve-state truth table, with the manifold and tray diagrams beside it, is in [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md). The manifold's printed trays are in [`/hardware/printed-parts/valve-manifold/`](/hardware/printed-parts/valve-manifold/); the pumps in [`/hardware/printed-parts/flavor/`](/hardware/printed-parts/flavor/); the hopper and the pump access beneath it in [`/hardware/printed-parts/zone-c/`](/hardware/printed-parts/zone-c/). The reservoir level-sensing pattern is in [`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md).

**Enclosure (back to front).**

The enclosure sits in the cabinet beneath the sink. Read it back to front: the cold core fills the back-bottom against the rear wall; the electronics ride above it at the back-top; the flavor funnel and pumps stack under a single front-top door; the compressor, condenser, and water-inlet plumbing cluster occupy the front-bottom. The condenser fan blows straight across the cabinet — intake grille on one side face, exhaust on the other. The cabinet prints as two telescoping halves that register on a corner joint and screw shut from the side faces. The rear face lands the water inlet, the AC cord, and the umbilical that carries the three lines up to the faucet; the front face carries the customer surfaces and no machinery.

The zone layout, which is flexible, is in [`/hardware/printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md). The split-printable box and its joint are in [`enclosure/`](/hardware/printed-parts/enclosure/enclosure/), the packed assembly in [`enclosure-assembly/`](/hardware/printed-parts/enclosure/enclosure-assembly/). The rear connections are in [`back-panel/`](/hardware/printed-parts/enclosure/back-panel/), the front surfaces in [`front-panel/`](/hardware/printed-parts/enclosure/front-panel/), the serialized plaque in [`nameplate/`](/hardware/printed-parts/enclosure/nameplate/). The mechanical assembly of the whole is in [`/hardware/assembly/enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md).

**Electronics and power.**

A single 120 VAC cord enters the rear panel. A 12 V supply makes the low-voltage bus that runs the diaphragm pump, the peristaltic pumps, the solenoid valves, the condenser fan, the displays, and the sensors; the logic rails are made on-board. The compressor switches on the AC side; the fan and the 12 V loads switch low-side, firmware-gated. The ESP32 controller, the motor and valve drivers, and the AC and DC distribution mount on printed trays in the back-top zone.

The trays — the power, controller, and driver groups — are in [`/hardware/printed-parts/electronics/`](/hardware/printed-parts/electronics/). The run-by-run AC schedule is in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md), and the power, pinout, and valve-control topology in [`/hardware/wiring/`](/hardware/wiring/). The bench build of the electronics, and the wiring procedure that follows it, are in [`/hardware/assembly/electronics-shelf.md`](/hardware/assembly/electronics-shelf.md) and [`/hardware/assembly/wiring.md`](/hardware/assembly/wiring.md). The controller PCB — a through-hole carrier the modules plug into — is in [`/hardware/pcb/`](/hardware/pcb/).

**Safety.**

Three hazards are designed around independently. The hydrocarbon refrigerant is contained by a sheet-metal shroud over the only ignition-risk parts, and watched by a gas sensor low in the cabinet. The carbonic-acid backflow path is held by a beverage backflow preventer whose vent weeps to a sensed drip pan as the mechanical telltale. The plumbed appliance's mains and ground-fault posture, the refrigerant charge limits, and the unit markings are consolidated in one place.

The whole safety and regulatory posture is in [`/business/regulatory.md`](/business/regulatory.md). The compressor shroud is in [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md); the refrigerant-handling and brazing safety in [`/hardware/assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) under "Safety". An integrated ground-fault (GFCI) module is a deferred desire, captured in [`/pie-in-the-sky/gfci.md`](/pie-in-the-sky/gfci.md).

**User-facing surfaces.**

Above the counter, a faucet lever pours, and a small touch display on the dispense head shows the selected flavor and switches it by touch. On the appliance's front face, a larger touchscreen is the configuration surface, beside a front-dispense spout that pours without the faucet installed. Flavor is refilled by opening the cabinet door — lift the hopper's silicone funnel and the pumps are beneath it.

The faucet stack — shell, mounting plate, gasket, o-ring — is in [`/hardware/printed-parts/faucet/`](/hardware/printed-parts/faucet/), over the cut [`under-counter plate`](/hardware/cut-parts/faucet/). The displays' reference geometry is in [`/hardware/reference/waveshare-43b-display/`](/hardware/reference/waveshare-43b-display/) and [`/hardware/reference/touch-flo-faucet/`](/hardware/reference/touch-flo-faucet/); the front-face layout in [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md); the hopper and pump access in [`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md). The behavior these surfaces drive is firmware — [`/firmware/`](/firmware/).

**Build order.**

The sequence the whole appliance is built in — vessel, cold core, refrigerant loop, internal plumbing, electronics, wiring, enclosure, faucet and umbilical, commissioning, burn-in, pack and ship — is the run of procedure docs in [`/hardware/assembly/`](/hardware/assembly/), with the skilled-hand tasks summarized in [`handwork.md`](/hardware/assembly/handwork.md).
