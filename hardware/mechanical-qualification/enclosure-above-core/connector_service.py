"""Manual reproduction of the recorded complete nominal XH housing sweeps.

The three straight motions use conservative continuous housing bounds. The
record separately identifies the removed funnel/frame/drain prerequisites and
the finite own-header omission during axial disengagement. These witnesses do
not qualify a latch, clone fit, hand force or flexible-lead dressing.
"""

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def phase_bounds(initial_bounds, displacements):
    """Enclose the whole housing throughout each complete straight motion."""
    low, high = initial_bounds
    offset = (0., 0., 0.)
    phases = []
    for displacement in displacements:
        following = tuple(a + b for a, b in zip(offset, displacement))
        phases.append([
            [low[i] + min(offset[i], following[i]) for i in range(3)],
            [high[i] + max(offset[i], following[i]) for i in range(3)],
        ])
        offset = following
    return phases


def housing_witness(initial_bounds, displacements):
    """Return the native stage solids and their complete compound."""
    import cadquery as cq

    stages = []
    for low, high in phase_bounds(initial_bounds, displacements):
        stages.append(cq.Solid.makeBox(
            *(high[i] - low[i] for i in range(3)), cq.Vector(*low)))
    return stages, cq.Compound.makeCompound(stages)


def recorded_witnesses():
    """Read the accepted native datums; do not generate or run a review."""
    record = json.loads((HERE / 'flavor-and-connector-review.json').read_text())
    return {
        name: housing_witness(
            path['datums']['initial_bounds_mm'],
            path['datums']['displacements_mm'])
        for name, path in record['connector_service']['paths'].items()
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='Directory for manually requested native BREP witnesses')
    arguments = parser.parse_args()
    arguments.output.mkdir(parents=True, exist_ok=True)
    for name, (stages, whole) in recorded_witnesses().items():
        whole.exportBrep(str(arguments.output / (name + '-service.brep')))
        for index, stage in enumerate(stages):
            stage.exportBrep(str(arguments.output / (name + '-' + str(index) + '.brep')))
