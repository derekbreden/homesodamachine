# Enclosure support work

Before changing an enclosure part, its placed component, or any down-facing enclosure
geometry, read **Support-removal strategy** in
[`enclosure/README.md`](enclosure/README.md#support-removal-strategy). Feature comments
describe their exact geometry; the README carries the policy.

The visible 0.08 mm top/bottom rounds print unsupported, including back-top's roof edges.
Retain supports for separate functional faces such as flat lifting ceilings and mounting
seats. Check the actual slice for contacts on the rounded show faces before sending it.
