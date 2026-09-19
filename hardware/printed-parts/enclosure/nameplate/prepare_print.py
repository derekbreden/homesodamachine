"""Prepare a face-down, two-colour PET-GF nameplate and matching receiver coupon.

Writes an editable Bambu project. Optional slicing is local and does not
connect to a printer. Settings start with the saved faucet PET-GF profile.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
import cadquery as cq
import numpy as np
import trimesh
import nameplate as plate

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/"tools").is_dir())
PROFILE = ROOT/"hardware/printed-parts/faucet/faucet-petgf.3mf"
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", CORE)
Q = lambda name: f"{{{CORE}}}{name}"


def meta(parent, key, value):
    ET.SubElement(parent,"metadata",key=key,value=str(value))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(unit=1):
    with zipfile.ZipFile(PROFILE) as source:
        settings = json.loads(source.read("Metadata/project_settings.config"))
        filament = source.read("Metadata/filament_settings_1.config")
    # Both colours use the same PET-GF process and the profile-compatible
    # extruder and remain registered as parts of a single object.
    original = copy.deepcopy(settings)
    for key,value in list(settings.items()):
        if isinstance(value,list) and len(value) in (1, len(original["filament_extruder_variant"])):
            settings[key] = value*2
    settings.update(filament_colour=["#000000","#FFFFFF"], filament_map=["1","1"],
                    filament_map_2=["1","1"], filament_prime_volume=["45","45"],
                    flush_volumes_vector=["140"]*4,
                    flush_volumes_matrix=["0","140","140","0"]*2)
    # Accessible supports preserve the square bearing faces below the catches.
    settings["support_top_z_distance"] = "0.24"
    settings["support_remove_small_overhang"] = "0"
    model = ET.Element(Q("model"),unit="millimeter")
    ET.SubElement(model,Q("metadata"),name="Application").text="BambuStudio-02.08.02.61"
    ET.SubElement(model,Q("metadata"),name="BambuStudio:3mfVersion").text="1"
    resources = ET.SubElement(model,Q("resources")); build = ET.SubElement(model,Q("build"))
    config = ET.Element("config")
    plater = ET.Element("plate")
    for key,value in {"plater_id":1,"plater_name":f"Nameplate {unit:04d} and receiver",
                      "locked":"false","bed_type":settings["curr_bed_type"],
                      "filament_map_mode":"Manual","filament_maps":"1 1",
                      "filament_volume_maps":"0 0"}.items():meta(plater,key,value)
    meshes = []
    body,ink = plate.split(cq.importers.importStep(str(plate.step_path(unit))).val())
    receiver = cq.importers.importStep(str(HERE/"nameplate-receiver.step")).val()
    posed = [plate.print_pose(body),plate.print_pose(ink),
             receiver.rotate((0,0,0),(1,0,0),180)]
    posed[2] = posed[2].translate((0,0,-posed[2].BoundingBox().zmin))
    for object_id,shape,name in zip((1,2,4),posed,("black body","white artwork","receiver")):
        vertices,faces=shape.tessellate(.015,.05)
        mesh=trimesh.Trimesh(vertices=[v.toTuple() for v in vertices],faces=faces,process=True)
        if not mesh.is_watertight or not mesh.is_winding_consistent:
            raise ValueError(f"{name} mesh is not closed and consistently oriented")
        obj=ET.SubElement(resources,Q("object"),id=str(object_id),type="model")
        geometry=ET.SubElement(obj,Q("mesh"));vs=ET.SubElement(geometry,Q("vertices"));ts=ET.SubElement(geometry,Q("triangles"))
        for vertex in mesh.vertices:
            ET.SubElement(vs,Q("vertex"),**dict(zip(("x","y","z"),(f"{v:.8f}" for v in vertex))))
        for triangle in mesh.faces:
            ET.SubElement(ts,Q("triangle"),**dict(zip(("v1","v2","v3"),map(str,triangle))))
        meshes.append({"name":name,"faces":len(mesh.faces),"bounds":mesh.bounds.tolist(),
                       "volume_mm3":float(mesh.volume),"watertight":True})
    for obj_id,parts,name,position in ((3,((1,"black body",1),(2,"white artwork",2)),
                                      f"Nameplate {unit:04d}",(165,125,0)),
                                     (5,((4,"receiver",1),),"Receiver coupon",(165,205,0))):
        obj=ET.SubElement(resources,Q("object"),id=str(obj_id),type="model")
        components=ET.SubElement(obj,Q("components"))
        cfg=ET.SubElement(config,"object",id=str(obj_id));meta(cfg,"name",name);meta(cfg,"extruder",1)
        for child,part_name,extruder in parts:
            ET.SubElement(components,Q("component"),objectid=str(child))
            part=ET.SubElement(cfg,"part",id=str(child),subtype="normal_part")
            meta(part,"name",part_name);meta(part,"extruder",extruder)
            meta(part,"matrix","1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")
        transform="1 0 0 0 1 0 0 0 1 "+" ".join(map(str,position))
        ET.SubElement(build,Q("item"),objectid=str(obj_id),transform=transform,printable="1")
        instance=ET.SubElement(plater,"model_instance")
        for key,value in {"object_id":obj_id,"instance_id":0,"identify_id":2300+obj_id}.items():meta(instance,key,value)
    config.append(plater)
    members={"3D/3dmodel.model":ET.tostring(model,encoding="UTF-8",xml_declaration=True),
             "Metadata/model_settings.config":ET.tostring(config,encoding="UTF-8",xml_declaration=True),
             "Metadata/project_settings.config":json.dumps(settings,indent=2).encode(),
             "Metadata/filament_settings_1.config":filament,
             "Metadata/filament_settings_2.config":filament,
             "_rels/.rels":b'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>''',
             "[Content_Types].xml":b'''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'''}
    out=HERE/f"nameplate-{unit:03d}-petgf.3mf"
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(members.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data)
    report={"project":str(out.relative_to(ROOT)),"project_sha256":sha(out),
            "source_step_sha256":sha(plate.step_path(unit)),
            "receiver_step_sha256":sha(HERE/"nameplate-receiver.step"),
            "profile_source":str(PROFILE.relative_to(ROOT)),"profile_sha256":sha(PROFILE),
            "settings_changes":{k:{"from":original.get(k),"to":v} for k,v in settings.items() if original.get(k)!=v},
            "meshes":meshes,"orientation":"artwork down; receiver in back-top orientation",
            "printer_submission":False,"physical_fit_tested":False}
    out.with_suffix(".print.json").write_text(json.dumps(report,indent=2)+"\n")
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit",type=int,default=1)
    parser.add_argument("--slice-output",type=Path)
    args=parser.parse_args();project=prepare(args.unit);print(project,flush=True)
    if args.slice_output:
        directory=args.slice_output.resolve();directory.mkdir(parents=True,exist_ok=True)
        if any(directory.iterdir()):raise ValueError("Use an empty slice directory")
        with (directory/"bambu-cli.log").open("w") as log:
            result=subprocess.run(["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
                                   "--slice","0","--arrange","0","--orient","0",
                                   "--outputdir",str(directory),str(project)],cwd=directory,
                                   stdout=log,stderr=subprocess.STDOUT)
        print(f"Local slice exit {result.returncode}: {directory}",flush=True)
        raise SystemExit(result.returncode)

if __name__=="__main__":main()
