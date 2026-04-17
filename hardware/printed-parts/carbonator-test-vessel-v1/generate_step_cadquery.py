import cadquery as cq
from pathlib import Path

OUTPUT = Path(__file__).parent

# ── Body dimensions ──────────────────────────────────────────────────────────
OD        = 50.0   # PA6-CF outer diameter (mm)
WALL_CF   = 4.0    # PA6-CF wall and floor thickness (mm)
WALL_TPU  = 2.0    # TPU liner wall and floor thickness (mm)
HEIGHT    = 60.0   # vessel height (mm)

# ── NPT boss ─────────────────────────────────────────────────────────────────
BOSS_OD   = 18.0   # boss outer diameter — minimum ~16mm for 1/4-NPT thread engagement
BOSS_H    = 8.0    # boss protrusion beyond vessel OD (mm)
PORT_Z    = 25.0   # boss center height from vessel bottom (mm)
TAP_DRILL = 8.5    # pilot hole; drill to 11.1mm (11/32") and tap 1/4-NPT after print

# ── Derived ───────────────────────────────────────────────────────────────────
CF_ID  = OD - 2 * WALL_CF       # 42.0mm — PA6-CF inner bore
WATER  = CF_ID - 2 * WALL_TPU   # 38.0mm — water cavity ID


def make_body_cf():
    # Outer cylinder with closed 4mm floor, hollowed from the top
    shell = (
        cq.Workplane("XY")
        .circle(OD / 2)
        .extrude(HEIGHT)
        .faces(">Z").workplane()
        .circle(CF_ID / 2)
        .cutBlind(HEIGHT - WALL_CF)
    )
    # Radial NPT boss protruding in +X
    boss = (
        cq.Workplane("XY")
        .transformed(
            offset=cq.Vector(OD / 2, 0, PORT_Z),
            rotate=cq.Vector(0, 90, 0),
        )
        .circle(BOSS_OD / 2)
        .extrude(BOSS_H)
    )
    # Pilot through-hole from boss face inward through CF wall
    pilot = (
        cq.Workplane("XY")
        .transformed(
            offset=cq.Vector(OD / 2 + BOSS_H, 0, PORT_Z),
            rotate=cq.Vector(0, -90, 0),
        )
        .circle(TAP_DRILL / 2)
        .extrude(BOSS_H + WALL_CF + 2)
    )
    return shell.union(boss).cut(pilot)


def make_body_tpu():
    # Cup sitting on CF floor: OD = CF_ID, 2mm walls, 2mm floor at bottom
    liner = (
        cq.Workplane("XY")
        .workplane(offset=WALL_CF)
        .circle(CF_ID / 2)
        .extrude(HEIGHT - WALL_CF)
        .faces(">Z").workplane()
        .circle(WATER / 2)
        .cutBlind(HEIGHT - WALL_CF - WALL_TPU)
    )
    # Clear TPU at the port so the hole is open to the water cavity
    port_clear = (
        cq.Workplane("XY")
        .transformed(
            offset=cq.Vector(CF_ID / 2, 0, PORT_Z),
            rotate=cq.Vector(0, -90, 0),
        )
        .circle(TAP_DRILL / 2 + 0.5)
        .extrude(WALL_TPU + 1)
    )
    return liner.cut(port_clear)


if __name__ == "__main__":
    cq.exporters.export(make_body_cf(), str(OUTPUT / "test_vessel_body_cf.step"))
    cq.exporters.export(make_body_tpu(), str(OUTPUT / "test_vessel_body_tpu.step"))
    print(f"CF body:   {OUTPUT}/test_vessel_body_cf.step")
    print(f"TPU liner: {OUTPUT}/test_vessel_body_tpu.step")
