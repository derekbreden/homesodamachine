/**
 * esp32-mcp-mini — the controller core on its real, calipered module footprints:
 * an ESP32-DevKitC-32E socket, two Waveshare MCP23017 boards (0x20, 0x21) on the
 * shared I2C bus, and two ULN2803A driver boards driven by 0x20's GPA/GPB banks.
 * Every footprint is the physical MODULE (2.54 mm header rows + its mounting
 * holes), not a bare chip. Through-hole, two layers.
 *
 * Module footprints from hardware/reference/{mcp23017,uln2803a} (calipered):
 *   MCP23017  23.3 x 38.5; 2x M2 holes at one end; 2x 10-pin GPIO + 6-pin I2C
 *   ULN2803A  23 x 24; 2x dia-3 holes on the centreline; 2x 9-pin channel rows
 *   ESP32     2x19 @ 2.54 mm, rows 25.4 mm (1.0") apart, DevKitC-32E map
 *
 * The modules carry their own I2C pull-ups, decoupling and flyback diodes, so the
 * carrier adds none of those — only sockets, power/ground, the I2C bus, and the
 * 0x20 -> ULN GPIO fan-out.
 */

const i8 = [0, 1, 2, 3, 4, 5, 6, 7]
const at = (px: number, py: number) => ({ pcbX: px, pcbY: py, schX: px / 6, schY: py / 6 })

const espA = ["3V3", "EN", "IO36", "IO39", "IO34", "IO35", "IO32", "IO33", "IO25",
  "IO26", "IO27", "IO14", "IO12", "GND", "IO13", "IO9", "IO10", "IO11", "V5"]
