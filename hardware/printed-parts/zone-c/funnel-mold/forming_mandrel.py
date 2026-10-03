"""Removable PETG tool forming the funnel's complete staged outlet bore.

The print axis is Z and the socket pilot's end is the bed datum. The finished
reference is the coated, measured tool; the print has a separate 0.05 mm normal
finishing reserve. The dry registration shank and first millimetre of the socket
pilot remain bare at 6.35 mm. Neither mould shell changes for this tool.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCP.BRepOffset import BRepOffset_Mode
from OCP.GeomAbs import GeomAbs_Arc
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p/'hardware/scripts/_cadq_export.py').is_file())
sys.path[:0] = [str(ROOT/'hardware/printed-parts/zone-c/funnel'),
                str(ROOT/'hardware/scripts')]
import funnel
from _cadq_export import export_assembly, import_step
from _materials import M_PETG_TRANSLUCENT, one_body
from flute_payload import cut as write_print_payload

length = 50.8
dry_shank_diameter = 6.35
socket_end_depth = 1.5
finishing_reserve = 0.05
socket_bare_length = 1.0
dry_bare_start_from_neck = 3.0
lateral_allowance = 0.5
tilt_allowance = 1.0
axial_allowance = 0.1
tolerance = 0.0001
# Fine layers include the entry shoulder, tiny relief and complete sealing land.
fine_band = (0.72, 7.12)
pilot_alignment_band = (0.72, 0.85)
pilot_alignment_layer_height = 0.14


def stations():
    """Axial stations in the funnel's frame, without building the bowl loft."""
    end = -funnel.drop+funnel.plug_lift
    neck = funnel.brim_thickness-funnel.chute_h-funnel._ramp_rise
    land_top = neck-funnel.neck_blend_drop
    return {'end': end, 'neck': neck, 'land_top': land_top,
            'land_bottom': land_top-funnel.sealing_land,
            'lead_top': end+funnel.bore_lead_height,
            'bottom': end-socket_end_depth,
            'top': end-socket_end_depth+length}


def cylinder(diameter, bottom, top):
    assert top > bottom
    return cq.Solid.makeCylinder(diameter/2, top-bottom, cq.Vector(0, 0, bottom))


def slab(bottom, top):
    return (cq.Workplane('XY').box(40, 40, top-bottom,
            centered=(True, True, False)).translate((0, 0, bottom)).val())


def one(shape):
    cleaned = shape.clean()
    if cleaned.isValid():
        shape = cleaned
    assert shape.isValid() and len(shape.Solids()) == 1
    return shape.Solids()[0]


def finished_local():
    """The exact wet profile and unchanged dry interfaces, on a centred axis."""
    z = stations()
    assert z['lead_top'] < z['land_bottom']
    shaft = cylinder(dry_shank_diameter, z['land_top'], z['top'])
    land = cylinder(funnel.sealing_id, z['land_bottom'], z['land_top']+0.01)
    relief = cylinder(funnel.bore_relief_id, z['lead_top'], z['land_bottom'])
    lead = cq.Solid.makeCone(funnel.bore_lead_id/2, funnel.bore_relief_id/2,
                            funnel.bore_lead_height, cq.Vector(0, 0, z['end']))
    # This 0.01 mm through overlap is also in the funnel's native bore.
    mouth = cylinder(funnel.bore_lead_id, z['end']-0.01, z['end']+0.01)
    pilot = cylinder(dry_shank_diameter, z['bottom'], z['end'])
    return one(shaft.fuse(land, relief, lead, mouth, pilot))


def raw_local():
    """Normal finishing reserve, with the two uncoated locating zones restored."""
    reference = finished_local()
    offset = BRepOffsetAPI_MakeOffsetShape()
    offset.PerformByJoin(reference.wrapped, -finishing_reserve, 1e-6,
                         BRepOffset_Mode.BRepOffset_Skin,
                         True, False, GeomAbs_Arc, False)
    assert offset.IsDone() and not offset.Shape().IsNull()
    raw = cq.Shape.cast(offset.Shape())
    if not raw.Solids() and len(raw.Shells()) == 1:
        raw = cq.Solid.makeSolid(raw.Shells()[0])
    z = stations()
    bare_pilot = reference.intersect(slab(z['bottom'], z['bottom']+socket_bare_length))
    bare_shank = reference.intersect(slab(z['neck']+dry_bare_start_from_neck, z['top']))
    raw = one(raw.fuse(bare_pilot, bare_shank))
    assert raw.cut(reference).Volume() < tolerance
    assert abs(raw.BoundingBox().zlen-length) < tolerance
    return raw


