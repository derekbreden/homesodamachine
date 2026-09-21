# Tee integration checks

The measured PP0208E radial envelope is integrated into the production reference,
manifold, carrier, release-wall journals and water split. `tee-integration.json`
records native checks of the coupled tee/valve/carrier region and every input
SHA-256. Its `print_release` is false: a local geometry pass does not release the
complete enclosure.

| Interface | Current dimension |
|---|---:|
| Documented nominal collar diameter | 16.3 mm |
| Rounded scanned collar envelope, including draft | 16.5 mm |
| Rounded fixed root envelope | 14.0 mm |
| Printed journal diameter | 17.0 mm |
| Carrier trough radius | 8.75 mm |
| Run span, extended / both sleeves pressed | 42.5 / 39.2 mm |
| Sleeve stroke / connected nose gap | 1.65 / 0.5 mm |
| Release-to-connected / full aft guide stroke | 2.15 / 4.65 mm |
| Tee bearing line | Y109.360 mm |
| Tee axis elevation | Z186.174 mm |
| Retained backing at each tee | 2.5 mm |
| Retained backing above each tee | 5.504166 mm |
| Deck separation | 60.95 mm |
| Air at complete aft-valve post insertion | 0.25 mm |
| Spring axes | X±97.535, Z211.209 mm |
| Fixed spring floor / moving release floor | Y87.460 / Y106.960 mm |
| Cartridge tube projection from barb station | 17.626 mm |

The collar envelope is a rounded reading of the scanned sample, not a production
manufacturing tolerance. The run and branch root/collar fit intervals are interior
patches. Conservative shoulders connect their envelopes without treating a patch
boundary as a manufactured edge.

`verify_tee_integration.py` checks the exported reference against those fitted
surfaces and bench spans; places the actual valve solids and corrected pump
stations; derives the same carrier/plate interface as the appliance; reads the
regenerated native carrier halves; and checks their local fixed wall, all operating
states, upper backing and full post-entry position. It also checks the water split's
distinct run and branch faces. Full carrier installation sweeps against all enclosure
parts remain the appliance assembly's separate check.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/verify_tee_integration.py
```

The production tee source explicitly retains three unqualified layout proxies:
branch extended face 20.07 mm, body/sleeve split 16.95 mm, release-nose radius 5.715 mm.
The minimum tee qualification is the requested **fully extended branch face to the
back of the widest run collar** caliper reading, plus identification of the **actual
moving terminal rim versus fixed small barrel** and its usable release-contact
surface. The known 1.65 mm stroke supplies the pressed face once the absolute face
is established. No new complete tee scan is necessary for that absolute reading.

Changing the absolute branch datum affects the shared reference, manifold lateral
stations/deck origin, release plate, carrier placement, water split and connected
tube endpoints. Those consumers remain linked to one source. Final release also
requires the measured spring ID/capture design, pump clamp qualification, regenerated
whole enclosure checks, current support-removal audit and exact slice identity.
The root [print-readiness report](../print-readiness.md) owns that combined status.
