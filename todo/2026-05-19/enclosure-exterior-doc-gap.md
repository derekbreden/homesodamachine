# The enclosure exterior has no design document, and the bottle-placement affordance has no home

**Author:** hourly agent, 2026-05-19 (sixth of the day, rewritten after operator correction)
**Status:** pre-first-sale (customer-facing fit-and-feel) — recommendation only, not for direct execution
**Audience:** Derek, future agents
**Distinct from siblings:**
- Morning sibling [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) — post-sale brand-name legal exposure.
- Midday sibling [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) — post-sale SKU stockout policy.
- Earlier today [`routine-is-optimizing-the-wrong-thing-gap.md`](routine-is-optimizing-the-wrong-thing-gap.md) — meta doc; this routine should bias toward the appliance.
- Earlier today [`integrated-firmware-gap.md`](integrated-firmware-gap.md) — firmware-side prototype-blocker.
- Earlier today [`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md) — vessel-side prototype-blocker.

This doc replaces an earlier, retracted version of itself (`front-panel-cad-gap.md`, commit `f404b7e`) that mis-scoped the front-panel doc and treated the CO2 cylinder as sitting in front of the appliance. The cylinder sits **beside** the appliance, in the side air-gap. The bottle-placement affordance belongs on the surface it neighbors there — and that surface has no design document. This is the corrected gap.

The same commit that adds this doc also cleans up the wrong-scope text in [`hardware/printed-parts/enclosure/front-panel/README.md`](../../hardware/printed-parts/enclosure/front-panel/README.md) and [`hardware/future.md`](../../hardware/future.md) so future agents (and Derek) don't inherit the same confusion.

---

## TL;DR

The enclosure has six exterior surfaces — front panel, back panel, two side faces, top face, and floor / bottom edge — plus the nameplate plaque. Three have design docs in [`hardware/printed-parts/enclosure/`](../../hardware/printed-parts/enclosure/): `front-panel/`, `back-panel/`, `nameplate/`. The other three have nothing.

| Surface | Document | What's on it |
|---|---|---|
| Front panel | `front-panel/README.md` | CO2 inlet, pump-cartridge access door |
| Back panel | `back-panel/README.md` | C14 AC inlet, water inlet, BiB adapter, 3 umbilical bulkheads |
| Nameplate plaque | `nameplate/README.md` | Serial, regulatory mark, QR code |
| **Side face A** (condenser-active side) | **— none —** | Condenser intake **or** exhaust grille |
| **Side face B** (opposite side) | **— none —** | Condenser exhaust **or** intake grille; and the bottle-placement affordance lives on one of A or B |
| **Top face** | **— none —** (integral hopper named in `future.md` only) | Hopper funnel for SodaStream concentrate bottles |
| **Floor / bottom edge** | **— none —** | Possibly contributes to the bottle-placement affordance |

`future.md` "Enclosure layout" describes the side-face airflow story and the top-face hopper in prose, but no part-level doc owns either surface, and there is no enclosure-shell CAD generator that ties the surfaces into one solid.

The most user-visible missing piece is the bottle-placement affordance: a bottle-shaped curve on the cylinder-side exterior surface that lands the customer's CO2 cylinder in the right place without instructions. It's been homeless across three docs (`future.md`, the front-panel README, and the retracted version of this doc) precisely because the surface it should live on has no document.

---

## Why this matters now

Three reasons it can't slide:

**1. Print-iteration latency.** The cold-core foam shell ([`hardware/printed-parts/cold-core/foam-shell/print-log.md`](../../hardware/printed-parts/cold-core/foam-shell/)) and the faucet shell ([`hardware/printed-parts/faucet/touch-flo-shell/print-log.md`](../../hardware/printed-parts/faucet/touch-flo-shell/) — recent commits `d38aaaa`, `b4e6239`, `fb4ffd4` logging attempts 10 + 11 + the 3-piece slice) both show the print-bring-up tail on large-format Bambu H2C parts: many hours per attempt, multiple iterations to converge. The cylinder-side exterior surface will need the same — fitting the curve to the actual cylinder Derek owns, getting the inlet-tether path obvious from the cabinet door view, sanity-checking against the condenser airflow. Start the surface doc now or pay the iteration tail in November.

**2. Several adjacent decisions are downstream.** The front-panel doc's "inlet-stub height" can't land until the cylinder side-gap decision is made (which side: condenser-active or quiet). The enclosure-shell CAD generator — if/when one is written — needs the side-face geometry to model the airflow grilles + the cylinder-side curve as continuous features. The install-consult playbook ([`../2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md)) needs an answer for "where does the customer put the bottle" that doesn't read as instructions.

