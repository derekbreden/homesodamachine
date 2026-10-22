# Internal water-pressure regulator

The Hydronix Shok Blok SB-FPV-40 supplies V-A's clean-water feed inside the
enclosure. `fluid-1` connects the water split to its inlet; `fluid-2` connects
its outlet to V-A. The stable assembly key is `flow-regulator`.

The body lies beside the water pump, inclined slightly down toward the rear.
One solid post on the cold-core lid supports its outlet socket. A six-inch
tie passes through the post and over the fixed socket, clear of both moving
collets. The post, regulator and pump travel together with the cold core.
The regulator occupies the rear service bay, clear of the funnel's planned
enlargement toward enclosure −Y.

The manufacturer's [data sheet](https://hydronixwater.com/wp-content/uploads/2018/10/SB_DS.pdf)
specifies 1/4-inch quick-connect ports and nominal 40 psi output. Its table
reports 40 psi at 100 psi inlet, 44 psi at 150 psi inlet and 50 psi at 200 psi
inlet. Maximum temperature is 40 °C. NSF/ANSI 61 certification covers material
requirements. The regulator controls pressure; reservoir level sensing ends
the clean fill.

The [Prime listing](https://www.amazon.com/dp/B01CFOGH6O) was checked on
2026-10-21 at $16.05, shipped and sold by Amazon. Acquisition is not recorded.
The envelope uses the listing's 101.6 mm length and photograph-scaled sections,
including a 34.3 mm body ring. Those sections, the assigned inlet/outlet ends
and the estimated 10 mm tube insertion are provisional. Follow the actual
part's flow marking from the split toward V-A and reconcile the envelope
before treating physical fit as accepted. Internal working parts are omitted.

[`shok_blok_regulator.py`](shok_blok_regulator.py) authors the reference with
flow along +X and the inlet face at the origin. The lid's
[`_water_pressure_regulator.py`](../../printed-parts/cold-core/_water_pressure_regulator.py)
owns its installed pose and single cradle.
