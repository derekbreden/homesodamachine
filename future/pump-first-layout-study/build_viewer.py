"""Compose native bay geometry into a rotatable, self-contained study viewer."""
from pathlib import Path
import argparse
import base64
import gzip
import hashlib
import json
import re
import struct

import cadquery as cq
import numpy as np

import baseline
from evidence_binding import content_sha256

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = baseline.CACHE / 'frozen-enclosure-assembly.step.mesh'
MESH_CACHE = ROOT / '.cache/pump-first-layout/viewer-meshes'


def base_name(name):
    return re.sub(r"/\d+$", "", name)


def role(name):
    if name in ("g-ganen-pump",):
        return "pump"
    if name.startswith(("funnel", "elbow-cradle")) or name == "tube-fluid-4":
        return "funnel"
    if name.startswith(("tube-water", "vk-solenoid", "suction-chain", "discharge-chain",
                        "asse", "moisture-plate", "water-split", "flow-regulator")):
        return "water"
    if name.startswith(("tube-co2", "tube-carb", "co2-", "gasher-co2", "wr1110", "digiten", "carb")):
        return "gas"
    if name in ("pcba", "psu", "c14-inlet", "ground-stack", "relay-1", "relay-2") or name.startswith("wago"):
        return "electronics"
    if name.startswith("enclosure-"):
        return "walls"
    if name.startswith("cold-core/") or name.startswith(("display", "grip-cover")):
        return "context"
    if name.startswith(("tube-fluid", "valve-v-", "coil-v-", "tee-y-", "turn-fluid", "step-fluid")):
        return "flavor"
    return "gas"


LABELS = {
    "g-ganen-pump": "G Ganen diaphragm pump",
    "pcba": "Main board", "psu": "12 V power supply", "relay-1": "Compressor relay",
    "relay-2": "Diaphragm-pump relay", "vk-solenoid": "V-K supply valve",
    "asse1022-assembly": "Backflow preventer", "asse-drip-pan": "Sensed drip tray",
    "moisture-plate": "Drip sensor", "water-split": "Water branch",
    "flow-regulator": "Flow regulator", "wr1110": "CO₂ regulator", "gasher-co2": "CO₂ check",
    "digiten-flow": "Carbonated-water flow sensor", "suction-chain": "Pump suction fittings",
    "discharge-chain": "Pump discharge check and fittings", "funnel": "Silicone funnel",
    "funnel-frame": "Sliding funnel frame", "funnel-cover": "Lift-off funnel cover",
    "funnel-drain-stub": "Removable funnel drain seal", "funnel-drain-union": "Funnel drain elbow",
    "elbow-cradle": "Drain-elbow cradle", "c14-inlet": "AC inlet",
    "bulkhead-water": "Rear water inlet", "bulkhead-carb": "Rear carbonated-water outlet",
    "co2-inlet": "Rear CO₂ inlet", "keystone-jack": "Control cable jack",
    "bulkhead-flavor-a": "Rear flavor A outlet", "bulkhead-flavor-b": "Rear flavor B outlet",
    "cold-core/foam-cap-lid-top": "Cold-core top lid", "cold-core/foam-cap-top": "Cold-core cap",
    "enclosure-back-top": "Upper rear shell", "enclosure-front-top": "Upper front shell",
    "rear-roof-hatch": "Roof hatch", "west-junction-platform": "West junction platform",
    "asse-removable-carrier": "Backflow carrier", "suction-chain-anchor": "Pump suction seat",
    "meter-roof-seat-1": "Meter roof seat", "relay-lid-platform": "Relay lid platform",
}


def label(name):
    return LABELS.get(name, name.replace("tube-", "Route · ").replace("-", " "))


def baseline_meshes():
    baseline.frozen_source('enclosure-assembly.step.mesh')
    raw = SOURCE.read_bytes()
    n = struct.unpack("<I", raw[:4])[0]
    header = json.loads(raw[4:4 + n])
    blob = raw[4 + n:]
    for m in header["meshes"]:
        p = np.frombuffer(blob, dtype="<f4", count=m["pos"][1], offset=m["pos"][0]).reshape(-1, 3).copy()
        i = np.frombuffer(blob, dtype="<u4", count=m["idx"][1], offset=m["idx"][0]).copy()
        normals = np.frombuffer(blob, dtype="<f4", count=m["nrm"][1], offset=m["nrm"][0]).reshape(-1, 3).copy()
        yield m["name"], {"p": p, "i": i, "n": normals}


