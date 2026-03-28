# Enclosure Construction Decision

## Recommendation: ASA + Solvent Weld + Acetone Vapor Smooth

Print both enclosure halves in **unfilled ASA**. Join them permanently with an **acetone solvent weld** along a tongue-and-groove perimeter, reinforced by **permanent snap-fits** on the interior. After assembly, **acetone vapor smooth** the entire enclosure to eliminate both layer lines and the seam simultaneously. Finish with a **matte 2K urethane clear coat** for durability and the dark satin appearance consistent with the product's design language.

---

## 1. Material: ASA (Unfilled)

### Why ASA

ASA is the only material in the H2C's supported set that satisfies all three requirements simultaneously:

- **Acetone-soluble** -- enables true molecular solvent welding (not adhesive bonding) and acetone vapor smoothing. This is the single capability that makes the entire strategy work. PLA, PETG, PA, and PC are all incompatible with acetone.
- **UV-stable and impact-resistant** -- designed as outdoor-grade ABS. The enclosure may live on a countertop near a window or under a sink. ASA will not yellow, become brittle, or degrade.
- **Matte surface off the printer** -- ASA's inherent matte finish is the closest any unfilled FDM material gets to a consumer product surface before post-processing. Even if vapor smoothing were skipped, ASA reads as "engineered product" rather than "3D print."
- **Fully supported by the H2C** -- the H2C's active chamber heating system is specifically designed for ASA/ABS, controlling chamber temperature to prevent warping on large parts. This is the printer's core competency.

### Why not ASA-CF

ASA-CF was the surface-finish research document's primary recommendation for raw off-the-printer appearance, and it is a legitimate choice. However, the carbon fibers in ASA-CF do not dissolve in acetone. This creates two problems:

1. **Vapor smoothing produces uneven results** -- the ASA matrix smooths around the fibers, leaving a textured surface rather than the glossy injection-molded finish that unfilled ASA achieves. Community reports on Bambu's ASA-CF specifically note that vapor smoothing is unreliable with their filled formulations.
2. **Solvent welding is weakened** -- fiber-filled joints have less polymer-to-polymer contact area at the weld interface. The weld is still functional but not as clean as unfilled-to-unfilled.

ASA-CF is the right answer if the plan is to skip all post-processing and accept a matte textured finish. But the design patterns research makes clear that premium consumer products present smooth, uniform surfaces. The enclosure should look injection-molded, not CNC-milled-from-composite. Unfilled ASA with vapor smoothing achieves that.

### Why not ABS

ABS is functionally identical to ASA for acetone smoothing and solvent welding. The only difference is UV stability -- ABS yellows and becomes brittle with UV exposure. Since the enclosure may sit on a countertop with indirect sunlight, ASA's UV resistance eliminates a failure mode at no trade-off.

### Print settings

- Layer height: **0.12 mm** -- balances print time against surface quality. Vapor smoothing eliminates layer lines regardless, but starting from 0.12 mm means less acetone exposure is needed (lower risk of dimensional distortion on a large part).
- Ironing: **enabled on top surfaces** -- improves the starting surface quality of flat panels before vapor smoothing.
- Wall count: **4-5 walls** -- structural integrity for an enclosure, and the vapor smoothing only affects the outermost fraction of a millimeter.
- Infill: **20-30% gyroid** -- adequate structural support without excessive material that increases warping stress.
- Brim: **5-8 mm outer brim** on both halves -- prevents corner lifting on the 300+ mm print footprint.
- Chamber heating: **active**, per Bambu's ASA profile.

---

## 2. Joining: Acetone Solvent Weld + Interior Snap-Fits

### Primary bond: Acetone solvent weld

The two enclosure halves meet along a tongue-and-groove perimeter joint. Acetone is applied to both mating surfaces with a fine brush, dissolving the outer molecular layer. The halves are pressed together and held until the acetone evaporates and the polymer chains re-entangle across the interface.

This is not glue. It is a molecular weld -- the same polymer on both sides dissolves and re-solidifies as a single continuous material. CNC Kitchen testing measured ABS acetone welds at 17 MPa, compared to 19 MPa for the interlayer adhesion of ABS itself. In 2 of 3 samples, the test part broke next to the bond rather than at it. ASA behaves identically.

The critical advantage for this project: because there is no adhesive layer with a different refractive index, color, or texture, the weld line is the same material as the surrounding surface. When the assembled enclosure is vapor smoothed, the seam dissolves along with the layer lines. It becomes physically invisible.

