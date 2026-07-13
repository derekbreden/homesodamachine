# JLCPCB parts inventory

Parts confirmed in the JLCPCB assembly library, and where each was found. This is the
shared parts reference — separate from BOM/CPL generation: the board carries footprints,
this carries the JLCPCB/LCSC identity each maps to. Stock and price are point-in-time
(date each row). Add rows as steps convert modules.

## Finding a part

- JLCPCB will assemble a part only if it resolves at `jlcpcb.com/partdetail/<slug>/<C#>`
  (the slug is ignored; the `C#` is canonical). The badge under the part name reads
  **Basic**, **Promotional Extended**, or **Extended**. Basic carries no per-part feeder
  fee; Extended adds a feeder/setup fee per unique part and must be in stock.
- An LCSC catalog number (`lcsc.com`) existing does **not** mean JLCPCB stocks it for
  assembly. Verify the JLCPCB partdetail resolves. `C72518` (ROQANG RVT1E471M1010,
  470µF/25V) is on LCSC but its JLCPCB partdetail redirects to `/parts` — not in the
  assembly library. The JLCPCB-library equivalents carry different `C#`s (e.g. `C3351`).
- Search the library: `jlcpcb.com/parts` → search `value package` (e.g. `470uF 25V SMD`)
  → the componentSearch grid; filter Parts Type and In-stock; read MFR Part #, LCSC #,
  library type, stock, price.
- Footprint into tscircuit: standard chip passives use the built-in footprinter names
  (`0603`, `0805`), which match the JLCPCB part. For THT or odd parts the generic footprint
  can mismatch the supplier's land pattern — `tsci build` prints a copper-IoU warning — so
  pull the real one with `tsci import <C#>` and use it (see C3 → `imports/`).
- Wire a part onto the board with `supplierPartNumbers={{ jlcpcb: ["C#"] }}` on the
  component; that is what flows into the JLCPCB BOM/CPL.

## Inventory

