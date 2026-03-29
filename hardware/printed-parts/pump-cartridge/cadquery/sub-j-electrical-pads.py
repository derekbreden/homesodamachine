"""
Sub-J: Electrical Contact Pad Areas — CadQuery Generation Script

Generates a CUT TOOL (single union solid for subtraction from Sub-A) containing:
  - 5 terminal retention slots (T1-T4: 6.3mm type, T5: 4.8mm 2-pin type)
  - 4 blade openings within the retention slots
  - 4 wire pass-through holes (W1-W4, 3mm dia through 8.5mm rear wall)
  - 2 floor wire channels (6mm wide, 2mm deep)

Coordinate system:
  Origin: rear-left-bottom corner (dock side)
  X: width, left to right (0..160)
  Y: depth, rear (dock) to front (user) (0..155)
  Z: height, bottom to top (0..72)
  Envelope: 160x155x72 mm -> X:[0,160] Y:[0,155] Z:[0,72]

This is a CUT TOOL — all features are positive solids that will be
subtracted from the tray body. The union of all features is exported.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import cadquery as cq
from step_validate import Validator

# ==========================================================================
# Dimensions from spec
# ==========================================================================

# Tray reference
REAR_WALL_T = 8.5   # rear wall thickness (Y = 0..8.5)

# --- T1-T4: 6.3mm terminal retention slots ---
SLOT_63_W = 8.0      # slot width (X)
SLOT_63_H = 8.5      # slot height (Z)
SLOT_63_D = 3.0      # slot depth into rear wall (Y = 0 to 3.0)

# Blade openings within 6.3mm slots
BLADE_63_W = 7.0     # blade opening width (X)
BLADE_63_H = 2.0     # blade opening height (Z)
# Blade opening runs full slot depth Y = 0..3.0

# --- T5: 4.8mm 2-pin terminal retention slot ---
SLOT_48_W = 18.0     # slot width (X)
SLOT_48_H = 7.0      # slot height (Z)
SLOT_48_D = 3.0      # slot depth (Y)

# Blade openings within T5 slot
BLADE_48_W = 5.5     # each blade opening width (X)
BLADE_48_H = 1.5     # each blade opening height (Z)
BLADE_48_CC = 7.0    # center-to-center spacing of the two blade openings (X)

# --- Slot positions (center X, center Z) ---
T1_X, T1_Z = 25.0, 18.0    # Pump 1 (+)
T2_X, T2_Z = 25.0, 30.0    # Pump 1 (-)
T3_X, T3_Z = 135.0, 18.0   # Pump 2 (+)
T4_X, T4_Z = 135.0, 34.0   # Pump 2 (-)
T5_X, T5_Z = 80.0, 8.0     # Cartridge-present jumper

# --- Wire pass-through holes W1-W4 ---
WIRE_DIA = 3.0  # 3mm diameter

# Same centers as T1-T4 (concentric)
W1_X, W1_Z = T1_X, T1_Z
W2_X, W2_Z = T2_X, T2_Z
W3_X, W3_Z = T3_X, T3_Z
W4_X, W4_Z = T4_X, T4_Z

# --- Floor wire channels ---
CHAN_W = 6.0       # channel width (X)
CHAN_D_Z = 2.0     # channel depth (cut from Z=3 down to Z=1)
CHAN_Z_TOP = 3.0   # floor surface (Z)
CHAN_Z_BOT = 1.0   # bottom of channel (Z)
CHAN_Y_MIN = 9.0   # rear end
CHAN_Y_MAX = 124.0 # front end
CHAN_LEN = CHAN_Y_MAX - CHAN_Y_MIN  # 115mm

# Left channel (Pump 1): X = 22..28
LCHAN_X_MIN = 22.0
LCHAN_X_MAX = 28.0

# Right channel (Pump 2): X = 132..138
RCHAN_X_MIN = 132.0
RCHAN_X_MAX = 138.0


# ==========================================================================
# Feature Planning Table (Rubric 1)
# ==========================================================================
print("=" * 100)
print("FEATURE PLANNING TABLE — Sub-J: Electrical Contact Pad Areas (CUT TOOL)")
print("=" * 100)
print(f"{'#':<3} {'Feature':<28} {'Function':<30} {'Op':<6} {'Shape':<10} {'Axis':<5} {'Center (X,Y,Z)':<20} {'Dimensions':<30}")
print("-" * 100)
features = [
    ("1",  "T1 retention slot",      "Hold 6.3mm spade terminal", "Add", "Box",   "Y",  f"({T1_X}, 1.5, {T1_Z})",  f"{SLOT_63_W}x{SLOT_63_D}x{SLOT_63_H}"),
    ("2",  "T1 blade opening",       "Blade entry into T1",       "Add", "Box",   "Y",  f"({T1_X}, 1.5, {T1_Z})",  f"{BLADE_63_W}x{SLOT_63_D}x{BLADE_63_H}"),
    ("3",  "T2 retention slot",      "Hold 6.3mm spade terminal", "Add", "Box",   "Y",  f"({T2_X}, 1.5, {T2_Z})",  f"{SLOT_63_W}x{SLOT_63_D}x{SLOT_63_H}"),
    ("4",  "T2 blade opening",       "Blade entry into T2",       "Add", "Box",   "Y",  f"({T2_X}, 1.5, {T2_Z})",  f"{BLADE_63_W}x{SLOT_63_D}x{BLADE_63_H}"),
    ("5",  "T3 retention slot",      "Hold 6.3mm spade terminal", "Add", "Box",   "Y",  f"({T3_X}, 1.5, {T3_Z})",  f"{SLOT_63_W}x{SLOT_63_D}x{SLOT_63_H}"),
    ("6",  "T3 blade opening",       "Blade entry into T3",       "Add", "Box",   "Y",  f"({T3_X}, 1.5, {T3_Z})",  f"{BLADE_63_W}x{SLOT_63_D}x{BLADE_63_H}"),
    ("7",  "T4 retention slot",      "Hold 6.3mm spade terminal", "Add", "Box",   "Y",  f"({T4_X}, 1.5, {T4_Z})",  f"{SLOT_63_W}x{SLOT_63_D}x{SLOT_63_H}"),
    ("8",  "T4 blade opening",       "Blade entry into T4",       "Add", "Box",   "Y",  f"({T4_X}, 1.5, {T4_Z})",  f"{BLADE_63_W}x{SLOT_63_D}x{BLADE_63_H}"),
    ("9",  "T5 retention slot",      "Hold 4.8mm 2-pin housing",  "Add", "Box",   "Y",  f"({T5_X}, 1.5, {T5_Z})",  f"{SLOT_48_W}x{SLOT_48_D}x{SLOT_48_H}"),
    ("10", "T5 blade opening left",  "Left blade entry into T5",  "Add", "Box",   "Y",  f"(76.5, 1.5, {T5_Z})",    f"{BLADE_48_W}x{SLOT_48_D}x{BLADE_48_H}"),
    ("11", "T5 blade opening right", "Right blade entry into T5", "Add", "Box",   "Y",  f"(83.5, 1.5, {T5_Z})",    f"{BLADE_48_W}x{SLOT_48_D}x{BLADE_48_H}"),
    ("12", "W1 pass-through hole",   "Wire from interior to T1",  "Add", "Cyl",   "Y",  f"({W1_X}, 4.25, {W1_Z})", f"D{WIRE_DIA} x {REAR_WALL_T} deep"),
    ("13", "W2 pass-through hole",   "Wire from interior to T2",  "Add", "Cyl",   "Y",  f"({W2_X}, 4.25, {W2_Z})", f"D{WIRE_DIA} x {REAR_WALL_T} deep"),
    ("14", "W3 pass-through hole",   "Wire from interior to T3",  "Add", "Cyl",   "Y",  f"({W3_X}, 4.25, {W3_Z})", f"D{WIRE_DIA} x {REAR_WALL_T} deep"),
    ("15", "W4 pass-through hole",   "Wire from interior to T4",  "Add", "Cyl",   "Y",  f"({W4_X}, 4.25, {W4_Z})", f"D{WIRE_DIA} x {REAR_WALL_T} deep"),
    ("16", "Left floor channel",     "Pump 1 wire routing",       "Add", "Box",   "Y",  f"(25, 66.5, 2.0)",        f"{CHAN_W}x{CHAN_LEN}x{CHAN_D_Z}"),
    ("17", "Right floor channel",    "Pump 2 wire routing",       "Add", "Box",   "Y",  f"(135, 66.5, 2.0)",       f"{CHAN_W}x{CHAN_LEN}x{CHAN_D_Z}"),
]
for f in features:
    print(f"{f[0]:<3} {f[1]:<28} {f[2]:<30} {f[3]:<6} {f[4]:<10} {f[5]:<5} {f[6]:<20} {f[7]:<30}")
print("=" * 100)
print()

# ==========================================================================
# Helper: create a 6.3mm terminal slot with blade opening
# ==========================================================================
def make_63_slot(cx, cz):
    """Create a 6.3mm terminal retention slot + blade opening cut tool.

    Slot: 8.0w x 8.5h x 3.0d pocket at Y=0..3.0, centered on (cx, cz).
    Blade opening: 7.0w x 2.0h through-channel at same Y range, centered
    on slot center. The blade opening is a subset of the slot volume, so
    we just need the slot box (blade opening is inside it already for the
    outer pocket). But the blade opening extends through the remaining wall
    behind the slot (Y=3.0..8.5) so the dock blade can reach the terminal.

    Actually per spec: blade opening depth is "Full: 0 to 3.0 mm" — it's
    within the slot depth, not through the wall. The slot floor at Y=3.0
    is the stop for the terminal. The blade opening is an open channel in
    the slot floor allowing the blade to enter. Since the slot already
    removes material from Y=0 to Y=3.0 at the full 8.0x8.5 size, the
    blade opening is geometrically contained within the slot volume.

    So we only need the slot box itself. The blade opening is just a
    conceptual narrowing that the terminal housing walls create — the
    printed geometry is the full 8.0x8.5 pocket.

    Wait — re-reading the spec more carefully: "The blade opening is a
    rectangular through-slot in the slot floor (at Y = 3.0), centered on
    the slot center, extending from Y = 0 to Y = 3.0."

    This means the blade opening is NOT separate from the slot — it's
    within the same Y range. The 0.5mm walls on each side of the blade
    opening are the thin walls between slot edge and blade opening. But
    since this is a CUT TOOL, we model the slot as the 8.0x8.5 pocket.
    The blade opening (7.0x2.0) is a narrower passage but it's entirely
    within the already-cut slot volume. No additional cut needed.

    Actually no — re-reading again: the slot is the pocket where the
    terminal housing sits (8.0x8.5x3.0). The blade opening is a narrower
    slot (7.0x2.0) that may extend DEEPER than the pocket to let the
    blade pass through. But spec says blade opening depth is Y=0 to 3.0,
    same as slot. So both are the same depth.

    The blade opening matters because it's narrower — the walls between
    the 8.0mm slot and the 7.0mm blade opening (0.5mm each side) create
    the retention shoulders that hold the terminal housing. But since
    this is a CUT TOOL for the full slot pocket, we model just the
    8.0x8.5x3.0 box. The blade opening is a subset.
    """
    # Retention slot: 8.0 x 3.0 x 8.5 (W x D x H) at Y=0..3.0
    slot_x = cx - SLOT_63_W / 2.0
    slot_z = cz - SLOT_63_H / 2.0
    slot = cq.Workplane("XY").transformed(offset=(slot_x, 0, slot_z)).box(
        SLOT_63_W, SLOT_63_D, SLOT_63_H, centered=False
    )
    return slot


def make_48_slot(cx, cz):
    """Create the T5 4.8mm 2-pin terminal retention slot cut tool.

    Single 18.0w x 7.0h x 3.0d pocket at Y=0..3.0.
    Two blade openings are conceptual within this pocket volume.
    """
    slot_x = cx - SLOT_48_W / 2.0
    slot_z = cz - SLOT_48_H / 2.0
    slot = cq.Workplane("XY").transformed(offset=(slot_x, 0, slot_z)).box(
        SLOT_48_W, SLOT_48_D, SLOT_48_H, centered=False
    )
    return slot


def make_wire_hole(cx, cz):
    """Create a 3mm diameter cylindrical hole through the rear wall (Y=0..8.5).

    The cylinder is oriented along Y axis.
    """
    hole = (
        cq.Workplane("XZ")
        .center(cx, cz)
        .circle(WIRE_DIA / 2.0)
        .extrude(-REAR_WALL_T)  # XZ normal is -Y; negative extrude goes +Y
    )
    return hole


def make_floor_channel(x_min, x_max):
    """Create a floor wire channel: box at Z=1..3, Y=9..124."""
    channel = cq.Workplane("XY").transformed(offset=(x_min, CHAN_Y_MIN, CHAN_Z_BOT)).box(
        x_max - x_min, CHAN_LEN, CHAN_D_Z, centered=False
    )
    return channel


# ==========================================================================
# Modeling — build all cut tool features and union them
# ==========================================================================

print("Building cut tool features...")

# Start with T1 retention slot
tool = make_63_slot(T1_X, T1_Z)

# T2 retention slot
tool = tool.union(make_63_slot(T2_X, T2_Z))

# T3 retention slot
tool = tool.union(make_63_slot(T3_X, T3_Z))

# T4 retention slot
tool = tool.union(make_63_slot(T4_X, T4_Z))

# T5 retention slot (4.8mm 2-pin type)
tool = tool.union(make_48_slot(T5_X, T5_Z))

# Wire pass-through holes W1-W4
tool = tool.union(make_wire_hole(W1_X, W1_Z))
tool = tool.union(make_wire_hole(W2_X, W2_Z))
tool = tool.union(make_wire_hole(W3_X, W3_Z))
tool = tool.union(make_wire_hole(W4_X, W4_Z))

# Floor wire channels
tool = tool.union(make_floor_channel(LCHAN_X_MIN, LCHAN_X_MAX))
tool = tool.union(make_floor_channel(RCHAN_X_MIN, RCHAN_X_MAX))

print("Cut tool complete.")
print()

# ==========================================================================
# Export STEP
# ==========================================================================
out_path = Path(__file__).with_suffix(".step")
cq.exporters.export(tool, str(out_path))
print(f"Exported STEP: {out_path}")
print()

# ==========================================================================
# Validation (Rubric 3-5)
# ==========================================================================
print("Running validation checks...")
print()

v = Validator(tool)

# --- T1 retention slot ---
# Slot volume: X = 21..29, Y = 0..3, Z = 13.75..22.25
v.check_solid("T1 slot center", T1_X, 1.5, T1_Z, "solid inside T1 slot volume")
v.check_solid("T1 slot X- edge inside", T1_X - SLOT_63_W/2 + 0.3, 1.5, T1_Z, "solid near T1 left edge")
v.check_solid("T1 slot X+ edge inside", T1_X + SLOT_63_W/2 - 0.3, 1.5, T1_Z, "solid near T1 right edge")
v.check_solid("T1 slot Z- edge inside", T1_X, 1.5, T1_Z - SLOT_63_H/2 + 0.3, "solid near T1 bottom")
v.check_solid("T1 slot Z+ edge inside", T1_X, 1.5, T1_Z + SLOT_63_H/2 - 0.3, "solid near T1 top")
v.check_void("T1 slot outside X+", T1_X + SLOT_63_W/2 + 0.5, 1.5, T1_Z, "void outside T1 right")
# Behind the slot at Y=3.5 — wire hole W1 passes through here, so it's solid
v.check_solid("T1 slot behind wall (W1 hole)", T1_X, SLOT_63_D + 0.5, T1_Z, "solid behind T1 slot (wire hole passes through)")
# Check void at Y=3.5 but OUTSIDE wire hole radius
v.check_void("T1 behind wall outside W1", T1_X + WIRE_DIA/2 + 1.0, SLOT_63_D + 0.5, T1_Z, "void behind T1 slot outside wire hole")

# --- T2 retention slot ---
v.check_solid("T2 slot center", T2_X, 1.5, T2_Z, "solid inside T2 slot volume")
v.check_solid("T2 slot Z- inside", T2_X, 1.5, T2_Z - SLOT_63_H/2 + 0.3, "solid near T2 bottom")
v.check_solid("T2 slot Z+ inside", T2_X, 1.5, T2_Z + SLOT_63_H/2 - 0.3, "solid near T2 top")
v.check_void("T2 outside X-", T2_X - SLOT_63_W/2 - 0.5, 1.5, T2_Z, "void outside T2 left")

# --- T3 retention slot ---
v.check_solid("T3 slot center", T3_X, 1.5, T3_Z, "solid inside T3 slot volume")
v.check_solid("T3 slot X- inside", T3_X - SLOT_63_W/2 + 0.3, 1.5, T3_Z, "solid near T3 left edge")
v.check_void("T3 outside X+", T3_X + SLOT_63_W/2 + 0.5, 1.5, T3_Z, "void outside T3 right")

# --- T4 retention slot ---
v.check_solid("T4 slot center", T4_X, 1.5, T4_Z, "solid inside T4 slot volume")
v.check_solid("T4 slot Z+ inside", T4_X, 1.5, T4_Z + SLOT_63_H/2 - 0.3, "solid near T4 top")
v.check_void("T4 outside Z+", T4_X, 1.5, T4_Z + SLOT_63_H/2 + 0.5, "void above T4")

# --- T5 retention slot (4.8mm 2-pin) ---
# Slot volume: X = 71..89, Y = 0..3, Z = 4.5..11.5
v.check_solid("T5 slot center", T5_X, 1.5, T5_Z, "solid inside T5 slot volume")
v.check_solid("T5 slot X- inside", T5_X - SLOT_48_W/2 + 0.3, 1.5, T5_Z, "solid near T5 left edge")
v.check_solid("T5 slot X+ inside", T5_X + SLOT_48_W/2 - 0.3, 1.5, T5_Z, "solid near T5 right edge")
v.check_solid("T5 slot Z- inside", T5_X, 1.5, T5_Z - SLOT_48_H/2 + 0.3, "solid near T5 bottom")
v.check_solid("T5 slot Z+ inside", T5_X, 1.5, T5_Z + SLOT_48_H/2 - 0.3, "solid near T5 top")
v.check_void("T5 outside X-", T5_X - SLOT_48_W/2 - 0.5, 1.5, T5_Z, "void outside T5 left")
v.check_void("T5 outside X+", T5_X + SLOT_48_W/2 + 0.5, 1.5, T5_Z, "void outside T5 right")

# --- W1 wire pass-through (Y=0..8.5 cylinder at T1 center) ---
v.check_solid("W1 hole center Y=4.25", W1_X, 4.25, W1_Z, "solid at W1 center (wire hole + slot overlap)")
v.check_solid("W1 hole center Y=6.0", W1_X, 6.0, W1_Z, "solid at W1 center behind slot")
v.check_void("W1 outside radius", W1_X + WIRE_DIA/2 + 0.5, 6.0, W1_Z, "void outside W1 hole radius")

# --- W2 wire pass-through ---
v.check_solid("W2 hole center Y=6.0", W2_X, 6.0, W2_Z, "solid at W2 center behind slot")
v.check_void("W2 outside radius", W2_X, 6.0, W2_Z + WIRE_DIA/2 + 0.5, "void outside W2 hole radius")

# --- W3 wire pass-through ---
v.check_solid("W3 hole center Y=6.0", W3_X, 6.0, W3_Z, "solid at W3 center behind slot")
v.check_void("W3 outside radius", W3_X - WIRE_DIA/2 - 0.5, 6.0, W3_Z, "void outside W3 hole radius")

# --- W4 wire pass-through ---
v.check_solid("W4 hole center Y=6.0", W4_X, 6.0, W4_Z, "solid at W4 center behind slot")
v.check_void("W4 outside radius", W4_X, 6.0, W4_Z - WIRE_DIA/2 - 0.5, "void outside W4 hole radius")

# --- Left floor channel (X=22..28, Y=9..124, Z=1..3) ---
v.check_solid("Left channel center", 25.0, 66.5, 2.0, "solid at left channel center")
v.check_solid("Left channel rear end", 25.0, 9.5, 2.0, "solid near left channel rear")
v.check_solid("Left channel front end", 25.0, 123.5, 2.0, "solid near left channel front")
v.check_void("Left channel below Z", 25.0, 66.5, 0.5, "void below left channel")
v.check_void("Left channel above Z", 25.0, 66.5, 3.5, "void above left channel")
v.check_void("Left channel outside X-", 21.5, 66.5, 2.0, "void left of left channel")
v.check_void("Left channel outside X+", 28.5, 66.5, 2.0, "void right of left channel")
v.check_void("Left channel behind Y", 25.0, 8.5, 2.0, "void behind left channel")
v.check_void("Left channel ahead Y", 25.0, 124.5, 2.0, "void ahead of left channel")

# --- Right floor channel (X=132..138, Y=9..124, Z=1..3) ---
v.check_solid("Right channel center", 135.0, 66.5, 2.0, "solid at right channel center")
v.check_solid("Right channel rear end", 135.0, 9.5, 2.0, "solid near right channel rear")
v.check_solid("Right channel front end", 135.0, 123.5, 2.0, "solid near right channel front")
v.check_void("Right channel below Z", 135.0, 66.5, 0.5, "void below right channel")
v.check_void("Right channel above Z", 135.0, 66.5, 3.5, "void above right channel")
v.check_void("Right channel outside X-", 131.5, 66.5, 2.0, "void left of right channel")
v.check_void("Right channel outside X+", 138.5, 66.5, 2.0, "void right of right channel")

# --- Verify T1 and W1 are connected (slot at Y=0..3, hole at Y=0..8.5) ---
# At the slot/hole overlap point, should be solid
v.check_solid("T1-W1 overlap Y=1.5", T1_X, 1.5, T1_Z, "solid where slot and hole overlap")
# Behind the slot but within the wire hole, should be solid
v.check_solid("W1 behind slot Y=5.0", W1_X, 5.0, W1_Z, "solid in wire hole behind slot")

# --- Bounding box ---
bb = tool.val().BoundingBox()
# X: min at left channel X=22, max at right channel X=138
# But T3/T4 are at X=135 +/- 4 = X=131..139, so max is 139
# T1/T2 at X=25 +/- 4 = X=21..29, min is 21
# Left channel is X=22..28, right channel X=132..138
# So overall X: 21..139
v.check_bbox("X", bb.xmin, bb.xmax, 21.0, 139.0)
# Y: slots at Y=0..3, wire holes at Y=0..8.5, channels at Y=9..124
v.check_bbox("Y", bb.ymin, bb.ymax, 0.0, 124.0)
# Z: T5 bottom at Z=4.5, T4 top at Z=38.25, channels at Z=1..3
# Actually channels go down to Z=1, and T4 top = 34 + 4.25 = 38.25
v.check_bbox("Z", bb.zmin, bb.zmax, 1.0, 38.25)

# --- Solid integrity ---
v.check_valid()
# Note: this is a union of disjoint features, so it may be multiple bodies.
# Actually wire holes W1-W4 overlap with slots T1-T4 at Y=0..3, so those
# are connected. But T5 is separate from the channels.
# For a cut tool, multiple bodies is acceptable. Let's check but not fail.
n_bodies = len(tool.solids().vals())
print(f"  [INFO] Body count: {n_bodies} (cut tool, multiple bodies acceptable)")

# Volume check — rough envelope
# Slots: 4 * (8.0 * 3.0 * 8.5) + 1 * (18.0 * 3.0 * 7.0) = 816 + 378 = 1194
# Wire holes: 4 * (pi * 1.5^2 * 8.5) = 4 * 60.1 = 240.4 (but partially overlaps slots)
# Channels: 2 * (6.0 * 115.0 * 2.0) = 2760
# Total ~ 4194 mm3 (rough)
vol = tool.val().Volume()
print(f"  [INFO] Total volume: {vol:.1f} mm³ (expected ~4000-4200 mm³)")

# Summary
print()
if not v.summary():
    sys.exit(1)
