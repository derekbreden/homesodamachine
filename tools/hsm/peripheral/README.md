# Peripheral host tools

`hsm-peripheral` prepares firmware assets and runs optional native app and device workflows.
Its commands run when requested, outside the print build.

| Command | Purpose |
| --- | --- |
| `ios-checks` | Compile and run the app's existing Swift experience checks |
| `ios-capture` | Build the adaptive study and collect its simulator renders |
| `firmware-pre-build` | Stamp firmware identity, patch TinyProto and prepare display blobs |
| `positioner-geometry` | Bind the controller header to the mechanical motion record |
| `uf2` | Pack a linked RP2040 flash image |
| `pico-pad-checksum` | Pad and checksum the SDK's compiled RP2040 boot stage |
| `positioner-verify` | Verify the released image, source hashes and current motion header |
| `boards` | Enumerate USB boards without opening their ports |
| `display-usb` | Request and verify the enclosure display's USB reattachment |
| `ota` | Transfer receiver-requested image chunks and confirm the running version |
| `firmware-live-check` | Run the enclosure display's requested diagnostic checks |
| `firmware-faucet-check` | Run the faucet display's requested diagnostic checks |
| `panelcam-console` | Send an explicit main-board console command |
| `panelcam-wake` | Wake the displays for a requested camera capture |
| `panelcam-rectify` | Find the panel, resample its pixel grid and read its test patterns |
| `x1-capture` | Record bytes from a physically receive-only serial connection |
| `x1-console` | Send an explicit rear-port console command and save the reply |
| `reed-sweep` | Run a sweep on the reed sweep rig and turn its controller's lines into each reed's closing and opening places |

`--root` selects the checkout. `HSM_PERIPHERAL_BIN` selects the installed executable
for the PlatformIO bridge and camera shell. `HSM_MARKETING_BIN` selects the native
display blob packager used by firmware preparation.

The native [marketing commands](../marketing/README.md) pack source PNG artwork
directly into display blobs. Their [shared conversion](../display-assets/src/lib.rs)
also supplies PNG decoding and resampling to the panel camera tools.

[`firmware/pre_build.py`](../../../firmware/pre_build.py) passes the SCons environment
into the native preparer; it contains no asset or build-policy implementation.
The positioner receipt binds the compiled firmware and native generators to
their exact source hashes and the current mechanical record. A receipt with a
recorded Git revision reads its source blobs from that revision.