| Board use | Value | Package | LCSC | Library | Stock (2026-06-27) | Unit |
|---|---|---|---|---|---|---|
| R1, R3 — gas divider, top leg | 2.2 kΩ ±1% | 0603 | C4190 | Basic | 2,358,134 | $0.0019 |
| R2, R4 — gas divider, bottom leg | 3.3 kΩ ±1% | 0603 | C22978 | Basic | 1,028,999 | $0.0023 |
| C1, C2 — V12 HF decouple | 0.1 µF 50V X7R | 0805 | C49678 | Basic | 8,182,736 | $0.0136 |
| C3 — V12 bulk | 470 µF 25V | radial THT, D10×12.5, 5.08 mm | C350206 | Extended | 91 | $0.105 |
| U4, U5 — valve/fan sink drivers | ULN2803A, 8-ch Darlington | SOIC-18 (300 mil) | C845537 | Extended | 350,244 | $0.089 |
| U2, U3 — I²C GPIO expanders | MCP23017, 16-bit | SOIC-28 (300 mil) | C47023 | Extended | — | — |
| U8 — alarm/tone buzzer | MLT-5020, passive magnetic (external drive), 4 kHz/75 dB, ~100 mA | SMD 5×5 mm | C94598 | Extended | 104,490 | $0.434 |
| Q1 — U8 low-side driver | S8050 (J3Y), NPN 25 V/500 mA | SOT-23 | C2146 | Basic | 554,300 | $0.015 |
| R5 — Q1 base | 1 kΩ ±1% | 0603 | C21190 | Basic | 6,282,722 | $0.0023 |
| U6 — RTC | DS3231SN, TCXO RTC (±2 ppm) | SOIC-16 (300 mil) | C9866 | Extended | 335 | $6.14 |
| BT1 — RTC backup | CR2032 coin base, 2-pin THT (horizontal) | THT plugin ~25×23 mm | C5365915 | Extended | 11,888 (2026-06-30) | $0.135 |
| U7 — RS485 to display | COS13487EESA-3.3, auto-direction transceiver, 3.3 V | SOP-8 (= SOIC-8) | C51949447 | Extended | 530 (2026-07-03) | $0.55 |
| D1 — RS485 line ESD | SM712, RS485 TVS array (−7/+12 V) | SOT-23 | C12067 | Extended | 35,585 | $0.41 |
| R6 — RS485 termination | 120 Ω ±1% | 0603 | C22787 | Basic | 1,728,584 | $0.0022 |
| U9 — 5V→3V3 LDO | AMS1117-3.3, fixed 3.3 V LDO | SOT-223 | C6186 | Basic | 1,843,633 (2026-07-02) | $0.1979 |
| U10 — 12V→5V buck | K7805-2000R3, 2 A non-isolated switcher | SIP-3 (THT) | C18212380 | Extended | — | — |
| U11, U12 — pump H-bridges | DRV8870DDAR, single H-bridge, 45 V / 3.6 A, 565 mΩ | HSOP-8-EP (PowerPAD) | C86590 | Extended | 34,907 (2026-07-02) | $0.41 |
| C13/C15/C17/C19 — buck/LDO/driver decouple | 10 µF 25V X5R | 0805 | C15850 | Basic | (see C11) | $0.01 |
| C14, C16 — 3V3 LDO / 5V buck output | 22 µF 25V X5R | 0805 | C45783 | Basic | — | $0.02 |
| C18/C20 — driver VM HF | 0.1 µF 50V X7R | 0805 | C49678 | Basic | (see C1/C2) | $0.0136 |
| D2 — fault LED (red) | KT-0603R, 0603 | 0603 | C2286 | Extended | — | — |
| D3, D5, D6 — status/rail LEDs (green) | KT-0603G, 0603 | 0603 | C12624 | Extended | 325,847 (2026-07-02) | $0.0121 |
| D4 — activity LED (blue) | KT-0603B, 0603 | 0603 | C2288 | Extended | 178,594 (2026-07-02) | $0.0102 |
| U1 — base controller | ESP32-WROOM-32E-N4, no radio | SMD module 18×25.5 mm | C701341 | Extended | 22,002 (2026-06-28) | $3.77 |
| R7, R8 — EN / IO0 pull-ups | 10 kΩ ±1% | 0603 | C25804 | Basic | 3,845,978 | $0.0013 |
| C10 — ESP 3V3 decouple | 0.1 µF 50V X7R | 0805 | C49678 | Basic | (see C1/C2) | $0.0136 |
| C11 — ESP 3V3 bulk | 10 µF 25V X5R | 0805 | C15850 | Basic | (see C8) | $0.01 |
| C12 — EN power-on RC | 1 µF 50V X5R | 0603 | C15849 | Basic | 6,521,627 | $0.036 |
| J3, J5, J8, J9, J11, J13 — 4-pin (FAUCET, RELAYS, I2C, DISPLAY, GAS, PUMPS) | XH2.54 4P | wafer, 2.5 mm | C5359632 | Extended | 39,475 (2026-06-30) | $0.0116 |
| J6 — 5-pin (REEDS A) | XH2.54 5P | wafer, 2.5 mm | C5359633 | Extended | 14,791 | $0.0294 |
| J2, J4 — 6-pin (MANIFOLD B, SENSORS) | XH2.54 6P | wafer, 2.5 mm | C5359634 | Extended | 42,550 | $0.0254 |
| J7 — 7-pin (REEDS B), **keyed EH** | JST-EH 7P (B7B-EH-A), 2.5 mm | wafer, 2.5 mm | C160254 | Extended | 12,140 (2026-07-13) | $0.0395 |
| J1 — 9-pin (MANIFOLD A) | XH2.54 9P | wafer, 2.5 mm | C5359637 | Extended | 380 (2026-06-30) | $0.0400 |
| J10 — 12 V inlet | KF301-5.0-2P screw terminal, 2P 5.0 mm, 17 A / 250 V, 14–22 AWG | THT block, 5.0 mm pitch | C474881 | Extended | 165,152 (2026-07-02) | $0.0995 |
| Q4 — reverse-polarity pass FET | AO3407 P-ch, −30 V, **±20 V Vgs**, ~60 mΩ | SOT-23 | C181093 | Extended | 176,290 (2026-07-13) | $0.03 |
| D8 — 12 V inlet surge clamp | SMAJ15A, 400 W uni TVS, 15 V standoff / 24.4 V clamp | SMA (DO-214AC) | C571368 | Extended | 2,440 (2026-07-13) | $0.038 |
| D9 — Q4 Vgs clamp | BZT52C15 (MDD), 15 V / 0.5 W Zener | SOD-123 | C173427 | Extended | 182,800 (2026-07-13) | $0.016 |
| R23 — Q4 gate pulldown | 100 kΩ ±1% | 0402 | C60491 | Basic | 3,594,500 (2026-07-13) | $0.0005 |
| U15 — gas→compressor interlock | 74LVC1G08GW, single 2-input AND gate | SOT-353 (SC-70-5) | C12512 | Extended | 1,263 (2026-07-13) | $0.045 |
| R24 — interlock B-node pulldown | 100 kΩ ±1% | 0402 | C60491 | Basic | (see R23) | $0.0005 |
| R25 — DOUT invert-select link | 0 Ω jumper | 0402 | C17168 | Basic | 18,421,967 (2026-07-13) | $0.0003 |
| C23 — U15 VCC decouple | 0.1 µF 50V X7R | 0402 | C1525 | Basic | 54,323,629 (2026-07-13) | $0.0018 |

