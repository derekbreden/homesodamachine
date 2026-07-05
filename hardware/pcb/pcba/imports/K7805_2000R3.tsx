import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["VIN"],
  pin2: ["GND"],
  pin3: ["+Vo"]
} as const

export const K7805_2000R3 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C18212380"
  ]
}}
      manufacturerPartNumber="K7805_2000R3"
      footprint={<footprint>
        {/* Body redrawn to the real YLPTEC K7805-2000R3: 11.6 mm along the pin row × 7.5 mm across
            (LCSC C18212380 spec, SIP; Mornsun-compatible SIP-3). The stock EasyEDA import over-drew
            the across depth (rear face at y -6.85 silk / -7.21 courtyard = ~9–9.75 mm), so the fence
            reached ~1.5 mm past the real plastic on the rear (interior) side. Pins sit 2.15 mm from the
            front face; the rear is pulled to -5.35 (silk) / -5.74 (courtyard) so the box is 7.5 mm deep. */}
        <platedhole  portHints={["pin3"]} pcbX="2.54mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin2"]} pcbX="0mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin1"]} pcbX="-2.54mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<silkscreenpath route={[{"x":-5.749975800000016,"y":2.14998300000002},{"x":-5.749975800000016,"y":-5.35},{"x":5.7500012000000424,"y":-5.35},{"x":5.7500012000000424,"y":2.14998300000002},{"x":-5.749975800000016,"y":2.14998300000002}]} />
<silkscreenpath route={[{"x":-3.772992199999976,"y":0.04998719999991863},{"x":-3.7773196200613484,"y":0.01711718127205586},{"x":-3.790006973719528,"y":-0.013512800000057723},{"x":-3.810189638789325,"y":-0.039815361210685296},{"x":-3.8364921999999524,"y":-0.059998026280595695},{"x":-3.8671221812719523,"y":-0.07268537993866175},{"x":-3.8999922000000424,"y":-0.07701280000003408},{"x":-3.932862218728019,"y":-0.07268537993866175},{"x":-3.963492200000019,"y":-0.059998026280595695},{"x":-3.98979476121076,"y":-0.039815361210685296},{"x":-4.00997742628067,"y":-0.013512800000057723},{"x":-4.0226647799387365,"y":0.01711718127205586},{"x":-4.026992199999995,"y":0.04998719999991863},{"x":-4.0226647799387365,"y":0.08285721872800877},{"x":-4.00997742628067,"y":0.11348720000012236},{"x":-3.98979476121076,"y":0.13978976121074993},{"x":-3.963492200000019,"y":0.15997242628066033},{"x":-3.932862218728019,"y":0.17265977993884007},{"x":-3.8999922000000424,"y":0.1769872000000987},{"x":-3.8671221812719523,"y":0.17265977993884007},{"x":-3.8364921999999524,"y":0.15997242628066033},{"x":-3.810189638789325,"y":0.13978976121074993},{"x":-3.790006973719528,"y":0.11348720000012236},{"x":-3.7773196200613484,"y":0.08285721872800877},{"x":-3.772992199999976,"y":0.04998719999991863}]} />
<courtyardoutline outline={[{"x":-6.117400000000089,"y":2.5359999999999445},{"x":6.142800000000079,"y":2.5359999999999445},{"x":6.142800000000079,"y":-5.74},{"x":-6.117400000000089,"y":-5.74},{"x":-6.117400000000089,"y":2.5359999999999445}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C18212380.obj?uuid=06df226ccd3445e79e15a1a814b913ad",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C18212380.step?uuid=06df226ccd3445e79e15a1a814b913ad",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 2.195998899999945, z: -8.7500072 },
      }}
      {...props}
    />
  )
}