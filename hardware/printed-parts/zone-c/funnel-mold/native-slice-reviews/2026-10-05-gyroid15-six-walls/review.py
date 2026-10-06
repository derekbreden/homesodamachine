"""Read current native mould slice without changing saved production projects."""
from pathlib import Path
import hashlib, json, math, re, sys, zipfile
import xml.etree.ElementTree as ET

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
HERE=ROOT/'.cache/funnel-gyroid-2026-10-05'
MODELS=ROOT/'hardware/printed-parts/zone-c/funnel-mold'
PUBLIC=Path(__file__).resolve().parent
PUBLIC.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'tools/funnel-mold-print')]
import enclosure_support_audit as support
from profiles import equivalent, qn
from verify_print import embedded_mesh

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

source=HERE/'current-funnel-mould-petg088.3mf'
sliced=HERE/'slice/current-funnel-mould-petg088.gcode.3mf'
record=json.loads((HERE/'preparation-review.json').read_text())
physical=json.loads((HERE/'physical-recipe-binding.json').read_text())
result=json.loads((HERE/'slice/result.json').read_text())
assert result['return_code']==0,result
assert len(result['sliced_plates'])==2
assert all(not p['warning_message'] for p in result['sliced_plates'])
with zipfile.ZipFile(source) as z:
    source_settings=json.loads(z.read('Metadata/project_settings.config'))