def included(name, m):
    name = base_name(name)
    if name.startswith("cold-core/"):
        return name in ("cold-core/foam-cap-top", "cold-core/foam-cap-lid-top")
    if name.startswith(("enclosure-front-bottom", "enclosure-back-bottom", "enclosure-pump-",
                        "enclosure-tee-", "enclosure-window-", "tee-carrier-spring", "grip-")):
        return False
    if "-word" in name or "nameplate" in name or "tube-collar" in name:
        return False
    bounds = np.array([m["p"].min(axis=0), m["p"].max(axis=0)])
    if bounds[1, 2] < 248 or bounds[1, 1] < 185:
        return name.startswith(("funnel", "elbow-cradle"))
    return True


def mesh_shape(shape):
    vertices, faces = shape.tessellate(0.06, 0.18)
    return {"p": np.array([v.toTuple() for v in vertices]),
            "i": np.array(faces, dtype=np.uint32).reshape(-1)}


def mesh_record(record):
    path=ROOT/record['brep']
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    expected=record.get('sha256')
    if isinstance(expected,dict):expected=expected.get(record['brep'])
    if expected and expected!=digest:
        raise ValueError('Changed viewer native part '+record['brep'])
    cached=MESH_CACHE/('native-006-018-'+digest+'.npz')
    if cached.is_file():
        with np.load(cached,allow_pickle=False) as data:
            return {'p':data['p'].copy(),'i':data['i'].copy()}
    mesh=mesh_shape(cq.Shape.importBrep(str(path)))
    MESH_CACHE.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(cached,**mesh)
    return mesh


def metadata(name, mesh, chosen_role=None, detail=None):
    bounds = [*mesh["p"].min(axis=0), *mesh["p"].max(axis=0)]
    reading = "X {:.1f}–{:.1f}, Y {:.1f}–{:.1f}, Z {:.1f}–{:.1f} mm".format(
        bounds[0], bounds[3], bounds[1], bounds[4], bounds[2], bounds[5])
    return {"mesh": name, "id": name, "role": chosen_role or role(base_name(name)),
            "label": label(base_name(name)), "detail": (detail + " · " if detail else "") + reading}


def pack(meshes, models, normals=True):
    data = {"meshes": {}, "models": models, "target": [0, 286, 301],
            "bounds": [[-120, 92, 233.4], [116, 493, 359]]}
    buf = bytearray()
    for name, mesh in meshes.items():
        row = {}
        for key in ("p", "n", "i"):
            if key == "n" and (not normals or key not in mesh):
                continue
            values = mesh[key]
            if key in ("p", "n"):
                values = np.rint(values * (1000 if key == "p" else 10000)).astype(np.int32)
                delta = np.diff(values.reshape(-1, 3), axis=0, prepend=np.zeros((1, 3), dtype=np.int32)).reshape(-1)
            else:
                delta = np.diff(values.astype(np.int32), prepend=0)
            buf.extend(b"\0" * (-len(buf) % 4))
            row[key] = [len(buf), len(delta)]
            buf.extend(delta.astype("<i4").tobytes())
        data["meshes"][name] = row
    header = json.dumps(data, separators=(",", ":")).encode()
    raw = struct.pack("<I", len(header)) + header
    raw += b"\0" * (-len(raw) % 4) + bytes(buf)
    return base64.b64encode(gzip.compress(raw, 9)).decode()


