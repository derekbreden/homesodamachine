# Sub-A: Box Shell -- Parts Specification

An open-top, open-front rectangular box printed in PETG. It is the foundational solid of the pump cartridge tray -- every other sub-component (B through J) is unioned to or cut from this part. The box has three closed walls (left, right, rear), a floor, and two open faces (top, front). The rear wall is thicker than the side walls to host fitting bores (Sub-D) and guide posts (Sub-E). The front opening receives the bezel (Sub-I). The top opening receives the lid (Sub-H).

---

## Coordinate System

Origin: rear-left-bottom corner of the box (dock side).

- **X axis**: width, 0 at left wall exterior, positive rightward. Total extent: 160 mm.
- **Y axis**: depth, 0 at rear wall exterior (dock side), positive toward user (front). Total extent: 155 mm.
- **Z axis**: height, 0 at floor bottom, positive upward. Total extent: 72 mm.

Print orientation: open top facing up, XY plane on build plate. Installed orientation: identical to print orientation (no rotation).

---

## Mechanism Narrative

### What the user sees and touches

The box shell is an internal structural component. The user never sees or touches it directly. It is entirely hidden behind the front bezel (the only user-facing surface) and inside the enclosure dock. During cartridge removal, the user's palm contacts the front bezel; the box shell is behind it. During assembly of the cartridge (a one-time build step), the builder handles the tray directly to install pumps, route tubes, and attach the bezel and lid.

### What moves

**Nothing.** The box shell is the stationary reference frame of the entire cartridge. Every moving part (the release plate sliding on guide posts, the linkage rods translating through side-wall slots, the lid snapping on/off) moves relative to the box shell, but the shell itself is rigid and fixed within the dock during operation.

During cartridge insertion and removal, the entire tray assembly (box shell included) translates along the Y axis on the T-rail tongues (Sub-B). The box shell provides the side-wall surfaces to which those tongues are bonded.

### What converts the motion

Not applicable. The box shell is a passive structural frame. It does not convert any motion. It provides:
- Mounting surfaces for features that do involve motion (guide posts for the release plate, linkage slots for the rods, T-rail tongue bond surfaces for cartridge sliding).
- Rigid constraint for all press-fit and snap-fit interfaces.

### What constrains the box shell

The box shell is constrained within the dock by the T-rail tongues (Sub-B) bonded to its left and right exterior walls. The tongues engage channels in the dock, constraining the cartridge in X (lateral), Z (vertical), and rotation about Y. The only free degree of freedom is translation along Y (insertion/removal axis), which is arrested at end-of-travel by the dock's rear stop and the fitting engagement.

### What provides the return force

Not applicable. There is no return force acting on the box shell. It is inserted by hand and removed by hand.

### What is the builder's physical interaction

1. The builder receives the box shell as a single printed part, open top facing up.
2. The builder installs heat-set inserts into the pump boss pilot holes on the floor (Sub-C features, not part of Sub-A).
3. The builder bolts pumps to the floor bosses, routes tubes through floor channels, presses John Guest fittings into rear wall bores -- all of which are features added to or cut from the box shell by subsequent sub-components.
4. The builder snaps the lid onto the top edges and the bezel onto the front edges.

The box shell itself requires no assembly -- it is a monolithic print.

---

## Overall Envelope

| Parameter | Value | Source |
|-----------|-------|--------|
| X extent (width) | 160.0 mm | Spatial resolution doc, outer envelope |
| Y extent (depth) | 155.0 mm | Spatial resolution doc, outer envelope |
| Z extent (height) | 72.0 mm | Spatial resolution doc, outer envelope |
| Material | PETG | Concept architecture, Section 7 |
| Infill | 20% gyroid (walls and floor are solid perimeter; infill applies to rear wall bulk only) | -- |
| Estimated mass | ~95 g | PETG at 1.27 g/cm^3, estimated solid volume ~75 cm^3 |

---

## Left Side Wall

| Parameter | Value |
|-----------|-------|
| Position (X) | X = 0 to X = 5 mm |
| Extent (Y) | Y = 0 to Y = 155 mm (full depth) |
| Extent (Z) | Z = 0 to Z = 72 mm (full height) |
| Thickness (X) | 5.0 mm |
| Interior face | X = 5 mm plane |
| Exterior face | X = 0 mm plane |

The left wall is a solid rectangular slab. Its exterior face (X = 0 plane) is the bond surface for the left T-rail tongue (Sub-B). Its interior face (X = 5 plane) hosts lid snap detent ridges (Sub-H) near the top edge and one linkage rod guide slot (Sub-G) at mid-height.

