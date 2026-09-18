"""Industrial faucet assembly, on the same hardware datums as Sculpted."""

from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parent
FAUCET = HARDWARE / "printed-parts" / "faucet"
INDUSTRIAL = FAUCET / "industrial"
for directory in (HARDWARE / "scripts", INDUSTRIAL, FAUCET / "faucet-shell"):
    sys.path.insert(0, str(directory))

from _cadq_export import export_assembly, import_assembly, import_step
from _materials import C_FAUCET_BLACK, M_TPU_BLACK
import faucet_shell as shell
import flute_payload
from industrial_display_cover import build_seated_display_cover


def build_assembly():
    bodies = import_assembly(HERE / "faucet-assembly.step")
    for name, part, material in (
        ("shell_base", "industrial-shell-base", C_FAUCET_BLACK),
        ("above_counter_plate", "industrial-above-counter-plate", C_FAUCET_BLACK),
        ("above_counter_gasket", "industrial-above-counter-gasket", M_TPU_BLACK),
    ):
        if name not in bodies:
            raise ValueError(f"the shared faucet has no {name}")
        bodies[name] = (import_step(INDUSTRIAL / f"{part}.step").val(), material)
    bodies["faucet-display-cover-seated"] = (build_seated_display_cover().val(), C_FAUCET_BLACK)
    assembly = cq.Assembly(name="faucet-industrial-assembly")
    for name, (body, color) in bodies.items():
        assembly.add(body, name=name, color=color)
    return assembly


def main():
    assembly = build_assembly()
    output = HERE / "faucet-industrial-assembly.step"
    export_assembly(assembly, str(output))
    surfaces = flute_payload.surfaces((INDUSTRIAL, FAUCET / "faucet-shell"))
    aliases = {
        "shell-base": surfaces["industrial-shell-base"],
        "shell-tip": surfaces["faucet-shell-tip"],
        "above-counter-plate": surfaces["industrial-above-counter-plate"],
        "above-counter-gasket": surfaces["industrial-above-counter-gasket"],
    }
    seated = build_seated_display_cover()
    pos, nrm, idx, fac = flute_payload.creased(shell.piece_mesh(seated))
    aliases["faucet-display-cover-seated"] = {
        "pos": pos.ravel().tolist(), "nrm": nrm.ravel().tolist(),
        "idx": idx.ravel().tolist(), "fac": fac.tolist(),
    }
    landed = flute_payload.graft(Path(str(output) + ".mesh"), aliases)
    if landed != len(aliases):
        raise ValueError(f"Industrial assembly: {landed}/{len(aliases)} exact surfaces")
    print(f"-> {output.name}: {landed} exact printed/seated surfaces")


if __name__ == "__main__":
    main()
