"""Limit commanded volumetric flow in the rebuilt tip's linear courses."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
import json
from math import dist, floor, pi
from pathlib import Path
import re


PHASE = b'; HSM_PHASE: '
START = b'; start printing object, unique label id: '
STOP = b'; stop printing object, unique label id: '
MODEL_START = b'; MACHINE_START_GCODE_END'
MODEL_END = b'; MACHINE_END_GCODE_START'
MAPPED = {b'tip shoulder entry',b'tip yellow shoulder',b'tip shoulder fade'}
MOTIONS = (b'G0', b'G1', b'G2', b'G3')
NUMBER = rb'[-+]?(?:\d+(?:\.\d*)?|\.\d+)'
WORDS = re.compile(rb'\b([XYZEFS])('+NUMBER+rb')')
F_WORD = re.compile(rb'\bF'+NUMBER)
CAP_LINE = b'; filament_max_volumetric_speed = '
DIAMETER_LINE = b'; filament_diameter = '
TIP_ID = 1902


def config_number(line, prefix):
    return float(line[len(prefix):].strip().split(b',')[0])


def feed_limited(tape):
    source_sha, output_sha = sha256(), sha256()
    counts, delta_seconds = Counter(), Counter()
    min_feed = None
    used_cap, diameter = None, None
    world = (0.,0.,0.)
    offset = (0.,0.,0.)
    original_feed, emitted_feed, speed, extrusion = 0.,0.,1.,1.
    began, absolute, relative_e = False,True,False
    obj, phase = None,b''
    retract_debt, current_e = 0.,0.
    first_changed = None
    worst_output_flow = 0.
    with tape.open('rb') as lines:
        for n,line in enumerate(lines,1):
            source_sha.update(line)
            changed=False
            original_line=line
            if line.startswith(b';'):
                if line.startswith(CAP_LINE):
                    used_cap=config_number(line,CAP_LINE)
                elif line.startswith(DIAMETER_LINE):
                    diameter=config_number(line,DIAMETER_LINE)
                elif line.startswith(MODEL_START):
                    began=True
                    if used_cap is None or diameter is None or used_cap<=0 or diameter<=0:
                        raise ValueError('Print profile is missing physical flow inputs')
                    area=pi*(diameter/2)**2
                    retract_debt=0.
                elif line.startswith(MODEL_END):
                    began=False
                elif line.startswith(START):
                    obj=int(line[len(START):].strip())
                elif line.startswith(STOP):
                    obj=None
                elif line.startswith(PHASE):
                    phase=line[len(PHASE):].strip()
            else:
                code,sep,comment=line.partition(b';')
                words=code.split(None,1)
                if words:
                    cmd=words[0]
                    if cmd==b'G90':
                        absolute=True
                    elif cmd==b'G91':
                        absolute=False
                    elif cmd in (b'M82',b'M83'):
                        relative_e=cmd==b'M83'
                    if cmd in (*MOTIONS,b'G92',b'M220',b'M221'):
                        args={key:float(value) for key,value in WORDS.findall(words[1])} if len(words)>1 else {}
                        if cmd==b'M220':
                            speed=args.get(b'S',100.)/100.
                        elif cmd==b'M221':
                            extrusion=args.get(b'S',100.)/100.
                        elif cmd==b'G92':
                            offset=tuple(x-args.get(k,x-o) for x,o,k in zip(world,offset, (b'X',b'Y',b'Z')))
                            current_e=args.get(b'E',current_e)
                        else:
                            endpoint=(tuple(args.get(k,x-o)+o for x,o,k in zip(world,offset,(b'X',b'Y',b'Z')))
                                      if absolute else tuple(x+args.get(k,0.) for x,k in zip(world,(b'X',b'Y',b'Z'))))
                            delta_e=args.get(b'E',0.) if relative_e else args.get(b'E',current_e)-current_e
                            current_e+=delta_e
                            net=delta_e-retract_debt
                            retract_debt=max(0.,retract_debt-delta_e)
                            original_feed=args.get(b'F',original_feed)
                            emitted_feed=args.get(b'F',emitted_feed)
                            scoped=began and obj==TIP_ID and phase in MAPPED
                            if scoped and net>1e-9 and (world!=endpoint or cmd in (b'G2',b'G3')):
                                if cmd not in (b'G0',b'G1') or b'F' not in args or not relative_e or not absolute:
                                    raise ValueError(f'Mapped deposition must be explicit-feed absolute linear pose: {n}')
                                if min(original_feed,speed,extrusion)<=0:
                                    raise ValueError(f'Invalid deposition feed or flow override: {n}')
                                d=dist(world,endpoint)
                                cap=60*used_cap*d/(area*net*speed*extrusion)
                                if original_feed>cap:
                                    # Rounding downward preserves the cap even for very short rounded moves.
                                    emitted_feed=floor(cap*100)/100
                                    if emitted_feed<=0:
                                        raise ValueError(f'Cannot represent positive capped feed at line {n}')
                                    text=f'F{emitted_feed:.2f}'.encode()
                                    code,changed=F_WORD.subn(text,code)
                                    if changed!=1:
                                        raise ValueError(f'Expected one explicit feed token at line {n}')
                                    line=code+sep+comment
                                    key=phase.decode()
                                    counts[key]+=1
                                    delta_seconds[key]+=60*d/speed*(1./emitted_feed-1./original_feed)
                                    min_feed=emitted_feed if min_feed is None else min(min_feed,emitted_feed)
                                    if first_changed is None:
                                        first_changed=n
                                worst_output_flow=max(
                                    worst_output_flow,extra_flow(area,net,d,emitted_feed,speed,extrusion),
                                )
                            elif began and emitted_feed!=original_feed and (world!=endpoint or delta_e):
                                raise ValueError(f'Capped modal feed would leak to untouched movement at line {n}')
                            world=endpoint
            if changed and F_WORD.sub(b'F',line)!=F_WORD.sub(b'F',original_line):
                raise ValueError(f'Unexpected change outside feed word at line {n}')
            output_sha.update(line)
            yield line
    yield {
        'purpose':__doc__,
        'profile_cap_mm3_s':used_cap,'filament_diameter_mm':diameter,
        'source_gcode_sha256':source_sha.hexdigest(),'gcode_sha256':output_sha.hexdigest(),
        'capped_moves_by_phase':dict(counts),'feed_only_additional_seconds_by_phase':dict(delta_seconds),
        'minimum_capped_feed_mm_min':min_feed,'maximum_nominal_output_flow_mm3_s':worst_output_flow,
        'first_changed_gcode_line':first_changed,
        'identifies_only_explicit_feed_words_in_mapped_linear_tip_deposition':True,
        'prior_nose_and_nontip_gcode_byte_identical':True,
        'scope':'Compares flow at commanded feed and tightened scope from the source header filament settings.',
    }


def extra_flow(area,length_extruded,distance,feed,speed,extrusion):
    return area*length_extruded*feed*speed*extrusion/(60*distance)


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    a=parser.parse_args()
    if a.source.resolve()==a.output.resolve():
        raise ValueError('Preserve original tape')
    tmp=a.output.with_suffix(a.output.suffix+'.making')
    try:
        with tmp.open('wb') as sink:
            for entry in feed_limited(a.source):
                if isinstance(entry,bytes):
                    sink.write(entry)
                else:
                    report=entry
        if report['maximum_nominal_output_flow_mm3_s']>report['profile_cap_mm3_s']+1e-8:
            raise ValueError('An above-cap mapped rate survived')
        tmp.replace(a.output)
        a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    finally:
        tmp.unlink(missing_ok=True)


if __name__=='__main__':
    main()
