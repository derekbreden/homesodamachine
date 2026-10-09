# Letter shop guides

Illustrated 8.5 × 11 inch instructions for the shop. The
[weld rotator build guide](../../weld-rotator-guide/README.md) sets the standard:
one useful picture per step, the part and tool in the working pose, a short
sequence of actions, and a visible check before the next operation.

| Guide | Work it covers |
|---|---|
| [Faucet assembly](../../faucet-assembly-guide/README.md) | Faucet, rear display pin map on page 2, vent bungs, mount stack and umbilical |
| [Drilling and cutting](../../drill-and-cut-guide/README.md) | Endcap preparation and registers, rod and tube stock, tiny inlet jet, plumbing and harness cuts, finishing |
| [Molds](../../mold-guide/README.md) | Silicone funnel tooling and casting, foam caps, cold-core body pour and demolding |
| [Refrigeration](../../refrigeration-guide/README.md) | Coil and probes, donor circuit, opening and joining, leak and vacuum work, charge and commissioning |
| [Drill and weld bench sheets](../letter/README.md) | The endcap register, closure weld setup, pedal and trigger sequence |
| [Weld rotator](../../weld-rotator-guide/README.md) | Building, checking and operating the rotation fixture |
| [Gun positioner](../../gun-positioner-guide/README.md) | PGFUN swivel/pivot fixture, controller wiring, one-camera dry learning and loaded commissioning |

The [document shelf](https://homesodamachine.com/drawings) carries each complete
PDF. Fabrication procedures under `hardware/assembly/` and physical qualification
records beside the parts own the operating requirements and accepted results.
A guide identifies an unresolved recipe or service qualification where that
operation reaches it.

## Authoring

The guides, illustrations, PDFs, cover thumbnails and document sidecars are
committed files. Their builders live under `tools/` and run by hand. They have
no CAD/Bazel target, scene-render dependency, sync gate or full-machine build
step. A geometry edit does not regenerate a guide. Review the affected operation
when its tool, datum, fit, material or process changes; source manifests record
what a manual build used.

Use the rotator guide or the Letter bench-sheet style for additional operations.
Give each operation enough space for its picture and bench-readable actions.
Show motion as a sequence. Keep dimensions beside their datum, distinguish a
schematic from a full-size template, and place the pass/hold check at the step
where it changes what the operator does.

`tools/assembly-guides/common.py` supplies the vector Letter page furniture.
`hardware/guide-assets/fonts/` supplies shared webfonts for HTML guides. These
assets carry no assembly or geometry logic.

## Epson Letter photo printing

The Letter bench sheets and new shop guides have instructional content centered
at 98%, with a separate full-scale bleed layer. The cobalt top and coral right
bands extend 1/3 inch inward and 1/4 inch beyond the page edges. Print at **100%**
with no additional reduction, single-sided, portrait, color and high quality.
Select **Letter borderless**, the matching photo-paper profile, and the **rear
feeder** explicitly.

```sh
lp -d EPSON_ET_8550_Series -n 1 \
  -o PageSize=Letter.Fullbleed -o MediaType=photographic-glossy \
  -o InputSlot=rear -o media-source=rear -o Duplex=None -o sides=one-sided \
  -o ColorModel=RGB -o cupsPrintQuality=High -o print-quality=5 \
  -o print-scaling=none -o number-up=1 \
  output/pdf/drill-and-cut-guide.pdf
```

The selected media profile must match the paper loaded. The rotator booklet has
its own print layout and is documented beside its source.

The assembly and tool-station cards are preserved at Git tag
`assembly-cards-archive-2026-10-04`. The tagged tree includes their sources and
the CAD artifact pointer that names their generated deck and pictures.
