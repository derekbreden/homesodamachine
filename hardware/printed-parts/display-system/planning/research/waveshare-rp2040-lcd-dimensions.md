# Waveshare RP2040-LCD-0.99-B Dimensions Reference

Research date: 2026-03-26
Sources: Waveshare wiki, Waveshare product page, Waveshare dimensional drawing, CNX Software review, bare LCD panel manufacturer specs

## Overall Module (CNC Aluminum Case)

| Dimension          | Value     | Notes                                        |
|--------------------|-----------|----------------------------------------------|
| Diameter           | 33.0 mm   | From Waveshare dimensional drawing           |
| Total thickness    | 9.8 mm    | Case top face to acrylic bottom plate        |
| Case body depth    | 8.0 mm    | Metal case portion only (side profile)       |
| Front bezel lip    | 1.75 mm   | Raised rim around display on front face      |
| Rear standoff      | 2.0 mm    | Screw standoff height on back plate          |
| Weight             | 17 g      | From Waveshare product page (0.017 kg)       |

## Display

| Dimension                  | Value                | Notes                                        |
|----------------------------|----------------------|----------------------------------------------|
| Display diagonal           | 0.99 inch (25.1 mm) | Marketing size                               |
| Display visible area       | ~25 mm diameter      | Circular visible area within 33mm case bezel |
| Pixel resolution           | 128 (H) x 115 (V)   | Non-square: flat bottom edge                 |
| Pixel pitch                | 0.19 x 0.19 mm      | From Waveshare wiki                          |
| Active area (calculated)   | 24.32 (H) x 21.85 (V) mm | 128 x 0.19 = 24.32, 115 x 0.19 = 21.85 |
| Display controller         | GC9107               | SPI interface                                |
| Display type               | IPS, 65K color       | Normally black                               |

## Bare LCD Panel (without Waveshare case)

From made-in-china.com panel manufacturer listing:

| Dimension          | Value              | Notes                           |
|--------------------|--------------------|---------------------------------|
| Panel outline      | 26.71 (H) x 26.22 (V) x 1.86 (D) mm | Module dimensions    |

## Connectors

| Connector    | Type       | Position                                      |
|--------------|------------|-----------------------------------------------|
| USB          | USB Type-C | Side of case (visible in side profile drawing as notch in 8.0mm case body) |
| GPIO         | SH1.0 6-pin| Accessible via case (4x GPIO: GP26-GP29, plus GND and 3V3) |
| Boot button  | Tactile    | Accessible externally                         |

## Construction

- **Top shell:** CNC machined aluminum (black anodized)
- **Bottom plate:** Acrylic, dull-polish finish
- **Assembly:** 4 screws visible on rear (in dimensional drawing)
- **Front:** Recessed display with 1.75mm raised bezel rim

## Internal Components

- RP2040 dual-core ARM Cortex-M0+ (up to 133 MHz)
- 264 KB SRAM, 2 MB flash (W25Q16JVUXIQ)
- QMI8658C 6-axis IMU (accelerometer + gyroscope)
- RT9013-33GB LDO regulator

## Mounting Considerations

- No external mounting holes or tabs on the CNC case
- 4 rear screws (hold acrylic back plate) could potentially be replaced with longer standoffs
- Circular form factor -- needs cradle, clip, or friction-fit mount
- USB-C on the side means cable exit must be accommodated in any enclosure pocket

## Dimensional Drawing (from Waveshare)

```
         FRONT VIEW              REAR VIEW              SIDE VIEW

        +----------+           +----------+           +---------+
       /  1.75mm    \         / o      o  \          | 9.8mm   |
      | bezel rim    |       |   2.0mm     |         |  total  |
      |  +------+   |       |  standoffs   |    _____|         |
      |  |display|   |       |              |   |8.0mm| case   |
      |  | area  |   |       |              |   |_____|body    |
      |  +------+   |       |              |         |         |
       \            /         \ o      o  /          +---------+
        +----------+           +----------+              USB-C
         Dia 33.0mm             Dia 33.0mm             notch here
```
