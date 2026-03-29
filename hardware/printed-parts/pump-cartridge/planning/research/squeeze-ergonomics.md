# Squeeze Ergonomics Research

Research into the biomechanics and ergonomics of the palm-up squeeze gesture described in vision.md Section 3: the user squeezes two flat surfaces together, palm pushing against the cartridge body while fingers curl upward to pull the release surface.

## 1. Palm-Up Squeeze Force Capacity

### Maximum palmar pinch strength (standard test position)

The definitive normative data comes from Mathiowetz et al. (1985), a study of 310 males and 328 females ages 20-94. Palmar pinch (three-jaw chuck pinch: thumb pad against index and middle finger pads) is the closest standard grip type to the cartridge squeeze gesture.

**Palmar pinch strength, dominant hand (lbs), Mathiowetz et al. 1985:**

| Age | Male Mean +/- SD | Female Mean +/- SD |
|-----|-------------------|---------------------|
| 20-29 | 26.3 +/- 4.8 | 17.5 +/- 2.8 |
| 30-39 | 25.5 +/- 4.5 | 18.4 +/- 4.7 |
| 40-49 | 24.3 +/- 3.8 | 17.5 +/- 3.1 |
| 50-59 | 23.8 +/- 5.1 | 16.7 +/- 3.2 |
| 60-69 | 21.6 +/- 3.2 | 14.5 +/- 3.1 |

Source: University of Michigan Ergonomics Data (adapted from Mathiowetz V, et al. 1985. Grip and pinch strength: normative data for adults. Arch Phys Med Rehabil, 66(2), 69-74).

**Converted to Newtons (1 lb = 4.448 N):**

| Age | Male Mean | Female Mean |
|-----|-----------|-------------|
| 20-29 | 117 N | 78 N |
| 30-39 | 113 N | 82 N |
| 40-49 | 108 N | 78 N |
| 50-59 | 106 N | 74 N |
| 60-69 | 96 N | 64 N |

A separate Iranian population study (Rostamzadeh et al., PMC4411908) confirmed similar ranges: males 20-24 averaged 12.9 kg (127 N) palmar pinch, females 20-24 averaged 7.2 kg (71 N).

### 5th percentile design target

Consumer products must be usable by the weakest expected users. Using the female 60-69 age group (Mean 14.5 lbs, SD 3.1 lbs), the 5th percentile is approximately:

- 5th percentile = Mean - 1.645 * SD = 14.5 - 5.1 = **9.4 lbs = 42 N**

For younger females (20-29), 5th percentile = 17.5 - 1.645 * 2.8 = **12.9 lbs = 57 N**

**Design-for-all 5th percentile female maximum palmar pinch: approximately 42-57 N depending on target age range.**

### Effect of supinated (palm-up) forearm position

Richards et al. (1996, Am J Occup Ther, 50(2), 133-138) studied 106 subjects and found that grip strength in forearm supination was the strongest, followed by neutral, then pronation. The palm-up orientation described in the vision is biomechanically favorable -- supination engages the biceps brachii and brachioradialis, providing a stable platform for the palm to push against.

This means the palmar pinch norms above are conservative -- the supinated position may yield equal or slightly higher forces than the standard test position (which uses a neutral forearm position with elbow at 90 degrees).

### Important caveat: this is NOT standard palmar pinch

The cartridge squeeze gesture differs from standard palmar pinch testing:
- Standard test: thumb pad opposes index + middle finger pads, small object between them
- Cartridge gesture: entire palm surface pushes against a flat plate, while 4 finger pads curl and pull the opposing flat plate

The cartridge gesture is a hybrid between palmar pinch and a full-hand squeeze. The palm contact area is much larger than a thumb pad, and all four fingers contribute instead of two. This should yield forces **at least equal to** standard palmar pinch and potentially higher due to the full-hand engagement. The pinch values above represent a conservative lower bound.


## 2. Comfortable vs. Maximum Force Thresholds

### Force budget guidelines

For consumer product controls, ergonomics literature and standards establish these general thresholds:

