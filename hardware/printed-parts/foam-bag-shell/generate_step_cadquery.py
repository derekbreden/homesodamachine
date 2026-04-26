from pathlib import Path
import cadquery as cq

# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════

xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))

tank_outer_radius = 63.5
copper_coil_buffer_radius = 7.0
tank_copper_shell_radius = tank_outer_radius + copper_coil_buffer_radius

tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
tank_copper_shell_height = tank_height + below_tank_elbows_height + above_tank_elbows_height

tank_support_height = 30.0
wall_and_floor_thickness = 1.0


def build_tank_copper_shell():
    
    return (
        cq.Workplane(xz_plane_y_up)
        .circle(tank_copper_shell_radius)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )

def build_tank_support_wedge():
    outer_edge_of_support_wedge_radius = tank_copper_shell_radius - wall_and_floor_thickness
    lower_edge_of_support_wedge = wall_and_floor_thickness
    cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=lower_edge_of_support_wedge)
        .circle(outer_edge_of_support_wedge_radius)
        .extrude(tank_support_height)
    )
    cone = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=lower_edge_of_support_wedge)
        .circle(outer_edge_of_support_wedge_radius)
        .extrude(tank_support_height, taper=45)
    )
    return cylinder.cut(cone)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    out = Path(__file__).resolve().parent / "foam-bag-shell.step"
    cq.exporters.export(
        build_tank_copper_shell().union(build_tank_support_wedge()),
        str(out),
    )
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
