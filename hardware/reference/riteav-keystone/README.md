# RiteAV RJ11 keystone

`replica.rs` draws the purchased jack's stepped shell, front socket, raised
cantilever latch and open rear IDC comb. Its seating face, mating axis and
receptacle capture clearances come from the existing interface fields in
[replica-parameters.json](replica-parameters.json). The rear body reach remains
a clearance estimate.

The [vendor's product photograph](https://www.riteav.com/products/riteav-rj11-phone-black-punchdown-type-keystone-jack-10-pack)
establishes the major exterior anatomy. The matching image is retained in
[evidence](evidence/vendor-mpn46181.jpg). Its perspective view supports shape
interpretation; it supplies no orthographic manufacturing dimensions. The
parameters separate those photo-scaled estimates from the retained panel
interface. The reference does not qualify a conforming rear cradle, latch
deflection or terminal fit against the received part.

`riteav_keystone.py` supplies the existing receptacle API used by the enclosure.
The reference's origin is the wall's outer plane, with the customer plug along
positive Y and the jack inboard along negative Y. Positive Z is up.
