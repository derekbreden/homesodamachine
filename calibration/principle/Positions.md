---

# User

---

Why do you agents always "probe" for these movements instead of just reading where things are positioned and moving them to that new position? Especially in a case like this, where we're rebuilding things from scratch, it just seems like a huge wast of resources and time to be running complex tools meant for the full geometry we don't have.

[Image: the ASSE joints session's Bash call, "Probing how far the pump moves aft and west to clear bulkheads", Running — the tail of the heredoc script under The search below, run with tools/cad-venv/bin/python]

---

# Assistant

---

Reading the other session's probe script and the study's code to see whether the pump and bulkhead positions could simply have been read off.

---

# Assistant

---

Reading that session's last few turns to see what led it to run the search instead of doing the arithmetic.

---

# User

---

Maybe we need a tool or tooling that enables/encourages/catalyzes agents to do formulaic position finding instead of searching by trial and error. It seems like we spend a great deal of time on this, overall, and it is quite frustrating to watch for these simple moves.

---

# Assistant

---

The probe finished after about 10 minutes, and its table doesn't show the collision. Now I'm checking which position tools the repo already has, so the tool I propose builds on them.

---

# Assistant

---

Reading the repo's note on what memory is for before I save anything, as the hook asks.

---

# Assistant

---

The repo teaches agents to search. Three things in it push them that way:

- **The docs say to.** AGENTS.md sends every agent to [hardware/README.md](/hardware/README.md). That file describes [probe.py](/hardware/scripts/probe.py) as the tool that "asks the placed machine a geometry question instead of reasoning about it," and probe.py's first line says the same. Both were committed on 2026-07-23, before commits quoted you, so git can't say whether that wording was yours.
- **The study is written that way.** [study.py](/hardware/manifold-layout/studies/rear-port-rebuild/study.py) finds the V-K stub's length by stepping half a millimetre at a time, and it finds the CO2 route by trying a grid of positions. That session had just done the CO2 move with that same grid search, and agents copy the code around them.
- **A search lets the agent skip working out what's in the way.** Reading positions makes it name that part first.

**What it cost this time.** The probe built every above-core part to use nine of them, and it ran almost 10 minutes. Every row against flavor-b read 0.02–0.04 mm. The script measured distance to the nearest surface, which reads about zero whether a part is touching flavor-b or sitting inside it, so the table never showed what was in the way. Then ASSE joints ran a second search, and over 15 minutes in it's reading the pump's rails and feet.

**Reading took 0.01 s.** I took each solid's box from the scene file the viewer already shows, moved the pump 17 mm aft, and listed what still overlaps. What's in the way is the pump's east rear foot. It ends up 6.6 mm into flavor-b's bulkhead, so "a little west" can't clear it. By the boxes it clears at about 30 mm west, or with the pump about 8 mm short of the wall, or with that foot clipped further forward if its rail allows. That's your call to make in that session.

**The tool I'd build from that prototype:**
1. `hardware/scripts/where.py` reads a scene file and gives every solid's box in machine coordinates. Give it a move and it lists each pair that still overlaps, with how far a move in each direction clears it. That names the part in the way, and the move you need is the largest number. A box is bigger than the round part inside it, so a move read off boxes always clears. The part in the way then gets one exact check at its new position.
2. The scene file names each solid, so the table says "rear foot" instead of `g-ganen-pump/25`. That changes every scene's file once.
3. hardware/README.md and probe.py stop saying "instead of reasoning." The README lists where.py first and keeps probe.py for questions a box can't answer.

None of it runs automatically, and there's no new rule in AGENTS.md. Agents will use where.py because it's the shortest route and the first tool the docs name.

Your memory hook caught me writing this up as a correction note. I read the calibration doc and didn't save it. If you want the tool, the lesson belongs in the repo.

---

# User

---

Yes, build it

---

# User

---

And put the lesson in the repo.

---

## The search

`aftwest.py`, the script in the screenshot, as the ASSE joints session wrote it on 2026-10-30. It builds every above-core part to read nine of them, takes the rear wall's inner face as two numbers, and steps the pump west half a millimetre at a time. Its output came back 9 min 35 s after it started.

```python
"""The pump aft to the rear wall's inner face, then west in half millimetres off the bulkheads."""
import json, sys, time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
HW = Path('/Users/derekbredensteiner/Developer/homesodamachine/hardware')
for p in ('scripts', 'manifold-layout'):
    sys.path.insert(0, str(HW / p))
import cadquery as cq
import above_core_parts as acp
t0 = time.time()
comps = acp.components()
print(f'components {time.time() - t0:.0f} s')
facts = json.load(open(HW / 'manifold-layout' / 'enclosure-assembly.facts.json'))
ROW_OLD = facts['card_ports']['bulkhead-water']['outboard']['pos'][2]
DROP = ROW_OLD - 328.0
rng = np.random.default_rng(1)
def pts(shape, step=0.4, tol=(0.03, 0.1)):
    vs, ts = shape.tessellate(*tol)
    vs = np.array([(q.x, q.y, q.z) for q in vs]); tri = vs[np.array(ts)]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    n = np.floor(area / step ** 2 + rng.random(len(area))).astype(int)
    i = np.repeat(np.arange(len(tri)), n)
    r1, r2 = np.sqrt(rng.random(len(i)))[:, None], rng.random(len(i))[:, None]
    return np.concatenate([(1 - r1) * a[i] + r1 * (1 - r2) * b[i] + r1 * r2 * c[i], vs])
pump = comps['g-ganen-pump'][0]
P = pts(pump, 0.5, (0.2, 0.5))
print('pump box', P.min(0).round(2), P.max(0).round(2), len(P))
blk = {}
for name in ('bulkhead-carb', 'bulkhead-drain', 'bulkhead-flavor-a', 'bulkhead-flavor-b'):
    for n in (name, name + '-nut'):
        s = comps[n][0].moved(cq.Location(cq.Vector(0., 0., -DROP)))
        blk[n] = pts(s, 0.3)
        print(f'  {n:24} box {blk[n].min(0).round(1)} {blk[n].max(0).round(1)}')
B = cKDTree(np.concatenate(list(blk.values())))
def face_y(Q):
    land = (Q[:, 0] >= 24.) & (Q[:, 0] <= 91.) & (Q[:, 2] >= 250.)
    return np.where(land, 465.3, 462.3)
print('dx west, dy aft, butt x-range, to bulkheads (nearest by part)')
for dx in np.arange(0., 40.01, 0.5):
    Q = P - np.array([dx, 0., 0.])
    dy = float((face_y(Q) - Q[:, 1]).min())
    Q = Q + np.array([0., dy, 0.])
    d = float(B.query(Q, distance_upper_bound=20.)[0].min())
    butt = Q[Q[:, 1] > Q[:, 1].max() - 0.5]
    if dx % 2 == 0 or d >= 0.:
        per = {n: round(float(cKDTree(v).query(Q, distance_upper_bound=20.)[0].min()), 2) for n, v in blk.items()}
        per = {n: v for n, v in per.items() if v < 20}
        print(f'  {dx:5.1f} {dy:6.2f}  butt X{butt[:, 0].min():.1f}..{butt[:, 0].max():.1f} Z{butt[:, 2].min():.1f}..{butt[:, 2].max():.1f}  {per}')
    if d >= 1.0:
        print(f'first clear by 1 mm: dx {dx}, dy {dy:.2f}')
        break
```

```text
  bulkhead-carb            box [ 66.1 446.5 284.6] [ 88.9 480.8 307.4]
  bulkhead-carb-nut        box [ 67.5 461.3 284.5] [ 87.5 465.3 307.5]
  bulkhead-drain           box [ 27.  449.8 285.8] [ 47.5 483.1 306.2]
  bulkhead-drain-nut       box [ 28.2 458.8 285.6] [ 46.2 465.3 306.4]
  bulkhead-flavor-a        box [ 67.3 449.8 253.8] [ 87.7 483.1 274.2]
  bulkhead-flavor-a-nut    box [ 68.5 458.8 253.6] [ 86.5 465.3 274.4]
  bulkhead-flavor-b        box [ 27.  449.8 253.8] [ 47.5 483.1 274.2]
  bulkhead-flavor-b-nut    box [ 28.2 458.8 253.6] [ 46.2 465.3 274.4]
dx west, dy aft, butt x-range, to bulkheads (nearest by part)
    0.0  17.00  butt X-14.5..33.2 Z262.3..298.7  {'bulkhead-drain': 0.02, 'bulkhead-drain-nut': 0.05, 'bulkhead-flavor-a': 15.29, 'bulkhead-flavor-a-nut': 14.83, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 0.46}
    0.5  17.00  butt X-15.0..32.7 Z262.3..298.7  {'bulkhead-drain': 0.04, 'bulkhead-drain-nut': 0.02, 'bulkhead-flavor-a': 15.75, 'bulkhead-flavor-a-nut': 15.27, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 0.86}
    1.0  17.00  butt X-15.5..32.2 Z262.3..298.7  {'bulkhead-drain': 0.03, 'bulkhead-drain-nut': 0.05, 'bulkhead-flavor-a': 16.22, 'bulkhead-flavor-a-nut': 15.71, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 1.16}
    1.5  17.00  butt X-16.0..31.7 Z262.3..298.7  {'bulkhead-drain': 0.04, 'bulkhead-drain-nut': 0.04, 'bulkhead-flavor-a': 16.68, 'bulkhead-flavor-a-nut': 16.15, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 1.49}
    2.0  17.00  butt X-16.5..31.2 Z262.3..298.7  {'bulkhead-drain': 0.03, 'bulkhead-drain-nut': 0.05, 'bulkhead-flavor-a': 17.15, 'bulkhead-flavor-a-nut': 16.6, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 1.9}
    2.5  17.00  butt X-17.0..30.7 Z262.3..298.7  {'bulkhead-drain': 0.07, 'bulkhead-drain-nut': 0.05, 'bulkhead-flavor-a': 17.62, 'bulkhead-flavor-a-nut': 17.04, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 2.34}
    3.0  17.00  butt X-17.5..30.2 Z262.3..298.7  {'bulkhead-drain': 0.33, 'bulkhead-drain-nut': 0.02, 'bulkhead-flavor-a': 18.09, 'bulkhead-flavor-a-nut': 17.48, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
    3.5  17.00  butt X-18.0..29.7 Z262.3..298.7  {'bulkhead-drain': 0.8, 'bulkhead-drain-nut': 0.09, 'bulkhead-flavor-a': 18.56, 'bulkhead-flavor-a-nut': 17.93, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 2.36}
    4.0  17.00  butt X-18.5..29.2 Z262.3..298.7  {'bulkhead-drain': 1.28, 'bulkhead-drain-nut': 0.07, 'bulkhead-flavor-a': 19.03, 'bulkhead-flavor-a-nut': 18.37, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
    4.5  17.00  butt X-19.0..28.7 Z262.3..298.7  {'bulkhead-drain': 1.76, 'bulkhead-drain-nut': 0.05, 'bulkhead-flavor-a': 19.5, 'bulkhead-flavor-a-nut': 18.82, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
    5.0  17.00  butt X-19.5..28.2 Z262.3..298.7  {'bulkhead-drain': 2.24, 'bulkhead-drain-nut': 0.05, 'bulkhead-flavor-a': 19.98, 'bulkhead-flavor-a-nut': 19.28, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
    5.5  17.00  butt X-20.0..27.7 Z262.3..298.7  {'bulkhead-drain': 2.72, 'bulkhead-drain-nut': 0.42, 'bulkhead-flavor-a-nut': 19.73, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 2.36}
    6.0  17.00  butt X-20.5..27.2 Z262.3..298.7  {'bulkhead-drain': 3.21, 'bulkhead-drain-nut': 0.89, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 2.36}
    6.5  17.00  butt X-21.0..26.7 Z262.3..298.7  {'bulkhead-drain': 3.69, 'bulkhead-drain-nut': 1.38, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 2.36}
    7.0  17.00  butt X-21.5..26.2 Z262.3..298.7  {'bulkhead-drain': 4.18, 'bulkhead-drain-nut': 1.87, 'bulkhead-flavor-b': 0.06, 'bulkhead-flavor-b-nut': 2.36}
    7.5  17.00  butt X-22.0..25.7 Z262.3..298.7  {'bulkhead-drain': 4.67, 'bulkhead-drain-nut': 2.37, 'bulkhead-flavor-b': 0.07, 'bulkhead-flavor-b-nut': 2.36}
    8.0  17.00  butt X-22.5..25.2 Z262.3..298.7  {'bulkhead-drain': 5.15, 'bulkhead-drain-nut': 2.87, 'bulkhead-flavor-b': 0.05, 'bulkhead-flavor-b-nut': 2.36}
    8.5  17.00  butt X-23.0..24.7 Z262.3..298.7  {'bulkhead-drain': 5.64, 'bulkhead-drain-nut': 3.36, 'bulkhead-flavor-b': 0.05, 'bulkhead-flavor-b-nut': 2.36}
    9.0  17.00  butt X-23.5..24.2 Z262.3..298.7  {'bulkhead-drain': 6.12, 'bulkhead-drain-nut': 3.86, 'bulkhead-flavor-b': 0.07, 'bulkhead-flavor-b-nut': 2.36}
    9.5  17.00  butt X-24.0..23.7 Z262.3..298.7  {'bulkhead-drain': 6.61, 'bulkhead-drain-nut': 4.36, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 2.36}
   10.0  17.00  butt X-24.5..23.2 Z262.3..298.7  {'bulkhead-drain': 7.1, 'bulkhead-drain-nut': 4.85, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
   10.5  17.00  butt X-25.0..22.7 Z262.3..298.7  {'bulkhead-drain': 7.58, 'bulkhead-drain-nut': 5.35, 'bulkhead-flavor-b': 0.06, 'bulkhead-flavor-b-nut': 2.36}
   11.0  17.00  butt X-25.5..22.2 Z262.3..298.7  {'bulkhead-drain': 8.07, 'bulkhead-drain-nut': 5.84, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 2.36}
   11.5  17.00  butt X-26.0..21.7 Z262.3..298.7  {'bulkhead-drain': 8.56, 'bulkhead-drain-nut': 6.34, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 2.36}
   12.0  17.00  butt X-26.5..21.2 Z262.3..298.7  {'bulkhead-drain': 9.05, 'bulkhead-drain-nut': 6.83, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
   12.5  17.00  butt X-27.0..20.7 Z262.3..298.7  {'bulkhead-drain': 9.53, 'bulkhead-drain-nut': 7.33, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
   13.0  17.00  butt X-27.5..20.2 Z262.3..298.7  {'bulkhead-drain': 10.02, 'bulkhead-drain-nut': 7.82, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
   13.5  17.00  butt X-28.0..19.7 Z262.3..298.7  {'bulkhead-drain': 10.51, 'bulkhead-drain-nut': 8.32, 'bulkhead-flavor-b': 0.05, 'bulkhead-flavor-b-nut': 2.36}
   14.0  17.00  butt X-28.5..19.2 Z262.3..298.7  {'bulkhead-drain': 11.0, 'bulkhead-drain-nut': 8.82, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 2.36}
   14.5  17.00  butt X-29.0..18.7 Z262.3..298.7  {'bulkhead-drain': 11.49, 'bulkhead-drain-nut': 9.31, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 2.36}
   15.0  17.00  butt X-29.5..18.2 Z262.3..298.7  {'bulkhead-drain': 11.99, 'bulkhead-drain-nut': 9.81, 'bulkhead-flavor-b': 0.06, 'bulkhead-flavor-b-nut': 2.36}
   15.5  17.00  butt X-30.0..17.7 Z262.3..298.7  {'bulkhead-drain': 12.48, 'bulkhead-drain-nut': 10.31, 'bulkhead-flavor-b': 0.06, 'bulkhead-flavor-b-nut': 2.36}
   16.0  17.00  butt X-30.5..17.2 Z262.3..298.7  {'bulkhead-drain': 12.97, 'bulkhead-drain-nut': 10.8, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 2.36}
   16.5  17.00  butt X-31.0..16.7 Z262.3..298.7  {'bulkhead-drain': 13.46, 'bulkhead-drain-nut': 11.3, 'bulkhead-flavor-b': 0.01, 'bulkhead-flavor-b-nut': 2.37}
   17.0  17.00  butt X-31.5..16.2 Z262.3..298.7  {'bulkhead-drain': 13.96, 'bulkhead-drain-nut': 11.8, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.36}
   17.5  17.00  butt X-32.0..15.7 Z262.3..298.7  {'bulkhead-drain': 14.45, 'bulkhead-drain-nut': 12.29, 'bulkhead-flavor-b': 0.03, 'bulkhead-flavor-b-nut': 2.37}
   18.0  17.00  butt X-32.5..15.2 Z262.3..298.7  {'bulkhead-drain': 14.94, 'bulkhead-drain-nut': 12.79, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 2.37}
   18.5  17.00  butt X-33.0..14.7 Z262.3..298.7  {'bulkhead-drain': 15.43, 'bulkhead-drain-nut': 13.29, 'bulkhead-flavor-b': 0.02, 'bulkhead-flavor-b-nut': 2.36}
   19.0  17.00  butt X-33.5..14.2 Z262.3..298.7  {'bulkhead-drain': 15.92, 'bulkhead-drain-nut': 13.79, 'bulkhead-flavor-b': 0.06, 'bulkhead-flavor-b-nut': 2.37}
   19.5  17.00  butt X-34.0..13.7 Z262.3..298.7  {'bulkhead-drain': 16.41, 'bulkhead-drain-nut': 14.29, 'bulkhead-flavor-b': 0.08, 'bulkhead-flavor-b-nut': 2.37}
   20.0  17.00  butt X-34.5..13.2 Z262.3..298.7  {'bulkhead-drain': 16.9, 'bulkhead-drain-nut': 14.78, 'bulkhead-flavor-b': 0.04, 'bulkhead-flavor-b-nut': 2.42}
   20.5  17.00  butt X-35.0..12.7 Z262.3..298.7  {'bulkhead-drain': 17.39, 'bulkhead-drain-nut': 15.28, 'bulkhead-flavor-b': 0.06, 'bulkhead-flavor-b-nut': 2.48}
   21.0  17.00  butt X-35.5..12.2 Z262.3..298.7  {'bulkhead-drain': 17.88, 'bulkhead-drain-nut': 15.78, 'bulkhead-flavor-b': 0.05, 'bulkhead-flavor-b-nut': 2.54}
   21.5  17.00  butt X-36.0..11.7 Z262.3..298.7  {'bulkhead-drain': 18.37, 'bulkhead-drain-nut': 16.28, 'bulkhead-flavor-b': 0.05, 'bulkhead-flavor-b-nut': 2.61}
   22.0  17.00  butt X-36.5..11.2 Z262.3..298.7  {'bulkhead-drain': 18.86, 'bulkhead-drain-nut': 16.78, 'bulkhead-flavor-b': 0.01, 'bulkhead-flavor-b-nut': 2.67}
   22.5  17.00  butt X-37.0..10.7 Z262.3..298.7  {'bulkhead-drain': 19.34, 'bulkhead-drain-nut': 17.28, 'bulkhead-flavor-b': 0.13, 'bulkhead-flavor-b-nut': 2.81}
   23.0  17.00  butt X-37.5..10.2 Z262.3..298.7  {'bulkhead-drain': 19.83, 'bulkhead-drain-nut': 17.78, 'bulkhead-flavor-b': 0.07, 'bulkhead-flavor-b-nut': 2.98}
   23.5  17.00  butt X-38.0..9.7 Z262.3..298.7  {'bulkhead-drain-nut': 18.27, 'bulkhead-flavor-b': 0.41, 'bulkhead-flavor-b-nut': 3.15}
   24.0  17.00  butt X-38.5..9.2 Z262.3..298.7  {'bulkhead-drain-nut': 18.77, 'bulkhead-flavor-b': 0.8, 'bulkhead-flavor-b-nut': 3.33}
   24.5  17.00  butt X-39.0..8.7 Z262.3..298.7  {'bulkhead-drain-nut': 19.27, 'bulkhead-flavor-b': 1.19, 'bulkhead-flavor-b-nut': 3.51}
first clear by 1 mm: dx 24.5, dy 17.00
```

## where.py on the same move

Read off the payload the viewer draws for the same scene, with `hardware/scripts/where.py` as committed beside this room.

```text
$ python3 hardware/scripts/where.py rear-port-rebuild g-ganen-pump --against enclosure-back-top --reach aft | tail -2
farthest move from there before a pair comes within 0 mm, by rays 0.25 mm apart through the meshes [by boxes]:
  aft     17.00 [   0.00]   g-ganen-pump/1 against enclosure-back-top
(0.9 s)

$ python3 hardware/scripts/where.py rear-port-rebuild g-ganen-pump --move 0 17 0 --against 'bulkhead-*' --margin 1 --clear west
moved X +0.00 Y +17.00 Z +0.00
g-ganen-pump                  26  X -38.30..56.57  Y 302.04..462.30  Z 253.40..313.93  94.87 x 160.26 x 60.53

boxes within 1 mm, how far they overlap, and the move in each direction that stands them 1 mm apart:
g-ganen-pump/1           X -21.80..40.13  Y 302.24..462.30  Z 255.36..313.82  61.93 x 160.06 x 58.46
  bulkhead-drain         overlap X 13.11 Y 12.46 Z 20.31   west 14.11 east 70.28 fore 13.46 aft 181.89 down 28.98 up 51.79
  bulkhead-drain-nut     overlap X 11.88 Y 3.50 Z 20.78   west 12.88 east 69.05 fore 4.50 aft 164.06 down 29.21 up 52.03
  bulkhead-flavor-b      overlap X 13.11 Y 12.46 Z 18.79   west 14.11 east 70.28 fore 13.46 aft 181.89 down 60.98 up 19.79
  bulkhead-flavor-b-nut  overlap X 11.88 Y 3.50 Z 19.03   west 12.88 east 69.05 fore 4.50 aft 164.06 down 61.21 up 20.03
g-ganen-pump/6           X -18.32..36.53  Y 380.94..455.94  Z 255.36..277.37  54.85 x 75.00 x 22.01
  bulkhead-flavor-b      overlap X 9.51 Y 6.10 Z 18.79   west 10.51 east 66.80 fore 7.10 aft 103.19 down 24.53 up 19.79
g-ganen-pump/9           X -15.34..33.60  Y 379.86..456.01  Z 262.84..312.18  48.94 x 76.15 x 49.34
  bulkhead-drain         overlap X 6.58 Y 6.17 Z 20.31   west 7.58 east 63.82 fore 7.17 aft 104.27 down 27.33 up 44.32
  bulkhead-flavor-b      overlap X 6.58 Y 6.17 Z 11.32   west 7.58 east 63.82 fore 7.17 aft 104.27 down 59.33 up 12.32
g-ganen-pump/25          X 31.63..56.57  Y 438.44..456.44  Z 253.40..271.80  24.93 x 18.00 x 18.40
  bulkhead-flavor-b      overlap X 15.85 Y 6.60 Z 17.95   west 30.55 east 16.85 fore 7.60 aft 45.69 down 18.95 up 21.75

least move from there with every pair 1 mm apart, by rays 0.25 mm apart through the meshes [by boxes]:
  west    24.94 [  30.55]   g-ganen-pump/25 against bulkhead-flavor-b
(0.4 s)
```
