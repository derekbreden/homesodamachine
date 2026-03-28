# Surface Finish Research for FDM-Printed Enclosure

Printer: Bambu Lab H2C. Goal: consumer-product-grade appearance — the enclosure should look injection-molded or CNC-machined, not 3D-printed.

---

## 1. Print Settings Optimization (Pre-Processing)

### Layer Height

| Layer Height | Ra (typical) | Visual Result | Print Time Impact |
|-------------|-------------|---------------|-------------------|
| 0.20 mm | 15-25 um | Visible stair-stepping on curves, acceptable on vertical walls | Baseline |
| 0.12 mm | 8-15 um | Reduced stair-stepping, still visible on close inspection | ~1.7x baseline |
| 0.08 mm | 5-10 um | Minimal stair-stepping, smooth to casual touch | ~2.5x baseline |

Layer lines are most visible on curved and angled surfaces. Vertical walls look similar at any height because the lines stack directly on top of each other. For the enclosure's curved transitions and top surfaces, 0.08-0.12 mm is the practical range where further reduction yields diminishing returns.

The H2C supports layer heights down to 0.08 mm (100 um minimum documented, but 80 um is achievable with a 0.4 mm nozzle).

### Ironing

Ironing is a slicer feature (available in Bambu Studio) where the nozzle re-traces the top surface at the same Z height with minimal extrusion, re-melting and smoothing the top layer.

- **What it does**: Fills gaps between top-surface lines, creating a flat, near-glossy top surface
- **Limitation**: Only effective on flat horizontal top surfaces. Does nothing for side walls or curves.
- **Materials**: Works with all thermoplastics (PLA, PETG, ABS, ASA, etc.)
- **Time cost**: Adds 10-30% to total print time depending on top surface area
- **Dimensional impact**: None (operates at existing layer height)
- **Best for**: Flat panels (the enclosure top panel, for example)
- **Layer lines after treatment**: Eliminated on top surface only; side walls unchanged

### Line Width and Perimeter Count

Using a wider line width (e.g., 0.5 mm with a 0.4 mm nozzle) slightly reduces the number of visible perimeter boundaries. More perimeters (4-5 instead of 2-3) improve outer surface consistency. Neither eliminates layer lines but both contribute to a cleaner baseline.

---

## 2. Material Selection (Inherent Finish Quality)

### Best Materials Off the Printer — Ranked

#### Tier 1: Best inherent surface finish

**Carbon Fiber Reinforced Filaments (PLA-CF, PETG-CF, PA-CF, ASA-CF)**
- The short carbon fibers create a fine, uniform matte texture that masks layer lines significantly
- The matte finish reads as "engineered product" rather than "3D print"
- NylonX (PA-CF) and similar CF-nylon blends are documented as requiring zero post-processing for a production-ready appearance
- Layer lines are still physically present but visually suppressed by the surface texture
- Drawback: abrasive to brass nozzles (requires hardened steel nozzle, which the H2C supports)
- Drawback: inter-layer adhesion can be slightly weaker than unfilled versions
- **Best match for this project**: ASA-CF or PETG-CF — combines the matte professional look with the mechanical and environmental properties needed for a kitchen appliance

**ASA (Acrylonitrile Styrene Acrylate)**
- Inherently matte finish that hides layer lines better than PLA or PETG
- UV-stable, weather-resistant, impact-resistant — originally designed as outdoor ABS
- Layer lines visible on close inspection but the matte surface makes them less obvious
- Acetone-smoothable (see Section 3)
- Prints at 240-260C, needs enclosed chamber (H2C is fully enclosed)
- **The professional matte finish is the closest any unfilled FDM material gets to "consumer product" off the bed**

**Silk PLA**
- Glossy, metallic-like sheen straight off the printer
- The high-gloss surface actually makes layer lines slightly more visible than standard PLA under raking light, but the overall "material impression" reads as premium
- Not suitable for functional enclosure parts: PLA has low heat resistance (55-60C glass transition), poor impact resistance, and no UV stability
- Best reserved for decorative non-structural pieces only
- **Not recommended for this project** due to PLA's mechanical limitations

