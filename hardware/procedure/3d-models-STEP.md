# STEP Generation Standards

This document defines the standards for programmatic STEP file generation in this project. Every custom part gets a Python script that generates its STEP file. The script IS the parametric model — it must faithfully represent the physical geometry of the part and every interface it engages with.

---

## 1. What These Models Are

These are **engineering models** — precise 3D solids that a 3D printer, CNC machine, or CAD operator could use to produce the part. They are not approximations, not simplified placeholders, not "close enough."

That means:
- Every dimension is caliper-verified or derived from caliper-verified measurements
- Every interface with an off-the-shelf component matches that component's actual physical geometry — its real shape, real profile, real mounting features
- Features exist because they serve a mechanical function, and the model must reflect that function faithfully
- The script demonstrates that the author understood the physical reality of every feature and interface

Off-the-shelf parts that interface with custom parts have **caliper-verified geometry descriptions and reference photographs** in `../off-the-shelf-parts/`. Each part's `extracted-results/geometry-description.md` contains dimensioned descriptions, ASCII art profiles, and references to numbered caliper photos in the sibling `raw-images/` directory. These are the authoritative source for purchased component geometry — the geometry descriptions explain the measurements, and the photographs show the actual physical object being measured.

---

## 2. Script Format

- **Language:** Python 3
- **Library:** CadQuery (standardized — not build123d)
- **Python:** `tools/cad-venv/bin/python3` (virtual environment with CadQuery installed)
- **Validation helper:** `import step_validate` from `tools/step_validate.py` (add `tools/` to `sys.path`)
- **Output:** STEP file (`.step`)
- **Script location:** `hardware/printed-parts/<part-name>/generate_step_cadquery.py`
- **Output location:** `hardware/printed-parts/<part-name>/<part-name>-cadquery.step`
- **Self-contained:** The script must run standalone with no external dependencies beyond CadQuery and `step_validate`
- **Commented:** Each modeling section references the feature name from parts.md

### Why CadQuery

CadQuery was chosen over build123d after comparative evaluation on the cartridge release plate:

1. **Workplane model reduces orientation errors.** CadQuery's "declare plane → sketch 2D → extrude" maps directly to how specs describe features. build123d's `Rot() * Pos() * Primitive()` requires mental simulation of rotation matrices — a reliable source of agent errors.
2. **Explicit orientation parameters.** `slot2D(length, width, angle=90)` self-documents intent. build123d's `SlotOverall` has no angle parameter — the slot's long axis is implicitly determined by sketch axis mapping, which caused a confirmed 90-degree rotation bug.
3. **Revolved profiles for stepped bores.** A bore's full axial cross-section (multiple diameters + chamfers) can be defined as a list of (R, Y) points and revolved once. This is correct-by-construction — no edge hunting for chamfer targets.
4. **Point-in-solid validation via OCP.** CadQuery exposes OCCT's `BRepClass3d_SolidClassifier` through its OCP bindings, enabling spatial probes that verify actual geometry, not just face/edge topology.
5. **`centered=False` eliminates positioning math.** Boxes placed at spec coordinates directly, without computing center offsets.

---

## 3. Source Material

For each part being modeled, the complete specification chain is:

1. **The part's `planning/parts.md`** — dimensions, features, interfaces, assembly notes
2. **Cross-referenced geometry descriptions** — linked from parts.md for every off-the-shelf component that mounts in or interfaces with the custom part (in `off-the-shelf-parts/*/extracted-results/geometry-description.md`)
3. **Reference photographs** — caliper photos of the physical off-the-shelf parts (in `off-the-shelf-parts/*/raw-images/`), referenced by number in the geometry descriptions
4. **Research files** — linked from parts.md, containing design analysis and rationale
5. **Requirements and vision** — `hardware/requirements.md` and `hardware/vision.md`

Every cross-reference in parts.md is a relative path. Follow them all. Read the geometry descriptions. Look at the photographs. Understand what you are modeling before you write a line of code.

---

## 4. Self-Review Rubrics

Apply these rubrics **during and after** generation. Rubrics 1 and 2 are completed before writing modeling code. Rubrics 3-5 are applied after the model is generated.

### Rubric 1 — Feature Planning Table (MANDATORY, before coding)

Before writing any modeling code, read parts.md and enumerate **every** feature in a table. Every line item under "Features" and "Interfaces" in parts.md becomes a row. If parts.md says there are N features, the table has N rows. Missing a row means missing a feature in the model.

