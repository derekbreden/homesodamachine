import type { ChipProps } from "@tscircuit/props"

// SN74LVC1G08 — single 2-input AND gate, SOT-353 / SC-70-5 (C12512). The firmware-independent
// gas→compressor interlock: it gates the ESP compressor command (A ← IO19) with the MQ-6 hardware
// gas-clear signal (B ← divided DOUT) and drives the relay line (Y → J5.IO19). Y = A·B, so the
// compressor energizes ONLY when firmware asks AND the sensor says clear.
//
// Pinout is the standard single-gate SC-70-5 map (Nexperia 74LVC1G08GW): pin1 = B (input),
// pin2 = A (input), pin3 = GND, pin4 = Y (output), pin5 = VCC. The pin-identical 74LVC1G00 NAND
// (C12508, same GW package) is a drop-in swap for an active-LOW relay module — no layout change.
// Genuine C12512 SC-70-5 land: pin1/2/3 on one long face, pin4/5 on the other; the placement seats it
// rot270 so B/A/GND land south and Y/VCC north. Only the footprint {NAME} silk is stripped — the
// centred() wrapper draws the upright ref-des on the body (SOT-353 has no centre pad).
const pinLabels = {
  pin1: ["B"],
  pin2: ["A"],
  pin3: ["GND"],
  pin4: ["Y"],
  pin5: ["VCC"],
} as const

export const SN74LVC1G08 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{ jlcpcb: ["C12512"] }}
      manufacturerPartNumber="74LVC1G08GW,125"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="0.844296mm" pcbY="-0.649986mm" width="0.8385048mm" height="0.3150108mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="0.844296mm" pcbY="0mm" width="0.8385048mm" height="0.3150108mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="0.844296mm" pcbY="0.649986mm" width="0.8385048mm" height="0.3150108mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-0.844296mm" pcbY="0.649986mm" width="0.8385048mm" height="0.3150108mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="-0.844296mm" pcbY="-0.649986mm" width="0.8385048mm" height="0.3150108mm" shape="rect" />
<silkscreenpath route={[{"x":0.7011923999998544,"y":1.1011916000001065},{"x":-0.7011924000000818,"y":1.1011916000001065}]} />
<silkscreenpath route={[{"x":0.7011923999998544,"y":-1.1011915999999928},{"x":-0.7011924000000818,"y":-1.1011915999999928}]} />
<silkscreenpath route={[{"x":-0.7011924000000818,"y":0.26390600000013364},{"x":-0.7011924000000818,"y":-0.26390600000001996}]} />
<silkscreenpath route={[{"x":1.1468099999999595,"y":-1.2598399999999401},{"x":1.1416949894875188,"y":-1.298692362136535},{"x":1.1266985374636533,"y":-1.3348969999999554},{"x":1.1028426273510377,"y":-1.3659866273510488},{"x":1.071753000000058,"y":-1.3898425374636645},{"x":1.0355483621365238,"y":-1.4048389894874163},{"x":0.996695999999929,"y":-1.4099539999999706},{"x":0.9578436378634478,"y":-1.4048389894874163},{"x":0.9216389999999137,"y":-1.3898425374636645},{"x":0.8905493726488203,"y":-1.3659866273510488},{"x":0.8666934625362046,"y":-1.3348969999999554},{"x":0.8516970105124528,"y":-1.298692362136535},{"x":0.8465820000000122,"y":-1.2598399999999401},{"x":0.8516970105124528,"y":-1.220987637863459},{"x":0.8666934625362046,"y":-1.1847829999999249},{"x":0.8905493726488203,"y":-1.1536933726489451},{"x":0.9216389999999137,"y":-1.1298374625363294},{"x":0.9578436378634478,"y":-1.114841010512464},{"x":0.996695999999929,"y":-1.1097260000000233},{"x":1.0355483621365238,"y":-1.114841010512464},{"x":1.071753000000058,"y":-1.1298374625363294},{"x":1.1028426273510377,"y":-1.1536933726489451},{"x":1.1266985374636533,"y":-1.1847829999999249},{"x":1.1416949894875188,"y":-1.220987637863459},{"x":1.1468099999999595,"y":-1.2598399999999401}]} />
<courtyardoutline outline={[{"x":-1.5199999999999818,"y":1.342200000000048},{"x":1.6977999999999156,"y":1.342200000000048},{"x":1.6977999999999156,"y":-1.672399999999925},{"x":-1.5199999999999818,"y":-1.672399999999925},{"x":-1.5199999999999818,"y":1.342200000000048}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C12512.obj?uuid=cb969c45c1dd4fed98451329f3c3c26e",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C12512.step?uuid=cb969c45c1dd4fed98451329f3c3c26e",
        pcbRotationOffset: 180,
        modelOriginPosition: { x: -0.000012700000070253736, y: 0, z: -0.049083 },
      }}
      {...props}
    />
  )
}
