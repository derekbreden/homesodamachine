import type { ChipProps } from "@tscircuit/props"

// Relabeled from the JLCPCB import (C701341) to the functional ESP32 pin names the
// board wires by. SENSOR_VP/VN -> IO36/IO39, RXD0/TXD0 -> IO3/IO1, the SD-flash pins
// (17-22) -> IO9/10/11/6/7/8 (left unconnected — internal flash), pin32 NC. Every GND
// pad (1, 15, 38) and the 9 centre thermal-pad pads (39-47) share the one "GND" port
// so a single net.GND trace lands them all; each pad still auto-stitches to the bottom
// plane individually (plane-stitching.md). 3V3 is the lone supply pin (no V5 — the bare
// module runs on 3V3 from the step-8 LDO).
const pinLabels = {
  pin1: ["GND"],
  pin2: ["3V3"],
  pin3: ["EN"],
  pin4: ["IO36"],
  pin5: ["IO39"],
  pin6: ["IO34"],
  pin7: ["IO35"],
  pin8: ["IO32"],
  pin9: ["IO33"],
  pin10: ["IO25"],
  pin11: ["IO26"],
  pin12: ["IO27"],
  pin13: ["IO14"],
  pin14: ["IO12"],
  pin15: ["GND"],
  pin16: ["IO13"],
  pin17: ["IO9"],
  pin18: ["IO10"],
  pin19: ["IO11"],
  pin20: ["IO6"],
  pin21: ["IO7"],
  pin22: ["IO8"],
  pin23: ["IO15"],
  pin24: ["IO2"],
  pin25: ["IO0"],
  pin26: ["IO4"],
  pin27: ["IO16"],
  pin28: ["IO17"],
  pin29: ["IO5"],
  pin30: ["IO18"],
  pin31: ["IO19"],
  pin32: ["NC"],
  pin33: ["IO21"],
  pin34: ["IO3"],
  pin35: ["IO1"],
  pin36: ["IO22"],
  pin37: ["IO23"],
  pin38: ["GND"],
  pin39: ["GND"],
  pin40: ["GND"],
  pin41: ["GND"],
  pin42: ["GND"],
  pin43: ["GND"],
  pin44: ["GND"],
  pin45: ["GND"],
  pin46: ["GND"],
  pin47: ["GND"]
} as const

export const ESP32_WROOM_32E_N4 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C701341"
  ]
}}
      manufacturerPartNumber="ESP32_WROOM_32E_N4"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-9.29001825mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-8.02001825mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-6.75001825mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-5.48001825mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="-4.21001825mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="-2.94001825mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="-1.67001825mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="-0.40001825mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="0.86998175mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="2.13998175mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="3.40998175mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin12"]} pcbX="4.67998175mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="5.94998175mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin14"]} pcbX="7.21998175mm" pcbY="-9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin15"]} pcbX="8.71502575mm" pcbY="-5.714873mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin16"]} pcbX="8.71502575mm" pcbY="-4.444873mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin17"]} pcbX="8.71502575mm" pcbY="-3.174873mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin18"]} pcbX="8.71502575mm" pcbY="-1.904873mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin19"]} pcbX="8.71502575mm" pcbY="-0.634873mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin20"]} pcbX="8.71502575mm" pcbY="0.635127mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin21"]} pcbX="8.71502575mm" pcbY="1.905127mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin22"]} pcbX="8.71502575mm" pcbY="3.175127mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin23"]} pcbX="8.71502575mm" pcbY="4.445127mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin24"]} pcbX="8.71502575mm" pcbY="5.715127mm" width="2.0999958mm" height="0.9500108mm" shape="rect" />
<smtpad portHints={["pin25"]} pcbX="7.21998175mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin26"]} pcbX="5.94998175mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin27"]} pcbX="4.67998175mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin28"]} pcbX="3.40998175mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin29"]} pcbX="2.13998175mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin30"]} pcbX="0.86998175mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin31"]} pcbX="-0.40001825mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin32"]} pcbX="-1.67001825mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin33"]} pcbX="-2.94001825mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin34"]} pcbX="-4.21001825mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin35"]} pcbX="-5.48001825mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin36"]} pcbX="-6.75001825mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin37"]} pcbX="-8.02001825mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin38"]} pcbX="-9.29001825mm" pcbY="9.000109mm" width="0.9500108mm" height="2.0999958mm" shape="rect" />
<smtpad portHints={["pin39"]} pcbX="-1.60905825mm" pcbY="-1.500251mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin40"]} pcbX="-1.60905825mm" pcbY="-2.900045mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin41"]} pcbX="-1.60905825mm" pcbY="-0.099949mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin42"]} pcbX="-3.00910625mm" pcbY="-0.099949mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin43"]} pcbX="-3.00910625mm" pcbY="-1.499997mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin44"]} pcbX="-3.00910625mm" pcbY="-2.900045mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin45"]} pcbX="-0.20901025mm" pcbY="-2.900045mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin46"]} pcbX="-0.20901025mm" pcbY="-1.499997mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<smtpad portHints={["pin47"]} pcbX="-0.20901025mm" pcbY="-0.099949mm" width="0.8999982mm" height="0.8999982mm" shape="rect" />
<silkscreenpath route={[{"x":-16.764019050000115,"y":9.000083599999925},{"x":-10.298118850000037,"y":9.000083599999925}]} />
<silkscreenpath route={[{"x":-16.764019050000115,"y":-8.999931199999992},{"x":-10.314044649999914,"y":-8.999931199999992}]} />
<silkscreenpath route={[{"x":-16.764019050000115,"y":9.000083599999925},{"x":-16.764019050000115,"y":-8.999931199999992}]} />
<silkscreenpath route={[{"x":-10.480059050000023,"y":9.000083599999925},{"x":-10.480059050000023,"y":-8.999931199999992}]} />
<silkscreenpath route={[{"x":-9.971195449999868,"y":9.01707620000002},{"x":-10.480059050000023,"y":9.01707620000002}]} />
<silkscreenpath route={[{"x":8.73595535000004,"y":6.396227999999837},{"x":8.73595535000004,"y":9.01707620000002},{"x":7.901158950000081,"y":9.01707620000002}]} />
<silkscreenpath route={[{"x":7.901158950000081,"y":-8.999931199999992},{"x":8.73595535000004,"y":-8.999931199999992},{"x":8.73595535000004,"y":-6.396050199999991}]} />
<silkscreenpath route={[{"x":-10.480059050000023,"y":-8.999931199999992},{"x":-9.971195449999868,"y":-8.999931199999992}]} />
<silkscreentext text="{NAME}" pcbX="-3.53768025mm" pcbY="11.040747mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-17.09728025000004,"y":10.29074700000001},{"x":10.021919750000052,"y":10.29074700000001},{"x":10.021919750000052,"y":-10.427652999999964},{"x":-17.09728025000004,"y":-10.427652999999964},{"x":-17.09728025000004,"y":10.29074700000001}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C701341.obj?uuid=cad43509223249168514859e4520db8a",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C701341.step?uuid=cad43509223249168514859e4520db8a",
        pcbRotationOffset: 180,
        modelOriginPosition: { x: -4.066063750000012, y: 0, z: 0 },
      }}
      {...props}
    />
  )
}