# Lillium under-sink prototype back top

This is the preserved back top for the Lillium-fed flavor prototype: the
existing printed shells, foam shell, pump cradle and cap, tee carrier and
funnel frame, with the reservoirs, main board and faucet assembled for daily
use. Lillium supplies the chilled carbonated water. The preserved geometry
includes the internal DIGITEN meter mounts and the existing SODA, flavor and
signal connections.

[manifest.json](manifest.json) binds the exact STEP, printable STL, viewer
payload, source files, declared placement box and saved print settings.
The compressed snapshots in `inputs/` are committed with this package. Restoring
them uses those bytes and imports no active enclosure, faucet or placement
generator. The CAD source revision is `b20e7d208`; the source archive retains
the exact source files and box named by the bound generation record for inspection.

## Fit evidence

[fit-check.json](fit-check.json) checks the back top against the C3/V69
front-top v20, the October 1 front/back bottom grip-bridge prints and the
October 5 funnel-frame print. The bottom fixtures are recovered from the
saved native input projects with their recorded original CAD centers and
unchanged triangle indices. Their input archives, original source hashes and
printer receipts are retained in the manifest.

The checks cover seated shell intersections, sampled straight sliding motions,
funnel-frame capture and its 0.25 mm rear roof-corner clearances. Native
installed-part checks cover the foam shell, reservoirs and caps, main board,
DIGITEN meter, pump cradle and cap, tee carrier and funnel frame.

[physical-observation.json](physical-observation.json) records Derek's
October 7 report that the existing prints fit together and that reservoir
printing is starting. The receipt bindings identify the latest recorded
production prints; Derek's report does not independently name their archives.
The back top has no physical fit or print-cleanup result in this package.
These geometric checks do not establish strength, lifetime or wet prototype
acceptance.

## Restore the back top

From the repository root:

```sh
python3 hardware/printed-parts/enclosure/lillium-prototype-2026-10-07/materialize.py
```

This writes `enclosure-back-top.step`, `enclosure-back-top.stl` and
`enclosure-back-top.step.mesh` under `.cache/lillium-prototype-2026-10-07/`.
Use `--all` to restore the fixed fit fixtures, print profile, solid-host
regions and source archive too, or `--output-dir` to choose another directory.

**Slice the STL.** It includes the fluted print surface; the STEP is the native
construction body. The restored part is in machine coordinates. Print it on
its exterior ceiling, with a 180-degree rotation about X. Its print height is
`355 mm − machine Z`.

The saved PET-GF recipe uses a fixed left hardened 0.4 mm standard-flow nozzle,
black PET-GF, a 0.20 mm first layer and ordinary 0.24 mm layers. The exterior
roof-side band at print Z0–9.4 mm uses six walls with support excluded from
its show transition. Functional seats retain accessible tree supports.
The source-bound `print-regions.json` snapshot supplies the local 100% infill
regions for the complete fastener hosts and seam roots. Follow the
[enclosure support-removal strategy](../enclosure/README.md#support-removal-strategy).

This mesh needs a fresh native slice and emitted support/solid-host review
before submission. The back-top v9 review binds a different mesh. This
package submits no printer job.

## Repeat the fit check

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/lillium-prototype-2026-10-07/verify_fit.py
```

The check restores and hashes every frozen input before evaluating geometry.
It writes only this package's fit report and its separate materialized files.
