import type { ChipProps } from "@tscircuit/props"

// SMD1812P200TF16 — RUILON resettable PPTC fuse, 1812 (C20812). I_hold 2 A, I_trip 4 A, V_max 16 V,
// R_init 20 mΩ / R_post-trip 100 mΩ (max), 800 mW, I_max 35 A, time-to-trip ≤2 s. The J10 12 V-inlet
// overcurrent device: in series between the screw terminal and Q4's drain, it rides the ~3.3 A board
// peak on thermal inertia, trips on a sustained sub-PSU-limit fault (~4 A the 6.7 A Mean Well ignores),
// and auto-recovers — so a downstream 12 V short can no longer cook Q4 or the island copper. 16 V
// clears the 12 V rail with margin; non-polarized, so pin1/pin2 are interchangeable.
//
// A standard 1812 reflow land: two 1.5 × 3.2 mm pads at ±1.9 mm (2.3 mm gap) capturing the 4.73 mm
// body's end terminals, courtyard a tight IPC keep-out so the vertical (rot 90) seating fits the slot
// west of J10. No cadModel — 3D deferred (best-effort GLB); the orientation audit skips model-less
// parts and the BOM/CPL ride supplierPartNumbers.
const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
} as const

export const SMD1812P200TF16 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{ jlcpcb: ["C20812"] }}
      manufacturerPartNumber="SMD1812P200TF16"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-1.9mm" pcbY="0mm" width="1.5mm" height="3.0mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="1.9mm" pcbY="0mm" width="1.5mm" height="3.0mm" shape="rect" />
        <courtyardoutline outline={[{"x":-2.75,"y":1.65},{"x":2.75,"y":1.65},{"x":2.75,"y":-1.65},{"x":-2.75,"y":-1.65},{"x":-2.75,"y":1.65}]} />
      </footprint>}
      {...props}
    />
  )
}
