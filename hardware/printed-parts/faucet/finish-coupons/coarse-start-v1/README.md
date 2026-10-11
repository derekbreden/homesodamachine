# Faucet lip coarse-start comparison

Five identical full-scale lip sections compare the accepted 0.12 mm band with
1, 2, 4 and 8 model layers at 0.24 mm before transitioning to 0.12 mm. Each is
21.1% of the earlier A/B/C foot volume. The original −15° pose, bed contact,
curved underside and continuous six-wall solid foot region are retained.
The frozen A/B/C section supplies the geometry; mutable full-faucet exports are
not source inputs. This is a section test, with no pedestal or scaled geometry.

| ID | Treatment | First fine nozzle Z |
| --- | --- | --- |
| A | Current 0.12 mm band beginning at Z13.40 | 13.52 mm |
| B | 1 × 0.24 mm | 15.44 mm |
| C | 2 × 0.24 mm | 15.68 mm |
| D | 4 × 0.24 mm | 16.16 mm |
| E | 8 × 0.24 mm | 17.12 mm |

The count begins at the last-starting portion of the retained outer lip,
nozzle Z15.32 mm. Earlier-starting portions receive more coarse layers.
The [native review](native-check.json) verifies every count and transition.

Derek reports that the first supported model layer falls away, including at
0.24 mm, and expects later coarse layers to recover the remaining underside.
First-layer loss is recorded separately from underside continuity, dimensions,
edge gaps and disturbance of the fine face. One coarse layer is expected to
fail; no treatment has a physical result yet.

Global settings are inherited byte-for-byte from the shipping faucet project:
PET-GF, fixed left hardened standard-flow 0.4 mm, external left 254, Textured PEI,
Mark2 +0.04 mm requested trim (+0.02 emitted), 265/280°C nozzle and 80°C bed,
saved cooling and Tree(auto)/Default. Probing clump detection is disabled.
The first bed layer is 0.20 mm. No fan, temperature, flow or support-gap
intervention is applied.

The requested support top gap is 0.45 mm in every object. Native layer-grid
rounding at the front-lip witness gives 0.60 mm for A and 0.48 mm for B/C/D/E.
The four coarse-count treatments share the same emitted witness gap. The
current fine control therefore also differs in this rounded gap; do not
attribute its difference to coarse-layer count alone. Cropping and plate
companions alter support tessellation and layer return time.

This separate plate is prepared only: native estimate **3 h 10 min 18 s**,
**63.2 g** at saved profile density and **87.3 mm** minimum full-bead edge
clearance. The [combined plate](combined/README.md) contains these five cases
and the seam-gap matrix and is the only plate authorized to start.

Reproduce with `tools/cad-venv/bin/python prepare.py`, the private saved native
slice command, then `tools/cad-venv/bin/python review.py`. These are manual
study tools; no hook or automatic verification is installed. Preparation tools
refuse to overwrite a plate with an attempted or accepted launch receipt.
