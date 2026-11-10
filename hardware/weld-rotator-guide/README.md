# Weld-rotator build guide

48 pages, 8.5 × 11 in, one picture per step: print, heat-set inserts, base, bearing, drive,
nest, copper contact, controller, and six commissioning gates. Served at
[homesodamachine.com/guides](https://homesodamachine.com/guides) and printed one-up on
Letter.

The fixture is [`fixtures/weld-rotator/`](/hardware/printed-parts/fixtures/weld-rotator/README.md),
the rig it belongs to is [`weld-rotation-rig.md`](/hardware/assembly/weld-rotation-rig.md), and
the controller is [`src_weld_rotator/`](/firmware/src_weld_rotator/README.md). Every number here
comes from one of those three; what this document adds is the order and the pictures.

## Manual document build

The numbered HTML leaves, committed pictures and bound book are maintained here.
The native [manual guide builder](../../tools/hsm/manual-guides/src/html.rs) renders
and binds them on demand. The appliance build does not regenerate this guide.
The PDF, cover and document sidecar deploy from their committed directory.

The [archived illustration source](https://github.com/derekbreden/homesodamachine/blob/7877f6193ead05647b529972ee9f50de305c8d44/tools/weld-rotator-guide/rotator_art.py)
records the source shapes and picture poses used by the committed artwork.

## What is here

| | |
|---|---|
| `NN-name.html` | 48 pages, in bound order. The native binder reads their order. |
| `style.css` | The page system. 2550 × 3300 px = 8.5 × 11 in at 300 dpi. |
| `art/*.png` | Committed fixture pictures with the source poses linked above. |
| `weld-rotator-guide.pdf` | The bound book. |
| `weld-rotator-guide.cover.png` | The cover thumbnail the guides page shows. |
| `weld-rotator-guide.pdf.json` | The sidecar `web/lib/walk.js` finds the PDF through. |
| `out/` | Page renders and staged STEPs. Regenerable, gitignored, unbundled. |

## The picture conventions

The picture-conventions page declares them to the reader.

- **Coral** is the part or fastener the step in hand adds. Everything already standing keeps the
  stock's own black.
- **Brass** is a heat-set insert.
- **Blue** is a gauge, a probe, a packing block or the dial indicator.
- **Fasteners stand off their own holes**, along the axis they go in on.

Screws, inserts, feeler blades, blocks and the indicator are catalogue-form proxies.
Dimensions come from the fixture source and assembly procedure.

## The motor screw

The [fixture instructions](../printed-parts/fixtures/weld-rotator/README.md),
[native dimensions](../printed-parts/fixtures/weld-rotator/numbers.rs) and
[assembly procedure](../assembly/weld-rotation-rig.md) govern the motor fastening.
The picture identifies the catalogue nut seat and the screw route through the
carriage arms and motor flange into its open corner channels.

## Rebuilding it

```bash
tools/run hsm-manual-guides bind weld-rotator-guide
```

The native binder renders every page through `tools/render/render-card.js`, which reports any page whose content
overflows the canvas or spills out of its `header` / `main` / `footer` band. The renderer prints
page 1 of each leaf and nothing else.
