#!/usr/bin/env python3
"""What `_rust_part.start` promises a Rust part's run, each case in an interpreter of its own:

- the mandrel's and the fuse clamp's numbers load neither CadQuery nor OCP, and the clamp's
  selftest, which asks its program, loads neither;
- a colour made while CadQuery is deferred answers `linear`, `toTuple` and `hash` with OCCT's
  bits, and the colours and planes the shared modules made become the real ones once it loads;
- OCP's loops end in Python, once, however OCP comes to load;
- a run on the mesh kernel keeps its own CadQuery.

Nothing here takes the CAD lock or cuts a file. Run it when the template changes:

    tools/cad-venv/bin/python hardware/scripts/test_rust_part.py
"""
import json
import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANDREL = ROOT / "hardware/printed-parts/cold-core/coil-mandrel"
CLAMP = ROOT / "hardware/printed-parts/refrigeration/fuse-clamp"
CADLIB = ROOT / "hardware/printed-parts/cadlib"

PRELUDE = f"""
import json, sys
sys.path[:0] = [{str(HERE)!r}, {str(CADLIB)!r}, {str(MANDREL)!r}, {str(CLAMP)!r}]

def patched(cls):
    # Whether `_cadq_export._end_ocp_loops_in_python` has wrapped `cls.__iter__`, and how often.
    wraps, each = 0, cls.__iter__
    while "sized" in getattr(each, "__qualname__", ""):
        wraps += 1
        each = next(c.cell_contents for c in each.__closure__ if callable(c.cell_contents))
    return wraps
"""


def probe(*code: str, env=None) -> dict:
    """The JSON the last line of `code` prints, run from the root in a fresh interpreter."""
    source = PRELUDE + "".join(textwrap.dedent(part) for part in code)
    run = subprocess.run([sys.executable, "-c", source], cwd=ROOT,
                         env={**os.environ, **(env or {})}, capture_output=True, text=True)
    if run.returncode:
        raise AssertionError(f"the probe failed:\n{run.stderr}")
    return json.loads(run.stdout.strip().splitlines()[-1])


def committed(part: Path, name: str) -> dict:
    return json.loads((part / f"{name}.numbers.json").read_text())


class APartsRun(unittest.TestCase):
    def test_numbers_load_neither_cadquery_nor_ocp(self):
        for part, module, name in ((MANDREL, "coil_mandrel", "coil-mandrel"),
                                   (CLAMP, "fuse_clamp", "fuse-clamp")):
            with self.subTest(module):
                said = probe(f"""
                    import _rust_part
                    _rust_part.start()
                    numbers = __import__({module!r}).numbers()
                    print(json.dumps({{"cadquery": type(sys.modules["cadquery"]).__name__,
                                      "ocp": [m for m in ("OCP", "OCP.OCP") if m in sys.modules],
                                      "numbers": numbers}}))
                """)
                self.assertEqual(said["cadquery"], "_Deferred")
                self.assertEqual(said["ocp"], [])
                held = committed(part, name)
                self.assertEqual({k: said["numbers"][k] for k in held}, held)

    def test_the_clamps_selftest_asks_its_program_without_either(self):
        # A selftest builds nothing, so it takes no CAD lock here.
        said = probe(f"""
            import runpy
            sys.argv = [{str(CLAMP / "fuse_clamp.py")!r}, "selftest"]
            try:
                runpy.run_path(sys.argv[0], run_name="__main__")
                code = None
            except SystemExit as stop:
                code = stop.code
            print(json.dumps({{"code": code, "cadquery": type(sys.modules["cadquery"]).__name__,
                              "ocp": "OCP.OCP" in sys.modules}}))
        """, env={"HSM_NO_BUILD_LOCK": "1"})
        self.assertEqual(said, {"code": 0, "cadquery": "_Deferred", "ocp": False})


