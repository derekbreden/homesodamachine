# Native handhold

The [isolated feature study](https://homesodamachine.com/labs/solidcraft/features?study=handhold) evaluates a native mechanical construction against functional appearance, usable grip space and editing behavior.

`handhold.sc` is the primary editable SolidCraft model. `handhold.json` is the same native parametric document in the supported plain format. The model contains constrained section sketches, native circular sketch fillets, lofts and a stock cut. Named opening and roof parameters drive the section dimensions. The saved native model is the edit path; its construction helper is retained with the downloadable study sources.

`interfaces.json` records the source enclosure dimensions and the deliberate plain stock fixture. The model excludes quadrant seams, exterior fluting and adjacent assembly attachments. It is a feature study, not a production quadrant replacement. Its mouth treatment intentionally uses chamfer and conical transitions. The current Rust handhold supplies context rather than an equality requirement.

The website retains the current reference, native candidate, native dimension edit, native project downloads and print geometry. Its `results.json` holds native feature counts, solved constraints, geometric dimensions, underside slopes, hashes, command-time observations and bounded failed constructions. Those command times exclude source authoring and tool recovery. Physical grip, printing and strength remain untested.

The associated native-feature fixtures show working face constraints and shell/rim edits, the scope of the snap primitive, and a measured unintended boss-axis movement. Their native source and observations are downloadable from the same page. Nothing in this study joins a normal build or commit check.
