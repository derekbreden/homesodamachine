#!/usr/bin/env python3
"""Link a scratch faucet preparer against the exact Cargo build artifacts."""

import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    artifacts, source, output = map(Path, sys.argv[1:])
    dependencies = {
        "anyhow", "hsm_faucet_numbers", "hsm_print_prep", "hsm_run_slots", "serde_json",
    }
    libraries = {}
    with artifacts.open() as rows:
        for line in rows:
            row = json.loads(line)
            if row.get("reason") != "compiler-artifact":
                continue
            name = row["target"]["name"]
            if name not in dependencies:
                continue
            files = [Path(path) for path in row["filenames"]]
            rlib = next((path for path in files if path.suffix == ".rlib"), None)
            if rlib is None:
                continue
            hashed = next((path.with_suffix(".rlib") for path in files if path.suffix == ".rmeta"), rlib)
            libraries[name] = hashed if hashed.is_file() else rlib
    missing = dependencies - libraries.keys()
    if missing:
        sys.exit(f"Missing Cargo libraries: {', '.join(sorted(missing))}")
    command = [
        os.environ.get("RUSTC", "rustc"), "--edition=2024", "--crate-name", "faucet_native_scratch",
        "-C", "opt-level=3", str(source.resolve()), "-o", str(output),
    ]
    for directory in sorted({path.parent for path in libraries.values()}):
        command.extend(["-L", f"dependency={directory}"])
    for name, path in sorted(libraries.items()):
        command.extend(["--extern", f"{name}={path}"])
    env = os.environ | {"HSM_DISPENSE_TRIAL_PREPARER": str(source.resolve())}
    subprocess.run(command, env=env, check=True)


if __name__ == "__main__":
    main()
