"""Three-piece cold-core casing in its native assembly frame.

The fixed shell floor is Z0. The bottom cap stands on Z−20 and the uniform top
lid presents its equipment face at Z233.4. The taller shell rim seats the lid
with its dry-face allowance. Vessel, reservoir, coil and port datums are fixed
independently of the casing rim. The separate B-fill bend holder belongs to the
populated cold-core assembly, not this casing-only assembly.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
_cold_core = _hw / "printed-parts" / "cold-core"
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_cold_core))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))

if __name__ == '__main__':
    import _rust_part
    _rust_part.start()


from _cold_core_interface import (
    cap_side_anchors,
    attachment_xy_positions,
    cap_shell_clearance,
    foam_cap_height,
    cap_anchors,
    cap_conduits,
    cap_conduit_floor_xy,
    cap_passive_guides,
    cap_cable_guides,
    cap_conduit_axis,
    cap_conduit_bore_radius,
    co2_inlet_tube_radius,
    screw_clearance_radius,
    deck_mount_xy,
    foam_shell_outer_height,
    head_pad_height,
)
from _foam_cap import cap_face_z, lid_total_height, stack_floor_z, top_cap_height
from _port_cuts import co2_inlet_xyz
import _internal_routes as routes
import _routing
import _materials as _mat
import _above_core_mounts as _above_mounts

# The one figure whoever seats this assembly needs: how far the cap face stands over the floor
# the stack is set down on. Both planes are `_foam_cap`'s, beside the lid whose faces they are.
cap_face_over_floor = cap_face_z - stack_floor_z

SHELL_STEP = _cold_core / "foam-shell" / "foam-shell.step"
CAP_DIR = _cold_core / "foam-cap"
RESERVOIR_DIR = _cold_core / "reservoir"
# Which reservoir STEP fills which pocket. `reservoir.py` builds both sides in the shell's
# own frame, so a body needs no placing; a cap seats on its body's top rim, which is the
# one figure this file carries about them.
RESERVOIRS = {"reservoir A": "reservoir-right", "reservoir B": "reservoir-left"}
RESERVOIR_CAP_Z = routes.reservoir_cap_z

# The three casing bodies' colours are `_materials`, which `foam_cap` and `foam_shell` bake into
# each piece's own STEP and `cold_core_assembly` places them with.
SHELL_COLOR = _mat.C_FOAM_SHELL
COLORS = {
    "foam-cap-lid-top": _mat.C_CAP_LID_TOP,
    "foam-cap-bottom": _mat.C_CAP_BOTTOM,
}

# The spool each potted route is cut off, in `_routing.SPOOLS`' own keys — the same six rolls
# the enclosure's runs come off, and every one of these lines butts an enclosure run at the
# conduit it leaves the stack by.
ROUTE_SPOOLS = {
    "water-in": "white",
    "carb-water-out": "blue",
    "co2-in": "red",
    "prv-vent": "black",
    "reservoir-a": "black",
    "reservoir-a-fill": "black",
    "reservoir-b": "black",
    "reservoir-b-fill": "black",
}
ROUTE_COLORS = {name: _routing.color(key) for name, key in ROUTE_SPOOLS.items()}


def spin_xy(p):
    """A cap-frame `(x, y)` at the top cap's install orientation — the half turn `_spin`
    gives the metal, given to a coordinate."""
    return (-p[0], -p[1])


def cap_conduit_station(name):
    """One cap conduit's mouth in the ASSEMBLY'S OWN frame: `(x, y)`.

    The bore is authored in the CAP's frame and the cap installs spun, so this is where a
    line crossing the stack's top face actually comes out."""
    return spin_xy(cap_conduits[name])


def cap_conduit_axis_out():
    """The way out of a cap conduit, in the assembly's frame — the top cap's +Z, which the
    spin about Z leaves alone."""
    return cap_conduit_axis


def cap_conduit_mouth(name):
    """Actual cap mouth and outward axis in the native core frame."""
    if name == 'reservoir-b-fill':
        passage = _above_mounts.reservoir_b_fill_passage()
        point = passage['entry_world_mm']
        mouth = routes.world_point_in_shell(point)
        outside = routes.world_point_in_shell(tuple(
            p+a for p,a in zip(point, passage['outward_axis_world'])))
        return mouth, tuple(b-a for a,b in zip(mouth,outside))
    x, y = cap_conduit_station(name)
    return (x, y, cap_face_z), cap_conduit_axis


