import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["GND"],
  pin2: ["TXD"],
  pin3: ["RXD"],
  pin4: ["V3"],
  pin5: ["D_POS"],
  pin6: ["D_NEG"],
  pin7: ["pin7"],
  pin8: ["OUT"],
  pin9: ["CTS"],
  pin10: ["DSR"],
  pin11: ["RI"],
  pin12: ["DCD"],
  pin13: ["DTR"],
  pin14: ["RTS"],
  pin15: ["R232"],
  pin16: ["VCC"]
} as const

// Supplier code points at C7464026, not the original C84681: both are the same
// CH340C (SOP-16, identical die/pinout), but C84681 read "Unavailable" at JLCPCB
// (2026-07-13, no assembly stock) while C7464026 sat at ~23,441 — a pure sourcing-
// code swap. The land + 3D model below are retained from the identical-MPN C84681
// (they solder C7464026 identically), so this disturbs zero copper. See jlcpcb-parts.md.
export const CH340C = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C7464026"
  ]
}}
      manufacturerPartNumber="CH340C"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-4.445mm" pcbY="-2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin2"]} pcbX="-3.175mm" pcbY="-2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin3"]} pcbX="-1.905mm" pcbY="-2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin4"]} pcbX="-0.635mm" pcbY="-2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin5"]} pcbX="0.635mm" pcbY="-2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin6"]} pcbX="1.905mm" pcbY="-2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin7"]} pcbX="3.175mm" pcbY="-2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin8"]} pcbX="4.445mm" pcbY="-2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin16"]} pcbX="-4.445mm" pcbY="2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin15"]} pcbX="-3.175mm" pcbY="2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin14"]} pcbX="-1.905mm" pcbY="2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin13"]} pcbX="-0.635mm" pcbY="2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin12"]} pcbX="0.635mm" pcbY="2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin11"]} pcbX="1.905mm" pcbY="2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin10"]} pcbX="3.175mm" pcbY="2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<smtpad portHints={["pin9"]} pcbX="4.445mm" pcbY="2.872486mm" width="0.5599938mm" height="1.7450054mm" radius="0.2799969mm" shape="pill" />
<silkscreenpath route={[{"x":-5.076190000000111,"y":-1.7713960000000952},{"x":-5.076190000000111,"y":1.7713959999999815},{"x":5.076189999999997,"y":1.7713959999999815},{"x":5.076189999999997,"y":-1.7713960000000952},{"x":-5.076190000000111,"y":-1.7713960000000952}]} />
<silkscreenpath route={[{"x":-4.2948860000000195,"y":-1.019047999999998},{"x":-4.300001010512574,"y":-1.057900362136479},{"x":-4.314997462536439,"y":-1.094105000000127},{"x":-4.338853372649055,"y":-1.1251946273511066},{"x":-4.369943000000035,"y":-1.1490505374637223},{"x":-4.406147637863455,"y":-1.1640469894875878},{"x":-4.445000000000164,"y":-1.1691619999999148},{"x":-4.483852362136531,"y":-1.1640469894875878},{"x":-4.520057000000065,"y":-1.1490505374637223},{"x":-4.551146627351045,"y":-1.1251946273511066},{"x":-4.575002537463661,"y":-1.094105000000127},{"x":-4.589998989487526,"y":-1.057900362136479},{"x":-4.595113999999967,"y":-1.019047999999998},{"x":-4.589998989487526,"y":-0.9801956378634031},{"x":-4.575002537463661,"y":-0.943990999999869},{"x":-4.551146627351045,"y":-0.912901372649003},{"x":-4.520057000000065,"y":-0.8890454625363873},{"x":-4.483852362136531,"y":-0.8740490105124081},{"x":-4.445000000000164,"y":-0.8689340000000811},{"x":-4.406147637863455,"y":-0.8740490105124081},{"x":-4.369943000000035,"y":-0.8890454625363873},{"x":-4.338853372649055,"y":-0.912901372649003},{"x":-4.314997462536439,"y":-0.943990999999869},{"x":-4.300001010512574,"y":-0.9801956378634031},{"x":-4.2948860000000195,"y":-1.019047999999998}]} />
<silkscreenpath route={[{"x":-5.027168000000074,"y":-2.8724859999999808},{"x":-5.032283010512401,"y":-2.9113383621365756},{"x":-5.047279462536267,"y":-2.9475430000001097},{"x":-5.071135372648882,"y":-2.9786326273510895},{"x":-5.102224999999862,"y":-3.002488537463705},{"x":-5.138429637863396,"y":-3.0174849894875706},{"x":-5.177281999999991,"y":-3.0225999999998976},{"x":-5.216134362136586,"y":-3.0174849894875706},{"x":-5.25233900000012,"y":-3.002488537463705},{"x":-5.2834286273511,"y":-2.9786326273510895},{"x":-5.307284537463715,"y":-2.9475430000001097},{"x":-5.322280989487581,"y":-2.9113383621365756},{"x":-5.327395999999908,"y":-2.8724859999999808},{"x":-5.322280989487581,"y":-2.8336336378634996},{"x":-5.307284537463715,"y":-2.7974289999999655},{"x":-5.2834286273511,"y":-2.766339372648872},{"x":-5.25233900000012,"y":-2.7424834625362564},{"x":-5.216134362136586,"y":-2.7274870105125046},{"x":-5.177281999999991,"y":-2.722372000000064},{"x":-5.138429637863396,"y":-2.7274870105125046},{"x":-5.102224999999862,"y":-2.7424834625362564},{"x":-5.071135372648882,"y":-2.766339372648872},{"x":-5.047279462536267,"y":-2.7974289999999655},{"x":-5.032283010512401,"y":-2.8336336378634996},{"x":-5.027168000000074,"y":-2.8724859999999808}]} />
<courtyardoutline outline={[{"x":-5.58400000000006,"y":3.704400000000078},{"x":5.329999999999927,"y":3.704400000000078},{"x":5.329999999999927,"y":-3.9583999999998696},{"x":-5.58400000000006,"y":-3.9583999999998696},{"x":-5.58400000000006,"y":3.704400000000078}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C84681.obj?uuid=07126628bc464d5389bb996c52812f54",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C84681.step?uuid=07126628bc464d5389bb996c52812f54",
        pcbRotationOffset: 90,
        modelOriginPosition: { x: -0.000012700000070253736, y: 0, z: 0.000575 },
      }}
      {...props}
    />
  )
}