| Force Level | Description | Application |
|-------------|-------------|-------------|
| < 5 N | Effortless, may feel accidental | Light buttons, touchscreens |
| 5-15 N | Light, deliberate, no strain | Keyboard keys, light switches, consumer latches |
| 15-30 N | Noticeable, requires intent | Squeeze bottles, child-resistant caps, deliberate releases |
| 30-50 N | Moderate effort, sustained use uncomfortable | Tool triggers, heavy latches |
| > 50 N | Strenuous for some users, not suitable for consumer appliances | Industrial controls |

Sources: Ergoweb force guidelines (maximum pinch force guideline: 9 lbs / 40 N; maximum push button force: 3 lbs / 13 N; palm button force: 1.9 lbs / 8 N). EN 894-3 covers control actuator force limits for machinery but does not provide specific squeeze-release values publicly.

### Design rule of thumb

A consumer product squeeze-release should require no more than **20-30% of the user's maximum voluntary contraction (MVC)** for a comfortable, repeatable action. Above 30% MVC, the action starts to feel effortful. Above 50% MVC, fatigue and discomfort appear quickly.

For the 5th percentile older female (42 N maximum):
- 20% MVC = **8 N** (effortless)
- 30% MVC = **13 N** (deliberate but comfortable)
- 50% MVC = **21 N** (upper comfortable limit)

For the 5th percentile younger female (57 N maximum):
- 20% MVC = **11 N**
- 30% MVC = **17 N**
- 50% MVC = **29 N**

### Recommended squeeze force target

**10-20 N is the target range for the cartridge squeeze mechanism.** This provides:
- A deliberate feel that prevents accidental release (above the 5 N accidental threshold)
- Comfortable operation for 95% of the adult female population (well below 30% MVC for the weakest users)
- A clear "I meant to do that" sensation without strain


## 3. Grip Span Considerations

### Optimal pinch span for maximum force

Cornell University ergonomics data (ergo.human.cornell.edu) states that pinch grip strength decreases rapidly at spans less than 25 mm (1") or greater than 76 mm (3"). Maximum pinch forces occur at spans between 13-38 mm.

### Comfortable pinch span by hand size

From CCOHS hand tool design guidelines and related literature:
- Small-to-medium hands: 50-55 mm comfortable grip span
- Larger hands: 55-65 mm
- Precision grip (pinch-type): 8-16 mm tool diameter, but this applies to cylindrical objects, not flat plates

### Application to the cartridge

The cartridge squeeze gesture uses flat parallel surfaces. The relevant dimension is the distance between the palm contact surface and the finger contact surface when the hand is wrapped around the cartridge in the palm-up position.

**Recommended cartridge squeeze span: 30-50 mm.** This range:
- Falls within the peak force generation zone (13-76 mm)
- Allows the fingers to curl comfortably around the cartridge body to reach the release surface
- Accommodates the 5th to 95th percentile hand span (true pinch span 5th %ile: 21 mm, 50th %ile: 43 mm, 95th %ile: 79 mm per Cornell data)
- A span of approximately 35-45 mm is the sweet spot where most adults can generate near-maximum pinch force comfortably

### Width vs. depth consideration

The "squeeze span" is the cartridge depth in the user's hand (front-to-back as the user faces the machine). The cartridge width (left-to-right) determines how many fingers engage. A wider cartridge allows more finger area but must still fit comfortably in one hand. Cartridge width should stay under 100 mm for comfortable one-hand grasp (CCOHS upper limit for grip tools).


## 4. Travel Distance for Satisfaction

### What makes a release feel deliberate

Mechanical switch and HMI design literature provides the closest analogs:

| Travel Range | Feel | Application |
|--------------|------|-------------|
| 0.5-1.0 mm | Too little -- feels twitchy, accidental activation risk | Membrane keypads |
| 1.0-2.0 mm | Light, quick, clearly actuated | Keyboard switches (Cherry MX actuation at 2 mm) |
| 2.0-4.0 mm | Deliberate, satisfying, full stroke feel | Keyboard full travel, consumer buttons |
| 4.0-8.0 mm | Very deliberate, latch/lever feel | Toggle switches, safety releases |
| > 8 mm | Laborious for repeated use | Industrial levers |

