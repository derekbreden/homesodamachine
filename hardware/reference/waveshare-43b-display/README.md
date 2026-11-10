# Waveshare enclosure display reference

`replica.rs` makes the purchased display's mounting glass, LCD chassis and major
rear interfaces as clean planes, cylinders and molded profiles. The physical
glass measurements set the enclosure mounting datums. The rear PCB, connector
placement and package bounds come from the manufacturer's mechanical assembly.
[The evidence record](replica-evidence.json) names the sources, coordinate mapping
and retained measurements.

The glass faces forward along negative Y. X crosses the screen and Z runs up it.
The front glass face is the depth origin. The LCD chassis retains the measured
body center; the glass carries its measured lateral and vertical offsets.

The model includes the routed PCB edge reliefs, antenna notch, display-cable
slot and mounting holes; the terminal socket and removable plug with their
broad stepped profile, wire-entry tapers and screw access; the rounded USB
mouth and tongue; and the principal card, radio, switch, FPC and power packages.
The `body` name identifies the LCD chassis and `bezel` identifies the mounting
glass. Rear components have their own body names and material colors.

`terminal-interfaces.json` owns the plug's mouth profiles, rear-face stations and
manufacturer-labeled pole order for both the replica and installed wiring.
The retained supplier interface photograph establishes that order. The record
distinguishes those labeled bindings from received-part electrical validation.

The smaller connector housings and component packages retain supplier exterior
bounds. Fine lead geometry, tiny passives, markings, hidden contacts and wire
clamps are omitted. Rear component positions follow the supplier assembly and
have no received-part caliper verification. The measured glass datums remain
the source for the conforming enclosure mount.

Regenerate through the shared run wrapper:

```sh
tools/run -- cargo run --release --locked -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-sandbox \
  --example waveshare-replica -- hardware/reference/waveshare-43b-display
```

`frozen-asset.json` binds the published files to their native source. Layout and
wiring read the saved model and terminal-interface data directly. The native
`part-data` reference provider also exposes the measured display dimensions.
