"""Manual contact reading of the combined native plate; no reslice or submission.

Checks first/second layers, six tube leaves, and complete cable wall/hook
components. Cooling and support-in-pocket readings have a separate owner.
"""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import sys

import numpy as np
from shapely import buffer,union_all
from shapely.geometry import LineString,box

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
SHARED=ROOT/'hardware/printed-parts/enclosure/trial-preparation'
sys.path.insert(0,str(SHARED))
import _mesh
spec=importlib.util.spec_from_file_location('combined_contact_reader',SHARED/'review.py')
reader=importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def pieces(s):
    return [g for g in getattr(s,'geoms',[s])if g.area>1e-6]


def plain(v):
    if isinstance(v,np.generic):
        return v.item()
    raise TypeError(type(v).__name__)


def main():
    overview=json.loads((HERE/'offline-review.json').read_text())
    directory=ROOT/overview['directory']
    archive=ROOT/overview['archive']
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=overview['archive_sha256']:
        raise ValueError('Combined archive differs from prepared binding')
    prep=json.loads((directory/'preparation.json').read_text())
    tube=json.loads((ROOT/'future/tube-snap-exploration/c2-bore-geometry.json').read_text())
    cable=json.loads((ROOT/'future/cable-clip-exploration/wall9-span-geometry.json').read_text())
    objects={}
    for rec in prep['objects']:
        if not np.allclose(rec['build_rotation'],np.eye(3),atol=1e-9):
            raise ValueError('Expected upright source meshes with identity rotation')
        if hashlib.sha256((ROOT/rec['stl']).read_bytes()).hexdigest()!=rec['stl_sha256']:
            raise ValueError('Source mesh changed since native preparation')
        offset=np.array(rec['translation_mm'])-np.array(rec['source_center_mm'])
        is_tube='tube-snap-c2-'in rec['stl']
        variant=None if is_tube else next(v for v in cable['variants']if v['stl']==rec['stl'])
        obj={'name':rec['name'],'tube':is_tube,'offset':offset,'record':rec,
             'triangles':_mesh.read_stl(ROOT/rec['stl']).astype(float)+offset,
             'previous':None,'first_two':[],'layers':0,'hook_layers':[]}
        if variant:
            obj.update(variant=variant,
                arm_region=box(offset[0]+.001,offset[1]-variant['span_along_cable_mm']/2-.001,
                               offset[0]+5.201,offset[1]+variant['span_along_cable_mm']/2+.001),
                corbel_start=variant['corbel']['build_start_z_mm']+offset[2],
                lip_z=variant['retaining_lip']['build_underside_z_mm']+offset[2])
        objects[rec['identify_id']]=obj
    if len(objects)!=3 or sum(o['tube']for o in objects.values())!=1:
        raise ValueError('Expected one three-bore tube object and two cable objects')
    leaves=[]
    upper_contact=[]
    features=Counter()
    handle,stream=reader.gcode_lines(archive)
    with stream:
        for z,height,roads in reader.layers(stream):
            for oid,obj in objects.items():
                own=[r for r in roads if r[5]in reader.MODEL and r[6]==oid]
                if not own:
                    continue
                obj['layers']+=1
                lines=np.array([LineString([(r[0],r[1]),(r[2],r[3])])for r in own],dtype=object)
                widths=np.array([r[4]for r in own])
                beads_each=buffer(lines,widths/2,quad_segs=4)
                beads=union_all(beads_each)
                previous=obj['previous']
                mid=z-height/2
                features.update(r[5]for r in own)
                if len(obj['first_two'])<2:
                    row={'layer_top_z_mm':z,'height_mm':height,
                         'model_components':len(pieces(beads)),
                         'component_areas_mm2':sorted(p.area for p in pieces(beads))}
                    if previous is not None:
                        contact=[b.intersection(previous).area/b.area for b in beads_each]
                        row.update(bead_area_fraction_over_first=beads.intersection(previous).area/beads.area,
                            minimum_individual_road_contact_fraction=min(contact),
                            roads_without_any_bead_contact=sum(c<=1e-8 for c in contact))
                    obj['first_two'].append(row)
                if obj['tube'] and mid>=tube['samples'][0]['tube_axis_z_mm']+obj['offset'][2]:
                    stock_section=_mesh.section_polygons(obj['triangles'],mid)
                    contacts=[]
                    expanded={}
                    free_lengths=[]
                    for line,road,bead in zip(lines,own,beads_each):
                        contacts.append(bead.intersection(previous).area/bead.area)
                        key=round(road[4],6)
                        if key not in expanded:
                            expanded[key]=previous.buffer(road[4]/2,quad_segs=4)
                        clear=line.difference(expanded[key])
                        free_lengths.extend(g.length for g in getattr(clear,'geoms',[clear]))
                    upper_contact.append({'layer_top_z_mm':z,'minimum_road_contact_fraction':min(contacts),
                        'roads_without_previous_bead_contact':sum(c<=1e-8 for c in contacts),
                        'longest_centerline_without_bead_contact_mm':max(free_lengths,default=0.)})
                    for sample in tube['samples']:
                        x=sample['centre_x_mm']+obj['offset'][0]
                        y=sample['centre_y_mm']+obj['offset'][1]
                        radius=sample['outer_radius_mm']
                        for side,xlo,xhi in [('left',x-radius-.01,x),('right',x,x+radius+.01)]:
                            region=box(xlo,y-4.01,xhi,y+4.01)
                            stock=stock_section.intersection(region)
                            if stock.area<.01:
                                continue
                            printed=beads.intersection(region)
                            stock_parts=pieces(stock)
                            leaves.append({'sample':sample['label'],'side':side,
                                'layer_top_z_mm':z,'stock_area_mm2':stock.area,
                                'bead_coverage':printed.intersection(stock).area/stock.area,
                                'stock_components':len(stock_parts),
                                'stock_components_touched':sum(printed.intersects(p)for p in stock_parts),
                                'bead_components':len(pieces(printed)),
                                'previous_bead_contact':previous.intersects(printed)})
                elif not obj['tube'] and mid>obj['corbel_start']:
                    stock=_mesh.section_polygons(obj['triangles'],mid).intersection(obj['arm_region'])
                    if stock.area>1e-5:
                        printed=beads.intersection(obj['arm_region'])
                        complete=[c for c in pieces(beads)if c.intersects(printed)]
                        obj['hook_layers'].append({'layer_top_z_mm':z,
                            'stage':'retaining hook/cap'if mid>=obj['lip_z']else'corbel/post',
                            'stock_area_mm2':stock.area,
                            'bead_coverage':stock.intersection(printed).area/stock.area,
                            'arm_region_bead_components':len(pieces(printed)),
                            'complete_wall_hook_components':len(complete),
                            'complete_components_touch_previous':bool(complete)and all(c.intersects(previous)for c in complete)})
                obj['previous']=beads
    handle.close()
    first={str(oid):{'name':o['name'],'layers':o['first_two']}for oid,o in objects.items()}
    cables=[]
    for oid,obj in objects.items():
        if obj['tube']:
            continue
        rows=obj['hook_layers']
        cables.append({'object_id':oid,'name':obj['name'],
            'span_along_cable_mm':obj['variant']['span_along_cable_mm'],
            'sampled_layers':len(rows),'retaining_hook_layers':sum(r['stage']=='retaining hook/cap'for r in rows),
            'minimum_stock_bead_coverage':min(r['bead_coverage']for r in rows),
            'layers_without_previous_complete_component_contact':sum(not r['complete_components_touch_previous']for r in rows),
            'layers':rows})
    checks={
        'generic_native_review_pass':overview['native_review_pass'],
        'all_three_first_second_layers_present':all(len(o['first_two'])==2 for o in objects.values()),
        'first_second_layers_one_component':all(r['model_components']==1 for o in objects.values()for r in o['first_two']),
        'second_layer_roads_all_touch_first':all(o['first_two'][1]['roads_without_any_bead_contact']==0 for o in objects.values()),
        'all_six_tube_leaves_present':{(r['sample'],r['side'])for r in leaves}=={(s['label'],side)for s in tube['samples']for side in ('left','right')},
        'tube_upper_stock_components_printed':all(r['stock_components_touched']==r['stock_components']for r in leaves),
        'tube_upper_leaf_beads_connected':all(r['bead_components']==1 for r in leaves),
        'tube_upper_leaf_beads_touch_previous':all(r['previous_bead_contact']for r in leaves),
        'tube_upper_roads_all_touch_previous':bool(upper_contact)and all(r['roads_without_previous_bead_contact']==0 for r in upper_contact),
        'both_cable_corbels_hooks_sampled':len(cables)==2 and all(c['sampled_layers']>0 and c['retaining_hook_layers']>0 for c in cables),
        'cable_complete_components_anchored_previous':all(c['layers_without_previous_complete_component_contact']==0 for c in cables),
    }
    report={'scope':'Manual commanded bead/contact reading only. Support-in-pocket and cooling/timing are reviewed separately.',
        'archive':overview['archive'],'archive_sha256':overview['archive_sha256'],
        'source_sha256':overview['source_sha256'],'reviewer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'features':dict(features),'layers_by_object':{o['name']:o['layers']for o in objects.values()},
        'first_two_model_layers':first,
        'tube':{'leaf_count':6,'sampled_leaf_layers':len(leaves),
            'minimum_leaf_stock_bead_coverage':min(r['bead_coverage']for r in leaves),
            'minimum_upper_road_previous_contact_fraction':min(r['minimum_road_contact_fraction']for r in upper_contact),
            'upper_roads_without_previous_bead_contact':sum(r['roads_without_previous_bead_contact']for r in upper_contact),
            'leaf_layers':leaves,'upper_road_layers':upper_contact},
        'cables':cables,
        'interpretation':'Cable anchoring follows each complete connected emitted section through the broad wall; the first corbel expansion may lie outside the previous wall while its full in-plane component remains attached. Tube upper leaves additionally require individual roads to contact previous-layer beads. These are geometric path readings, not physical bond/strength or grip acceptance.',
        'checks':checks,'pass':all(checks.values())}
    (HERE/'path-review.json').write_text(json.dumps(report,indent=2,default=plain)+'\n')
    print(json.dumps({'pass':report['pass'],'checks':checks,'tube':{k:v for k,v in report['tube'].items()if k not in {'leaf_layers','upper_road_layers'}},
        'cables':[{k:v for k,v in c.items()if k!='layers'}for c in cables]},indent=2,default=plain),flush=True)
    if not report['pass']:
        raise ValueError('Manual combined path/contact review needs attention')


if __name__=='__main__':
    main()
