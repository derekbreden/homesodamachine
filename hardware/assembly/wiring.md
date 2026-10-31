# Wiring

The procedure for executing every electrical run in the appliance — chassis ground bonds, AC mains, the cabinet-side [12 V](DC_BUS_V) branches, and signal looms. The schedule of runs is [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md); this doc is the build-order procedure for executing that schedule. Each end lands at the stage of the build where it can be reached, and the runs are finished through the funnel opening once the box is closed.

The routed groups above the cold-core lid carry [16 AWG](AWG_AC_MAIN) mains, [12 V](DC_BUS_V) power, and [22 AWG](AWG_DC_BRANCH) signal in close proximity. Topology lives in [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd), [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd), and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd). Every low-voltage run lands on a labeled edge connector of the main board ([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), the canonical pin map) or on a relay module's terminals.

The field harnesses are **not** wired in place conductor-by-conductor — they are **pre-fabricated as cable assemblies** on the bench (cut-to-length all-black silicone, ferruled/crimped, black-braided-sleeved, continuity-tested), then landed here. The fabrication procedure is [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md); a failed harness is swapped as a whole assembly, never repaired conductor-by-conductor. Wire is all-black throughout **except the AC mains** (black hot / white neutral / green ground — a safety convention, not a service aid).

The PCB lies flat on the cold-core lid. The PSU mounts base-up in back-top’s shallow ceiling recess and both relays mount to its dry west wall, and the meter travels on its east-wall carriers. Back-top's rear ceiling is continuous, so every end beneath it lands while back-top is open on the bench. Once the box is closed, the only way in is the funnel opening with the frame out, and the ends that lie under the opening are landed through it. The frame drops in after [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md), whose USB console and test points lie beneath it; it carries no wiring. The [installed routing review](/hardware/wiring/installed/above-core-review/README.md) records the nominal conductor paths and its remaining evidence limits.

## Scope

In: the enclosure pieces and cold core at the bench stages of [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md), [`electronics-bay.md`](/hardware/assembly/electronics-bay.md) and [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md), unpowered; the compressor bolted down to the enclosure floor on its four posts with the donor's moulded cover securely retained over its terminal block and PTC module, its factory-external electrical interface accessible without disturbing the cover; condenser + fan standing east of it on the shell's own tangent. The bagged faucet-and-umbilical sub-assembly (output of [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)) arrives with its completed RJ11 plug. Connect it to the rear keystone for end-to-end testing. This procedure terminates only the inboard SIG-6 loom, from J3 to the keystone's 110 IDC; the umbilical cable stays intact.

Wire stock and small parts: the pre-fabricated cable assemblies from [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) — one labeled loom per board connector (J1–J7, J9, J11, J13), each ending in a JST XH [2.5 mm](JST_PITCH) housing at the main board end; [16 AWG](AWG_AC_MAIN) silicone hookup wire for the ground bonds (green); [16 AWG](AWG_AC_BRANCH_U) solid black/white UL1007 for fixed AC-1/2/3, DC-1/2/4 and the two AC join pigtails, per the wiring schedule's conductor-construction table; [18 AWG](COMP_LEAD_AWG) SJOOW 3-conductor jacketed cable for the compressor lead; ferrules sized for [16/22 AWG](AWG_TRIPLE); ring terminals for the ground stack + the compressor's terminal-box earth screw; female-disconnect (Faston) terminals for the diaphragm pump, valves, and condenser fan; the current donor compressor's factory-external connector is Open item 1; black PET braided sleeve + zip ties for bundling; Wago 221 lever nuts for the device-end fan-outs (221-420 at MANIFOLD A, 221-415 at MANIFOLD B, 221-413 at the sensor commons, power row and the three joins under the funnel opening).

