"""Exact pipe plus1 mm portal for lid-rooted PSU fore-left bridge."""
from pathlib import Path
import json,sys,cadquery as cq
ROOT=Path(__file__).resolve().parents[3];S=ROOT/'future/pump-first-layout-study';H=S/'routing';C=ROOT/'.cache/pump-first-layout/routing';sys.path.insert(0,str(H));from curves import *
a=V((-51.5,401,257.6));b=V((-37.81,446.51,269.024));es,meta=s(a,Y,b);q=swept(es,Y,8.35);p=C/'flavor-a-psu-portal.brep';q.exportBrep(str(p));bb=q.BoundingBox();(H/'flavor-a-portal.json').write_text(json.dumps({'brep':str(p.relative_to(ROOT)),'print_owner':'cold-core-lid','target_hosts':['supply-lid-web-1'],'radial_air_mm':1,'bounds':[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax],'scope':'Final A rear return unchanged fromstation401 tofixedrearA446.51; truncatefore-leftbossabove tube andrecutthis portal in supporting ordinary3 mm web.'},indent=2)+'\n');print(p, [bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax],flush=True)
