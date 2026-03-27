# Hardware Store Bolt Approach -- Twist/Screw Release Mechanism

Research document for using a standard metric bolt as the threaded strut in the cartridge twist-release mechanism. Covers bolt selection, thread interface with the release plate, knob design, rear wall bearing, specific product recommendations, assembly, failure modes, and force analysis.

## System Context

- Release plate: 59W x 47H x 6D mm, PETG, 4 stepped bores in 2x2 grid (40mm H x 28mm V center-to-center)
- Required plate travel: ~3mm (1.3mm collet travel + 1.7mm margin)
- Plate guided by 2x 3mm steel dowel pins with return springs
- Strut spans ~122mm from rear wall (Y=126) to front wall (Y=4)
- Cartridge envelope: 148W x 130D x 80H mm
- Rear wall: 4mm thick PETG at Y=126-130
- Front wall: 4mm thick PETG at Y=0-4
- Total actuation force: ~12-20N (4 collets at ~3-5N each)
- Must be food-safe (potable water contact possible)
- One-handed operable in a dark under-sink cabinet

---

## 1. Bolt/Rod Selection

### Thread Size Comparison

| Parameter | M6 x 1.0 (coarse) | M8 x 1.25 (coarse) | M8 x 1.0 (fine) |
|---|---|---|---|
| Thread pitch | 1.0 mm | 1.25 mm | 1.0 mm |
| Turns for 3mm travel | 3.0 turns | 2.4 turns | 3.0 turns |
| Shaft diameter | 6 mm | 8 mm | 8 mm |
| Hex head across flats | 10 mm | 13 mm | 13 mm |
| Rigidity over 122mm span | Adequate (low lateral load) | Better | Better |
| Availability at hardware stores | Excellent | Excellent | Poor (specialty) |
| Matching nut/insert availability | Excellent | Excellent | Poor |
| Heat-set insert availability | Excellent (ruthex RX-M6x12.7) | Excellent (ruthex RX-M8x12.7) | Rare |

### Recommendation: M6 x 1.0 (coarse)

**M6 x 1.0 coarse is the best choice.** Rationale:

1. **3 turns for 3mm travel is ideal.** Three full turns is enough to feel intentional (prevents accidental release from vibration) but fast enough to not be tedious. At roughly 1 second per turn, that is a 3-second release -- comparable to the cam lever it replaces.

2. **Availability.** M6 x 1.0 coarse is the most common M6 thread worldwide. Every hardware store stocks it. Fine-pitch M8 x 1.0 would give the same turns-per-mm but is a specialty item.

3. **6mm shaft is adequate.** The bolt carries only axial tension (~20N) and negligible lateral load (the dowel pins handle all lateral guidance). A 6mm 304 stainless rod has a tensile strength of roughly 21 kN -- the 20N actuation load is 0.1% of capacity. Bending stiffness is more than sufficient for the supported-at-both-ends configuration.

4. **Smaller hole in walls.** A 6mm bore through the front and rear walls preserves more wall material than an 8mm bore. In a 4mm thick PETG wall, every millimeter matters for structural integrity around the hole.

5. **Lighter.** A 150mm M6 stainless bolt weighs about 28g vs 50g for M8. Not critical, but no reason to be heavier.

### Required Length

The bolt must span from the front knob face through the front wall (4mm), across the interior (122mm), through the rear wall (4mm), and thread into the release plate nut/insert. Total path:

- Knob engagement: ~10mm (bolt head captured inside knob)
- Front wall + bushing: ~6mm
- Interior span: 122mm
- Rear wall + bushing: ~6mm
- Thread engagement in release plate: ~6mm (into heat-set insert)

**Total: ~150mm.** An M6 x 150mm fully threaded bolt is the right size. This is a standard catalog length.

### Material

**304 stainless steel (A2).** This is the standard "stainless steel" at hardware stores. It is:

