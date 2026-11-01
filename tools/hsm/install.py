#!/usr/bin/env python3
"""Install a built hsm under its build ID, with one command and retained legacy restarts.

    python3 tools/hsm/install.py tools/hsm/target/release/hsm
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess


MARKER = "#!/bin/sh\n# hsm build launcher\n"


def endpoint(binary):
    return json.loads(subprocess.check_output([str(binary), "endpoint"], text=True))


def put(path, data, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{os.getpid()}")
    temp.write_bytes(data)
    temp.chmod(mode)
    temp.replace(path)


def launcher(current, legacy, sockets):
    text = MARKER
    if legacy:
        # Earlier MCP clients restart current_exe() with their fixed socket. Their daemon
        # keeps its real build ID because this route executes the retained binary itself.
        text += """socket=
previous=
action=
for arg in "$@"; do
    if [ -n "$previous" ]; then
        if [ "$previous" = --socket ]; then socket=$arg; fi
        previous=
        continue
    fi
    case "$arg" in
        --socket) previous=--socket ;;
        --socket=*) socket=${arg#--socket=} ;;
        --root|--scene|--store|--cache-mb|--build-mb|--keep-mb|--idle-minutes) previous=value ;;
        -*) ;;
        *) if [ -z "$action" ]; then action=$arg; fi ;;
    esac
done
if [ "$action" = daemon ]; then
    case "$socket" in
"""
        text += "        " + "|".join(shlex.quote(s) for s in sockets)
        text += f") exec {shlex.quote(str(legacy))} \"$@\" ;;\n"
        text += "    esac\nfi\n"
    return text + f"exec {shlex.quote(str(current))} \"$@\"\n"


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("binary", type=Path)
    args.add_argument("--root", type=Path, default=Path.home() / ".local")
    args.add_argument("--legacy-socket", action="append", default=[],
                      help="additional endpoint an already-running unversioned MCP restarts")
    args = args.parse_args()
    binary, root = args.binary.resolve(), args.root.resolve()
    build = endpoint(binary)["build_id"]
    directory = root / "lib" / "hsm"
    current = directory / build / "hsm"
    if not current.exists():
        put(current, binary.read_bytes(), 0o555)
    elif endpoint(current)["build_id"] != build:
        raise SystemExit(f"{current} serves another build; installation left unchanged")

    state_path = directory / "launcher.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {"legacy": None, "legacy_sockets": []}
    command = root / "bin" / "hsm"
    if state["legacy"] is None and command.exists():
        data = command.read_bytes()
        if not data.startswith(MARKER.encode()):
            digest = hashlib.sha256(data).hexdigest()
            legacy = directory / "legacy" / digest / "hsm"
            if not legacy.exists():
                put(legacy, data, 0o555)
            state["legacy"] = str(legacy)
    state["legacy_sockets"] = sorted(set(state["legacy_sockets"] + args.legacy_socket
                                         + [f"/tmp/hsm-{os.geteuid()}/engine.sock"]))
    put(state_path, (json.dumps(state, indent=2) + "\n").encode(), 0o644)
    put(command, launcher(current, state["legacy"], state["legacy_sockets"]).encode(), 0o755)
    print(json.dumps({"command": str(command), "build_id": build,
                      "executable": str(current), "legacy": state["legacy"]}, indent=2))


if __name__ == "__main__":
    main()
