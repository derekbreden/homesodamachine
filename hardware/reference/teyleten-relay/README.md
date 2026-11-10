# Teyleten relay — exterior replica

The purchased relay module switches the compressor and diaphragm pump from
back-top's dry wall. Both PCB ends carry screw terminals. The contact terminals
are at positive X; the control terminals are at negative X. The housings' broad
wire mouths face outward at opposite PCB ends; their narrower rear inspection
windows face inward. Z rises from the PCB underside toward the components.

The frozen model uses clean molded housing cross-sections, flat relay-can faces,
rounded wire mouths, rear inspection windows and recessed terminal screws.
The substantial control packages and jumper use idealized exterior silhouettes.
Its PCB outline and mounting openings use fitted scan datums. Observed solder
tips use smooth closed envelopes at their measured positions and downward extent.
[scan-datums.json](scan-datums.json) owns these dimensions and the wire-entry
interfaces exposed by [teyleten_relay.py](teyleten_relay.py).

[scan_model.rs](scan_model.rs) prepares the reference manually from those datums;
this purchased part has no normal build.
[frozen-asset.json](frozen-asset.json) identifies its STEP, native model and
display payload. [scan-model-evidence.json](scan-model-evidence.json) identifies
the native capture, its rigid frame and exterior face and screw-well fits.

Putty-covered underside features are absent. The mounting openings fit their
visible front rims; bore walls and deep terminal cavities are not fully
observed. Recesses close behind their visible mouths; concealed terminal
internals are absent. Scanning spray remains in the measurements, and fitting
residuals do not establish absolute accuracy or installation clearance. The
[enclosure mounting
review](../../printed-parts/enclosure/enclosure/relay-mount-fit.json) defines
the screw stack and measured geometry scope; physical load retention remains
unqualified.
