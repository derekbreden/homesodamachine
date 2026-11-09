# Native carbonator assembly boundary

The [carbonator lab](https://homesodamachine.com/labs/solidcraft/carbonator) evaluates opening and editing a small assembly without recursively loading its descendants' geometry or authoring histories.

## Native project

The tube and endcap are independent SolidCraft designs under `parts/`. The tube uses a fully constrained annular sketch and an extrusion; the endcap blank uses a fully constrained circular sketch and an extrusion. Their nominal stock and fit come from the production [tube](../../../cut-parts/carbonation/carbonator-tube/numbers.rs) and [endcap](../../../cut-parts/carbonation/endcaps-circular/numbers.rs) definitions. The example owns those inputs and imports no machine-layout code.

`carbonator.json` links the finished bodies of those designs. The tube is grounded. The endcap definition is placed at both ends and joined to the tube's named annular end faces with rigid joints. The recess is an assembly parameter; the cap placements follow the end faces when the tube changes length. The assembly retains an exploded view for inspecting the fit-up.

`representation.json` defines the assembly envelope with a native cylinder driven by the published tube exterior. It supplies the external diameter and end planes for layout. Exact seating, internal clearance, mass and manufacturing queries use the core or leaf design. The envelope is reference geometry in the assembly.

`parent.json` links that envelope as an opaque component. Its feature contains no tube or endcap geometry, sketch history, core component tree, or internal joints. It owns only the saved envelope body needed to show and place the module.

Native links retain their finished geometry in the parent file. The Import features are produced by SolidCraft's Insert Design and link update commands. Opening these assemblies does not update links. Explicit Update Links reads the selected source and replaces that component's saved bodies; its named faces preserve the assembly joints. Copies of the endcap share a definition.

## Evaluation boundary

This is the tube and unported endcap fit-up. Fluid ports, tapping, rod registers, floats, weld geometry, fittings and the cold-core casing are outside the example. The exercised edits are tube length, plate thickness and cap recess. Stock diameter, wall and diametral allowance define its nominal radial fit; geometry redesign across those interfaces is a separate operation.

The evaluation opens the core without its part files and opens the parent without the representation, core or part files. The browser leaf test edits the tube, publishes its exact native bodies and updates only its core link. The update coordinator reads the exact tube's finished exterior bounds. Changed bounds update the native envelope and its parent link. An internal cap or recess edit leaves the envelope unchanged and does not open its source. The endcap authoring design remains unopened during the tube test. [evaluation.json](evaluation.json) records the source hashes, native construction and reviewed cases.

This establishes both a representation boundary and an authoring-history boundary. Native linking loads the finished bodies embedded in the chosen representation together; it does not automatically stream nested geometry. The explicit envelope is the chosen substitute for parent layout. Visible geometry still occupies memory and needs drawing. Repeating the simple core tests definition reuse and request behavior; it does not benchmark the full enclosure's shapes or qualify its print interfaces.

## Website

The website's initial view loads the module interface and a saved envelope mesh. Selecting a component on the model or in its list highlights it and opens a component panel. **Open** enters that component's saved display; breadcrumbs and browser Back and Forward walk between the parent, core and individual occurrences. The canvas, camera position, roll and orbit point stay in place across that walk. Hide and Show affect only the current display. The preview reuses the parts viewer's camera controls and ViewCube and draws only when the view changes.

Opening the core requests its exact child display shapes and placements. A direct link to a leaf requests that leaf's display without loading sibling or ancestor display meshes. **Edit in SolidCraft** starts the native runtime and requests the selected workspace alone. Previously opened workspaces are kept separately in local browser storage and restored on request. Returning to a saved display, pausing or backgrounding unloads the native runtime after saving the current workspace.

The native update uses SolidCraft's own component extraction, link update, file save and joint solver. The browser writes the selected part into its in-memory native filesystem and updates its core link. When its published exterior changes, it supplies those inputs to the native envelope design, saves the evaluated envelope and updates the parent's link. Source files for unrelated leaves are not needed.

The reference preview is the published snapshot. Local edits appear in the native workspace; **Reference preview** returns to the published display. Downloads preserve the current native design, while the project download supplies the complete reference example.

`display_cache.py` packs SolidCraft's exported surfaces into module and leaf display representations. It merges coincident vertices and dissolves nearly coplanar tessellation edges; the recorded mesh volumes and bounds describe the packing. It changes no native part geometry. Its opaque module mesh carries no editable child tree. It is a manual asset producer outside ordinary builds and commits.

The packed native copies are generated from their JSON designs. Save each part as its matching native file and update the core's links. Publish its exterior dimensions to the envelope design, save that design and update the parent's link. Source designs and packed copies are included in the website's project download. The [lab implementation](../../../../web/public/solidcraft-lab/carbonator/) owns the isolated page, loading audit and display assets.
