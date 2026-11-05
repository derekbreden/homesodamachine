"""Pin every Rust program in every Python process of a harness run.

HSM_PINS names a JSON file mapping a program name to its binary. When `_rust_part` is
imported, its `program(crate, name)` returns the pinned binary instead of building one.
"""
import json
import os
import sys

_PINS = os.environ.get('HSM_PINS')
if _PINS:
    import importlib.abc
    import importlib.machinery

    with open(_PINS) as _f:
        _TABLE = json.load(_f)

    class _PinFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if name != '_rust_part':
                return None
            spec = importlib.machinery.PathFinder.find_spec(name, path)
            if spec is None or spec.loader is None:
                return spec
            run = spec.loader.exec_module

            def exec_module(module):
                run(module)
                from pathlib import Path

                def program(crate, name):
                    if name not in _TABLE:
                        raise SystemExit(f'no pinned program {crate}/{name}')
                    return Path(_TABLE[name])

                module.program = program

            spec.loader.exec_module = exec_module
            return spec

    sys.meta_path.insert(0, _PinFinder())

# This file shadows the interpreter's own sitecustomize (Homebrew's sets sys.executable, the
# prefixes and its site-packages); run that one as Python would have.
import importlib.machinery as _machinery

_here = os.path.dirname(os.path.abspath(__file__))
_spec = _machinery.PathFinder.find_spec(
    'sitecustomize', [p for p in sys.path if os.path.abspath(p or '.') != _here])
if _spec is not None and _spec.origin and os.path.abspath(_spec.origin) != os.path.abspath(__file__):
    with open(_spec.origin) as _f:
        exec(compile(_f.read(), _spec.origin, 'exec'), {'__name__': 'sitecustomize', '__file__': _spec.origin})
