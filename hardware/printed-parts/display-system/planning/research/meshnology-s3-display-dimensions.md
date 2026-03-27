# Meshnology ESP32-S3 1.28" Round Rotary Display - Dimensions Reference

Product: Meshnology ESP32 Round Rotary Display 240x240 1.28"
Also sold as: Elecrow CrowPanel 1.28inch-HMI ESP32 Rotary Display
Amazon: B0G5Q4LXVJ
MCU: ESP32-S3-N16R8 (dual-core LX7, 240 MHz, 8MB PSRAM, 16MB Flash)
Display driver: GC9A01A, 240x240 IPS, capacitive touch (CST816D)

## Overall Module Envelope

| Dimension | Value |
|-----------|-------|
| Width     | 48 mm |
| Height    | 48 mm |
| Depth     | 33 mm |
| Weight    | 50 g  |

The 48x48 mm footprint is the outer shell (square with rounded corners).
The 33 mm depth includes the rotary knob protrusion above the display face.

## Shell Construction

- Material: aluminum alloy + plastic + acrylic
- Square outer profile, 48x48 mm face
- Acrylic lens over the round display
- Aluminum alloy body/ring
- Plastic base/bottom

## Display (GC9A01A, 1.28" IPS)

| Parameter              | Value     |
|------------------------|-----------|
| Active area diameter   | 32.4 mm   |
| Active area (alt. src) | 32.51 mm  |
| Pixel pitch            | 0.135 mm  |
| Resolution             | 240 x 240 |
| Panel type             | IPS, 178 deg viewing angle |
| Color depth            | 65K (16-bit RGB565) |
| Touch controller       | CST816D (I2C) |
| Touch I2C pins         | SDA=6, SCL=7 |
| Backlight pin          | GPIO 46   |

Note: The 32.4 mm and 32.51 mm active area values come from different sources
(Waveshare GC9A01 datasheet vs Elecrow bare module spec). The true visible
circle through the acrylic lens may be slightly smaller due to the bezel/mask.
Use 32.4 mm as the conservative design value.

## Inner PCB (bare module, for reference)

The rotary display uses a round PCB internally. The bare (non-rotary) CrowPanel
1.28" round display module has these dimensions:

| Parameter   | Value      |
|-------------|------------|
| PCB size    | 42 x 42 mm |
| PCB depth   | 9.8 mm     |
| Weight      | 15 g       |

The rotary version's internal PCB is likely the same or very similar, housed
inside the 48x48x33 mm aluminum/plastic shell.

## Rotary Encoder / Knob

- Infinite rotation (no endstops), smooth feel
- Supports: clockwise, counterclockwise, press (click)
- Encoder part number: E5A5-23-12-8
- GPIO pins: Encoder A = 45, Encoder B = 42, Switch = 41
- The knob ring surrounds the display and protrudes above the face
- The knob is the primary reason for the 33 mm total depth

## Connectors (Bottom Edge)

The module does NOT have a standard USB-C port on the shell. Instead, it uses
small board-level connectors accessed from the bottom/base:

| Connector     | Type               | Count | Notes |
|---------------|--------------------|-------|-------|
| Power/program | 12-pin FPC, 0.5 mm pitch | 1 | 5V/1A input, also carries USB data |
| UART          | ZH/MX 1.25mm 4-pin | 2    | Serial expansion |
| I2C           | ZH/MX 1.25mm 4-pin | 1    | I2C expansion |

An MX1.25-to-USB-A cable (50 cm) is included for power and programming.
The FPC connector is on the bottom of the unit; connecting cables causes
the module to sit slightly raised on that side.

## Mounting

- M2.5 screw terminals mentioned for mounting
- No detailed mounting hole pattern documented in available sources
- The flat bottom of the 48x48 mm shell is the primary mounting surface
- Eagle PCB files (.sch, .brd) and 3D STEP files available in the Elecrow
  GitHub repo for exact hole positions:
  https://github.com/Elecrow-RD/CrowPanel-1.28inch-HMI-ESP32-Rotary-Display-240-240-IPS-Round-Touch-Knob-Screen

## RGB LED Ring

- 5x WS2812 addressable LEDs (ambient lighting)
- Data pin: GPIO 48
- Max draw: ~60 mA per LED at full white (~300 mA total)
- Visible around the perimeter of the display

## Buttons

- Reset button (on shell)
- Boot button (for firmware flashing)
- Knob press = encoder switch (GPIO 41)

## Power

- Input: 5V / 1A via FPC connector
- Onboard 3.3V regulator
- Operating temperature: -20 C to 65 C

## Key Dimensions Summary (for enclosure design)

```
        48 mm
   +--------------+
   |   /------\   |
   |  | 32.4mm |  |  48 mm
   |  | display|  |
   |   \------/   |
   +--------------+

   Depth: 33 mm (includes knob protrusion above face)
   Knob ring: surrounds display, rotates freely
   Connectors: bottom edge (FPC + 3x MX1.25)
   Mounting: M2.5 screws, exact pattern in STEP/Eagle files
```

## Sources

- Elecrow product page (rotary version): elecrow.com/crowpanel-1-28inch-hmi-esp32-rotary-display
- Elecrow wiki (rotary): elecrow.com/wiki/CrowPanel_1.28inch-HMI_ESP32_Rotary_Display.html
- Elecrow wiki (bare round): elecrow.com/wiki/CrowPanel_ESP32_1.28-inch_Round_Display.html
- Waveshare GC9A01 1.28" LCD module: waveshare.com/1.28inch-lcd-module.htm
- CNX Software review: cnx-software.com (Sep 2025)
- It's FOSS review: itsfoss.com/crowpanel-rotary-display-review
- MakerGuides tutorial: makerguides.com/getting-started-crowpanel-1-28inch-hmi-esp32-rotary-display
- GitHub (Eagle/STEP files): github.com/Elecrow-RD/CrowPanel-1.28inch-HMI-ESP32-Rotary-Display-240-240-IPS-Round-Touch-Knob-Screen