- FDA-accepted for food contact surfaces
- NSF/ANSI 51 listed for food equipment
- Corrosion resistant in potable water
- Non-magnetic (mostly -- cold working can induce slight magnetism)

316 stainless (A4) has better corrosion resistance but is harder to find at hardware stores and unnecessary for potable water with infrequent exposure. 304 is the right call for availability and cost.

### Head Style

**Socket head cap screw (SHCS) is preferred over hex head.** Reasons:

- The cylindrical head embeds neatly inside a 3D-printed knob cavity
- The hex socket (4mm for M6) provides anti-rotation when the knob is tightened/loosened
- A hex head would need a hex pocket in the knob, which is harder to print cleanly than a cylindrical recess
- SHCS are available in 304 stainless at the same lengths

However, **hex head bolts are far more available at Home Depot in long lengths.** Socket head cap screws above 80mm are uncommon at brick-and-mortar stores and typically require online ordering (McMaster-Carr, Amazon, Bolt Depot).

**Practical compromise:** Use a hex head bolt. The hex head sits in a hex pocket in the knob, which actually provides excellent anti-rotation. Hex pockets are easy to model and print well if oriented correctly (hex flat on bed).

---

## 2. Nut/Thread Interface at the Release Plate

The bolt must engage the 6mm-thick PETG release plate to pull it forward (toward the user) when the knob is turned. Three options:

### Option A: Heat-Set Brass Insert (Recommended)

A brass heat-set threaded insert is pressed into the release plate using a soldering iron. The bolt threads directly into the brass insert.

**Product: ruthex RX-M6x12.7**
- Internal thread: M6
- Length: 12.7mm
- Outer diameter: ~8.7mm (knurled)
- Pilot hole for PETG: ~8.0-8.2mm diameter
- Material: brass

**Problem: The release plate is only 6mm thick, but the insert is 12.7mm long.**

Solutions:
1. **Blind hole from the back face.** The insert sits proud of the plate's rear face by ~6.7mm. This is acceptable because the insert faces into the cartridge interior where there is plenty of clearance. The insert only needs to be captured by the plate, not flush with it.
2. **Use a shorter insert.** Prusa sells M6 heat-set inserts at 9.5mm length (still proud by 3.5mm). Or cut a standard insert to length on a lathe.
3. **Local boss.** Add a cylindrical boss on the rear face of the release plate around the insert hole, extending the local wall thickness to 12-13mm. This is the cleanest solution -- the boss provides full insert embedment. A 15mm diameter x 12.7mm tall boss adds negligible weight and prints easily.

**Recommendation: Option 3 (local boss).** Model a cylindrical boss on the release plate rear face: 15mm OD, 12.7mm tall, with an 8.0mm pilot hole. The ruthex M6 insert heat-sets fully into this boss. The bolt threads into solid brass with 12.7mm of engagement -- far more than needed for the 20N load.

**Advantages of heat-set insert:**
- Brass threads are durable and resist cross-threading
- Excellent pull-out strength in PETG (rated 500N+ per CNC Kitchen testing)
- Easy installation with a soldering iron at 245C
- No epoxy or adhesive needed
- Repairable -- a damaged insert can be melted out and replaced

### Option B: Captured Hex Nut

A standard M6 hex nut sits in a hex pocket on the rear face of the release plate. The nut is captured by the pocket geometry and cannot rotate (the pocket matches the hex profile). The bolt threads through the plate and into the nut.

**Advantages:**
- Zero specialized tooling (no soldering iron)
- Stainless steel nut matches the bolt material
- Easy to replace

**Disadvantages:**
- M6 hex nut is 5mm thick. With only 6mm plate thickness, the hex pocket must be 5mm deep, leaving only 1mm of PETG behind it. This is structurally marginal.
- The nut can rattle if the hex pocket has any play
- Requires a through-hole in the plate (the bolt must pass all the way through to reach the nut)

