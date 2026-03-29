# Tray Sub-Component Decomposition

## Decomposition Rationale

The tray is the structural backbone of the pump cartridge: an open-top box with features spanning its floor, side walls, and rear wall. Despite its complexity, every feature is prismatic (extrude-and-cut). There are no revolved profiles, sweeps, or lofts. However, the sheer number of features (~20+) spread across multiple faces makes a single monolithic CadQuery script fragile and hard to validate. Decomposing into sub-components lets each be specified, drawn, and tested independently, then combined via boolean union/cut in a deterministic build sequence. Each sub-component is a single extrusion or a set of related cuts on the same face, keeping every sub-problem firmly in 2.5D territory.

---

## Sub-Components

### Sub-A: Box Shell

**Features from concept:** Open-top rectangular box with 5 mm side walls, 3 mm floor, 8.5 mm rear wall. The fundamental solid from which everything else is added or subtracted.

**Geometric paradigm:** Single box extrusion, then shell (or equivalent: outer box minus inner pocket). Pure prismatic.

**Key dimensions (rough):**
- Outer envelope: ~160 x 155 x 72 mm (X width, Y depth, Z height)
- Side wall thickness: 5 mm (left and right)
- Floor thickness: 3 mm
- Rear wall thickness: 8.5 mm (thicker to host fitting bores and guide posts)
- Open top (no ceiling)
- Open front (the bezel attaches separately)

**Interface boundary:** The outer surfaces of the box shell are the base geometry that all subsequent sub-components attach to or cut from. The inner pocket volume is where pumps, tubes, and the release plate live.

**Dependencies:** None. This is the first operation.

---

### Sub-B: T-Rail Tongues

**Features from concept:** T-shaped rail tongues running the full depth of both outer side walls. Offset vertically (not centered) for keying so the cartridge cannot be inserted upside down.

**Geometric paradigm:** Two extruded T-profile solids, unioned to the left and right outer side walls. Each is a constant cross-section extruded along Y (depth axis). Pure prismatic.

**Key dimensions (rough):**
- T cross-section: 6 mm wide tongue, 3 mm tall cap, 4 mm slot depth
- Rail length: full cartridge depth (~155 mm)
- Left rail: offset vertically toward the top of the side wall
- Right rail: offset vertically toward the bottom (or vice versa -- asymmetric for keying)
- Clearance designed for 0.3 mm per side against dock channels

**Interface boundary:** Each tongue bonds flush to the flat outer face of a side wall. The contact surface is a rectangular strip running the full Y depth of the wall.

**Dependencies:** Sub-A (box shell must exist to provide the side wall surfaces).

---

### Sub-C: Pump Mounting Bosses

**Features from concept:** 4 cylindrical bosses on the tray floor with heat-set insert pockets (M3 x 5.7 mm inserts). Two per pump, at 49.45 mm center-to-center per pump. Also includes 2 semicircular motor cradles (half-pipe ribs rising from the floor behind each pump, ~35.5 mm ID).

**Geometric paradigm:** Cylindrical boss extrusions (union) rising from the floor plane, each with a concentric pilot hole cut. Motor cradles are extruded half-pipe profiles (union) rising from the floor. All prismatic extrude-and-cut along Z.

**Key dimensions (rough):**
- Boss OD: ~8 mm (4 mm pilot hole + 2 mm wall all around)
- Boss height: rising from floor to support bracket (~5-8 mm above floor surface)
- Pilot hole: 4.0 mm diameter, depth to accept M3 x 5.7 mm insert
- 4 bosses total: 2 per pump at 49.45 mm X spacing
- Pump-to-pump gap: ~5 mm between brackets
- Motor cradle: semicircular rib, ~35.5 mm ID, wall thickness ~3 mm, height ~15-20 mm above floor
- 2 cradles, one per pump, positioned behind the pump head zone (toward motor end)

**Interface boundary:** Bosses and cradles sit on and rise from the interior floor surface of the box shell.

**Dependencies:** Sub-A (floor surface must exist).

---

### Sub-D: Fitting Bore Array

**Features from concept:** 4 through-bores in the rear wall for John Guest PP0408W press-fit mounting. The center body (9.31 mm OD) press-fits into 9.5 mm bores. The body end shoulders (15.10 mm OD) capture axially against the rear wall faces. Also includes 4 entry funnels on the outboard (dock-facing) face of the rear wall -- shallow chamfers or countersinks that guide the dock tube stubs toward the fitting ports.

**Geometric paradigm:** 4 cylindrical through-cuts in the rear wall (Z-oriented bores through a wall that runs in the XZ plane). Entry funnels are shallow conical countersinks on the outboard face. All cuts, no unions. Pure prismatic/cylindrical removal.

