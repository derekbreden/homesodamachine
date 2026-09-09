# Controlled core extraction

Four M5 screw jacks lift the core while four long printed guides keep it aligned.
The ears, nut seats, washer pockets, guides and their supports are integral to
[funnel-mold-guided-vacuum-petg-08-016.3mf](funnel-mold-guided-vacuum-petg-08-016.3mf).
All four stations lie outside the forming surfaces, at the middle of each side.
The forming geometry retains its 0.20 mm net finishing allowance.

A screw passes through a captive square nut in the core ear. Its tip rests on
the solid ring of a steel washer in the cavity's pocket. Turning clockwise tries
to advance the screw downward; the washer stops its tip, so the nut and core
rise. The washer spreads the load into a solid pad, a 45° corbel and a radial web
rooted in the cavity's structural rib. The nut lifts against a 4.4 mm printed
roof; the threaded engagement is steel.

The four screws control displacement separately. Equal turns keep the core
level; they do not equalize force automatically. Use the included hand hex key,
where changes in resistance can be felt. A powered driver can overload a printed
ear before a stuck casting releases.

## Hardware for one mold

Amazon's signed-in order details were checked on September 8, 2026.

| Item | Quantity | Verified stock / purchase |
|---|---:|---|
| M5 × 0.8 × 50 mm fully threaded socket-head screws | 4 | [SVLING 40-pack](https://www.amazon.com/dp/B0GHNQFZYR), 12.9 alloy steel, black; 4 mm hex key included. Ordered September 8, order **112-6085763-5397009**, **$8.57 paid** ($7.99 + $0.58 tax), arrival shown for **September 11**. |
| M5 × 0.8 square nuts, 8 mm square × 4 mm thick | 4 | [Owned 100-pack](https://www.amazon.com/dp/B0F6B5X6CX), Amazon confirms delivered **September 5**. |
| M5 × 25 mm OD steel fender washers | 4 | [Owned 60-pack](https://www.amazon.com/dp/B0GSMDY5GL). The design accommodates **0.8–2.0 mm** thickness; measure the stock. |
| 6.35 × 50.8 mm ground spout rod | 1 | [Owned POWERTEC 71476 pins](https://www.amazon.com/dp/B086DCHYQK). |

No additional purchase is specified. The washer pocket is 25.4 mm diameter with
an exposed, fully supported floor. The screw axis is **8 mm off the washer's
centre**, clear of both its hole and its outside edge. Keep the screw end flat
and free of burrs, and replace a washer if its bearing track becomes deeply scored.

## Fits and travel

| Feature | Modeled dimension |
|---|---|
| Jack clearance bore | 5.8 mm diameter |
| Side-entry square-nut slot | 8.4 mm wide × 4.4 mm high |
| Nut-bearing roof | 4.4 mm thick |
| Downward core guide | 8 mm square, 0.6 mm corner chamfers, 0.8 mm tip lead-in |
| Cavity guide sleeve | 8.6 mm square bore, 14 mm long, chamfered entry |
| Guide reach below core parting plane | 50 mm |
| Controlled working lift | **32 mm** |
| Guide overlap at 32 mm lift | **12 mm** |
| Rod's initial socket engagement | 28.8 mm |
| Screw-head clearance after 32 mm lift | 5.8–7.0 mm for the stated washer range |

Four shallow marks on the outside faces of the guide posts align with the
sleeve mouths at 32 mm lift. These are travel witnesses, not hard stops. The core
can then lift free of the guides; the screws leave their washers with it. The
chamfered guide tips enter their sleeves before the forming plug enters the
cavity when assembling.

The additions stay inside the original core's corner-to-corner circle, about
284.3 mm diameter. The owned chamber is listed in the tool ledger with an 11.8-inch
(299.7 mm) interior. Verify the actual opening, shelf and catch-tray clearance;
clamps and tray rims need their own space. Keep all backing-air exits exposed.

## Print the small fits first

Plate 1 includes the finish witness, a hardware witness and a guide pin. The
hardware witness reproduces the nut slot in the inverted core's print orientation,
a guide sleeve and a washer pocket. Check the actual nut, screw and washer in it.
The pin must slide through the sleeve freely without being forced or rocked.
Remove brim and strings before assessing the fits. Keep these sliding and seating
surfaces uncoated. Correct a tight fit on the small sample before printing the
large halves.

The coupon verifies local fit; it cannot establish alignment of four widely
spaced guides. Dry-assemble the finished prints before coating: lower the core
through all four sleeves, confirm the skirt seats flat, and run the full 32 mm
stroke with the actual rod installed. The rod must slide freely in its socket.
The jacks must not be used to force a tight guide or rod fit.

## Assemble, cast and extract

1. Slide one square nut into each core ear from its outside edge. Pass the screw
   through it to retain it. Set one washer flat in each cavity pocket.
2. Back the screws out enough that their tips clear the washers while the core
   seats. Hold the core evenly seated for the pour and cure using the mold's
   holding arrangement. The jacks are lifting devices; they do not clamp it shut.
   Keep the pour, silicone vents and backing-air channels open.
3. After full cure, remove the holding clamps or weight. Turn each screw down by
   hand until its tip just contacts the washer. This is the zero-lift position.
4. Advance the four screws in **opposite-side pairs**, one quarter-turn each,
   then repeat around the mold. M5 × 0.8 advances **0.20 mm per quarter-turn**.
   Watch the gaps and rod. Stop if one ear bends, a guide binds or one side rises
   ahead of the others; resolve the obstruction before continuing.
5. Once the guide marks reach the sleeve mouths, the core has lifted 32 mm
   (40 complete screw turns from contact). Its 28.8 mm rod socket has cleared
   a stationary rod. Observe the rod directly: adhesion may have pulled it upward
   with the core. Continue lifting straight by hand until the guides clear.
6. Peel the silicone out of the cavity, then draw the rod axially from the
   silicone and trim the sacrificial tip and pour/vent pips.

The CAD and slice checks establish geometry and toolpaths. Actual extraction
force, printed stiffness, coating durability and release remain physical bench
checks; no rated lifting load is assigned to the printed ears.
