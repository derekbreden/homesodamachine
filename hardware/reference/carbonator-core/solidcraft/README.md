# Native carbonator assembly boundary

The [carbonator lab](https://homesodamachine.com/labs/solidcraft/carbonator) evaluates a recognizable saved assembly shape whose child designs remain closed.

## Native project

The tube and endcap are independent SolidCraft designs under parts/. The tube uses a fully constrained annular sketch and an extrusion; the endcap blank uses a fully constrained circular sketch and an extrusion. Their nominal stock and fit come from the production [tube](../../../cut-parts/carbonation/carbonator-tube/numbers.rs) and [endcap](../../../cut-parts/carbonation/endcaps-circular/numbers.rs) definitions. The example owns those inputs and imports no machine-layout code.

carbonator.json links their finished bodies. The tube is grounded. Copies of the shared endcap definition join to the tube's named annular end faces with rigid joints. The recess is an assembly parameter; cap placement follows those faces when the tube changes length. A native exploded view retains the fit-up.

representation.json defines a finished reference shape in its own component using native cylinder primitives: a bored barrel and recessed cap discs. It retains the tube wall, the clearance around the caps and their inset faces. Its bodies have no child component definitions, linked part designs, sketches or assembly joints. The small core's barrel and caps all contribute to its exterior, so their simple shapes are retained.

parent.json links those finished reference bodies as an opaque component. Opening it reads no representation, core or leaf source file. Native links retain the finished geometry in the parent file. Explicit Update Links reads the selected source and replaces that component's saved bodies.

## Published exterior

The update coordinator measures the exact core's cylindrical tube faces and solved cap placements. The tube radii, barrel length, cap diameter, plate thickness and end recesses drive the reference shape. Changes to those inputs refresh the native reference design and its parent link. Source files for unrelated leaves stay closed.

The parent and core retain the same assembled appearance and finish. A collapsed component keeps the visible geometry published for that level. Native linking loads its saved bodies together and does not automatically stream individual bodies inside a representation. Visible detail still consumes display geometry; the reference shape avoids recursively opening child designs.

This example includes the barrel and unported endcap blanks. Fluid ports, tapping, rod registers, floats, welds, fittings and the cold-core casing belong outside it. The exercised edits are tube length, plate thickness and cap recess. Arbitrary redesign across stock and fit interfaces is a separate operation. Exact fit, mass and manufacturing work uses the core or leaf design.

The repeated-module case evaluates shared display geometry, native links and source request behavior. It does not measure complete-enclosure performance or qualify production print interfaces. [evaluation.json](evaluation.json) records the native source hashes and reviewed cases.

## Website

The initial view loads the module interface and a saved exterior mesh. Selecting a component on the model or in its list highlights it and opens a component panel. **Open** enters that component's saved display; breadcrumbs and browser Back and Forward walk between the parent, core and individual occurrences. The canvas and camera stay in place. Hide and Show affect only the local display.

Opening the core requests its exact child display shapes and placements. A direct leaf link requests that leaf's display without loading sibling or ancestor meshes. **Edit in SolidCraft** starts the native runtime and requests the selected workspace alone. Local workspaces are stored separately and restored on request. Returning to the reference display, pausing or backgrounding unloads the native runtime after saving the current workspace.

The native update uses SolidCraft's component extraction, link update, parameter editing, file save and joint solver. The selected part is written to its in-memory native filesystem before its core link is updated. The finished core supplies the inputs to the saved exterior; the parent then updates that reference link.

The reference preview is the published snapshot. Local edits appear in the native workspace; **Reference preview** returns to the published display. Downloads preserve the current native design. The project download supplies the reference source designs and their evaluated packed copies.

display_cache.py packs native exported surfaces into module and leaf display assets. It merges coincident vertices and dissolves nearly coplanar tessellation edges without changing the native geometry. The parent display is a combined mesh with no editable child tree. Its placements share the mesh. The producer is manual and outside ordinary builds and commits.

Generate packed copies from their JSON designs. Save each part and update the core's links, publish the core's exterior inputs to the reference design, save that design and update the parent's link. The [lab implementation](../../../../web/public/solidcraft-lab/carbonator/) owns the isolated page, loading audit and display assets.
