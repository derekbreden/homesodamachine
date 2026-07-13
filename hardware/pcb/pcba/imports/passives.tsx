/**
 * passives — JLCPCB-imported land patterns + 3D models for the board's chip passives.
 *
 * Every resistor/capacitor carries JLCPCB's EXACT footprint (pads + origin + model) so the
 * CPL rotation matches JLCPCB's library — the same silent-flip guarantee every other part on
 * the board already has. (For a symmetric 2-pad passive there is in fact no rotation offset —
 * the pads are pin-1-west/horizontal exactly like the generic footprint — so this is belt-and-
 * suspenders: zero exceptions to reason about.) The imported silk is dropped; parts.tsx'
 * Cap/Res helper draws the shared symmetric two-line mark + upright ref-des. The pads + courtyard
 * are kept (the courtyard feeds footprint-audit's body model). Three JLCPCB lands cover every
 * value: res 0603 (±0.753), cap 0805 (±1.000), cap 0603 (±0.700).
 */

// deduped land patterns (a fresh <footprint> per call — never share one JSX node across parts)
const RES_0603 = () => (
  <footprint>
    <smtpad portHints={["pin1"]} pcbX="-0.753364mm" pcbY="0mm" width="0.8064754mm" height="0.8640064mm" shape="rect" />
    <smtpad portHints={["pin2"]} pcbX="0.753364mm" pcbY="0mm" width="0.8064754mm" height="0.8640064mm" shape="rect" />
    <courtyardoutline outline={[{"x":-1.647000000000162,"y":0.9103999999999814},{"x":1.6216000000000577,"y":0.9103999999999814},{"x":1.6216000000000577,"y":-0.9103999999998678},{"x":-1.647000000000162,"y":-0.9103999999998678},{"x":-1.647000000000162,"y":0.9103999999999814}]} />
  </footprint>
)
const CAP_0805 = () => (
  <footprint>
    <smtpad portHints={["pin1"]} pcbX="-0.999998mm" pcbY="0mm" width="1.4100048mm" height="1.35001mm" shape="rect" />
    <smtpad portHints={["pin2"]} pcbX="0.999998mm" pcbY="0mm" width="1.4100048mm" height="1.35001mm" shape="rect" />
    <courtyardoutline outline={[{"x":-2.205799999999954,"y":1.1644000000000005},{"x":2.2311999999999443,"y":1.1644000000000005},{"x":2.2311999999999443,"y":-1.13900000000001},{"x":-2.205799999999954,"y":-1.13900000000001},{"x":-2.205799999999954,"y":1.1644000000000005}]} />
  </footprint>
)
const CAP_0603 = () => (
  <footprint>
    <smtpad portHints={["pin1"]} pcbX="-0.700024mm" pcbY="0mm" width="0.7999984mm" height="0.8999982mm" shape="rect" />
    <smtpad portHints={["pin2"]} pcbX="0.700024mm" pcbY="0mm" width="0.7999984mm" height="0.8999982mm" shape="rect" />
    <courtyardoutline outline={[{"x":-1.647000000000162,"y":0.9612000000000762},{"x":1.6216000000000577,"y":0.9612000000000762},{"x":1.6216000000000577,"y":-0.9611999999999625},{"x":-1.647000000000162,"y":-0.9611999999999625},{"x":-1.647000000000162,"y":0.9612000000000762}]} />
  </footprint>
)
// 0402 resistor land (UNI-ROYAL 0402WGF series, same family as the 0603s) — the tight SENSORS
// pocket only fits two 0402s where a 0603 would crowd R9/U10/J4. PASSIVE_SIZE already carries "0402".
const RES_0402 = () => (
  <footprint>
    <smtpad portHints={["pin1"]} pcbX="-0.432816mm" pcbY="0mm" width="0.565658mm" height="0.540004mm" shape="rect" />
    <smtpad portHints={["pin2"]} pcbX="0.432816mm" pcbY="0mm" width="0.565658mm" height="0.540004mm" shape="rect" />
    <courtyardoutline outline={[{"x":-1.1897999999998774,"y":0.7580000000000382},{"x":1.189799999999991,"y":0.7580000000000382},{"x":1.189799999999991,"y":-0.7326000000000477},{"x":-1.1897999999998774,"y":-0.7326000000000477},{"x":-1.1897999999998774,"y":0.7580000000000382}]} />
  </footprint>
)

