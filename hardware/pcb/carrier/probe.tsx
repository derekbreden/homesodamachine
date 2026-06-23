/** throwaway: does pcbRotation orient a chip and a header? (left = default, right = rotated 90) */
export default () => (
  <board width="70mm" height="45mm">
    <chip name="U1" footprint="dip8" pcbX={-22} pcbY={8}
      pinLabels={{ pin1: "a", pin2: "b", pin3: "c", pin4: "d", pin5: "e", pin6: "f", pin7: "g", pin8: "h" }} />
    <chip name="U2" footprint="dip8" pcbX={2} pcbY={8} pcbRotation={90}
      pinLabels={{ pin1: "a", pin2: "b", pin3: "c", pin4: "d", pin5: "e", pin6: "f", pin7: "g", pin8: "h" }} />
    <pinheader name="J1" pinCount={6} pitch="2.54mm" footprint="pinrow6" pcbX={-22} pcbY={-12} pinLabels={["1", "2", "3", "4", "5", "6"]} />
    <pinheader name="J2" pinCount={6} pitch="2.54mm" footprint="pinrow6" pcbX={6} pcbY={-12} pcbRotation={90} pinLabels={["1", "2", "3", "4", "5", "6"]} />
  </board>
)