This option works but is less elegant than the heat-set insert. The thin remaining wall (1mm) is a concern for long-term durability under repeated loading.

### Option C: Tapped Hole in PETG (Not Recommended)

Tap M6 x 1.0 threads directly into the PETG plate.

**Why this fails:**
- 6mm of PETG thread engagement gives only 6 threads at 1.0mm pitch
- PETG threads wear rapidly under repeated load cycles
- Cross-threading risk is high because plastic threads deform easily
- No practical way to repair stripped threads without reprinting the plate

**Verdict: Do not tap threads directly in PETG for a load-bearing, frequently-cycled connection.**

### Anti-Rotation

The release plate is constrained against rotation by the two 3mm dowel pins sliding in slots. The bolt/insert interface only needs to handle axial load (tension to pull the plate forward, compression from the return springs pushing it back). No torque is transmitted through the nut/insert -- all rotational force stays in the bolt/knob system. This means thread engagement strength is the only concern, not anti-rotation features on the insert itself.

---

## 3. Knob Design

### Basic Configuration

The knob is a 3D-printed PETG part that captures the bolt head. The user grips the knob and turns it. The bolt rotates inside the knob but cannot translate relative to it -- the knob is the "bearing" that converts rotation to axial pull.

### Bolt Capture Method

The bolt passes through the front wall from the interior. The bolt head sits inside a cavity in the knob. A retaining feature prevents the bolt from pulling back through the knob.

Two approaches:

**A. Hex pocket capture (for hex head bolt):**
```
    Cross-section (front wall at right, knob at left):

    ┌──────────────┐  ┌────┐  ┌───────────
    │   knob body  │  │wall│  │  interior
    │  ┌────────┐  │  │    │  │
    │  │hex head│  │  │ ○  │  │  ← bolt shaft
    │  │captured│  │  │    │  │    passes through
    │  └────────┘  │  │    │  │    wall
    │   retainer   │  │    │  │
    └──────────────┘  └────┘  └───────────
```

The hex pocket prevents the bolt head from rotating relative to the knob. A snap-fit retainer ring or printed cap holds the bolt head in the pocket. The knob and bolt rotate together.

**B. Through-bolt with knob nut:**
The bolt passes entirely through the knob. A second nut (or another heat-set insert) on the outer face of the knob captures it. This is simpler to assemble but puts a nut on the exposed face, which is less clean.

**Recommendation: Hex pocket capture (Option A).** Print the knob in two pieces -- a main body with the hex pocket and a thin cap that snaps or screws on to retain the bolt head. Or print as one piece with the bolt inserted during assembly (the hex pocket is a blind recess accessed from the wall side of the knob, and the knob slides onto the bolt before the bolt is inserted through the wall).

### Ergonomics

| Parameter | Value | Rationale |
|---|---|---|
| Outer diameter | 35-40mm | Comfortable one-handed grip, clears adjacent surfaces in a cabinet |
| Height/depth | 15-20mm | Enough to grip without being bulky |
| Surface texture | Knurled ribs (0.8-1.0mm deep, 2mm pitch) | Printable on FDM, provides grip in wet/oily conditions |
| Shape | Cylindrical with flat top | Can be turned from any angle, no orientation needed |
| Flats or wings | Optional 2 opposing flats or wings | Aids grip for wet hands, provides visual rotation feedback |

A 38mm diameter knob with 6 radial fins (like a star/handwheel) is another option. Fins provide excellent grip and clear visual feedback on rotation position. They print well standing upright.

### Dual-Purpose: Knob as Pull Handle

The knob could double as the cartridge pull handle for withdrawal after release. Requirements:

- Must provide a secure grip for pulling the cartridge straight back (~1.8 lbs / 8N cartridge weight plus friction)
- Must be centered on the cartridge face (or close to it) to avoid torquing the cartridge in its guides
- The bolt strut would need to be strong enough to transmit the pull force from the knob through the front wall

