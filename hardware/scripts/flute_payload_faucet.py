"""Publish the faucet's checked print meshes as viewer payloads.

The shell, display cover, above-counter plate and gasket retain every triangle
from their actual STLs. The assembled shell payload, which `faucet_shell.py` writes
beside `faucet-shell.step`, receives both printed shell surfaces.
The shared pipeline also handles the appliance's fluted parts; the faucet
itself has smooth CAD-native surfaces.
"""

import sys

import flute_payload


if __name__ == "__main__":
    sys.exit(flute_payload.rust_main(flute_payload.FAUCET_DIRS, preserve_print_triangles=True))
