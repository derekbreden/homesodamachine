# Integral spring capture feasibility

The proposed **19 mm integral external sleeve cannot follow the existing carrier assembly path**. Its operating geometry can clear after a retaining-rim relief, but its overlap with a closed moving bore prevents the final sideways seating of each carrier half. The existing aft guide shoulder blocks the additional axial travel that would disengage it.

A **permanently closed moving cup with the existing fixed cup** has a clear native loading route using a temporary flat-ended pusher. This requires no spring-ID measurement and no additional retained part. It is the simplest spring-capture candidate in this study. The native model does not establish that the spring will remain straight or that hand compression will be comfortable.

Short **complementary integral arc guards** can clear the existing sideways seating motion, but the tested pair only bounds a rigid outside-diameter envelope where the arcs overlap. Its open end regions still need capture surfaces, and those surfaces introduce additional reliefs and assembly constraints. The arcs remain exploratory.

All files here are a separate feasibility study. **No production source, physical coupon, slice or print is released.** The sleeve blocker uses the matched archived fixture in `../inputs/`. The closed-cup and arc checks also use the independently rebuilt front-top preserved in `frozen-front-top/`, SHA-256 `63471e1fa49233b281b6334ec3ef82c73a3abe8c635eb537c4f38e2a2e6e5508`. Its matching carrier and nearby hardware are frozen in `current-inputs/manifest.json`. The `current-` filenames identify this snapshot; they do not assert that production placement is current. The new measured tee branch dimensions and selected G Ganen pump require rebase.

## External sleeve

| Interface | Hypothesis |
|---|---:|
| Spring outside diameter / free length | 6 / 27 mm, reported by Derek |
| Fixed sleeve ID / wall / OD | 6.57 / 1.30 / 9.17 mm |
| Fixed sleeve projection | 19 mm |
| Moving bore ID / depth | 9.67 / 11.10 mm |
| Sleeve-to-moving-bore radial air | 0.25 mm |
| Spring-floor separation, release / connected / aft stop | 19.50 / 21.65 / 24.15 mm |
| Sleeve overlap, release / connected / aft stop | 10.60 / 8.45 / 5.95 mm |
| Sleeve tip-to-floor air, release / connected / aft stop | 0.50 / 2.65 / 5.15 mm |

The unrelieved retaining rim intersects the sleeve by **19.248 mm³ per side** at every operating state. Continuing the Ø9.67 relief through the rim's 6.15 mm fore projection clears that interference. The modified halves and fixed shell remain single valid solids; release, connected and aft-stop poses have no modeled overlap with the matched fixed shell, cartridge or cap. The added sleeve clears the archived cartridge's complete 100 mm vertical bounding sweep.

The assembly obstruction remains. Each half approaches the wall opening **3.25 mm inboard**, then seats outward at the **4.65 mm aft stop**. A closed bore around the sleeve permits only **0.25 mm parallel axis offset**. At the prescribed inboard pose, the sleeve intersects the carrier by **165.412 mm³ per side**. Even the lower-bound alternative with the bore mouth behind the sleeve needs **10.85 mm aft offset**, **6.20 mm past the stop**; its upper retaining rim intersects the actual aft shoulder by **55.800 mm³**. The guide shoulder is retained, not cut away to make that path appear clear.

The same contradiction applies to the current declared stations: at maximum travel the moving mouth is **13.05 mm behind the fixed floor**. Positive continuous overlap requires a rigid sleeve longer than 13.05 mm, while the existing lateral entry requires its tip to clear that closed mouth. This is a restriction of the established assembly path and retained guides, not a claim that every different integral mechanism is impossible.

## Stock, neighboring hardware and spring alignment

The enlarged bore leaves **1.70 mm** minimum inboard bar stock; the rim relief leaves **1.88 mm** radial outer stock. The current native comparison removes no upper/lower flat guide-bearing stock, main web/flange/central-joint stock within |X| ≤90 mm, or material behind the spring floor. It does remove material locally in the spring bar and rim.

Thin native section readings show that the added window closure increases the root section's geometric bending term at X91.5–93.5 by approximately **5.7–14.2%**, while the larger bore/rim relief reduces that term at X97.535 and X101.8 by approximately **1.4% and 3.0%**. Sections at X40 and X90 are unchanged. These are converged local section comparisons, **not assembled rigidity or allowable-load measurements**. Print structure, contact play, torsion and material properties are not assigned values.

