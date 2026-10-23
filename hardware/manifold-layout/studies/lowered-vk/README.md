# Pump, lowered V-K and ASSE

The water group places ASSE directly above the pump, with V-K beside the inlet.
V-K retains vertical ports and its head toward −Y. Short, joined fittings define
the arrangement; the pump's scanned foot plane supplies the lower height datum.
The study is in free space, with no enclosure or supports placed.

The existing printed TPU pump elbow is clocked **25° downward toward +Y** around
the inlet barb. Its mouth meets a stem elbow's female socket on a **31.891 mm
concealed tube**: 15 mm in the TPU and 16.891 mm in the fitting. That elbow's male
stem inserts into a second elbow, whose male stem inserts into V-K's lower port.
The two elbows therefore stack stem-to-socket. Their shoulders sit flush under
the [trimmed-stem assumption](../stem-fittings/trimmed/dimensions.json).

The pump-side elbow has a 16.891 mm stem for its NeoFit host; its
[native model and dimensions](parts/dimensions.json) are local to this study.
The valve-side elbow uses the existing 12.7 mm valve-host model. Clocking the TPU
adapter down and sideways lets the return sit above the foot plane. The lowest
new fitting is **3.09 mm above** that plane. V-K moves **28.32 mm downward**,
25.10 mm toward −X and 34.03 mm toward +Y without rotating.

An upper stem elbow turns V-K's inlet toward the tee. A **NeoFit branch-stem tee**
inserts directly into the ASSE TPU outlet adapter; its straight run supplies V-K
and the regulator/V-A branch. The regulator and V-A are clocked a quarter-turn
about their fluid axes, with their heads outward toward +Y relative to the run.
The pump discharge TPU elbow, single check and downward carbonator handoff retain
their poses.

Two connected arrangements are recorded:

| Upper group | ASSE nearest surface gap to pump | ASSE bottom above pump crown |
|---|---:|---:|
| Clocked 20° inward about V-K's upper port | 5.64 mm | 5.41 mm |
| ASSE orientation preserved | 9.54 mm | 5.41 mm |

The inward clock turns the upper elbow, tee, ASSE and flavor-water branch as a
connected group. V-K keeps its orientation. Both layouts have no unrelated body
intersections in the manual mesh check. The run-stem reference
arrangement has a 37.93 mm nearest ASSE-to-pump gap. Gaps describe these reference
geometries; the supplier-estimated fitting profiles and unmeasured host depths
retain their stated scope.

[`study.json`](study.json) carries poses, connection points, insertion depths and
measured body gaps. The local floor guide is the pump's scanned support height,
not a placed enclosure floor. `models.py` derives the additional square-cut elbow
from its native source. `study.py` reads the committed
[water-group benchmark](../stem-fittings/socket-layout.json), applies the
connected transforms and writes the comparison data under ignored `out/`.

From the repository root:

```sh
PYTHONPATH=. tmp/takeover/cadq "Lowered V-K elbow model" -- \
  tools/cad-venv/bin/python hardware/manifold-layout/studies/lowered-vk/models.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/lowered-vk/study.py --check
```

The interference and distance questions run on demand with `--check`; this study
adds no enclosure build dependency or automatic check.
