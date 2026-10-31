"""Run a generator on the mesh kernel: `run.py <generator.py> [args...]`.

The generator runs as `__main__` with its own argv, exactly as `python <generator.py>` would,
except that every CadQuery solid it builds is a Manifold mesh.
"""

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import meshcad
    meshcad.activate()
    target = Path(sys.argv[1]).resolve()
    sys.argv = [str(target)] + sys.argv[2:]
    sys.path.insert(0, str(target.parent))
    runpy.run_path(str(target), run_name="__main__")
