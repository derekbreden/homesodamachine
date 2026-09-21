# Archived front-top baseline fixture

[`current-front-top.step`](current-front-top.step) is a separate native fixture
built with `enclosure.build_piece(box, 'front', 'top')` from the completed Box
`a1468381b233f54a07cd491fefe3dabdc56da89bb46fa3bffb6d2181802427c9`.
It retains every front-top tray, guide, roof, pocket and final clearance cut.
[`fixture.json`](fixture.json) records the loaded source closure, Box digest,
native digest and round-trip validity readings. The imported STEP is one valid
solid. Its 0.005457 mm³ volume-integration difference is 4.01 × 10⁻⁹ of the
1,360,531 mm³ source volume; maximum outer-bound change is 0.0000006 mm.

This is the current **SeaFlo-sized Box baseline**. It does not include the selected
G Ganen integration and does not qualify the provisional tee branch/nose datums,
the spring-capture study or the integral-latch study. Production enclosure files
are not replaced, and no printable mesh or slice is produced here.

**Branch-dependent print release is held.** [Derek's measured overall branch width](../../../../reference/jg-pp0208e-tee/branch-operating-measurements.json),
from the back of the widest fixed run collar to the outermost collet face, is
30.5 mm extended and 29.0 mm pressed. Only the small terminal ring moves. The
resulting 1.5 mm branch stroke is distinct from the 1.65 mm run-sleeve stroke.
This fixture and its interrupted motion audit retain the frozen, unqualified 20.07 mm
branch-reach datum and existing stroke model. Their results apply only to the
recorded source state; the measured branch dimensions require propagation and
fresh branch-dependent geometry checks before release.

The carrier halves in this audit are the frozen production lap-joint baseline.
They do not qualify a joint replacement or require reuse of either half. The
replacement joint must provide simple two-piece assembly with broad flexing
walls informed by the physically proven faucet display cover.

## Native guide and backing evidence

[`upper-backing-check.json`](upper-backing-check.json) is the existing carrier
verifier's `--wall-step` audit against this fixture. Its 26 wall stock/alignment
readings and 12 opposed X-rotation contact readings pass. The current carrier's
upper backing is 5.504166 mm thick. The fixed service-slot lands, recess roof and
fore guide are present in the actual completed wall.

At the connected station, first contact while holding the carrier center fixed is
approximately 2.078–2.107°. End-station contacts also involve the stops. Those
angles are not free-body backlash or stiffness measurements. No spring guide is
credited as a restraint. Joint play, material response and assembled rigidity
remain separate physical qualifications.

[`readiness-audit.json`](readiness-audit.json) and
[`readiness-audit.svg`](readiness-audit.svg) retain the verifier's section and
declared body-bending comparison. The center joint is excluded from that model.

The local wrapper redirects only the verifier's five literal expressions naming
its three report files. Geometry, inputs, thresholds and checks execute from the
existing verifier. Its production report files are hashed before and after and
must remain unchanged.

## Local motion evidence

[`check_motion.py`](check_motion.py) calls the existing production carrier
entry/travel checker with the fresh front-top and actual native carrier halves.
Its other blockers are the current cartridge/cap and production-placed valve and
coil solids. Tee and flexible-tube motions use the production functions. The
current Box, derived local interface and native input bytes are checked explicitly.

[`motion-check.json`](motion-check.json) records the result and exact bounded
scope. The operation was deliberately interrupted to prioritize propagation of
the measured tee branch geometry. It is **incomplete**, with no motion pass or
fail result and no recorded partial motion readings. Other enclosure quadrants,
cold core, diaphragm pump and hardware outside that set are excluded. The
finished wall and backing readings above remain archived baseline evidence.

## Reproduce

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/current-front-top/build_fixture.py \
  --box-sha256 a1468381b233f54a07cd491fefe3dabdc56da89bb46fa3bffb6d2181802427c9
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/current-front-top/check_upper_backing.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/current-front-top/check_motion.py
```

The builder uses the ordinary CAD generator mutex. Both subsequent checks are
read-only geometry probes whose reports remain in this directory. No global
trace, printer operation, production-file replacement or publication occurs.