### Structural reinforcement: Permanent snap-fits

The weld carries the cosmetic burden (invisible seam). The snap-fits carry the structural burden (mechanical retention). Permanent snap-fits with 90-degree catch angles lock the halves together with a positive mechanical interlock that requires destruction to separate. ASA has adequate ductility for snap-fit assembly (2-4% strain tolerance).

The snap-fits are entirely interior -- they do not appear on any external surface. Their purpose is to ensure the enclosure remains rigid even if the weld were to crack from an impact or drop (it should not, but defense in depth costs nothing in this context).

### Joint geometry

- **Tongue-and-groove perimeter**: self-aligning, increases bonded surface area, controls solvent application to the interior of the joint rather than the visible exterior.
- **Seam placement along a geometric edge**: per the design patterns research (Theme 1), the seam line between halves should coincide with a deliberate design line -- a chamfer, a step, or a material transition. Even though vapor smoothing should make the seam invisible, designing the parting line as an intentional feature provides a fallback if any trace remains.

---

## 3. Surface Finishing: Acetone Vapor Smooth + 2K Matte Clear Coat

### Step 1: Acetone vapor smoothing (after assembly)

The fully assembled enclosure is placed in a sealed container with acetone vapor for 15-45 minutes. The vapor dissolves the outermost molecular layer uniformly across the entire surface, causing it to self-level. Layer lines, seam lines, and minor surface defects all flow together and re-solidify as a smooth, glossy surface.

Expected results:
- Surface roughness reduction: 70-80%
- Ra from ~15 um (raw ASA at 0.12 mm) to ~3-5 um (vapor smoothed)
- Layer lines: eliminated
- Seam line at joint: eliminated (same material, same process)
- Dimensional change: +0.05 to +0.15 mm per surface (acceptable; design tolerances accommodate this)

For a part this large (~220 x 300 x 400 mm), the vapor chamber must be proportionally large. A large glass or metal container (e.g., a stainless steel pot or a glass aquarium) with a sealed lid works. Cold vapor (acetone-soaked paper towels on the bottom, part suspended on a wire rack above) is safer and more controllable than heated vapor for large parts, reducing the risk of over-exposure and warping on flat surfaces.

### Step 2: Light sanding (600-800 grit)

After vapor smoothing and 2-4 hours of curing in open air, a light hand-sand with 600-800 grit removes any minor glossy irregularities from uneven vapor exposure. This takes 10-15 minutes and provides a uniform matte surface for the clear coat to adhere to.

### Step 3: Matte 2K urethane clear coat

Two to three light coats of SprayMax 2K matte clear coat. This provides:

- **Durability**: automotive-grade scratch and chemical resistance. The finish will outlast the electronics inside.
- **UV protection**: the clear coat adds a UV barrier on top of ASA's inherent UV stability.
- **Matte/satin appearance**: consistent with the #1a1a2e dark navy design language. A matte finish is also more forgiving of any residual micro-imperfections than gloss.
- **Permanent surface**: unlike epoxy coatings, 2K urethane does not yellow, chip, or peel under normal indoor/under-sink conditions.

The clear coat is applied over ASA's natural dark color (printing in a dark navy or black ASA filament). No spray paint layer is needed unless the exact #1a1a2e tone cannot be matched with available ASA filament colors. Dark ASA filaments from Polymaker, eSUN, and others are available in matte black and dark gray; the clear coat's matte finish unifies the final appearance regardless of the exact filament shade.

### Why this sequence works as a system

The three choices are not independent -- they form a closed loop:

1. **ASA** is chosen because it is the only material that is both solvent-weldable and vapor-smoothable with the same chemical (acetone).
2. **Acetone solvent welding** is chosen because it creates a joint that is molecularly identical to the parent material, which means vapor smoothing erases it.
3. **Acetone vapor smoothing** is chosen because it eliminates both layer lines and the weld seam in a single hands-off step, and only works on ASA (and ABS).
4. **2K clear coat** is chosen because it protects the vapor-smoothed surface without adding the labor of a full primer + paint workflow.

Remove any one element and the system degrades. Switch to PETG and you lose solvent welding and vapor smoothing. Switch to CA glue and the seam survives vapor smoothing (different material at the joint). Switch to primer + paint instead of vapor smoothing and you add a full weekend of sanding labor. The four choices are coupled because they share the same chemistry.