**Assessment: This works.** The bolt is threaded into a brass insert in the release plate, which is bolted to the dock wall via the fittings. After release (plate pulled forward, collets disengaged), pulling the knob further simply pulls the cartridge out of the dock. The 8N pull force is trivial for an M6 bolt. The knob is already at the front center of the cartridge -- ideal for a pull handle.

**One concern:** After the 3mm release travel, continued pulling must disengage the bolt from the release plate insert (the plate stays with the dock, the bolt comes with the cartridge). This means the bolt should NOT be threaded into the release plate. Instead, the release plate interface should be a **thrust bearing arrangement** -- the bolt pushes/pulls the plate via a captured washer or shoulder, not by threading into it.

**Wait -- this contradicts the screw mechanism.** The whole point is that turning the bolt draws the plate forward via thread engagement. If the bolt is threaded into the plate, then pulling the cartridge out requires unthreading the bolt from the plate (which has already been done by the 3-turn release action). After the 3 turns, the bolt is fully disengaged from the plate's insert, and the cartridge slides free.

**Revised understanding:** The operational sequence is:
1. Turn knob 3 turns -- bolt unthreads from release plate insert, plate moves 3mm toward rear wall (return springs push it), collets release
2. Pull cartridge straight out -- bolt is no longer engaged with the plate, so the cartridge slides freely
3. To reinsert: slide cartridge in (tubes auto-engage collets), turn knob 3 turns the other way to thread bolt back into plate insert

Actually, this needs reconsideration. The requirement says turning the knob DRAWS the plate toward the user (toward the front wall). This means the bolt is threaded into the plate, and turning the knob pulls the bolt (and plate) forward. But then to remove the cartridge, you would be pulling the plate WITH the cartridge, which is the opposite of what we want -- the plate must stay with the dock.

**Correct geometry:** The release plate is on the dock side of the rear wall. The bolt passes through the rear wall. Turning the knob (at the front) rotates the bolt, which is threaded into the plate. The thread engagement means rotation converts to axial pull on the plate. The plate moves toward the rear wall (toward the cartridge interior), which pushes the collets inward.

After 3mm of plate travel (3 turns), the collets are released. Now the cartridge can be withdrawn. But the bolt is still threaded into the plate. To withdraw the cartridge, the bolt must come free of the plate. Options:

1. **The 3 turns also fully disengages the bolt from the insert.** If the bolt tip only has ~3mm of thread engagement with the insert at rest, then 3 turns backs it out completely. This is elegant -- the release action and disconnect are the same operation.

2. **The bolt has a smooth section that allows the plate to slide off.** After 3mm of travel, the plate reaches a smooth (unthreaded) section of the bolt and can slide freely. This requires precise control of where threads start/stop on the bolt.

3. **Coupling nut/sliding interface.** The bolt engages the plate through a half-nut or bayonet that can disengage axially after the thread travel is completed.

**Option 1 is the clear winner.** Design the assembly so the bolt tip has exactly 3-4mm of thread engagement with the heat-set insert when the plate is in the "locked" (home) position. Three turns of the knob backs the bolt out of the insert entirely. The plate, now free of the bolt, is pushed back to home by the return springs. The cartridge slides out freely.

**Reinsertion:** Push the cartridge in. The bolt tip meets the insert. Turn the knob 3 turns to thread the bolt back into the insert, pulling the plate forward and allowing the return springs to seat it against the collets in the locked position.

This means the heat-set insert in the release plate acts as a **captive nut** that the bolt threads into and out of. The insert must be long enough to guide the bolt in during reinsertion (a chamfered/countersunk entry helps) but the thread engagement at "locked" position is only ~3mm.

### Revised Insert Sizing

With only 3mm of thread engagement needed, the M6 heat-set insert is more than adequate. At M6 x 1.0 pitch, 3mm = 3 threads. The insert's 12.7mm length provides a long guide funnel for blind re-engagement when inserting the cartridge (the user cannot see the bolt tip meeting the insert under a sink).