**3. The honesty cost.** Right now three docs gesture at "visual affordance — cradle, retention strap, labeled inlet" without owning any of it. Each new agent reading the repo inherits the same scope confusion the retracted doc demonstrated (most recently: me). Naming the missing doc is the cheapest way to stop that pattern from compounding.

Founder Edition cadence (~12 units/year per [`marketing/target-market.md`](../../marketing/target-market.md)) means the side-face geometry is one of the things the customer sees every time they open the cabinet door. Founder Edition is the era where fit-and-feel carries the product story; this surface is part of that story.

---

## What the missing document should own

Listed concretely so a future agent has something to push back against, not in priority order:

1. **Which side the cylinder lives on.** Two side gaps, one of them condenser-active. The exhaust side runs 40-50 °C; aluminum cylinder doesn't mind, but airflow blocked by a cylinder body does. The intake side runs at cabinet-ambient; blocking that with a cylinder reduces the condenser's mass-flow rate. The quiet (non-condenser) side would be a separate cabinet gap with whatever the customer's plumbing already occupies. This is a real layout call.

2. **The bottle-shaped curve.** Cylinder OD ~5.25" / 133 mm (Catalina/Luxfer 5 lb aluminum CGA-320). A shallow concave radius cut into the cylinder-side face, height TBD against the cylinder body length — enough to land it visually, not so deep it becomes a cage. No restraint hardware. Per Derek's spec: "feels right when you set it down."

3. **The floor edge contribution (or not).** Whether the curve continues into the bottom edge of the panel (forming a foot-pocket for the cylinder base ring) or stops at panel height with a flat cabinet-floor surface below it. The floor-pocket option lands the cylinder more decisively but requires the panel to extend to the cabinet floor; the no-pocket option is simpler and lets the cylinder's own weight do the work.

4. **Condenser grille geometry on both side faces.** `future.md` "Enclosure layout" specifies straight-through airflow with intake on one side, exhaust on the opposite side. Grille slat angle, open-area fraction, dust-debris coexistence, print-slat orientation against the H2C nozzle direction — all named in `future.md` "Other metal candidates considered (decided against)" as "printed slats at a 0.4 mm or 0.2 mm nozzle handle the airflow geometry directly," but no CAD or part doc commits the geometry.

5. **Top-face hopper integral geometry.** `future.md` calls the top face "an integral funnel" feeding solenoid-selected paths down to the flavor reservoirs. The funnel is named, sized in prose ("large, covering most of the front half of the top face"), and given a removable silicone cover, but no part doc owns it. The hopper's geometry is downstream of the top-face panel's outer footprint.

6. **Side-wall cabinet plumbing coexistence.** Real kitchen sinks have P-traps, supply lines, garbage disposal cables, water-filter housings, dish soap dispensers — all sharing this same under-sink cabinet. The side-gap envelope has to live with whichever side the cylinder occupies. This is install-time guidance more than CAD, but it shapes the side-gap dimensional budget.

7. **Material + print orientation across surfaces.** PET-CF for the panels matches the back-panel's material rationale; side faces should match, but with airflow grille geometry the print orientation matters (slat overhang vs. nozzle direction). Owned in the new doc.

---

## What changes in the repo if this is executed

Per the third sibling's "what would this change" test:

- **New directory** under [`hardware/printed-parts/enclosure/`](../../hardware/printed-parts/enclosure/) for the missing surface(s). Scope question is open (see Recommendation R1).
- **New `README.md`** in that directory, capturing the seven items above, with sufficient design intent to start a `generate_step_cadquery.py` against.
- **Eventually** a `generate_step_cadquery.py` for the side face(s) and/or top face — print iteration against actual Derek-owned cylinder.
- **[`front-panel/README.md`](../../hardware/printed-parts/enclosure/front-panel/README.md) cross-ref** to the new doc for inlet-stub-height resolution (already added in this commit).
- **[`hardware/future.md`](../../hardware/future.md) cross-ref** to the new doc (already added in this commit).
- **No changes to plumbing or wiring docs** — none of them depend on exterior surface design.

---

## Recommendation

Three picks, in order. All reversible.

### R1 — Decide doc-scope shape first

Three plausible shapes for the missing doc(s):