Source: Durgod mechanical switch design guides; keyboard switch research (PMC7606033 -- participants rated devices with 1.3-1.6 mm travel with least discomfort for repetitive tasks).

### Snap ratio for a satisfying feel

For consumer controls, a snap ratio around 50% with actuation force around 1.3 N (130 gf) is recommended for keypads. For a squeeze release mechanism, this translates to: the force should build, then give way noticeably when the collets release. The release plate should have a distinct "break-over" point.

### Recommended travel for the cartridge squeeze

**3-6 mm of squeeze travel** is recommended for the cartridge release. This provides:
- Enough travel to feel intentional (above the 2 mm accidental-feeling threshold)
- Not so much travel that it feels like operating a tool (below 8 mm)
- Sufficient stroke to mechanically actuate 4 collet releases through the release plate
- A travel distance compatible with the John Guest collet release mechanism (collets typically require 1-3 mm of axial depression)

The mechanism should have a perceptible force buildup followed by a release point -- the collets letting go creates a natural "click" that confirms the action.


## 5. Surface Area and Pressure Distribution

### Palm contact surface

The palm surface that pushes against the cartridge body is the thenar and hypothenar eminences plus the central palm. For a flat surface contact:

- Total palm surface area: males ~83 cm2, females ~64 cm2 (Kavakli et al., Turkish young adults study)
- Hand width: males ~85 mm, females ~72 mm
- Palm length: males ~98 mm, females ~89 mm

The cartridge body surface that the palm contacts does not need to match the full palm area. A contact surface of approximately **50-70 mm wide x 40-60 mm tall** (20-42 cm2) distributes force across the central palm and thenar/hypothenar eminences comfortably.

### Finger contact surface

The finger side of the squeeze engages the distal and middle phalanges of 4 fingers (index through pinky) curling upward. Each fingertip pad is approximately 10-15 mm wide x 10-15 mm long. Four fingers provide roughly **40-60 mm of contact width** and **10-15 mm of contact depth**.

