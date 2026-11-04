"""JSON transport for scalar Rust programs used by Python compatibility modules.

One process per program serves this interpreter. Rust owns the calculations and
file transformations; callers register the input and rewritten paths they hand
over through the existing build trace registries.
"""

import atexit
import json
import subprocess
import threading

import _rust_part

# Runtime cleanup must follow worker cleanup, including workers first used by
# a generator's exit-time timing record.
_rust_part._slots()

_WORKERS = {}
_LOCK = threading.RLock()


class _Worker:
    def __init__(self, crate, name):
        self.name = name
        program = _rust_part.program(crate, name)
        self.process = subprocess.Popen(
            [str(program), "--serve"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=_rust_part.ROOT,
            **_rust_part._slots().subprocess_kwargs(),
        )

    def request(self, payload):
        if self.process.poll() is not None:
            raise RuntimeError(f"{self.name} exited with status {self.process.returncode}")
        self.process.stdin.write(json.dumps(payload, ensure_ascii=False, allow_nan=False) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            status = self.process.wait()
            raise RuntimeError(f"{self.name} closed its response stream (status {status})")
        result = json.loads(line)
        if isinstance(result, dict) and set(result) == {"error"}:
            raise ValueError(f"{self.name}: {result['error']}")
        return result

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process.stdout.close()


def request(crate, name, payload):
    """Send a JSON value to a program's ``--serve`` loop and return its reply."""
    with _LOCK:
        key = (crate, name)
        if key not in _WORKERS:
            _WORKERS[key] = _Worker(crate, name)
        return _WORKERS[key].request(payload)


@atexit.register
def _close():
    for worker in _WORKERS.values():
        worker.close()
    _WORKERS.clear()
