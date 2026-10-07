"""Native screw passage, insert stock and complete bearing footprints.

The inspected shapes are imported from the study manifests. This binds actual
holes, ledges and hosts rather than treating nominal mounting datums as proof.
Manufacturer insert dimensions are recorded in mechanical-qualification/README.
"""
from pathlib import Path
import sys, json, hashlib, math
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.TopTools import TopTools_ListOfShape

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(STUDY / 'pump'))
import generate as G

TOL = 1e-5


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def circle_axes(shape, radius):
    axes = set()
    for edge in shape.Edges():
        if edge.geomType() != 'CIRCLE':
            continue
        circle = BRepAdaptor_Curve(edge.wrapped).Circle()
        if abs(circle.Radius() - radius) > 1e-5:
            continue
        if abs(circle.Axis().Direction().Z()) < .999999:
            continue
        p = circle.Location()
        axes.add((round(p.X(), 5), round(p.Y(), 5)))
    return sorted(axes)


def circular_face_levels(shape, radius):
    levels = []
    for edge in shape.Edges():
        if edge.geomType() != 'CIRCLE':
            continue
        circle = BRepAdaptor_Curve(edge.wrapped).Circle()
        if abs(circle.Radius() - radius) < 1e-5 and abs(circle.Axis().Direction().Z()) > .999999:
            levels.append(circle.Location().Z())
    return sorted(set(levels))


def cylinder(radius, length, point, axis=(0, 0, 1)):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*point), cq.Vector(*axis))


def annulus(inner, outer, length, point, axis=(0, 0, 1)):
    return cylinder(outer, length, point, axis).cut(cylinder(inner, length, point, axis))


def missing_volume(stock, witness):
    return abs(witness.cut(stock).Volume())


def material_volume(shape):
    return sum(abs(solid.Volume(tol=1e-9)) for solid in shape.Solids()) if shape else 0.


def material_operation(left, right, operation_type):
    """Complete material operation on independent copies of the full operands."""
    operation = operation_type()
    arguments, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
    arguments.Append(left.copy(mesh=False).wrapped)
    tools.Append(right.copy(mesh=False).wrapped)
    operation.SetArguments(arguments)
    operation.SetTools(tools)
    operation.SetFuzzyValue(.0001)
    operation.SetRunParallel(True)
    operation.Build()
    if not operation.IsDone() or (hasattr(operation, 'HasErrors') and operation.HasErrors()):
        raise ValueError('Meter stock material operation did not complete')
    if operation.Shape().IsNull():
        return None
    result = cq.Shape.cast(operation.Shape())
    if not result.isValid() or any(not solid.isValid() for solid in result.Solids()):
        raise ValueError('Invalid meter stock material operation result')
    return result


def complete_common(left, right):
    """Inspect every full Solid pair; no bounding-box or failed-Cut admission."""
    if not left or not right:
        return 0., []
    pairs, total = [], 0.
    for i, source in enumerate(left.Solids()):
        for j, target in enumerate(right.Solids()):
            result = material_operation(source, target, BRepAlgoAPI_Common)
            volume = material_volume(result)
            if volume > min(material_volume(source), material_volume(target)) + TOL:
                raise ValueError('Meter stock Common exceeds its full operand')
            pairs.append({'solid_indices': [i, j], 'completed': True, 'valid': True,
                          'result_solids': len(result.Solids()) if result else 0,
                          'tolerance_mm': .0001, 'common_mm3': volume})
            total += volume
    return total, pairs


