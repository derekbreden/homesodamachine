from pathlib import Path
import cadquery as cq

# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════

tank_outer_radius = 63.5
copper_coil_radius = 7.0

def build_floor():
    floor_radius = tank_outer_radius + copper_coil_radius
    floor_thickness = 1.0
    return (
        cq.Workplane("XZ")
        .circle(floor_radius)
        .extrude(floor_thickness)
    )


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    floor_solid = build_floor()

    out = Path(__file__).resolve().parent / "foam-bag-shell.step"
    cq.exporters.export(floor_solid, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