**Key dimensions (rough):**
- Bore diameter: 9.5 mm (press-fit on 9.31 mm center body)
- Bore depth: 12.16 mm (matches center body length)
- 2x2 grid pattern at 20 mm center-to-center spacing
- Grid centered on the rear wall
- Entry funnels: conical or chamfered countersinks (~15-16 mm OD at the outer face, tapering to ~9.5 mm bore)
- Rear wall thickness: 8.5 mm (bore depth fits within this -- the bore captures the center body, with body end shoulders bearing against both faces)

**Interface boundary:** Bores penetrate the rear wall of the box shell. The bore centers define the fitting grid, which is the reference for the release plate guide posts (Sub-E).

**Dependencies:** Sub-A (rear wall must exist to cut bores into).

---

### Sub-E: Guide Post Array

**Features from concept:** 4 cylindrical guide posts for the release plate, rising from the interior face of the rear wall. Positioned at diagonal corners of the fitting grid. The release plate slides on these posts with 0.2-0.3 mm clearance.

**Geometric paradigm:** 4 cylindrical extrusions (union) rising from the rear wall interior face along the Y axis (toward the front of the cartridge). Pure prismatic.

**Key dimensions (rough):**
- Post diameter: 3.5 mm
- Post length: 8-10 mm (sufficient bearing length to prevent plate tilt)
- 4 posts at diagonal corners of the ~40 x 40 mm fitting grid area
- Posts rise from the interior face of the rear wall, extending into the cartridge interior

**Interface boundary:** Posts bond flush to the interior face of the rear wall. Their positions are referenced to the fitting bore grid center (Sub-D defines that grid).

**Dependencies:** Sub-A (rear wall interior face), Sub-D (guide post positions are referenced to the fitting bore grid -- not a geometric dependency, but a dimensional reference).

---

### Sub-F: Tube Routing Channels

**Features from concept:** U-shaped channels molded into the tray floor for routing 4 silicone tubes from pump barbs to John Guest fittings. Includes snap-over clip features at intervals to retain tubes.

**Geometric paradigm:** Rectangular channel cuts into the floor surface (or raised channel walls as extrusions from the floor -- either approach is prismatic). Snap clips are small extruded tabs rising from channel walls. All prismatic extrude along Z.

