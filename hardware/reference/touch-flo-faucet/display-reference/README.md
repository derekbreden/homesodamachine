# Faucet display reference — Waveshare ESP32-S3-Touch-LCD-1.47

The faucet's flavor display + touch toggle (BOM §1, ASIN
[B0FCF1MGT3](https://www.amazon.com/dp/B0FCF1MGT3)). A 1.47" 172×320 IPS
capacitive-touch LCD on an ESP32-S3R8 board (JD9853 display driver,
AXS5106L touch chip).

The faucet assembly ([`../faucet-assembly/faucet_assembly.py`](/hardware/reference/touch-flo-faucet/faucet-assembly/faucet_assembly.py))
models this as a **dimensioned stand-in** (`build_display_body` +
`build_display_screen`), not the vendor STEP: the vendor solid is 14 MB
and inflates the multi-solid assembly STEP to ~68 MB. The stand-in's
sizes come from the vendor 2D/3D drawing:

The board nests (all centered): PCB outline ⊃ plastic bezel ⊃ active area.
The bezel is narrower than the PCB and sits **proud** of it, so the
bare/plastic boundary is the step where the PCB ledge meets the bezel base
— the edge a printed retaining shell wraps up to.

| Feature | Value |
|---|---|
| PCB outline / exposed underside (W × L) | 24.55 × 44.50 mm |
| Plastic bezel — proud, narrower (W × L) | 22.05 × 42.00 mm |
| Active display area (W × L) | 17.75 × 32.93 mm |
| Total depth | 10.6 mm = 5.2 exposed underside + 5.4 plastic bezel |
| PCB corner radius | R5.75 mm |

The vendor STEP measures 24.55 × 44.73 × **15.60** mm — its depth includes
pin headers the no-header B0FCF1MGT3 variant lacks, so the drawing's
10.6 mm device depth is authoritative.

Vendor 2D/3D files (schematic, DXF, STEP):
`https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-2D3D.zip`
Docs: `https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.47`