Manufacturers: C4190 / C22978 / C21190 = UNI-ROYAL 0603WAF series; C49678 = YAGEO
CC0805KRX7R9BB104; C845537 = UMW (Youtai) ULN2803A; C47023 = Microchip MCP23017-E/SO;
C94598 = Jiangsu Huaneng MLT-5020; C2146 = JSCJ S8050 J3Y; C474881 = Cixi Kefa Elec
KF301-5.0-2P screw terminal; XH2.54 connectors = XUNPU WAFER-XH2.54-{n}PZZ, one vendor
across the four XH pin counts used (4/5/6/9P), vertical THT. J7 (7-pin REEDS B) is a keyed
JST-EH (B7B-EH-A, C160254), not XH — see the keying note below.

**U7 is `C51949447` (COSINE COS13487EESA-3.3), a native-3.3 V auto-direction RS-485
transceiver** — a MAX13487E-equivalent whose datasheet pin map (1 RO, 2 /RE, 3 /SHDN,
4 DI, 5 GND, 6 A, 7 B, 8 VCC) the board wires directly: /RE→GND (always receive), /SHDN→VCC
(always on), and the driver auto-enables on TX off the DI pin — so there is no host DE/RE
line and no ESP GPIO is spent on direction (the pin budget is why an auto-direction part is
required, not a plain DE/RE one). Single-3.3 V supply keeps RO's swing safe for the input-only
IO34; ±15 kV ESD, −7..+12 V common-mode (matches the SM712 clamp). SOP-8 lands on the generic
`soic8` footprint (1.27 mm pitch, so the /RE and /SHDN plane-stitch vias clear — a 0.5 mm-pitch
SOT would collide them). Extended, and stock runs shallow (~530 at 2026-07-03) — a COSINE
second-source, so glance at stock and consider a genuine TI THVD1426DR (`C5215921`, SOIC-8,
same pinout) if a run needs deeper supply than COSINE carries.

**The XH2.54 connectors use per-count imported footprints (XUNPU WAFER-XH2.54-{n}PZZ).** The
`Jst` helper places the tsci-imported footprint for each count (`./imports/WAFER_XH2_54_{n}PZZ`),
so the CPL rotation matches JLCPCB's library and the 3D wafer body seats on the pads (the old
generic `pinrow` placed the body mis-rotated). These mate with the standard female XH housings
the wiring kits use. Every XH2.54 part is Extended (no Basic option); the 9P `C5359637` runs
lower stock (~380 at 2026-06-30 vs tens of thousands for the rest) — the lone MANIFOLD A
connector, fine for a build, glance at it before a large run.

