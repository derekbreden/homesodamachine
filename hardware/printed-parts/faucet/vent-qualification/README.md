# Faucet overflow drip indicator

The white drain is neoFlo LLDPE4M-WHITE: 4 mm OD and 2.5 mm ID, as specified
in the [manufacturer's metric tubing table](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf).
Its square-cut end stops in the shared tip's unsealed pocket. Two plain
2 mm printed routing walls guide the continuous drink tubes and insulated
conductors. A round Ø4 mm underside hole crosses the pocket's upstream low
corner and opens over the bowl. No drain bung, gasket or insertion tool is
part of this arrangement.

The product requirement is a visible drip during a major fault. Derek accepts
incidental escape into the housing during that event and calls for complete
replacement after it. The faucet drain is not a sealed tube connection.

The [native geometry reading](simple-drip-check.json) binds the current STEP,
STL, viewer payload and source. It checks the hole's open connection to the
pocket, the tube end's location, clearance from the actual nominal tubing,
and unchanged material outside the drain region. The shared joint, display
retention and beverage face retain their geometry. The 4 mm hole has 2.56
times the tube-bore area; hole area alone does not determine discharge flow.
Physical drip direction and complete fault-vent performance are unmeasured.

The [Industrial complete print selection](../industrial/selected-print.json)
is held at Derek's request, with 0.12 mm base shoulder bands, corrected screw
reinforcement and 0.50 mm longer display-cover wings. Its matching native slice
and five-part toolpath readings are retained in the selected job; starting
requires Derek's separate go-ahead.

The retained [hydraulic report](hydraulic-report.json),
[sealed-port witness](port-native-check.json) and
[sealed-cavity print evidence](native-print-review-evidence.json) are bound
to the two-bung sealed cavity and large flared outlet identified in their
source/artifact hashes. Their containment, capacity and cleanup claims do
not apply to the unsealed drip indicator.