def compose(fragment):
    styles = """
:root{color-scheme:light dark;--background:light-dark(#fff,#181818);--foreground:light-dark(#222,#eee);--muted-foreground:light-dark(#666,#aaa);--viz-series-1:light-dark(#2f7894,#72b8d2);--viz-series-2:light-dark(#9c6b2d,#dcaf71);--viz-series-3:light-dark(#527d56,#8db391);--viz-series-4:light-dark(#886da2,#bfa5d8);--viz-series-5:light-dark(#976875,#d39cad);--viz-series-6:light-dark(#8a452f,#d79573);--border:light-dark(#ccc,#555);--primary:light-dark(#292929,#eee);--primary-foreground:light-dark(#fff,#222)}
*{box-sizing:border-box}body{margin:0;padding:24px;max-width:1250px;margin-inline:auto;background:var(--background);color:var(--foreground);font:14px/1.5 system-ui,sans-serif}.viz-controls{display:flex;gap:12px 18px;align-items:end;flex-wrap:wrap}.form-label{display:flex;flex-direction:column;gap:4px}.form-select{max-width:100%;font:inherit;padding:5px 25px 5px 8px;border:1px solid var(--border);border-radius:4px;background:var(--background);color:var(--foreground)}.form-check{display:flex;align-items:center;gap:6px;min-height:32px}.btn{font:inherit;padding:6px 12px;border:1px solid var(--border);border-radius:5px;background:var(--background);color:var(--foreground)}.text-small{font-size:12px}.text-muted{color:var(--muted-foreground)}.tabular-nums{font-variant-numeric:tabular-nums}.sr-only{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip:rect(0,0,0,0)}
@media(pointer:coarse){.form-select,.form-check,.btn{min-height:44px}.form-select{font-size:16px}}@media(max-width:580px){body{padding:16px}}
"""
    return '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pump-first bay layout</title><style>' + styles + '</style></head><body>\n' + fragment + '\n</body></html>\n'


