from pathlib import Path
import cadquery as cq

# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════

tank_outer_radius = 63.5
copper_coil_buffer_radius = 7.0
tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
tank_support_height = 30.0
wall_thickness = 1.0

def build_tank_copper_shell():
    shell_height = tank_height + below_tank_elbows_height + above_tank_elbows_height
    shell_radius = tank_outer_radius + copper_coil_buffer_radius
    return (
        cq.Workplane("XZ")
        .circle(shell_radius)
        .extrude(shell_height)
        .faces(">Y")
        .shell(-wall_thickness)
    )

def build_tank_support_wedge():
    shell_radius = tank_outer_radius + copper_coil_buffer_radius
    inner_face_radius = shell_radius - wall_thickness
    inner_radius = inner_face_radius - tank_support_height
    bottom_y = wall_thickness
    top_y = wall_thickness + tank_support_height
    profile = (
        cq.Workplane("XY")
        .moveTo(inner_radius, top_y)
        .lineTo(inner_face_radius, top_y)
        .lineTo(inner_face_radius, bottom_y)
        .close()
    )
    return profile.revolve(360, axisStart=(0, 0, 0), axisEnd=(0, 1, 0))


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