**Key dimensions (rough):**
- Channel width: ~10 mm (for 1/4" OD tubing with clearance)
- Channel depth: ~10 mm
- 4 channels routing from pump zone (mid-cartridge) to fitting zone (rear wall)
- Routes run roughly parallel to Y axis with gentle lateral offsets
- Snap clips: small overhanging tabs at ~30 mm intervals, ~1 mm thick, ~3 mm overhang

**Interface boundary:** Channels are cut into (or built up from) the interior floor surface. They run between the pump mounting zone (Sub-C) and the fitting zone (Sub-D).

**Dependencies:** Sub-A (floor surface). Should be applied after Sub-C (pump bosses) to avoid interference with boss geometry.

---

### Sub-G: Linkage Rod Guide Slots

**Features from concept:** Slots in both inner side walls for the linkage rods that connect the release plate to the front pull tabs. The rods (~4 mm diameter) pass through these slots and slide fore-aft during the squeeze-release action.

**Geometric paradigm:** Through-slot cuts in the side walls. Each slot is an elongated hole (stadium/slot shape) cut through the wall thickness. Pure prismatic cut along X (through the wall).

**Key dimensions (rough):**
- Slot width: ~4.5-5 mm (clearance for 4 mm rod)
- Slot length (along Y): ~10-15 mm (enough for 1.5 mm plate travel + rod hook clearance)
- Slot height position (Z): mid-wall, aligned with the release plate's linkage attachment points
- 1 slot per side wall, 2 total
- Cut through the full wall thickness (5 mm)

**Interface boundary:** Slots penetrate the left and right side walls of the box shell. Their Y-position corresponds to the zone between the fitting area and the pump area. Their Z-position corresponds to the release plate's edge height.

**Dependencies:** Sub-A (side walls must exist to cut slots into).

---

### Sub-H: Lid Snap Detent Ridges

**Features from concept:** Detent ridges along the top edges of both long side walls (interior face). The lid's snap tabs engage these ridges. 4 per long edge, 8 total.

**Geometric paradigm:** Small extruded ridges (union) on the interior faces of the side walls near the top edge. Each ridge is a short raised bump (triangular or rectangular cross-section) extruded along X (across the wall interior face). Pure prismatic.

**Key dimensions (rough):**
- Ridge profile: ~1 mm tall, ~2 mm wide (triangular or half-round cross-section for snap engagement)
- 4 ridges per side, spaced evenly along the Y (depth) axis
- Located ~1-2 mm below the top edge of the side wall, on the interior face

**Interface boundary:** Ridges bond to the interior faces of the side walls, near the top edge.

**Dependencies:** Sub-A (side walls must exist).

---

### Sub-I: Front Bezel Receiving Features

**Features from concept:** Snap tab receiving features at the front open edge of the tray where the front bezel attaches. Includes tab pockets or detent recesses on the front edges of the side walls, floor, and top edges.

**Geometric paradigm:** Small pocket cuts (rectangular recesses) in the front edges of the side walls and floor. Pure prismatic cuts.

**Key dimensions (rough):**
- 2 tab pockets per side wall (4 total on side walls)
- 1 tab pocket on the floor front edge
- Pocket size: ~3 x 5 x 1.5 mm (width x height x depth) -- sized for the bezel's snap tabs with the 1.5 mm step-lap overlap
- Step-lap ledge: the front edge of the tray is recessed by ~1.5 mm around its perimeter so the bezel overlaps, creating the shadow-line seam

**Interface boundary:** Features are on the front-facing edges of the box shell (the open end opposite the rear wall).

**Dependencies:** Sub-A (box shell edges must exist).

---

### Sub-J: Electrical Contact Pad Areas

**Features from concept:** Flat pad areas on the rear wall exterior (dock-facing side) or side walls where blade terminal connectors mount. 4 motor blades + 1 cartridge-present blade pair = 5 blade positions. Female spade terminals are crimped onto wires inside the cartridge; the pads/slots on the tray provide routing and retention for these terminals.

**Geometric paradigm:** Small rectangular recesses or channels cut into wall surfaces for wire routing and terminal retention. Pure prismatic cuts.

**Key dimensions (rough):**
- 5 terminal positions (2 per pump + 1 cartridge-present pair)
- Wire channels: ~3-4 mm wide, ~2 mm deep
- Terminal retention slots sized for 6.3 mm blade terminal housings
- Positioned on the rear wall or rear portion of side walls, aligned with the insertion axis so blades engage during cartridge insertion
- Asymmetric vertical spacing between pump 1 and pump 2 blade pairs (polarity/keying)

**Interface boundary:** Cuts into the rear wall exterior face and/or side wall surfaces near the rear.

**Dependencies:** Sub-A (wall surfaces must exist). Should be applied after Sub-D (fitting bores) to avoid interference.

---

## Build Sequence

The following order ensures each sub-component's dependencies are satisfied before it is applied:

```
Step  Sub-Component                 Operation   Dependencies
----  ----------------------------  ----------  ----------------
 1    Sub-A: Box Shell              CREATE      (none)
 2    Sub-B: T-Rail Tongues         UNION       A
 3    Sub-C: Pump Mounting Bosses   UNION       A
 4    Sub-E: Guide Post Array       UNION       A
 5    Sub-H: Lid Snap Detent Ridges UNION       A
 6    Sub-F: Tube Routing Channels  UNION/CUT   A, after C
 7    Sub-D: Fitting Bore Array     CUT         A
 8    Sub-G: Linkage Rod Guide Slots CUT        A
 9    Sub-I: Front Bezel Receiving  CUT         A
10    Sub-J: Electrical Contact Pads CUT        A, after D
```

**Rationale for ordering:**
- All unions (material additions) are performed before cuts (material removals). This follows the OCCT best practice of building up the solid before carving into it, which avoids thin-wall failures and ensures cuts have sufficient material to operate on.
- Sub-F (tube channels) comes after Sub-C (pump bosses) because the channels must route around the boss positions.
- Sub-J (electrical pads) comes after Sub-D (fitting bores) to avoid interference between bore cuts and terminal slots.
- Sub-G (linkage slots) and Sub-I (bezel features) are independent cuts that can be applied in any order after the shell exists.

---

## Composition Specification

**Final solid = ((((((((A + B) + C) + E) + H) +/- F) - D) - G) - I) - J**

All sub-components operate on the same solid. There is no separate assembly -- this is a single printed part built up by boolean operations on a growing solid.

**Interface treatments:**
- Sub-B to Sub-A: flush rectangular bond along side wall exterior faces. 1 mm fillet at the junction between the T-rail cap and the side wall for printability (avoids sharp overhang).
- Sub-C to Sub-A: flush cylindrical bond on floor. No fillet needed (bosses rise straight from floor).
- Sub-E to Sub-A: flush cylindrical bond on rear wall interior. No fillet needed.
- Sub-H to Sub-A: flush bond on side wall interior. No fillet (the ridge IS the snap feature).
- All cuts (D, G, I, J): no interface treatment -- cuts produce clean edges. Optional 0.5 mm chamfer on bore entries (Sub-D) for press-fit ease, and on entry funnels.

**Boolean operation notes:**
- Perform all unions before all cuts. OCCT can produce degenerate faces if a cut creates a zero-thickness wall that a subsequent union tries to bond to.
- The fitting bore array (Sub-D) cuts through the full rear wall thickness. Ensure the rear wall is 8.5 mm thick (set by Sub-A) before these bores are applied.
- Guide posts (Sub-E) are unioned to the rear wall interior face. They do NOT interfere with the fitting bores because the posts are at diagonal corners of the fitting grid, outside the bore diameter envelopes.
- The T-rail tongues (Sub-B) run the full Y depth. If the front of the tray is open (no front wall), the rail extrusion simply starts and ends at the tray's Y extent.
