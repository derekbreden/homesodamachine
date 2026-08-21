# Unboxing and Quick-Start

The appliance ships in a carton with the owner's manual across the interior under the top
flap — a twelve-page booklet at 5.5 × 8.5 in, built in
[`/hardware/manual/`](/hardware/manual/README.md). The faucet ships in a smaller box inside
the appliance carton. Everything the appliance dispenses leaves by the umbilical, so the
faucet is what puts a glass under the machine.

## The book

Twelve pages, in this order. The install is five numbered steps, one to a page, each with the
step's numeral set larger than its title.

| Page | |
|---|---|
| 1 | Cover — the machine in white line art on navy |
| 2 | What is in the carton, what the customer supplies, and the contents |
| 3 | Where it goes — the cabinet, the slot, the three clearances |
| 4 | **1** · Tee into the water |
| 5 | **2** · Connect the CO₂ |
| 6 | **3** · Mount the faucet |
| 7 | **4** · Connect the umbilical — the four ports and their rings |
| 8 | **5** · Power up and fill |
| 9 | The first pour — fill the hopper, prime, pour |
| 10 | Every day — the lever, and the five pages on the display |
| 11 | Keeping it running — flavor, cylinder, clean cycle, filter |
| 12 | If something is wrong, and the machine in numbers |

The two iso views are the enclosure's own line art
([`/hardware/printed-parts/enclosure/drawings/line-art/`](/hardware/printed-parts/enclosure/drawings/line-art/)):
the front three-quarter on the cover and on page 3, the rear on page 7 with the port rings it
carries. Everything else a page draws is inline SVG.

## What the customer meets, in order

1. **Where it goes.** A sink base cabinet that is not empty. The disposal takes the middle;
   the machine and the customer's CO₂ cylinder take the slot beside it.
2. **The water.** Shut the angle stop, break the supply line once, fit a tee — the kit carries
   one for a 3/8" stop with a braided supply and one for a line already running 1/4" tubing —
   filter inline, tube into the **white-ringed** union.
3. **The gas.** Cylinder upright beside the machine, the shipped CGA-320 regulator on it, red
   tube into the **red-ringed** bulkhead, primary set anywhere in 70–100 PSI.
4. **The faucet.** Drop it through the countertop hole from above, slide the keyhole plate in
   laterally from below onto the dangling umbilical, washer and nut.
5. **The umbilical.** Blue tube into the **blue-ringed** union; the two black tubes into the
   two black FLAVOR ports, either into either.
6. **Power.** Cord into the recessed inlet, then the wall. The machine fills, chills, and
   carbonates on its own; the first chill is tens of minutes.
7. **Flavor and the first pour.** A 440 mL concentrate bottle inverted over the funnel in the
   top wall, per side. Prime the channel from the display, then open the lever.

## Color system

Three colors: **blue = carbonated water**, **red = CO2**, **white = tap water**. All three do wayfinding — they match a word on the page to a marker on the appliance or on the customer's supply.

Blue is the one that fixes the other two. The carbonated-water line is bought as blue tube and the union that receives it is bought wearing a blue ring ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3 and §8), so blue names that union and nothing else on the rear wall — which leaves white for the tap-water station the customer tees into. A blue arrow on a tap-water step would send them to the faucet's own union three stations up the same wall. The rear face states the scheme once, in [`/hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py`](/hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py), and the book's stylesheet and the line-art rings both paint from it.

White is drawn as its outline. That is what white is on white paper, and it is what the white ring on the wall reads as in line art.

Motion arrows (the keyhole plate sliding, bottles pouring) are plain line work, no color. They show direction of motion, not a connection to color-coded hardware.

A valve or shutoff drawn on a page is colored by the fluid it actuates — red at the CO2 cylinder valve, white at the water angle stop — because that doubles as wayfinding for which valve is which.