with zipfile.ZipFile(sliced) as z:
    assert z.testzip() is None
    settings=json.loads(z.read('Metadata/project_settings.config'))
    left_bed=np.array([list(map(float,p.split('x'))) for p in settings['extruder_printable_area'][0].split(',')])
    left_bed_low=left_bed.min(axis=0)
    left_bed_high=left_bed.max(axis=0)
    changed={k:{'input':source_settings.get(k),'sliced':settings.get(k)}
             for k in source_settings.keys()|settings.keys()
             if source_settings.get(k)!=settings.get(k)}
    meaning_changed={k:row for k,row in changed.items()
                     if not equivalent(k,row['input'],row['sliced'])}
    essential=tuple(record['selected_recipe'])
    assert all(equivalent(k,source_settings[k],settings[k]) for k in essential)
    slices=ET.fromstring(z.read('Metadata/slice_info.config'))
    config=ET.fromstring(z.read('Metadata/model_settings.config'))
    plates=[]
    figures=[]
    for i,name in enumerate(('cavity','core'),1):
        obj=next(obj for obj in config.findall('object')
                 if obj.find("part/metadata[@key='name']").attrib['value']==name)
        mesh_check=embedded_mesh(z,obj.attrib['id'],MODELS/(name+'.stl'))
        gname=f'Metadata/plate_{i}.gcode'
        raw=z.read(gname)
        assert hashlib.md5(raw).hexdigest()==z.read(gname+'.md5').decode().strip().lower()
        gpath=HERE/'slice'/f'plate_{i}.gcode'
        assert gpath.read_bytes()==raw
        gcode=raw.decode()
        nozzle=[n.attrib for n in slices.findall('plate')[i-1].findall('nozzle')]
        assert nozzle==[{'id':'0','extruder_id':'1','nozzle_diameter':'0.4','volume_type':'Standard'}],nozzle
        trims=[line.strip() for line in gcode.splitlines() if line.strip().startswith('G29.1 Z')]
        assert 'G29.1 Z0.16' in trims,trims

        # The coordinate profile contains exactly this part; the core's plate
        # is normalized from project X545.5 back to its local X149.5 bed frame.
        with zipfile.ZipFile(source) as src:
            payloads={n:src.read(n) for n in src.namelist()}
        model=ET.fromstring(payloads['3D/3dmodel.model'])
        resources=model.find(qn('resources'))
        for objnode in list(resources):
            if objnode.attrib.get('id')!=str(i*2):resources.remove(objnode)
        build=model.find(qn('build'))
        for item in list(build):
            if item.attrib.get('objectid')!=str(i*2):build.remove(item)
        item=next(iter(build))
        transform=[float(v) for v in item.attrib['transform'].split()]
        transform[9]-=396*(i-1)
        item.set('transform',' '.join(f'{v:.12g}' for v in transform))
        cfg=ET.fromstring(payloads['Metadata/model_settings.config'])
        for node in list(cfg):
            if node.tag=='object' and node.attrib['id']!=str(i*2):cfg.remove(node)
        payloads['3D/3dmodel.model']=ET.tostring(model,xml_declaration=True,encoding='UTF-8')
        payloads['Metadata/model_settings.config']=ET.tostring(cfg,xml_declaration=True,encoding='UTF-8')
        coordinate=HERE/(name+'-coordinate-profile.3mf')
        with zipfile.ZipFile(coordinate,'w',zipfile.ZIP_DEFLATED) as out:
            for n,data in payloads.items():out.writestr(n,data)
        audit=support.audit(gpath,'funnel-mold/'+name,model=MODELS/(name+'.stl'),
             profile=source,coordinate_profile=coordinate,include_unlabelled_support=True)
        audit_path=PUBLIC/(name+'-support-topology.json')
        audit_path.write_text(json.dumps(audit,indent=2)+'\n')

        # All deposited path bounds use the emitted width, not centreline
        # bounds. Startup purge, machine custom moves and tool changes are
        # excluded; model, brim and every support feature are included.
        xy=np.array([0.,0.]);e=0.;relative_e=True;absolute_xy=True
        feature='';width=.42;layer=0;zheight=None
        lo=np.array([math.inf,math.inf]);hi=-lo
        first_model=[];first_support=[];interface=[];supports=[]
        features={};first_z=None
        for rawline in gcode.splitlines():
            line=rawline.strip()
            if line.startswith('; layer num/total_layer_count:'):
                layer=int(line.split(':',1)[1].split('/')[0])
            elif line.startswith('; Z_HEIGHT:'):
                zheight=float(line.split(':',1)[1]);first_z=first_z or zheight
            elif line.startswith('; FEATURE:'):
                feature=line.split(':',1)[1].strip()
            elif line.startswith('; LINE_WIDTH:'):
                width=float(line.split(':',1)[1])
            code=line.split(';',1)[0].strip()
            if not code:continue
            command=code.split(None,1)[0]
            words={k:float(v) for k,v in support._WORD.findall(code)}
            if command=='G90':absolute_xy=True;continue
            if command=='G91':absolute_xy=False;continue
            if command=='M82':relative_e=False;continue
            if command=='M83':relative_e=True;continue
            if command=='G92':
                xy=np.array([words.get('X',xy[0]),words.get('Y',xy[1])]);e=words.get('E',e);continue
            if command not in ('G0','G1','G2','G3'):continue
            new=np.array([words.get('X',xy[0]),words.get('Y',xy[1])]) if absolute_xy else xy+np.array([words.get('X',0.),words.get('Y',0.)])
            de=words.get('E',0.) if relative_e else words.get('E',e)-e
            if zheight is not None and de>1e-9 and np.linalg.norm(new-xy)>1e-9 and feature not in ('Custom','Flush','Wipe tower',''):
                points=([tuple(new)] if command in ('G0','G1') else support._arc_points(tuple(xy),tuple(new),words,command=='G2'))
                start=xy
                for point in points:
                    end=np.array(point)
                    lo=np.minimum(lo,np.minimum(start,end)-width/2)
                    hi=np.maximum(hi,np.maximum(start,end)+width/2)
                    features[feature]=features.get(feature,0)+1
                    segment=[start.tolist(),end.tolist()]
                    if feature.startswith('Support'):
                        if layer==1:first_support.append(segment)
                        # Subsample only the visualization; topology audit
                        # above reads every support extrusion path.
                        if features[feature]%50==0:supports.append(segment)
                        if feature=='Support interface' and features[feature]%30==0:interface.append(segment)
                    elif layer==1:first_model.append(segment)
                    start=end
            xy=new
            if 'E' in words:e=e+words['E'] if relative_e else words['E']
        assert len(first_model)>0
        within=bool(np.all(lo>=left_bed_low) and np.all(hi<=left_bed_high))
        assert within,(lo,hi)
        p=result['sliced_plates'][i-1]
        est=float(p['total_predication']);mass=float(p['filaments'][0]['total_used_g'])
        plate_record={'part':name,'plate':i,'orientation':'upright' if i==1 else 'inverted',
           'mesh':mesh_check,'gcode_sha256':hashlib.sha256(raw).hexdigest(),'nozzle':nozzle,
           'z_trim_commands':trims,'support_present':bool(first_support or supports or interface),'slice_warning':p['warning_message'],
           'layers':int(re.search(r'; total layer number: (\d+)',gcode)[1]),
           'estimated_seconds':est,'estimated_filament_g':mass,
           'all_deposited_feature_bounds_xy_mm':[lo.tolist(),hi.tolist()],
           'left_nozzle_printable_polygon_mm':left_bed.tolist(),
           'within_printable_area':within,'minimum_bed_edge_margin_mm':float(min(*(lo-left_bed_low),*(left_bed_high-hi))),
           'first_layer_height_mm':first_z,'first_layer_model_segments':len(first_model),
           'first_layer_support_segments':len(first_support),'extrusion_feature_segment_counts':features,
           'support_topology_summary':audit['summary'],'support_topology_record_sha256':sha(audit_path),
           'support_removal_scope':'Every emitted support body is retained in the topology record, including bodies lacking interface labels. Open side bolt pockets provide access to cut and detach any cavity support; the core has an open tapered rod access hole. A collision-free withdrawal of complete connected support bodies, adhesion, clean release and finished casting are not established by this reading.'}
        plates.append(plate_record)
        fig,axes=plt.subplots(1,2,figsize=(12,6),constrained_layout=True)
        for ax in axes:
            ax.set_xlim(left_bed_low[0],left_bed_high[0]);ax.set_ylim(left_bed_low[1],left_bed_high[1]);ax.set_aspect('equal');ax.set_xlabel('Left nozzle bed X (mm)');ax.set_ylabel('Bed Y (mm)');ax.grid(alpha=.2)
        axes[0].add_collection(LineCollection(first_model,colors='#356b97',linewidths=.8))
        axes[0].add_collection(LineCollection(first_support,colors='#e8903c',linewidths=.8))
        axes[0].set_title(f'{name.capitalize()}: first layer model and supports')
        axes[1].add_collection(LineCollection(supports,colors='#888888',linewidths=.3,alpha=.5))
        axes[1].add_collection(LineCollection(interface,colors='#c04060',linewidths=.45,alpha=.8))
        axes[1].set_title('Support paths and labelled interfaces, top view')
        image=PUBLIC/(name+'-native-supports.png')
        fig.savefig(image,dpi=160);plt.close(fig)
        figures.append({'file':image.name,'sha256':sha(image),'scope':'First layer complete; all-layer support/interface drawing is subsampled. Topology record reads every emitted path.'})

