# Faucet display reference — Waveshare ESP32-S3-Touch-LCD-1.47

The faucet's flavor display + touch toggle (BOM §1, ASIN
[B0FCF1MGT3](https://www.amazon.com/dp/B0FCF1MGT3)). A 1.47" 172×320 IPS
capacitive-touch LCD on an ESP32-S3R8 board (JD9853 display driver,
AXS5106L touch chip).

The faucet assembly ([`../faucet-assembly/faucet_assembly.py`](/hardware/reference/touch-flo-faucet/faucet-assembly/faucet_assembly.py))
models this as a **dimensioned stand-in** (`build_display_body` +
`build_display_screen`), not the vendor STEP: the vendor solid is 14 MB
and inflates the multi-solid assembly STEP to ~68 MB.

Structure, front to back: a plastic housing (screen glass flush in its
front face) overhangs the PCB by ~0.275 mm per side. Below the PCB
underside, components protrude — the metal feet are the extreme point
and set the device's bounding depth. The stand-in models that under-PCB
zone as a full-footprint bounding block down to the feet plane; it
shares the PCB's outline, so the PCB underside has no edge in the
solid.

| Feature | Value |
|---|---|
| Plastic housing (W × L × depth) | 24.50 × 44.50 × 5.00 mm |
| PCB (W × L × thickness) | 23.95 × 43.95 × 1.45 mm |
| Housing front face → PCB underside | 6.45 mm |
| Housing front face → metal feet (bounding depth) | 10.35 mm |
| Glass panel (W × L), inset in the housing front | 22.05 × 42.00 mm |
| Active display area (W × L) | 17.75 × 32.93 mm |
| Corner radius (housing) | R5.75 mm |

Housing, PCB, and depths are caliper measurements of the device; the
glass panel, active area, and corner radius come from the vendor 2D
drawing (R5.75 corroborated by a rocked-max caliper diagonal across
opposite housing corners: 46.96 mm measured, 46.97 mm predicted). The
PCB is centered under the housing.

Vendor 2D/3D files (schematic, DXF, STEP):
`https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-2D3D.zip`
Docs: `https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.47`
