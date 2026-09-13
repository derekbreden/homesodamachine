#!/usr/bin/env python3
"""Compose the cylinder, power, fill and pour pictures for the printed sheet."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HARDWARE=ROOT/'hardware'
OUT=HARDWARE/'quickstart-codex/out'
ART=HARDWARE/'quickstart-codex/art'
os.environ.setdefault('HSM_NO_BUILD_LOCK','1')
sys.path[:0]=[str(HARDWARE/'install-guide'),str(HARDWARE/'quickstart'),str(HARDWARE/'scripts')]
import cadquery as cq
import _install_art as install
import _cad_art as original

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

reg=load(HARDWARE/'reference/wellbom-regulator/wellbom_regulator.py','quickstart_regulator')
SILVER=cq.Color(.63,.66,.70)
BLACK=cq.Color(.07,.075,.085)
GLASS=cq.Color(.58,.70,.74,.30)
DRINK=cq.Color(.20,.07,.025,1.0)
jobs=[]

def stage(name,assembly,cam,target,span,size='1600x1500',flutes=False):
    path=OUT/f'{name}.step'
    original._export_colored(assembly,path,mesh=True)
    if flutes: install._graft_flutes(path)
    jobs.append(dict(step=str(path.relative_to(HARDWARE)),out=str(ART/f'{name}.png'),
        cam=cam,target=target,span=span,size=size,up=(0,0,1),bg='#f2eee8',
        transparent=True,solid=True,ortho=True,trim=False,ground=False,fog=False))
    print('Staged',name,flush=True)

def cylinder(gap=0):
    a=cq.Assembly(name='cylinder-connection')
    for child in reg.build_assembly().children:a.add(child)
    cx=-115.0
    body=(cq.Workplane('XZ',origin=(cx,0,-468))
          .moveTo(0,0).lineTo(54,0).threePointArc((64,6),(66.5,17))
          .lineTo(66.5,366).threePointArc((60,400),(19,424))
          .lineTo(16,424).lineTo(16,441).lineTo(0,441).close().revolve())
    a.add(body,name='cylinder-body',color=SILVER)
    a.add(install._cyl(cx,0,-29,24,43),name='cylinder-valve',color=install.BRASS)
    a.add(install._cyl(cx,0,14,8,12),name='cylinder-valve-stem',color=install.BRASS)
    a.add(install._cyl(cx,0,25,48,8),name='cylinder-handwheel',color=BLACK)
    a.add(install._cyl(cx,0,-1,18,115-reg.INLET_NUT_FACE,axis='X'),name='valve-outlet',color=install.BRASS)
    tip,_=reg.outlet();nut_len=14
    a.add(install._hex(tip[0],tip[1],tip[2]-nut_len-gap,reg.OUTLET_HEX_FLATS,nut_len),name='tether-nut',color=install.BRASS)
    a.add(install._bend([(0,0,tip[2]-nut_len-gap),(0,0,tip[2]-69-gap),(160,0,tip[2]-69-gap)],radius=28),name='red-tether',color=install.RED_TUBE)
    return a

def fill(gap=0):
    source=install.s_bottle_in_funnel();a=cq.Assembly(name='fill')
    exterior={'funnel','nameplate','nameplate-ink','enclosure-front-top','enclosure-front-bottom',
              'enclosure-back-top','enclosure-back-bottom','front-display','front-display-screen',
              'display-cover','enclosure-display','enclosure-display-screen'}
    for child in source.children:
        if child.name.startswith('bottle-'):
            a.add(child.obj.translate((0,0,gap)),name=child.name,color=child.color)
        elif child.name in exterior or 'display' in child.name:
            a.add(child)
    return a

def pour(pressed):
    fa=original._load_faucet_module();parts=original._children_by_name(fa.build_assembly())
    rest,held=original._physical_levers(fa)
    a=cq.Assembly(name='first-pour')
    names=['westbrass','soda_faucet_tube','tpu_o_ring','flavor_tube_pos_x','flavor_tube_neg_x','lever',
        'above_counter_plate','above_counter_gasket','shell_base','shell_tip','faucet-display-cover',
        'faucet_display','faucet_display_screen']
    for name in names:
        child=parts[name];obj=(held if pressed else rest) if name=='lever' else child.obj
        if name in {'westbrass','flavor_tube_pos_x','flavor_tube_neg_x'}:obj=original._clip_z(obj,fa.countertop_top_z,260)
        a.add(obj,name=name,color=child.color)
    a.add(install._box(-120,-280,-14,240,340,14),name='countertop',color=install.STONE)
    _,tip_vector=fa._tip_centerline_world()
    tip=tip_vector.toTuple()
    gx,gy=tip[0],tip[1]
    glass=(cq.Workplane('XY').circle(31).workplane(offset=104).circle(37).loft()
        .cut(cq.Workplane('XY').workplane(offset=4).circle(28).workplane(offset=101).circle(34.2).loft()))
    a.add(glass.translate((gx,gy,0)),name='glass',color=GLASS)
    rim=cq.Workplane('XY').workplane(offset=103.4).circle(37).circle(34.1).extrude(.7)
    a.add(rim.translate((gx,gy,0)),name='glass-rim',color=cq.Color(.80,.87,.90))
    if pressed:
        drink=cq.Workplane('XY').workplane(offset=5).circle(27.7).workplane(offset=75).circle(32.1).loft()
        a.add(drink.translate((gx,gy,0)),name='drink',color=DRINK)
    (OUT/'pour-points.json').write_text(json.dumps({'tip':list(tip),'lever':[0,fa.lever_pivot_y,fa.lever_pivot_z]}))
    return a

def render():
    """Draw these snapshots with a clear glass, using a private copy of the renderer."""
    source=original.RENDERER.read_text()
    source=source.replace('from "./browser.js"',f'from {(original.RENDERER.parent/"browser.js").as_uri()!r}')
    source=source.replace('from "../../web/server.js"',f'from {(ROOT/"web/server.js").as_uri()!r}')
    source=source.replace('import sharp from "sharp";',f'import {{ createRequire }} from "module"; const sharp = createRequire({str(original.RENDERER)!r})("sharp");')
    source=source.replace('const REPO_ROOT = path.resolve(__dirname, "..", "..");',f'const REPO_ROOT = {str(ROOT)!r};')
    source=source.replace('renderer.render(scene, cam);', '''
    currentGroup.traverse((part) => {
      if (part.name === "glass") {
        part.material = new THREE.MeshPhysicalMaterial({
          color: "#c9e0e5", opacity: 0.10, transparent: true,
          roughness: 0.15, metalness: 0.05, depthWrite: false,
          side: THREE.DoubleSide,
        });
        part.renderOrder = 10;
      } else if (part.name === "drink") {
        part.material = new THREE.MeshPhongMaterial({
          color: "#351507", specular: "#251408", shininess: 35,
        });
      }
    });
    renderer.render(scene, cam);''')
    renderer=OUT/'render-scenes.mjs';renderer.write_text(source)
    (OUT/'scenes.json').write_text(json.dumps(jobs,indent=2))
    subprocess.run(['node',str(renderer),'--jobs',str(OUT/'scenes.json')],cwd=ROOT,check=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True);ART.mkdir(exist_ok=True)
    wanted=set(sys.argv[1:])
    if not wanted or 'gas' in wanted:
        stage('co2-ready',cylinder(29),(.12,1,.15),(-34,0,-58),150)
        stage('co2-connected',cylinder(),(.12,1,.15),(-34,0,-58),150)
    if not wanted or 'power' in wanted:
        paths=original._build_connection_steps(OUT)
        connected=cq.Assembly.load(str(paths['connect-rear-connected']))
        for label,gap in [('power-ready',65),('power-connected',.5)]:
            a=cq.Assembly(name=label)
            for child in connected.children:a.add(child)
            a.add(install._c13_cordset(gap),name='cordset',color=install.CORDSET)
            x,z=install.C14_STATION
            stage(label,a,(-.85,1,.25),(x-8,install.REAR_FACE_Y+34,z-16),64,size='1800x1300',flutes=True)
    if not wanted or 'fill' in wanted:
        for name,gap in [('fill-ready',85),('fill-seated',0)]:
            stage(name,fill(gap),(.65,-1,.50),(0,140,465),265,flutes=True)
    if not wanted or 'pour' in wanted:
        for name,pressed in [('pour-ready',False),('pour-running',True)]:
            stage(name,pour(pressed),(1,-1.8,.67),(0,-78,119),140)
    render()

if __name__=='__main__':main()
