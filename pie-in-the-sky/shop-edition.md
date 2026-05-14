# Shop Edition — countertop variant

*Pie-in-the-sky, not roadmap. Captured from a conversation 2026-05-13 / 14.*

*BOM figures in this doc are first-pass estimates intended to size the idea, not specifications.*

A second SKU sharing ~90% of the BOM with the under-counter Kitchen Edition. Where the Kitchen Edition disappears into the kitchen and the wow is "the faucet pours soda," the Shop Edition is the opposite — it sits on a countertop in a garage, basement bar, man-cave, or shop, and the wow is "look at this thing." Different buyer mindset, same hatred of cans, same machine underneath.

## The customer

Someone who would buy the Kitchen Edition but for living-partner / kitchen-priority / countertop-real-estate reasons can't put a faucet penetration in the main kitchen. The product moves to the next-most-natural place in their home: the workshop counter, the basement bar, the garage fridge area. Visible CO2 bottle, visible plumbing, visible appliance — those become the *aesthetic* in this context, not blemishes to hide. Bar/shop visual language.

## What's the same as Kitchen Edition

- Cold core, carbonator vessel, refrigeration loop, foam shells, flavor reservoirs, valve manifold, peristaltic pumps, electronics shelf — all unchanged.
- Side-to-side condenser airflow (per the airflow correction in `hardware/future.md` 2026-05-13). Intake on one side face, exhaust on the opposite — no thermal duty on the front face, which is the precondition that makes Shop Edition possible at all.
- Regulatory posture identical. R-600a, UL 60335-2-89 compliance, SNAP markings. The flame symbol and "flammable refrigerant" labels become user-visible on a countertop unit — worth designing into the rear nameplate as deliberate visual elements rather than letting them look like stickers.
- Same CO2 inlet, same water inlet, same C14 power inlet on the rear panel. Customer plumbs water + CO2 once, plugs in, done.

## What's different

