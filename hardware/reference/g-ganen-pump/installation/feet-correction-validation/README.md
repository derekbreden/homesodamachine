# Common-foot installation validation

The four identical 7 mm rubber feet sit at the full-engagement extremes of the visible rail: local X = 9.5 and 67.5 mm. Each clip spans 18 mm on the rail interval 0.5–76.5 mm. The pad outline does not define travel. Screw axes are 1.5 mm outward from the slot centers, and the whole pump sits 1 mm forward of the baseline neighbor assembly. Its lateral and vertical datums are fixed.

`validation.json` indexes the exact evidence and final input audit. The original reports and executed probe scripts are unchanged. `manifest.json` hashes every retained file; compressed native files also bind their decompressed bytes. The baseline assembly is identified by its published content hash in `fixtures/baseline-assembly.json`; the smaller foam datum, V-F fixture, changed native bodies and washer inputs are retained here.

The bounded pump/route check passes 830 pair readings against the complete 210-body baseline. It rebuilds the pump, water-6, water-7, fluid-14 and both mount-bearing cap pieces from the frozen source. All unrelated neighbors retain a 1 mm minimum. Named endpoint and bearing contacts remain explicit. The pump's movement also changes fluid-14's aft hose-dependent turn; its valve-side segment and complete cap bearing stay fixed.

| Current reading | Result |
| --- | ---: |
| Pump / flavor-A union native air | 1.274542 mm |
| Water-7 / fluid-14 mesh air | 1.369922 mm |
| Water-7 / CO₂-2 mesh air | 1.744636 mm |
| Fluid-14 / V-A mesh air | 1.075416 mm |
| Fluid-14 / V-K mesh air | 1.125118 mm |
| Fluid-14 / lid intended bearing air | 0.150000 mm |
| Rigid pump / lid native air | 1.960953 mm |
| Each rubber foot / lid native overlap | 0 mm³ |
| Water-6 and water-7 minimum bend radius | 15.9 mm |
| Fluid-14 minimum bend radius | 14 mm |

The nominal Ø9 washer has 0.5 mm clearance from the rubber shoulder and 38.289 mm² of supported annular area. Both axial sides of the slot support it; the M3 shank has 0.4 mm minimum slot clearance. The current 8.5 mm blind bore leaves 6.1 mm of floor and 1.7 mm of nominal screw-tip reserve with a 20 mm screw, 7 mm pad, 0.8 mm washer and 5.4 mm lid. The earlier washer report retains its explicit 8.514 mm depth calculation; the current round 8.5 mm depth is verified separately by the final production mount check.

Fasten the pump before installing fluid-18 and the rear keystone jack, which obstruct straight driver access. Tightening torque, rubber compression, clip retention and hose-clamp retention are physical assembly observations. These reports establish geometry, not those forces. The filled hidden rail/casing envelopes overlap only the foot's upper clip region; `reference-clip-attribution.json` identifies those reference-envelope contacts and makes no manufactured interference or clip-fit claim.

The final input audit records the metadata-only reference manifest update without changing the original probe hashes. The later foam export contains the updated mounts; its fresh production mount validation confirms the same pump pose. Full regenerated assembly/scorecard and the new cap/lid slice reviews remain independent downstream evidence.

To verify the archive without CAD work:

```sh
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/installation/feet-correction-validation/reproduce.py verify
```

To repeat the bounded native probe, use a new private output directory and supply the exact baseline STEP named in `fixtures/baseline-assembly.json`. `--fetch-baseline` is an explicit alternative; downloads are verified before use. The replay refuses changed runtime geometry inputs. It changes only filesystem setup in the saved script and supplies the preserved foam datum.

```sh
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/installation/feet-correction-validation/reproduce.py neighbors --baseline-step /path/to/exact-baseline.step --output /tmp/g-ganen-neighbor-replay
tools/cad-venv/bin/python hardware/reference/g-ganen-pump/installation/feet-correction-validation/reproduce.py washer --output /tmp/g-ganen-washer-replay
```

The production mount validator is `../validate_installation.py --skip-hoses`; its executed source snapshot and exact final report are retained. No complete producer or printer command is part of this package.