**JLCPCB's footprints for this "series" are NOT uniform** — the thing that made the connector
orientations look random before the import. Two axes vary by count, and the `Jst` helper
carries a lookup for each (see `parts.tsx`): the mating OPENING faces +Y at rot 0 for
3/4/9P but −Y for 5/6/7P (`WAFER_OPEN`); and PIN 1 sits at the west end for all but the 7P,
which numbers from the east (`WAFER_PIN1_WEST`). The caller gives an ordinary numeric `rot` in a
UNIFORM convention (0 = opening faces north, CCW); the helper offsets it by `WAFER_OPEN` so `rot`
means the same thing for every count — the wafer's real pcbRotation absorbs the intrinsic opening —
and reverses the label list wherever the pin order flips, so every net keeps the same physical pin
and every IC→connector fan stays uncrossed. Pin order on the looms is not depended on anywhere (the board drives the field), so the
reversals are free. The hole PITCH is a uniform 2.5 mm across the series (`WAFER_PITCH` = 2.5 for
every count): the "2.54" in the part name is the nominal series name, not the drawn pitch — the
XUNPU spec lists 2.5 mm (LCSC C5359632: "Pitch 2.5 mm", "X-Length of Bottom Edge on Board 12.5 mm"
for the 4P, i.e. 2.5 mm of plastic past each outer pin, `XH_END` in `component-bodies.ts`).

**J7 (REEDS B) is a keyed JST-EH, not XH.** J4 (SENSORS) and J7 are both 7-pin on the same
2.5 mm grid, so as XH they are cross-mateable — and a loom swap would drive SENSORS' 5V/3V3 rails
into the MCP reed inputs. J7 carries only dry-reed signals, so it takes a JST-EH housing
(B7B-EH-A, `C160254`): the same single-row 2.5 mm hole grid, but an EH housing cannot mate an XH
loom (or vice versa) — the swap is now mechanically impossible. The `Jst` helper carries an EH
branch (`series="EH"`, `EH_*` lookups in `parts.tsx`); the EH footprint numbers pin 1 from the
WEST (opposite the XH 7P), so `EH_PIN1_WEST[7]=true` keeps every reed net on the barrel it used as
XH — a body/footprint/silk swap with no reroute. Top-entry B7B-EH-A (the side-entry S7B-EH is out
of stock at JLCPCB); it has no STEP model on the tscircuit CDN, so J7 alone is absent from the 3D
preview — its footprint (pads + courtyard + silk) and the fab output are complete.

**J10 is a KF301-5.0-2P screw terminal (`C474881`), not an XH wafer.** The 12 V inlet
carries the whole board — both pumps priming + a few valves + the condenser fan ≈ 3.3 A
peak — and the XUNPU XH wafer contact is rated 2 A (LCSC C5359632, "Current Rating 2A"), so
it was the one connector running well over its rating. The KF301 is a 5.0 mm-pitch 2-pole block rated 17 A / 250 V, 14–22 AWG (Cixi
Kefa Elec): real margin, and it lands the 16–18 AWG power feed on a screw instead of a
crimp. Extended (every screw terminal in the library is), deep stock (165k at 2026-07-02,
$0.0995/1+); wave-soldered THT, so it rides the same through-hole assembly the XH wafers +
coin base already require (no new process, no JLCPCB assembly-difficulty flag).
Footprint pulled with `tsci import C474881` (→ `imports/KF301_5_0_2P.tsx`), then its auto
ref-des was stripped so the label block is hand-drawn, all reading bottom-to-top (the
east-edge convention): the `GND`/`V12` pin labels (0.8 mm) sit OUTBOARD east of the throats
where the wires land, `12V` (1.4 mm function label) + the ref-des in the strip west of the
body. It sits at the south end of the east edge (below MANIFOLD B), placed `pcbRotation={90}`
so the wire throats face the east board edge — the loom feeds in from outside — with pin1 → GND
on the south pad, pin2 → V12 on the north, the polarity silked at each screw. The V12 barrel now
lands on `net.V12IN` (the raw inlet), upstream of the Q4 reverse-polarity block below — so a
reversed loom no longer cooks the polarised bulk cap (C3), the K7805, or the DRV8870s.