class AColourMadeWhileDeferred(unittest.TestCase):
    def test_it_answers_with_occts_bits_and_becomes_the_real_one(self):
        said = probe("""
            import random
            import _rust_part
            _rust_part.start()
            import cadquery as cq
            import _materials as m
            import world_workplane as ww
            constants = {k: v for k, v in vars(m).items() if isinstance(v, cq.Color)}
            planes = [v for v in vars(ww).values() if isinstance(v, cq.Plane)]
            rng = random.Random(7)
            triples = [(rng.random(), rng.random(), rng.random()) for _ in range(3000)]
            hexes = [f"#{b:02X}{(b * 37) % 256:02x}{255 - b:02X}" for b in range(256)]
            made = ([cq.Color(h) for h in hexes] + [cq.Color(*t) for t in triples]
                    + [cq.Color(*t, a=0.5) for t in triples[:200]]
                    + [cq.Color(*t, 0.25) for t in triples[:200]]
                    + [cq.Color(*t, 1.0, False) for t in triples[:200]])
            read = lambda c: [m.linear(c), list(c.toTuple()), hash(c)]
            before = {"constants": {k: read(c) for k, c in constants.items()},
                      "made": [read(c) for c in made], "hex": [m.linear(h) for h in hexes]}
            deferred = type(sys.modules["cadquery"]).__name__
            cq.Workplane                                  # CadQuery loads
            after = {"constants": {k: read(c) for k, c in constants.items()},
                     "made": [read(c) for c in made], "hex": [m.linear(cq.Color(h)) for h in hexes]}
            print(json.dumps({
                "deferred": deferred, "constants": len(constants), "planes": len(planes),
                "same": {k: before[k] == after[k] for k in before},
                "real": all(type(c) is cq.Color for c in [*constants.values(), *made])
                        and all(type(p) is cq.Plane for p in planes),
                "plane": list(ww.xy_plane_z_down.zDir.toTuple())}))
        """)
        self.assertEqual(said["deferred"], "_Deferred")
        self.assertGreater(said["constants"], 50)
        self.assertGreater(said["planes"], 5)
        self.assertEqual(said["same"], {"constants": True, "made": True, "hex": True})
        self.assertTrue(said["real"])
        self.assertEqual(said["plane"], [0.0, 0.0, -1.0])


class OCPsLoops(unittest.TestCase):
    CHECK = """
        from OCP.TopTools import TopTools_ListOfShape
        print(json.dumps({"wraps": patched(TopTools_ListOfShape),
                          "export": "_cadq_export" in sys.modules}))
    """

    def test_an_occt_generator_importing_a_rust_part_gets_the_patch(self):
        for module in ("coil_mandrel", "fuse_clamp"):
            with self.subTest(module):
                said = probe(f"import cadquery\nimport {module}\n", self.CHECK)
                self.assertEqual(said, {"wraps": 1, "export": True})

    def test_ocp_loaded_after_the_deferral_gets_it_once(self):
        # A part's chain imports `_cadq_export` before OCP loads; with no part, OCP's load does.
        for module in ("coil_mandrel", "fuse_clamp", None):
            with self.subTest(module):
                said = probe(f"""
                    import _rust_part
                    _rust_part.start()
                    import cadquery
                    {f"import {module}" if module else "assert '_cadq_export' not in sys.modules"}
                    cadquery.Workplane
                """, self.CHECK)
                self.assertEqual(said, {"wraps": 1, "export": True})


class AMeshKernelRun(unittest.TestCase):
    def test_keeps_its_own_cadquery(self):
        said = probe("""
            import meshcad
            meshcad.activate()
            import _rust_part
            _rust_part.start()
            import cadquery, coil_mandrel
            print(json.dumps({"mesh": bool(getattr(cadquery, "MESH", False)),
                              "cadquery": type(cadquery).__name__,
                              "color": coil_mandrel.numbers()["color"]}))
        """)
        self.assertEqual(said["mesh"], True)
        self.assertEqual(said["cadquery"], "module")
        self.assertEqual(said["color"], committed(MANDREL, "coil-mandrel")["color"])


if __name__ == "__main__":
    unittest.main()