---

## 4. Bearing/Bushing at the Rear Wall

The bolt passes through the rear wall (4mm PETG) and rotates during operation. This interface needs consideration.

### Do We Need a Bushing?

The bolt rotates at most 3 turns per actuation, maybe once a month. This is extremely low duty cycle. Direct PETG-on-stainless contact would likely last years without measurable wear.

However, a bushing provides:

1. **Smoother feel.** Brass-on-steel has lower friction than PETG-on-steel, giving a more premium tactile feedback.
2. **Wear protection.** If the bolt is slightly misaligned, a brass bushing prevents the bolt from wallowing out the PETG hole over time.
3. **Tighter clearance.** A precision brass bushing has tighter bore tolerance than a 3D-printed hole, reducing bolt wobble.
4. **Structural reinforcement.** The bushing acts as a bearing surface that distributes load across more of the wall thickness.

### Recommendation: Flanged Brass Bushing

A flanged brass bushing pressed into the rear wall:

```
    ┌──────────────────────────────────┐
    │          rear wall (PETG)        │
    │   ┌──────────────────────┐       │
    │   │ flanged brass bushing│       │
    │   │  ┌──────────────┐   │       │
    │   │  │  6.1mm bore  │   │ ← bolt passes through
    │   │  └──────────────┘   │       │
    │   │   flange (dock side)│       │
    │   └──────────────────────┘       │
    └──────────────────────────────────┘
```

**Specifications:**
- Bore: 6.1-6.2mm (clearance fit on 6mm bolt shaft)
- OD: 8-10mm (press fit into PETG wall)
- Length: 4-6mm (matches or slightly exceeds wall thickness)
- Flange OD: 12-14mm
- Flange thickness: 1-1.5mm
- Material: C360 brass (free-machining, food-safe)

The flange sits on the dock-facing side of the rear wall, preventing the bushing from being pushed through. The press-fit OD locks into the PETG bore.

### Front Wall Bushing

The front wall also needs a bushing where the bolt passes through. Same specifications as above, with the flange on the exterior (knob-facing) side. The knob sits against this flange, which acts as a thrust surface -- when the user turns the knob and the bolt pulls forward, the reaction force is transmitted through the knob body against the flange/wall.

**Both walls need bushings.** The front wall bushing is arguably more important because it bears the axial thrust load from the knob.

### McMaster-Carr Options

McMaster-Carr carries flanged sleeve bearings in the relevant sizes:

- **Flanged sleeve bearing, SAE 841 bronze:** 6mm ID x 10mm OD x 6mm length, with 14mm flange OD. Oil-impregnated sintered bronze. Part numbers vary by exact dimensions -- search "flanged sleeve bearing" with 6mm bore.
- **Flanged drill bushing, brass:** Intended for drill jig work but dimensionally suitable. Precision bore, various ODs.

For food safety, **oil-impregnated bronze (SAE 841) should be avoided** -- the embedded oil is a petroleum product. Use plain brass or dry-running PTFE-lined bushings instead.

**Alternative: Print the bushing pocket oversized and use a plain brass tube section.** Cut a 10mm OD x 6.1mm ID brass tube to 4mm length, press into the wall. Add a printed flange retainer on the exit side. Less elegant but uses readily available brass tube stock.

---

## 5. Specific Product Recommendations

### Primary Components

| Component | Specification | Source | Notes |
|---|---|---|---|
| Bolt | M6-1.0 x 150mm hex head, 304 SS, fully threaded | Amazon / Bolt Depot | Home Depot unlikely to stock 150mm length in-store; order online |
| Heat-set insert | ruthex RX-M6x12.7, M6 thread, 12.7mm long, brass | Amazon (ASIN: B09BHHKWPD) | 25-pack ~$12. Pilot hole 8.0mm for PETG. |
| Hex nut (spare/option B) | M6-1.0, 304 SS, DIN 934 | Home Depot, aisle fastener bin | 5mm thick, 10mm across flats |
| Flat washer | M6, 304 SS, DIN 125A | Home Depot | 6.4mm ID, 12mm OD, 1.6mm thick. For thrust surface. |

