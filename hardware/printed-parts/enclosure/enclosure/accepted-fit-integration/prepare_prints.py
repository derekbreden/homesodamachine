"""Slice accepted flat-wing upper enclosure halves using shared PET-GF settings."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,zipfile
import xml.etree.ElementTree as ET
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'tools').is_dir());ENC=HERE.parent
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
import refresh_print_project as writer
PROFILE=ROOT/'hardware/printed-parts/petgf.3mf'
JOBS={
 'front-top':('H2C',.18,0.,'2026-10-01-enclosure-front-top-flat-wings-h2c-v15','enclosure-front-top-flat-wings-black-z018-h2c-v15'),
 'back-top':('Mark2',.04,180.,'2026-10-01-enclosure-back-top-flat-wings-mark2-v4','enclosure-back-top-flat-wings-black-z004-mark2-v4')}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(part):
 printer,trim,angle,directory,stem=JOBS[part];job=ROOT/'.cache/prints'/directory
 job.mkdir(parents=True,exist_ok=True);target=job/(stem+'-input.3mf')
 assert not target.exists(),'Reviewed projects are immutable.'
 source=ENC/f'enclosure-{part}.stl'
 # Centre the roof-down part's complete tree-base footprint, retaining the
 # 15 mm model border and over 10 mm for every support extrusion.
 offset=(0.,9.3) if part=='back-top' else (0.,0.)
 report=writer.refresh(PROFILE,target,parts=((f'enclosure-{part}',source,angle),),offsets=(offset,),
                       title=f'Enclosure {part}, accepted flat-wing receiver; {printer}',z_trim=trim,plate_border=15.)
 with zipfile.ZipFile(target) as z:members={n:z.read(n) for n in z.namelist()}
 settings=json.loads(members[writer.SETTINGS_MEMBER])
 overrides={'extruder_ams_count':['1#0|4#0','1#0|4#0'],'support_filament':'1','support_interface_filament':'1','flush_into_support':'0'}
 # The roof-down part uses the same uncompensated bed perimeter as the accepted
 # additive carrier foot; X/Y fit features begin well above this roof band.
 if part=='back-top':overrides['elefant_foot_compensation']='0'
 settings.update(overrides)
 members[writer.SETTINGS_MEMBER]=json.dumps(settings,indent=2).encode()
 # Range IDs are one-based object indices, not the 3MF resource object IDs.
 ranges=ET.Element('objects');obj=ET.SubElement(ranges,'object',id='1')
 if part=='front-top':
  row=ET.SubElement(obj,'range',min_z='187.0000',max_z='195.0000')
  ET.SubElement(row,'option',opt_key='layer_height').text='0.08'
  bands=[{'min_z':187.,'max_z':195.,'layer_height':.08,'reason':'Complete visible roof/corner rounds; measured on STEP.'}]
 else:
  row=ET.SubElement(obj,'range',min_z='0.0000',max_z='9.4000')
  ET.SubElement(row,'option',opt_key='layer_height').text='0.24'
  ET.SubElement(row,'option',opt_key='wall_loops').text='6'
  bands=[{'min_z':0.,'max_z':9.4,'layer_height':.24,'wall_loops':6,'reason':'Additive expanding roof-side transition and its show-surface run-out.'}]
 members['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='utf-8',xml_declaration=True)
 member=report['parts'][0]['member'];raw=members[member]
 vp=rb'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"\s*/>'
 tp=rb'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"\s*/>'
 vertices=np.fromiter((float(v) for m in re.finditer(vp,raw) for v in m.groups()),dtype=float).reshape(-1,3)
 faces=np.fromiter((int(v) for m in re.finditer(tp,raw) for v in m.groups()),dtype=np.int64).reshape(-1,3)
 cad=vertices+report['parts'][0]['source_center_mm'];tri=cad[faces]
 # Restrict blocking to the external roof-side transitions; interior hardware
 # seats, display-wing roofs and nameplate pockets retain their tree supports.
 west=(tri[:,:,0].max(axis=1)<=-100)&(tri[:,:,2].min(axis=1)>=345.69)
 east=(tri[:,:,0].min(axis=1)>=100)&(tri[:,:,2].min(axis=1)>=345.69)
 selected=west|east;assert selected.any()
 flags=iter(selected)
 def paint(m):return m.group(0).replace(b'/>',b'paint_supports="8" />') if next(flags) else m.group(0)
 members[member]=re.sub(tp,paint,raw)
 assert members[member].replace(b'paint_supports="8" ',b'')==raw
 writer.archive_write(target,members)
 report.update(printer=printer,project_sha256=sha(target),intentional_overrides=overrides,layer_ranges_mm=bands,
      normal_layer_height_mm=.24,first_layer_height_mm=.2,normal_wall_loops=2,
      source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [source,source.with_suffix('.step'),Path(__file__),PROFILE,ENC/'enclosure.py',ENC/'_display_wing_interface.py',ENC/'_nameplate_wing_interface.py']},
      paint={'west':int(west.sum()),'east':int(east.sum()),'cad_z_min':345.69,'abs_x_min':100},
      support_policy='Shared tree supports; black base and interface; exterior roof-side transitions blocked; internal functional contacts retained.',
      requested_z_trim_mm=trim,expected_textured_trim_mm=trim-.02)
 (job/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
 ready=job/'ready';ready.mkdir()
 command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0','--outputdir',str(ready),'--export-3mf',stem+'.gcode.3mf',str(target)]
 (job/'slice-command.json').write_text(json.dumps(command,indent=2)+'\n')
 with (ready/'bambu-cli.log').open('w') as log:rc=subprocess.run(command,cwd=ready,stdout=log,stderr=subprocess.STDOUT).returncode
 print(part,'SLICE_EXIT',rc,flush=True)
 return rc

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('part',choices=JOBS)
 raise SystemExit(main(parser.parse_args().part))
