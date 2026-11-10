# Native carbonator assemblies

The [carbonator lab](https://homesodamachine.com/labs/solidcraft/carbonator#parent) evaluates saved assembly shapes, nested component navigation and native editing without loading child histories.

## Assembly boundaries

The native project follows the material ledger: instrumented carbonator and coil, fitted carbonator vessel, vessel weldment, prepared cap groups and magnetic float. The cap groups open into the machined cap, guide rod and upper stop; the float opens into its shell and ring magnet. Each assembly links only the published shapes of its direct children. The repeated parent links the instrumented assembly's exterior as an opaque component.

Published references contain finished bodies in a single native import component. They contain no live source links, child component definitions, sketches or assembly joints. The weldment exterior retains its barrel, cap inset, clearance and ports. Its float, guide rod, upper stop and the tapped bore hidden under the attached earth clamp remain in the owning designs. The barrel's cylindrical faces supply the published barrel dimensions. Fittings, coil, shroud, bridge and sensor envelopes remain recognizable at the outer levels.

The water adapter, installed tubing, insulation casing and equipment lid belong outside the instrumented assembly. The earth lead publishes its attached ring, crimp barrel and conductor exit interface; free conductor dressing belongs to installation. Bought parts use the repo's capture envelopes. Thread helices, weld beads, tooth serrations and electronic internals are omitted.

## Native construction

The Rust producer reads the owning tube, cap, float, bridge, coil and assembly interfaces and emits SolidCraft command histories. It starts no machine CAD build. The finished rod drawing supplies the flat-ended rod and drill-point seat calculation. Native cylinder and cone cuts retain the blind registers. The cap's register follows its thickness, depth and drill-point parameters.

The float shell contains its guide bore and enclosed annular magnet pocket. Its own assembly seats the ring magnet. A bounded native slider retains captive float travel in the weldment. Rigid joints hold the fixed physical assemblies at their authored fits. Controlled stock and welded-part dimensions remain design inputs; changing them calls for matching their owning interfaces.

The reed bridge uses a revolved radial profile, a plan intersection, pocket cuts and lead grooves. The copper uses a native spatial spline over the bridge, exact arc and line tails, and pipe features with the specified stock wall. Face splits retain the winding through native reference imports. They preserve the tube's solid geometry.

The native JSON designs under native/ are editable in SolidCraft. Packed copies in the project download retain evaluated geometry. The separate [core blank study](https://homesodamachine.com/labs/solidcraft/carbonator/core-study#parent) uses parts/, carbonator.json, representation.json and parent.json for its annular tube, unported discs and face-driven recess experiment.

## Website and local editing

Selecting geometry or a component row highlights it and opens the component panel. Open enters that component. Breadcrumbs and browser Back and Forward retain the viewer and camera. Hide, Section and Explode affect the local display. A direct leaf link requests its display and ancestor placement metadata; it does not request ancestor or sibling meshes.

The initial page loads a combined saved exterior. Repeated occurrences share its display geometry and draw call. Opening an assembly uses only its direct saved shapes. A child mesh already included in the parent's package is reused without another download. Native authoring starts only through Edit. The selected native file retains finished geometry, so linked source files remain closed.

The default display reads SolidCraft's saved preview manifest and binary mesh entries. The native document and payload digests bind the mesh to its saved design. Surface coordinates and triangles are retained; the browser supplies shading normals and component picking. When a combined preview exceeds the native cache budget, an assembly package holds its direct children's native saved meshes and native occurrence placements. A leaf without a saved preview uses SolidCraft's native mesh export. This packaging and browser navigation belong to the lab; they are not standalone SolidCraft representation management.

Compare display paths switches to the retained packed preview for visual and loading comparisons. Both paths defer the native editor. The browser's timing list measures opening a display after the viewer starts, rather than the whole page and its scripts. The evaluation record identifies the measured model, payload sizes and publication timings.

Browser workspaces persist separately in IndexedDB. Pausing or leaving native editing saves the current document and unloads the runtime. Update parents writes the changed design to the native filesystem, updates selected links and republishes affected references. Published source geometry, solved placements and appearance identify unchanged exteriors, so an internal float move can stop at the weldment boundary. Shared cap edits reach both cap groups. Other leaf sources remain closed.

Local native edits appear in the native workspace. Reference preview shows the published website snapshot. Downloads retain the current native design. Assembly references serve display and placement; manufacturing and aggregate mass use the owning detailed designs.

## Manual production

The producer, native display publisher and manifest publisher run only for this lab, outside ordinary builds and commits. The display command extracts native saved meshes, packages shallow assembly displays and reuses payloads whose native sources and dependencies match. It uses the CLI's cached-open path to prepare absent previews; the CLI reports whether it adopted the saved CAD model or recomputed features. The manifest publisher writes shallow manifests and the downloadable native project. Evaluation records live in the lab's levels-evidence.json.

From the repository root:

```sh
solidcraft_run=$(mktemp -d .cache/runs/solidcraft-levels-XXXXXX)
CARGO_BUILD_JOBS=2 python3 tools/run.py -- cargo run --release --manifest-path hardware/reference/carbonator-core/solidcraft/producer/Cargo.toml --target-dir tools/hsm/target -- build --out "$solidcraft_run"
CARGO_BUILD_JOBS=2 python3 tools/run.py -- cargo run --release --manifest-path hardware/reference/carbonator-core/solidcraft/producer/Cargo.toml --target-dir tools/hsm/target -- display --out "$solidcraft_run"
python3 hardware/reference/carbonator-core/solidcraft/publish_levels.py
```

Run display on its own to refresh website meshes from existing packed native designs. The packed comparison is a fixed comparison artifact. Keep concise reviewed results in the evaluation record and remove the temporary run after publication. The native JSON histories and project download retain the deliverables.
