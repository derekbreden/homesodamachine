# Vision

## 1. Values

1. **This is a consumer product, a kitchen appliance.**

2. **User experience is paramount in all things.**

3. **Ease and simplicity of 3D printing and assembly is always the second consideration after UX**


## 2. An architecture the user imagines

- The outer enclosure is 220 mm x 300 mm x 400 mm
- It is printed in two halves, snapped together permanently. The user never opens the enclosure.
- Every single interior piece has specific snap connecting points on those outer two halves, so that the entire thing is assembled by pressing things together
- The 2L bags are mounted one above the other, diagonally, such that the "cap" is at the back and bottom of the enclosure, and the "top" of each bag is pinned flat against the front wall of the device
- The funnel is shaped to be directly on top of the bags
- The bags are each supported by their own lens shaped platform that fits their natural liquid filled shape, and are constrained from above identically, such they have no freedom of movement as they fill and unfill. Without this constraint, the bottom portion may rise to 40mm height, but with the constraint they remain at 25mm - 30mm more consitently throughout their midsection, and please remember, they are diagonal at 35 degrees, with the cap end down and the other end folded flat against the front wall
- The screens and air switch are in the middle of the front face, directly below the bags
- The pump cartridge is below those, at the front and bottom of the device
- The valves are behind the pump cartridge
- The electronics sit at the back and top of the device
- The back of the device has an inlet and outlet for the refrigerated carbonated water (simply to detect flow, but to make installation an obvious process instead of "attach this flow meter" it is "give us an input and we give you an output")
- The back of the device has an inlet for tap water (for the clean cycle)
- The back of the device has the two outlets for each flavoring dispense
- We provide a matte black faucet with black silicone tubing running parallel along it
- Everything is 1/4" hard tubing with John Guest quick connects, both within the device and the connections I just described, with the lone exception of the foot or so of black silicone tubing that runs along the matte black faucet
- The cartridge itself has 4 quick connects inside of it, and the user squeezes towards them a flat surface (against another flat surface) that pulls a release plate that presses the collets of those 4 quick connects towards the user, so that it can be detached from the 4 tube stubs in the enclosure dock
- When I push the air switch, I feel and hear a click that lets me know the flavor is changed
- The RP2040 display is as easily mounted to the wood panel in front of my sink as is the air switch, and the RP2040 always shows me the real logo of the Coke or Pepsi product I have selected, because the iOS app allowed me to upload over BLE any image I wanted for each flavor.
- I can imagine a user who would be as ecstatic about having the full rotary knob S3 mounted externally as I am personally about having the sleek tiny flat RP2040 there
- I can imagine a user who would be ecstatic to have both simply remain where the factory put them, on the front of the device
- Some users may leave the air switch there even
- Some users may put the device on top of their counter
- Many users may put it under the sink
- It will look and feel amazing no matter where they put it


## 3. On the cartridge specifically

- The release plate is inside of the cartridge, and so the quick connects are even further inside of the cartridge
- The user will need to pull the release plate towards them somehow (with their fingers), and so they will need leverage to push against (with their palm), but both surfaces can be perfectly flat and that will still provide the satisfying user experience we seek.
  - The surface the users palm pushes against must eventually be attached to whatever the quick connects are mounted in
	- The surface the users fingers pull must eventually be attached to the release plate
	- The release plate must be able to move towards the quick connect collets
- The cartridge itself will be on guides or rails of some sort to make a consistent and smooth motion removing and putting a new one back in
- For putting it back in, there is no need to worry about the collets at all, regardless of their position the tubes can be pushed into the quick connects and proper mechanisms in the quick connects will ensure the the cartridge will no longer be able to be removed (without of course pushing the collets again)
- The most difficult aspect of the cartridge really, is not this mechanism, but the mounting of the pumps themselves, which have 4 mounting points oriented on the same axis as the metal cylinder body they surround, and so it is very likely a hole sufficient for a 35.73mm (measurements and photos are in the repo) cylinder metal body to fit through will need to itself need to have the 4 mounting points around it in the ~48mm square that those 3.13mm mounting holes sit in. There are many photos from many angles of the pumps in the repo, and there are calipers taking measurements in all of those photos.