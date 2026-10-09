# borrowed-17-positioner-shelf: what bought motion hardware carries, resolves, speaks and costs

Origin: swarm (wave 2; the digest's thin region "bought multi-axis positioners that already have a software interface" and Derek's request to add ordinary robot arms and other multi-axis positioners to the search). Maturity: developed (a lens, not an arrangement). Scene: `scenes/borrowed-17-positioner-shelf/index.html`.

## Picture it

A plot with payload on one axis and the smallest step or repeatability a row states on the other, both logarithmic, a dashed vertical line at the gun's mass and a dashed horizontal line at a tolerance. A handful of dots: a 0.25 kg desktop arm at 0.2 mm, a 3 kg collaborative arm at 0.02 mm, a telescope mount at 0.0008 mm hollow because it is a step and not a repeatability. Under it a table, one row per product class, with the one or two numbers the listing or the maker really states, the interface, the price and the delivery date observed, and a sentence on what it would change about an idea. Two sliders, gun mass and lever, turn a rated payload into "covers this mass / does not / not stated" and an angular step into millimetres at the dot.

## The proposal

Wave 1 reached gimbals, gantries and a hobby CNC. The thin region in the digest lists desktop and collaborative arms, delta, SCARA and hexapod platforms, camera motion-control rigs, telescope mounts and microscope and lab stands. This shelf lays out what the Prime listings (and, for arms that are not on Prime, maker and reseller pages) actually state, and what each product class would change about an arrangement already in the study:

- **Telescope mounts** (Sky-Watcher AZ-GTi, $525; Star Adventurer GTi, $579): two rotations with motors and output-shaft encoders that follow a hand slew, Wi-Fi with a public command set (search), a 5 kg rating and a 0.625 arcsecond step (search). It is freedom-09 (pose logger) and freedom-10 (nudge box) for two rotations in one product, and borrowed-02's gimbal replaced by a worm-geared, encoded mount. The gun has to be balanced on it and the pivot is not the dot.
- **PTZ cameras** (NexiGo, $242.99, 5,521 ratings; TONGVEO, $299): Derek's example: pan and tilt with presets. A positioner for an eye; the control protocol is not on either listing.
- **Printers, CNC and their rails** (Ender-3 V3 SE, $219, 2,153 ratings; PROVerXL 4030, $659; MGN12 rail, $20.49): XYZ with G-code, homing and probing; the payload of their carriages is not stated.
- **Sit-stand frames and drawer slides** (VIVO, $199.99, 220 lb; FivePears slides, $19.79, 150 lb): the lift and the drawer of room-10 and room-05; height resolution and side play are not stated.
- **Desktop arms** (Mirobot, SO-ARM101 kits): 0.25 to 0.5 kg; below the gun.
- **Collaborative arms** (uFactory Lite 6, Fairino FR3; maker and reseller pages): the FR3 states 3 kg and +-0.02 mm at 622 mm with software access included; hand guiding and gravity compensation are features of the class.
- **Hexapod** (PI H-811; quote): +-17 mm and +-21 deg with a software pivot: borrowed-13.

## What carries loads, establishes position, is free, restrained or driven

Per product; nothing here is an arrangement. The rows say what a product could carry by its own rating; that rating is for a centre of mass near the axis or flange, and the gun sits at a lever (1.2 kg at 250 mm is 2.9 N.m about an axis).

## Software: command, observe, manual

- Command through: G-code (printers, CNC; probe inputs and homing come with it), the SynScan protocol over Wi-Fi (mounts), vendor SDKs or ROS (arms), presets (PTZ), a controller with a software pivot (hexapod).
- Observe: step counts, joint encoders, presets: never the dot.
- Manual: balancing the gun on a mount, coupling the shell to any of them, calibrating the pivot to the dot.

## What was tried to break it

1. **The desktop arms on Prime cannot carry the gun.** Payloads of 0.25 to 0.5 kg. Under a balancer that takes the weight they would carry only the reaction, and their servos step 0.088 deg (12 bit), which is 0.4 mm at 250 mm. Left standing: the MiroMAX models quote 1 kg and +-0.05 mm (maker pages, not Amazon listings, search summary).
2. **The high-volume products state no repeatability.** A printer with 2,153 ratings has a step of 0.0125 mm (search: GT2 20-tooth, 1/16 microstep), belt elasticity of 50 to 100 micrometres (search), and nothing on its carriage's payload. What they carry and how repeatable they are has to be measured.
3. **Only one arm states enough.** FR3: 3 kg, +-0.02 mm, 622 mm reach, $6,799 US (reseller pages, search summaries). It is not a Prime listing: lead time and order path were not observed. It is the reference the others are measured against (wave 1's "used industrial arm" stays as that reference), and it already contains a hand-guiding mode.
4. **Angular positioners turn a lever into resolution.** A step of 0.625 arcsecond is 0.0008 mm at 250 mm; a joint step of 0.088 deg is 0.38 mm at 250 mm. The interesting property of any angular product is what carries the load at the lever, which is rated torque and is on none of the listings read.

## Branches and combinations

- With borrowed-13: a hexapod from six mini rails and rod ends is the parts route to the PI class.
- With freedom-09 / freedom-10: a telescope mount as pose logger and nudge box for two rotations.
- With freedom-02: an arm as the weight path and a positioner as the location path.
- With room-01 and room-05: the gantry parts, the lift and the slide.

## Unresolved problems and questions that need Derek

- None of the interface claims from search summaries has been tried (SynScan on UDP, PTZ control, arm SDKs). Derek owns a printer and a laptop: does he already have a mount, a PTZ camera or an arm in the shop?
- Rated torque and backlash of any mount are not on the listings; the gun's mass and centre of mass decide whether a 5 kg rating means anything.

## Assumptions

- Each cell is tagged in the scene by source: listing (product page read 2026-09-29), search (unchecked summary), maker (a maker or reseller page found by search), derived. Only Amazon Prime listings are recorded from Amazon. Prices and delivery dates are single observations. Gun mass 1.2 kg and lever 250 mm are the illustrative defaults.

## Sourcing pointers

sourcing/borrowed.md wave 2: every Amazon row has ASIN, price, ratings, delivery; maker rows have the search that found them.

## Scene

`borrowed-17-positioner-shelf`
