"""JSON transport for scalar Rust programs used by Python compatibility modules.

One process per program serves this interpreter. Rust owns the calculations and
file transformations; callers register the input and rewritten paths they hand
over through the existing build trace registries.
"""

import atexit
import itertools
import json
import subprocess
import threading

import _rust_part

# Runtime cleanup must follow worker cleanup, including workers first used by
# a generator's exit-time timing record.
_rust_part._slots()

_WORKERS = {}
_LOCK = threading.RLock()
_SERVICE_CONTEXT = threading.local()
_GENERATIONS = itertools.count(1)


def service_generation(service):
    """The live process identity behind one service's native object registry."""
    with _LOCK:
        worker = _WORKERS.get(tuple(service))
        return worker.generation if worker is not None and not worker.closed else None


def current_service():
    """The Rust service whose provider callback is currently running."""
    stack = getattr(_SERVICE_CONTEXT, "stack", ())
    return stack[-1] if stack else None


def json_default(value):
    """Materialize compiled numeric containers at an ordinary JSON boundary."""
    from _rust_objects import NativeProxy
    if isinstance(value, NativeProxy) and value._tag["$native"]["kind"] in {"dict", "list", "tuple", "set"}:
        return value._invoke("snapshot")
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


class _Worker:
    def __init__(self, crate, name, program=None):
        self.crate = crate
        self.name = name
        self.program = program or _rust_part.program(crate, name)
        self.busy = 0
        self.reentrant = False
        self.closed = False
        self.generation = next(_GENERATIONS)
        self.process = subprocess.Popen(
            [str(self.program), "--serve"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=_rust_part.ROOT,
            **_rust_part._slots().subprocess_kwargs(),
        )

    def request(self, encoded, callback=None, nested=False, completed=None):
        if self.process.poll() is not None:
            raise RuntimeError(f"{self.name} exited with status {self.process.returncode}")
        wire = '{"_hsm_request":' + encoded + '}' if nested else encoded
        self.process.stdin.write(wire + "\n")
        self.process.stdin.flush()
        while True:
            line = self.process.stdout.readline()
            if not line:
                status = self.process.wait()
                raise RuntimeError(f"{self.name} closed its response stream (status {status})")
            result = json.loads(line)
            if not isinstance(result, dict) or "_hsm_callback" not in result:
                break
            previous_reentry = self.reentrant
            self.reentrant = result.get("_hsm_reentrant", False)
            if not hasattr(_SERVICE_CONTEXT, "stack"):
                _SERVICE_CONTEXT.stack = []
            _SERVICE_CONTEXT.stack.append((self.crate, self.name))
            try:
                if callback is None:
                    raise ValueError("this Rust call has no provider callback")
                reply = {"_hsm_callback_result": callback(result["_hsm_callback"])}
                encoded = json.dumps(reply, ensure_ascii=False, allow_nan=False, default=json_default)
            except Exception as error:
                if self.closed:
                    raise
                encoded = json.dumps({"_hsm_callback_error": type(error).__name__ + ": " + str(error)}, ensure_ascii=False)
            finally:
                _SERVICE_CONTEXT.stack.pop()
                self.reentrant = previous_reentry
            self.process.stdin.write(encoded + "\n")
            self.process.stdin.flush()
        if isinstance(result, dict) and set(result) == {"_hsm_nested_result"}:
            result = result["_hsm_nested_result"]
        if completed is not None:
            completed[0] = True
        if isinstance(result, dict) and set(result) == {"error"}:
            raise ValueError(f"{self.name}: {result['error']}")
        return result

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            self.process.stdin.close()
        except (OSError, ValueError):
            pass
        self._wait()
        self.process.stdout.close()

    def _signal(self, method):
        try:
            method()
        except ProcessLookupError:
            pass

    def _wait(self):
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self._signal(self.process.terminate)
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._signal(self.process.kill)
                self.process.wait()

    def abort(self):
        """Discard a stream with an unfinished request before closing its pipes."""
        if self.closed:
            return
        self.closed = True
        self._signal(self.process.terminate)
        self._wait()
        for stream in (self.process.stdin, self.process.stdout):
            try:
                stream.close()
            except (OSError, ValueError):
                pass


def request(crate, name, payload, callback=None):
    """Send JSON, answering any raw-provider queries the Rust calculation makes.

    Reentrant services answer nested callbacks in the same resident process,
    preserving their mutable module values and compiled callable identities.
    """
    with _LOCK:
        # A native container can belong to this same worker. Complete its
        # snapshot request while the worker still waits for an ordinary call.
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, default=json_default)
        key = (crate, name)
        if key not in _WORKERS:
            _WORKERS[key] = _Worker(crate, name)
        worker = _WORKERS[key]
        reenter = worker.busy and worker.reentrant
        separate = worker.busy and not reenter
        if separate:
            worker = _Worker(crate, name, program=worker.program)
        worker.busy += 1
        completed = [False]
        try:
            return worker.request(encoded, callback, nested=reenter, completed=completed)
        except BaseException:
            # A consumed domain error leaves the line protocol synchronized.
            # Cancellation, malformed JSON and pipe failures do not.
            if not completed[0]:
                if _WORKERS.get(key) is worker:
                    del _WORKERS[key]
                try:
                    worker.abort()
                except Exception:
                    pass
            raise
        finally:
            worker.busy -= 1
            if separate:
                worker.close()


@atexit.register
def _close():
    for worker in _WORKERS.values():
        worker.close()
    _WORKERS.clear()
