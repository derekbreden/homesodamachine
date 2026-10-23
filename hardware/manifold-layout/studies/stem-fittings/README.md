# Stem fittings in the free-space water group

This study connects the ASSE 1022, tee, V-K, pump, single check, regulator and
V-A in their water-path sequence. Pump, V-K, check and the existing bent TPU
pump adapters have fixed poses. ASSE translates without rotating; regulator
and V-A translate together along the tee's run. The carbonator handoff points
down. No enclosure, component supports or electrical placement constrain this study.

The [NeoFit stem elbow](../../../reference/neofit-stem-elbow/README.md) plugs
directly into V-K and another into the check outlet. The
[run-stem tee](../../../reference/neofit-stem-run-tee/README.md) plugs directly
into the upper elbow. A [branch-stem tee](../../../reference/branch-stem-tees/README.md)
inserts into the ASSE TPU outlet socket, with a concealed tube connecting
its run socket to the elbow. The two alternatives use the same number of fittings.

| Arrangement | X, mm | Y, mm | Z, mm |
|---|---:|---:|---:|
| NeoFit run stem | 185.9 | 170.6 | 135.6 |
| NeoFit branch stem | 195.0 | 161.7 | 135.6 |
| JG branch stem, published pressed-collet state | 193.7 | 160.6 | 135.6 |
| Union-fitting reference | 198.8 | 172.0 | 141.8 |

These are occupied axis-aligned envelopes excluding the four arbitrary external
tube stubs. They include component bodies, adapters and clamp bands. A smaller
envelope is a packing result, not a completed enclosure installation.

V-K and check sockets use a 12.7 mm insertion estimate, studied over 10–15 mm.
The NeoFit female socket uses its published 16.891 mm depth; the ASSE TPU socket
uses its modeled 15 mm depth. Full stems remain modeled, including the shoulder
gap outside each host. The branch-stem alternative needs a 33.782 mm concealed
tube between the NeoFit elbow and tee, with 16.891 mm engaged at each end.
All internal connecting tube has zero visible stub. The JG tee's collet state
and the NeoFit branch drawing's interpreted axis mapping are documented with
their models; their small nominal differences are not established fit advantages.

[`study.json`](study.json) records interfaces, transforms, occupied envelopes,
host-depth and elbow-reach sensitivity, and the manual unrelated-body mesh
interference result. Intended insertions are excluded from that exterior check;
the reference models do not fully represent every host's hidden bore. The
nominal alternatives have no unrelated-body intersections in this check.

[`socket-layout.json`](socket-layout.json) names the geometry and agreed poses
in the self-contained `socket-layout.npz` benchmark. These are layout meshes;
the individual stem fittings also have editable builders and native STEP files
in their reference directories. `study.py` uses those references and writes
the numerical report and a compact viewer dataset under ignored `out/`.

Run the mesh-only study from the repository root:

```sh
tools/cad-venv/bin/python hardware/manifold-layout/studies/stem-fittings/study.py --check
```

`--check` runs the exterior interference question on demand. The study is not
part of the enclosure build or an automatic check.