def finished_funnel_frame():
    return finished_local().translate((funnel.neck_dx, funnel.neck_dy, 0))


def raw_print_frame():
    return raw_local().translate((0, 0, -stations()['bottom']))


def cylindrical_faces(shape):
    """The actual native cylinder stations, including the finishing transitions."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    rows = []
    for face in shape.Faces():
        if face.geomType() != 'CYLINDER':
            continue
        cylinder_face = BRepAdaptor_Surface(face.wrapped).Cylinder()
        # STEP uncertainty expands BoundingBox; vertices give the actual axial
        # trim stations of these complete cylindrical faces.
        values = [vertex.Center().z for vertex in face.Vertices()]
        bottom, top = min(values), max(values)
        rows.append({'diameter_mm': 2*cylinder_face.Radius(),
                     'z_mm': [bottom, top], 'length_mm': top-bottom})
    return sorted(rows, key=lambda row: row['z_mm'][0])


def load_screen():
    """Static equalized-head sizing only; release and creep are unqualified."""
    z = stations()
    head = funnel.brim_thickness+5-z['end']
    pressure = 1130*9.81*(head/1000)/1000  # kPa
    unsupported = z['neck']+10-z['bottom']
    diameter = funnel.sealing_id-2*finishing_reserve
    inertia = math.pi*diameter**4/64
    distributed = pressure/1000*funnel.bore_lead_id  # N/mm
    modulus = 1000.0
    return {'model': 'cantilever with full maximum head applied laterally along its unsupported length',
            'head_pressure_kpa': pressure, 'unsupported_length_mm': unsupported,
            'minimum_solid_diameter_mm': diameter, 'assumed_modulus_mpa': modulus,
            'lateral_force_n': distributed*unsupported,
            'tip_deflection_mm': distributed*unsupported**4/(8*modulus*inertia),
            'maximum_bending_stress_mpa': distributed*unsupported**2/2*(diameter/2)/inertia,
            'maximum_axial_head_force_n': pressure/1000*math.pi*(funnel.bore_lead_id/2)**2,
            'scope': 'Room-temperature equalized-pressure static screening; not release-force, creep, lifetime or sealed-vacuum qualification.'}


def metadata(raw=None, reference=None):
    raw = raw_print_frame() if raw is None else raw
    reference = finished_local().translate((0, 0, -stations()['bottom'])) if reference is None else reference
    z = stations()
    return {
        'material': 'PETG Translucent with a separately measured finishing stack',
        'print_frame': 'socket pilot end at Z0, axis X0 Y0, shank upright',
        'print_to_funnel_translation_mm': [funnel.neck_dx, funnel.neck_dy, z['bottom']],
        'length_mm': length,
        'dry_shank_diameter_mm': dry_shank_diameter,
        'socket_end_depth_mm': socket_end_depth,
        'normal_finishing_reserve_mm': finishing_reserve,
        'uncoated_print_z_mm': [[0, socket_bare_length],
                              [z['neck']+dry_bare_start_from_neck-z['bottom'], length]],
        'wet_forming_print_z_mm': [socket_end_depth, z['neck']-z['bottom']],
        'recommended_fine_band_print_z_mm': list(fine_band),
        'recommended_fine_layer_height_mm': 0.08,
        'recommended_pilot_alignment_layer': {
            'print_z_range_mm': list(pilot_alignment_band),
            'layer_height_mm': pilot_alignment_layer_height,
            'scope': 'One local phase-alignment layer on the dry pilot, followed by 0.08 mm layers through the wet band. Keep the saved 0.20 mm bed layer and global PETG settings.'},
        'finished_profile': {
            'entry_diameter_mm': funnel.bore_lead_id,
            'lead_height_mm': funnel.bore_lead_height,
            'relief_diameter_mm': funnel.bore_relief_id,
            'relief_print_z_mm': [z['lead_top']-z['bottom'], z['land_bottom']-z['bottom']],
            'relief_height_mm': z['land_bottom']-z['lead_top'],
            'land_diameter_mm': funnel.sealing_id,
            'land_print_z_mm': [z['land_bottom']-z['bottom'], z['land_top']-z['bottom']],
            'land_height_mm': funnel.sealing_land,
            'throat_diameter_mm': funnel.spout_id},
        'raw_cylindrical_faces': cylindrical_faces(raw),
        'finished_cylindrical_faces': cylindrical_faces(reference),
        'positioning_allowance': {'lateral_mm': lateral_allowance,
                                  'tilt_deg': tilt_allowance, 'axial_each_way_mm': axial_allowance,
                                  'poses': 72,
                                  'scope': 'Tool-specific combined positioning screen against the unchanged cavity; nominal finished wet profile still requires measured alignment.'},
        'load_screen': load_screen(),
        'demould': {
            'direction_in_funnel_frame': '-Z after both shells are removed',
            'trim_before_withdrawal': 'Remove the sacrificial socket collar flush with the block bottom before pulling the 8.4 mm entry through it.',
            'maximum_shank_diameter_through_land_mm': dry_shank_diameter,
            'land_diameter_mm': funnel.sealing_id,
            'required_land_diametric_expansion_percent': 100*(dry_shank_diameter/funnel.sealing_id-1),
            'scope': 'Silicone-assisted withdrawal; native rigid-body interference is intentional. Release force, coating adhesion, cure compatibility and casting quality are untested.'},
        'finishing_check': {
            'method': 'Mask the recorded bare zones. Finish a same-stack witness, measure net growth, and measure the finished tool against the finished reference before casting.',
            'reference': 'forming-mandrel-finished.step',
            'criterion': 'The finished wet profile must retain the 8.4 mm entry, 6.7 mm relief, 6.0 mm by 3.0 mm land and 6.35 mm throat. Finishing may not erase the relief or add a ridge at the land transitions.',
            'qualification': 'Printed geometry and reserve only; a coating thickness assumption is not a measured finished tool.'},
        'status': 'Native geometry checked separately; printed fit, finishing, release and casting remain physical checks.'}


def export(output):
    output.mkdir(parents=True, exist_ok=True)
    raw = raw_print_frame()
    reference = finished_local().translate((0, 0, -stations()['bottom']))
    step = output/'forming-mandrel.step'
    stl = output/'forming-mandrel.stl'
    export_assembly(one_body(cq.Workplane(obj=raw), 'forming-mandrel', M_PETG_TRANSLUCENT),
                    str(step), precision_mode=1)
    export_assembly(one_body(cq.Workplane(obj=reference), 'forming-mandrel-finished', M_PETG_TRANSLUCENT),
                    str(output/'forming-mandrel-finished.step'), precision_mode=1)
    native = import_step(str(step)).val()
    assert native.isValid() and len(native.Solids()) == 1
    native.exportStl(str(stl), tolerance=0.005, angularTolerance=0.05, relative=False)
    mesh = trimesh.load(stl, force='mesh', process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
    mesh.export(stl)
    write_print_payload(step, stl)
    info = metadata(native, import_step(str(output/'forming-mandrel-finished.step')).val())
    info['sha256'] = {name: hashlib.sha256((output/name).read_bytes()).hexdigest()
                      for name in ('forming-mandrel.step', 'forming-mandrel.stl',
                                   'forming-mandrel-finished.step')}
    info['mesh'] = {'triangles': len(mesh.faces), 'watertight': True,
                    'winding_consistent': True, 'bodies': 1}
    (output/'forming-mandrel-design.json').write_text(json.dumps(info, indent=2)+'\n')
    print(json.dumps({'sha256': info['sha256'], 'mesh': info['mesh'],
                      'finished_profile': info['finished_profile'],
                      'raw_cylindrical_faces': info['raw_cylindrical_faces']}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    export(parser.parse_args().output)


if __name__ == "__main__":
    main()
