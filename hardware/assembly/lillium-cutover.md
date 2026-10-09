# Lillium cutover

The printed enclosure goes under the sink fed by the Lillium: two flavors, two pumps, the
white faucet, and the flow meter that starts each pour. The Lillium makes the cold carbonated
water; this build adds no carbonator, refrigeration, CO2 or tap-water feed.

The flavor manifold carries the eight valves front-top holds, V-C through V-J, and all six
tees. V-A (tap water) and V-B (funnel) stand on the cold-core cap, which this build leaves out.
V-A's tee port takes a plug and V-B's takes a dip tube, so a bottle refills a reservoir through
the firmware's own Fill. When tap water and the funnel come in, V-A goes onto the plugged port
and V-B and the funnel onto the dip-tube line; nothing inside front-top changes. The Lillium's
own filtered tap-water outlet ([plumbing](/docs/plumbing.md#water-supply)) can feed V-A then.

**In this build:** front-top with V-C–V-J, Y-A–Y-G and the tee carrier; the pump cartridge with
both KPHM600s; both reservoirs in the foam shell with their caps, gaskets, floats and reed looms;
the DIGITEN meter; the main board, the enclosure display and the faucet display; the white
Sculpted faucet; the C14 inlet and the IRM-90-12ST supply. The printed parts are the ones in
[the prototype record](/hardware/printed-parts/enclosure/lillium-prototype-2026-10-07/README.md)
with the [current back top](/hardware/printed-parts/drain-readiness/prints/2026-10-08-current-back-top-mark1/README.md).

**Left out:** V-A, V-B and the foam cap they stand on; the funnel and its drain elbow; V-K and
the clean cycle; the carbonator, refrigeration loop and condenser fan; the CO2 path; the
temperature probes and the gas sensor; the ASSE 1022 and the DRAIN line.

## Soda water

Lillium's cold carbonated outlet → blue 1/4" LLDPE → the TAP bulkhead → blue run inside to the
DIGITEN meter's inlet collet → `carb-2` → the blue-ringed SODA bulkhead → the blue umbilical
tube to the faucet.

- The Lillium's outlets are 1/4" push-connect, and TAP is a 1/4" PP1208E bulkhead
  ([rear wall](/hardware/printed-parts/enclosure/y-wall-of-back-top/README.md)).
- The meter hangs in its two roof anchors, one 6" zip tie each, with its arrow toward SODA
  ([internal plumbing §4](internal-plumbing.md#4-risers-up-to-the-umbilical-bulkheads-on-the-y-wall)).
- TAP → meter is the one run with no model. TAP stands west of SODA on the top row and the meter
  hangs by SODA's column, so cut this run on the parts, across the empty water deck, with bends no
  tighter than R14 and clear of the electronics bay. `carb-2` keeps its modeled run.
- Sleeve both inside runs in the CARGEN foam. The line is cold and the cabinet is not.
- The faucet goes together per [faucet and umbilical](faucet-and-umbilical.md) with the blue
  tube, both flavor tubes and the faucet display's ribbon. There is no DRAIN tube.

## Flavor manifold

Build front-top on the bench per
[internal plumbing §3](internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps)
steps 1–3, all eight valves and all six tees. Then:

- **Y-A port 1**, V-A's: one John Guest PI0808S 1/4" stem plug
  ([B003NUUKL8](https://www.amazon.com/dp/B003NUUKL8), 10-pack).
- **Y-B port 1**, V-B's: the dip tube. Black 1/4" LLDPE from the port up through the funnel
  frame's drain hole and out of the funnel opening, long enough to reach the bottom of a bottle
  standing beside the machine. Between fills, its end rests up in the funnel opening.
- **The reservoir runs** go straight to the reservoirs: V-F → reservoir A's fill bore, reservoir
  A's draw → V-E, V-I → reservoir B's fill bore, reservoir B's draw → V-H. A draw leaves its
  floor bulkhead through the foam shell's lane
  ([foam shell](/hardware/printed-parts/cold-core/foam-shell/README.md)).
- **The risers:** V-G → one FLAVOR bulkhead, V-J → the other.
- The pump cartridge goes in after the box closes (§3 step 4).

Cuts, black 1/4" LLDPE unless noted:

| Run | Joins | Cut |
|---|---|---|
| fluid-6, 7, 8 | the Y-A–Y-B crossbar; Y-A → V-C; Y-B → V-D | butts: both insertion depths, no exposed tube |
| fluid-9, 19 | V-C → Y-C; V-D → Y-F | the inner hairpin ([the fold](/hardware/manifold-layout/README.md#the-fold)) |
| fluid-17, 27 | Y-D → V-G; Y-G → V-J | the outer hairpin (the same) |
| fluid-10, 13, 20, 23 | the four bowed stubs | fit at the bench (§3 step 3) |
| fluid-11, 12, 21, 22 | the pump tubes | set at the cartridge (§3) |
| fluid-18, 28 | V-G, V-J → the FLAVOR bulkheads | the run's developed length in [the assembly facts](/hardware/manifold-layout/enclosure-assembly.facts.json) |
| fluid-14, 16, 24, 26 | the reservoir fills and draws | at the bench: the modeled runs end at the foam cap's conduits, and these continue to the reservoirs |
| dip tube | Y-B port 1 → bottle | at the bench |
| soda, inside | TAP → meter | at the bench, blue |
| `carb-2` | meter → SODA | its developed length in the assembly facts, blue |

## Wiring

| Board | This build |
|---|---|
| J10 | 12 V from the IRM-90-12ST, fed from the C14 by AC-1 and AC-2 ([AC schedule](/hardware/wiring/ac-wiring-schedule.md)). AC-3 to AC-6, the compressor's, are not built. |
| J1 MANIFOLD A | The complete harness ([cable assemblies](cable-assemblies.md)). OUT3–OUT8 to V-C–V-H; OUT1 (V-A) and OUT2 (V-B) folded back and labeled. |
| J2 MANIFOLD B | OUT1 to V-I, OUT2 to V-J. OUT3 (V-K) and FAN folded back and labeled. |
| J13 | Both pumps, through the cartridge's contact pair. |
| J6, J7 | Reservoir A's and B's reeds. J7's CLO and CHI unconnected. |
| J4 | The meter on SIG-4: IO25, V5, GND ([wiring](wiring.md)). No 1-wire probes. |
| J9 | The enclosure display. |
| J3 | The faucet display, through the RJ11 keystone (SIG-6). |
| J5, J11 | Nothing: no relay loads, no gas sensor. |

## What the firmware does here

The main board runs `b79be4d54` or later. Nothing is configured for this build.

- **Pour.** Flow at the meter opens the selected flavor's pair, V-E/V-G or V-H/V-J, and bursts its
  pump into the stream.
- **Prime.** A held Prime opens the pair, then runs the pump. On first use, hold each flavor until
  syrup reaches the faucet.
- **Fill.** Dip tube to the bottom of a 440 mL bottle, then Fill A or B on the machine display. The
  pump draws the bottle into that reservoir and then air through the line, and stops at 80 s or
  at the reservoir's full reed. A reservoir's usable window holds two bottles, so one bottle into a
  reservoir at half or lower cannot overflow it, with or without calibrated reeds. Refill one
  flavor at a time and let each fill draw its bottle empty, so air follows the syrup through the
  line the two flavors share ([concerns](/hardware/concerns.md), "One flavor carried into the
  other").
- **Dry**, Settings → Pump service: the dip tube out of the bottle, in air.
- **Clean** is not for this build. With V-A's port plugged no water comes in, and its flush step
  pumps the reservoir out through the faucet.
- With no probes the cold loop reports a fault and asks for nothing. With no gas sensor the alarm
  input reads clear. Neither stops a pour.

## Before guests use it

1. **Water first.** Fill both reservoirs with water through the dip tube and leave them a few hours
   over a towel. The current reservoir prints have no water result
   ([concerns](/hardware/concerns.md), "Reservoir watertightness").
2. **Pump current.** Read one pump's startup and stall current with the multimeter in series on a
   motor lead. The cartridge contacts are rated 2 A each, and nothing on the board limits motor
   current below that ([concerns](/hardware/concerns.md), "Pump startup or jam current through the
   pogo contacts").
3. **The first glass.** Leave it idle overnight, then pour each flavor without priming.
4. Keep the old prototype's pumps, controller, faucet and labeled lines together until that
   passes.
