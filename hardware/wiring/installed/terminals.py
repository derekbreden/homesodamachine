"""Electrical attachments resolved against the populated machine.

Valve attachments come from the actual separate metal spades. Board pins come
from the fabricated circuit JSON, carried through the board's native pose.
Representative device envelopes retain explicit nominal/unlocated status.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import math
from pathlib import Path
import sys

from .model import Terminal, add, mul, sub, unit

ROOT = Path(__file__).resolve().parents[3]
HW = ROOT / "hardware"


def bounds(shape):
    b = shape.BoundingBox()
    return ((b.xmin, b.ymin, b.zmin), (b.xmax, b.ymax, b.zmax))


def centre(shape):
    lo, hi = bounds(shape)
    return tuple((a+b)/2 for a, b in zip(lo, hi))


def carbonator_bond_datums(ea):
    """Carry the shared steel contact and crimp mouth with the cold core."""
    import above_core as layout
    from _foam_cap import top_cap_height
    bond = ea._cca._V._bond
    d = bond.datums(ea._cca._V.top_plate_z[1])
    def world(point):
        x, y, z = point
        return layout.point(layout.cap_lid_pose(),
                            (-x, -y, z - ea._cci.foam_shell_outer_height
                             - top_cap_height))
    def axis(direction):
        return layout.vector(layout.cap_lid_pose()['rotation'],
                             (-direction[0], -direction[1], direction[2]))
    return {**d, 'contact_point_mm': world(d['contact_point_mm']),
            'contact_outward': axis(d['contact_outward']),
            'wire_exit_mm': world(d['wire_exit_mm']),
            'wire_outward': axis(d['wire_outward'])}


class Attachments:
    def __init__(self, scene, ea):
        self.scene = {n.replace("_", "-"): s for n, (s, _c) in scene.items()
                      if not n.startswith(("wire-", "wiring-", "terminal-"))}
        self.ea = ea
        self.terminals = {}
        self.frames = {}
        self.frame_checks = {}
        self.parts = {}
        self.fuse_leads = {}

    def part(self, name):
        if name in self.scene:
            return self.scene[name]
        return self.scene["cold-core/"+name]

    def put(self, id, part, point, outward, kind, basis, status="modeled", pin=""):
        t = Terminal(id, part, tuple(float(x) for x in point), tuple(float(x) for x in unit(outward)),
                     kind, basis, status, str(pin))
        self.terminals[id] = t
        return t

    def station(self,spec):
        if 'point_mm' in spec:
            p=spec['point_mm']
        elif 'passage' in spec:
            p=self.passages[spec['passage']]['points_mm'][spec.get('end',0)]
        elif 'terminal' in spec:
            p=self.terminals[spec['terminal']].point
        else:
            lo,hi=bounds(self.part(spec['part']))
            p=tuple(lo[i]+(hi[i]-lo[i])*spec.get('fraction',[.5,.5,.5])[i] for i in range(3))
        return add(p,spec.get('offset',[0,0,0]))

    def frame(self, part, reference, turns=()):
        """Production native poses for the above-core parts and junctions.

        Unmoved reference families retain their established native rotation and
        measured translation. Bounds verify an explicit pose; they never infer
        the rotation of a relocated board, valve, PSU or relay.
        """
        from _cadq_export import import_step
        import cadquery as cq
        key = (part, str(reference), str(turns))
        if key in self.frames:
            return self.frames[key]
        ref = import_step(str(reference)).val()
        import above_core as layout
        import above_core_wiring as junctions
        explicit = junctions.frame(part)
        if explicit is None:
            explicit = layout.specification()['parts'].get(part)
        if explicit is not None:
            placed = ref.moved(layout.frame_location(explicit))
            a, b = bounds(placed); c, d = bounds(self.part(part))
            self.frame_checks[part] = {
                'reference': str(Path(reference).relative_to(ROOT)),
                'basis': 'Explicit production native frame',
                'rotation': explicit['rotation'],
                'translation_mm': explicit['translation_mm'],
                'maximum_extent_residual_mm': max(abs((b[i]-a[i])-(d[i]-c[i])) for i in range(3)),
                'maximum_bounds_residual_mm': max(abs(x-y) for p,q in ((a,c),(b,d)) for x,y in zip(p,q)),
            }
            def carry(p, axis):
                return layout.point(explicit, p), layout.vector(explicit['rotation'], axis)
            self.frames[key] = carry
            return carry
        turned = ref
        basis = [cq.Vector(1, 0, 0), cq.Vector(0, 1, 0), cq.Vector(0, 0, 1)]
        for axis, deg in turns:
            turned = turned.rotate((0,0,0), axis, deg)
            # A rotated point on a unit vector gives the same rotation without
            # depending on the source shape's local location representation.
            from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf
            tr = gp_Trsf(); tr.SetRotation(gp_Ax1(gp_Pnt(0,0,0), gp_Dir(*axis)), math.radians(deg))
            basis = [cq.Vector(v.wrapped.Transformed(tr)) for v in basis]
        shift = sub(centre(self.part(part)), centre(turned))
        a, b = bounds(turned); c, d = bounds(self.part(part))
        residual = max(abs((b[i]-a[i])-(d[i]-c[i])) for i in range(3))
        self.frame_checks[part] = {"reference": str(Path(reference).relative_to(ROOT)),
                                  "turns": turns, "translation_mm": shift,
                                  "maximum_extent_residual_mm": residual}
        def rotate(p):
            return tuple(sum(basis[j].toTuple()[i]*p[j] for j in range(3)) for i in range(3))
        def carry(p, axis):
            return add(rotate(p), shift), rotate(axis)
        self.frames[key] = carry
        return carry

    def resolve(self):
        self.board(); self.valves(); self.wagos(); self.power(); self.pump_motors()
        self.sensors(); self.boundaries()
        self.cable_passages()
        return self.terminals

    def cable_passages(self):
        """Cable guide mouths and exact printed corridor in the world frame."""
        import above_core as layout
        import _above_core_mounts
        face = layout.specification()['cap_face_z_mm']
        self.passages = {}
        for name, xy in self.ea._cci.cap_cable_conduits.items():
            corridor = _above_core_mounts.cable_guide_points(name)
            lower = corridor['points_mm'][0]
            floor = (lower[0],lower[1],lower[2]+1.)
            upper = layout.point(layout.cap_lid_pose(), (*xy, self.ea._foam.lid_total_height))
            self.passages[name] = {
                'points_mm': [(upper[0],upper[1],face+1.6),
                              (floor[0],floor[1],floor[2]-1.6)],
                'upper_mouth_mm': upper,
                'lower_entry_mm': floor,
                'corridor_points_mm': corridor['points_mm'],
                'corridor_bend_radius_mm': corridor['bend_radius_mm'],
                'bore_diameter_mm': 2*self.ea._cci.cap_conduit_bore_radius,
                'basis': 'Native top-cap cable conduit, carried into the installed frame',
            }
        import _box_spec
        enc = self.ea._enc
        box, _bounds = _box_spec.read(
            enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate),
            path=HW / 'manifold-layout/enclosure-box.json')
        self.passages.update(enc._fixed_pump_mount.wiring_passages(enc, box))

    def board(self):
        path=Path(__file__).with_name('connector-map.json')
        data=json.loads(path.read_text())
        self.pcb_reference=data['source_sha256']
        carry = self.frame("pcba", self.ea.PCBA_STEP, self.ea.PCBA_TURN)
        # The native mechanical board is centred on its outline and has its own
        # 1.6 mm top datum. Circuit XY coordinates retain their physical origin.
        pcb_centre = self.ea._pcba._centre
        top = self.ea._pcba._thickness
        for owner,entry in data['connectors'].items():
            if owner=='J8':continue
            for pin in entry['pins']:
                x,y=pin['xy_mm'];label=pin['label']
                local=(x-pcb_centre[0],y-pcb_centre[1],top+9.8)
                direction=(0,0,1)
                basis='connector-map.json fabricated physical pad and native board pose; JST XH nominal 9.8 mm assembled height'
                if owner=='J10':
                    box=entry['component_glb_bounds_mm']
                    local=(box[1]-pcb_centre[0],y-pcb_centre[1],top+(box[5]-.7)*.4)
                    direction=(1,0,0)
                    basis='KF301 native component envelope, +X side wire entry; mouth height nominal, separate from screw axis'
                point, axis = carry(local, direction)
                self.put(owner+'.'+label, 'pcba', point, axis,
                         'screw' if owner=='J10' else 'JST-XH',basis,'nominal',pin['number'])

    def valves(self):
        for letter in 'ABCDEFGHIJK':
            name = ('vk-solenoid' if letter=='K' else
                    'valve-v-'+letter.lower() if letter in 'AB' else
                    'coil-v-'+letter.lower())
            body = self.part(name)
            tabs = []
            for s in body.Solids():
                lo, hi = bounds(s); dims=sorted(b-a for a,b in zip(lo,hi))
                if abs(dims[0]-.8)<.02 and abs(dims[1]-6.3)<.05 and abs(dims[2]-8.6)<.05:
                    tabs.append(s)
            # V-K is a merged reference valve; recover its two thin tab faces
            # through the same reference frame when they aren't separate solids.
            if len(tabs)==2:
                bulk=max(body.Solids(), key=lambda s:s.Volume()); root=centre(bulk)
                ends=[]
                for tab in tabs:
                    lo,hi=bounds(tab); axis=max(range(3),key=lambda i:hi[i]-lo[i])
                    sign=1 if centre(tab)[axis]>root[axis] else -1
                    p=list(centre(tab)); p[axis]=hi[axis] if sign>0 else lo[axis]
                    a=[0.,0.,0.];a[axis]=float(sign);ends.append((tuple(p),tuple(a)))
                ends.sort(key=lambda e:abs(e[0][0]))
                for label,(point,axis) in zip(('positive','negative'),ends):
                    if letter in 'GJ':
                        # The disconnect engages the tab below its free tip and
                        # dresses aft in the inter-tier space. No rigid boot box
                        # or immutable straight-tab approach is imposed here.
                        point=(point[0],point[1],point[2]-4.3)
                        axis=(0.,1.,0.)
                    self.put('V-'+letter+'.'+label,name,point,axis,'female-disconnect',
                             ('Native tab engagement region; proposed aft wire exit with flexible tab/disconnect' if letter in 'GJ' else
                              'Actual native 6.3 × 0.8 mm metal tab, tip on its long axis; inboard tab assigned positive'),
                             'nominal' if letter in 'GJ' else 'modeled')
            elif letter in 'ABK':
                carry=self.frame(name, self.ea.ml.VALVE_STEP if hasattr(self.ea.ml,'VALVE_STEP') else
                                 HW/'reference/beduan-solenoid/beduan-solenoid.step', ())
                entries=[carry((sx*7.45,27.1,52.2),(0,1,0)) for sx in (-1,1)]
                entries.sort(key=lambda e:abs(e[0][0]))
                for label,(p,a) in zip(('positive','negative'),entries):
                    self.put('V-'+letter+'.'+label,name,p,a,'female-disconnect',
                             'Native reference tab through explicit production valve pose')
            else:
                raise ValueError(f'{name}: expected two separate metal spades, found {len(tabs)}')

    def wagos(self):
        ea=self.ea
        import above_core_wiring as junctions
        sizes={n:row['size'] for n,row in junctions.placements().items()
               if n.startswith('wago-')}
        dims={'413':(18.8,18.6,8.4,3,1),'415':(30.,18.6,8.4,5,1),'420':(29.8,18.3,15.8,10,2)}
        for name,size in sizes.items():
            carry=self.frame(name,ea.wago_step(size),ea.WAGO_TURN_WEST if 'reeds-' in name or name=='wago-sensors' else ea.WAGO_TURN)
            w,d,h,n,rows=dims[size];cols=n//rows
            for i in range(n):
                local=(-w/2+w/cols*(i%cols+.5),d/2,h*(i//cols+.5)/rows)
                p,a=carry(local,(0,1,0))
                self.put(f'{name}.{i+1}',name,p,a,'WAGO-port',
                         'Distinct nominal port centres within native WAGO envelope; bores unmodelled','nominal',i+1)

    def power(self):
        ea=self.ea
        psu=self.frame('psu',ea.PSU_STEP,ea.PSU_TURN)
        for label,x,side in (('L',-4.,1),('N',4.,1),('V12',-4.,-1),('GND',4.,-1)):
            p,a=psu((x,side*52.5,10.2),(0,side,0))
            self.put('psu.'+label,'psu',p,a,'screw','Representative terminal block; pole pitch and wire entry nominal','nominal')
        for index,turn in ((1,ea.RELAY_TURN),(2,ea.RELAY2_TURN)):
            name=f'relay-{index}'; carry=self.frame(name,ea.RELAY_STEP,turn)
            for label,y in (('COM',-5.),('NO',0.),('NC',5.)):
                p,a=carry((25.,y,11.5),(0,0,1))
                self.put(name+'.'+label,name,p,a,'screw','Representative relay contact block; pole order nominal','nominal')
            for label,y in (('V5',-2.54),('GND',0.),('IN',2.54)):
                p,a=carry((-26.,y,11.5),(0,0,1))
                self.put(name+'.'+label,name,p,a,'logic-header','Representative VCC/GND/IN header; lead termination unlocated','nominal')
        carry=self.frame('c14-inlet',ea.C14_STEP,())
        for label,x,z in (('L',-6.7,2.45),('PE',.35,-2.6),('N',7.1,2.65)):
            p,a=carry((x,-25.,z),(0,-1,0))
            self.put('c14.'+label,'c14-inlet',p,a,'solder-tab','Scanned tab positions; L/N assignment awaits physical moulded marks','nominal')
        carry=self.frame('thermal-fuse',HW/'reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step',ea.FUSE_TURN)
        from .bundles import definitions
        leads=definitions()['compressor-cord']['fuse_leads']
        for label,sign in (('in',-1),('out',1)):
            p,a=carry((sign*(ea._fuse.BODY_L/2+ea._fuse.LEAD_STUB),0,ea._fuse.AXIS_Z),(sign,0,0))
            lead=leads[label]
            points=[add(p,offset) for offset in lead['offsets_mm']]
            self.fuse_leads[label]={**lead,'points_mm':points,'native_stub_tip_mm':p,
                                   'lead_diameter_mm':ea._fuse.LEAD_D,
                                   'native_straight_mm':ea._fuse.LEAD_STUB,
                                   'available_lead_mm':ea._fuse.LEAD_LONG if label=='in' else ea._fuse.LEAD_SHORT}
            self.put('fuse.'+label,'thermal-fuse',points[-1],(1,0,0),'insulated-splice',
                     'Proposed splice beyond dressed SF76E lead; native first 3 mm remain straight','nominal')
        carry=self.frame('ground-stack',ea.GND_STACK_STEP,ea.RELAY_TURN)
        gnd=ea._gnd;mouth=gnd.eye_od/2-1+gnd.barrel_len
        for i,(label,bearing) in enumerate(gnd.RINGS):
            angle=math.radians(bearing)
            p,a=carry((mouth*math.cos(angle),mouth*math.sin(angle),i*gnd.tongue_t+gnd.barrel_d/2),
                      (math.cos(angle),math.sin(angle),0))
            self.put('ground.'+label,'ground-stack',p,a,'ring-barrel',
                     'Native crimp-barrel free end; compressor uses the downward-facing lug',pin=i+1)

    def pump_motors(self):
        for bank in ('a','b'):
            name=f'pump-{bank}-motor'; lo,hi=bounds(self.part(name)); c=centre(self.part(name))
            for i,dx in ((1,-4.),(2,4.)):
                self.put(f'pump-{bank}.{i}',name,(c[0]+dx,c[1],hi[2]),(0,0,1),'female-disconnect',
                         'Faston receptacle on the motor tab, at the native rear-cap plane inside the integral mount terminal room; actual motor tabs unlocated','unlocated',i)

    def sensors(self):
        ea=self.ea
        carry=self.frame('mq6-sensor',ea.MQ6_STEP,ea.MQ6_TURN)
        for i in range(4):
            p,a=carry((-13.,(i-1.5)*2.54,0),(0,0,-1))
            self.put(f'mq6.{i+1}','mq6-sensor',p,a,'pin-header','Native header tips; VCC/GND/DO/AO assignment follows module description','nominal',i+1)
        meter=ea._digiten
        carry=self.frame('digiten-flow',ea.DIGITEN_STEP,ea.DIGITEN_TURN)
        # All three leave the observed wire boss; fanout starts outside that boss.
        local,outward=meter.wire_exit()
        for i,label in enumerate(('V','PULSE','GND')):
            p,a=carry((local[0]+(i-1)*1.8,local[1],local[2]),outward)
            self.put('flow.'+label,'digiten-flow',p,a,'factory-lead','Observed wire-exit boss; individual lead spacing nominal','nominal')
        for label,name in (('carbonator','probe-carbonator-ds18b20'),('coil','probe-coil-ds18s20')):
            lo,hi=bounds(self.part(name)); c=centre(self.part(name))
            tank=centre(self.part('carbonator-tube'))
            radial=unit((c[0]-tank[0],c[1]-tank[1],0.))
            joint=add((c[0],c[1],lo[2]),mul(radial,7.))
            tangent=(-radial[1],radial[0],0.)
            for i,pin in enumerate(('V','DATA','GND')):
                # These are harness splice positions, not the package's pin
                # order. Dress the bare leads to the arriving ribbon row.
                row_sign=-1. if label=='coil' else 1.
                self.put('temp-'+label+'.'+pin,'cold-core/'+name,add(joint,mul(tangent,row_sign*(i-1)*1.85)),radial,
                         'TO-92-lead','Proposed insulated solder joints 7 mm radially outside the probe, with a tangential 1.85 mm lead row; bare lead dressing and pin assignment nominal','nominal')
        for bank,count in (('a',4),('b',4),('carb',2)):
            for i in range(1,count+1):
                name=f'reed-{bank}-{i}';lo,hi=bounds(self.part(name));c=centre(self.part(name))
                for label,z,axis in (('signal',hi[2],(0,0,1)),('GND',lo[2],(0,0,-1))):
                    point=(c[0],c[1],z)
                    basis='Reed capture-envelope ends; soldered lead extensions and insulation are proposed'
                    if bank=='carb':
                        tank=centre(self.part('carbonator-tube'))
                        radial=unit((c[0]-tank[0],c[1]-tank[1],0.))
                        tangent=(-radial[1],radial[0],0.)
                        point=add((c[0],c[1],z),mul(radial,8.));axis=radial
                        basis='Proposed insulated splice outside the coil; the 14 mm reed capture envelope includes lead/tape room, not measured glass ends'
                        if label=='GND':
                            point=add(add((c[0],c[1],z-3.),mul(radial,8.)),mul(tangent,2.8))
                            axis=(0,0,1)
                            basis='Proposed insulated tap on the continuous carbonator-reed common, 2.8 mm beside the signal splice row and 3 mm below its capture envelope; local bare lead dressing nominal'
                    elif label=='GND':
                        # One continuous common spine, with a short reed lead
                        # bent into each insulated tap beside the glass.
                        point=(c[0]-2.8,c[1],z-3.)
                        axis=(0,0,1)
                        basis='Proposed insulated tap on the continuous common spine, 2.8 mm along the channel width beside the reed axis and 3 mm below its capture envelope; local bare lead dressing nominal'
                    self.put(name+'.'+label,'cold-core/'+name,point,axis,
                             'insulated-splice' if label=='GND' else 'reed-lead',basis,'nominal')
        # The display reference has no populated rear PCB/terminal geometry.
        carry=self.frame('display',HW/'reference/waveshare-43b-display/waveshare-43b-display.step',(ea.DISPLAY_TILT,))
        for i,label in enumerate(('B','A','GND','V12')):
            p,a=carry(((i-1.5)*3.5,18.,0.),(0,1,0))
            self.put('display.'+label,'display',p,a,'display-terminal',
                     'Accessible rear display region; exact RS485 and power terminal positions unlocated','unlocated')
        lo,hi=bounds(self.part('keystone-jack'));c=centre(self.part('keystone-jack'))
        for i in (2,3,4,5):
            self.put(f'keystone.{i}','keystone-jack',(c[0]+(i-3.5)*2.54,lo[1],c[2]),(0,-1,0),'IDC',
                     'Native jack envelope; individual IDC locations nominal, electrical pin map from cable schedule','nominal',i)

    def boundaries(self):
        # The retained power-cover primitive is a distinct native solid. Keep the
        # estimated donor landings beside that cover, not on the can's far flank.
        power_box=next(s for s in self.part('compressor').Solids()
                       if all(abs(a-b)<.1 for a,b in zip(
                           sorted(y-x for x,y in zip(*bounds(s))),[27.5,45.,45.])))
        lo,hi=bounds(power_box);c=centre(power_box)
        for i,label in enumerate(('H','N','PE')):
            self.put('compressor.'+label,'compressor',(hi[0],c[1]+(i-1)*5.,hi[2]-7.),(1,0,0),'donor-interface',
                     'Proposed external landing region beside retained native power box; exact Unit B lead and earth contacts unlocated','unlocated')
        lo,hi=bounds(self.part('condenser+fan'))
        for i,label in enumerate(('positive','negative')):
            self.put('fan.'+label,'condenser+fan',(hi[0]-6-i*2.,lo[1]+30.,hi[2]+4.),(0,1,0),'donor-lead',
                     'Condenser crown approach; donor lead and terminal unlocated','unlocated')
        lo,hi=bounds(self.part('g-ganen-pump'));c=centre(self.part('g-ganen-pump'))
        for i,label in enumerate(('positive','negative')):
            self.put('diaphragm.'+label,'g-ganen-pump',(c[0]+(i-.5)*4.,hi[1],c[2]),(0,1,0),'factory-lead',
                     'Proposed motor-lead approach; scan records casing/lead transition regions, not terminal polarity','unlocated')
        # The terminal is the ring's wire mouth, rather than an arbitrary point
        # on the vessel bounds. Carry its shared steel/fastener datums through
        # the same cap pose as the rest of the cold core.
        d = carbonator_bond_datums(self.ea)
        self.put('carbonator.PE','cold-core/carbonator-earth-tab',
                 d['wire_exit_mm'],d['wire_outward'],'ring-barrel',
                 'M3 closed ring on the welded top-plate earth tab; shared tab/fastener and ring-barrel datums')

    def record(self):
        return {k:asdict(v) for k,v in sorted(self.terminals.items())}
