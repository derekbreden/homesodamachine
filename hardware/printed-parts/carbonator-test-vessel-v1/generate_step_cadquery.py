import cadquery as cq
from pathlib import Path

OUTPUT = Path(__file__).parent

# ── Dimensions ────────────────────────────────────────────────────────────────
OD          = 50.0   # PA6-CF outer diameter (mm)
WALL_CF     = 4.0    # PA6-CF wall thickness (mm)
WALL_TPU    = 2.0    # TPU liner wall thickness (mm)
HEIGHT      = 60.0   # vessel body height above port floor (mm)
PORT_FLOOR  = 12.0   # solid floor thickness for 1/4-NPT engagement (mm)
TAP_DRILL   = 8.5    # pilot hole; drill to 11.1mm (11/32") and tap 1/4-NPT after print

# ── Test cap ─────────────────────────────────────────────────────────────────
CAP_PLUG_OD    = 41.6   # press-fit into CF_ID bore (0.4mm undersize for FDM tolerance)
CAP_PLUG_H     = 8.0    # depth into bore (mm)
CAP_FLANGE_OD  = 54.0   # flange OD — proud of vessel so hose clamp bites over the rim
CAP_FLANGE_H   = 3.0    # flange thickness (mm)

# ── Derived ───────────────────────────────────────────────────────────────────
CF_ID      = OD - 2 * WALL_CF        # 42.0mm — PA6-CF inner bore
WATER      = CF_ID - 2 * WALL_TPU    # 38.0mm — water cavity ID
TOTAL_H    = HEIGHT + PORT_FLOOR     # 72.0mm — total print height
BORE_START = PORT_FLOOR + WALL_CF    # 16.0mm — Z where bore begins (bottom of water cavity)


def make_body_cf():
    body = (
        cq.Workplane("XY")
        .circle(OD / 2)
        .extrude(TOTAL_H)
        .faces(">Z").workplane()
        .circle(CF_ID / 2)
        .cutBlind(HEIGHT - WALL_CF)
    )
    # Vertical pilot hole through port floor — parallel to print axis, no overhang
    pilot = (
        cq.Workplane("XY")
        .circle(TAP_DRILL / 2)
        .extrude(BORE_START + WALL_TPU + 2)
    )
    return body.cut(pilot)


def make_body_tpu():
    liner = (
        cq.Workplane("XY")
        .workplane(offset=BORE_START)
        .circle(CF_ID / 2)
        .extrude(HEIGHT - WALL_CF)
        .faces(">Z").workplane()
        .circle(WATER / 2)
        .cutBlind(HEIGHT - WALL_CF - WALL_TPU)
    )
    # Clear pilot hole through TPU floor
    port_clear = (
        cq.Workplane("XY")
        .workplane(offset=BORE_START)
        .circle(TAP_DRILL / 2 + 0.5)
        .extrude(WALL_TPU + 1)
    )
    return liner.cut(port_clear)


def make_test_cap():
    # Plug portion: press-fits into bore
    plug = (
        cq.Workplane("XY")
        .circle(CAP_PLUG_OD / 2)
        .extrude(CAP_PLUG_H)
    )
    # Flange: sits on vessel rim, hose clamp bites over the edge
    flange = (
        cq.Workplane("XY")
        .workplane(offset=CAP_PLUG_H)
        .circle(CAP_FLANGE_OD / 2)
        .extrude(CAP_FLANGE_H)
    )
    return plug.union(flange)


if __name__ == "__main__":
    cq.exporters.export(make_body_cf(), str(OUTPUT / "test_vessel_body_cf.step"))
    cq.exporters.export(make_body_tpu(), str(OUTPUT / "test_vessel_body_tpu.step"))
    cq.exporters.export(make_test_cap(), str(OUTPUT / "test_vessel_cap.step"))
    print(f"CF body:   {OUTPUT}/test_vessel_body_cf.step")
    print(f"TPU liner: {OUTPUT}/test_vessel_body_tpu.step")
    print(f"Test cap:  {OUTPUT}/test_vessel_cap.step")
