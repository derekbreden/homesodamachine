# Frizzlife PRV01 water pressure regulator

Ordered native **1/4-inch OD push-connect** water regulator, Amazon ASIN
`B08NDQCZN2`. The manufacturer describes a nominal 60 psi regulator with a
50–60 psi regulated range, maximum 300 psi inlet and maximum 40°C water.

The official dimensional photograph controls the **66.802 mm overall length**,
38.354 mm main housing length, 24.892 mm upper-body diameter, 26.67 mm lower-cuff
diameter and 20.066 mm outlet-collar width. The canonical frame has flow along
**+X**, from the wide-cuff inlet at X0 to the narrower-neck outlet at X66.802.
Both ports take 6.35 mm OD tube directly.

The outside-envelope model estimates undimensioned shoulder stations,
collet/clip detail and collar facets from the manufacturer photographs.
The nominal tube-mouth span uses the published overall length. The 15.7 mm
insertion depth is a layout estimate based on familiar 1/4-inch push-connects.
These estimates are recorded separately from published dimensions in
`dimensions.json`. Plain insertion sockets are modeled; the regulating
mechanism is not.

[`frizzlife-prv01.step`](https://github.com/derekbreden/homesodamachine/blob/b57b985c648c34346481a57fde897374b0e8f068/hardware/reference/frizzlife-prv01/geometry/frizzlife-prv01.step)
is a colored native assembly with named inlet and outlet tube-mouth faces. It
and the individual valid solids are at the `archive-finished-trials` tag.
Their frozen NPZ meshes are in `geometry/`; `dimensions.json` retains the
model inputs and interface datums.

Sources: [manufacturer product page](https://www.frizzlife.com/collections/pressure-regulators/products/frizzlife-water-filter-pressure-regulator-protection-valve-for-reverse-osmosis-water-filter-system-60psi-1-4-quick-connect-push-fit-prv01),
[manufacturer dimensional photograph](https://cdn.shopify.com/s/files/1/0159/8429/5990/files/PRV013_77f49cde-2932-4349-856b-636ef15aa6ae_1.jpg?v=1758007365),
and [purchased product identity](https://www.amazon.com/dp/B08NDQCZN2).

The source derivations are preserved at their recorded revision: [build.py](https://github.com/derekbreden/homesodamachine/blob/a518a57a878f02d9ac5b8b638c1c5883cadf6669/hardware/reference/frizzlife-prv01/build.py), [model.py](https://github.com/derekbreden/homesodamachine/blob/a518a57a878f02d9ac5b8b638c1c5883cadf6669/hardware/reference/frizzlife-prv01/model.py).