For each feature:

```
| # | Feature Name | Mechanical Function | Operation | Shape | Axis | Center Position (X,Y,Z) | Dimensions | Notes |
```

Column definitions:
- **Feature Name**: Exact name from parts.md (e.g., "guide pin slot", "tube clearance hole")
- **Mechanical Function**: WHY this feature exists — what it does in the assembly. A slot that allows sliding is fundamentally different from a decorative groove, even if the dimensions are identical. Getting the function right determines whether you get the orientation, tolerances, and shape right.
- **Operation**: Add (boss, pad, extrusion) or Remove (bore, pocket, slot, cut-through)
- **Shape**: Cylinder, box, stadium/slot, chamfer, etc.
- **Axis**: Which axis the feature runs along (X, Y, or Z). For through-features, this is the axis you'd drill along.
- **Center Position**: Where the feature center is in the part's coordinate system
- **Dimensions**: All relevant dimensions from parts.md
- **Notes**: Clearance requirements, tolerances, interface constraints

This table is the contract between the specification and the model. Print it to stdout when the script runs.

### Rubric 2 — Coordinate System Declaration (MANDATORY, before coding)

Declare the part's coordinate system explicitly at the top of the script:

```
# Coordinate system:
#   Origin: [where — e.g., "plate bottom-left-front corner"]
#   X: [what — e.g., "plate width, left to right"]
#   Y: [what — e.g., "plate depth, front to back"]
#   Z: [what — e.g., "plate height, bottom to top"]
#   Envelope: [W]x[D]x[H] mm → X:[0,W] Y:[0,D] Z:[0,H]
```

Map parts.md dimensions to axes explicitly. When parts.md says "59W x 47H x 6D", that must map to specific axes with specific ranges. This prevents the class of error where width and depth get swapped or a feature ends up on the wrong face.

### Rubric 3 — Feature-Specification Reconciliation (MANDATORY, after generation)

After generating the model, the script must programmatically verify **every row** of the Feature Planning Table against the actual solid using point-in-solid probing. Use the `Validator` class from `tools/step_validate.py`.

For each feature, probe specific spatial coordinates to verify:

1. **Existence**: `check_void()` inside bores/slots/holes, `check_solid()` inside bosses/tabs/walls. If a feature is missing, the probe will detect solid where void is expected (or vice versa).
2. **Dimensions**: Probe at the expected boundary radius/edge. A point just inside the bore radius should be void; a point just outside should be solid. Wrong diameter → wrong probe result.
3. **Position**: Probe at the feature's expected center coordinates. Wrong position → probe hits wrong material state.
4. **Orientation**: For directional features (stadium slots, elongated cutouts), probe at both ends of the long axis AND at the midpoint of the short axis. A 90-degree rotation error will cause the long-axis probe to hit solid instead of void.

Example validation pattern for a stadium slot with long axis along Z:

```python
# Slot center — should be void
v.check_void("Slot center", sx, mid_y, sz, "void at slot center")

# Long-axis ends (Z direction) — should be void if orientation is correct
v.check_void("Slot Z+ end", sx, mid_y, sz + SLOT_L/2 - 0.3, "void near top of slot")
v.check_void("Slot Z- end", sx, mid_y, sz - SLOT_L/2 + 0.3, "void near bottom of slot")

# Short-axis extents (X direction) — should be SOLID if orientation is correct
# (probing outside the 3.3mm width but inside the 7.3mm length)
v.check_solid("Slot X+ wall", sx + SLOT_W/2 + 0.5, mid_y, sz, "solid outside slot width")
```

If the slot were rotated 90 degrees, the Z+ end probe would hit solid (the slot only extends 3.3mm in Z instead of 7.3mm), catching the bug.

**Zero FAILs required.** If any feature fails, fix it before exporting the STEP.

### Rubric 4 — Solid Validity

After the final boolean operation, verify using `Validator`:

```python
v.check_valid()         # No self-intersecting faces
v.check_single_body()   # One connected solid, not fragmented
v.check_volume(expected_envelope=W*D*H, fill_range=(0.5, 1.2))
```

### Rubric 5 — Bounding Box Reconciliation

Query the model's actual bounding box and compare against the envelope from parts.md using `Validator.check_bbox()`. Check all three axes, accounting for features that intentionally extend beyond the base body (tabs, bosses).

