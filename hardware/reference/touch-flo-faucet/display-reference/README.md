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

Per the product photos, the black plastic bezel runs **flush with the PCB
edge** (no PCB rim along the long sides), so the device envelope is a
uniform **24.55 × 44.50 mm**. The drawing's 22.05 mm is the **glass panel**,
inset within that full-width bezel; the active (lit) area is smaller still.
The front **5.4 mm** is the plastic bezel (sits proud of any printed shell);
the back **5.2 mm** is the bare PCB underside a shell wraps. Same width, so
the boundary is a material line — modeled as a perimeter groove at z = 5.2.

| Feature | Value |
|---|---|
| Device envelope (W × L), bezel flush with PCB | 24.55 × 44.50 mm |
| Glass panel (W × L), inset in the bezel | 22.05 × 42.00 mm |
| Active display area (W × L) | 17.75 × 32.93 mm |
| Total depth | 10.6 mm = 5.2 exposed underside + 5.4 plastic bezel |
| Corner radius | R5.75 mm |

The vendor STEP measures 24.55 × 44.73 × **15.60** mm and shows a *narrower*
bezel — but its depth includes pin headers the no-header B0FCF1MGT3 lacks,
and its narrower bezel disagrees with the current product photos, so it's
treated as an older revision. The drawing + photos are authoritative.

Vendor 2D/3D files (schematic, DXF, STEP):
`https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-2D3D.zip`
Docs: `https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.47`
