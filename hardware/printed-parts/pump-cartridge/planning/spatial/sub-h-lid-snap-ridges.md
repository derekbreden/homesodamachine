# Spatial Resolution: Sub-H Lid Snap Detent Ridges

## 1. System-Level Placement

```
Mechanism: Lid Snap Detent Ridges (Sub-H)
Parent: Tray (Sub-A), interior faces of left and right side walls, near top edge
Position: 8 ridges total, 4 on each long side wall interior face
Orientation: level (no rotation). Ridges are in the tray reference frame.
```

Sub-H is purely prismatic geometry bonded to flat interior wall surfaces. No angled mounting, no physics-dependent profiles, no cross-frame transforms. The tray sits level in the enclosure and the ridges are simple extrusions on wall faces.

---

## 2. Part Reference Frame

```
Part: Lid Snap Detent Ridges (Sub-H)
  Frame: Tray reference frame (identical to Sub-A)
  Origin: rear-left-bottom corner of tray
  X: width, 0..160 mm (left to right when facing front)
  Y: depth, 0..155 mm (0 = dock/rear, 155 = user/front)
  Z: height, 0..72 mm (0 = floor bottom, 72 = top of side walls)
  Print orientation: tray prints open-top-up; ridges print integral with side walls
  Installed orientation: identical to print orientation (no rotation)
```

---

## 3. Derived Geometry

### 3a. Host surfaces

The ridges attach to the interior faces of both long side walls:

| Wall | Interior face plane | Usable Y range | Usable Z range |
|------|---------------------|----------------|----------------|
| Left | X = 5 mm | Y = 8.5..155 mm | Z = 3..72 mm |
| Right | X = 155 mm | Y = 8.5..155 mm | Z = 3..72 mm |

Ridges protrude inward from these faces (toward the tray centerline at X = 80).

### 3b. Z position of ridges

The side walls top at Z = 72 mm. The lid is a flat panel that sits on top of the tray. The lid's snap tabs are flexible cantilevers that hang downward from the lid perimeter and deflect outward (away from tray center) to clear the ridges during installation, then spring inward behind the ridges to lock.

The ridge peak (highest point of the ridge profile) is positioned 1.5 mm below the top edge of the side wall:

```
Ridge peak Z = 70.5 mm (tray frame)
Ridge base Z range = 69.5 to 71.5 mm (2.0 mm tall base, centered on peak)
```

This places the ridge catch face at Z = 69.5 mm. The lid's snap tab hook engages below this face, preventing the lid from lifting off.

### 3c. Y positions of ridges (4 per side)

The interior Y range is 8.5 mm (rear wall interior face) to 155 mm (front open edge). The front ~10 mm is reserved for bezel receiving features (Sub-I), and the rear ~6.5 mm is close to the rear wall interior corner. Usable range for ridge placement: Y = 20 mm to Y = 140 mm (120 mm span).

Four ridges are evenly spaced across this span:

```
Ridge 1:  Y = 20 mm   (near rear/dock end)
Ridge 2:  Y = 60 mm
Ridge 3:  Y = 100 mm
Ridge 4:  Y = 140 mm  (near front/user end)
```

Spacing between adjacent ridges: 40 mm center-to-center.

These positions are identical on both left and right walls (the ridges are symmetric about the X centerline).

### 3d. Ridge positions -- complete coordinate table

All 8 ridges in the tray reference frame. "Protrusion direction" indicates which way the ridge peak extends from the wall face.

| Ridge ID | Wall | Wall plane | Y (mm) | Z_peak (mm) | Protrusion direction |
|----------|------|------------|--------|-------------|----------------------|
| L1 | Left | X = 5 | 20 | 70.5 | +X (inward, toward X = 80) |
| L2 | Left | X = 5 | 60 | 70.5 | +X (inward) |
| L3 | Left | X = 5 | 100 | 70.5 | +X (inward) |
| L4 | Left | X = 5 | 140 | 70.5 | +X (inward) |
| R1 | Right | X = 155 | 20 | 70.5 | -X (inward, toward X = 80) |
| R2 | Right | X = 155 | 60 | 70.5 | -X (inward) |
| R3 | Right | X = 155 | 100 | 70.5 | -X (inward) |
| R4 | Right | X = 155 | 140 | 70.5 | -X (inward) |