**Front face becomes the product.** No faucet penetration through a countertop. The chilled outlet redirects horizontally inside the enclosure (~6–10" of additional insulated run, thermally trivial) to a forward-facing spout sculpted into the front of the appliance. The front face is otherwise free, because the airflow correction means no condenser grille lives there.

**Touchless dispense, gated by a physical arm.** A VL53L1X ToF sensor under the spout sees a glass at the right height. The only way to dispense is: tap the arm switch (LED ring lights up around the dispense field for ~10 s), present a glass, soda pours while glass is present, stops when glass is removed. After 10 s of no glass, auto-disarms. Two things at once: the wow gesture (touchless from a real bar tap) and the safety gate (no accidental dispense from a cat, a kid, or a stray elbow). Momentary rather than latching is the right answer — eliminates the "left it armed, dispensed two flavors of Pepsi on the counter overnight" failure mode.

**Flavor select on the device, not on a remote air switch.** The KRAUS air switch goes away (it was sink-mounted). Two illuminated capacitive buttons next to the dispense field select active flavor. The RP2040 round display showing the active flavor's logo relocates from the through-counter position to the front face, angled up toward the user.

**Drain, not drip tray.** The clean cycle in particular wants a real drain — see the discussion that prompted this doc. The dispense field sits over a slotted SS grate (draft-beer pattern), funneling into a small printed sump tank with a level-switched 12 V diaphragm pump that lifts effluent out to a standard drain connection — washer standpipe, utility-sink tailpiece, or a tee into nearby drain plumbing. ASSE 1021-pattern air-gap on the outlet handles the regulatory mirror of the inlet-side Multiplex 19-0897. Customer plumbs water in, CO2 in, drain out, plug in.

**Front-face ID does real work.** Because the front has no thermal duty, the dispense field can be a sculpted recess — the spout set back into the cabinet face, indirect LED edge lighting around the proximity field, the round display angled up toward the user, the arm switch as a tactile slide or push with a satisfying click. The two flavor-select buttons backlit. The whole assembly reads as a piece of bar equipment, not a kitchen appliance. This is wow the Kitchen Edition fundamentally can't deliver, because its visible part is just a faucet at the back of a sink.

## BOM delta (rough)

| Out | Δ |
|---|---:|
| Westbrass Touch-Flo faucet | −$31 |
| SendCutSend 0.060" SS under-counter plate | −$4 |
| KRAUS air switch | −$40 |
| **subtotal removed** | **−$75** |

| In | Δ |
|---|---:|
| Front nozzle assembly (printed spout + SS internal tube) | +$8 |
| VL53L5CX 8×8 ToF array sensor (glass-edge + rim-fill detection) | +$20 |
| Arm switch — vandal-resistant SS illuminated pushbutton, 16–22 mm, ring-illuminated, momentary, real tactile click | +$30 |
| Two flavor-select buttons — same SS illuminated pushbutton family, matched aesthetic | +$50 |
| WS2812 LED ring around dispense field + diffuser + driver | +$10 |
| Drain sump (printed) + SS drip grate | +$15 |
| Second 12 V diaphragm lift pump (SeaFlo class) | +$48 |
| Drain solenoid (Beduan, valve-manifold extension) | +$10 |
| Sump level reeds (×2) | +$2 |
| Drain tubing + clamps + air-gap fitting | +$10 |
| **subtotal added** | **+$203** |

Net per-unit BOM impact: roughly **+$128** over Kitchen Edition. Both editions hold the same Founder Edition price ($7,500) and same Standard Edition price ($5,500) — the Shop Edition's value proposition isn't cheaper, it's a different aesthetic for a different room.

Two cost-driver observations worth naming:

- **The drain subsystem is the largest single BOM addition (~$85),** not the gesture. Pump + solenoid + sump + grate + plumbing. The drain is what makes the clean cycle unattended and the dispense field self-managing on a countertop — quietly load-bearing for the whole Shop Edition concept, and quietly expensive.
- **The gesture (proximity + arm + flavor buttons + LED ring) lands around $110.** The commodity parts for the same functions would be ~$25, but those parts are wrong here — a $5 plastic rocker on a $7,500 piece of "bar equipment" reads as cheap and undoes the front-face story the Shop Edition exists to tell. Vandal-resistant SS illuminated pushbuttons + an array ToF + a real LED ring are the honest spec.

Front-face industrial design (NRE — printed cabinet face, spout sculpt, button placement, display surround, drip grate geometry) is a separate cost on top of BOM, amortized across the run rather than per-unit.

## Marketing slot

The target-market doc names the Kitchen Edition's center-of-bullseye buyer: $200K+, 2-4 sodas/day, homeowner, "hates the cans." The Shop Edition extends, not splits, that market:

- Homeowners with finished garages, basement bars, or shop spaces where this becomes part of the room's identity.
- Homeowners whose living-partner kitchen dynamics rule out a faucet penetration in the primary kitchen but have other appropriate spots.
- The "adulting upgrade" / man-cave content genre on TikTok/Instagram — the proximity-dispense gesture is genuinely shareable in 30-second video form.

The "He hates these cans" framing still applies. The cans were always going to lose; the only question was where the replacement lives.

## Risks worth naming

- **Front-face industrial design is real work.** Kitchen Edition gets away with the front face being utility because the user never sees it. Shop Edition does not. The dispense spout, drip grate, display surround, button layout, arm switch placement, LED edge geometry — that's a real ID pass, not just a part swap.
- **Tip-over and rear clearance.** Freestanding on a countertop means a wide stable footprint and a rear-condenser-exhaust-side gap the customer can't defeat by shoving the unit flush to a wall. Side-to-side airflow needs both side gaps respected. A rear standoff bumper helps; a printed "do not place against wall on this side" arrow on the rear panel helps more.
- **Drain install friction.** Adds one connection at install. Targets the "plug and play in under an hour" promise. Manageable in the Shop Edition context where the customer is already running water and CO2 through stud bays.
- **Don't backport to Kitchen.** The drain feature looks attractive for unattended clean cycles on the Kitchen Edition too. Resist. Kitchen Edition has a sink under it and a clean cycle that already works. Scope discipline.

## What's needed to validate this is real

1. A countertop mockup of the front face — a non-functional printed shell with the spout, grate, display surround, buttons, arm switch in place — to test whether the proportions actually read as "bar equipment" rather than "kitchen appliance with a hole in the front."
2. A ring-1 or ring-2 buyer (per the target-market rings model) whose room genuinely fits Shop Edition better than Kitchen. One real installation in a real garage settles a lot of questions that no amount of CAD answers.
3. Confirmation that the side-to-side airflow geometry actually works at the donor fan's native pressure curve once the enclosure is sealed up — the donor was designed for an open countertop ice maker, not a stuffed-cabinet under-sink layout. (This is a Kitchen Edition question too, raised here only because the side ducts in Shop Edition's mockup are the cheapest place to instrument it.)
