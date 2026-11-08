# Teyleten relay — scan reference

The purchased relay module switches the compressor and diaphragm pump from
back-top's dry wall. Both PCB ends carry screw terminals. The contact terminals
are at positive X; the control terminals are at negative X. Their wire openings
face positive X. Z rises from the PCB underside toward the components.

The frozen model preserves the observed terminal housings, screw wells, relay
can and control components. Its PCB outline and mounting openings use fitted
scan datums. Observed solder tips use closed envelopes of their scan points.
[scan-datums.json](scan-datums.json) owns these dimensions and the wire-entry
interfaces exposed by [teyleten_relay.py](teyleten_relay.py).

[scan_model.rs](scan_model.rs) prepares the reference manually from the archived
reconstruction; this purchased part has no normal build.
[frozen-asset.json](frozen-asset.json) identifies its STEP, native model and
display payload. [scan-model-evidence.json](scan-model-evidence.json) identifies
the native capture, its rigid frame, preparation and surface comparison.

Putty-covered underside features are absent. The mounting openings fit their
visible front rims; bore walls and deep terminal cavities are not fully
observed. Closed unobserved surfaces are reconstruction closures. Scanning spray
remains in the measurements, and the surface comparison does not establish
absolute accuracy or installation clearance. The [enclosure mounting
review](../../printed-parts/enclosure/enclosure/relay-mount-fit.json) defines
the screw stack and measured geometry scope; physical load retention remains
unqualified.