const espB = ["GNDb", "IO23", "IO22", "IO1", "IO3", "IO21", "GNDc", "IO19", "IO18",
  "IO5", "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "IO8", "IO7", "IO6"]

const mcpGPB = ["VCC", "GND", "GPB7", "GPB6", "GPB5", "GPB4", "GPB3", "GPB2", "GPB1", "GPB0"]
const mcpGPA = ["VCC", "GND", "GPA0", "GPA1", "GPA2", "GPA3", "GPA4", "GPA5", "GPA6", "GPA7"]
const mcpI2C = ["VCC", "GND", "SDA", "SCL", "INTA", "INTB"]
const ulnIN = ["IN1", "IN2", "IN3", "IN4", "IN5", "IN6", "IN7", "IN8", "GND"]
const ulnOUT = ["OUT1", "OUT2", "OUT3", "OUT4", "OUT5", "OUT6", "OUT7", "OUT8", "COM"]

// A stroked rectangle on the silk layer — the module's PCB outline.
const Outline = ({ x, y, w, h }: { x: number; y: number; w: number; h: number }) => (
  <silkscreenpath
    strokeWidth="0.2mm"
    route={[
      { x: x - w / 2, y: y - h / 2 },
      { x: x + w / 2, y: y - h / 2 },
      { x: x + w / 2, y: y + h / 2 },
      { x: x - w / 2, y: y + h / 2 },
      { x: x - w / 2, y: y - h / 2 },
    ]}
  />
)

// ---- ESP32-DevKitC-32E socket ----------------------------------------------
const Esp32 = ({ x, y }: { x: number; y: number }) => (
  <>
    <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pinLabels={espA} {...at(x, y + 12.7)} />
    <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pinLabels={espB} {...at(x, y - 12.7)} />
    <Outline x={x} y={y} w={52} h={28} />
    <silkscreentext text="ESP32" fontSize="3mm" pcbX={x} pcbY={y} />
    <trace from=".U1A > .3V3" to="net.V3_3" />
    <trace from=".U1A > .GND" to="net.GND" />
    <trace from=".U1B > .GNDb" to="net.GND" />
    <trace from=".U1B > .IO21" to="net.SDA" />
    <trace from=".U1B > .IO22" to="net.SCL" />
  </>
)

// ---- Waveshare MCP23017 board (23.3 x 38.5) --------------------------------
// Two 10-pin GPIO headers along the long edges (X=+/-10), a 6-pin I2C header at
// the +Y end, 2x M2 holes at that same end. breakout=true fans GPA/GPB to nets.
const Mcp23017 = ({ name, x, y, addr, breakout = false }: { name: string; x: number; y: number; addr: string; breakout?: boolean }) => (
  <>
    <Outline x={x} y={y} w={23.3} h={38.5} />
    <silkscreentext text={`MCP ${addr}`} fontSize="2.6mm" pcbX={x} pcbY={y} />
    <hole shape="circle" diameter="2mm" pcbX={x + 9.4} pcbY={y + 16.75} />
    <hole shape="circle" diameter="2mm" pcbX={x - 9.4} pcbY={y + 16.75} />
    <pinheader name={`${name}B`} pinCount={10} pitch="2.54mm" gender="female" footprint="pinrow10" pcbRotation={90} pinLabels={mcpGPB} {...at(x - 10, y + 1.5)} />
    <pinheader name={`${name}A`} pinCount={10} pitch="2.54mm" gender="female" footprint="pinrow10" pcbRotation={90} pinLabels={mcpGPA} {...at(x + 10, y + 1.5)} />
    <pinheader name={`${name}I`} pinCount={6} pitch="2.54mm" gender="female" footprint="pinrow6" pinLabels={mcpI2C} {...at(x, y + 17.25)} />
    <trace from={`.${name}I > .VCC`} to="net.V3_3" />
    <trace from={`.${name}I > .GND`} to="net.GND" />
    <trace from={`.${name}I > .SDA`} to="net.SDA" />
    <trace from={`.${name}I > .SCL`} to="net.SCL" />
    <trace from={`.${name}A > .VCC`} to="net.V3_3" />
    <trace from={`.${name}A > .GND`} to="net.GND" />
    <trace from={`.${name}B > .VCC`} to="net.V3_3" />
    <trace from={`.${name}B > .GND`} to="net.GND" />
    {breakout && i8.map((k) => <trace key={`a${k}`} from={`.${name}A > .GPA${k}`} to={`net.${name}_GPA${k}`} />)}
  </>
)

// ---- ULN2803A board (23 x 24) ----------------------------------------------
// 9-pin input row (1B-8B + GND) and 9-pin output row (1C-8C + COM) on opposite
// long edges; 2x dia-3 holes on the centreline. Inputs come from srcPrefix0..7;
// outputs + COM leave the board (solenoids / +12V), unconnected on this mini.
const Uln2803 = ({ name, x, y, srcPrefix }: { name: string; x: number; y: number; srcPrefix: string }) => (
  <>
    <Outline x={x} y={y} w={23} h={24} />
    <silkscreentext text={name} fontSize="2.6mm" pcbX={x} pcbY={y} />
    <hole shape="circle" diameter="3mm" pcbX={x} pcbY={y + 8.75} />
    <hole shape="circle" diameter="3mm" pcbX={x} pcbY={y - 8.75} />
    <pinheader name={`${name}I`} pinCount={9} pitch="2.54mm" gender="female" footprint="pinrow9" pcbRotation={90} pinLabels={ulnIN} {...at(x - 10, y)} />
    <pinheader name={`${name}O`} pinCount={9} pitch="2.54mm" gender="female" footprint="pinrow9" pcbRotation={90} pinLabels={ulnOUT} {...at(x + 10, y)} />
    <trace from={`.${name}I > .GND`} to="net.GND" />
    {i8.map((k) => <trace key={`in${k}`} from={`.${name}I > .IN${k + 1}`} to={`net.${srcPrefix}${k}`} />)}
  </>
)

// ---- the board -------------------------------------------------------------
// ESP socket on the left; the two MCPs stacked on the shared I2C bus; each MCP
// fans its right-facing GPA bank straight across to one ULN driver board, so no
// bundle wraps the board. (On the real unit 0x21 reads reeds; here it drives a
// ULN to exercise the same board-to-board footprint.)
export default () => (
  <board width="125mm" height="100mm" minTraceWidth="0.2mm" traceClearance="0.4mm">
    <Esp32 x={-33} y={0} />
    <Mcp23017 name="U2" x={8} y={23} addr="0x20" breakout />
    <Mcp23017 name="U3" x={8} y={-23} addr="0x21" breakout />
    {/* ULN raised 5.31mm so its IN1-8 row lines up with the MCP's GPA0-7 row
        (GPA sits high on its header, IN low on its own) — straight traces across */}
    <Uln2803 name="U4" x={36} y={28.31} srcPrefix="U2_GPA" />
    <Uln2803 name="U5" x={36} y={-17.69} srcPrefix="U3_GPA" />
  </board>
)