Out: every run in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) executed and continuity-tested. AC runs AC-1 through AC-6 landed, with the C14 ground pin bonded to the central chassis-ground point and onward to the two specified metal destinations (carbonator, compressor body). The current donor's connector is Open item 1. DC runs DC-1 through DC-9 landed. The inboard SIG-6 loom lands from J3 to the rear keystone; the other signal runs are landed at both ends. SIG-7 (4.3" enclosure display) is a [~400 mm](SIG_DISPLAY_LEN) internal run from the main board to the front face; SIG-6 (1.47" faucet display, direct TTL UART) rides the umbilical up to the above-counter faucet, while SIG-4 (flow meter) is a short internal run above the core. Both static AC checks pass.

Not in scope: applying [120 VAC](AC_LINE_V); flashing firmware; bringing up the [12 V](DC_BUS_V) rail; any sensor probe-into-water service — see [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md). Mounting the PSU, relays, PCB, junctions and ground boss — see [`electronics-bay.md`](/hardware/assembly/electronics-bay.md). The compressor terminal block's clip-on PTC start relay / overload module and moulded cover are donor-side subassemblies preserved during teardown ([`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) "Powering and control"). The cover stays installed: the appliance lead terminates at the donor assembly's factory-external electrical interface.

## Inputs per appliance

Wire stock, connectors, and termination consumables are in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 — that one section carries all of it: the 16 AWG AC + ground stock, the 22 AWG DC/signal stock, the Wago 221 lever nuts, the spade and ring terminals, the ferrules, the heat-shrink, and the braided sleeve. The AC hardware the runs land *on* is §5 (C14 inlet, line cord, the GEARit SJOOW compressor lead, the thermal fuse). Status in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md). The runs themselves are in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) §"Run table".

Tooling: ratcheting crimper for insulated and uninsulated terminals + ferrules + Faston disconnects + JST XH (one tool covers all four with the appropriate die per terminal family); wire strippers sized for [16/22 AWG](AWG_TRIPLE); small flat screwdriver for Wago 221 levers and the relay screw terminals; soldering iron and solder for the C14 tabs and the meter's lead joints; PEX-style sidecutters for trimming; a hot-glue gun for strain relief at intermediate tie points where the run crosses a printed-part edge; cable-tie tensioner (optional); multimeter for the continuity checks at step 3.

## Procedure

Each conductor's end lands at the first stage where the end is reachable, and the runs are finished through the funnel opening once the box is closed. Within each stage, runs follow the run-number order of [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md). The static AC check comes in two parts: one on the open back-top, and one in the closed box before any power.

### Where each end lands