If the bounding box is SMALLER than expected in any dimension → likely missing a protruding feature.
If the bounding box is LARGER than expected in an unexpected dimension → likely a feature in wrong orientation.

---

## 5. CadQuery Techniques

Preferred patterns for common modeling tasks:

### Stepped bores with chamfers — use revolved profiles

Define the full axial cross-section as a list of (R, Y) coordinate pairs and revolve once. This includes all diameter steps and chamfers in a single operation — no edge filtering, no silent failures.

```python
# Example: 3-stage stepped bore with entry chamfer
profile_pts = [
    (0,              0),           # axis at entry face
    (R_OUTER - C,    0),           # chamfer start
    (R_OUTER,        C),           # chamfer end
    (R_OUTER,        DEPTH_1),     # step to next diameter
    (R_INNER,        DEPTH_1),     # inner bore wall
    (R_INNER,        DEPTH_2),     # step to smallest
    (R_TUBE,         DEPTH_2),     # tube hole wall
    (R_TUBE,         FULL_DEPTH),  # through to back face
    (0,              FULL_DEPTH),  # axis at back face
]

bore = cq.Workplane("XY").polyline(profile_pts).close().revolve(360, (0,0), (0,1))
plate = plate.cut(bore.translate((cx, 0, cz)))
```

### Positioning — use `centered=False` and `translate()`

Place boxes at spec coordinates directly:

```python
plate = cq.Workplane("XY").box(W, D, H, centered=False)  # X:[0,W] Y:[0,D] Z:[0,H]
```

### Stadium slots — use `slot2D()` with explicit `angle`

Always specify the `angle` parameter. The long axis of the slot is along the sketch X by default; `angle=90` rotates it to sketch Y (which maps to Z on the XZ workplane).

```python
slot = (
    cq.Workplane("XZ")
    .center(slot_cx, slot_cz)
    .slot2D(SLOT_LENGTH, SLOT_WIDTH, angle=90)  # long axis along Z
    .extrude(-PLATE_D)  # XZ normal is -Y; negative extrude goes +Y
)
```

### Extrude direction on non-XY workplanes

CadQuery's `extrude(positive)` goes along the workplane normal, `extrude(negative)` goes opposite. Workplane normals:
- `"XY"` → +Z
- `"XZ"` → -Y
- `"YZ"` → +X

Comment the extrude direction when using XZ or YZ workplanes.

---

## 6. Validation Helper

The validation helper at `tools/step_validate.py` provides the `Validator` class. Import it at the top of each generation script:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from step_validate import Validator
```

After building the model:

```python
v = Validator(plate)  # plate is the CadQuery Workplane

# Feature probes (one section per Feature Planning Table row)
v.check_solid("Plate body interior", 29.5, 3.0, 23.5)
v.check_void("Bore 1 center", 9.5, 1.0, 9.5)
# ... etc for every feature ...

# Bounding box
bb = plate.val().BoundingBox()
v.check_bbox("X", bb.xmin, bb.xmax, expected_xmin, expected_xmax)
v.check_bbox("Y", bb.ymin, bb.ymax, expected_ymin, expected_ymax)
v.check_bbox("Z", bb.zmin, bb.zmax, expected_zmin, expected_zmax)

# Solid integrity
v.check_valid()
v.check_single_body()
v.check_volume(expected_envelope=W*D*H)

# Summary — exits 1 on any failure
if not v.summary():
    sys.exit(1)
```

---

## 7. Workflow

1. Read the part's `planning/parts.md` and follow **every** cross-reference (geometry descriptions, research, architecture)
2. Look at reference photographs of interfacing off-the-shelf parts
3. Complete the Feature Planning Table (Rubric 1) and Coordinate System Declaration (Rubric 2)
4. Write the modeling code using CadQuery, referencing the planning table for every feature
5. Write the validation section using `Validator`, with probes for every feature
6. Run the script with `tools/cad-venv/bin/python3`
7. Verify all checks pass (zero FAILs)
8. Fix any failures and re-run until all checks pass
9. Export STEP file

---

## 8. Related Documents

- **Drawing standards (SVG):** `hardware/procedure/engineering-drawings-SVG.md`
- **Validation helper source:** `tools/step_validate.py`
- **Off-the-shelf part geometry and photographs:** `hardware/off-the-shelf-parts/*/`