def cap_anchor_station(name):
    """One chain anchor's seat centre in the ASSEMBLY'S OWN frame: `(x, y)`.

    The rib is authored in the CAP's frame and the cap installs spun, so this is where the seat
    a body lies in actually stands. Its height over the lid's outer face is
    `_cold_core_interface.cap_anchor_axis_over_face`, and the rib runs along the assembly's own
    ∓X — the spin carries the cap's +X onto it."""
    return spin_xy(cap_anchors[name].centre)


def cap_side_anchor_station(name):
    """One SIDEWAYS anchor's pipe axis in the ASSEMBLY'S OWN frame: `(x, y)`.

    The post is authored in the CAP's frame and the cap installs spun, so this is where the seat
    a run beds into actually stands. The pipe runs along the assembly's own ∓X and opens toward
    the assembly's own −Y, which the spin carries the cap's +X onto."""
    a = cap_side_anchors[name]
    return spin_xy((a.centre[0] + a.axis_off, a.centre[1]))


def deck_mount_station(name):
    """One deck mount's column tops in the ASSEMBLY'S OWN frame: a tuple of `(x, y)`.

    The columns are authored in the CAP's frame and the cap installs spun, so this is where
    a module's mount pattern actually lands on the stack. Both frames are centred on the
    stack's own axis, so the spin is the whole of the difference. What each module then
    stands at in Z is `_cold_core_interface.deck_mount_standoff`; whoever seats the
    assembly carries all of it."""
    return tuple(spin_xy(p) for p in deck_mount_xy(name))


