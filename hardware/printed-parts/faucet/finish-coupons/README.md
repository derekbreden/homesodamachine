# Faucet support trials

## Inclined contacts

Support D released from the tested flat rail ceilings. The inclined faucet base has
a different contact surface and cleanup access. Prepare the incline comparisons before
treating D as an accepted recipe for a curved contact. The [comparison matrix](https://github.com/derekbreden/homesodamachine/blob/ed4ebc3cf65805689fe1421af6710770936107ec/hardware/print-tests/petgf-dense-roofs/inclines/matrix.json)
holds the dense interface constant while varying the gap and the tree algorithm.
Read both the density and the footprint the tree actually lays.

| Trial | What the print showed |
| --- | --- |
| [Inclined base](https://github.com/derekbreden/homesodamachine/blob/7b4d4c7d87dda9db021665b2e7c7e255d996a39d/hardware/print-tests/petgf-dense-roofs/D-representative-mark2/physical-result.json) | The tree stems broke and left contact material on the base. |
| [Explicit Tree Slim](https://github.com/derekbreden/homesodamachine/blob/be19fb8a4693edecead5753aa2bcb42c54dcdbf0/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-mark1/physical-result/physical-result.json) | Interface paths followed the curve, but the support still failed to release. |
| [Larger contact gap](https://github.com/derekbreden/homesodamachine/blob/a261387d7021b9f74675793f5b1a3fd188cfccec/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-slim-gap048-mark1/physical-result/physical-result.json) | The connected roof mats came off more easily. The underside finish was essentially unchanged. |
| [Nonplanar coupon](https://github.com/derekbreden/homesodamachine/blob/542ced3900b6b513c521c525582c22f167c9584d/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-gap024-widebands-mark1/physical-result/physical-result.json) | The underside improved. Support remained trapped in the insert pockets. |
| [Rim fins](https://github.com/derekbreden/homesodamachine/blob/534b87cc5f8d6911f8bcfa38378116d8dcdcb6bd/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-10-faucet-nonplanar-rim-fins-mark1/physical-result/physical-result.json) | The dense roof and the support came off together. |

Keep the heat-insert recesses clear of support. Bridge the shoulders and blind pilot
roofs and read the emitted paths through both stages. The [tree and contoured-rim trial](https://github.com/derekbreden/homesodamachine/blob/ed4ebc3cf65805689fe1421af6710770936107ec/hardware/print-tests/petgf-dense-roofs/inclines/prints/2026-11-11-faucet-trees-only-mark1/print-job.json)
specifies the dense roof and bridged pockets on the complete lower curve. The
[product plate recipe](../README.md#prepare-a-product-plate) owns the settings used for production.

## Curved edge fins

The [accepted base result](https://github.com/derekbreden/homesodamachine/blob/9a785be8163fcb13a7efd24e78b249419bc0806e/hardware/printed-parts/faucet/finish-coupons/2026-10-15-edge-supports/base-mark2/physical-result/physical-result.json)
records Derek's best observed PET-GF underside and easy snap-off at the base's
recorded print angle. Interrupted arcs carry the visible rim, with a continuous arc
across its front midpoint and trees under the remaining underside. Adjust the
contact strips, release gaps and anchors for the edge being printed.
