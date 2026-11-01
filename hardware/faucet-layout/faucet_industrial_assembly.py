"""Industrial faucet assembly, on the same hardware datums as Sculpted.

THE KERNEL CUTS THE FILES. `numbers()` is the faucet assembly's own (`faucet_assembly.numbers`)
with the Industrial shell base, above-counter plate, gasket and seated display cover standing in
for the Sculpted ones, and `faucet_industrial_assembly.rs`, beside this module, cuts
`faucet-industrial-assembly.step` and the payload `/3d` draws from them.
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parent
FAUCET = HARDWARE / "printed-parts" / "faucet"
INDUSTRIAL = FAUCET / "industrial"
for directory in (HARDWARE / "scripts", INDUSTRIAL, FAUCET / "faucet-shell"):
    sys.path.insert(0, str(directory))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import faucet_assembly
import flute_payload
from industrial_display_cover import SEATED_STEP


def numbers():
    import _rust_part

    n = faucet_assembly.numbers()
    n["name"] = "faucet-industrial-assembly"
    for body, part in (("shell_base", "industrial-shell-base"),
                       ("above_counter_plate", "industrial-above-counter-plate"),
                       ("above_counter_gasket", "industrial-above-counter-gasket")):
        n[body] = _rust_part.step(INDUSTRIAL / f"{part}.step")
    n["display_cover"] = _rust_part.step(SEATED_STEP)
    return n


def main():
    import _rust_part

    said = _rust_part.cut("faucet", "faucet-industrial-assembly", numbers(), HERE)
    output = HERE / "faucet-industrial-assembly.step"
    print("-> " + ", ".join(said["files"]))
    surfaces = flute_payload.surfaces((INDUSTRIAL, FAUCET / "faucet-shell", FAUCET / "umbilical-organizer", FAUCET / "lever-replica"))
    aliases = {
        "lever": surfaces["lever"],
        "shell-base": surfaces["industrial-shell-base"],
        "shell-tip": surfaces["faucet-shell-tip"],
        "above-counter-plate": surfaces["industrial-above-counter-plate"],
        "above-counter-gasket": surfaces["industrial-above-counter-gasket"],
        "umbilical-organizer": surfaces["umbilical-organizer"],
    }
    landed = flute_payload.graft(Path(str(output) + ".mesh"), aliases)
    if landed != len(aliases):
        raise ValueError(f"Industrial assembly: {landed}/{len(aliases)} exact surfaces")
    print(f"-> {output.name}: {landed} exact printed surfaces")


if __name__ == "__main__":
    main()
