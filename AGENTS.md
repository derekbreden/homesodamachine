# Soda Flavor Injector

## What This Is

A home soda machine — a kitchen appliance that dispenses flavored carbonated water from a faucet. In the prototype, refrigerated carbonated water is provided by an external carbonator (Lillium, Brio). When flow is detected, peristaltic pumps inject flavoring through a parallel line. Two flavors, each primed and valve-locked for instant dispensing. The mixing happens in the user's glass, not before. With the product now under development, the carbonator chiller is integrated, see `hardware/future.md` for details.

## Why This Exists

Pepsi and Coke will not sell bag-in-box syrup to home consumers without a business license. Pepsi does sell their own brand formulations as SodaStream-compatible syrup (1:20 ratio, sucralose, no sugar) to home consumers. Diet Mountain Dew syrup made by Pepsi is Diet Mountain Dew — not an off-brand approximation.

Dispensed through chilled carbonated water, the result is indistinguishable from the canned product, with equal or better carbonation and temperature. This is not a compromise or substitute. It is the same product, colder and fizzier than a can, on tap.

There is no machine on the market that gives a home user this experience — turn the handle, soda comes out. The alternatives are hauling cans from the store every week, or home carbonation products that carbonate warm water into bottles that go flat within hours. Despite enormous initial sales, very few people stick with home carbonation because warm water cannot hold carbonation — it is flat before it reaches your glass.

## CadQuery

Run `generate_step_cadquery.py` scripts with the project's CadQuery venv: `tools/cad-venv/bin/python`. cadquery is not installed on the system python.

Reference scripts for how to structure CadQuery parts: `hardware/printed-parts/foam-bag-shell/generate_step_cadquery.py` and `hardware/printed-parts/pump-case/generate_step_cadquery.py`. Follow their pattern: constants by concern, geometry helpers, feature functions, top-level assembly as a bill of operations.

## Firmware

Flash with `./tools/flash.sh <env>` (envs: `esp32dev`, `rp2040_display`, `esp32s3_config`). The build depends on a sibling `PersistentLog` repo at `../PersistentLog` — flash.sh errors clearly if it's missing.

### Amazon Prime

You have access to my Chrome which is signed in to my amazon through your MCP. I only care about Amazon Prime listings. Non-Prime listings are non-existent as far as I am concerned. Do not read them. Do not mention them. They do not exist.