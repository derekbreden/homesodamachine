# Full Pisco with shorter axial grip

The preceding cover held the regulator steady across its diameter. Derek could still slide the regulator along its axis. Three features on the housing moved about 0.55 mm relative to the printed parts in the clearest stroke on film. He pointed to the face beside the short, white outlet ring as the place to tighten the grip. [Hand test and image measurements](../../prints/2026-11-25-mark2-two-dot-drop/physical-result.json)

The cover lip reaches **0.24 mm farther toward the rear bore** to catch the shoulder on the rigid aluminum outlet fitting. Each receiver pocket starts **0.12 mm farther back**, so the cover can slide forward by 0.12 mm less. These changes shorten the end-to-end grip by **0.36 mm total**. Both pieces carry two exterior dots. The middle of the long snap guide follows the closest of the latest tested profiles, and the saddle retains the previous cover’s 0.20 mm adjustment. [Coupon comparison](../../../open-snap-section/prints/2026-11-25-mark1-refinements/physical-result.json) · [Geometry and native measurements](fit-check.json)

## Try the fit

1. Rest the receiver on its flat roof. Point the long inlet neck toward the rear bore, with the short outlet facing the open end. Lower the regulator into the channel about 16 mm forward and slide the long neck back into its seat.
2. Point the cover’s raised lip toward the short outlet. Keep the cover toward the open end of its small fore/aft clearance. Press above the wings until both hooks seat.
3. Hold the receiver, move the regulator body gently fore and aft, and watch the white ring relative to both printed parts. Check side-to-side rocking and turning separately. Compare with the preceding full pair using the same regulator.
4. Spread the exposed wings and remove the cover for tube-release access. In the installed corner, remove the ASSE and meter groups first, then reverse the short straight closing stroke and tilt the cover past the meter shoulder. [Service geometry](../../../../printed-parts/enclosure/rear-equipment-caps/README.md)

The submitted Mark2 paths leave about **0.016–0.056 mm** of rigid axial travel, depending on where the housing sits against the receiver. The modeled short ring stays clear of the lip at both ends. The hand comparison will establish the motion and removal effort of the cooled parts. [Axial limits and ring clearance](fit-check.json)

## Reproduce

From the repository root, generate the full pair with the axial-grip option. The cover prints on its short-outlet end and the receiver prints roof-down. [Part frames and hashes](geometry.json) · [Receiver print features](receiver.print-features.json)

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin pisco-wide-snap -- --axial-grip
```