def main():
    manifests = {folder: json.loads((STUDY / folder / 'candidate.json').read_text())
                 for folder in ['pump', 'structure', 'routing', 'mounts']}
    hatch_manifest = json.loads((HERE / 'roof-hatch.json').read_text())
    records = {}
    for folder in ['pump', 'routing', 'structure', 'mounts']:
        records.update(manifests[folder]['parts'])
    records.update(hatch_manifest['parts'])
    water5_manifest=json.loads((STUDY/'mounts/water5-hosts.json').read_text())
    records.update(water5_manifest['parts'])
    fluid_path=STUDY/'mounts/fluid-candidate.json'
    fluid_manifest=json.loads(fluid_path.read_text())
    records.update(fluid_manifest['parts'])
    tube_path=STUDY/'routing/tube-hosts.json'
    tube_manifest=json.loads(tube_path.read_text())if tube_path.exists()else{}
    records.update(tube_manifest.get('parts',{}))
    inputs = {}
    loaded = {}

    def load_record(name, rec):
        if name not in loaded:
            path = ROOT / rec['brep']
            actual_sha = sha(path)
            if isinstance(rec.get('sha256'), str) and rec['sha256'] != actual_sha:
                raise ValueError('Changed declared native input: ' + name)
            loaded[name] = cq.Shape.importBrep(str(path))
            inputs[name] = {'brep': rec['brep'], 'sha256': actual_sha}
        return loaded[name]

    def load(name):
        return load_record(name, records[name])

    checks = []
    stations = []

    def check(label, passed, **data):
        row = {'check': label, 'pass': bool(passed), **data}
        checks.append(row)
        print(('PASS ' if passed else 'FAIL ') + label, flush=True)

    print_path = HERE / 'print-parts.json'
    printed = json.loads(print_path.read_text())

    def load_print(name):
        rec = printed['parts'][name]
        path = ROOT / rec['brep']
        actual_sha = sha(path)
        if actual_sha != rec['sha256']:
            raise ValueError('Joined print has changed since its root audit: ' + name)
        shape = cq.Shape.importBrep(str(path))
        inputs['joined-print/' + name] = {'brep': rec['brep'], 'sha256': actual_sha}
        check(name + ' final joined print is one valid solid',
              shape.isValid() and len(shape.Solids()) == 1,
              valid=shape.isValid(), solids=len(shape.Solids()))
        return shape

    joined_lid = load_print('cold-core-lid')
    joined_roof = load_print('enclosure-back-top')
    joined_hatch = load_print('rear-roof-hatch')

    meter=json.loads((STUDY/'routing/candidate.json').read_text())['ports']['digiten-flow']
    mx,_,mz=meter['inlet']['pos']
    water5_tool=load_record('meter-bridge-clearance/tube-water-5',
                           manifests['pump']['clearance_cutters']['tube-water-5'])
    for index,band in enumerate(fluid_manifest['meter_fixed_collar_bands'],1):
        cy=sum(band)/2
        for side,(a,b) in enumerate([(cy-3.45,cy-1.75),(cy+1.75,cy+3.45)],1):
            # Water5's full R4.175 clearance removes the unused east crown
            # corner. Keep the complete rectangular-envelope diagnostic,
            # attribute every missing volume to that actual declared tool,
            # and require the remaining uninterrupted strip and both low
            # bearing walls to reach the unchanged positive roof coupon.
            upper=cq.Solid.makeBox(24.8,b-a,351.01-(mz+12.41),
                                  cq.Vector(mx-12.4,a,mz+12.41))
            source=load(f'meter-roof-seat-{index}')
            present,stock_pairs=complete_common(upper,joined_roof)
            source_present,source_pairs=complete_common(upper,source)
            missing_shape=material_operation(upper,joined_roof,BRepAlgoAPI_Cut)
            missing=material_volume(missing_shape)
            tool_present,tool_pairs=complete_common(missing_shape,water5_tool)
            conservation=abs(material_volume(upper)-present-missing)
            tool_error=abs(missing-tool_present)
            source_error=abs(material_volume(upper)-source_present)
            rectangular_diagnostic={
                'full_width_mm':24.8,'witness_volume_mm3':material_volume(upper),
                'full_stock_common_mm3':present,'intentional_water5_relief_mm3':missing,
                'complete_rectangle_retained':missing<TOL,
                'missing_bounds_mm':G.bounds(missing_shape) if missing_shape else None,
                'missing_solids':len(missing_shape.Solids()) if missing_shape else 0,
                'source_missing_mm3':source_error,'conservation_error_mm3':conservation,
                'missing_in_declared_water5_tool_mm3':tool_present,
                'missing_not_in_water5_tool_mm3':tool_error,
                'stock_commons':stock_pairs,'source_commons':source_pairs,
                'missing_tool_commons':tool_pairs,
                'witness_bounds_mm':[mx-12.4,a,mz+12.41,mx+12.4,b,351.01]}
            check(f'meter seat {index} web {side} rectangular crown has only declared Water5 relief',
                  max(conservation,tool_error,source_error)<TOL,
                  **rectangular_diagnostic)
            crown=cq.Solid.makeBox(24.05,b-a,351.01-(mz+12.41),
                                  cq.Vector(mx-12.4,a,mz+12.41))
            present,pairs=complete_common(crown,joined_roof)
            missing=abs(material_volume(crown)-present)
            check(f'meter seat {index} web {side} complete uninterrupted post-cut roof bridge',missing<TOL,
                  missing_mm3=missing,crown_strip_width_mm=24.05,axial_web_mm=b-a,
                  radial_bearing_wall_mm=3.,positive_roof_join_mm=.01,
                  witness_bounds_mm=[mx-12.4,a,mz+12.41,mx+11.65,b,351.01],
                  completed_valid_commons=pairs)
            for edge,x in [('west',mx-12.4),('east',mx+9.4)]:
                # The east tie-head pocket intentionally opens the lowest
                # 0.8mm of this wall. Witness the continuous bearing stock
                # above that pocket; the west wall has no such opening.
                bottom=mz+(1. if edge=='east' else .1)
                top=mz+9.1
                foot=cq.Solid.makeBox(3.,b-a,top-bottom,cq.Vector(x,a,bottom))
                present,pairs=complete_common(foot,joined_roof)
                missing=abs(material_volume(foot)-present)
                check(f'meter seat {index} web {side} {edge} complete bearing wall',missing<TOL,
                      missing_mm3=missing,radial_wall_mm=3.,axial_web_mm=b-a,
                      witness_bounds_mm=[x,a,bottom,x+3.,b,top],
                      tie_head_opening_below_mm=mz+.9 if edge=='east' else None,
                      completed_valid_commons=pairs)
            coupon_name=f'meter-root-coupon-{index}-'+('fore' if side==1 else 'aft')
            coupon=load_record(coupon_name,fluid_manifest['joined_root_coupons'][coupon_name])
            present,pairs=complete_common(coupon,joined_roof)
            missing=abs(material_volume(coupon)-present)
            check(coupon_name+' complete unchanged positive roof stock',missing<TOL,
                  missing_mm3=missing,witness_volume_mm3=material_volume(coupon),
                  witness_bounds_mm=G.bounds(coupon),completed_valid_commons=pairs)

    def split_key_stations(prefix,properties,stock):
        n=cq.Vector(*properties['normal']).normalized()
        u=cq.Vector(*properties['tube_axis']).normalized()
        v=n.cross(u).normalized()
        centre=cq.Vector(*properties.get('screw_datum_centre_mm',properties['centre_mm']))
        split=properties['split_local_mm']
        key_thickness=properties['key_thickness_mm']
        depth=properties['blind_pilot_depth_mm']
        cover=properties['closed_pilot_stock_mm']
        insert=properties['insert_length_mm']
        boss=properties.get('screw_boss_local_mm',properties['screw_side']*(properties['bore_radius_mm']+5.5))
        pitch=properties['screw_half_pitch_mm']
        key=load(properties.get('key_part',prefix+'-key'))
        axial_stations=properties.get('screw_axial_stations_mm',[-pitch,pitch])
        for index,axial_station in enumerate(axial_stations,1):
            label=prefix+' station '+str(index)
            mouth=centre+n*split+u*axial_station+v*boss
            pilot=cylinder(2,depth,mouth.toTuple(),n.toTuple())
            annular=annulus(2,3.6,depth,mouth.toTuple(),n.toTuple())
            cap=cylinder(2,cover,(mouth+n*depth).toTuple(),n.toTuple())
            pilot_common=G.overlap(stock,pilot)
            annular_missing=missing_volume(stock,annular)
            cap_missing=missing_volume(stock,cap)
            check(label+' full joined pilot, insert annulus and closed end',
                  pilot_common<TOL and annular_missing<TOL and cap_missing<TOL,
                  mouth_mm=mouth.toTuple(),axis=n.toTuple(),pilot_depth_mm=depth,
                  pilot_common_mm3=pilot_common,annular_missing_mm3=annular_missing,
                  cap_missing_mm3=cap_missing,minimum_annular_wall_mm=1.6,closed_end_mm=cover)
            screw=load(properties.get('screw_parts',[prefix+'-screw-1',prefix+'-screw-2'])[index-1])
            # These complete modeled heads/shafts have planar axial ends.
            # Native vertex projection gives their actual tip in any clock.
            tip=max(vertex.Center().dot(n) for vertex in screw.Vertices())
            engagement=tip-mouth.dot(n)
            reserve=depth-engagement
            common_stock=G.overlap(screw,stock)
            common_key=G.overlap(screw,key)
            check(label+' actual complete M3x8 shaft and tip reserve',
                  common_stock<TOL and common_key<TOL
                  and engagement>=insert-1e-6 and reserve>=.5-1e-6 and depth-insert>=1-1e-6,
                  stock_common_mm3=common_stock,key_common_mm3=common_key,
                  actual_engagement_mm=engagement,insert_length_mm=insert,
                  pilot_tip_reserve_mm=reserve,insert_blind_relief_mm=depth-insert)
            front=mouth-n*key_thickness
            bearing=annulus(1.6,2.75,.01,front.toTuple(),n.toTuple())
            missing=missing_volume(key,bearing)
            check(label+' complete native key head bearing',missing<TOL,
                  missing_mm3=missing,key_stock_mm=key_thickness,
                  key_hole_diameter_mm=3.2,head_bearing_outer_radius_mm=2.75)
            stations.append({'owner':prefix,'index':index,'mouth_mm':mouth.toTuple(),
                             'screw_length_mm':8,'actual_engagement_mm':engagement,
                             'tip_reserve_mm':reserve})

    split_key_stations('water5-east-drop',water5_manifest['split_seat_properties'],joined_roof)
    fastener_stations=set()
    for name,properties in tube_manifest.get('stations',{}).items():
        if 'blind_pilot_depth_mm'not in properties:continue
        prefix=properties.get('fastener_station',properties['part_prefix'])
        if prefix in fastener_stations:continue
        fastener_stations.add(prefix)
        owner=properties['print_owner']
        stock={'enclosure-back-top':joined_roof,'cold-core-lid':joined_lid}.get(owner)
        if stock is None:stock=load_print(owner)
        split_key_stations(prefix,properties,stock)

    owners = {'pcba': ('controller-roof-boss-', 'controller-screw-', 1.6),
              'psu': ('supply-lid-boss-', 'supply-screw-', 1.75)}
    for owner, (host_prefix, screw_prefix, hole_radius) in owners.items():
        component = load(owner)
        native_axes = circle_axes(component, hole_radius)
        mounts = [m for m in manifests['structure']['mounts'] if m['owner'] == owner]
        check(owner + ' four native site holes', len(native_axes) == len(mounts) == 4,
              hole_diameter_mm=2 * hole_radius, native_axes_mm=native_axes)
        for index, m in enumerate(mounts, 1):
            label = owner + ' station ' + str(index)
            x, y, z = m['mouth']
            axis = tuple(m['axis'])
            unit = cq.Vector(*axis)
            host = load(host_prefix + str(index))
            screw = load(screw_prefix + str(index))
            pilot = cylinder(2, m['pilot_depth'], m['mouth'], axis)
            minimum_stock = annulus(2, 3.6, m['pilot_depth'], m['mouth'], axis)
            host_stock = joined_lid if owner == 'psu' else joined_roof
            stock_missing = missing_volume(host_stock, minimum_stock)
            pilot_common = G.overlap(host_stock, pilot)
            check(label + ' native hole and screw axis agree',
                  (round(x, 5), round(y, 5)) in native_axes,
                  mouth_mm=m['mouth'], hole_radius_mm=hole_radius)
            common = G.overlap(screw, component)
            check(label + ' complete screw passes populated component', common < TOL,
                  common_mm3=common, shank_diameter_mm=3, radial_hole_air_mm=hole_radius - 1.5)
            check(label + ' full-depth open pilot', pilot_common < TOL,
                  common_mm3=pilot_common, pilot_depth_mm=m['pilot_depth'])
            check(label + ' complete minimum insert annulus', stock_missing < TOL,
                  missing_mm3=stock_missing, bore_diameter_mm=4,
                  minimum_surrounding_wall_mm=1.6, nominal_host_diameter_mm=8)
            closed_start = (cq.Vector(x, y, z) + unit * m['pilot_depth']).toTuple()
            cover = m.get('end_cover', m.get('root_cover'))
            cover_witness = cylinder(2, cover, closed_start, axis)
            cap_missing = missing_volume(host_stock, cover_witness)
            check(label + ' complete native blind end', cap_missing < TOL,
                  missing_mm3=cap_missing, closed_cover_mm=cover)
            box = screw.BoundingBox()
            tip_z = box.zmax if axis[2] > 0 else box.zmin
            engagement = (tip_z - z) * axis[2]
            reserve = m['pilot_depth'] - engagement
            check(label + ' actual screw tip, insert and blind relief',
                  engagement >= m['insert_length'] - 1e-6 and reserve >= .5 - 1e-6
                  and m['pilot_depth'] - m['insert_length'] >= 1 - 1e-6,
                  actual_tip_z_mm=tip_z, engagement_mm=engagement,
                  insert_length_mm=m['insert_length'], tip_reserve_mm=reserve,
                  insert_blind_relief_mm=m['pilot_depth'] - m['insert_length'])
            bearing_z = min(circular_face_levels(component, hole_radius)) if owner == 'pcba' else component.BoundingBox().zmin + 6.7
            bearing_radius = 2.75 if owner == 'pcba' else 3.5
            # Ten microns within the actual reference bearing material.
            witness_z = bearing_z if owner == 'pcba' else bearing_z - .01
            bearing = annulus(hole_radius, bearing_radius, .01, (x, y, witness_z))
            bearing_missing = missing_volume(component, bearing)
            check(label + ' complete native bearing footprint', bearing_missing < TOL,
                  missing_mm3=bearing_missing, bearing_plane_z_mm=bearing_z,
                  bearing_outer_radius_mm=bearing_radius,
                  imported_board_plane_offset_mm=bearing_z - 347.4 if owner == 'pcba' else 0)
            if owner == 'psu':
                washer = load('supply-washer-' + str(index))
                washer_common = G.overlap(screw, washer)
                washer_seat = washer.distance(component)
                washer_component_common = G.overlap(washer, component)
                check(label + ' washer passage and seated ledge',
                      washer_common < TOL and washer_seat < 1e-6 and washer_component_common < TOL,
                      screw_washer_common_mm3=washer_common,
                      washer_component_common_mm3=washer_component_common,
                      washer_ledge_gap_mm=washer_seat,
                      ledge_stock_mm=6.7, washer_stock_mm=.8,
                      washer_bore_mm=3.2, washer_radial_shank_air_mm=.1)
            stations.append({'owner': owner, 'index': index,
                             'native_hole_xy_mm': [x, y], 'mouth_mm': m['mouth'],
                             'screw_length_mm': m['screw_length'],
                             'actual_engagement_mm': engagement, 'tip_reserve_mm': reserve})

    for m in fluid_manifest.get('mounts',[]):
        if m['owner']!='asse-removable-carrier':continue
        index=m['index'];label='ASSE carrier station '+str(index)
        mouth=cq.Vector(*m['mouth']);axis=cq.Vector(*m['axis'])
        depth=m['pilot_depth'];cover=m['root_cover'];insert=m['insert_length']
        pilot=cylinder(2,depth,mouth.toTuple(),axis.toTuple())
        stock=annulus(2,3.6,depth,mouth.toTuple(),axis.toTuple())
        cap=cylinder(2,cover,(mouth+axis*depth).toTuple(),axis.toTuple())
        pilot_common=G.overlap(joined_roof,pilot)
        stock_missing=missing_volume(joined_roof,stock)
        cap_missing=missing_volume(joined_roof,cap)
        check(label+' complete joined pilot, minimum annulus and blind end',
              pilot_common<TOL and stock_missing<TOL and cap_missing<TOL,
              pilot_common_mm3=pilot_common,annular_missing_mm3=stock_missing,
              closed_end_missing_mm3=cap_missing,blind_pilot_depth_mm=depth,
              minimum_annular_wall_mm=1.6,closed_end_stock_mm=cover)
        screw=load('asse-carrier-screw-'+str(index))
        clamp=load('asse-carrier-clamp-'+str(index))
        common_roof=G.overlap(screw,joined_roof);common_clamp=G.overlap(screw,clamp)
        tip=max(vertex.Center().dot(axis)for vertex in screw.Vertices())
        engagement=tip-mouth.dot(axis);reserve=depth-engagement
        check(label+' actual complete M3x12 passage and short-insert reserve',
              common_roof<TOL and common_clamp<TOL and engagement>=insert-1e-6
              and reserve>=.5-1e-6 and depth-insert>=1-1e-6,
              joined_roof_common_mm3=common_roof,clamp_common_mm3=common_clamp,
              actual_engagement_mm=engagement,insert_length_mm=insert,
              pilot_tip_reserve_mm=reserve,blind_relief_mm=depth-insert)
        p=cq.Vector(mouth.x,m['head_bearing_y_mm'],mouth.z)
        bearing=annulus(1.65,2.75,.01,p.toTuple(),axis.toTuple())
        bearing_missing=missing_volume(clamp,bearing)
        check(label+' complete clamp head bearing footprint',bearing_missing<TOL,
              missing_mm3=bearing_missing,head_bearing_y_mm=p.y,
              clamp_bearing_stock_mm=m['clamp_bearing_stock_mm'])
        stations.append({'owner':'asse-removable-carrier','index':index,
                         'mouth_mm':m['mouth'],'screw_length_mm':m['screw_length'],
                         'actual_engagement_mm':engagement,'tip_reserve_mm':reserve})

    sys.path.insert(0, str(ROOT / 'hardware/reference/ground-ring-stack'))
    import ground_ring_stack as ground
    ground_mount = next(m for m in manifests['structure']['mounts'] if m['owner'] == 'ground-stack')
    datum = tuple(ground_mount['mouth'])
    gx, gy, gz = datum
    screw_length = ground_mount['screw_length']
    pilot_depth = ground_mount['pilot_depth']
    insert_length = ground_mount['insert_length']
    end_cover = ground_mount['end_cover']
    head_seat_z = gz - 4.8
    tip_z = head_seat_z + screw_length
    engagement = tip_z - gz
    tip_reserve = pilot_depth - engagement
    clock=ground_mount.get('clock_degrees',0.)
    turn = lambda s: s.rotate((0, 0, 0), (1, 0, 0), 180).rotate(
        (0,0,0),(0,0,1),clock).translate(datum)
    rings = [turn(ground._ring(i * .8, i * 60).val()) for i in range(5)]
    washer = turn(annulus(1.6, 3.5, .8, (0, 0, 4)))
    # Reference display used an enlarged fusion shank; the study has the actual
    # 3mm nominal screw. Separate native ring solids allow passage measurement.
    shaft = cylinder(1.5, screw_length, (gx, gy, head_seat_z))
    head = cylinder(2.75, 3, (gx, gy, head_seat_z - 3))
    actual_screw = shaft.fuse(head)
    current_stack = load('ground-stack')
    head_nominal = G.overlap(current_stack, shaft)
    check('ground display contains the nominal M3 shank',
          abs(head_nominal - shaft.Volume()) < TOL,
          current_shank_common_mm3=head_nominal, nominal_shank_mm3=shaft.Volume())
    for index, ring in enumerate(rings, 1):
        common = G.overlap(shaft, ring)
        check('ground M3 passage through ring ' + str(index), common < TOL,
              common_mm3=common, eye_diameter_mm=3.2, shank_diameter_mm=3,
              radial_hole_air_mm=.1)
    common = G.overlap(actual_screw, washer)
    check('ground M3 passage through tooth washer', common < TOL,
          common_mm3=common, bore_mm=3.2, shank_mm=3)
    bearing = annulus(1.6, 2.75, .01, (gx, gy, head_seat_z))
    bearing_missing = missing_volume(washer, bearing)
    check('ground screw complete washer bearing footprint', bearing_missing < TOL,
          missing_mm3=bearing_missing, bearing_outer_radius_mm=2.75)
    host = joined_hatch
    pilot = cylinder(2, pilot_depth, datum)
    stock = annulus(2, 3.6, pilot_depth, datum)
    pilot_common = G.overlap(host, pilot)
    stock_missing = missing_volume(host, stock)
    end_missing = missing_volume(host, cylinder(2, end_cover, (gx, gy, gz + pilot_depth)))
    check('ground full pilot, minimum annulus and blind end',
          pilot_common < TOL and stock_missing < TOL and end_missing < TOL,
          pilot_common_mm3=pilot_common, annular_missing_mm3=stock_missing,
          end_missing_mm3=end_missing, surrounding_wall_mm=1.6, end_cover_mm=end_cover)
    check('ground actual M3×12 stack and insert reserve',
          engagement >= insert_length and tip_reserve >= .5 and pilot_depth - insert_length >= 1,
          ring_stack_mm=4, tooth_washer_mm=.8, screw_length_mm=screw_length,
          engagement_mm=engagement, insert_length_mm=insert_length, tip_reserve_mm=tip_reserve,
          blind_relief_mm=pilot_depth-insert_length, head_bearing_z_mm=head_seat_z, tip_z_mm=tip_z)
    stations.append({'owner': 'ground-stack', 'mouth_mm': list(datum),
                     'screw_length_mm': screw_length, 'actual_engagement_mm': engagement,
                     'tip_reserve_mm': tip_reserve,'clock_degrees':clock})

    hatch_axes = circle_axes(joined_hatch, 1.65)
    expected_hatch_axes = {(round(m['mouth'][0],5),round(m['mouth'][1],5))
                           for m in hatch_manifest['mounts']}
    check('hatch four native clearance holes', expected_hatch_axes <= set(hatch_axes),
          expected_axes_mm=sorted(expected_hatch_axes), native_axes_mm=hatch_axes,
          clearance_diameter_mm=3.3)
    for index,m in enumerate(hatch_manifest['mounts'],1):
        label='hatch station '+str(index)
        x,y,z=m['mouth']
        screw=load('hatch-screw-'+str(index))
        pilot=cylinder(2,m['pilot_depth'],m['mouth'],m['axis'])
        minimum_stock=annulus(2,3.6,m['pilot_depth'],m['mouth'],m['axis'])
        pilot_common=G.overlap(joined_roof,pilot)
        stock_missing=missing_volume(joined_roof,minimum_stock)
        check(label+' full-depth open fixed-roof pilot',pilot_common<TOL,
              common_mm3=pilot_common,pilot_depth_mm=m['pilot_depth'])
        check(label+' complete minimum insert annulus',stock_missing<TOL,
              missing_mm3=stock_missing,surrounding_wall_mm=1.6)
        end=(cq.Vector(*m['mouth'])+cq.Vector(*m['axis'])*m['pilot_depth']).toTuple()
        end_missing=missing_volume(joined_roof,cylinder(2,m['root_cover'],end,m['axis']))
        check(label+' complete native blind end',end_missing<TOL,
              missing_mm3=end_missing,closed_cover_mm=m['root_cover'])
        roof_common=G.overlap(screw,joined_roof)
        hatch_common=G.overlap(screw,joined_hatch)
        check(label+' complete screw passes joined roof and hatch',
              roof_common<TOL and hatch_common<TOL,roof_common_mm3=roof_common,
              hatch_common_mm3=hatch_common,shank_diameter_mm=3,
              nominal_radial_clearance_mm=.15)
        bearing=annulus(1.65,2.75,.01,(x,y,m['head_bearing_z']-.01))
        missing=missing_volume(joined_hatch,bearing)
        check(label+' complete hatch head bearing footprint',missing<TOL,
              missing_mm3=missing,bearing_plane_z_mm=m['head_bearing_z'],
              head_web_mm=3.)
        tip=screw.BoundingBox().zmin
        engagement=z-tip
        reserve=m['pilot_depth']-engagement
        check(label+' actual M3x8 engagement and blind relief',
              engagement>=m['insert_length'] and reserve>=.5
              and m['pilot_depth']-m['insert_length']>=1,
              actual_tip_z_mm=tip,engagement_mm=engagement,
              insert_length_mm=m['insert_length'],tip_reserve_mm=reserve,
              insert_blind_relief_mm=m['pilot_depth']-m['insert_length'])
        check(label+' head remains below sealed roof height',
              screw.BoundingBox().zmax<=355.,head_top_z_mm=screw.BoundingBox().zmax,
              flush_silicone_cap_stock_mm=.5)
        stations.append({'owner':'rear-roof-hatch','index':index,'mouth_mm':m['mouth'],
                         'screw_length_mm':m['screw_length'],
                         'actual_engagement_mm':engagement,'tip_reserve_mm':reserve})

    bridge = load('supply-lid-boss-3').fuse(load('supply-lid-web-2'))
    # Fixed entry mouth has a vertical attachment lead below its first R14 arc.
    fill_stub = cylinder(3.175, 17.15, (57.5, 426.3, 253.4))
    fixed_checks = [('g-ganen-pump', load('g-ganen-pump')),
                    ('tube-water-5', load('tube-water-5')),
                    ('tube-water-6', load('tube-water-6')),
                    ('fixed flavor-A fill mouth and lead', fill_stub)]
    for name, shape in fixed_checks:
        common = G.overlap(bridge, shape)
        check('fore-east bridge clears ' + name, common < TOL,
              common_mm3=common, native_gap_mm=bridge.distance(shape))
    bridge_boss = load('supply-lid-boss-3')
    web = load('supply-lid-web-2')
    check('fore-east boss reaches lid through native rail and web',
          bridge_boss.distance(web) < 1e-6 and web.distance(load('cold-core/foam-cap-lid-top')) < 1e-6,
          boss_web_gap_mm=bridge_boss.distance(web),
          web_lid_gap_mm=web.distance(load('cold-core/foam-cap-lid-top')),
          pilot_blind_root_mm=3, rail_stock_mm=[8, 3],
          floor_web_fore_edge_y_mm=430.5)

    result = {
        'pass': all(c['pass'] for c in checks), 'checks': checks,
        'stations': stations, 'native_inputs': inputs,
        'source_sha256': {'future/pump-first-layout-study/structure/build_candidate.py': sha(HERE / 'build_candidate.py'),
                          'future/pump-first-layout-study/structure/check_fasteners.py': sha(Path(__file__)),
                          'hardware/reference/ground-ring-stack/ground_ring_stack.py': sha(ROOT / 'hardware/reference/ground-ring-stack/ground_ring_stack.py'),
                          'hardware/mechanical-qualification/README.md': sha(ROOT / 'hardware/mechanical-qualification/README.md')},
        'manifest_sha256': {f: sha(STUDY / f / 'candidate.json') for f in manifests},
        'hatch_manifest_sha256': sha(HERE / 'roof-hatch.json'),
        'water5_manifest_sha256':sha(STUDY/'mounts/water5-hosts.json'),
        'fluid_manifest_sha256':sha(fluid_path),
        'tube_manifest_sha256':sha(tube_path)if tube_path.exists()else None,
        'joined_print_report_sha256': sha(print_path),
        'pilot_scope': 'The complete fused and recut roof/lid/hatch print solids, including parent stock at each pilot mouth, annulus and blind end.',
        'meter_profile_scope': 'The full24.8mm crown rectangle has an explicitly recorded Water5 clearance corner. Complete24.05mm uninterrupted strips, lower3mm bearing walls and unchanged roof-root coupons are required; all missing rectangular material must lie wholly inside the full declared Water5 tool. This establishes nominal geometric attachment only, not loaded capacity or lifetime.',
        'factory_sequence': [
            'Install all heat-set inserts in the empty native roof and lid hosts. The complete 4.6mm knurl cannot pass through the assembled 3.2mm PCB or 3.5mm supply site holes.',
            'Prewire the populated controller and mount it components down with M3×6 screws. The supply is carried unfastened during the main back-top Y slide, then seated on its four native6.7mm ledges and clamped through the open rear hatch with0.8mm washers and M3×12 screws.',
            'Enter the bare ASSE valve through the fore aperture in its rolled pose with the purchased VK still absent. Hold the seated valve while its separate carrier and two bearing clamps are fitted; both M3×12 screws enter the short4mm inserts before the purchased VK is installed. Full entry and tool paths are owned by asse-factory-check.json.',
            'Clamp the five-lug ground fan and discharge-chain key to the removed hatch. After its checked +Z landing, install four M3×8 hatch screws from the top and cast the continuous silicone seam and flush head caps after torque.',
        ],
        'limits': [
            'Exact nominal geometry and shaft passage are qualified. Insert pullout, print bending, tightening torque, creep and vibration remain physical properties.',
            'The supply mounting ledges and ground rings retain their reference representative-envelope scope; machining tolerances and actual hardware must follow the controlled purchased parts.',
            'The fore-east bridge check covers the fixed fill mouth and vertical attachment lead. The complete rebuilt fluid18 sweep belongs to the integrated native route audit.',
            'This audit does not qualify whole roof closure motion or flexible hose and wire deformation.',
        ],
    }
    drift = [n for n, r in inputs.items() if sha(ROOT/r['brep']) != r['sha256']]
    result['source_drift'] = drift
    result['pass'] = result['pass'] and not drift
    (HERE / 'fastener-native-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'pass': result['pass'], 'checks': len(checks), 'stations': len(stations)}), flush=True)


if __name__ == '__main__':
    main()