### 3e. Ridge cross-section profile

Each ridge has a triangular cross-section viewed in the YZ plane (looking along the ridge extrusion axis, which is X). The profile provides a ramped entry for the lid tab from above and a near-vertical catch face below.

Cross-section defined in a local (dZ, dX_protrusion) coordinate system, where dZ = 0 at the ridge base bottom (Z = 69.5 mm in tray frame) and dX_protrusion = 0 at the wall interior face:

```
Ridge cross-section profile (left wall ridges, looking in +Y direction):

    dX (protrusion from wall face, mm)
     ^
     |
1.0 -|         *  <-- peak at (1.0, 1.0)
     |        /|
     |       / |
     |      /  |  45° ramp (entry/top side)
     |     /   |
     |    /    |  vertical catch (bottom side)
     |   /     |
0.0 -|--*------*--> dZ (mm)
     0.0      2.0
     (Z=69.5)  (Z=71.5)

Profile vertices (dX_protrusion, dZ):
  (0.0, 0.0)   -- base corner, bottom (Z = 69.5)
  (0.0, 2.0)   -- base corner, top (Z = 71.5)
  (1.0, 1.0)   -- peak (Z = 70.5)
```

Correction -- the profile is better understood as:

```
Ridge cross-section (viewed from +Y, left wall example):

  Z (tray frame)
  ^
  |
71.5 --  B---------C     B = wall face, top of ridge base (X=5, Z=71.5)
         |        /       C = peak (X=6, Z=71.5) -- NOT: ramp is on top
         |       /
         |      /         45° ramp from peak down to bottom-outer corner
         |     /
69.5 --  A----D           A = wall face, bottom of ridge base (X=5, Z=69.5)
         |                D = bottom-outer corner (X=6, Z=69.5)
         |
     X=5    X=6
     (wall face)
```

Revised to proper snap-fit geometry. The ramp should face upward (the direction the lid tab slides past during installation) and the catch face should face downward (preventing the lid from pulling off):

```
Ridge cross-section (viewed from +Y direction, left wall example):

  Z (tray frame)
  ^
  |
71.5 --  A                A = wall face, top of ridge (X=5, Z=71.5)
         |\
         | \              45° ramp (top/entry face)
         |  \             lid tab slides down past this ramp, deflecting outward
         |   \
70.5 --  |    B           B = peak/tip (X=6.0, Z=70.5)
         |    |
         |    |           vertical catch face (bottom/retention face)
         |    |           lid tab hook catches under this face
69.5 --  C----D           C = wall face, bottom (X=5, Z=69.5)
                          D = base of catch (X=6.0, Z=69.5)
     X=5    X=6.0
```

**Profile vertices in tray frame (left wall ridges):**

| Vertex | X (mm) | Z (mm) | Description |
|--------|--------|--------|-------------|
| A | 5.0 | 71.5 | Wall face, top of ridge |
| B | 6.0 | 70.5 | Peak / tip of ridge (1.0 mm protrusion) |
| D | 6.0 | 69.5 | Base of vertical catch face |
| C | 5.0 | 69.5 | Wall face, bottom of ridge |

**Profile vertices in tray frame (right wall ridges, mirrored):**

| Vertex | X (mm) | Z (mm) | Description |
|--------|--------|--------|-------------|
| A | 155.0 | 71.5 | Wall face, top of ridge |
| B | 154.0 | 70.5 | Peak / tip of ridge (1.0 mm protrusion) |
| D | 154.0 | 69.5 | Base of vertical catch face |
| C | 155.0 | 69.5 | Wall face, bottom of ridge |

### 3f. Ridge extrusion length

