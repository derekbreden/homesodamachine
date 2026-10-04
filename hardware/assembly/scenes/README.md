# Assembly scenes

Named subsets of the built machine, posed for the parts viewer and local bench
service views. A scene's roots are the printed pieces that carry a unit; its
members come from the fastening, rider, anchor and bearing tables in
[_scenes.py](_scenes.py). The cold-core members use that model's own solids in
the machine's frame.

`enclosure_assembly` calls [write_glbs](render_scenes.py) on the machine it has
already built and the exact current surface payloads. The resulting `glb/`
files travel with the CAD artifacts. Scene publication does not start a browser
or build the appliance again. [The local service view](_local_service.py) cuts
the same subsets for its bench inspection.

[Letter shop guides](../guides/README.md) own the human instructions. Their
illustrations and PDFs are authored and built by hand outside the CAD graph.

```sh
tools/cad-venv/bin/python hardware/assembly/scenes/render_scenes.py selftest
```
