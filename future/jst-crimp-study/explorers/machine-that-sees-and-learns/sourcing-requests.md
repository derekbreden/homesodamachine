# Sourcing requests: machine-that-sees-and-learns

These are Amazon candidates for the coordinator's Prime-confirmation pass. No
amazon.com page was fetched, and no listing was read, to make this list. In the
idea files these parts are called "Amazon, Prime to be confirmed".

Items already in [`../../context/sourcing-requests.md`](../../context/sourcing-requests.md)
are not repeated: the load cell with HX711, the crimp-height micrometer, the
SO-101 kit, the small vibratory feeder, and the JST WC-110. The ideas here use
them as listed there.

| Item | Idea | Capability that matters | Search terms |
|---|---|---|---|
| 16MP USB camera board with an M12 lens mount (manual focus), plus M12 lenses of 12 mm and 16 mm | [v1](ideas/v1-watched-nest.md), [v5](ideas/v5-inspection-booth.md) | ~120 px/mm at 100 mm working distance [calc: vision_budget §1]. UVC, so it works with the repo's panelcam tooling. MJPG at full resolution. Lens swappable | `16MP USB camera M12 lens IMX298`, `USB camera module M12 mount manual focus 4K`, `M12 lens 12mm 16mm board camera` |
| Clip-on close-up (macro) lens, +20 D class | v1, v5 | Brings the ELP on hand to ~86 px/mm at ~50 mm [calc: vision_budget §1]. Must fit over or in front of the ELP's small lens | `clip on macro lens 15x`, `close up lens +20 diopter small` |
| Small first-surface mirror, 25–50 mm | v1, v5 | Front-surface, no double image, so one camera gets a top view and a side view in one frame | `first surface mirror small`, `front surface mirror 2 inch` |
| LED light pad (tracing pad), A5 or smaller, USB powered | [v4](ideas/v4-tap-look-pick.md), [v4b](ideas/v4b-pocket-plate.md), v5 | Even, diffuse white backlight. Thin. Dimmable | `A5 LED light pad tracing USB`, `LED tracing light box A5 dimmable` |
| Opal (white diffusing) acrylic sheet, 2–3 mm | v1 nest backlight, v4 tray top | Diffuses a single LED into a small even backlight. Tray top that sheds static | `opal acrylic sheet 3mm white diffuser`, `white translucent acrylic sheet small` |
| WS2812B LED ring, 12 or 16 LEDs | v1 | Addressable, so LEDs can be lit one at a time for the shading pictures. 5 V, ESP32-driven | `WS2812B LED ring 16`, `WS2812 ring 12 bit` |
| Line laser module, 650 or 520 nm, focusable, 5 mW class | [v6](ideas/v6-patient-cell.md) | A thin line across the ribbon, to profile the grooves between conductors | `line laser module 650nm focusable`, `5mW line laser diode module adjustable` |
| Mini diaphragm vacuum pump 12 V, solenoid valve, vacuum pressure sensor module | v4, v4b | Enough vacuum to lift a 0.043 g contact by a 0.8–1.0 mm nozzle. A pressure sensor that reads a pick | `mini vacuum pump 12V diaphragm`, `12V solenoid valve 2 way normally closed mini`, `XGZP6847 vacuum pressure sensor` |
| Pick-and-place nozzles, ~0.5–1.0 mm tip (Juki 500-series or similar) | v4, v4b | Small tip for the contact's box top. Fits a printed holder | `Juki nozzle 502 503`, `SMT pick and place nozzle set` |
| Push-pull solenoid 12 V, ~10 mm stroke | v4 tapper | A short, sharp tap under a light tray. Duty cycle for repeated taps | `push pull solenoid 12V 10mm stroke`, `mini solenoid 12V push type` |
| Digital indicator, 0.001 mm resolution, with data output | [v3](ideas/v3-press-that-runs-experiments.md) | Reads ram position into software. Absolute. Data port | `digital indicator 0.001mm data output`, `electronic dial indicator SPC output` |
| Spring steel shim, 1.0 and 1.5 mm | v3 (the camera-read force leaf) | Hardened and tempered strip that bends elastically to ~450 MPa [calc: campaign §4] | `spring steel shim 1mm`, `blue tempered spring steel strip` |
| Precision pin gauge set, ~0.5–1.5 mm | v1, v5 | Known-diameter reference pins in the silhouette frame | `pin gauge set 0.5 1.0 mm`, `precision plug gauge pins small` |
| #11 scalpel blades and handle | v6 split | Thin, sharp, replaceable | `#11 scalpel blades`, `scalpel handle #3` |
| Hobby servos: MG90S class and a ~25 kg·cm class | v1 hold-down finger, v1 tab cutter, v6 tweezer, v3 bend arm | Position control. The larger one closes a flush cutter on a 0.2 mm tab (~50–160 N at the jaw [xh-facts §4]) | `MG90S servo`, `25kg digital servo` |
| Ender-3-class printer (as a stage) | [v1b](ideas/v1b-printer-as-stage.md) | Three axes with G-code over USB. Creality lists the Ender-3 V3 SE at $199 on its own store (2026-09-28) | `Ender-3 V3 SE` |

