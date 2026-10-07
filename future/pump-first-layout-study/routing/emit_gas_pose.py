from pathlib import Path
import sys,cadquery as cq
ROOT=Path(__file__).resolve().parents[3];S=ROOT/'future/pump-first-layout-study';C=ROOT/'.cache/pump-first-layout/routing';sys.path.insert(0,str(S));import baseline
ns=['wr1110','co2-adapter-regulator-in','co2-adapter-regulator-out'];o=baseline.read(ns)
for n in ns:
 q=o[n].rotate((0,0,0),(0,0,1),90).translate((364.5026,306.05,-54.66058083755))
 q=q.rotate((-50,308.5,281.3),(-49,308.5,281.3),90).rotate((-50,308.5,281.3),(-50,308.5,282.3),75).translate((-38.5,12.5,40.1));q.exportBrep(str(C/('chosen-'+n+'.brep')))
ns=['gasher-co2','co2-adapter-check-in','co2-adapter-check-out'];o=baseline.read(ns)
for n in ns:
 q=o[n].rotate((0,0,0),(0,0,1),-90).translate((-324.1526,319.55,-54.96058083755))
 q=q.rotate((-19,281.1,281),(-19,281.1,282),-90).translate((93,149.9,-15.5));q.exportBrep(str(C/('chosen-'+n+'.brep')))
 print(n,[q.BoundingBox().xmin,q.BoundingBox().ymin,q.BoundingBox().zmin,q.BoundingBox().xmax,q.BoundingBox().ymax,q.BoundingBox().zmax])
