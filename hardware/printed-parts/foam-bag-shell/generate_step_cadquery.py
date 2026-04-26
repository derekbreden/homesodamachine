from pathlib import Path
import cadquery as cq

# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════

tank_outer_radius = 63.5
copper_coil_buffer_radius = 7.0
shell_radius = tank_outer_radius + copper_coil_buffer_radius
tank_height = 152.4
elbows_height = 60.0
buffer_height = 8.6
shell_height = tank_height + elbows_height + buffer_height
wall_thickness = 1.0

def build_shell():
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
    cq.exporters.export(build_shell(), str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