### Bushing Options

| Component | Specification | Source | Notes |
|---|---|---|---|
| Flanged bushing (ideal) | 6mm bore x 10mm OD x 6mm L, flanged, plain brass | McMaster-Carr | Search 6mm flanged sleeve bearing, avoid oil-impregnated |
| Brass tube (fallback) | 10mm OD x 6mm ID, cut to 4mm length | Home Depot / hobby shop | K&S Metals or similar hobby brass tube |
| PTFE bushing | 6mm bore x 10mm OD, PTFE or PTFE-lined | McMaster-Carr | Best for food safety, lowest friction |

### Home Depot Availability Reality Check

Home Depot's in-store metric bolt selection typically maxes out around 60-80mm length. An M6 x 150mm bolt will almost certainly require online ordering. The most practical sourcing:

- **Amazon:** M6 x 150mm 304 SS hex bolts are widely available in packs of 4-12. ~$8-12 per pack. Ships Prime.
- **Bolt Depot (boltdepot.com):** Excellent metric selection, sells individually. M6 x 150mm socket head cap screw in 18-8 stainless available.
- **McMaster-Carr:** Single-piece ordering, precise specifications, fast shipping. More expensive per unit but guaranteed quality.

For everything else (nuts, washers), Home Depot's fastener aisle has M6 stainless covered.

---

## 6. Assembly Sequence

### One-Time Build

1. **Prepare release plate:**
   - Print release plate with 15mm diameter x 12.7mm tall boss on rear face, centered on the bolt axis
   - Drill 8.0mm pilot hole through the boss
   - Heat-set the ruthex M6 insert into the boss at 245C using a soldering iron with an M6 tip

2. **Prepare rear wall:**
   - Drill or print a 10mm bore through the rear wall at the bolt axis location
   - Press-fit the rear flanged brass bushing (flange on dock side)

3. **Prepare front wall:**
   - Drill or print a 10mm bore through the front wall at the bolt axis location
   - Press-fit the front flanged brass bushing (flange on exterior/knob side)

4. **Install dowel pins and springs:**
   - Press 3mm steel dowel pins into the dock back wall (or rear wall, depending on where they are anchored)
   - Slide return springs over the pins
   - Position the release plate on the pins, springs compressed

5. **Install bolt:**
   - From the cartridge interior (front wall side), insert the M6 x 150mm bolt through the front wall bushing
   - Thread the bolt tip into the release plate insert (only 3-4mm of engagement at "locked" position)
   - Verify the bolt rotates freely in both bushings

6. **Install knob:**
   - Slide the knob onto the bolt from the front
   - The hex head (or bolt end) captures in the knob's internal cavity
   - Attach retainer (snap ring, cap, or set screw) to lock the knob to the bolt

7. **Test:**
   - Turn knob counterclockwise 3 turns -- the release plate should move ~3mm toward the rear wall
   - Verify the bolt tip fully disengages from the insert after 3 turns
   - Release the knob -- the return springs should push the plate back to home position
   - Turn knob clockwise 3 turns -- bolt re-engages insert, plate locks forward

### Cartridge Swap Operation

1. Turn knob 3 turns counterclockwise (plate releases, collets disengage)
2. Pull cartridge straight out by gripping the knob
3. Swap cartridge (replace pumps, tubing, etc.)
4. Push new cartridge into dock (tube stubs auto-engage collets)
5. Turn knob 3 turns clockwise (bolt threads into plate insert, confirms full seating)

---

## 7. Failure Modes and Concerns

### 7.1 Bolt Bending Over 122mm Span