#### Tier 2: Acceptable with post-processing

**PETG**
- Semi-glossy finish, decent layer adhesion
- Layer lines clearly visible, slightly glossy which can make them more noticeable
- Good chemical resistance, moderate heat resistance (~80C)
- Harder to sand than PLA or ABS

**ABS**
- Similar to ASA but without UV stability
- Matte finish, acetone-smoothable
- Enclosure use is viable if not exposed to sunlight

#### Tier 3: Not recommended for visible surfaces

**Standard PLA** — glossy finish highlights layer lines, low heat resistance, brittle
**PA (Nylon)** — excellent strength but hygroscopic, warps, difficult to finish
**PC (Polycarbonate)** — high-performance but very difficult to print with good surface quality

### Recommendation for This Project

**Primary choice: ASA-CF** — matte professional finish, UV-stable, acetone-smoothable if needed, strong, food-adjacent safe (not food-contact but enclosure exterior only). The carbon fiber texture makes it look like a product material rather than a printing material.

**Fallback: ASA** (unfilled) — same benefits minus the CF texture masking, but opens up vapor smoothing as a primary finishing strategy.

---

## 3. Acetone Vapor Smoothing (ABS / ASA / ASA-CF)

### Technique

The part is suspended in a sealed container above a small pool of acetone. The acetone vapor dissolves the outermost molecular layer of the plastic, causing it to flow and self-level before re-solidifying as the part is removed and the acetone evaporates.

### Process

1. Print part in ABS, ASA, or compatible material
2. Place part on a raised platform inside a sealed glass or metal container
3. Add acetone to the bottom (or heat it gently to accelerate vapor production)
4. Expose for 10-60 minutes depending on desired smoothness
5. Remove and let cure in open air for 2-4 hours

### Results

| Metric | Value |
|--------|-------|
| Ra reduction | 70-80% (from ~15 um to ~3-5 um typical) |
| Best documented result | 0.30 um Ra (with controlled multi-cycle process) |
| Layer line visibility | Eliminated at optimal exposure; faint ghost lines possible if under-exposed |
| Dimensional change | +0.05 to +0.15 mm per surface (material flows outward); sharp edges radius slightly |
| Strength impact | Surface layer becomes denser but overall tensile strength may decrease 5-15% |

### Compatible Materials

- ABS — excellent
- ASA — excellent
- HIPS — good
- PC (polycarbonate) — partial
- PMMA — good
- **PLA, PETG, PA, TPU — not compatible**

### Tools and Consumables

- Acetone (hardware store, ~$8/quart)
- Glass or metal container with lid
- Wire rack or clips to suspend part
- Optional: small heater or heat gun for controlled vapor generation
- Ventilation or fume hood (acetone vapor is flammable and an irritant)

### Scalability

Excellent for repeatability — the process is hands-off once set up. Multiple parts can be smoothed simultaneously. The main variable is exposure time, which can be calibrated with test pieces. For the two-half enclosure, both halves can be smoothed in the same batch.

### Durability

The smoothed surface is the same material as the part — no coating to chip or peel. Durability is equivalent to the base material. ASA parts remain UV-stable after smoothing.

### Limitations

- Cannot smooth PLA or PETG
- Over-exposure destroys fine features and lettering
- Dimensional accuracy degrades with longer exposure
- Carbon fiber filled variants smooth less uniformly because the fibers don't dissolve — the resin matrix smooths around them, creating a slightly textured-but-smooth surface (which can actually be desirable)

---

## 4. Filler Primer + Paint (Universal Technique)

### Technique

Sand the raw print, apply automotive filler primer to fill layer lines, sand again, then apply paint and clear coat. This is the most proven path to true injection-mold appearance on any FDM material.

### Process

1. Sand raw print: 120 grit to knock down major lines, 220 grit to refine
2. Apply automotive filler primer (Rust-Oleum Filler Primer or similar): 2-3 coats, light sanding (400 grit) between coats
3. Inspect under raking light — repeat filler primer + sand if lines still visible
4. Apply color coat: 2-3 light coats of spray paint
5. Apply clear coat: 2-3 coats of 2K automotive urethane clear coat for durability
6. Optional: wet sand with 1500-2000 grit, then polish for mirror finish

