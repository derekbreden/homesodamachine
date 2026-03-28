# Vision

## 1. Values

These values are absolute and apply to every decision at every level:

1. **This is a high-end consumer product.** Not a prototype, not a maker project, not a proof of concept. The standard is: what would Apple build if they were making a soda machine, but restricted to this specific 3D printer and components available from Amazon?

2. **User experience is paramount in all things.** Above durability, above simplicity, above prototypability, above cost. One-handed operation, intuitive feel, speed, dark-cabinet usability. If a design choice improves UX at the expense of everything else, it is the right choice.

3. **Cost is not a factor.** Never use cost as a reason to choose or reject any approach. Any filament, any fastener, any component that is available can be purchased. The budget is unlimited for the purpose of all design decisions.

4. **Design a product, not an assembly of parts.** The finished product must look like it was always meant to be this way — as if every surface, every transition, every interaction point was designed together as a single coherent object. Nothing should look added on, bolted to, or improvised. A stranger encountering the product for the first time should see a product, not a collection of components.

5. **Nothing needs to come apart.** The only serviceable component is the pump cartridge, which slides in and out. Everything else is permanent. If the enclosure cannot be disassembled once assembled, that is a feature, not a flaw. I hope you can see how the dishwasher safe funnel insert is not the sort of thing we are referring to here.


## 2. An architecture the user imagines

- The outer enclosure is 220 mm x 300 mm x 400 mm (the depth is necessary for the bags to sit in their natural shape without kinking)
- It is printed in two halves, snapped together permanently
- Every single interior piece has specific snap connecting points on those outer two halves, so that the entire thing is assembled by pressing things together, and once together, so shall they remain
- The 2L bags are mounted one above the other, diagonally, such that the "cap" is at the back and bottom of the enclosure, and the "top" of each bag is pinned flat against the front wall of the device
- The funnel is shaped to be directly on top of the bags
- The bags are each supported by their own lens shaped structure that fits their natural filled shape
- The screens and air switch are in the middle of the front face, directly below the bags
- The pump cartridge is below those, at the front and bottom of the device
- The valves are behind the pump cartridge
- The electronics sit at the back and top of the device
- The back of the device has an inlet and outlet for the refrigerated carbonated water (simply to detect flow, but to make installation an obvious process instead of "attach this flow meter" it is "give us an input and we give you an output")
- The back of the device has an inlet for tap water (for the clean cycle)
- The back of the device has the two outlets for each flavoring dispense
- We provide a matte black faucet with black silicone tubing running parallel along it
- Everything is 1/4" hard tubing with John Guest quick connects, both within the device and the connections I just described, with the lone exception of the foot or so of black silicone tubing that runs along the matte black faucet
- The cartridge itself has 4 quick connects in it, and the screw mechanism that "unlocks" the cartridge pulls the collets of those 4 quick connects towards the user so that it can be detached from the 4 tube stubs in the enclosure dock
- When I push the air switch, I feel and hear a click that lets me know the flavor is changed
- The RP2040 display is as easily mounted to the wood panel in front of my sink as is the air switch, and the RP2040 always shows me the real logo of the Coke or Pepsi product I have selected, because the iOS app allowed me to upload over BLE any image I wanted for each flavor.
- I can imagine a user who would be as ecstatic about having the full rotary knob S3 mounted externally as I am personally about having the sleek tiny flat RP2040 there
- I can imagine a user who would be ecstatic to have both simply remain where the factory put them, on the front of the device
- Some users may leave the air switch there even
- Some users may put the device on top of their counter
- Many users may put it under the sink
- It will look and feel amazing no matter where they put it