**Risk: Low.** The bolt is supported at both ends (front wall bushing and rear wall bushing/insert) and carries purely axial load. The dowel pins handle all lateral positioning of the release plate. The only bending scenario is if the bolt is significantly misaligned with the insert during reinsertion, but the 12.7mm insert length provides a generous guide funnel.

If bending is a concern, the bolt could be upgraded to M8 at the cost of larger wall penetrations. Not recommended unless testing reveals a problem.

### 7.2 Cross-Threading on Reinsertion

**Risk: Moderate.** The user reinserts the cartridge by feel in a dark cabinet. The bolt tip must find the heat-set insert bore and thread in cleanly. Mitigations:

- **Chamfered insert entry.** The heat-set insert naturally has a slight chamfer from the installation process. Enlarging this chamfer (45-degree countersink on the insert face) helps guide the bolt in.
- **Long insert = long guide.** 12.7mm of insert length means the bolt has ~10mm of straight bore to find before threads engage. This is very forgiving.
- **Tactile feedback.** The user feels the bolt tip enter the insert bore before applying rotational force. If it does not drop in, the cartridge is not fully seated.
- **Brass insert vs steel bolt.** If cross-threading occurs, the softer brass threads deform rather than the steel bolt threads. The insert can be replaced; the bolt is unharmed.

### 7.3 Thread Wear Over Time

**Risk: Very Low.** At one swap per month, the bolt threads into the insert 12 times per year. Each engagement is only 3 turns. That is 36 thread revolutions per year under 20N axial load. Brass-on-stainless thread wear at this duty cycle is negligible -- the mechanism will outlast the printer that made the cartridge.

### 7.4 PETG Wall Wear at Bushing

**Risk: Low with bushings, Moderate without.** The brass bushings prevent direct bolt-on-PETG contact. Without bushings, the bolt rotating in the PETG bore would eventually wallow it out, introducing play and misalignment. With bushings, the wear interface is brass-on-steel, which is a well-proven bearing combination.

### 7.5 Food Safety of Lubricants

**Concern: Valid.** No petroleum-based lubricant should be used on the bolt threads or bushings. Acceptable options:

- **No lubricant.** Brass-on-stainless and PETG-on-stainless work fine dry at this load and speed. This is the simplest approach.
- **Food-grade silicone grease (NSF H1 rated).** If smoothness is desired, a thin film of Super Lube 92003 (NSF H1 certified, available at Home Depot) on the bolt threads is food-safe. Apply sparingly during assembly.
- **Never use:** WD-40, petroleum jelly, motor oil, or general-purpose grease.

### 7.6 Return Spring Failure

If a return spring fails or weakens, the release plate will not fully return to the locked position after the bolt is disengaged. The collets may not fully re-grip the tube stubs. Mitigation: use stainless steel compression springs rated for the application, and design the spring pockets so springs can be replaced without disassembling the entire mechanism.

### 7.7 Bolt Loosening from Vibration

**Risk: Very Low.** The system has no significant vibration source (peristaltic pumps produce low-amplitude vibration, and the bolt is not in the vibration path). The thread pitch (1.0mm) provides enough friction to resist self-loosening. If this becomes a concern, a nylon-insert lock nut (nyloc) at the knob end adds vibration resistance, but this is almost certainly unnecessary.

### 7.8 Lost Bolt Position Awareness

The user cannot see the bolt under a sink. They need to know whether the mechanism is locked or released. Mitigations:

- **Tactile/audible stop.** Design the knob so it hits a hard stop (front wall flange) when fully tightened. The "thunk" of bottoming out confirms locked state.
- **Knob position indicator.** A line on the knob and a matching line on the cartridge face. Three turns = ~1080 degrees, so position is ambiguous, but a printed arrow that points to "LOCK" / "OPEN" text on the cartridge face could work with detent positions.
- **Thread engagement feel.** The transition from "bolt threading into insert" to "bolt free-spinning in air" is tactilely obvious. The user feels resistance during the 3 turns of engagement and then free spin after disengagement.

