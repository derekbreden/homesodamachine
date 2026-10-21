"""Append one native wiring subassembly, preserving every physical STEP record.

The marked block is replaced on subsequent runs. Component placement uses the
host's existing identity datum; the imported wires are already in machine XYZ.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import re

RECORD=re.compile(r'^#(\d+)\s*=(.*?);[ \t]*\n',re.M|re.S)
REF=re.compile(r'#(\d+)')
BEGIN='/* HSM_INSTALLED_WIRING_BEGIN */\n'
END='/* HSM_INSTALLED_WIRING_END */\n'


def base_document(text):
    if BEGIN in text:
        start=text.index(BEGIN);end=text.index(END,start)+len(END)
        return text[:start]+text[end:]
    return text


def records(text): return {int(m[1]):m[2] for m in RECORD.finditer(text)}
def refs(body): return [int(n) for n in REF.findall(body)]


def root(rec,name=None):
    products=[n for n,b in rec.items() if b.strip().startswith('PRODUCT(') and
              (name is None or b.strip().startswith(f"PRODUCT('{name}',"))]
    product=products[0]
    def parent(n,kind):
        rows=[k for k,b in rec.items() if b.strip().startswith(kind+'(') and n in refs(b)]
        if len(rows)!=1:raise ValueError((n,kind,rows))
        return rows[0]
    formation=parent(product,'PRODUCT_DEFINITION_FORMATION')
    pd=parent(formation,'PRODUCT_DEFINITION')
    pds=parent(pd,'PRODUCT_DEFINITION_SHAPE')
    sdr=parent(pds,'SHAPE_DEFINITION_REPRESENTATION')
    representation=refs(rec[sdr])[1]
    axis=next(n for n in refs(rec[representation]) if rec[n].strip().startswith('AXIS2_PLACEMENT_3D('))
    return pd,representation,axis


def install(host,wire_step,verify_retained=False):
    import flute_payload
    import _mesh_payload
    host,wire_step=Path(host),Path(wire_step)
    base=base_document(host.read_text());original=records(base)
    incoming=records(wire_step.read_text())
    hp,hr,ha=root(original,'enclosure-assembly')
    wp,wr,wa=root(incoming,'installed-wiring')
    offset=max(original)
    remap={n:n+offset for n in incoming}
    added=''.join(f'#{remap[n]} ={REF.sub(lambda m:"#"+str(remap[int(m[1])]),b)};\n' for n,b in incoming.items())
    n=max(remap.values())+1
    added+=(f'#{n} = CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#{n+1},#{n+3});\n'
            f"#{n+1} = ( REPRESENTATION_RELATIONSHIP('','',#{remap[wr]},#{hr}) "
            f'REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(#{n+2}) SHAPE_REPRESENTATION_RELATIONSHIP() );\n'
            f"#{n+2} = ITEM_DEFINED_TRANSFORMATION('','',#{remap[wa]},#{ha});\n"
            f"#{n+3} = PRODUCT_DEFINITION_SHAPE('Placement','Installed wiring',#{n+4});\n"
            f"#{n+4} = NEXT_ASSEMBLY_USAGE_OCCURRENCE('installed-wiring','installed-wiring','',#{hp},#{remap[wp]},$);\n")
    end=base.rfind('ENDSEC;')
    result=base[:end]+BEGIN+added+END+base[end:]
    host.write_text(result)
    mesh=Path(str(host)+'.mesh')
    old=flute_payload.read_payload(mesh)
    retained=[m for m in old if not m['name'].startswith(('wire-','wiring-','terminal-'))]
    def fingerprint(m):
        import numpy as np
        h=hashlib.sha256()
        for k in ('pos','nrm','idx','fac'):
            h.update(np.asarray(m[k],dtype='<f4' if k in ('pos','nrm') else '<u4').tobytes())
        return h.hexdigest()
    before={m['name']:fingerprint(m) for m in retained} if verify_retained else None
    wires=flute_payload.read_payload(Path(str(wire_step)+'.mesh'))
    _mesh_payload.write(retained+wires,str(mesh),src=_mesh_payload.source_digest(host))
    after=({m['name']:fingerprint(m) for m in flute_payload.read_payload(mesh) if m['name'] in before}
           if verify_retained else None)
    return {'schema':1,'scope':'Wiring-only integration; existing physical parts retained',
            'physical_step_sha256':hashlib.sha256(base.encode()).hexdigest(),
            'installed_step_sha256':hashlib.sha256(result.encode()).hexdigest(),
            'physical_records_retained':len(original),'physical_meshes_retained':len(retained),
            'wiring_meshes':len(wires),
            'all_retained_viewer_arrays_identical':before==after if verify_retained else None,
            'wiring_step_sha256':hashlib.sha256(wire_step.read_bytes()).hexdigest()}