Internal corner fillet where the left wall meets the floor: 1.0 mm radius, running the full Y extent (Y = 0 to Y = 155). This fillet is at the junction of the X = 5 plane and the Z = 3 plane.

Internal corner fillet where the left wall meets the rear wall: 1.0 mm radius, running the full Z extent (Z = 0 to Z = 72). This fillet is at the junction of the X = 5 plane and the Y = 8.5 plane.

---

## Right Side Wall

| Parameter | Value |
|-----------|-------|
| Position (X) | X = 155 to X = 160 mm |
| Extent (Y) | Y = 0 to Y = 155 mm (full depth) |
| Extent (Z) | Z = 0 to Z = 72 mm (full height) |
| Thickness (X) | 5.0 mm |
| Interior face | X = 155 mm plane |
| Exterior face | X = 160 mm plane |

Mirror of the left side wall. Exterior face (X = 160 plane) bonds the right T-rail tongue (Sub-B). Interior face (X = 155 plane) hosts lid snap detent ridges (Sub-H) and one linkage rod guide slot (Sub-G).

Internal corner fillet where the right wall meets the floor: 1.0 mm radius, running the full Y extent.

Internal corner fillet where the right wall meets the rear wall: 1.0 mm radius, running the full Z extent.

---

## Floor

| Parameter | Value |
|-----------|-------|
| Position (Z) | Z = 0 to Z = 3 mm |
| Extent (X) | X = 0 to X = 160 mm (full width, contiguous with side walls) |
| Extent (Y) | Y = 0 to Y = 155 mm (full depth, contiguous with rear wall) |
| Thickness (Z) | 3.0 mm |
| Interior face | Z = 3 mm plane |
| Exterior face | Z = 0 mm plane (build plate contact surface) |

The floor is a solid flat plate. Its interior surface (Z = 3 plane) is the mounting surface for pump bosses (Sub-C), motor cradles (Sub-C), and tube routing channels (Sub-F). Its exterior surface (Z = 0 plane) rests on the dock's horizontal support surfaces.

The floor spans the full outer envelope in X and Y, forming a contiguous solid with both side walls and the rear wall. There is no separate floor-to-wall joint -- the box is a single monolithic shell operation (outer block minus inner pocket).

---

## Rear Wall

| Parameter | Value |
|-----------|-------|
| Position (Y) | Y = 0 to Y = 8.5 mm |
| Extent (X) | X = 0 to X = 160 mm (full width, contiguous with side walls) |
| Extent (Z) | Z = 0 to Z = 72 mm (full height, contiguous with floor) |
| Thickness (Y) | 8.5 mm |
| Interior face | Y = 8.5 mm plane |
| Exterior face | Y = 0 mm plane (dock-facing) |

The rear wall is thicker than the side walls (8.5 mm vs 5 mm) to host the fitting bore array (Sub-D) and guide post array (Sub-E). The 8.5 mm thickness accommodates the John Guest PP0408W center body length of approximately 8.0 mm with clearance, plus the bore shoulder captures on both faces.

The exterior face (Y = 0 plane) is the dock-mating surface. It receives fitting entry funnels (Sub-D) and electrical contact pads (Sub-J). The interior face (Y = 8.5 plane) is the mounting surface for guide posts (Sub-E).

Internal corner fillet where the rear wall meets the floor: 1.0 mm radius, running from X = 5 to X = 155 (between side wall interior faces).

---

## Interior Pocket

The pocket is the void created by the shell operation (outer block minus inner block).

| Parameter | Value |
|-----------|-------|
| X extent | X = 5 to X = 155 mm (150 mm wide) |
| Y extent | Y = 8.5 to Y = 155 mm (146.5 mm deep) |
| Z extent | Z = 3 to Z = 72 mm (69 mm tall) |
| Volume | 150 x 146.5 x 69 = ~1,516,275 mm^3 (~1,516 cm^3) |

The pocket is open at the top (Z = 72 plane) and at the front (Y = 155 plane). All internal corners where walls meet the floor or each other have 1.0 mm fillets for printability and stress relief.

---

## Open Faces

### Top opening

| Parameter | Value |
|-----------|-------|
| Plane | Z = 72 mm |
| Extent (X) | X = 0 to X = 160 mm (full width including wall tops) |
| Extent (Y) | Y = 0 to Y = 155 mm (full depth including rear wall top) |
| Wall top surfaces | 5 mm wide strips (left, right side walls), 8.5 mm deep strip (rear wall) |

The top edges of the side walls (Z = 72 plane, 5 mm wide) and rear wall (Z = 72 plane, 8.5 mm deep) are the seating surfaces for the lid (Sub-H). Lid snap detent ridges are on the interior faces of the side walls near Z = 72, not on the top edges themselves.

