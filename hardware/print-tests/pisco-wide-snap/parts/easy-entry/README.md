# Full Pisco push-on pair

The full cover and receiver for the Pisco RVFUP1/4–1/4-0.3 each have one exterior dot. The short one-dot coupon on the same Mark2 plate has the same spring and receiver sections. The full part adds the regulator cradle, axial stops and end guides. [Part geometry](geometry.json) · [Coupon comparison](../../../open-snap-section/parts/easy-entry/bench.md)

## Try the push-on

1. Rest the receiver on its flat roof. Try the cover once with the channel empty. Set it squarely over the receiver and press above both wings. Check whether the feet find the entrance with a direct push.
2. Remove the cover. Point the long inlet toward the rear bore and the short white outlet toward the open end. Lower the regulator into the channel about 16 mm forward of its seat, then slide the long inlet into the bore.
3. Point the cover’s raised lip toward the short outlet. Center the cover over the regulator and press above both wings. Let the cover shift slightly toward the outlet as the end guides line up. The round regulator starts to spread the wings before they reach the receiver. Compare the starting effort and click with the empty pair and the short one-dot coupon. [Entry measurements](fit-check.json)
4. Hold the receiver and gently push and pull the **rigid metal outlet**. Watch a metal groove relative to the cover lip, then relative to the fixed receiver. The white release ring has its own travel. Repeat with the previous full pair under the same hand load. In the earlier recording the rigid metal moved about **0.4 mm**, with individual strokes of **0.3–0.5 mm**. [Hand-test measurements and images](../../prints/2026-11-25-mark2-axial-grip/physical-result.json)

The new cover has a broad bearing against the **lower aluminum taper just behind the short neck**. To see whether it carries load, put a thin removable transfer mark on that metal taper and, separately, on the molded shoulder at the rear bore. Keep the marks clear of the fitting mouths, seals and release rings. Seat the cover, repeat the gentle push and pull, then inspect both contact patches. A fixed camera showing the metal grooves, cover lip and receiver together can distinguish movement at the cradle from movement of the cover.

The submitted toolpaths put the new taper bearing **0.022 mm** from contact when the existing radial saddle first seats at the modeled registration. Both hooks already overlap the receiver by about **0.80 mm** there. Another 0.051 mm of closing brings 7.1 mm of the taper width into contact. The original rigid axial stops are still in place. The assembled hand test will establish the resulting movement and force. [Toolpath and installed-fit measurements](fit-check.json)

Spread the exposed wings and lift the cover for tube service. The long inlet ring extends beyond the receiver. With the cover lifted, the short release ring has over 4.8 mm of clearance to the receiver through a modeled 2.10 mm axial sweep. In the installed corner, remove the ASSE and meter groups, spread the wings and reverse the short straight closing stroke before tilting the cover past the meter shoulder. [Installed access](../../../../printed-parts/enclosure/rear-equipment-caps/README.md)

## Reproduce

Generate the full pair from the repository root. The cover prints on its short outlet end and the receiver prints roof-down. [Part frames and hashes](geometry.json) · [Receiver print features](receiver.print-features.json)

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin pisco-wide-snap -- --easy-entry
```