---

## 8. Force Analysis

### Mechanical Advantage of the Screw

The screw converts rotational torque into axial force with mechanical advantage determined by the thread geometry.

**Governing equation (power screw):**

```
T = (F * dm / 2) * (L + pi * mu * dm) / (pi * dm - mu * L)
```

Where:
- T = input torque (N-mm)
- F = axial force (N)
- dm = mean thread diameter (mm)
- L = lead = pitch for single-start thread (mm)
- mu = coefficient of friction

**M6 x 1.0 parameters:**
- Major diameter: 6.0mm
- Pitch diameter (dm): 5.35mm
- Pitch / Lead (L): 1.0mm
- Coefficient of friction (stainless on brass, dry): mu = 0.25-0.35

**Required axial force:** F = 20N (4 collets x 5N each, upper estimate)

**Calculating required torque:**

Using mu = 0.30 (conservative):

```
T = (20 * 5.35 / 2) * (1.0 + pi * 0.30 * 5.35) / (pi * 5.35 - 0.30 * 1.0)
T = 53.5 * (1.0 + 5.04) / (16.81 - 0.30)
T = 53.5 * 6.04 / 16.51
T = 53.5 * 0.366
T = 19.6 N-mm
T = ~0.020 N-m
```

**Converting to fingertip effort on a 38mm diameter knob:**

```
Finger force = T / (knob_radius)
Finger force = 19.6 N-mm / 19 mm
Finger force = 1.03 N
```

**That is approximately 100 grams of fingertip force.** This is trivially easy -- lighter than clicking a pen. Even with worst-case friction (mu = 0.45 for dirty/corroded threads), the required fingertip force would be about 1.5N (150g), which is still effortless.

### Mechanical Advantage Summary

| Parameter | Value |
|---|---|
| Thread pitch | 1.0 mm |
| Effective mechanical advantage | ~17:1 (at dm=5.35mm) |
| Required axial force | 20 N (upper estimate) |
| Required torque | ~20 N-mm (0.020 N-m) |
| Required finger force (38mm knob) | ~1.0 N (~3.6 oz) |
| Self-locking? | Yes (lead angle 3.4 deg < friction angle ~17 deg) |

### Self-Locking Verification

A screw is self-locking when the lead angle is less than the friction angle:

- Lead angle = arctan(L / (pi * dm)) = arctan(1.0 / (pi * 5.35)) = arctan(0.0595) = 3.4 degrees
- Friction angle = arctan(mu) = arctan(0.30) = 16.7 degrees

Since 3.4 < 16.7, the screw is **self-locking**. The release plate cannot back-drive the bolt (push it out by spring force alone). The return springs can push the plate back only after the bolt is unthreaded. This is the desired behavior -- the mechanism stays locked until the user deliberately turns the knob.

---

## 9. Summary and Recommendation

The hardware store bolt approach is mechanically sound and straightforward. The key components are:

1. **M6 x 150mm fully threaded hex bolt, 304 stainless steel** -- order from Amazon or Bolt Depot (not reliably available in-store at Home Depot in this length)
2. **ruthex RX-M6x12.7 brass heat-set insert** -- pressed into a local boss on the release plate rear face
3. **Two flanged brass bushings (6mm bore)** -- press-fit into front and rear cartridge walls
4. **3D-printed PETG knob** -- 38mm diameter with hex pocket for bolt head capture
5. **M6 flat washers** -- thrust surfaces at wall interfaces

The mechanism requires ~1N of fingertip force on the knob, is self-locking, and completes release in 3 turns (~3 seconds). Total hardware cost is under $15. All metal components are food-safe 304 stainless or brass.

The main design refinement is ensuring the bolt tip has exactly 3-4mm of thread engagement with the insert at "locked" position, so that the 3-turn release action fully disengages the bolt from the plate, allowing the cartridge to slide free.
