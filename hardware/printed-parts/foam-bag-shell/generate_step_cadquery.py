from pathlib import Path
import cadquery as cq

# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════

tank_outer_radius = 63.5
copper_coil_buffer_radius = 7.0
floor_radius = tank_outer_radius + copper_coil_buffer_radius
floor_thickness = 1.0
wall_height = 220.0

def build_floor():
    return (
        cq.Workplane("XZ")
        .circle(floor_radius)
        .extrude(floor_thickness)
    )

def build_wall():
    return (
        cq.Workplane("XZ")
        .workplane(offset=floor_thickness)
        .circle(floor_radius)
        .extrude(wall_height)
    )


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    shell = build_floor().union(build_wall())

    out = Path(__file__).resolve().parent / "foam-bag-shell.step"
    cq.exporters.export(shell, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