**Q4/D8/D9/R23 — J10 reverse-polarity + surge block.** The incoming 12 V passes through a
P-channel high-side pass FET (**Q4, AO3407, `C181093`, SOT-23**) before it reaches the V12 island,
in the slot west of J10 (C5 east → J10 body). DRAIN → `net.V12IN` (the J10 barrel, via a wide
1.6 mm top stub carrying the ~3.3 A board peak), SOURCE → the V12 island (the island floods the
source pad directly — the source→island tie is pour copper, not a trace). A P-channel body diode
points **drain→source**, so with drain=input / source=load it conducts input→load in normal
polarity (channel enhancing, Vgs ≈ −12 V within the **±20 V** rating — an AO3401A's ±12 V would be
marginal) and BLOCKS load→input under reverse polarity, body diode reverse-biased: the board sees
no current. **R23 (100 kΩ 0402, `C60491`, Basic)** pulls the gate to GND so an unplugged/loose
terminal can't float it. **D9 (BZT52C15 15 V Zener, `C173427`, SOD-123)** clamps Vgs (cathode→
source, anode→gate) short of the ±20 V gate-oxide limit. **D8 (SMAJ15A, `C571368`, SMA)** clamps
the surge the board sees, island→GND at the inlet: 15 V standoff (no leakage on the 12 V rail),
24.4 V clamp under C3's 25 V rating. Q4/D8/D9 have no tscircuit CDN 3D model (absent from the 3D
preview only); footprints (pads + courtyard + silk) and the fab output are complete. Q4's SOT-23
sits a touch tighter than IPC-Nominal against C5/J10 (courtyard advisory ~−0.08 mm; copper clears
at the 0.15 mm floor). D8's `C571368` runs shallow at JLCPCB (~2,440) — glance before a large run.

**U15/R24/R25/C23 — gas→compressor interlock.** A firmware-independent AND gate on the compressor
relay line: **U15 (74LVC1G08GW, `C12512`, SOT-353)** takes the ESP compressor command on A (← IO19)
and the divided MQ-6 DOUT on B, and only its output Y reaches the relay (→ J5.IO19), so a gas trip
opens the compressor in hardware even if firmware is hung (Y = A·B). B defaults LOW through **R24
(100 kΩ 0402, `C60491`, Basic)** at the gate pad, so a broken B-haul, an unpowered ESP, or a gate
with no VCC all fail safe (relay OFF). Two polarities wait on bench truth: **R25 (0 Ω 0402, `C17168`,
Basic)** is the invert-select link in series from the DOUT node (default pass-through); and the
pin-identical **74LVC1G00 NAND (`C12508`, same SOT-353 land)** drops in for an active-LOW relay
module with no layout change. **C23 (0.1 µF 0402, `C1525`, Basic)** decouples VCC. U15 has no
tscircuit CDN 3D model (footprint + fab output complete); `C12512` is Extended and ran ~1,263 at
JLCPCB (2026-07-13) — glance before a large run, or the NAND `C12508` if depleted. The interlock
seats E of the WROOM on the old IO19→J5 corridor, so A/Y are the two halves of an already-clean
haul; only B is a new run, around the module's SE and up the east flank (a 0.15 mm U6 nudge opened
the flank for it — see the pcba.tsx GAS block). No relay-side firmware change: the ESP still drives
IO19, the gate just vetoes it on gas.

**U4/U5 are `C845537`** (UMW ULN2803A, SOP-18-300mil wide body). No Basic ULN2803 SOIC
exists in the library — every ULN2803 part is Extended — so the feeder fee is unavoidable;
C845537 is the cheapest with deep stock (genuine-TI ULN2803ADWR is `C9683`, ~$4.40). The
generic `soic18_w7.5mm_p1.27mm` footprint matches the 300-mil land pattern (no IoU warning),
so no `tsci import`. Pins 1-8 IN1-IN8, 9 GND, 10 COM (12 V flyback common), 11-18 OUT8-OUT1.

**C3 is wired as a THT radial — `C350206`** (SamYoung NXB, D10×12.5 mm, 5.08 mm pitch,
53 mΩ ESR / 1.36 A ripple / 4000 h @105 °C), placed by JLCPCB through-hole assembly; its
barrel stitches to V12/GND directly (no SMD via). Footprint pulled with `tsci import` to
match the part's pads — the generic `radial_p5.08mm` matched at only IoU 0.55 → `imports/`.

