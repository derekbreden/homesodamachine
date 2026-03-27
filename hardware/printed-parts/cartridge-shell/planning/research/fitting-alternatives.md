# Fluid Fitting Alternatives for Cartridge Dock

Survey of every viable option for the 4 fluid connections between the removable pump cartridge and the dock. The chosen approach is John Guest push-to-connect with a cam lever release plate.

**Application:** Food-grade flavor concentrate, <5 PSI, ~30-60 ml/min, 1/4" OD tubing, connect/disconnect once per 18-36 months.

---

## Options Evaluated

### A. John Guest Push-to-Connect -- $8 for 4

**How it works:** Tube pushes in past collet teeth + O-ring. To disconnect, push collet inward while pulling tube out.

| Spec | Value |
|---|---|
| Body profile | Barbell: 9.31mm center body, 15.10mm body ends (caliper-verified) |
| Body length (union) | 39.13mm collets compressed / 41.80mm collets extended (caliper-verified) |
| Insertion depth | ~15-18mm per side |
| Cost (PI0408S) | ~$2 each, $8 for 4 |
| Food safety | NSF 61 (potable water) |
| Disconnect method | Two-handed (push collet + pull tube) |
| Intuitiveness | Requires learning the collet push -- non-obvious after a 2-year gap |
| Release mechanism needed? | **Yes** -- 4 simultaneous collet releases require cam lever / release plate |

**Pros:** Cheap, proven in beverage applications, NSF 61 certified, ubiquitous availability. The cam lever release plate provides a single-motion disconnect for all 4 fittings simultaneously.
**Cons:** Non-intuitive bare disconnect (mitigated by the cam lever), requires the release mechanism for simultaneous 4-fitting disconnect.

### B. Barb Fittings with Hose Clamps -- $5 for 4

Cheapest option. Push silicone tubing over a barbed nipple.

| Spec | Value |
|---|---|
| Cost | $0.75-$2.50 per connection, $3-10 total |
| Food safety | FDA compliant materials |
| Disconnect method | Twist and pull hard -- requires significant force |
| Intuitiveness | **Poor** -- pulling tubing off a barb is non-obvious and physically difficult |
| Release mechanism needed? | No, but disconnection is unacceptable for a consumer product |

**Not recommended.** The disconnect experience is unacceptable for a consumer product.

### C. Luer Lock -- $12 for 4

Medical/lab fittings. Tapered male cone into female socket with quarter-turn threaded lock collar.

| Spec | Value |
|---|---|
| Bore | ~2.5-2.9mm (significant flow restriction from 6.35mm tube) |
| Cost | $1-6 per pair, $4-24 total |
| Food safety | FDA compliant materials (medical-grade) |
| Disconnect method | Twist collar and pull -- intuitive (widely understood paradigm) |
| Intuitiveness | **Good** -- twist-to-unlock is universally understood |
| Release mechanism needed? | No -- individual twist-off per connection |

**Concern:** The ~2.5-2.9mm bore is an 80% flow area reduction from 1/4" tubing. May not matter at 30-60 ml/min but adds unnecessary restriction.

### D. SMC Pneumatic Push-to-Connect -- $17 for 4

Functionally identical to John Guest but from the industrial pneumatics market.

- Standard KQ2 series: **NOT food-safe certified**
- FDA-compliant KQG2-F series: $15-30 per fitting (much more expensive)
- Same two-handed disconnect problem as John Guest
- **Not recommended over John Guest** -- same UX weakness, higher cost, no food cert on affordable series.

### E. Custom 3D-Printed Bayonet -- ~$1 for 4 (O-rings only)

Quarter-turn bayonet integrated into the 3D-printed cartridge body with O-ring seals.

| Spec | Value |
|---|---|
| Cost | ~$0.20-1.00 (O-rings only; cartridge body is already being printed) |
| Food safety | **FDM layer lines harbor bacteria** -- not certifiable for food contact |
| Disconnect method | Quarter-turn and pull |
| Intuitiveness | Fair -- user must know direction and amount of turn |
| Release mechanism needed? | No -- bayonet IS the mechanism |

**Risks:** FDM tolerance (+/-0.2mm) is marginal for O-ring sealing. Bayonet tabs may crack under torsional load at layer lines. Good for prototyping, not for production without injection molding.

### F. Magnetic Coupling with O-Ring -- ~$15 for 4

Neodymium magnets self-align and pull cartridge into dock. O-rings seal the fluid path.

| Spec | Value |
|---|---|
| Cost | $10-25 total (magnets + O-rings + custom design) |
| Food safety | Achievable if magnets are isolated from fluid path |
| Disconnect method | Pull straight out -- magnets release |
| Intuitiveness | **Excellent** -- push in (self-aligns), pull out. Zero learning curve. |
| Release mechanism needed? | No -- pull overcomes magnetic force |

**Risks:** Magnetic force must be carefully balanced (strong enough to seal, weak enough to pull apart). May attract metallic debris. May interfere with pogo pins or sensors. No precedent in food/beverage equipment. Fully custom design -- no off-the-shelf product exists.

