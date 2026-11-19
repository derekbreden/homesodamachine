# Inclined support release

These prepared plates compare gap and tree algorithm while retaining the shared
D dense interface. The [faucet lower-curve result](https://github.com/derekbreden/homesodamachine/blob/7b4d4c7d87dda9db021665b2e7c7e255d996a39d/hardware/print-tests/petgf-dense-roofs/D-representative-mark2/physical-result.json)
records stems breaking with contact material retained on the part. The flat rail
acceptance does not qualify this inclined contact.

The [frozen-article contact reading](contact-reading.json) separates missing roof
generation from physical release. Default emits interface paths in a low band
while bare tree paths continue along the higher curve. Explicit Tree Slim emits
interface paths into that curved band at the same requested contact gap and
density. Increasing the general XY distance alone leaves the upper interface
absent. The [Mark1 Slim removal result](https://github.com/derekbreden/homesodamachine/blob/be19fb8a4693edecead5753aa2bcb42c54dcdbf0/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-mark1/physical-result/physical-result.json)
records retained contact material despite screwdriver prying. Roof generation
alone does not qualify release.

Each coupon has a single anchoring wall and open remaining edges. Its bed tab
carries an identifier without anchoring the free roof edges. Native targets cover
the inclined underside. The [matrix](matrix.json) owns the geometry, incline
angles, gap settings and shared process. Angles are measured from the bed plane.

| Plate | Comparison | Files |
| --- | --- | --- |
| Faucet curve | The frozen failed faucet article in its original build pose, with explicit Tree Slim as the only retained-object setting change. | [Editable project](https://homesodamachine.com/print-archive/c18067afa062d1d3d7117ccf5e32961092152c98/faucet-slim.3mf), [native archive](https://homesodamachine.com/print-archive/2d9c55609158a4ebdd36f937537dd7eb90bbe073/faucet-slim.gcode.3mf), [estimate and preparation](plates/faucet-slim/preparation.json), [native previews](plates/faucet-slim/preview/preview.json) |
| Gap | Matching inclines at different gaps with Default trees, which resolve to Organic for these coupons. | [Editable project](https://homesodamachine.com/print-archive/62a5f98be53923b36a9e8d8ab3be6740054f3deb/inclines-gap.3mf), [native archive](https://homesodamachine.com/print-archive/207f22831a25e97aa3c23f88398373c01374b55a/inclines-gap.gcode.3mf), [estimate and preparation](plates/inclines-gap/preparation.json) |
| Tree Slim | The same inclines and gaps with explicit Tree Slim. Compare each specimen with its counterpart on the gap plate. | [Editable project](https://homesodamachine.com/print-archive/60c83120986bfc785a9b6ac7730a14baae4d1af4/inclines-slim.3mf), [native archive](https://homesodamachine.com/print-archive/6481f53a02209b5d8501696bd6759a275b83d12d/inclines-slim.gcode.3mf), [estimate and preparation](plates/inclines-slim/preparation.json) |

Interface spacing and layer count, bridge flow, bridge speed, localized cooling,
side clearance, material and model layer schedule remain common. Tree algorithms
place different contact footprints; equal roof density does not establish equal
coverage. The [verification](verification.json) binds the selected object settings
to the emitted native support paths. Requested gaps remain slicer inputs rather
than measured physical air clearances. Each archive uses Mark2's calibration.

The [previews](preview/) draw the authored coupon triangles and commanded support
bead envelopes through the native renderer. Model stock, support stems and dense
interface paths have separate display colors. The envelopes illustrate the slice;
they do not simulate molten material, sagging or adhesion.

The planar plates are prepared and unprinted. The [completed larger-gap Mark1 trial](https://github.com/derekbreden/homesodamachine/blob/a261387d7021b9f74675793f5b1a3fd188cfccec/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-gap048-mark1/physical-result/physical-result.json)
records easier support removal with connected roof mats and essentially
unchanged underside finish. It increases the top contact gap after the
[completed Slim trial](https://github.com/derekbreden/homesodamachine/blob/be19fb8a4693edecead5753aa2bcb42c54dcdbf0/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-mark1/print-job.json)
failed release. It retains the dense interface, model, pose, side clearance,
cooling and printer calibration. The [contact comparison](https://github.com/derekbreden/homesodamachine/blob/a261387d7021b9f74675793f5b1a3fd188cfccec/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-gap048-mark1/separation.json)
reads the emitted interface and model bead envelopes; it does not measure
molten material or removal force.

The [stopped rim-fin trial](https://github.com/derekbreden/homesodamachine/blob/534b87cc5f8d6911f8bcfa38378116d8dcdcb6bd/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-rim-fins-mark1/physical-result/physical-result.json) records the dense
interface and trees releasing together with open heat-insert pockets.
The [current Mark1 trial](prints/2026-11-11-faucet-trees-only-mark1/print-job.json) uses trees, a dense roof,
a perimeter that follows the suspended rim, and bridged insert pockets.

The installed slicer's [style selection](https://raw.githubusercontent.com/bambulab/BambuStudio/v02.08.02.61/src/libslic3r/Support/SupportParameters.hpp)
resolves Default to Organic for these fixed-height, non-soluble tree supports.
Its [Organic settings](https://raw.githubusercontent.com/bambulab/BambuStudio/v02.08.02.61/src/libslic3r/Support/TreeSupportCommon.hpp)
use a distinct overhang XY clearance limited by external perimeter width and
round the top distance to layer steps. The [other tree path](https://raw.githubusercontent.com/bambulab/BambuStudio/v02.08.02.61/src/libslic3r/Support/TreeSupport.cpp)
provides explicit Slim contact generation and roof clipping. These differences
justify the comparison; they do not establish the cause of the retained faucet
material from photographs alone.

The [geometry source](samples.rs) runs as the `support-inclines` sandbox example.
The [plate preparer](prepare.rs) runs as the `incline-support-plates` binary in
`hsm-print-prep`, taking a run directory and optional `--slice`. Run either through
`tools/run` with the shared Cargo manifest. Neither contacts a printer.
