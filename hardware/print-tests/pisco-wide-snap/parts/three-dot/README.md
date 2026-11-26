# Full three-dot Pisco cover and receiver

The cover and receiver each have three recessed dots. The cover carries the three-dot coupon’s 2.00 mm feet and wing-side lead. Both full-length receiver pockets carry its matching entrance and full retaining lip. The cradle, rigid outlet bearing, collet relief and fore-and-aft stops come from the full one-dot pair Derek operated in C037. [Three-dot coupon dimensions](../../../open-snap-section/parts/easy-entry/geometry.json) · [Full one-dot trial](../../prints/2026-11-26-mark2-easy-entry/physical-result.json) · [New full dimensions and print frames](geometry.json)

The earlier full Pisco used the one-dot coupon. Its spring and catch sections matched that coupon across the part, but each full spring engages 37.32 mm along the regulator. Each short coupon engages 12 mm. The actual round housing starts spreading the full cover about 20 mm before closure. In an empty one-dot pair the receiver starts spreading it about 12 mm before closure. The full cover also has to square up between its fore-and-aft stops. [Previous full-part entry and seating](../easy-entry/fit-check.json) · [Three coupons on the same Mark2 plate](../../prints/2026-11-26-mark2-easy-entry/coupon-section-check.json)

On the Mark2 toolpaths, both relaxed toes clear the incoming rim by 0.66 mm. At the same receiver-roof reference, the full three-dot pair has 1.558 mm of radial hook overlap per side and the short three-dot pair has 1.557 mm. With the real regulator at first saddle contact, the full pair retains 1.369 mm per side. The full one-dot pair had 0.795 mm there. The three-dot lip asks for about 0.97 mm more spring travel on the way in. [Full-size fit measurements](fit-check.json)

Rest the receiver on its flat roof with the channel facing up. Start the regulator about 16 mm toward the open end, lower it into the channel and slide its long inlet back into the rear bore. Point the raised cover lip toward the short outlet. Center the cover, then press over the two wings. Compare how the snap starts and seats with the one-dot full pair. Hold the receiver and push and pull the rigid metal fitting to compare end travel. The white release ring has its own stroke. Lift the cover for tube service.

Generate the two meshes from the repository root. The cover STL stands on its short outlet end. Rotate the receiver 180° around X to place its flat roof on the build plate.

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin pisco-wide-snap -- --three-dot
```
