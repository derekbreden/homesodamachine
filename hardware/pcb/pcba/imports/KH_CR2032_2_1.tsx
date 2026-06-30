import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"]
} as const

// KH-CR2032-2-1 (C5365915) — Kinghelm 2-pin THT CR2032 base. The cell drops into a round
// cradle centered on the two solder posts (20 mm apart, ±10 mm). tsci's EasyEDA import drew
// the battery-body silk ~19 mm east of the posts (a single mis-placed arc primitive — the
// name + courtyard + "+" mark imported centered/correct), so it overlapped U6 and the WROOM.
// Re-authored here with the body outline centered on the posts. pin1 = + (the "+" silk, ->
// DS3231 VBAT), pin2 = - (-> GND).
export const KH_CR2032_2_1 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5365915"
  ]
}}
      manufacturerPartNumber="KH_CR2032_2_1"
      footprint={<footprint>
        <platedhole portHints={["pin2"]} pcbX="-9.99998mm" pcbY="0mm" outerDiameter="1.999996mm" holeDiameter="1.1999976mm" shape="circle" />
<platedhole portHints={["pin1"]} pcbX="9.99998mm" pcbY="0mm" outerDiameter="1.999996mm" holeDiameter="1.1999976mm" shape="circle" />
{/* battery body outline, centered on the posts (re-authored — see header) */}
<silkscreenpath route={[{"x":11.0000,"y":0.0000},{"x":10.9470,"y":1.0782},{"x":10.7886,"y":2.1460},{"x":10.5263,"y":3.1931},{"x":10.1627,"y":4.2095},{"x":9.7011,"y":5.1854},{"x":9.1462,"y":6.1113},{"x":8.5031,"y":6.9783},{"x":7.7782,"y":7.7782},{"x":6.9783,"y":8.5031},{"x":6.1113,"y":9.1462},{"x":5.1854,"y":9.7011},{"x":4.2095,"y":10.1627},{"x":3.1931,"y":10.5263},{"x":2.1460,"y":10.7886},{"x":1.0782,"y":10.9470},{"x":0.0000,"y":11.0000},{"x":-1.0782,"y":10.9470},{"x":-2.1460,"y":10.7886},{"x":-3.1931,"y":10.5263},{"x":-4.2095,"y":10.1627},{"x":-5.1854,"y":9.7011},{"x":-6.1113,"y":9.1462},{"x":-6.9783,"y":8.5031},{"x":-7.7782,"y":7.7782},{"x":-8.5031,"y":6.9783},{"x":-9.1462,"y":6.1113},{"x":-9.7011,"y":5.1854},{"x":-10.1627,"y":4.2095},{"x":-10.5263,"y":3.1931},{"x":-10.7886,"y":2.1460},{"x":-10.9470,"y":1.0782},{"x":-11.0000,"y":0.0000},{"x":-10.9470,"y":-1.0782},{"x":-10.7886,"y":-2.1460},{"x":-10.5263,"y":-3.1931},{"x":-10.1627,"y":-4.2095},{"x":-9.7011,"y":-5.1854},{"x":-9.1462,"y":-6.1113},{"x":-8.5031,"y":-6.9783},{"x":-7.7782,"y":-7.7782},{"x":-6.9783,"y":-8.5031},{"x":-6.1113,"y":-9.1462},{"x":-5.1854,"y":-9.7011},{"x":-4.2095,"y":-10.1627},{"x":-3.1931,"y":-10.5263},{"x":-2.1460,"y":-10.7886},{"x":-1.0782,"y":-10.9470},{"x":-0.0000,"y":-11.0000},{"x":1.0782,"y":-10.9470},{"x":2.1460,"y":-10.7886},{"x":3.1931,"y":-10.5263},{"x":4.2095,"y":-10.1627},{"x":5.1854,"y":-9.7011},{"x":6.1113,"y":-9.1462},{"x":6.9783,"y":-8.5031},{"x":7.7782,"y":-7.7782},{"x":8.5031,"y":-6.9783},{"x":9.1462,"y":-6.1113},{"x":9.7011,"y":-5.1854},{"x":10.1627,"y":-4.2095},{"x":10.5263,"y":-3.1931},{"x":10.7886,"y":-2.1460},{"x":10.9470,"y":-1.0782},{"x":11.0000,"y":-0.0000}]} />
{/* + polarity mark by pin1 */}
<silkscreenpath route={[{"x":6.8709,"y":0},{"x":8.6489,"y":0}]} />
<silkscreenpath route={[{"x":7.7599,"y":0.8889},{"x":7.7599,"y":-0.8891}]} />
<silkscreentext text="{NAME}" pcbX="-1.247902mm" pcbY="12.406378mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-13.9058,"y":11.6564},{"x":11.41,"y":11.6564},{"x":11.41,"y":-11.4242},{"x":-13.9058,"y":-11.4242},{"x":-13.9058,"y":11.6564}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5365915.obj?uuid=97e47c867b624ee8a0b22f9881406067",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5365915.step?uuid=97e47c867b624ee8a0b22f9881406067",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 1.1987103000001111, y: 0.0021124999999999616, z: -0.000006999999999646178 },
      }}
      {...props}
    />
  )
}
