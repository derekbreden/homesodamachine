"""
STEP Validation Helpers — shared infrastructure for generation scripts.

Provides point-in-solid probing and structured pass/fail reporting.
Each generation script imports this module, builds its model, then
calls check functions to verify every feature against the spec.

Usage in a generation script:

    from step_validate import Validator

    v = Validator(solid)           # solid is a CadQuery Workplane or Shape

    # Probe material presence/absence at specific coordinates
    v.check_void("Bore 1 center", cx, 1.0, cz, "void at outer bore depth")
    v.check_solid("Bore 1 wall", cx + 8.0, 1.0, cz, "solid outside bore")

    # Bounding box checks
    v.check_bbox("X", bb.xmin, bb.xmax, -9.15, 68.15)

    # Solid validity
    v.check_valid()
    v.check_single_body()
    v.check_volume(expected_envelope=59*6*47, fill_range=(0.5, 1.2))

    # Print summary and exit(1) if any failures
    v.summary()
"""

from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt


class Validator:
    """Structured validation for CadQuery STEP generation scripts."""

    def __init__(self, workplane):
        """Initialize with a CadQuery Workplane object.

        Args:
            workplane: A CadQuery Workplane. The underlying OCC solid is
                       extracted automatically via .val().
        """
        self._workplane = workplane
        self._solid = workplane.val()
        self._results = []

    # ------------------------------------------------------------------
    # Core probing
    # ------------------------------------------------------------------

    def _classify(self, x, y, z, tol=0.001):
        """Return OCC topology state: 0=IN, 1=ON, 2=OUT."""
        classifier = BRepClass3d_SolidClassifier(
            self._solid.wrapped, gp_Pnt(x, y, z), tol
        )
        return classifier.State()

    def is_void(self, x, y, z, tol=0.001):
        """True if the point is outside the solid (empty space)."""
        return self._classify(x, y, z, tol) != 0

    def is_solid(self, x, y, z, tol=0.001):
        """True if the point is inside the solid (material present)."""
        return self._classify(x, y, z, tol) == 0

    # ------------------------------------------------------------------
    # Check methods — each records a PASS/FAIL result
    # ------------------------------------------------------------------

    def _record(self, name, passed, detail):
        status = "PASS" if passed else "FAIL"
        self._results.append((name, status, detail))
        print(f"  [{status}] {name}: {detail}")
        return passed

    def check_void(self, name, x, y, z, detail=None):
        """Assert that (x, y, z) is empty space (bore, slot, hole)."""
        result = self.is_void(x, y, z)
        detail = detail or f"void at ({x:.2f}, {y:.2f}, {z:.2f})"
        return self._record(name, result, detail)

    def check_solid(self, name, x, y, z, detail=None):
        """Assert that (x, y, z) is inside the solid (material)."""
        result = self.is_solid(x, y, z)
        detail = detail or f"solid at ({x:.2f}, {y:.2f}, {z:.2f})"
        return self._record(name, result, detail)

    def check_bbox(self, axis_name, actual_min, actual_max, expected_min, expected_max, tol=0.5):
        """Assert bounding box span matches expected range on one axis."""
        ok = abs(actual_min - expected_min) < tol and abs(actual_max - expected_max) < tol
        detail = f"[{actual_min:.2f}, {actual_max:.2f}] vs expected [{expected_min:.2f}, {expected_max:.2f}]"
        return self._record(f"Bounding box {axis_name}", ok, detail)

    def check_valid(self):
        """Assert the solid passes OCC validity check."""
        ok = self._solid.isValid()
        return self._record("Solid validity", ok, "valid" if ok else "INVALID solid")

    def check_single_body(self):
        """Assert the result is a single connected solid (not fragmented)."""
        n = len(self._workplane.solids().vals())
        ok = n == 1
        return self._record("Single body", ok, f"{n} body(ies)")

    def check_volume(self, expected_envelope, fill_range=(0.5, 1.2)):
        """Assert volume is within expected fraction of the envelope volume."""
        vol = self._solid.Volume()
        ratio = vol / expected_envelope
        lo, hi = fill_range
        ok = lo < ratio < hi
        return self._record(
            "Volume ratio",
            ok,
            f"{vol:.1f} mm³ ({ratio:.1%} of {expected_envelope:.0f} mm³ envelope, "
            f"expected {lo:.0%}–{hi:.0%})"
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    @property
    def all_passed(self):
        return all(s == "PASS" for _, s, _ in self._results)

    @property
    def fail_count(self):
        return sum(1 for _, s, _ in self._results if s == "FAIL")

    @property
    def pass_count(self):
        return sum(1 for _, s, _ in self._results if s == "PASS")

    def summary(self):
        """Print summary and return True if all passed."""
        print()
        print("=" * 60)
        total = len(self._results)
        if self.all_passed:
            print(f"ALL {total} CHECKS PASSED")
        else:
            print(f"{self.fail_count} of {total} CHECKS FAILED:")
            for name, status, detail in self._results:
                if status == "FAIL":
                    print(f"  - {name}: {detail}")
        print("=" * 60)
        return self.all_passed