### G. Press-Fit / Friction Fit with O-Ring -- ~$2 for 4

Cylindrical stubs push into close-tolerance bores. O-rings provide sealing and frictional retention. No locking mechanism.

| Spec | Value |
|---|---|
| Cost | $0.20-1.00 (O-rings only) + dock bore machining/molding |
| Food safety | FDA compliant with standard food-grade materials |
| Disconnect method | Pull straight out -- O-ring friction releases |
| Intuitiveness | **Very good** -- push in, pull out. Nearly as intuitive as magnetic. |
| Release mechanism needed? | No -- cartridge simply slides in and out |

**Risk:** No positive locking. Vibration, bumps, or accidental contact could partially unseat connections and cause leaks. Mitigation: guide rails with a detent/latch on the cartridge housing (not on the fittings themselves).

---

## Cross-Cutting Comparison

### Which eliminate the cam lever / release plate?

| Eliminates release mechanism | Options |
|---|---|
| Yes | C (Luer), E (Bayonet), F (Magnetic), G (Press-Fit) |
| No -- requires release mechanism | A (John Guest), D (SMC) |

Only John Guest and SMC push-to-connect fittings require the release plate because their collets must be individually depressed for disconnection. **Every other option eliminates this mechanism entirely.**

### Intuitiveness Ranking (for a 2-year-gap user)

| Rank | Option | Why |
|---|---|---|
| 1 | F. Magnetic | Push in (self-aligns), pull out. Zero learning curve. |
| 2 | G. Press-Fit | Push in, pull out. Nearly as intuitive but no self-alignment. |
| 3 | C. Luer Lock | Twist-to-unlock is a widely understood paradigm. |
| 4 | E. Bayonet | Twist-lock but user must know direction and amount. |
| 5 | B. Barb | Push on is obvious; pulling off is difficult and confusing. |
| 6 | A/D. JG/SMC | Push-in is easy; disconnect requires non-obvious collet push. |

---

## Summary Matrix

| Criterion | A. JG | B. Barb | C. Luer | E. Bayonet | F. Magnetic | G. Press-Fit |
|---|---|---|---|---|---|---|
| **Cost (4x)** | $8 | $5 | $12 | $1 | $15 | $2 |
| **Intuitiveness** | Poor (bare) / Good (cam lever) | Poor | Good | Fair | Excellent | Very Good |
| **One-hand disconnect** | Yes (cam lever) | No | Yes | Yes | Yes | Yes |
| **Food cert** | NSF 61 | FDA mat'l | FDA mat'l | No | Custom | FDA mat'l |
| **Eliminates lever** | No | Yes | Yes | Yes | Yes | Yes |
| **Off-the-shelf** | Yes | Yes | Yes | No | No | Partial |
| **Connection reliability** | High | Moderate | High | Low-Med | Med-High | Medium |
| **Production-ready** | Yes | Yes | Yes | No | No | Yes |

---

## Decision: John Guest Push-to-Connect

John Guest 1/4" push-to-connect fittings are the chosen approach. The rationale:

1. **Cost.** $8 for 4 fittings is the cheapest off-the-shelf option with food-grade certification. The cam lever and release plate add ~$5-10, bringing the total to $13-18 -- still far cheaper than any alternative with comparable reliability.

2. **Proven in beverage applications.** JG fittings are the industry standard for residential water filtration, ice makers, and RO systems. NSF 61 certified for potable water contact.

3. **Ubiquitous availability.** Available from Amazon, Home Depot, plumbing supply houses. No specialty sourcing required.

4. **Cam lever release plate gives simultaneous disconnect.** The release plate with four stepped bores engages all 4 body ends at once. Flipping the lever is a single motion that releases all connections -- solving the "non-intuitive collet push" problem that would otherwise make JG fittings a poor UX choice.

5. **High connection reliability.** Collet grip provides ~20N retention across 4 fittings. The cam lever adds an over-center lock that prevents vibration-induced withdrawal over the 18-36 month service interval.

### Why alternatives were not chosen

- **Barb fittings:** Unacceptable disconnect experience for a consumer product.
- **Luer Lock:** 80% flow area reduction from the ~2.5mm bore. Unnecessary restriction.
- **SMC pneumatic:** Same mechanism as JG but more expensive and no food cert on affordable series.
- **3D-printed bayonet:** FDM layer lines are not food-safe. Tolerance marginal for O-ring sealing.
- **Magnetic coupling:** No off-the-shelf product exists. Fully custom design with no beverage industry precedent. Magnetic force balance is difficult to get right.
- **Press-fit with O-ring:** No positive locking. Vibration could unseat connections over 18-36 months.

### Implications for Other Design Documents

- `cam-lever.md`, `collet-release.md`, `release-plate.md` -- all relevant and describe the JG release mechanism
- `mating-face.md` -- 4 JG fittings on the dock back wall in a 2x2 grid, barbell profile (9.31mm center body / 15.10mm body ends), 40mm horizontal x 28mm vertical center-to-center
- Cartridge rear face carries 4 tube stubs (1/4" OD hard nylon, ~30mm protrusion)
- The cam lever on the cartridge front face drives the release plate via push rod
