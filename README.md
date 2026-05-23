# Home Soda Machine

A kitchen appliance that dispenses real Pepsi-made diet soda — Diet Mountain Dew, Diet Pepsi, Pepsi Zero Sugar — cold and carbonated, from a faucet. Turn the handle, soda comes out.

The public face of the project is **[homesodamachine.com](https://homesodamachine.com)** — what this is, the build blog, the 3D viewer, and a single signup form to be notified when units are available. This repository is the working substrate behind that.

The prototype that proves the dispense path is in Derek's kitchen today — a Lilium under-counter carbonator with peristaltic pumps injecting flavor concentrate into the dispensed water. The project's biography lives in [`biography/`](biography/) — [`2026-04-05.md`](biography/2026-04-05.md) (origin story: failed SodaStream, the business-license wall, the AI design wall) and [`2026-05-23.md`](biography/2026-05-23.md) (vision into work: welding, marketing, the engineering).

The product under development is an integrated under-counter appliance — custom-fabricated 316L stainless carbonator vessel, harvested ice-maker refrigeration loop, foam-insulated cold core, two flavor reservoirs, all behind a single 120 VAC cord and one CO2 line. Architecture: [`hardware/future.md`](hardware/future.md). Founder Edition (units 001-050, $7,500 hand-built) is the launch tier — [`marketing/target-market.md`](marketing/target-market.md) covers who it's for and why.

## What's where

| Path | Contents |
|---|---|
| [`biography/`](biography/) | Project biography by chapter — `2026-04-05.md` (founding), `2026-05-23.md` (vision into work) |
| [`hardware/`](hardware/) | The integrated appliance under development — CAD scripts, [`bom.md`](hardware/bom.md), [`purchases.md`](hardware/purchases.md), [`assembly/`](hardware/assembly/) procedures, printed parts, wiring schedules |
| [`firmware/`](firmware/) | ESP32 + RP2040 + ESP32-S3 firmware (prototype + shared base for appliance) — see [`firmware/README.md`](firmware/README.md) |
| [`web/`](web/) | homesodamachine.com — Node server, blog, CAD viewer — see [`web/README.md`](web/README.md) |
| [`ios/`](ios/) | iOS companion app (BLE bridge, settings, usage stats) |
| [`android/`](android/) | Android companion app |
| [`marketing/`](marketing/) | Target market analysis, unboxing brief, video scripts |
| [`business/`](business/) | Incorporation, regulatory (UL 943, ASSE 1022) |
| [`posts/`](posts/) | Daily build log, rendered as the blog at homesodamachine.com/blog |
| [`pie-in-the-sky/`](pie-in-the-sky/) | Real desires not yet committed to plans |
| [`tools/`](tools/) | CadQuery venv, render scripts, measurement utilities |

Agents and collaborators landing in this repo: [`CLAUDE.md`](CLAUDE.md) is the entry point.

## License

MIT