### Results

| Metric | Value |
|--------|-------|
| Final Ra | < 1 um achievable (with thorough sanding through 1200 grit before primer) |
| Layer line visibility | Completely eliminated — indistinguishable from injection molding |
| Dimensional change | +0.1 to +0.3 mm per surface (primer + paint thickness) |
| Total thickness added | ~50-150 um per coat of filler primer; ~25-50 um per coat of paint |

### Compatible Materials

All FDM materials. PLA, PETG, ABS, ASA, PA, PC — all accept primer and paint. Some materials (PLA, PETG) benefit from a plastic adhesion promoter before primer.

### Tools and Consumables

- Sandpaper: 120, 220, 400, 600, 800 grit minimum
- Filler primer (Rust-Oleum Automotive Filler Primer, ~$8/can)
- Spray paint in desired color (~$5-12/can)
- 2K clear coat (SprayMax 2K, ~$20/can) — the 2K urethane is far more durable than 1K acrylic clear
- Sanding block or sponge
- Tack cloth
- Optional: wet/dry sandpaper 1000-2000 grit for final polish

### Time and Effort

- Initial sanding: 15-30 min per part
- Primer cycles (2-3 coats + sanding): 2-4 hours (mostly drying time)
- Paint + clear coat: 1-2 hours (mostly drying time)
- Total active labor: ~1-2 hours per part
- Total calendar time: 1-2 days (drying/curing between coats)

### Scalability

Moderate. Each part requires manual sanding, which is the bottleneck. Spray application scales well (multiple parts in one session). For a two-part enclosure, expect a full weekend of intermittent work.

### Durability

