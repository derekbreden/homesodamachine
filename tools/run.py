#!/usr/bin/env python3
"""Run a heavy command through the native host runner."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _run_native import executable, read as _native


def script_key(command): return _native("runner_script_key", {"command": list(map(str, command))})
def limit_jobs(command, jobs): return _native("runner_limit_jobs", {"command": list(map(str, command)), "jobs": jobs})
def workspace_root(): return Path(_native("runner_workspace_root"))
def _producer_data(producer):
    if producer is None:
        return None
    host, port, token, root, directory, outputs = producer
    return [host, port, token, str(root), str(directory), list(map(str, outputs))]


def viewer_producer(command, root):
    row = _native("runner_viewer_producer", {"command": list(map(str, command)), "root": str(root)})
    if row is None:
        return None
    host, port, token, root, directory, outputs = row
    return host, port, token, Path(root), Path(directory), list(map(Path, outputs))


def viewer_snapshot(producer):
    return {Path(name): tuple(stamp) for name, stamp in _native("runner_viewer_snapshot", {"producer": _producer_data(producer)}).items()}


def viewer_completed(producer, before):
    return _native("runner_viewer_completed", {"producer": _producer_data(producer), "before": {str(name): stamp for name, stamp in before.items()}})


def main():
    runner = str(executable())
    os.execv(runner, [runner, *sys.argv[1:]])


if __name__ == "__main__":
    main()