### Front opening

| Parameter | Value |
|-----------|-------|
| Plane | Y = 155 mm |
| Extent (X) | X = 0 to X = 160 mm |
| Extent (Z) | Z = 0 to Z = 72 mm |
| Wall/floor cross-sections at Y = 155 | Left wall: 5 mm x 72 mm. Right wall: 5 mm x 72 mm. Floor: 160 mm x 3 mm. |

The front edges of the side walls and floor at Y = 155 are the receiving surfaces for the front bezel (Sub-I). The bezel overlaps the tray walls by 1.5 mm in a step-lap joint, so the front edges include shallow recesses cut by Sub-I.

---

## Internal Corner Fillets

All internal corners (where two interior faces meet) have 1.0 mm fillets for printability and stress relief.

| Junction | Location | Fillet radius | Run length |
|----------|----------|---------------|------------|
| Left wall to floor | X = 5, Z = 3, Y = 0..155 | 1.0 mm | 155 mm |
| Right wall to floor | X = 155, Z = 3, Y = 0..155 | 1.0 mm | 155 mm |
| Rear wall to floor | Y = 8.5, Z = 3, X = 5..155 | 1.0 mm | 150 mm |
| Left wall to rear wall | X = 5, Y = 8.5, Z = 0..72 | 1.0 mm | 72 mm |
| Right wall to rear wall | X = 155, Y = 8.5, Z = 0..72 | 1.0 mm | 72 mm |

No external corner fillets on the box shell. External fillets on the front bezel (2 mm) are specified by Sub-I. The T-rail junction fillet (1 mm at cap-to-wall bond) is specified by Sub-B.

---

## Print Orientation and Support

| Parameter | Value |
|-----------|-------|
| Orientation | Open top facing up (Z+ up on build plate) |
| Build plate contact | Z = 0 plane (floor exterior) |
| Supports needed | None. All walls rise vertically from the floor. No overhangs. The internal fillets (1.0 mm) are small enough to print without support at standard PETG settings (45-degree max overhang). |
| Layer height | 0.2 mm (standard). The box shell has no critical-tolerance features -- all precision geometry is added by downstream sub-components. |
| Wall line count | 4 perimeters minimum (0.4 mm nozzle x 4 = 1.6 mm perimeter shell on each face of the 5 mm side walls, with ~1.8 mm infill core; rear wall and floor are fully solid at their thicknesses). |

---

## Interface Surfaces Summary

| Interface | Location in part frame | Mating sub-component | Nature |
|-----------|----------------------|----------------------|--------|
| Left wall exterior | X = 0 plane | Sub-B (left T-rail tongue) | Bond surface (union) |
| Right wall exterior | X = 160 plane | Sub-B (right T-rail tongue) | Bond surface (union) |
| Interior floor | Z = 3 plane, X = 5..155, Y = 8.5..155 | Sub-C (pump bosses), Sub-F (tube channels) | Bond surface (union) |
| Rear wall interior | Y = 8.5 plane, X = 5..155, Z = 3..72 | Sub-E (guide posts) | Bond surface (union) |
| Rear wall exterior | Y = 0 plane, X = 0..160, Z = 0..72 | Sub-D (fitting bores, entry funnels), Sub-J (electrical pads) | Cut surface (subtraction) |
| Left wall interior | X = 5 plane, Y = 8.5..155, Z = 3..72 | Sub-G (linkage slot), Sub-H (lid snap ridges) | Cut (G) / Bond (H) |
| Right wall interior | X = 155 plane, Y = 8.5..155, Z = 3..72 | Sub-G (linkage slot), Sub-H (lid snap ridges) | Cut (G) / Bond (H) |
| Front edges | Y = 155 plane | Sub-I (bezel receiving features) | Cut surface (subtraction) |
| Top edges | Z = 72 plane, wall cross-sections | Sub-H (lid snap ridges, near top) | Bond surface (union) |

---

## Assembly Sequence

The box shell is Step 1 in the tray build sequence. It is the CREATE operation -- no prior geometry exists.

1. **Print the box shell** as a single monolithic part: outer block (160 x 155 x 72) minus inner pocket (150 x 146.5 x 69), with 1.0 mm internal fillets. Open top, open front.
2. **All subsequent sub-components** (B through J) are boolean operations on this solid. The shell must be fully formed before any union or cut is applied.

There is no multi-part assembly for Sub-A itself. It is one printed piece.

### Disassembly

The box shell cannot be disassembled -- it is a monolithic print. If it is damaged, it is reprinted. All features attached to it by other sub-components (bosses, posts, ridges) are integral to the same printed body.