A finger contact surface (the release plate's exposed edge or surface) of approximately **50-70 mm wide x 10-20 mm deep** allows all four finger pads to engage without cramping.

### Pressure distribution

At 15 N of squeeze force distributed across a 50 x 15 mm finger contact area (7.5 cm2):
- Average pressure = 15 / 7.5 = **2.0 N/cm2 = 20 kPa**

This is well below discomfort thresholds. For reference, sustained pressures above 50-100 kPa on finger pads cause discomfort, and above 200 kPa causes pain. A rounded or slightly convex finger contact surface further improves pressure distribution.

On the palm side at 15 N across a 50 x 40 mm surface (20 cm2):
- Average pressure = 15 / 20 = **0.75 N/cm2 = 7.5 kPa**

This is negligible -- the palm side will feel like resting the hand on a surface.


## 6. One-Handed vs. Two-Handed Operation

### The gesture as described in the vision

The user must simultaneously:
1. **Squeeze** the cartridge (palm pushes, fingers pull) to release the 4 collets
2. **Pull** the cartridge forward out of the dock (slide it off the tube stubs)

### Can one hand do both?

**Yes, with careful design, but it is marginal for weaker users.** Here is the analysis:

**In favor of one-handed operation:**
- The squeeze is a self-contained action within the hand (palm vs. fingers) -- it does not require the arm to push or pull
- Once the collets release, the same hand's arm pulls the cartridge forward while maintaining the squeeze
- The supinated (palm-up) position naturally aligns with a pulling motion (biceps engaged)
- Cartridges, ink tanks, and similar consumer products routinely use one-handed squeeze-and-pull removal

**Against one-handed operation:**
- The user must maintain squeeze force (to keep collets released) while also generating pull force (to slide the cartridge off the tubes)
- This splits attention and force between two concurrent actions
- Weaker users may struggle to maintain the squeeze while pulling
- If the tubes have significant friction (4 tubes with O-ring seals), the pull force adds to the total hand/arm effort

**Recommendation:** Design for one-handed operation as the primary mode, but ensure it works:
- Keep squeeze force low (10-20 N target) so maintaining it while pulling is not fatiguing
- Minimize tube extraction friction (chamfered tube stubs, smooth collet release)
- Consider a **latch or detent** on the release plate so the user can squeeze once, the plate latches in the released position, and then the user pulls the cartridge out without needing to maintain squeeze force. Re-insertion pushes the latch back. This completely eliminates the simultaneous squeeze-and-pull problem.
- If a latch is not feasible, ensure the total combined effort (squeeze + pull) stays below 30 N for the weakest expected user


## 7. Force Budget Summary

### User-side force budget (what the human can provide)

| Parameter | Design Value | Basis |
|-----------|-------------|-------|
| Maximum available squeeze force (5th %ile older female) | 42 N | Mathiowetz 1985, female 60-69, -1.645 SD |
| Maximum available squeeze force (5th %ile younger female) | 57 N | Mathiowetz 1985, female 20-29, -1.645 SD |
| Target squeeze force for comfortable operation | 10-20 N | 20-30% MVC of weakest user |
| Comfortable grip span | 30-50 mm | Cornell/CCOHS data, peak force zone |
| Squeeze travel | 3-6 mm | HMI/switch design literature |
| Palm contact area | 50-70 mm x 40-60 mm | Hand anthropometry |
| Finger contact area | 50-70 mm x 10-20 mm | Finger pad dimensions x 4 fingers |

### Mechanism-side force budget (what the mechanism must overcome)

The release plate must depress 4 John Guest collets simultaneously. The total collet release force (to be determined by separate collet force research) must be **well below the 10-20 N user target** after accounting for mechanical advantage.

If the total 4-collet release force is C Newtons:
- At 1:1 mechanical advantage, C must be < 10-20 N
- If C exceeds 20 N, a lever or cam mechanism is needed to provide mechanical advantage
- Available mechanical advantage from a 5 mm travel squeeze acting on a 2 mm collet depression = up to 2.5:1 geometric advantage, meaning the mechanism could overcome up to 25-50 N of collet force while keeping user effort at 10-20 N

### Design equation

```
User squeeze force (10-20 N) x Mechanical advantage (1:1 to 2.5:1)
    >= 4 x Single collet release force + Friction losses

Solving for allowable single collet force:
    At 1:1 MA, 15 N user force: single collet <= 3.75 N (minus friction)
    At 2:1 MA, 15 N user force: single collet <= 7.5 N (minus friction)
    At 2.5:1 MA, 15 N user force: single collet <= 9.4 N (minus friction)
```

## Sources

1. Mathiowetz V, Kashman N, Volland G, Weber K, Dowe M, Rogers S. (1985). Grip and pinch strength: normative data for adults. Arch Phys Med Rehabil, 66(2), 69-74.
2. Richards L, Olson B, Palmiter-Thomas P. (1996). How forearm position affects grip strength. Am J Occup Ther, 50(2), 133-138.
3. Rostamzadeh S, Saremi M, Taheri F. (2020). Normative data of grip and pinch strengths in healthy adults of Iranian population. PMC4411908.
4. Cornell University Ergonomics Web. Manual Materials Handling -- Hand Grip Data. ergo.human.cornell.edu.
5. Canadian Centre for Occupational Health and Safety (CCOHS). Hand Tool Ergonomics -- Tool Design. ccohs.ca.
6. Ergoweb LLC. Force Guidelines. ergoweb.com.
7. Kavakli A. Determination of hand and palm surface areas as a percentage of body surface area in Turkish young adults. oatext.com.
8. Durgod. What is Travel Distance of a Mechanical Keyboard Switch. durgod.com.
9. PMC7606033. Going Short: The Effects of Short Travel Key Switches on Typing Performance. 2020.
10. Mekoprint. Tactile Feedback HMI Design Guide Series. mekoprint.com.