THT because the need (V12 bulk decoupling) has no Basic SMD option: both 470 µF/25V and
100 µF/25V SMD are **Extended only** across the whole library (Rubycon / Panasonic / Nichicon
included). Extended SMD alternatives, for a full-reflow board: `C3351` (Honor RVT1E471M1010,
$0.060), `C47023111` (D8×L10, $0.050), `C3445246` (90 mΩ / 5000 h, $0.091); or a Basic MLCC
bank (several 25V MLCCs — lower bulk, far lower ESR, wants checking against the solenoid inrush).

**U8 is a passive buzzer + transistor, not an active buzzer.** The firmware generates the
tone on IO13 (LEDC), so the part must be externally driven — `C94598` (MLT-5020) is passive
electromagnetic. Every passive SMD buzzer in the library is Extended; `C94598` has the deepest
stock at 5×5 mm. Its ~100 mA coil exceeds the ESP32 GPIO's ~12 mA source, so it is **low-side
switched** by Q1 (`C2146`, S8050 NPN, Basic): IO13 → R5 (1 kΩ base) → Q1 base; Q1 collector
sinks the buzzer's − leg, emitter to the GND plane, the + leg on the 5 V plane. No flyback
diode (per the step spec); the S8050's 25 V Vce(o) is the only clamp on the coil's turn-off
spike — the first thing to add if the transistor shows stress. Q1 emitter and U8 + are SMD
plane pads and auto-stitch to GND / 5 V (see [`plane-stitching.md`](plane-stitching.md)).

**BT1 is a THT coin base (`C5365915`, Kinghelm KH-CR2032-2-1), not the cheapest SMT clip.**
The bare bent-leg SMT clip (`C70373`, $0.05, 27k stock) is the cheapest CR2032 holder in the
library, but JLCPCB rates it **"Assembly difficulty: High"** — it trips the "processing of this
component is difficult" review (and a possible advanced-option fee) on every order. Every CR2032
holder in the library is Extended (no Basic option), so the feeder fee is unavoidable either way;
among the holders JLCPCB does **not** flag, the 2-pin THT base is the mechanically secure choice and
rides the through-hole assembly the board already runs for the XH connectors. Two 1.2 mm plated
posts at ±10 mm: pin1 (silk-marked +) → DS3231 VBAT, pin2 (−) → GND; the cell is retained by the
molded base. `tsci import` pulled the real land pattern (→ `imports/KH_CR2032_2_1.tsx`).

**U1 is the bare ESP32-WROOM-32E-N4 (`C701341`, Extended), the ESP32 base part.**
The only ESP32 base part the design needs — radio unused, so the cheapest WROOM-32E variant
(4 MB, N4) is fine; the keepout silk stays but no plane is carved (no RF). Placed `rot 0`,
putting the ADC/UART/sensor pins on the south row toward the bottom connector row and the
I²C/pump/boot lines on the north row (the buzzer's IO13 on the east column), keeping the
driver and faucet route corridors clean. It is **3V3-only** — no onboard regulator, no V5 pin — drawing the WiFi-idle ~110 mA
peak from the 3V3 plane through its single 3V3 stitch via, with C10 (0.1 µF) + C11
(10 µF bulk) at the pin. The 3 castellated GND pads + the 9-pad centre thermal pad all share
one `GND` port and each auto-stitches to the bottom plane. EN power-on RC: R7 (10 kΩ, `C25804`
Basic) up to 3V3, C12 (1 µF, `C15849` Basic) to GND. IO0 held high by R8 (10 kΩ). Programming
is the on-board USB-C block — J14 + U13 (CH340C), auto-reset onto EN/IO0 (see
[`esp32-scope.md`](esp32-scope.md)). The bare module's IO pins are SMD pads, single-layer
endpoints: a net that needs the bottom layer lands its run up onto the top pad through a
via-in-pad, capped like the plane stitches; every signal on the board is a hand-routed
`pcbPath` (see [`hand-routing.md`](hand-routing.md)).
