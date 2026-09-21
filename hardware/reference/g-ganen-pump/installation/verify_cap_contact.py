"""Exercise the production bearing classifier on a retained native placed pack.

This reads exact retained geometry, then injects known invalid contact cases. It
never exports production geometry and does not model rubber compression.
"""
from argparse import ArgumentParser
from pathlib import Path
from types import SimpleNamespace
import hashlib
import inspect
import json
import sys
import time

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'hardware/manifold-layout'))
import enclosure_assembly as ea
import _scorecard
import g_ganen_installation as pump


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bounds(shape):
    b = shape.BoundingBox()
    return [[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]]


def run(pack, output):
    started = time.monotonic()
    frames = json.loads((pack / 'frames.json').read_text())
    actual = cq.Shape.importBrep(str(pack / frames[pump.SCENE_KEY]['brep']))
    foam = cq.Shape.importBrep(str(pack / frames['foam-assembly']['brep']))
    local = pump.suction()[0]
    world = frames[pump.SCENE_KEY]['ports']['suction'][0]
    origin = (world[0] + local[1], world[1] - local[0], world[2] - local[2])
    rebuilt, carry = ea.seat_body(pump.build(), (((0, 0, 1), pump.YAW),),
                                 station=(pump.bearing_datum(), origin))
    if max(abs(a-b) for rowa, rowb in zip(bounds(actual), bounds(rebuilt))
           for a, b in zip(rowa, rowb)) > 1e-5:
        raise ValueError('Retained native pump does not match the installed reference pose')
    inputs = [pack/'frames.json', pack/frames[pump.SCENE_KEY]['brep'],
              pack/frames['foam-assembly']['brep'], Path(pump.__file__),
              HERE/'verify_cap_contact.py', pump.envelope.NATIVE]
    hashes = {str(path): sha(path) for path in inputs}
    classifier_sha = hashlib.sha256(inspect.getsource(_scorecard.pump_cap_contact).encode()).hexdigest()
    a = SimpleNamespace(carries={pump.SCENE_KEY: carry})
    bodies = {pump.SCENE_KEY: actual, 'foam-assembly': foam}
    cases = []

    def check(name, fixture, expected, assembly=a):
        reading = _scorecard.pump_cap_contact(assembly, fixture)
        passed = reading['pass'] is expected
        cases.append({'case': name, 'expected_classification_pass': expected,
                      'reading': reading, 'test_pass': passed})
        print(name, json.dumps(reading), 'PASS' if passed else 'FAIL', flush=True)
        if not passed:
            raise AssertionError(name)

    check('Four exact unloaded rubber-foot bearing contacts', bodies, True)
    # A cap addition that actually enters the rigid motor casing must stay a hit.
    motor = pump.build_parts()['motor_can_vent_filled_envelope'].moved(carry.where)
    center = motor.Center()
    intrusion = cq.Solid.makeBox(3, 3, 3, center - cq.Vector(1.5, 1.5, 1.5))
    check('Rigid cap addition above bearing plane',
          {pump.SCENE_KEY: actual, 'foam-assembly': cq.Compound.makeCompound([foam, intrusion])}, False)
    # Even a body addition absent from the reference split must remain visible
    # in the complete-pump residual; the masks cannot exempt the whole pair.
    cap_z = ea.cap_face(foam)
    outside = cq.Solid.makeBox(3, 3, 3, cq.Vector(75, origin[1], cap_z+5))
    check('Extra shared material outside every foot mask',
          {pump.SCENE_KEY: cq.Compound.makeCompound([actual, outside]),
           'foam-assembly': cq.Compound.makeCompound([foam, outside])}, False)
    _, wrong = ea.seat_body(pump.build(), (((0, 0, 1), pump.YAW),),
                           station=(pump.bearing_datum(), (origin[0], origin[1], origin[2]+.05)))
    try:
        _scorecard.pump_cap_contact(SimpleNamespace(carries={pump.SCENE_KEY: wrong}), bodies)
    except ValueError as exc:
        cases.append({'case': 'Bearing plane mismatch', 'rejected': str(exc), 'test_pass': True})
    else:
        raise AssertionError('Incorrect bearing plane accepted')
    if hashes != {str(path): sha(path) for path in inputs}:
        raise RuntimeError('Contact test inputs changed')
    if classifier_sha != hashlib.sha256(inspect.getsource(_scorecard.pump_cap_contact).encode()).hexdigest():
        raise RuntimeError('Contact classifier changed')
    report = {'scope': 'Retained native placed pump and foam; injected invalid test geometry is scratch only.',
              'input_sha256': hashes, 'classifier_function_sha256': classifier_sha,
              'origin_mm': origin, 'cap_plane_z_mm': cap_z, 'cases': cases,
              'all_tests_pass': all(row['test_pass'] for row in cases),
              'physical_compression_qualified': False,
              'elapsed_seconds': time.monotonic()-started}
    output.write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=HERE/'cap-contact-check.json')
    args = parser.parse_args()
    run(args.pack, args.output)