At the frozen pack placement, the sleeve's nearest modeled hardware/tube is `fluid-13`/`fluid-23`, **6.811 mm** away. Added window stock is **4.562 mm** from the nearest tube at the nominal connected pose. These local sleeve checks exclude the front-top and do not replace a final dynamic assembly check. The separate plain closed-cup path is checked against the rebuilt frozen front-top below.

A Ø9.67 moving bore also leaves **1.835 mm radial freedom** around the Ø6 spring beyond the sleeve tip, over as much as **5.15 mm** of end length. Enclosing a spring is not the same as centering its moving end. A narrow integral end cup would use some tip clearance and requires a separate design check; it is not silently assumed in these results.

## Closed moving cup with the existing fixed cup

This candidate permanently fills the inboard loading window while preserving the original Ø6.57 teardrop bore, its **11.10 mm moving-cup depth**, and the fixed **2.00 mm cup**. The closure adds material and does not enlarge the bore or cut guide/bearing surfaces.

One tested loading route is clear on both sides of both native fixtures: the matched archived wall and the independently rebuilt, frozen front-top.

1. Put the spring in the moving cup while the half is accessible. A temporary flat-ended pusher holds it at **12.15 mm** length. Its geometry is an access probe: a **Ø6.3 ×0.6 mm** tip and **10 ×1 mm** inboard handle.
2. Carry the half, held spring and pusher through the existing rear entry, lowering, approach to the wall shoulder, forward slide and outward seating. Both valve rows are absent, as in the authored installation sequence. The right-side checks include the parked left half.
3. Move the pusher inboard to the outer well, lift it and withdraw it through the open rear. The modeled coaxial spring expansion from the held position into the fixed cup is clear. Nothing from the pusher stays in the assembly.
4. Join the two halves at the aft stop and verify the spring ends seat and remain aligned through release and connected travel.

The probe checks 264 native readings across four held lengths and both sides. The **12.15 mm case clears the complete tested path**. Longer held lengths fail this particular pusher approach or withdrawal route; that does not establish a unique loading length or exclude a differently shaped tool. The actual pusher's stiffness, grip and compression effort are unqualified.

The added closure material also clears conservative continuous enclosing sweeps for rear entry, lowering, shoulder approach, the fore slide and the outward seating motion against the rebuilt frozen wall. Both complete modified halves are single valid solids and clear that wall at release, connected and aft-stop poses. The right-side delta checks include the parked left half. This is additional-stock and tool access evidence; the original carrier guide path is a separate check. Valves are absent during installation. Neither the selected water pump nor the revised tee placement is qualified by this fixture.

The spring is compressed **14.85 mm from its 27 mm free length** while held. Its reported compressed length is about 7 mm, so this case does not approach that reported limit. No spring rate or force is inferred from those lengths. A clear cylindrical expansion envelope does not prove that the released spring follows that envelope without bowing.

| Carrier state | Spring length | Open span between cup mouths |
|---|---:|---:|
| Release | 19.50 mm | 6.40 mm |
| Connected | 21.65 mm | 8.55 mm |
| Aft stop | 24.15 mm | 11.05 mm |

The two closed cups provide positive end walls under a coaxial spring, but there is no intermediate lateral guide across that open span. A representative physical trial must establish controlled loading/release, both ends staying seated, and no problematic lateral bowing through full travel and unequal-hand operation. Those observations decide whether an additional guide is useful. The existing one-plug study remains an alternative; this review does not make it mandatory.

## Complementary integral arc guards

The small native probe uses a **110° fixed inboard arc** and a **110° moving outboard arc**, each projecting **13.50 mm** from its own spring floor. Both use Ø6.57 inside / 1.30 mm wall / Ø9.17 outside geometry. They retain the exact frozen floor separation and working travel.

| Geometric reading | Result |
|---|---:|
| Arc overlap at release / connected / aft stop | 7.50 / 5.35 / 2.85 mm |
| Minimum arc-to-arc air through the entire 3.25 mm sideways seating | 0.518 mm |
| Chord across each angular opening where both arcs overlap | 3.768 mm |
| Held spring length for the assembly probe | 9.61 mm |
| Held spring's fore end behind the fixed arc tip | 1.04 mm |

The guard-to-guard clearance is continuous: their projected X intervals remain disjoint at every offset between 3.25 and 0 mm. The held Ø6.5 spring clearance envelope also clears the fixed guard. Keeping 19 mm guards would leave only **5.15 mm** behind the fixed tip at the seating pose, below the reported approximately 7 mm compressed spring length. Shortening the arcs is necessary for this loading approach.