record['native_slice_pending']=False
record['native_slice_success']=True
record['native_slice']={'slice_sha256':sha(sliced),'slice_file':str(sliced.relative_to(ROOT)),
 'cli_return_code':result['return_code'],'slicer_version':'02.08.02.61','plates':plates,
 'all_settings_changes':changed,'nontrivial_setting_changes':meaning_changed,
 'selected_recipe_retained':True, 'sparse_process': 'six walls, 15% gyroid, six top/bottom layers','figures':figures}
record['physical_recipe_binding']=physical
record['scope']='Complete funnel tooling: two PETG mold bodies and a stock straight 6 x 25 mm stainless steel rod. This record checks the exported geometry and native slice; print and casting behavior remain ordinary physical design outcomes to observe in use. No print was submitted.'
record['native_support_tool_sha256']=sha(ROOT/'hardware/scripts/enclosure_support_audit.py')
record['support_topology_method']={'grid_mm':support.GRID_MM,
 'support_layer_link_mm':support.TREE_LINK_MM,'interface_layer_link_mm':support.INTERFACE_LINK_MM,
 'scope':'Quantized connectivity of emitted extrusion centrelines. It identifies support groups and labelled interface regions; it does not reconstruct solid support volumes or prove their complete withdrawal.'}
(PUBLIC/'readiness-review.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'plates':plates,'setting_changes':changed,'scope':record['scope']},indent=2),flush=True)