def _report(placed, *, measurements):
    def bounds(name):
        from types import SimpleNamespace
        low, high = measurements['bounds'][name]
        return SimpleNamespace(xmin=low[0], ymin=low[1], zmin=low[2],
                               xmax=high[0], ymax=high[1], zmax=high[2],
                               xlen=high[0]-low[0], ylen=high[1]-low[1], zlen=high[2]-low[2])

    print("  part                  X range            Y range            Z range")
    for name, (shape, _c) in placed.items():
        b = bounds(name)
        print(
            "  %-19s [%7.1f,%7.1f]  [%7.1f,%7.1f]  [%7.1f,%7.1f]"
            % (name, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)
        )

    # Both closures land on the shell-native screw stations. The equipment
    # lid's authored pattern is the inverse of its installed half-turn pose.
    P = [(round(x, 6), round(y, 6)) for x, y in attachment_xy_positions]

    # The two planes the machine reads off this stack, held against the stack that came out.
    # The cap face is a LID FACE and not the box's top, so it is read as the top lid's own
    # plate rather than as whatever stands on it.
    floor = bounds("foam-cap-bottom").zmin
    face = bounds("foam-cap-lid-top").zmin + lid_total_height
    assert abs(floor - stack_floor_z) < 1e-6 and abs(face - cap_face_z) < 1e-6, (
        f"the stack stands on {floor:.4f} and presents its cap face at {face:.4f}, against the "
        f"{stack_floor_z:.4f} / {cap_face_z:.4f} this module tells the machine to expect")
    print("  cap face %.1f, %.1f mm over the stack's own floor — what stands on the core "
          "is placed off this, not off the box's top  OK" % (face, cap_face_over_floor))

    # The CO2's REACH IN — the last straight of its run, from the corner it takes out in the
    # open port lane to the collet made up under the bottom plate's lane-side port. The
    # collet takes the tube on the port's own axis, so this leg has to be straight and open:
    # a bend finished inside it is a tube that never bottoms. `report_routes` measures the
    # whole line; what is probed here is the one leg a fitting depends on.
    probe_r = co2_inlet_tube_radius - 0.3
    shell_solid = placed["foam-shell"][0]
    reading = measurements['co2']
    reach_xy = (*reading['start'][:2], *reading['end'][:2])
    reach_length, blocked = reading['length'], reading['blocked']
    print("  CO2 reach in: (%.2f, %.2f) .. (%.2f, %.2f) at z %.2f, %.1f mm straight — %s"
          % (*reach_xy, co2_inlet_xyz[2], reach_length,
             "clear  OK" if blocked <= 1e-6 else "** BLOCKED by %.3f mm^3" % blocked))

    # Read each actual passage, including the cable detours and B-fill's
    # side entry with its vertical reservoir outlet.
    probe_r = cap_conduit_bore_radius - 0.3
    for cname in cap_conduits:
        # The R14 B-fill channel uses the holder's D6.8 section rather than
        # the ordinary D7.5 vertical guide. Read its actual tube envelope.
        radius = routes.line_radius if cname == 'reservoir-b-fill' else probe_r
        reading = next(row for row in measurements['passages'] if row['name'] == cname)
        blocked = {row['name']: row['volume'] for row in reading['blocked']}
        bottom_open = reading['bottom_open']
        if bottom_open:
            print(f"  ** foam-cap-bottom is open on {cname}'s lower entry")
        for name, volume in blocked.items():
            if volume > 1e-6:
                print(f"  ** {name} blocks {cname}'s actual passage by {volume:.3f} mm^3")
        mouth, _axis = cap_conduit_mouth(cname)
        verdict = "clear  OK" if max(blocked.values()) <= 1e-6 else "** BLOCKED"
        print("  cap conduit %-16s mouth (%+7.2f,%+7.2f,%+7.2f): %s"
              % (cname,*mouth,verdict))

    # A thin vertical probe at each screw position must pass clear through both
    # parts of each stack — a real through-hole for every screw.
    probe_r = screw_clearance_radius - 0.3
    clear = True
    for name in ("foam-cap-lid-top", "foam-cap-bottom"):
        solid = placed[name][0]
        b = bounds(name)
        for x, y in P:
            blocked = next(row['blocked'] for row in measurements['screw_paths']
                           if row['name'] == name and tuple(row['xy']) == (x, y))
            if blocked > 1e-6:
                clear = False
                print("  ** screw path BLOCKED in %s at (%.1f, %.1f)" % (name, x, y))
    print(
        f"  screw paths: all {len(attachment_xy_positions)} clear through every "
        f"cap + lid (top + bottom)  OK"
        if clear
        else "  ** SCREW PATHS BLOCKED **"
    )

    # No two solids may share volume; mating faces touch at zero volume only.
    names = list(placed)
    clash = False
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = placed[names[i]][0], placed[names[j]][0]
            vol = (next(row['volume'] for row in measurements['clashes']
                        if row['a'] == names[i] and row['b'] == names[j]))
            if vol > 1e-3:
                clash = True
                print("  ** SOLID clash %s / %s = %.2f mm^3" % (names[i], names[j], vol))
    print("  no solid collisions" if not clash else "  ** CLASHES PRESENT **")


def rust_main(output=None):
    """Write the casing and installed routes from their authoritative fine models."""
    import _rust_part
    import foam_numbers
    output = Path(output) if output is not None else _here.parent
    output.mkdir(parents=True, exist_ok=True)
    numbers = foam_numbers.numbers()
    result = _rust_part.cut('cold-core', 'foam-assembly', numbers, output)
    casing = [row for row in result['bodies'] if row['name'] in COLORS or row['name'] == 'foam-shell']
    measurements = casing[0]['assembly_report']
    measurements['bounds'] = {row['name']: (row['min'], row['max']) for row in casing}
    _report({row['name']: (None, None) for row in casing}, measurements=measurements)
    routes_reading = next(row['route_report'] for row in result['bodies'] if 'route_report' in row)
    fitted = {row['name']: (row['bend'], None) for row in routes_reading['routes']}
    obstacles = {row['name']: None for row in routes_reading['routes'][0]['blocked']}
    routes.report_routes(fitted, obstacles, measurements=routes_reading)
    sys.path.insert(0, str(_hw / 'cold-core-layout'))
    from _core_presentation import finish
    finish(output / 'foam-assembly.step', numbers['models'])
    return result


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='directory for generated assembly files')
    args = parser.parse_args(argv)
    rust_main(args.output)


if __name__ == "__main__":
    main()