The moving arc clears the rebuilt frozen front-top at release, connected, aft stop and the inboard assembly pose, on both sides. The fixed arc intersects the unmodified moving carrier's lower window lip: **1.116 mm³ per side at release**, **0.646 mm³ connected**, **0.098 mm³ at the aft stop** and **0.122 mm³ at the inboard assembly pose**. The exact affected bounds are recorded. The raw interference reaches approximately **0.471 mm below the existing loading-window floor**. It is localized outside the main joint/web and the upper/lower flat guide-bearing regions. A manufactured relief must also provide motion clearance; it removes lower-lip stock and creates a local notch. The relief is **not implemented**, and its remaining stock, local stress and assembled rigidity are unqualified. The enlarged-bore section results above do not apply to this different arc modification.

The 3.768 mm angular opening is narrower than an undeformed Ø6 cylinder only in the arc-overlap region. With the existing 2 mm fixed cup and open moving loading window, the single-arc end regions remain open in the guard geometry. At the aft stop, their axial lengths reach **8.65 mm near the fixed end** and **9.55 mm near the moving end**, both larger than the spring OD. The rest of the native carrier can bound some directions; those guard-only lengths do not by themselves establish a complete escape path.

A separate native probe checks the moving-end opening directly: a **Ø6 rigid ball can travel 10 mm inboard** through the loading window at the aft stop, clear of the original carrier, both proposed arcs and the rebuilt frozen front-top on both sides. Its continuous swept capsule is clear, with 1.775 mm axial air to the fixed arc tip and to the end of the loading window. This establishes an open local lane, not that a complete spring will bend into it or unseat. The initial arc pair is not a complete enclosure of the spring length.

An analytical extension with **5.75 mm closed cups at both ends** would reduce the axial openings to **0.25 / 2.40 / 4.90 mm** through the three stops. It also needs a local fore-rim relief for the larger fixed cup, a partial loading-window closure, and a verified pusher withdrawal lane. That extension was not built or tested. The smaller openings still would not prove that flexible coil wire cannot escape. No stiffness, spring-rate, manual-force or endurance claim follows from the dimensions.

## Assembly and complexity

The plain closed-cup candidate adds broad material to the carrier and retains the original bore. It requires one controlled spring-compression and temporary-pusher withdrawal operation for each spring, with no permanent plug, guide or spring-ID feature. The remaining uncertainty is physical spring stability across the open middle span.

The arc approach adds interleaving surfaces, clearance reliefs and more end-capture details. The initial geometry is feasible locally but provides insufficient end-region enclosure. It is not the preferred answer merely because it can be made to fit an existing carrier.

These findings do not require retaining the present joint or either carrier half. A simpler carrier can use broad, substantial walls and a simple joint based on the physically successful faucet display cover, while the spring cups are evaluated independently. Native checks from the existing two-half path establish access evidence for that path only; they do not settle a new carrier's architecture. All physical coupons remain held during that revision and the tee-datum rebase.

The bounded [continuous-carrier study](single-carrier-route/README.md) examines removing the centre joint entirely. A virtual bottom opening admits the continuous carrier with closed cups, but putting its removed guide stock directly on front-bottom blocks the shell's existing Y-slide closure. One broad stationary keeper attached to front-top remains an architectural candidate; its connection and stiffness need design and full-width physical evaluation.

## Reproduction and scope

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/evaluate.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/check_current.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/closed_cup_loading.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/closed_cup_loading.py --current
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/closed_cup_stock.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/arc_guard_probe.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/spring-capture-study/telescoping-feasibility/arc_end_opening.py
```

`checks.json` records the sleeve motion, native assembly obstruction and retained stock. `current-checks.json` records the local enlarged-bore carrier sections and frozen nearby hardware. `closed-cup-checks.json` and `current-closed-cup-checks.json` record the temporary-pusher access probes, including failures and clear cases. `current-closed-cup-stock-checks.json` records the closure's continuous assembly sweeps and complete operating poses. `arc-guard-checks.json` records the limited arc topology probe; `arc-end-opening-checks.json` records the open moving-end lane. Input and artifact manifests carry byte digests.

The STEP coupons are local native sections for inspection. They are not sliced or released print fixtures and do not reproduce full-width joint rigidity. A rebase to the measured tee, a complete production assembly audit, an actual support-removal review and a physical spring trial remain necessary before adoption. The sleeve/cup bores have straight extraction mouths before installation; no production support body or removal effort is qualified here.