def main(inline=None):
    source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [Path(__file__),HERE/'viewer.template.html',HERE/'baseline.py',HERE/'evidence_binding.py']}
    paths=[(folder,HERE/folder/'candidate.json') for folder in ('funnel','pump','routing','structure','mounts','wiring')]
    paths.insert(2,('pump-fluid24',HERE/'pump/fluid24-candidate.json'))
    paths.append(('fluid-mounts',HERE/'mounts/fluid-candidate.json'))
    paths.append(('water5-mounts',HERE/'mounts/water5-hosts.json'))
    paths.append(('tube-hosts',HERE/'routing/tube-hosts.json'))
    paths.append(('body-mounts',HERE/'mounts/body-candidate.json'))
    paths.append(('roof-hatch',HERE/'structure/roof-hatch.json'))
    paths.append(('scene-stock',HERE/'structure/scene-stock.json'))
    paths.append(('psu-clearance',HERE/'routing/psu-surround-feasibility.json'))
    paths.append(('front-handling',HERE/'wiring/front-loom-handling.json'))
    paths.append(('front-closure',HERE/'structure/front-closure-check.json'))
    aft=json.loads((HERE/'funnel/candidate.json').read_text())['aft_extension_mm']
    paths.append(('funnel-tooling',HERE/f'funnel/candidate-aft-{aft:g}-tooling.json'))
    manifests=[];manifest_bytes={};native_parts={}
    for folder,path in paths:
        if not path.exists():continue
        raw=path.read_bytes();manifest=json.loads(raw)
        if folder=='scene-stock':
            semantic=manifest.get('inputs_content_sha256')
            bindings=semantic if semantic is not None else manifest.get('inputs_sha256',{})
            if any(not (HERE/p).is_file() or
                   (content_sha256(json.loads((HERE/p).read_bytes())) if semantic is not None
                    else hashlib.sha256((HERE/p).read_bytes()).hexdigest())!=digest
                   for p,digest in bindings.items()):continue
        manifests.append(manifest)
        manifest_bytes[folder]=(path,raw)
    if len(manifests) < 3:
        raise RuntimeError("The funnel, pump, and bay-routing manifests are required")
    wiring=json.loads(manifest_bytes['wiring'][1]) if 'wiring' in manifest_bytes else {}
    if not wiring or not wiring.get('pass') or len(wiring.get('parts',{}))!=97:
        raise RuntimeError('The complete reviewed 97-part wiring package is required')
    replacements = {name for d in manifests for name in d.get("replacement_names", [])}
    latest = {}
    for folder,(path,raw) in manifest_bytes.items():
        if folder!='front-handling':latest.update(json.loads(raw).get('parts', {}))
    meshes, current, candidate = {}, [], []
    grouped = {}
    for name, mesh in baseline_meshes():
        if not included(name, mesh):
            continue
        grouped.setdefault(base_name(name), []).append(mesh)
    for name, members in grouped.items():
        vertices, normals, indices, count = [], [], [], 0
        for m in members:
            vertices.append(m["p"]); normals.append(m["n"]); indices.append(m["i"] + count); count += len(m["p"])
        mesh = {"p": np.concatenate(vertices), "n": np.concatenate(normals), "i": np.concatenate(indices)}
        key = "current-" + name
        meshes[key] = mesh
        row = metadata(key, mesh, role(name)); row["label"] = label(name); row["id"] = name
        current.append(row)
        if name not in replacements:
            candidate.append(row.copy())
    for name, part in latest.items():
            native_parts[name]={'brep':part['brep'],'sha256':hashlib.sha256((ROOT/part['brep']).read_bytes()).hexdigest()}
            mesh = mesh_record(part)
            key = "candidate-" + name
            meshes[key] = mesh
            chosen_role = part.get('role') or role(name)
            if name=='rear-roof-hatch' or name.startswith(('enclosure-front-','enclosure-back-')):
                chosen_role='walls'
            if name=='digiten-flow' or name.startswith(('tube-carb-','carb-foam-','bulkhead-carb','bulkhead-ring-carb')):
                chosen_role='gas'
            detail=part.get('detail','')
            if name=='psu':
                clearance=next((m for m in manifests if 'barrier_review' in m),{})
                selected=next((p for p in clearance.get('probes',[]) if p['name']=='selected'),{})
                rear=selected.get('wall_plane_air',{}).get('rear_air_mm')
                controller=next((p['supply_air_mm'] for p in selected.get('controller_probes',[])
                                 if p['controller_y_shift_mm']==0),None)
                if rear is not None and controller is not None:
                    detail+=f' · Installation clearance unresolved: {rear:.1f} mm rear air, {controller:.2f} mm to controller; manufacturer surrounding-distance guidance 10 mm'
            for manifest in manifests:
                for rid,route in manifest.get('routes',{}).items():
                    if name=='tube-'+rid and isinstance(route.get('from'),str) and isinstance(route.get('to'),str):
                        detail+=' · '+route['from']+' → '+route['to']
                for rid,route in manifest.get('power_routes',{}).items():
                    if name=='wire-'+rid:
                        detail+=' · '+route['from_key']+' → '+route['to_key']+f" · {route['length_mm']:.1f}mm route"
            row = metadata(key, mesh, chosen_role, detail)
            if 'color_role' in part:row['color_role']=part['color_role']
            row["id"] = name; row["label"] = part.get("label", label(name)); candidate.append(row)
    funnel=json.loads((HERE/'funnel/candidate.json').read_text())
    capacity=funnel['capacity_to_brim_ml'];headroom=funnel['capacity_10mm_below_brim_ml']
    gain=(capacity/455.18178-1)*100
    models = {
        "current": {"parts": current, "readouts": ["455 mL to brim", "Pump length along Y", "Current installed bay"],
                    "detail": "Current native component geometry · X width · +Y aft · Z height · dimensions in millimetres"},
        "candidate": {"parts": candidate, "readouts": [f"{capacity:.0f} mL to brim · +{gain:.1f}%", f"{headroom:.0f} mL at 10 mm headroom", f"{funnel['aft_extension_mm']:g} mm aft extension"],
                      "detail": "Native layout candidate · X width · +Y aft · Z height · Supply installation clearance unresolved · print and installed-fit qualification pending"},
    }
    handling=json.loads(manifest_bytes['front-handling'][1])
    closure=json.loads(manifest_bytes['front-closure'][1])
    if not handling.get('pass') or not closure.get('pass'):
        raise ValueError('Reviewed front closure and parked contact lead are required')
    absent=set(handling['absent_during_closing'])|set(closure['deferred_fore_link_names'])
    factory=[p.copy() for p in candidate if p['id'] not in absent]
    shown={p['id'] for p in factory}
    for name in handling['moving_names']:
        if name in shown or name in absent or name not in handling['native_inputs']:continue
        part=handling['native_inputs'][name];mesh=mesh_record(part)
        if mesh['p'][:,2].max()<248:continue
        native_parts[name]={'brep':part['brep'],'sha256':hashlib.sha256((ROOT/part['brep']).read_bytes()).hexdigest()}
        key='factory-'+name;meshes[key]=mesh
        row=metadata(key,mesh,role(name));row['id']=name;row['label']=label(name)
        factory.append(row)
    for name,part in handling['parts'].items():
        native_parts[name]={'brep':part['brep'],'sha256':hashlib.sha256((ROOT/part['brep']).read_bytes()).hexdigest()}
        key='factory-'+name;mesh=mesh_record(part);meshes[key]=mesh
        row=metadata(key,mesh,'wiring',part.get('detail',''));row['id']=name
        row['label']='Parked contact lead';factory.append(row)
    models['factory']={'parts':factory,'readouts':['102.2 mm closing stroke','Contact lead parked','Display installed afterward'],
        'detail':'Front closure staging · Contact lead travels with the front through the empty display opening · Individual dressing and physical fit qualification pending'}
    tooling=json.loads(manifest_bytes['funnel-tooling'][1]);molds=[]
    for name,title,shift in [('cavity','Cavity mold',-120),('core','Core mold',120)]:
        part=tooling['artifact_parts'][name];mesh=mesh_record(part)
        native_parts['mold-'+name]={'brep':part['brep'],'sha256':hashlib.sha256((ROOT/part['brep']).read_bytes()).hexdigest()}
        key='tooling-'+name;meshes[key]=mesh
        row=metadata(key,mesh,'funnel','Native forming surfaces · Exploded display placement')
        row['id']='mold-'+name;row['label']=title
        turn=-1 if name=='core' else 1;lift=float(mesh['p'][:,2].max()) if name=='core' else 0
        row['matrix']=[1,0,0,0,0,turn,0,0,0,0,turn,0,shift,0,lift,1]
        molds.append(row)
    models['tooling']={'parts':molds,'readouts':[f"{tooling['enclosing_diameter_mm']:.1f} mm enclosing diameter",'211 × 223.7 mm flanges','Core forming face upward'],
        'detail':'Native casting molds · Displayed apart with the core turned over · Casting and physical qualification pending'}
    evidence={"baseline_sha256":baseline.prepare()["sha256"],
              "source_mesh_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "manifests":{folder:hashlib.sha256(raw).hexdigest()for folder,(path,raw)in manifest_bytes.items()},
              "manifest_content_sha256":{str(path.relative_to(ROOT)):content_sha256(json.loads(raw))
                                         for path,raw in manifest_bytes.values()},
              "native_parts":native_parts,"source_inputs":source_inputs}
    evidence['source_drift']=[p for p,h in source_inputs.items()if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    evidence['source_drift'] += [n for n,r in native_parts.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    evidence['manifest_drift']=[folder for folder,(path,raw)in manifest_bytes.items()
                                if content_sha256(json.loads(path.read_bytes()))!=content_sha256(json.loads(raw))]
    evidence['pass']=not evidence['source_drift'] and not evidence['manifest_drift']
    if not evidence['pass']:raise ValueError('Viewer inputs changed during native composition')
    (HERE/'viewer-source.json').write_text(json.dumps(evidence,indent=2)+'\n')
    template = (HERE / "viewer.template.html").read_text()
    full = template.replace("__MODEL_DATA__", pack(meshes, models))
    (HERE / "index.html").write_text(compose(full))
    if inline:
        # The bay conversation view keeps all component surfaces; the full native shell
        # and cap-support detail remains in the companion viewer.
        compact_models = json.loads(json.dumps(models))
        omit = {n for n in meshes if any(n.endswith(x) for x in
                ("enclosure-front-top", "enclosure-back-top", "cold-core/foam-cap-top"))}
        for model in compact_models.values():
            model["parts"] = [p for p in model["parts"] if p["mesh"] not in omit]
        compact = template.replace("__MODEL_DATA__", pack({k: v for k, v in meshes.items() if k not in omit}, compact_models, normals=False))
        if len(compact.encode()) >= 1_000_000:
            raise RuntimeError(f"Inline native component payload is {len(compact.encode())} bytes; use rendered views")
        inline.parent.mkdir(parents=True, exist_ok=True); inline.write_text(compact)
    print(json.dumps({"full_viewer": str(HERE / "index.html"), "parts_current": len(current),
                      "parts_candidate": len(candidate), "full_bytes": len(full.encode()),
                      "source_mesh_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inline", type=Path)
    main(parser.parse_args().inline)
