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


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    out = Path(__file__).resolve().parent / "foam-bag-shell.step"
    cq.exporters.export(build_tank_copper_shell(), str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
