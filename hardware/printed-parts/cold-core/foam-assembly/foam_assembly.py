"""Three-piece cold-core casing in its native assembly frame.

The fixed shell floor is Z0. The bottom cap stands on Z−20 and the uniform top
lid presents its equipment face at Z233.4. The taller shell rim seats the lid
with its dry-face allowance. Vessel, reservoir, coil and port datums are fixed
independently of the casing rim. The separate B-fill bend holder belongs to the
populated cold-core assembly, not this casing-only assembly.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
_cold_core = _hw / "printed-parts" / "cold-core"
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_cold_core))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly, import_step
from _foam_shell import import_shell
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
from _foam_cap import cap_face_z, import_cap_part, lid_total_height, stack_floor_z, top_cap_height
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


def _load(path):
    if Path(path) == SHELL_STEP:
        return import_shell(path)
    if Path(path).parent == CAP_DIR:
        return import_cap_part(path)
    if Path(path).parent == RESERVOIR_DIR:
        import reservoir
        return reservoir.import_part(path)
    return import_step(str(path)).val()


def _spin(shape):
    """Rotate 180° about the Z axis — the top cap's install orientation,
    which carries its deck-mount stations to the deck positions they hold."""
    return shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180)


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


def cap_passage_probe(name, radius):
    """The existing cap-opening report's probe, following its actual passage."""
    if name in cap_cable_guides:
        route = _above_mounts.cable_guide_points(name)
        points = [routes.world_point_in_shell(p) for p in route['points_mm']]
        return routes.build_route(points, route['bend_radius_mm'], radius)
    if name in cap_passive_guides or name in ('water-in', 'carb-water-out', 'reservoir-b-fill'):
        return routes.build_route(routes.routes[name], routes.route_bend_radius, radius)
    x,y = cap_conduit_station(name)
    return cq.Solid.makeCylinder(radius,cap_face_z-foam_shell_outer_height+2.,
        cq.Vector(x,y,foam_shell_outer_height-1.))


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


def _place_z(shape, *, zmin=None, zmax=None):
    """Translate along Z only (parts are already XY-centered and correctly
    oriented). Sets either the min-Z or max-Z face to a target."""
    bb = shape.BoundingBox()
    if zmin is not None:
        dz = zmin - bb.zmin
    elif zmax is not None:
        dz = zmax - bb.zmax
    else:
        dz = 0.0
    return shape.translate((0, 0, dz))


def build():
    """Three printed pieces in the core's fixed assembly frame."""
    shell = _load(SHELL_STEP)
    lid_top = _spin(_load(CAP_DIR/'foam-cap-lid-top.step')).translate(
        (0.,0.,cap_face_z-lid_total_height))
    cap_bottom = _load(CAP_DIR/'foam-cap-bottom.step').translate((0.,0.,stack_floor_z))
    placed = {
        'foam-shell':(shell,SHELL_COLOR),
        'foam-cap-lid-top':(lid_top,COLORS['foam-cap-lid-top']),
        'foam-cap-bottom':(cap_bottom,COLORS['foam-cap-bottom']),
    }
    assy = cq.Assembly(name='foam-assembly')
    for name,(shape,color) in placed.items():assy.add(shape,name=name,color=color)
    return assy,placed


