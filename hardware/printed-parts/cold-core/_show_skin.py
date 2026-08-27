"""The cold core's show surfaces, in the triangles a printer reads.

WHY IT IS NOT IN THE SOLID. The fade that stops the flutes is a FIELD OVER THE SURFACE — how
far a station stands from the nearest place the show face ends — and a boundary-representation
prism cannot carry one. It would have to follow a port's rim, a lane slot's jamb, a boss web's
arris and the piece's own top edge with one rule, and every attempt costs a separate mechanism
per edge. Measured over the surface they are all one fact and there is nothing to enumerate.
So the STEP beside a piece is a smooth prism, and the STL is the fluted surface.
`cadlib/flute_skin.py` is the field; this is the core's own way in to it.

ONE RUN, AND EVERY PIECE OF THE STACK STANDS ON IT. The shell, both caps and both lids are cut
to the SAME footprint, so from the outside the core is one silhouette with seams across it.
`_cold_core_interface.outer_shell_plan_at` is that silhouette and every piece strikes its field
on the same arc length, which is why a groove crossing a seam does not step.

WHAT A PIECE IS NOT TOLD is where its own openings are. The field asks, at every station,
whether the piece has material at the nominal surface — and where it does not, that is an edge,
whatever made it. A port bore, a lane slot, an insert pocket, a boss web's shoulder, the top
and bottom faces a cap lands on: one question, one answer, one ramp.
"""

import sys
from pathlib import Path

import trimesh

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
import flute_skin                                                        # noqa: E402

from _cold_core_interface import (                                       # noqa: E402
    flute_depth,
    flute_rise,
    flute_pitch,
    outer_shell_plan_at,
    outer_shell_plan_perimeter,
)

# HOW FINELY A PIECE IS TESSELLATED FOR THE BED. The show surface is fluted, so the mesh a
# slicer reads has to hold a curve the nozzle can draw: the deviation allowed is a fraction of
# the 0.42 mm bead, and the angle is tight enough that a groove's own arc does not come back as
# a few flats. It costs file size and nothing else — a slicer reads the triangles once.
mesh_tol = 0.02
mesh_angle = 0.15


def piece_mesh(solid):
    """One solid as the mesh that goes to a bed.

    TESSELLATED, NOT ROUND-TRIPPED THROUGH STL. An STL is a triangle soup with no shared
    vertices, and what comes back from re-merging one is a surface with edges that hold one
    face where they should hold two — which a mesh boolean rightly refuses to treat as a
    volume. `tessellate` hands back the indices directly."""
    solid = solid.val() if hasattr(solid, "val") else solid
    points, tris = solid.tessellate(mesh_tol, mesh_angle)
    mesh = trimesh.Trimesh(vertices=[(p.x, p.y, p.z) for p in points],
                           faces=tris, process=True)
    mesh.merge_vertices()
    return mesh


def outer_rail():
    """The one closed run the core's flutes are struck along.

    Nothing is berthed against it: what stands inside the shell is inside it, and the faces
    this run walks are the outside of the machine's own cold core."""
    return [flute_skin.Rail(at=outer_shell_plan_at,
                            length=outer_shell_plan_perimeter())]


def fluted(solid):
    """`solid` as the mesh a printer reads, with the core's show skin cut into it."""
    return flute_skin.flute(piece_mesh(solid), outer_rail(),
                            flute_pitch(), flute_depth, flute_rise)


def write_bed_file(solid, path):
    """`solid` fluted and written to `path`, and the reading taken off the FILE.

    WHAT IS CHECKED IS WHAT A SLICER REFUSES. `is_watertight` is the easier question and a mesh
    can pass it while Bambu Studio rejects the file outright, because winding can close over an
    edge that four faces share. `non_manifold_edges` asks the harder one, and it is asked of the
    bytes rather than of memory: everything before the write is in double precision and what
    goes to the bed is not."""
    path = Path(path)
    mesh = fluted(solid)
    mesh.export(str(path))
    written = trimesh.load_mesh(str(path))
    loose = flute_skin.non_manifold_edges(written)
    print(f"-> {path.name}  ({len(mesh.faces)} facets, "
          f"{'watertight' if written.is_watertight else 'NOT WATERTIGHT'})")
    if loose or not written.is_watertight:
        raise ValueError(
            f"{path.name}: a slicer refuses this — {loose} non-manifold edge(s), "
            f"watertight={written.is_watertight}, over {len(written.faces)} facets")
    return mesh
