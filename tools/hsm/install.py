#!/usr/bin/env python3
"""Install the built hsm and its native host runtime."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _run_native import executable, read as _native


def launcher(current, legacy, sockets):
    return _native("runner_launcher", {"current": str(current), "legacy": str(legacy) if legacy is not None else None,
                                       "sockets": list(sockets)})


def main():
    runner = str(executable())
    os.execv(runner, [runner, "--install-hsm", str(ROOT), *sys.argv[1:]])


if __name__ == "__main__":
    main()
