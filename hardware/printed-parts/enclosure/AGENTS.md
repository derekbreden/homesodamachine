# Enclosure support work

Before changing an enclosure part, its placed component, or any down-facing enclosure geometry,
read and follow **Support-removal strategy** in
[`enclosure/README.md`](enclosure/README.md#support-removal-strategy). That section is the
canonical policy; keep feature comments about their exact geometry instead of copying the policy
into each helper.

Use the production-profile support audit together with the exact assembly gates. Do not optimize
supported area at the expense of removal count, hide multiple contact islands inside one tree
count, treat a placed component as immovable without checking, or resolve one support defect by
silently creating another. Keep support build-up and model-versus-bed rooting as independent
readings when candidate designs trade one against the other.

The support audit is design and reconciliation evidence, not a build or publication gate. Run it
when support topology is the question, or while the interactive visual loop is quiet. Keep it out
of the normal derive/publish path and never delay a coherent visual iteration for a production
slice. The root build-latency rule applies equally to exact assembly gates.
