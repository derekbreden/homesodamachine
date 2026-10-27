"""Manual native bead/contact reading of three retention strips and18 leaves.

This reads only the prepared archive and bound source meshes. No print settings
or geometry change, and no printer communication.
"""
from __future__ import annotations
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from shapely import buffer,union_all
from shapely.geometry import LineString,box

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
SHARED=ROOT/'hardware/printed-parts/enclosure/trial-preparation'
sys.path.insert(0,str(SHARED))
import _mesh
spec=importlib.util.spec_from_file_location('retention_matrix_native_reader',SHARED/'review.py')
reader=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def components(shape):
    return [g for g in getattr(shape,'geoms',[shape])if g.area>1e-6]


def plain(value):
    if isinstance(value,np.generic):
        return value.item()
    raise TypeError(f'Unsupported report value: {type(value).__name__}')


def main():
    overview=json.loads((HERE/'offline-review.json').read_text())
    directory=ROOT/overview['directory']
    preparation=json.loads((directory/'preparation.json').read_text())
    report=json.loads((HERE.parents[1]/'retention-matrix-geometry.json').read_text())
    records=preparation['objects']
    if len(records)!=3:
        raise ValueError('The plate must contain three independent strip objects')
    objects={}
    for record,rowid in zip(records,'ABC'):
        rotation=np.array(record['build_rotation'])
        if not np.allclose(rotation,np.eye(3),atol=1e-9):
            raise ValueError('Source+X and row order must retain identity rotation, no scaling')
        translation=np.array(record['translation_mm'])
        centre=np.array(record['source_center_mm'])
        source=_mesh.read_stl(ROOT/record['stl']).astype(float)
        triangles=((source.reshape(-1,3)-centre)@rotation.T+translation).reshape(-1,3,3)
        samples=[s for s in report['samples']if s['label'].startswith(rowid)]
        objects[record['identify_id']]={'row':rowid,'record':record,'triangles':triangles,
            'offset':translation-centre,'samples':samples,'previous':None}
        if len(samples)!=3 or record['fins']or record['ribbons']or record['modifiers']:
            raise ValueError('Each row needs exactly three clips and no added microfins/modifiers')
    object_rows,leaf_rows=[],[]
    feature_counts=Counter()
    handle,stream=reader.gcode_lines(ROOT/overview['archive'])
    with stream:
        for z,height,roads in reader.layers(stream):
            for oid,obj in objects.items():
                model=[r for r in roads if r[5]in reader.MODEL and r[6]==oid]
                if not model:
                    continue
                lines=np.array([LineString([(r[0],r[1]),(r[2],r[3])])for r in model],dtype=object)
                widths=np.array([r[4]for r in model])
                road_beads=buffer(lines,widths/2,quad_segs=4)
                beads=union_all(road_beads)
                previous=obj['previous']
                contact=[]
                free_lengths=[]
                full_nonbridge=0
                mid=z-height/2
                axis_z=obj['samples'][0]['tube_axis_z_mm']+obj['offset'][2]
                expanded_previous={}
                # The requested contact questions concern the second layer and
                # upper leaves. Other layers still supply the preceding beads.
                if previous is not None and (abs(z-.44)<1e-5 or mid>=axis_z):
                    for line,road,bead in zip(lines,model,road_beads):
                        area=bead.intersection(previous).area
                        contact.append(area/bead.area)
                        width=round(road[4],6)
                        if width not in expanded_previous:
                            expanded_previous[width]=previous.buffer(road[4]/2,quad_segs=4)
                        free=line.difference(expanded_previous[width])
                        free_lengths.extend(g.length for g in getattr(free,'geoms',[free]))
                        if area<1e-9 and road[5]not in {'Bridge','Internal Bridge'}:
                            full_nonbridge+=1
                object_rows.append({'row':obj['row'],'layer_top_z_mm':z,'height_mm':height,
                    'model_area_mm2':beads.area,
                    'minimum_road_bead_contact_fraction':min(contact)if contact else None,
                    'roads_without_previous_bead_contact':sum(c<=1e-8 for c in contact),
                    'longest_centerline_with_no_bead_contact_mm':max(free_lengths,default=0),
                    'fully_unbacked_nonbridge_roads':full_nonbridge,
                    'upper_leaf_layer':mid>=axis_z})
                feature_counts.update(r[5]for r in model)
                if mid>=axis_z:
                    section=_mesh.section_polygons(obj['triangles'],mid)
                    for sample in obj['samples']:
                        x=sample['centre_x_mm']+obj['offset'][0]
                        y=sample.get('centre_y_mm',0.)+obj['offset'][1]
                        radius=sample['outer_radius_mm']
                        for side,xlo,xhi in [('left',x-radius-.01,x),('right',x,x+radius+.01)]:
                            region=box(xlo,y-4.01,xhi,y+4.01)
                            stock=section.intersection(region)
                            if stock.area<.01:
                                continue
                            printed=beads.intersection(region)
                            stock_pieces=components(stock)
                            printed_pieces=components(printed)
                            probe=LineString([(xlo,y),(xhi,y)])
                            crossings=[]
                            for line,road in zip(lines,model):
                                cross=line.intersection(probe)
                                for point in getattr(cross,'geoms',[cross]):
                                    if point.geom_type=='Point'and stock.buffer(.03).covers(point):
                                        crossings.append((round(point.x-obj['offset'][0],5),road[5],road[4]))
                            leaf_rows.append({'sample':sample['label'],'bore_mm':sample['bore_diameter_mm'],
                                'spring_wall_mm':sample['spring_wall_mm'],'tip_angle_deg':sample['tip_angle_deg'],
                                'side':side,'layer_top_z_mm':z,'stock_area_mm2':stock.area,
                                'bead_coverage':printed.intersection(stock).area/stock.area,
                                'stock_components':len(stock_pieces),'bead_components':len(printed_pieces),
                                'stock_pieces_touched':sum(printed.intersects(part)for part in stock_pieces),
                                'centre_span_path_crossings':sorted(set(crossings)),
                                'bead_footprint_touches_previous':previous.intersects(printed)if previous is not None else None})
                obj['previous']=beads
    handle.close()
    upper=[r for r in object_rows if r['upper_leaf_layer']]
    seconds=[r for r in object_rows if abs(r['layer_top_z_mm']-.44)<1e-5]
    support_roads=0
    brim_roads=0
    handle,stream=reader.gcode_lines(ROOT/overview['archive'])
    with stream:
        for z,height,roads in reader.layers(stream):
            support_roads+=sum(r[5]in reader.SUPPORT for r in roads)
            brim_roads+=sum(r[5]=='Skirt'for r in roads)
    handle.close()
    checks={
        'nine_same_bores':all(abs(s['bore_diameter_mm']-6.55)<1e-7 for s in report['samples']),
        'all18_upper_leaves_have_paths':{(r['sample'],r['side'])for r in leaf_rows}=={(s['label'],side)for s in report['samples']for side in ('left','right')},
        'all_upper_stock_components_touched':all(r['stock_pieces_touched']==r['stock_components']for r in leaf_rows),
        'all_upper_leaf_bead_footprints_connected':all(r['bead_components']==1 for r in leaf_rows),
        'all_upper_leaf_footprints_touch_previous':all(r['bead_footprint_touches_previous']for r in leaf_rows),
        'all_upper_roads_have_previous_bead_contact':all(r['roads_without_previous_bead_contact']==0 for r in upper),
        'all_second_layer_roads_have_previous_bead_contact':len(seconds)==3 and all(r['roads_without_previous_bead_contact']==0 for r in seconds),
        'no_support_roads':support_roads==0,
    }
    summary={
        'scope':'Bound STL sections and commanded bead envelopes only; no physical adhesion, grip, force, layer-strength or lifetime claim.',
        'archive':overview['archive'],'archive_sha256':overview['archive_sha256'],
        'source_sha256':overview['source_sha256'],
        'object_count':3,'samples':9,'upper_leaf_count':18,'layer_count_by_row':dict(Counter(r['row']for r in object_rows)),
        'features':dict(feature_counts),'support_roads':support_roads,'skirt_brim_roads':brim_roads,
        'upper_leaf_samples':len(leaf_rows),
        'minimum_upper_leaf_bead_coverage':min(r['bead_coverage']for r in leaf_rows),
        'upper_leaf_missing_stock_pieces':sum(r['stock_components']-r['stock_pieces_touched']for r in leaf_rows),
        'upper_leaf_disconnected_bead_footprints':sum(r['bead_components']>1 for r in leaf_rows),
        'upper_leaf_layers_without_previous_bead_contact':sum(not r['bead_footprint_touches_previous']for r in leaf_rows),
        'second_layer_minimum_road_bead_contact_fraction':min(r['minimum_road_bead_contact_fraction']for r in seconds),
        'upper_layer_minimum_road_bead_contact_fraction':min(r['minimum_road_bead_contact_fraction']for r in upper),
        'upper_layer_longest_centerline_without_bead_contact_mm':max(r['longest_centerline_with_no_bead_contact_mm']for r in upper),
        'checks':checks,'pass':all(checks.values()),'leaf_rows':leaf_rows,'layer_rows':object_rows}
    (HERE/'path-review.json').write_text(json.dumps(summary,indent=2,default=plain)+'\n')
    print(json.dumps({k:v for k,v in summary.items()if k not in {'leaf_rows','layer_rows','source_sha256'}},indent=2,default=plain),flush=True)


if __name__=='__main__':
    main()
