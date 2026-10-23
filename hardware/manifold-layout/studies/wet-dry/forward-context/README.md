# Forward PCB diagnostic context

The retained front wet parts occupy part of the space below the funnel. These
frozen meshes and two explicit PCB poses make that overlap visible without
moving any wet component.

Both board poses occupy X−74..−1.2 and Y182..272.816 mm, with components upward.
The low pose has its board underside at Z257; it intersects V-B, its formed
outlet, and the reservoir B fill/draw lines. Installed local PCB leads also
intersect the funnel elbow cradle and WAGO-mana. The raised pose has its board
underside at Z316; the populated board and active mating connections intersect
the actual funnel and frame.

`checks.json` binds these two queries to their exact poses. It separates
installed geometry from optional unplugging/tool probes. `high-planes.json`
records the same footprint at five upper heights in both horizontal clockings;
`high-planes-xlong.json` records three heights with the board turned crosswise.
Each specified upper pose intersects the funnel and frame. These results apply
to those poses; they do not establish that every farther-forward arrangement
is blocked.

V-B has its own cap cradle and two separate tube connections. It is not a
directly butted member of the fixed front source/valve chain. Its inlet is fed
by the funnel tube; its outlet reaches fixed tee Y-B through a formed R14
turn/step. `relationships.json` records those datums and the two reservoir B
cap openings. Support features and outgoing routes tied to relocated rear
components are excluded from this retained-obstacle set.

`inventory.json` records component provenance and SHA-256 hashes. NPZ arrays
`v`/`f` retain source-world coordinates. `query-context.json` identifies the
additional existing funnel/frame, WAGOs and ceiling used by the selected
manual query. No source STEP, production generator or temporary path is needed.

Import `study.py` for:

- `library()`: `forward-*` meshes and shared `connection-*` meshes.
- `obstacles()`: unchanged wet-neighbor instances.
- `ghost('low'|'high')`: the selected board pose.
- `connections('low'|'high', probes=False)`: carried active housings and local
  leads, with unique names; probes are opt-in and unused J8 is excluded.
- `query('low'|'high', obstacle_meshes=None)`: a manual surface-intersection
  query; supplied obstacles are name-to-`(v, f)` world meshes.

Run the two selected queries explicitly with:

```sh
PYTHONPATH=. tmp/takeover/cadq "Forward PCB diagnostic" -- \
  tools/cad-venv/bin/python \
  hardware/manifold-layout/studies/wet-dry/forward-context/study.py --check
```

The study contains no PCB carrier, new mounting features, full harness route,
or wet-part relocation. The access meshes describe local straight tool and
unplugging paths rather than a complete service sequence.