---

## Bill of Materials

### Filament

| Item | Qty | Notes |
|------|-----|-------|
| ASA filament, dark (black or dark gray), 1 kg spool | 2-3 | Polymaker PolyLite ASA, eSUN ASA, or Bambu ASA. Match color across spools. |

### Joining consumables

| Item | Qty | Notes |
|------|-----|-------|
| Acetone (hardware store) | 1 quart | Used for both solvent welding and vapor smoothing |
| Fine-tip applicator brushes | Pack of 10 | For controlled acetone application to weld joint |
| Nitrile gloves | Box | Acetone degrades latex; use nitrile |
| Organic vapor respirator (3M 6200 + 6001 cartridges) | 1 | Required for both welding and vapor smoothing |

### Surface finishing consumables

| Item | Qty | Notes |
|------|-----|-------|
| Glass or metal container with sealable lid (large enough for enclosure half) | 1 | Vapor smoothing chamber. Stainless pot, glass aquarium, or similar. Must fit ~300 x 220 x 200 mm. |
| Wire rack or clips | 1 set | To suspend part above acetone pool |
| Paper towels | Roll | Acetone-soaked, placed in bottom of chamber |
| Sandpaper, 600 grit | 3 sheets | Post-smoothing prep |
| Sandpaper, 800 grit | 3 sheets | Post-smoothing prep |
| SprayMax 2K Matte Clear Coat | 2 cans | Two cans ensures enough for 2-3 coats on both halves. Activated by twisting the can's internal catalyst -- single-use per can once activated, so plan to coat both halves in one session per can. |
| Tack cloth | 2 | Dust removal before clear coat |

### Printing consumables (per H2C requirements)

| Item | Qty | Notes |
|------|-----|-------|
| Hardened steel nozzle 0.4 mm | 0 | Not required for unfilled ASA (only needed for CF variants). Standard brass nozzle is fine. |
| Bambu liquid glue stick | 1 | Bed adhesion for ASA |

---

## What Would Change This Recommendation

### If ASA warps unacceptably on the H2C at enclosure scale

The enclosure halves are at or near the H2C's build volume limits (~300 x 220 mm footprint per half). If large flat sections warp despite the H2C's active chamber heating, the fallback is:

**Split each half into 2-3 sub-panels** and solvent-weld them together before the final two-half assembly. More weld seams, but vapor smoothing erases them all equally. This adds labor but does not change the material or finishing strategy.

Alternatively, if warping is severe and splitting is insufficient: **switch to PETG + Weld-On 16 (dichloromethane) + filler primer + paint**. This is the fallback from the joining research. It works, but requires a full sand-prime-paint workflow because PETG cannot be vapor smoothed. The seam is hidden by paint rather than by chemistry. It is a significantly longer process.

### If vapor smoothing distorts the enclosure geometry

Large flat panels are the highest-risk geometry for vapor smoothing -- the softened surface can sag or warp under its own weight. If test pieces show dimensional distortion:

1. **Reduce exposure time** and accept a semi-smooth rather than fully glossy result. Even partial smoothing significantly reduces layer line visibility.
2. **Smooth each half separately before assembly**, then solvent-weld. This means the weld seam is not vapor-smoothed, but if the seam is on a designed geometric edge (Theme 1 from design patterns), a slight visible line at a deliberate crease is acceptable.
3. **Switch to the ASA-CF no-post-processing path** -- accept the matte carbon fiber texture as the product finish. This is a legitimate consumer product aesthetic, just a different one.

### If the dark navy color (#1a1a2e) cannot be matched with available ASA filament

Add a **spray paint step** between vapor smoothing and clear coat: sand (600 grit) after smoothing, apply 2-3 coats of color-matched spray paint, then 2K clear coat. This adds one step and about 2 hours of drying time but achieves exact color matching. The SprayMax 2K system is available in custom-mixed colors from automotive paint suppliers.

### If Bambu's ASA formulation does not vapor smooth cleanly

The Bambu forum thread on ASA-CF noted that Bambu's ASA/ABS formulations contain additives that can interfere with vapor smoothing. If Bambu's ASA specifically is problematic:

**Use a third-party ASA** (Polymaker PolyLite ASA, eSUN ASA+) which are widely documented to vapor smooth cleanly. Third-party filaments are fully supported on the H2C via custom profiles in Bambu Studio.