With 2K urethane clear coat, the finish is extremely durable:
- Scratch-resistant (automotive grade)
- UV-stable
- Chemical-resistant (won't yellow or degrade)
- Withstands handling and light impacts

Without 2K clear (using regular spray clear), durability drops significantly — scratches easily, yellows over time.

### Color Considerations for This Project

The vision document specifies a dark navy theme (#1a1a2e). A matte or satin black/dark navy spray paint + matte clear coat would match the design language. Matte finishes are also more forgiving of minor surface imperfections than gloss.

---

## 5. XTC-3D Epoxy Coating

### Technique

XTC-3D is a two-part epoxy resin (made by Smooth-On) specifically formulated for coating 3D prints. It is brushed on, self-levels, and fills layer lines as it cures.

### Process

1. Mix Part A and Part B (2:1 ratio by volume)
2. Brush onto print surface — working time is ~10 minutes
3. The epoxy self-levels, filling layer lines and minor surface defects
4. Cure time: 2-4 hours at room temperature
5. Optional: sand cured surface (400-600 grit) and apply a second coat for deeper lines
6. Can be painted or clear-coated after curing

### Results

| Metric | Value |
|--------|-------|
| Layer line visibility | Significantly reduced in one coat; near-eliminated in two coats (at 0.1 mm layer height) |
| Surface quality | Glossy, smooth — user reports describe parts at 0.1 mm layer height as having barely visible lines after one coat |
| Dimensional change | +0.1 to +0.5 mm per surface depending on application thickness |
| Coverage | ~100 sq inches per ounce |

### Compatible Materials

PLA, ABS, ASA, PETG, powder prints, and most other rigid FDM materials.

### Tools and Consumables

- XTC-3D kit: 6.4 oz (~$18), 24 oz (~$30)
- Disposable brushes
- Mixing cups and stir sticks
- Gloves (epoxy is a skin sensitizer)
- Optional: heat gun to pop bubbles during application

### Time and Effort

- Application: 10-15 minutes per part
- Cure: 2-4 hours
- Total: significantly less labor than sanding + primer + paint
- One of the fastest paths from raw print to smooth surface

### Scalability

Good for one-off and small batches. The 10-minute working time means you must work quickly on large parts. For the enclosure halves (~220x300 mm panels), you would need to work efficiently but it is feasible.

### Durability

Moderate. The epoxy coating is hard and scratch-resistant when cured, but:
- Not UV-stable without a UV-protective clear coat on top
- Can yellow over time with sun exposure
- Less scratch-resistant than 2K urethane or Cerakote
- Good for indoor products; adequate for this under-counter application

### Limitations

- Adds more dimensional variance than primer/paint (epoxy pools in recesses)
- Difficult to get perfectly uniform thickness on complex geometry
- Brush marks possible if not applied carefully (though the self-leveling formulation minimizes this)
- Cannot be vapor-smoothed after application

---

## 6. Cerakote Ceramic Coating

### Technique

Cerakote is a polymer-ceramic composite coating sprayed via HVLP gun and cured (air-cure or oven-cure depending on formulation). It is the industry standard for professional finishing of 3D-printed parts in production contexts.

### Process

1. Sand and clean part surface
2. Apply Cerakote via HVLP spray gun in thin, even coats
3. Air-cure (H-series) or oven-cure (C-series, typically 250F/120C — too hot for PLA, fine for ABS/ASA/PETG/PA)
4. Multiple coats for full coverage

### Results

| Metric | Value |
|--------|-------|
| Coating thickness | 12-25 um (0.0005-0.001 inches) per coat |
| Layer line visibility | Significantly reduced but not fully eliminated by the coating alone — pre-sanding is still needed for line-free results |
| Scratch resistance | ASTM D4060 tested — lasts ~24x longer than competitive coatings |
| Dimensional change | Minimal (+12-25 um per surface per coat) — suitable for tight tolerances |

### Compatible Materials

All FDM plastics. Oven-cure variants require materials with glass transition above 120C (ABS, ASA, PA, PC — not PLA).

### Tools and Consumables

- Cerakote coating (~$30-50 per color, small kit)
- HVLP spray gun
- Air compressor
- Sandpaper for surface prep
- Oven (for C-series cure)
- Over 150 color options available

### Properties

- Extreme scratch and abrasion resistance
- Chemical resistant
- UV stable
- Hydrophobic
- Thin application preserves dimensional accuracy

### Time and Effort

- Prep: 30-60 min (sanding, cleaning)
- Application: 15-30 min
- Cure: 1-2 hours (air-cure) or oven cycle
- Total: comparable to paint, but requires spray equipment

### Scalability

Excellent for production runs — the process is industrial-grade and highly repeatable. For a one-off project, the equipment investment (HVLP gun + compressor) is the barrier, but the per-part finish quality is unmatched.

### Durability

The most durable option on this list. Cerakote is used on firearms, automotive parts, and industrial tooling. For a kitchen appliance enclosure, it is extreme overkill in the best possible way — the finish will outlast every other component in the device.

---

## 7. Hydrographic Film (Water Transfer Printing)

### Technique

A printed film is floated on water, activated with a solvent, and the part is dipped through the film. The pattern wraps conformally around the part surface.

### Process

1. Sand and prime the part (white primer for best pattern clarity)
2. Apply base coat in desired color
3. Float hydrographic film on water surface in a dip tank
4. Spray activator on the film
5. Dip part slowly through the film surface
6. Rinse, dry, and apply clear coat

### Results

| Metric | Value |
|--------|-------|
| Layer line visibility | Film conforms to surface geometry — lines visible through the film if not sanded/primed first |
| Pattern options | Carbon fiber, wood grain, marble, camouflage, abstract — hundreds of patterns available |
| Dimensional change | +0.1-0.3 mm (primer + clear coat, similar to paint process) |

### Compatible Materials

All FDM materials after priming. The film adheres to the primer/base coat, not the raw plastic.

### Tools and Consumables

- Hydrographic film (~$15-30 per meter)
- Dip tank (large enough for the part — a plastic storage container works)
- Activator spray (~$15-25)
- Primer and base coat
- Clear coat
- Warm water (80-90F)

### Time and Effort

- Prep (sand + prime + base coat): 2-3 hours with drying
- Dip: 5-10 minutes
- Clear coat: 30 min + drying
- Total: similar to primer + paint, with the dip step added

### Scalability

Good for repeatable patterns. Once set up, multiple parts can be dipped sequentially. The film is inexpensive.

### Durability

Dependent entirely on the clear coat applied over the film. With 2K urethane clear, durability is excellent. Without clear coat, the film is fragile and peels.

### Relevance to This Project

Hydrographic film makes most sense for decorative patterns (carbon fiber look, wood grain, etc.). For a solid dark navy product finish, primer + paint or Cerakote is simpler and more consistent. Hydro dip is best if you want the enclosure to have a textured visual pattern without the cost of multi-material printing.

---

## Comparison Matrix

| Approach | Layer Lines Eliminated? | Ra Achievable | Dimensional Change | Time (per part) | Skill Required | Durability | Materials |
|----------|------------------------|---------------|-------------------|-----------------|----------------|------------|-----------|
| Print settings only (0.08mm + ironing) | Reduced, not eliminated | 5-10 um | None | Print time only | Low | Base material | All |
| Material choice (ASA-CF) | Visually masked | 8-15 um (masked by texture) | None | Print time only | Low | Excellent (UV, impact) | CF-filled only |
| Acetone vapor smoothing | Yes (ABS/ASA) | 0.3-5 um | +0.05-0.15 mm/surface | 1-4 hours | Medium | Base material | ABS, ASA, HIPS, PMMA |
| Filler primer + paint + 2K clear | Yes (completely) | < 1 um | +0.1-0.3 mm/surface | 1-2 days | Medium-High | Excellent with 2K clear | All |
| XTC-3D epoxy | Mostly (1-2 coats) | 1-3 um | +0.1-0.5 mm/surface | 3-5 hours | Low-Medium | Moderate (indoor) | All rigid |
| Cerakote | With pre-sand, yes | < 1 um | +0.012-0.025 mm/coat | 3-4 hours | High (spray equipment) | Best on this list | All (oven-cure limits PLA) |
| Hydrographic film | With pre-sand + prime, yes | Depends on prep | +0.1-0.3 mm/surface | 3-5 hours | Medium | Good with clear coat | All (after priming) |

---

## Recommended Strategy for This Project

### Approach: ASA + Acetone Vapor Smoothing + Matte Clear Coat

This combination is recommended for the enclosure based on the project's constraints and values:

1. **Print in ASA at 0.12 mm layer height** — ASA's matte finish and acetone compatibility make it the ideal base material. The 0.12 mm layer height balances print time against surface quality (the vapor smoothing handles the rest). The H2C's enclosed chamber handles ASA's warping tendency.

2. **Acetone vapor smooth both enclosure halves** — eliminates layer lines chemically rather than mechanically. No manual sanding needed. The process is repeatable and consistent.

3. **Light sand (600 grit) after smoothing** — removes any minor glossy spots or irregularities from the vapor process.

4. **Apply matte or satin 2K clear coat** — protects the smoothed surface, provides the dark matte finish consistent with the #1a1a2e design language, and gives automotive-grade durability.

### Why Not the Alternatives?

- **ASA-CF**: The carbon fiber texture looks great but prevents uniform vapor smoothing. If a matte textured look (rather than smooth) is acceptable, ASA-CF with no post-processing is the fastest path.
- **Filler primer + paint**: More labor-intensive than vapor smoothing for the same result. Makes sense if you want a specific color that can't be achieved with tinted ASA + clear coat.
- **XTC-3D**: Good for quick results but adds more dimensional variance and less durable than vapor smoothing + clear coat.
- **Cerakote**: Best possible finish but requires HVLP equipment investment for a one-off project.
- **Hydrographic**: Pattern-oriented; not needed for a solid-color product.

### Alternative Approach: ASA-CF, No Post-Processing

If the timeline or effort budget is tight, printing in ASA-CF at 0.08 mm layer height with ironing on flat surfaces produces a result that reads as "engineered product" without any post-processing. The matte carbon fiber texture is a legitimate product finish used by consumer electronics companies. This trades "injection-mold smooth" for "CNC-machined composite" — both are valid consumer product aesthetics.
