# PGFUN two-axis weld positioner shop guide

The [assembly guide](gun-positioner-guide.pdf) uses the shared Letter shop-guide
theme: IBM Plex, cobalt/coral page bands, ice panels, numbered actions and
visible ready checks. Its clickable contents and PDF bookmarks lead to the
operations. Current CAD pictures sit beside the corresponding assembly step.
The wiring and learning diagrams precede their detailed instructions.

It includes printing, the complete Prime parts list, exact fastener allocation,
wiring, firmware setup, loaded commissioning and one-camera learning/replay.

The [build package](../gun-positioner/README.md) links editable CAD and
governing source instructions. The [source receipt](source-receipt.json)
binds this PDF to its inputs. Rebuild it with
`tools/cad-venv/bin/python tools/gun-positioner-guide/build.py`.

Print at **100%**, single-sided, Letter portrait. Content is centered at 98%,
with a separate full-scale cobalt/coral bleed layer. For Epson Letter
borderless printing, select the matching paper profile and rear feeder
explicitly; the [shared print instructions](../assembly/guides/README.md#epson-letter-photo-printing)
describe those settings.