// per-part 3D model (its own JLCPCB/EasyEDA asset)
const CAD: Record<string, any> = {
  C25804: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C25804.obj?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C25804.step?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    pcbRotationOffset: 90,
    modelOriginPosition: { x: -0.004999999999999977, y: 0, z: -0.01 },
  },
  C22787: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C22787.obj?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C22787.step?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    pcbRotationOffset: 90,
    modelOriginPosition: { x: -0.004999999999999977, y: 0, z: -0.01 },
  },
  C23162: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C23162.obj?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C23162.step?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    pcbRotationOffset: 90,
    modelOriginPosition: { x: -0.004999999999999977, y: 0, z: -0.01 },
  },
  C23179: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C23179.obj?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C23179.step?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    pcbRotationOffset: 90,
    modelOriginPosition: { x: -0.004999999999999977, y: 0, z: -0.01 },
  },
  C23186: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C23186.obj?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C23186.step?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    pcbRotationOffset: 90,
    modelOriginPosition: { x: -0.004999999999999977, y: 0, z: -0.01 },
  },
  C21190: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C21190.obj?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C21190.step?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    pcbRotationOffset: 90,
    modelOriginPosition: { x: -0.004999999999999977, y: 0, z: -0.01 },
  },
  C4190: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C4190.obj?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C4190.step?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    pcbRotationOffset: 90,
    modelOriginPosition: { x: -0.004999999999999977, y: 0, z: -0.01 },
  },
  C22978: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C22978.obj?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C22978.step?uuid=6bd5cd867e9542ebae21caaf5d2d4c4d",
    pcbRotationOffset: 90,
    modelOriginPosition: { x: -0.004999999999999977, y: 0, z: -0.01 },
  },
  C49678: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C49678.obj?uuid=b87ab0c5465a48b3a1c9a6dac8d30bc5",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C49678.step?uuid=b87ab0c5465a48b3a1c9a6dac8d30bc5",
    pcbRotationOffset: 0,
    modelOriginPosition: { x: 0, y: -0.000012700000070253736, z: -0.65 },
  },
  C15850: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C15850.obj?uuid=b87ab0c5465a48b3a1c9a6dac8d30bc5",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C15850.step?uuid=b87ab0c5465a48b3a1c9a6dac8d30bc5",
    pcbRotationOffset: 0,
    modelOriginPosition: { x: 0, y: -0.000012700000070253736, z: -0.65 },
  },
  C45783: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C45783.obj?uuid=b87ab0c5465a48b3a1c9a6dac8d30bc5",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C45783.step?uuid=b87ab0c5465a48b3a1c9a6dac8d30bc5",
    pcbRotationOffset: 0,
    modelOriginPosition: { x: 0, y: -0.000012700000070253736, z: -0.65 },
  },
  C15849: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C15849.obj?uuid=ac9b32e974bc448eab36b1293f859dcb",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C15849.step?uuid=ac9b32e974bc448eab36b1293f859dcb",
    pcbRotationOffset: 0,
    modelOriginPosition: { x: 0, y: 0, z: -0.4 },
  },
  C25900: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C25900.obj?uuid=026a4a15ab5c4a92ac0e421d6d013717",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C25900.step?uuid=026a4a15ab5c4a92ac0e421d6d013717",
    pcbRotationOffset: 0,
    modelOriginPosition: { x: 0, y: -0.000012700000070253736, z: 0 },
  },
  C11702: {
    objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C11702.obj?uuid=026a4a15ab5c4a92ac0e421d6d013717",
    stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C11702.step?uuid=026a4a15ab5c4a92ac0e421d6d013717",
    pcbRotationOffset: 0,
    modelOriginPosition: { x: 0, y: -0.000012700000070253736, z: 0 },
  },
}

const LAND: Record<string, () => any> = {
  C25804: RES_0603,
  C22787: RES_0603,
  C23162: RES_0603,
  C23179: RES_0603,
  C23186: RES_0603,
  C21190: RES_0603,
  C4190: RES_0603,
  C22978: RES_0603,
  C49678: CAP_0805,
  C15850: CAP_0805,
  C45783: CAP_0805,
  C15849: CAP_0603,
  C25900: RES_0402,
  C11702: RES_0402,
}

export const passiveImport = (jlcpcb: string): { footprint: () => any; cadModel: any } => ({
  footprint: LAND[jlcpcb] ?? RES_0603,
  cadModel: CAD[jlcpcb],
})
