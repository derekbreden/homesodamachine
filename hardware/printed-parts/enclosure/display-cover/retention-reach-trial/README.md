# Display-cover low-force clearance trial

Two complete covers fit the same [broad-leaf receiver](../retention-trial/README.md).
Both have centered 75 mm leaves, 3.6 mm square hooks, 0.9 mm inward leaf positions,
0.8 mm root fillets and the same bezel and window. Only the straight arm length varies.

| Cover | Printer | Extra arm reach | Increase from the shake-tested cover | Hook shoulder below face | Nominal catch clearance |
|---|---|---:|---:|---:|---:|
| `display-cover-retention-reach-060` | Mark2 | 0.60 mm | 0.10 mm | 11.10 mm | 1.08 mm |
| `display-cover-retention-reach-075` | H2C | 0.75 mm | 0.25 mm | 11.25 mm | 1.23 mm |

Physical evaluation checks full hook engagement, remaining bow, free play and shake
retention in the existing receiver. The printed contact finish contributes to the fit;
the nominal CAD clearance alone does not measure it.

## Next after cover selection

The requirement is **low-force clearance for rough overhang surfaces involved**.
After Derek selects a cover, apply this requirement to the tee carrier's sliding fit.
Use the cover's measured fit as evidence and check the carrier's own supported contact
surfaces, motion and retention. A universal numeric clearance is not established.

`retention_reach_trial.py` writes both cover STEP/STL/viewer triplets. The existing
receiver remains the test fixture. Printer starts use the three-minute minimum stagger.
