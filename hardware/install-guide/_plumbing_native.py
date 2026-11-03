"""Load optional native plumbing builders for hand-run illustration tools."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def load(driver, family):
    import cadquery as cq

    path = Path(__file__).with_name(f"_plumbing_native_{family}.py")
    name = f"{driver.__name__}_native_{family}"
    spec = importlib.util.spec_from_file_location(name, path)
    native = importlib.util.module_from_spec(spec)
    native.__dict__.update({key: value for key, value in vars(driver).items()
                            if not key.startswith("__")})
    native.__dict__.update({key: cq.Color(*value) for key, value in vars(driver).items()
                            if key.startswith("C_")})
    sys.modules[name] = native
    spec.loader.exec_module(native)
    return native