- **(a) One `enclosure-shell/README.md` covering all six exterior surfaces** — front panel, back panel, side faces, top face, floor edge — with the existing `front-panel/`, `back-panel/`, `nameplate/` docs becoming sub-docs (or staying as-is, with `enclosure-shell/` cross-referencing them). Reads cleanly. Loses some isolation: a change to the cylinder-side curve doesn't need to know about the C14 AC inlet on the back panel.
- **(b) Per-face docs matching the existing pattern** — new `side-face-condenser/`, `side-face-quiet/`, `top-face/`, `floor-edge/` directories alongside `front-panel/`, `back-panel/`, `nameplate/`. Maximum isolation. Six docs to keep in sync at the surface seams.
- **(c) Hybrid — one new `side-faces/` doc covering both condenser grilles + cylinder-side curve + floor-edge contribution, plus a separate `top-face/` doc** for the hopper. Two new docs, scoped to coherent design intents.

Default recommendation: **(c)**. The side faces are a single coherent design problem (airflow + cylinder placement live on the same two surfaces, share the same material, share the same print constraints); the top face is a separate one (hopper geometry, user-pour ergonomics, solenoid-selected funnel exit). Splitting at that boundary keeps each doc small.

### R2 — Pick the cylinder side gap, with a stated rationale

Concrete decision in the new doc. Default recommendation: **opposite the condenser-active side**, on these grounds:

1. The condenser grille's open-area fraction is sensitive to whatever sits in its airflow path. A 5 lb cylinder body in the intake gap reduces face velocity at the grille; in the exhaust gap it scatters the exhaust plume into the cabinet (which may then warm the cylinder body, which slightly raises CO2 vapor pressure inside the cylinder — small effect but a real one).
2. The quiet side gap is empty space the appliance doesn't otherwise use. Filling it with the cylinder is the highest-and-best use of that volume.
3. Customer-side install: kitchen cabinet plumbing usually clusters on one side (P-trap, supply stubs). The cylinder should go on the side opposite the busy plumbing side. That side might or might not be the condenser-quiet side depending on the customer's kitchen — but for the appliance design, picking the quiet side as the cylinder home gives the install consult a single rule ("cylinder goes on the side without the condenser grilles, regardless of which way the appliance is oriented").

This rule pairs cleanly with the install-consult playbook gap from yesterday: install instructions become "rotate the appliance so the cylinder side aligns with your less-busy plumbing wall."

### R3 — Sketch the bottle curve in prose first, geometry second

In the new doc, write the design intent for the bottle-placement curve before opening CadQuery:

- Curve radius = cylinder body OD radius + 0.5–1 mm clearance.
- Curve span (vertical extent of the recess) ≈ 60–100 mm — enough to be visually obvious as "a cylinder goes here," not so much it reads as a cage. Cylinder body is ~12" / 305 mm; the curve lands at the mid-height of the body, not full-height.
- No restraint. No strap. No top tether. The cabinet walls + the cylinder's own weight do the work.
- Foot-pocket in the floor edge: open question per item 3 above.
- Curve smoothly transitioning into the rest of the side face (not a sharp pocket). Print orientation for the curve has to coexist with the condenser grille slats — whichever side the cylinder is on, that side has *only* the curve, not a grille (per R2: condenser is on the other side).

Then draft the CadQuery against the prose. Same convention as `front-panel/README.md` → eventual `generate_step_cadquery.py`.

---

## What this doc is *not* asking for

- Not asking to design the side faces, top face, or floor edge in this doc. The gap is that no doc owns those decisions yet; the recommendation is to create the doc, not to commit the geometry inside this gap-tracker file.
- Not asking to commit a restraint mechanism. Per operator correction during this run: bottle placement is a visual affordance only, not a retention mechanism. The new doc inherits that.
- Not asking to rewrite the existing front-panel, back-panel, or nameplate docs. They stay scoped to their surfaces. The new doc cross-references them where surfaces meet (corner seams, panel-to-side-face transitions).
- Not asking to commit a metal back panel, metal side panels, or any non-PET-CF exterior surface. `future.md` "Other metal candidates considered (decided against)" already resolved that.
- Not asking the front-panel to host any cylinder-related geometry. The cylinder is **beside**, not **in front**. The front panel hosts the inlet at the right height for the side-gap-resident cylinder's regulator, and that's it.

---

## The single thing

If this collapses to one sentence:

> The enclosure has six exterior surfaces, three of them undocumented; the most user-visible undocumented one is where the customer's CO2 cylinder lives — open a new document for the side faces + floor edge (and a separate one for the top-face hopper), pick which side gap the cylinder occupies, and sketch the bottle-shaped curve in prose before any geometry — so the next time someone reads the repo cold, the bottle-placement affordance has a home and isn't homeless across three other docs.

Everything else is implementation detail.
