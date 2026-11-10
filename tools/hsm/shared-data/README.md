# Shared material data

`hsm-shared-data` supplies the machine's authored material, tube-stock and scalar data.

`hsm-finishes` reads the material and tube-stock catalogs and refreshes the viewer's finish
table and shared PET-GF appearance contract on request. It runs outside the normal build.

```sh
hsm-finishes
hsm-finishes --check
hsm-finishes --write
```

The default prints the current table without writing. `--check` compares the saved table and
contract with the catalogs. `--write` refreshes `web/public/finishes.json` and
`web/contracts/material-finishes.js`. `--root` selects the checkout.

The inputs are `catalog/materials.json` and `catalog/routing.json` in this package.
Native installed scenes use the same catalog merge while retaining their own input tracking.