| Stage | When | Ends landed |
|---|---|---|
| Front-bottom, open on the bench | [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §3, before front-top slides on | The compressor end of the SJOOW lead: SF76E splice, donor interface, and the AC-6 ring on the can's earth screw. Both fan leads: J2's `FAN` leg and its positive branch. The J11 loom's MQ-6 end. |
| Front-top, open on the bench | [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3, before front-top slides on | J1 and J2 at the front coils V-C through V-J, and their `COM` feeds in front-top's 221-420 and 221-415 |
| Back-top, open on the bench | [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §1–§2 and [`electronics-bay.md`](/hardware/assembly/electronics-bay.md) steps 2–3 | AC-1, AC-2 and AC-3, complete. The back-top ends of DC-1, DC-2, the three join pigtails, the PE bus and J5. J3 at the keystone. The V-A and V-K legs at their blades. The meter's leads. |
| Cold core, open on its cart | [`cold-core.md`](/hardware/assembly/cold-core.md) and [`electronics-bay.md`](/hardware/assembly/electronics-bay.md) steps 1 and 4 | J10 on the loose PCB and into the V12/GND WAGOs. J4's temperature conductors, J6 and J7. The pump negative in the GND WAGO, and the pump positive dressed to the opening. V-B's leg at its blades. The carbonator bond; its ring connects to the prepared rear-wall star before back-top closes. |
| Through the funnel opening | box closed, frame out ([`electronics-bay.md`](/hardware/assembly/electronics-bay.md) step 5) | Every board housing not yet seated, with its loose contacts. The free ends of DC-1 and DC-2 in the V12/GND WAGOs. The front-top positives. The three joins. |

Dress each free end so it lies within the funnel opening's footprint once the box is closed, clear of the seams, the rails and every surface that slides. Label each free end with its run ID while it waits.

For board service, remove the funnel and frame, release the three free joins
and move them with their leads aside before lifting J1/J2. Disconnect the
V-B-to-Y-B return and cradled drain before J11 withdrawal. The
[current native housing paths](/hardware/mechanical-qualification/enclosure-above-core/connector-service-review.json)
use 17 mm up then 8 mm fore for J1/J2, and 6 mm up, 10 mm east, then
20 mm up for J11; the Reservoir B draw stays installed.

### 1. Chassis-ground bonds (single-point ground on the rear wall)

Chassis grounding is via discrete green wires from the exposed metal parts back to one ring-terminal stack at world (−48.15, 461.7, 313.935) mm on back-top below C14. The separate carbonator lead and rear PE-bus pigtail are [16 AWG](AWG_AC_MAIN) green-insulated, with rings at their screw landings. The compressor's AC-6 bond is the green [18 AWG](COMP_LEAD_AWG) core of its jacketed power lead.

Bond, from each target to the stack:

- **Carbonator** — crimp a closed M3 / #4 ring onto the green 16 AWG lead and clamp it directly to bare steel on the existing upper vessel rim, using [the rim attachment and clamp sequence](/hardware/assembly/pressure-vessel.md#upper-rim-earth-bond). Fit the steel-side clamp before foil and the body pour. Bring the free wire into the shared west-side seven-core `sensor-cable` passage at world X−48/Y347, thread both cap pieces, follow its R5.5 transition to the X−78/Y320 lid exit, then crimp its outside ring for the rear-wall star.
- **Compressor body** — ring terminal under the compressor's own earth screw at its terminal box, landed with front-bottom open ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §3). **Not under a floor screw.** The compressor stands on four rubber grommets and the posts under them are printed PET-GF, so a ring on one of those heads reaches rubber and plastic and touches no compressor metal at all. The earth screw is on the can. **This is the machine's only bond to the refrigeration metalwork**, and it is run AC-6 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md): the G conductor of the same jacketed lead that carries AC-4 and AC-5 to the donor assembly's factory-external electrical interface, so the bond arrives with the power it protects.

The stack is bonded to the C14 inlet's earth pin through AC-1's green conductor (C14 earth → rear PE WAGO) and the PE-bus pigtail (rear PE WAGO → stack).

Prepare the green bond leads from the allocated stock and trim after dressing
all three branches to the relocated star. Keep the carbonator lead's outside
end free until it has passed through the shared cap guide. The short AC-1
earth pigtail from C14 to the rear WAGO has its own cut.

Fasten the star on open back-top, before the rear assembly closes over the core.
The carbonator bond takes the west-facing lug, the inlet PE bus the
east-facing lug and AC-6 the downward/east-facing lug; the flat washer and
M3 × 8 close the stack ([`electronics-bay.md`](/hardware/assembly/electronics-bay.md)
step 4). Dress the rear PE feed, compressor lead and short carbonator bond
as three distinct branches, retaining their final straight crimp entries.

Check each bond from its metal to its free ring before that metal is closed in: the carbonator's before the body pour, the compressor's with front-bottom open. Record a low-resistance bond measurement rather than relying only on a continuity beeper; subtract the test-lead resistance. After the stack is fastened, check C14's earth pin to each ring's exposed metal and to the compressor body. The carbonator's steel-side clamp is already buried at this stage, so retain its pre-pour steel-to-free-ring reading with the assembly record. These assembly readings do not replace the appliance's protective-bond qualification.

### 2. AC mains (C14 → distribution → relay #1 → compressor + PSU)

AC-1, AC-2 and AC-3 lie wholly on back-top and are landed while it is open on the bench ([`electronics-bay.md`](/hardware/assembly/electronics-bay.md) step 3). AC-1 lands the rear C14 inlet directly on the AC distribution block; there is no device in series — ground-fault protection is deferred, see [/future/pie-in-the-sky/gfci.md](/future/pie-in-the-sky/gfci.md). AC-1 is [~150 mm](AC1_LEN) of solid black hot, white neutral and green earth, soldered to the inlet's tab pins at the C14 end and stripped bare into the Wago block at the distribution end; H, N, and G land directly on the block. AC-2 (distribution block → PSU primary) is [~200 mm](AC2_LEN), solid black hot and white neutral directly in the WAGO and PSU screw cages. The encapsulated Class II PSU has no earth terminal; exposed metalwork bonds to the separate stack. AC-3 is the hot-pickup leg from the H block into relay #1's contact common.

Land the two AC join pigtails at the same time: [~300 mm](JOIN_LEN) of solid black from relay #1's NO terminal and the same of solid white from the rear N WAGO's free port. Dress both forward along the west wall to the funnel opening.

Compressor lead (AC-4 + AC-5 + AC-6): stage a single [18 AWG](COMP_LEAD_AWG) SJOOW 3-conductor lead from [~700 mm](COMP_LEAD_LEN) preparation stock, carrying switched H, N and PE. Land its compressor end at [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §3 with front-bottom open. Switched H reaches the dressed SF76E lead splice and then the verified hot side of the donor's factory-external interface; N reaches its verified neutral side; PE takes a ring at the compressor's terminal-box earth screw. Preserve the donor cover and factory lead exit. The exact current-donor connector and polarity mapping remain Open item 1. The shared jacket rises through the front floor opening and valve-bank gap and ends at about X48/Y165.76/Z274.77, under the funnel opening; its three insulated cores wait there in the front column.

After the box closes, through the opening: the PE core's ring goes on the stack (step 1); then switched H and N each join their back-top pigtail in a WAGO 221-413, the cores ferruled. Dress and retain the jacket and its three fanouts along the [installed model](/hardware/wiring/README.md), then trim. The preparation stock covers the core's modeled path through to relay #1, 606.306 mm main plus a separate 36.777 mm fuse continuation; each core ends at its join, short of that path.

Color discipline (AC only): [16 AWG](AWG_AC_MAIN) solid on AC-1/2/3 and the two pigtails and stranded silicone on the separate earth bonds, black for hot, white for neutral, green for ground. DC and signal wire is all-black (cut-to-length, per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)) — color is reserved for the mains as a safety convention.

### 3. Static AC checks

Two cold checks, multimeter only, with the C14 inlet **disconnected from line**. The AC path runs C14 inlet → AC distribution block directly (AC-1). Ground-fault protection is deferred — see [/future/pie-in-the-sky/gfci.md](/future/pie-in-the-sky/gfci.md).

**On the open back-top**, once AC-1 to AC-3 and both AC pigtails are landed:

- **Continuity (ohms-low):** C14 earth pin to the rear PE WAGO and the PE-bus ring. C14 hot pin to the H block, relay #1 common and PSU L. C14 neutral pin to the N block, PSU N and the free end of the neutral pigtail.
- **Open (ohms-high):** C14 hot to C14 neutral; each of them to C14 earth; relay #1 common to the free end of the NO pigtail, with the relay at rest.

**In the closed box, before the joins:**

- **Winding (ohms):** across the free ends of the SJOOW's switched-H and N cores, through the SF76E and the donor interface. Confirm ~[10](WINDING_R_LOW)–[30 Ω](WINDING_R_HIGH) for a [100 W](COMP_CLASS_W) hermetic, matching the donor compressor's nameplate.
- **Open (ohms-high):** each core end to the PE core's ring.

**In the closed box, after the joins and the stack:**

- **Continuity (ohms-low):** C14 earth pin to the stack and to every bond landed in step 1. C14 neutral pin to the H join's test slot: the compressor winding again, through the N join.
- **Open (ohms-high):** C14 hot to C14 neutral, relay #1 at rest; C14 hot and C14 neutral each to C14 earth; each join's test slot to C14 earth.

Relay #1's switching is proven under firmware at [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) step 8. If any check fails, find and fix it before going on.

### 4. Cabinet-side [12 V](DC_BUS_V) runs (DC-3, DC-5 through DC-9)

The power runs DC-1, DC-2 and DC-4 land per [`electronics-bay.md`](/hardware/assembly/electronics-bay.md): DC-1's PSU end and DC-2's relay end on the open back-top, DC-4 on the open core, and the free ends of DC-1 and DC-2 in the core-lid V12/GND WAGOs through the funnel opening. The cabinet-side runs land in schedule order:

- **DC-3** (relay #2 contact output → G Ganen diaphragm pump) — two pieces joined under the funnel opening. The relay pigtail, [~300 mm](JOIN_LEN) with a ferrule in relay #2's NO cage, is landed on the open back-top; the pump positive, the same length with a female disconnect on the pump's lead, is landed on the open core. Both are dressed to the opening and joined in a WAGO 221-413 after the box closes. The pump negative lands in the core-lid DC GND WAGO on the open core.
- **DC-5** (PUMPS J13 → Kamoer pump A / pump B) — one 500 mm 22 AWG 4P ribbon, landed with front-top loose ([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3). Thread the bare pump end forward through the shared rear electrical mouth and out underneath before crimping four Fastons. Ring out the harness, land the Fastons on the loose pumps, then raise the prepared pumps and lower retainer motor-first into the integral upper mount while drawing slack aft. The pairs lie in the transverse terminal channel; the joined ribbon crosses the common rear passage below SIG-7, then runs below the funnel frame, west of the Y-B stem elbow and over the J6 leads to J13. The conductor order is `AM2`, `AM1`, `BM2`, `BM1` from +X to −X; the +X pair serves pump A and the −X pair pump B ([`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md#pump-leads--dc-5)). Keep the ribbon bare and its unused preparation reserve relaxed behind the common mouth. Seat J13 through the funnel opening after closure, and unplug it by its housing before separating enclosure pieces.
- **DC-6** (MANIFOLD A J1 → 8 solenoid coils) — a **black sleeved trunk**: 9 conductors of 22 AWG black (8 OUT + COM), cut-to-length and carried in 3/4" braided sleeve per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md). On the open front-top it lands at the six front coils V-C through V-H, each OUT on a female disconnect at its valve, and its COM in the manifold's 221-420 lever nut, which fans the [12 V](DC_BUS_V) to every valve's other tab. Its two other legs land on their own pieces, their XH contacts crimped but out of the housing: `OUT1` and positive-A on V-A's blades on the open back-top, `OUT2` and positive-B on V-B's blades on the open core. After the box closes, the `OUT1` and `OUT2` contacts seat in J1 cavities 2 and 3 before the housing goes on its wafer, and positives A and B take their 221-420 ports. Valve ↔ OUT mapping per [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd).
- **DC-7** (MANIFOLD B J2 → 2 solenoid coils) — same pattern on the J2 trunk, 5 of its 6 ways populated (2 OUT + FAN + COM + `OUT3`). On the open front-top, `OUT1` and `OUT2` land at V-I and V-J and `COM` in the 221-415. The FAN conductor is DC-8, `OUT3` is DC-9, and `OUT4` is a spare board channel left unpopulated.
- **DC-9** (MANIFOLD B J2 `OUT3` + a `COM` tap → V-K) — the water-supply fill/shutoff coil seats in back-top’s east sidewall mount. On the open back-top, land `OUT3` and V-K's positive on its blades, `OUT3`'s XH contact crimped but out of the housing, and dress both forward to the opening, clear of the pump, meter and soda fittings. After the box closes, `OUT3` seats in J2 cavity 4 and the positive in the 221-415. Low-side switching like every manifold valve: `OUT3` sinks V-K's − through the on-board TBD62083 #2 (MCP23017 0x21 PA5), and + taps the shared `COM` at the manifold's fan-out, the way the fan's does. V-K stops water reaching the carbonator on a leak alarm or a power loss.
- **DC-8** (condenser fan) — the fan's + ties to the manifold's COM fan-out; the J2 `FAN` conductor sinks the − side through the on-board TBD62083 #2 channel 5 (MCP23017 0x21 PA3 commands it), flyback through the driver's integrated diode to COM. Land both fan leads with female Fastons at the fan with front-bottom open ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §3), `FAN`'s XH contact crimped but out of the housing; their free ends wait in the front column. Dress the pair together along the east wall and seat both leads in front-top’s integral fan hook above the condenser, with the paired leg below the hook clear of the sliding seam. The `FAN` conductor is cut from [~650 mm](FAN_RUN_LEN) stock. After the box closes, `FAN` seats in J2 cavity 2 and the positive in the 221-415.

### 5. Signal looms (SIG-1 through SIG-4, SIG-6 through SIG-12)

Execute the SIG runs from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Sensors and signal", one pre-fabricated loom per board connector. Every board end is a JST XH [2.5 mm](JST_PITCH) housing seated on its labeled wafer — J4 and J7 share the same 7P housing, so land each by its loom label ([`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)); a swap would put J4's 3V3/V5 on J7's reed inputs. J4, J6 and J7 seat on the open core; the others seat through the funnel opening once the box is closed.

- **SENSORS J4 loom** — three runs share it, GND split at the core-lid sensor WAGO. **SIG-1**: the 1-wire temperature bus (`IO26` + `3V3` + GND), [22 AWG](AWG_DC_BRANCH), [~650 mm](SIG_ONEWIRE_LEN) to the back of the cold core — a DS18B20 (carbonator-wall, family 0x28) and a DS18S20 (evap-suction, family 0x10) bussed in parallel and told apart in firmware by family code; the [4.7 kΩ](PULLUP_R) data pull-up is on the main board (R9), nothing in the loom. Probes land at the cold core's exit per [`cold-core.md`](/hardware/assembly/cold-core.md). Seat J4 on the open core with cavities 4 and 5 empty. **SIG-4**: the DIGITEN flow meter (`IO25` + `V5` + GND) on back-top, on edge between the pump and east gas group with fore–aft ports and its lead root downward. On the open back-top, solder J4's flow pair and the sensor-GND branch to the meter's three factory leads and heat-shrink each joint; dress them below V-K's coil, east ahead of the foam and forward to the opening. After the box closes, the `V5` and `IO25` contacts seat in J4 cavities 5 and 4, and the GND ferrule takes the sensor WAGO's third port. **SIG-9**: J4 `IO23` and `IO27` are reserved and unpopulated. The visible faucet drain is observed directly.
- **REEDS A J6 loom** — **SIG-10**: reservoir A's 4 level reeds + shared GND, [22 AWG](AWG_SIGNAL), [~650 mm](SIG_REEDS_A_LEN) up reservoir A's own reed channel and out the cap's `reed-cable-a` conduit; GND runs continuously from J6 alongside the four signal wires, with insulated local taps at the reeds. The reeds ride the on-board MCP23017 internal pull-ups (INPUT_PULLUP, magnet pulls LOW) — no resistors in the loom. Seat the five leads in the integral lid hook beside the PSU, with GND, RA4, RA3, RA2 and RA1 from bottom to top. The shared low run leads aft into the reservoir's cap passage.
- **REEDS B J7 loom** — three runs share it, GND branches in a three-port 221-413 at the cold-core end, with one common wire per reed column. **SIG-2/SIG-3**: the carbonator low/high reeds (`CLO` / `CHI`). **SIG-11**: reservoir B's 4 reeds (`RB1`–`RB4`). Same internal-pull-up pattern.
- **FAUCET J3 loom** — **SIG-6**: direct TTL UART to the gooseneck-mounted ESP32-S3-Touch-LCD-1.47 faucet display. **The run crosses the +Y wall of back-top and the loom is only its inboard half**: XH housing on J3 at one end, 110 IDC on the back of the RiteAV CAT3 USOC keystone at X−64/Z291.5 at the other ([`../printed-parts/enclosure/y-wall-of-back-top/README.md`](/hardware/printed-parts/enclosure/y-wall-of-back-top/README.md)). Punch it down on the open back-top; its housing seats at J3 once the box is closed. Outboard of the jack the BNTECHGO ribbon runs [~2 m](SIG_UMBILICAL_LEN) down the umbilical on its completed plug. Punch down **J3 pin 3/V5 → jack 2 (white/orange label), J3 pin 4/GND → jack 3 (blue), J3 pin 2/IO35 RX → jack 4 (white/blue), J3 pin 1/IO33 TX → jack 5 (orange)**. Leave jack 1 and 6 open. All conductors are black; the colors name the jack's printed USOC labels. The [faucet guide's page 15](https://homesodamachine.com/read/faucet-assembly-guide/faucet-assembly-guide.pdf#page=15) shows the oriented plug and punchdown slots, and [`cable-assemblies.md#faucet-display-sig-6`](/hardware/assembly/cable-assemblies.md#faucet-display-sig-6) gives the complete mapping. Neither half carries components: the series damping + ESD clamps are on the main board ([`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) "Faucet-display ESD protection").
- **DISPLAY J9 loom** — **SIG-7**: the RS485 link + power to the ESP32-S3-Touch-LCD-4.3B enclosure display (`B` / `A` / GND / `V12`). The A/B pair lands on the 4.3B's onboard SP3485 terminals; `V12` + GND feed its 7–36 V screw input. With front-top loose and the facet open, feed the display end through the same rear electrical mouth as DC-5, above the pump ribbon, and up the chimney into the display pocket. Keep its ribbon bare inside the printed channels and finish the PET braid aft of the common mouth. Land the screw terminals with the display out, then seat it ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §8). Its housing seats at J9 through the funnel opening after closure.
- **GAS J11 loom** — **SIG-12**: the MQ-6 combustible-gas sensor low in the refrigeration bay, in the two floor posts down its -X strip beside the compressor (`GND` / `V5` / `DOUT` / `AOUT`). The sensor board's header faces EAST, out of the strip and into the bay the front assembly opens onto, so the loom lands on it from the room and runs aft up the -X flank. Seat its four bare conductors together in the integral hook on front-bottom’s solid lower west-wall band, with the cable clear of the ventilation openings. Land it with front-bottom open ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §3); its housing waits in the front column. Once the box is closed, seat it at J11 before the V-B return union and its flexible tube go in ([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md)); the return lies over J11. Its 0–5 V outputs are divided to ESP-safe levels on the main board (R1–R4), so the loom is a plain sensor cable. This loom also feeds the on-board gas→compressor interlock (U15): the compressor relay cannot energize until it is landed and the sensor warmed.

Continuity-test each signal run end-to-end before zip-tying down.

### 6. Bundle, route, and strain-relieve

Bundle by zone:

- **Core bundle** — the J4 temperature loom, the J6 + J7 reed looms (SIG-1/2/3/10/11) and the carbonator's chassis-ground bond, from the shared seven-core west riser, reservoir A's straight cap passage and reservoir B's shell-rim outlet to the PCB, the lid WAGOs and the rear-wall star ([`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) for the reed columns).
- **Back-top bundle** — the ends landed on the open back-top: DC-1, DC-2, the three join pigtails, the PE bus, J5, the V-A and V-K legs and the meter's leads, dressed along back-top's west and east walls to the funnel opening. J3 stays at the keystone until its housing seats.
- **Manifold bundle** — the J1 + J2 manifold trunks (DC-6/DC-7/DC-8) from the front coils toward the main board, carried in the front column until their housings seat. Braided-sleeve and zip tie; fan-out happens at the manifold.
- **Compressor bundle** — the [18 AWG](COMP_LEAD_AWG) SJOOW jacketed lead from step 2 is its own bundle, up the fore floor lane; zip-tie tie-down points only.
- **Front-face bundle** — J13 DC-5 and J9 SIG-7 share one rear electrical mouth at front-top's centreline. DC-5 occupies the lower lane and splits through the transverse channel into the two motor terminal rooms; SIG-7 occupies the upper lane and rises into the display pocket. Both ribbons stay bare within the print. SIG-7's PET braid ends aft of the mouth. Dress the free reserve below the funnel frame, clear of the manifold Wagos, tube approaches and enclosure joints.
- **Gas bundle** — the J11 GAS loom from the MQ-6 aft up the −X flank.
- **Manifold-to-fan branch** — DC-8 leaves the J2 trunk at the manifold and runs alone along the side wall to the condenser fan; female Fastons at the fan.

Provide strain relief at the funnel opening's edge, the cold-core penetrations, the manifold entry and the umbilical keystone. DC-5's reserve, drawn aft through the shared electrical mouth during motor-first pump installation, lies below the funnel frame. Retain the compressor lead at its shared jacket and along the three insulated upper fanouts; keep pull from reaching the terminal landings and joins. Use existing printed-part features. Cable-tie anchors are placed below the cable.

## Output condition

A wired but unenergized chassis:

- The two chassis-ground bonds (carbonator, compressor body) and the inlet PE bus land at the single ring stack on back-top below C14; the stack is bonded to the C14 inlet's earth pin.
- All AC runs (AC-1 through AC-6) executed and continuity-tested, the compressor's switched H and N through their joins; both static AC checks (step 3) pass
- The compressor's donor moulded cover is intact, unmodified, and securely retained over the terminal/PTC assembly; the appliance lead terminates only at the factory-external electrical interface and the factory lead exit is undamaged
- All DC runs (DC-1 through DC-9) in place — the [12 V](DC_BUS_V) path is contiguous from PSU output to every load, the pump through its join and the fan on the low-side-switched DC-8 branch
- The main board's J1, J2, J3, J4, J5, J6, J7, J9, J11, and J13 looms seated on their labeled wafers, every loose contact seated, and landed at their devices; J10 landed
- SIG-7 (4.3" enclosure-display run) seated at J9 and landed at the enclosure display
- SIG-6's inboard J3 loom landed on the rear keystone; the separate faucet-and-umbilical assembly retains its finished RJ11 plug
- Wire bundles are black-braided-sleeved or zip-tied by zone, with strain relief at every transition
- The funnel frame still out, so commissioning reaches J14 and the test points through the opening
- The chassis is safe to apply [120 VAC](AC_LINE_V) but no power has been applied

The chassis is the input to [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md).

## Open items

1. **The current donor compressor's external electrical interface is not recorded.** Unit A establishes a black/white pigtail pattern for that donor only. The current BOM uses Frigidaire Unit B, whose external lead colors, connector family, polarity mapping, and retained harness length remain pending teardown. Preserve Unit B's donor-side termination at harvest, identify it at the bench, and specify a recognized mating connector or splice for AC-4/5 in the schedule and BOM. Do not inherit Unit A's wire-color assumptions; direct access to the terminal block under the cover is not the fallback.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_wiring_sync.py`