def _report(placed):
    print("  part                  X range            Y range            Z range")
    for name, (shape, _c) in placed.items():
        b = shape.BoundingBox()
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
    floor = placed["foam-cap-bottom"][0].BoundingBox().zmin
    face = placed["foam-cap-lid-top"][0].BoundingBox().zmin + lid_total_height
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
    start, end = routes.route_legs(routes.routes["co2-in"])[-1]
    reach = end - start
    probe = cq.Solid.makeCylinder(probe_r, reach.Length, start, reach.normalized())
    blocked = shell_solid.intersect(probe).Volume()
    print("  CO2 reach in: (%.2f, %.2f) .. (%.2f, %.2f) at z %.2f, %.1f mm straight — %s"
          % (start.x, start.y, end.x, end.y, co2_inlet_xyz[2], reach.Length,
             "clear  OK" if blocked <= 1e-6 else "** BLOCKED by %.3f mm^3" % blocked))

    # Read each actual passage, including the cable detours and B-fill's
    # side entry with its vertical reservoir outlet.
    probe_r = cap_conduit_bore_radius - 0.3
    for cname in cap_conduits:
        # The R14 B-fill channel uses the holder's D6.8 section rather than
        # the ordinary D7.5 vertical guide. Read its actual tube envelope.
        radius = routes.line_radius if cname == 'reservoir-b-fill' else probe_r
        probe = cap_passage_probe(cname, radius)
        blocked = {name: placed[name][0].intersect(probe).Volume()
                   for name in ("foam-shell", "foam-cap-lid-top")}
        lower_x, lower_y = spin_xy(cap_conduit_floor_xy[cname])
        for name in ("foam-cap-bottom",):
            solid = placed[name][0]
            b = solid.BoundingBox()
            lower = cq.Solid.makeCylinder(probe_r,b.zlen+4.,
                cq.Vector(lower_x,lower_y,b.zmin-2.))
            if solid.intersect(lower).Volume() <= 1e-6:
                print(f"  ** {name} is open on {cname}'s lower entry")
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
        b = solid.BoundingBox()
        for x, y in P:
            probe = cq.Solid.makeCylinder(
                probe_r, b.zlen + 4, cq.Vector(x, y, b.zmin - 2), cq.Vector(0, 0, 1)
            )
            if solid.intersect(probe).Volume() > 1e-6:
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
            vol = a.intersect(b).Volume()
            if vol > 1e-3:
                clash = True
                print("  ** SOLID clash %s / %s = %.2f mm^3" % (names[i], names[j], vol))
    print("  no solid collisions" if not clash else "  ** CLASHES PRESENT **")


def installed_internal_route(name, shape):
    """The installed line, with the PRV vent cut flush to the shell's +Y flank."""
    if name != "prv-vent":
        return shape
    b = shape.BoundingBox()
    keep = cq.Solid.makeBox(
        b.xlen + 2.0, routes.prv_vent_flank_y - b.ymin + 1.0, b.zlen + 2.0,
        cq.Vector(b.xmin - 1.0, b.ymin - 1.0, b.zmin - 1.0))
    return shape.intersect(keep)


def build_internal_routes(placed):
    """Every fluid line inside the core, drawn at the arc its own corridor leaves.

    The obstacles are what a line actually runs among down there: the shell, the carbonator with
    its wrapped coil, and both reservoirs with their caps. The reservoirs are not in the
    foam assembly — they are dropped into its pockets — but a line that crosses a pocket
    crosses them, so they are here."""
    obstacles = {"the foam shell": placed["foam-shell"][0], "the carbonator": routes.carbonator_envelope()}
    for name, stem in RESERVOIRS.items():
        obstacles[name] = _load(RESERVOIR_DIR / f"{stem}.step")
        cap = _load(RESERVOIR_DIR / f"{stem.replace('reservoir', 'reservoir-cap')}.step")
        obstacles[f"{name}'s cap"] = cap.translate((0, 0, RESERVOIR_CAP_Z))
    fitted = routes.build_routes(obstacles)
    routes.report_routes(fitted, obstacles)
    assy = cq.Assembly(name="internal-routes")
    for name in sorted(fitted):
        assy.add(installed_internal_route(name, fitted[name][1]),
                 name=name, color=ROUTE_COLORS[name])
    return assy


def main():
    assy, placed = build()
    out = _here.parent / "foam-assembly.step"
    export_assembly(assy, str(out))
    # AND THE FLUTED SURFACES INTO THE PAYLOAD THE VIEWER READS. The shell and both caps carry a
    # show skin that is in the printed mesh and not in the solid (`cold-core/_show_skin.py`), so
    # the payload written beside this STEP holds three smooth prisms until they are put back.
    # `loadStepFile` prefers that payload to the STEP, so this is what /3d draws.
    #
    # IMPORTED HERE AND NOT AT THE TOP, the way `enclosure_assembly` does it: `flute_payload`
    # pulls in a decimator and a proximity index that only the run which cuts an assembly uses.
    #
    # AND ASKED FOR THE CORE'S TREE, not the disk. This assembly holds cold-core bodies and no
    # others, so the box's six fluted pieces are surfaces it can never graft — and indexing them
    # makes this wait on the enclosure, which the box is built from and the box stands on this.
    import flute_payload                                                # noqa: E402
    _grafted = flute_payload.graft(Path(str(out) + ".mesh"),
                                   flute_payload.surfaces(flute_payload.COLD_CORE_DIRS))
    if _grafted:
        print(f"-> {Path(str(out)).name}.mesh  ({_grafted} fluted piece(s))")
    print("-> foam-assembly.step")
    _report(placed)

    export_assembly(build_internal_routes(placed), str(_here.parent / "internal-routes.step"))
    print("-> internal-routes.step")


if __name__ == "__main__":
    main()