## Wave 2 additions (exchange on terminal-supply)

These serve the combinations in
[`../../exchange/machine-that-sees-and-learns--on--terminal-supply.md`](../../exchange/machine-that-sees-and-learns--on--terminal-supply.md).
No amazon.com page was fetched to make them.

| Item | Where it is used | Capability that matters | Search terms |
|---|---|---|---|
| Miniature linear slide with a small stepper (NEMA 8 or 11) and lead screw, 10–50 mm stroke | the strip fence moved in Y by the picture every cycle (a2 + v1); a5's anvil Z set per cavity | Lead of 1–2 mm; low backlash; small enough to sit beside a strip track | `mini linear stage stepper motor lead screw 50mm`, `NEMA 8 linear actuator slide` |
| Opal acrylic or white diffuser sheet, 1 mm | the backlight vane slid between two strip contacts | Thin enough to enter a 5.2 mm gap with clearance; glows evenly when lit from its edge or from above | `1mm opal acrylic sheet`, `white light diffuser sheet 1mm` |

## Non-Amazon sources used in the ideas (observed 2026-09-28)

- **Raspberry Pi HQ camera** (IMX477, 1.55 µm, C/CS mount): $55, 1 in stock,
  limit 10 per customer. 16 mm lens $77.50, 6 mm lens $49.30.
  [Adafruit 4561](https://www.adafruit.com/product/4561).
  It needs a Pi to host it. The idea files use it only as an alternative to a
  USB camera.
- **Creality Ender-3 V3 SE**: $199, estimated shipping Sep 28–30.
  [Creality store](https://store.creality.com/products/ender-3-v3-se-3d-printer).
- **SO-101 arm**: bill of materials $229.88 for a leader and follower pair,
  $121.94 for a follower alone. Kits from PartaBot, Seeed Studio, WowRobo and
  others. [SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100).
- **Dobot MG400**: ±0.05 mm repeatability, 500 g payload, 440 mm reach. Price
  not listed.
  [Dobot](https://www.dobot-robots.com/products/desktop-four-axis/mg400.html).
- **Software**, all free:
  - LeRobot, which trains on Apple silicon (`mps`)
    ([docs](https://huggingface.co/docs/lerobot/il_robots));
  - OpenPnP's ReferenceHeapFeeder
    ([wiki](https://github.com/openpnp/openpnp/wiki/ReferenceHeapFeeder));
  - OpenCV.

## Wave 2 additions (v7 the run, v8 the tack)

These serve [v7](ideas/v7-the-run.md) and [v8](ideas/v8-tack-look-crimp.md).
No amazon.com page was fetched to make them.

| Item | Idea | Capability that matters | Search terms |
|---|---|---|---|
| ESP32 development board (ESP32-S3 DevKitC class), two | v7 station MCU; v7 stack B force MCU | PlatformIO support, enough GPIO for a step/dir pair, a load-cell amplifier, 4–6 servos, an LED ring and 5–9 far-end inputs; native USB serial | `ESP32-S3 DevKitC-1`, `ESP32-S3 development board N16R8` |
| HX717 load-cell amplifier module, or an ADS1220 24-bit ADC module | v7 stroke; v8 former load cell | HX717 samples at 320 SPS against the HX711's 80 [source: Klipper Load_Cell]; the ADS1220 runs faster still | `HX717 load cell amplifier`, `ADS1220 module 24 bit` |
| MKS DLC32 (ESP32 board sold for grbl and FluidNC engravers) | v7 stack B | FluidNC-capable board with drivers on board; stage and press axes from one YAML file | `MKS DLC32`, `ESP32 grbl board FluidNC` |
| TMC2209 stepper driver modules | v7 press axis (stack A) | Quiet at crawl speeds; step/dir; the bench's DM542T serves a NEMA 23 instead | `TMC2209 stepper driver module` |
| Emergency-stop mushroom switch (NC) and a roller-lever microswitch | v7 e-stop and lid interlock in the drivers' enable line | Normally-closed contact; latching mushroom head | `emergency stop button 22mm NC latching`, `micro limit switch roller lever` |
| Powered USB 3 hub with per-port switches | v7 cameras and boards | Its own supply, so a servo move cannot brown out a camera; a port can be power-cycled by hand | `powered USB 3.0 hub individual switches 7 port` |
| 6 V 5–10 A supply for hobby servos | v7 servos (keys, former, shear) | Servos never powered from USB | `6V 10A power supply servo`, `5V 10A switching power supply` |
| Small UPS | v7 power loss (optional) | Carries the Mac and controllers through a short outage, so the journal and the MCU hold cleanly | `APC Back-UPS 600VA` |
| 35 kg·cm digital metal-gear servo (the 25 kg·cm class is already listed) | v8 tack former through a 1–3:1 lever | ~140–520 N at the former [calc: wave2 §5] | `35kg servo digital metal gear 180 degree` |
| Ground flat stock, or square HSS tool blanks | v8 anvil insert under the insulation barrel | Hard, flat and square; 14–57 MPa of tack load [calc: wave2 §5] | `HSS tool blank 1/4 square`, `O1 ground flat stock 1/8` |
| Spare SN-series jaw set for the SN-2549 | v8 tack former profile (insulation section) | Same profile family as the final crimper; $4.99–9.99 direct [hand-tool-as-press, source] | `SN-2549 replacement jaw`, `IWISS SN-2549 jaw set` |
| Small LEDs, 1–3 mm, for the frame-sync indicator | v7 capture | A dot in each camera's field that says which lighting state a frame was taken under | `3mm LED assortment`, `0603 LED` |

## Non-Amazon sources and software (wave 2, observed 2026-09-28)

- **Klipper** load-cell support: HX711 at 80 SPS, HX717 at 320 SPS,
  `trigger_force` and `force_safety_limit`.
  [klipper3d.org/Load_Cell.html](https://www.klipper3d.org/Load_Cell.html).
  Free.
- **FluidNC:** ESP32 CNC firmware, YAML configuration, RC servos, relays and
  probe inputs, G-code over USB and WiFi.
  [github.com/bdring/FluidNC](https://github.com/bdring/FluidNC). Free.
- **ntfy:** notifications by HTTP PUT or POST to a topic, JPEG or PNG
  attachments up to 15 MB, up to three action buttons including http actions.
  Self-hostable. [docs.ntfy.sh/publish](https://docs.ntfy.sh/publish/). Free.
- **Claude Code headless:** `claude -p` with `--output-format json`,
  `--json-schema`, `--resume` and `--allowedTools`. The JSON output reports
  `total_cost_usd`. [code.claude.com/docs/en/headless](https://code.claude.com/docs/en/headless).
- **BTT SKR Pico** (4× TMC2209, Klipper), $39.85, in stock
  [procedure-is-the-machine, source]. For v7 stack C.
- **SparkFun TAL220 10 kg bar load cell**, $12.95, in stock
  [hand-tool-as-press, source]. For v8's former.
- **Laser-cut 1.2–1.5 mm stainless** for v8's former: a sheet-metal service
  such as SendCutSend (2–4 days [borrowed-machines, source]). Not priced here.

## Wave 3

These serve W1 and W2 in
[`../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md`](../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md)
(v8's tack station T and a4's one-nest die set as station C). No amazon.com
page was fetched to make them. Items already confirmed in
[`../../sourcing/amazon-prime.md`](../../sourcing/amazon-prime.md) (the 500 kg
button cell, the Clockwise DITR-0105 indicator, the 10:1 NEMA 23 planetary, the
DS3235 servo, the HSS blanks, the M12 camera) are not repeated.

| Item | Where it is used | Capability that matters | Search terms |
|---|---|---|---|
| Bar load cell, 20 kg, with HX711 board | T: under the nest insert, reading the tack's forming force | 33–132 N forming force [calc: wave2 §5] with margin; the confirmed 5 kg cell tops out at 49 N | `20kg load cell HX711`, `bar load cell 20kg aluminum` |
| Disc springs (Belleville), 20–25 mm OD, 1.0–1.25 mm thick, spring steel (DIN 2093 group 2 class), not the light stainless assortment | C: the preloaded stack under the lower die holder (a4) | A 3–4 stacked set preloaded to ~3.5 kN with 0.3–0.6 mm of further travel over 1–2 kN [hand-tool-as-press calc §6] | `DIN 2093 disc spring 20mm`, `belleville spring washer 25mm heavy duty` |
| O1 or A2 ground flat stock, 1/16 in (1.6 mm) × 1/2 in | T: the tack former plate (1.2–1.5 mm, filed to an insulation profile); C: the seat's floor ledge | Flat, hardenable, thin enough for the former's 1.2–1.5 mm | `O1 ground flat stock 1/16`, `precision ground flat stock 1/16 x 1/2` |
| USB to RS232 cable for the Clockwise DITR-0105 (DTCR-01 or equivalent) | C: reading the re-touch indicator into the runner | The indicator's own data port; the DTCR-01 had no Prime listing on 2026-09-28 | `Clockwise Tools DTCR-01`, `digital indicator USB data cable Clockwise` |

### Wave 3, final pass

These serve [v9](ideas/v9-tack-at-the-anvil.md), [v9b](ideas/v9b-tack-by-hand-on-the-jack-test.md),
[v4](ideas/v4-tap-look-pick.md), [v3](ideas/v3-press-that-runs-experiments.md)
and [v7](ideas/v7-the-run.md). No amazon.com page was fetched to make them. The
20 kg bar cell, the O1 or A2 flat stock, the DIN 2093 disc springs and the
DTCR-01 cable above also serve v8 and v9.

| Item | Idea | Capability that matters | Search terms |
|---|---|---|---|
| Soft bellows vacuum cup, 2–3 mm, for a pick-and-place or vacuum pen | v4 | Seals on a box top tilted 11–17° on its lance; fits a 0.8–1.5 mm nozzle stem or a printed holder | `mini bellows suction cup 3mm`, `SMT rubber suction nozzle bellows`, `vacuum pen soft rubber tip small` |
| 14-bit SPI magnetic angle encoder board (AS5047P, AS5048A or MT6816 class) with a diametric magnet | v3 crank height gauge; v9; v7 stack C | 0.2–0.5 µm of height per count near a crank's re-touch point [bm W §6]; SPI, so a Klipper `[angle]` or an ESP32 reads it | `AS5047P encoder board`, `AS5048A magnetic encoder SPI`, `MT6816 encoder module` |
| Narrow-beam white LEDs, 3 mm, 15–20° | v8, v9, v9b, v1 | A small spot at 60–75° elevation into a 1.4–1.6 mm-wide barrel, for the shadow test | `3mm white LED narrow angle 15 degree`, `3mm LED 20 degree white` |
| Small push-pull toggle clamp with a stated plunger stroke (GH-301/GH-302 class) | v9b | Plunger stroke of ~10–15 mm stated on the page, to move a former onto a screw stop | `GH-301 push pull toggle clamp`, `push pull toggle clamp 10mm stroke small` |
| Precut first-surface mirror, 10–25 mm | v9, v9b, v5 | Saves cutting the 100 × 100 mm plate for a 10 mm mirror at 45° | `first surface mirror 25mm`, `front surface mirror small square 20mm` |
