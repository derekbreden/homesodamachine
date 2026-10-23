# Frozen CO2 hardware

This portable model contains the WR1105 secondary regulator's scanned WR1110
exterior, the nominal GASHER female-inlet/male-outlet check, and the purchased
gray-acetal John Guest PI010822S / PI450822S transitions. Gas flows from the
rear bulkhead through the regulator and check to the carbonator's plain bottom
gas port. Both metal bodies use native +Y flow.

The compact assembly connects the regulator's male 1/4 NPT outlet directly to
the check's female 1/4 NPT inlet. It has one JG inlet adapter and one JG outlet
adapter. Its nominal mouth-to-mouth length is 129.17 mm, with 9.18 mm direct
thread engagement, 14.3 mm inlet-adapter engagement and 11 mm outlet-adapter
engagement. The scanned regulator stub bounds the first of these. The actual
thread make-up reaches remain estimates; an inlet adapter made up by 11 mm
instead of the full projection adds 3.3 mm to the chain.

The active adapter envelopes use the retained manufacturer dimension sheets:
17.5 mm wrench flats and 19.1 mm maximum diameter; the male fitting has a
13.7 mm mouth-to-thread-shoulder length and 14.3 mm thread projection; the
female fitting is 32 mm overall. Undimensioned profile transitions are
occupancy estimates. Tube insertion is the explicit 15.7 mm layout value
from the sheets' released-collet datum. Thread form, seal geometry and
resting-collet travel are not reproduced.

The cap handoff is `(77.500000016, 322.2999999, 253.4)` mm, outward +Z. It is
a 7.5 mm passive guide bore around the continuous 6.35 mm red tube, with no
sealing joint or tube end at the cap. The existing lower tube continues to
the bottom gas elbow; the cap handoff adds no fitting or insertion allowance.

`source-evidence.json` pins the source mesh, current generator records, scan
scope and primary PDFs. `authored/` preserves the four source adapter meshes
as evidence; those meshes are not the active fit model. `geometry/` contains
the canonical metal meshes and published-size adapter meshes. The metal
source artifact is pointer-pinned but marked unproven against its source
commit by the repository's existing artifact record. No production rebuild
is required to use these local snapshots.

## API

Import `model.py` by file path. It requires NumPy only.

- `library()` returns six geometry IDs, `co2-parts-<part-name>`, as `(v, f)`.
- `direct_instances(rotation=None, translation=None, engagement_mm=9.18, inlet_engagement_mm=14.3)`
  returns the four compact assembly instances in a chosen world pose.
- `direct_ports(...)` returns the inlet/outlet tube mouths in that pose.
- `direct_joint()` returns the check-to-regulator placement and assumptions.
- `instances({"regulator": pose, "check": pose})` supplies the six-part
  arrangement if independent placement of both adapter-equipped bodies is useful.
- `ports(group, rotation=None, translation=None)` transforms a group's metal
  and tube datums. Pose dictionaries use `rotation` and `translation_mm`.
- `interfaces()`, `dimensions()`, `evidence()` and `cap_handoff()` return the
  local source and interface records.
- `mates(direct=True)` identifies intended thread-contact pairs.

The canonical regulator origin is its female inlet face. The canonical check
origin is its body's midpoint. For the compact assembly, the check origin is
at `(0,74.47,0)` in the regulator frame. The inlet and outlet mouths are
`(0,-13.7,0)` and `(0,115.47,0)` respectively.

`inlet_engagement_mm` moves the male inlet adapter and its tube-mouth datum
without changing either metal body. The integrated grid study selects 11 mm,
leaving 3.3 mm more inlet projection and giving a 132.47 mm mouth span.

Run `freeze.py` manually to capture the current source meshes. Rebuild only
the local published-size adapter models through the CAD queue:

```sh
PYTHONPATH=. tmp/takeover/cadq "CO2 adapter envelopes" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/co2-grid/co2-parts/build_adapters.py
```

`audit.json` records a one-time source reconstruction and selected envelope
check. This directory adds no recurring verification to the repository.
