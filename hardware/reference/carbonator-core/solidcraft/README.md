# Native carbonator assembly boundary

The [carbonator lab](https://homesodamachine.com/labs/solidcraft/carbonator) evaluates opening and editing a small assembly without recursively loading its descendants' authoring histories.

## Native project

The tube and endcap are independent SolidCraft designs under `parts/`. The tube uses a fully constrained annular sketch and an extrusion; the endcap blank uses a fully constrained circular sketch and an extrusion. Their nominal stock and fit come from the production [tube](../../../cut-parts/carbonation/carbonator-tube/numbers.rs) and [endcap](../../../cut-parts/carbonation/endcaps-circular/numbers.rs) definitions. The example owns those inputs and imports no machine-layout code.

`carbonator.json` links the finished bodies of those designs. The tube is grounded. The endcap definition is placed at both ends and joined to the tube's named annular end faces with rigid joints. The recess is an assembly parameter; the cap placements follow the end faces when the tube changes length. The assembly retains an exploded view for inspecting the fit-up.

`parent.json` links the finished carbonator as an opaque component. Its feature does not contain the tube or endcap's sketch histories, the core's component tree, or its internal joints. It owns the saved final bodies needed to show and place the module.

Native links retain their finished geometry in the parent file. Opening these assemblies does not update links. Explicit Update Links reads the selected source and replaces that component's saved bodies; its named faces preserve the assembly joints. Copies of the endcap share a definition.

## Evaluation boundary

This is the tube and unported endcap fit-up. Fluid ports, tapping, rod registers, floats, weld geometry, fittings and the cold-core casing are outside the example. The exercised edits are tube length, plate thickness and cap recess. Stock diameter, wall and diametral allowance define its nominal radial fit; geometry redesign across those interfaces is a separate operation.

The evaluation opens the core without its part files and opens the parent without the core or part files. The browser leaf test edits the tube, publishes its exact native bodies, updates only its core link, and updates the module's parent link. The endcap authoring design remains unopened. [evaluation.json](evaluation.json) records the source hashes, native construction and reviewed cases.

This establishes an authoring-history boundary. The final visible geometry still occupies memory and needs drawing. Repeating the simple core tests definition reuse and request behavior; it does not benchmark the full enclosure's shapes or qualify its print interfaces.

## Website

The website's initial view loads the module interface and a saved display mesh. Expanding it requests child display shapes and placements. Choosing a native workspace starts SolidCraft and requests that workspace alone. Previously opened workspaces are kept separately in local browser storage and restored on request. Pausing or backgrounding unloads the native runtime after saving the current workspace.

The native update uses SolidCraft's own component extraction, link update, file save and joint solver. The browser writes the selected part into its in-memory native filesystem, updates its core link, saves the evaluated core, and updates the parent's module link. Source files for unrelated leaves are not needed.

The reference preview is the published snapshot. Local edits appear in the native workspace; **Reference preview** returns to the published display. Downloads preserve the current native design, while the project download supplies the complete reference example.

`display_cache.py` packs SolidCraft's exported surfaces into module and leaf display representations. It merges coincident vertices and dissolves nearly coplanar tessellation edges; the recorded mesh volumes and bounds describe the packing. It changes no native part geometry. Its opaque module mesh carries no editable child tree. It is a manual asset producer outside ordinary builds and commits.

The packed native copies are generated from their JSON designs. Save each part as its matching native file, update the core's links and save the core, then update the parent's link. Source designs and packed copies are included in the website's project download. The [lab implementation](../../../../web/public/solidcraft-lab/carbonator/) owns the isolated page, loading audit and display assets.