Each ridge is a short extrusion along the Y axis. The extrusion length is 6 mm, centered on the ridge's Y position.

```
Ridge Y extent = Y_center - 3.0 mm  to  Y_center + 3.0 mm
```

| Ridge | Y_start (mm) | Y_end (mm) | Length (mm) |
|-------|-------------|-----------|-------------|
| L1/R1 | 17.0 | 23.0 | 6.0 |
| L2/R2 | 57.0 | 63.0 | 6.0 |
| L3/R3 | 97.0 | 103.0 | 6.0 |
| L4/R4 | 137.0 | 143.0 | 6.0 |

### 3g. Interface with lid snap tabs (mating feature from tray's perspective)

The lid's snap tabs are the mating features. From the tray ridge's perspective, each ridge engages one lid tab. The interface is defined here so the lid specification can be cross-checked.

**What the tray expects from each lid tab:**

- The tab is a flexible cantilever hanging downward from the lid's underside edge.
- Tab tip reaches below the ridge catch face (below Z = 69.5 in tray frame) when engaged.
- Tab deflects outward (away from tray center) by at least 1.0 mm to clear the ridge peak during lid installation.
- Tab catches behind the vertical face of the ridge (tab hook face presses upward against the ridge catch face at Z = 69.5).
- Each tab aligns with one ridge at the same Y position.

**Engagement envelope per ridge (tray frame):**

The volume that the lid tab occupies when engaged, from the tray's perspective:

| Parameter | Left wall value | Right wall value |
|-----------|----------------|-----------------|
| X range of tab (engaged) | 5.0 to 7.0 mm | 153.0 to 155.0 mm |
| Z range of tab hook | 67.5 to 69.5 mm | 67.5 to 69.5 mm |
| Y range | same as ridge Y extent (6 mm) | same as ridge Y extent (6 mm) |

The tab hook occupies the 2 mm zone directly below the ridge catch face (Z = 67.5 to 69.5). The tab extends 2 mm from the wall face inward (same direction as the ridge). This gives 1 mm of overlap behind the ridge's vertical catch face -- the retention depth.

**Retention force geometry:**
- Retention depth (horizontal overlap behind catch face): 1.0 mm
- This means the lid tab must deflect 1.0 mm outward to disengage
- The 45-degree ramp on the ridge top face guides the tab outward during installation, requiring ~1.0 mm of tab deflection

### 3h. Clearance check -- ridge tips vs. interior pocket

The ridge tips protrude 1.0 mm from the wall interior faces:
- Left wall ridges: tips at X = 6.0 mm (interior pocket starts at X = 5.0 mm, so 1.0 mm into the pocket)
- Right wall ridges: tips at X = 154.0 mm (interior pocket ends at X = 155.0 mm, so 1.0 mm into the pocket)

Clear space between opposing ridge tips: 154.0 - 6.0 = 148.0 mm. The lid is 160 mm wide with 5 mm wall thickness on each side, so the lid's interior span is 150 mm. The 1 mm ridge protrusion on each side leaves 148 mm -- no interference with any interior components (pumps, tubes, release plate). The ridges are also at Z = 69.5 to 71.5, which is the top 2.5 mm of the 69 mm tall interior cavity -- well above the pump zone and tube routing zone.

---

## 4. Transform Summary

```
Sub-H frame = Tray frame = Sub-A frame (identity transform)

No rotation. No translation.
Ridges are specified directly in the tray reference frame.
```

### Verification

- Ridge L1 peak at tray (6.0, 20.0, 70.5) -- left wall interior, near rear, near top edge. Correct.
- Ridge R3 peak at tray (154.0, 100.0, 70.5) -- right wall interior, mid-depth, near top edge. Correct.
- Ridge L4 bottom-outer corner at tray (6.0, 140.0, 69.5) -- left wall, near front, just below peak. Correct.

All points lie on the correct wall interior faces, within the side wall Z range (3..72), and within the usable Y range (8.5..155). Identity transform confirmed.
