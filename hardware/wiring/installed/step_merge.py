"""Append the installed wiring subassembly, preserving every physical STEP record.

The marked block is replaced on subsequent runs. Component placement uses the
host's existing identity datum; the imported wires are already in machine XYZ.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import struct

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


def _wiring(name):
    return name.startswith(('wire-','wiring-','terminal-'))


def _payload_merge(host,wires,src):
    """Append the existing array byte ranges without expanding meshes into Python lists."""
    def header(stream):
        size=struct.unpack('<I',stream.read(4))[0]
        return json.loads(stream.read(size)),4+size
    temporary=host.with_name(f'.{host.name}.{os.getpid()}.tmp')
    with host.open('rb') as a,wires.open('rb') as b:
        before,ab=header(a);incoming,bb=header(b)
        meshes=[];copies=[];offset=0
        retained=[m for m in before['meshes'] if not _wiring(m['name'])]
        for stream,blob,rows in ((a,ab,retained),(b,bb,incoming['meshes'])):
            for original in rows:
                row=dict(original)
                for key in ('pos','nrm','idx','fac','col','uv'):
                    if key not in row:continue
                    start,count=row[key];size=count*4
                    row[key]=[offset,count];offset+=size
                    copies.append((stream,blob+start,size))
                meshes.append(row)
        result={**before,'meshes':meshes,'src':src}
        encoded=json.dumps(result,separators=(',',':')).encode()
        encoded+=b' '*(-len(encoded)%4)
        with temporary.open('wb') as out:
            out.write(struct.pack('<I',len(encoded)));out.write(encoded)
            for stream,start,size in copies:
                stream.seek(start)
                while size:
                    block=stream.read(min(size,1024*1024))
                    if not block:raise EOFError('Truncated mesh payload array')
                    out.write(block);size-=len(block)
    temporary.replace(host)
    return len(retained),len(incoming['meshes'])


def _digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def install(host,wire_step,verify_retained=False,*,wire_model=None):
    """Install the STEP/payload; a supplied fine wiring model stays standalone."""
    import _mesh_payload
    if wire_model is None or verify_retained:
        import flute_payload
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
    old=flute_payload.read_payload(mesh) if wire_model is None or verify_retained else None
    retained=[m for m in old if not _wiring(m['name'])] if old is not None else None
    def fingerprint(m):
        import numpy as np
        h=hashlib.sha256()
        for k in ('pos','nrm','idx','fac'):
            h.update(np.asarray(m[k],dtype='<f4' if k in ('pos','nrm') else '<u4').tobytes())
        return h.hexdigest()
    before={m['name']:fingerprint(m) for m in retained} if verify_retained else None
    if wire_model is None:
        wires=flute_payload.read_payload(Path(str(wire_step)+'.mesh'))
        _mesh_payload.write(retained+wires,str(mesh),src=_mesh_payload.source_digest(host))
        counts=len(retained),len(wires)
        model=None
    else:
        counts=_payload_merge(mesh,Path(str(wire_step)+'.mesh'),_mesh_payload.source_digest(host))
        model={'path':str(wire_model),'sha256':_digest(wire_model)}
    after=({m['name']:fingerprint(m) for m in flute_payload.read_payload(mesh) if m['name'] in before}
           if verify_retained else None)
    return {'schema':1,'scope':'Wiring-only integration; existing physical parts retained',
            'physical_step_sha256':hashlib.sha256(base.encode()).hexdigest(),
            'installed_step_sha256':hashlib.sha256(result.encode()).hexdigest(),
            'physical_records_retained':len(original),'physical_meshes_retained':counts[0],
            'wiring_meshes':counts[1],
            'all_retained_viewer_arrays_identical':before==after if verify_retained else None,
            'wiring_step_sha256':hashlib.sha256(wire_step.read_bytes()).hexdigest(),
            **({'wiring_fine_model':model} if model is not None else {})}
