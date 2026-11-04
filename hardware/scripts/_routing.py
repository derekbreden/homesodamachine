"""_routing — the geometry kit the enclosure's lines are built with.

A run is a `route(...)`: a port anchor at each end, one-dimensional constraints between. Each
constraint supplies one coordinate and the other two carry over, so a waypoint moves along one
axis and every corner is square. Every `F.*` constraint reads off a port or a body face of the
component that owns it — `F.x(port, d)` is the plane `d` along world X from that port,
`F.out(port, d)` steps `d` along the port's own face normal, `F.face("x+", gap)` sits `gap` clear
of the component's +X body face. A frame's box comes off the placed solid and its ports off
`scorecard.PORTS`, so a run rides a move of its parts.

A line leaves and enters along its port's face normal; `route` emits the exit and approach stubs,
one bend radius by default. Each interior corner is a tangent arc backed off `r·tan(θ/2)` down
each leg, so `Run.length` is the length of stock the run cuts.

Every corner turns at its OWN radius (`seat_radii`, `Run.radii`) — the largest its two legs
seat. `bend=` is the ceiling, not the radius: one number caps every corner, a
`{corner index: number}` caps them one at a time, and a turn meant tighter than its legs allow
is said there. A leg between two corners is shared, so the two rise together and whichever runs
out first stops; the other keeps rising into what is left.

An unknown port, a destination that is not an anchor, a bore the port never declared, a `bend=`
cap on a waypoint that does not turn: these RAISE.

A close leaving two coordinates to one turn, a close nearer its port than its own approach stub,
a leg leaving or entering a collet past its skew, a corner with no tangent left to seat an arc
in: the run is DRAWN at what it has — the diagonal leg, the stub clamped to the room, the skew,
the square corner — and its shortfall recorded in `BLOCKED` with the measurement. `tube` sweeps
the port's bore Ø along that centreline like any other.

`redrawn(run, pts)` puts an authored run down a different centreline and re-solves its corners,
so a waypoint can be MOVED and the cost read before anything is edited.
[`probe.World.reroute`](/hardware/scripts/probe.py) is what sweeps that across a range of
positions and says what the run runs into at each one.

Coordinates are the assembly's world frame. Authorship:
[`manifold-layout/_lines.py`](/hardware/manifold-layout/_lines.py). Precedent:
[`routing.ts`](/hardware/pcb/pcba/routing.ts).
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
import sys
from _shared_data import call, box_record

_yw = Path(__file__).resolve().parents[1] / 'printed-parts/enclosure/y-wall-of-back-top'
if str(_yw) not in sys.path:
    sys.path.insert(0, str(_yw))
import _y_wall_dimensions as _rear

BLOCKED = {}
_frames = {}

def __getattr__(name):
    if name == 'cq':
        import cadquery
        globals()[name] = cadquery
        return cadquery
    raise AttributeError(name)

def __dir__():
    return sorted(set(globals()) | {'cq'})

def _call(op, **values):
    result = call('routing.' + op, blocked=BLOCKED, **values)
    BLOCKED.clear()
    BLOCKED.update(result['blocked'])
    return result['value']

_DEFINITIONS = _call('definitions', palette=_rear.port_colors)
FACE_NORMAL = {k:tuple(v) for k,v in _DEFINITIONS['face_normal'].items()}
AXES = ('x','y','z')
BEND_RATIO = _DEFINITIONS['constants']['bend_ratio']
BUTT_MAX = _DEFINITIONS['constants']['butt_max']
COLLET_SKEW = _DEFINITIONS['constants']['collet_skew']
_STRAIGHT_TOL = _DEFINITIONS['constants']['straight_tol']
STUB = None

def normal_of(face):
    return tuple(_call('normal', face=face))

def face_name(face):
    return _call('face_name', face=face)

def leg_skew(a,b,d):
    return _call('skew', a=a, b=b, direction=d)

def _blocked(cid,why):
    _call('blocked',cid=cid,why=why)

def _c(axis,value):
    return {axis:float(value)}

@dataclass
class Frame:
    name: str
    ports: dict
    bb: object

    def _record(self):
        return {'name':self.name,'ports':self.ports,'bb':box_record(self.bb)}
    def _port(self,p):
        return _call('frame_port',frame=self._record(),port=p)
    def at(self,p):
        return tuple(self._port(p)[0])
    def normal(self,p):
        return normal_of(self._port(p)[1])
    def diam(self,p):
        return self._port(p)[2]
    def x(self,p,d=0.):
        return _call('frame_constraint',frame=self._record(),method='x',port=p,distance=d)
    def y(self,p,d=0.):
        return _call('frame_constraint',frame=self._record(),method='y',port=p,distance=d)
    def z(self,p,d=0.):
        return _call('frame_constraint',frame=self._record(),method='z',port=p,distance=d)
    def out(self,p,d):
        return _call('frame_constraint',frame=self._record(),method='out',port=p,distance=d)
    def face(self,f,gap=0.):
        return _call('frame_constraint',frame=self._record(),method='face',face=f,distance=gap)

def frame(name,solid,ports,bb=None):
    if bb is None:
        import _boxes
        bb = _boxes.boxed(solid)
    result = Frame(name,ports,bb)
    _frames[name] = result
    return result

def channel(a,b,bias=0.):
    return _call('channel',a=a,b=b,bias=bias)

def _anchor(anchor):
    comp,_,port = anchor.partition('.')
    return _frames[comp],port

@dataclass
class Run:
    id: str
    kind: str
    frm: str
    to: str
    pts: list
    diam: float
    bend: float
    note: str = ''
    min_bend: float | None = None
    bends: list = field(default_factory=list)
    radii: dict = field(default_factory=dict)
    caps: dict = field(default_factory=dict)
    @property
    def length(self):
        return _call('length',run=asdict(self))
    @property
    def tightest(self):
        return _call('tightest',run=asdict(self))

def _run(value):
    value = dict(value)
    value['pts'] = [tuple(p) for p in value['pts']]
    value['bends'] = [tuple(p) for p in value['bends']]
    value['radii'] = {int(k):v for k,v in value['radii'].items()}
    value['caps'] = {int(k):v for k,v in value['caps'].items()}
    return Run(**value)

def _records():
    return {name:frame._record() for name,frame in _frames.items()}

def route(cid,frm,*rest,kind='refrigerant',stub=STUB,bend=None,skew=None,note=''):
    return _run(_call('route',frames=_records(),cid=cid,frm=frm,rest=rest,kind=kind,stub=stub,bend=bend,
                      skew=skew,note=note,bend_ratio=BEND_RATIO,collet_skew=COLLET_SKEW))

def bent(cid,frm,*rest,kind='refrigerant',bend=None,skew=None,lead=None,min_bend=None,note=''):
    return _run(_call('bent',frames=_records(),cid=cid,frm=frm,rest=rest,kind=kind,bend=bend,skew=skew,
                      lead=lead,min_bend=min_bend,note=note,bend_ratio=BEND_RATIO,butt_max=BUTT_MAX,collet_skew=COLLET_SKEW))

def redrawn(run,pts):
    return _run(_call('redrawn',run=asdict(run),points=pts))

def meet(p,u,q,v,bias):
    return tuple(_call('meet',p=p,u=u,q=q,v=v,bias=bias))

def _dedupe(pts):
    return [tuple(p) for p in _call('dedupe',points=pts)]

def _straighten(pts):
    return [tuple(p) for p in _call('straighten',points=pts)]

def _unit(a,b):
    return _call('unit',a=a,b=b)

def _bends(pts,cid):
    return [tuple(row) for row in _call('bends',points=pts)]

@dataclass
class Stock:
    name: str
    od: float
    min_bend: float
    kinds: tuple
    source: str

STOCKS = tuple(Stock(**{**s,'kinds':tuple(s['kinds'])}) for s in _DEFINITIONS['stocks'])

def stock_of(kind,od):
    value = _call('stock',kind=kind,diam=od)
    return Stock(**{**value,'kinds':tuple(value['kinds'])})

def stock_min(kind,diam):
    return stock_of(kind,diam).min_bend

@dataclass(frozen=True)
class Spool:
    name: str
    rgb: tuple
    names: str
    alpha: float = 1.
    roughness: float = .35
    metalness: float = 0.

SPOOLS = {k:Spool(**{**v,'rgb':tuple(v['rgb'])}) for k,v in _DEFINITIONS['spools'].items()}
SPOOL_OF = _DEFINITIONS['spool_of']
_BY_PREFIX = _DEFINITIONS['by_prefix']

def spool_of(cid):
    return SPOOLS[_call('spool_key',cid=cid)]

def color(key):
    import cadquery as cq
    return cq.Color(*_call('color',spool=asdict(SPOOLS[key])))

def tube_color(cid):
    import cadquery as cq
    return cq.Color(*_call('color',spool=asdict(spool_of(cid))))

def _caps(bends,bend,cid,diam):
    return {int(k):v for k,v in _call('caps',bends=bends,bend=bend,cid=cid,diam=diam).items()}

def seat_radii(pts,bends,caps,cid,diam):
    return {int(k):v for k,v in _call('seat_radii',points=pts,bends=bends,caps=caps,cid=cid,diam=diam).items()}

def leg_caps(run):
    return [tuple(row) for row in _call('leg_caps',run=asdict(run))]

def centreline(run):
    import cadquery as cq
    edges = []
    for segment in _call('segments',run=asdict(run)):
        points = [cq.Vector(*p) for p in segment['points']]
        edges.append(cq.Edge.makeLine(*points) if segment['kind']=='line' else cq.Edge.makeThreePointArc(*points))
    return cq.Wire.assembleEdges(edges)

def tube(run):
    import cadquery as cq
    recipe = _call('tube_recipe',run=asdict(run))
    profile = cq.Wire.makeCircle(recipe['radius'],cq.Vector(*recipe['origin']),cq.Vector(*recipe['direction']))
    return cq.Solid.sweep(profile,[],centreline(run),makeSolid=True,isFrenet=True)
