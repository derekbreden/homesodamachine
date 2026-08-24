# Faucet shell — material

Polymaker Fiberon PET-GF15, black, on the Bambu 0.4 mm tungsten carbide hotend — the one
spool and the one nozzle every surface a customer sees comes off ([bom.md
§7](/hardware/ledger/bom.md), [tools.md](/hardware/ledger/tools.md)). The shell's two
pieces and the [above-counter plate](/hardware/printed-parts/faucet/above-counter-plate/)
stand in the counter in the same black the box on the floor is closed in.

15 wt% glass fibre in PET. 1.43 g/cm³, $25.02/kg. Polymaker's published figures on printed
specimens: 59.9 MPa tensile in X-Y and **48.2 MPa in Z**, 8.7 kJ/m² notched Charpy, 4144 MPa
Young's modulus, 3705 MPa bending modulus in X-Y and 2998 in Z, HDT 133.7 °C at 0.45 MPa
after annealing. Nothing here is annealed.

**Z is the direction this part is loaded and the direction it is built in.** Neither piece
prints upright. Each beds on the face at the far end of its own half of the gooseneck and
tilts [35°](PRINT_TILT), which lands its build direction on that half's angular midpoint —
and that is what holds every visible surface to [35°](MAX_PRINT_OVERHANG) of overhang, off
supports. The base stands [236.9 mm](BASE_PRINT_HEIGHT) tall built that way and the tip
[99.3 mm](TIP_PRINT_HEIGHT); the layer planes lie [35°](PRINT_TILT) off the shank axis
rather than square to it, so the lever the customer pulls reacts across them at that angle.

Drying: 100 °C × 10 h in the SUNLU E2, only if the spool has taken on moisture. The 3 kg
spools feed the print from a PolyDryer Box XL — a 3 kg spool turns too stiffly in the E2's
chamber ([tools.md](/hardware/ledger/tools.md) "What dries where").

The wetted path is not this print: soda runs in its own tube through the gooseneck onto the
TPU thimble, and the two flavour tubes run their own length to the tip
([ASSEMBLY.md](ASSEMBLY.md)).

Calibration history at [`print-log.md`](/hardware/printed-parts/faucet/faucet-shell/print-log.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/faucet-shell/faucet_shell.py`
