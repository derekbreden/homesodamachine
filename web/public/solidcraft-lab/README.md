# Native Beduan lab

[Open the experiment](https://homesodamachine.com/labs/solidcraft/beduan).

The page provides an isolated native SolidCraft session for editing and viewing the Beduan valve. Its parameter controls apply a combined native parameter edit to the existing session. SolidCraft evaluates the affected history and draws its own display geometry directly. The embedded editor exposes the source's sketches, features and appearances.

`beduan.js` retains the design in this browser's local storage, tracks edits made through the native editor and unloads the embedded runtime when paused or backgrounded, after pending work and the local save finish. Resume evaluates the retained native design. Restore reference opens the source from the website's deployed checkout. Download native design saves the edited JSON without changing the repository or the published manufacturing artifacts.

The host's update observations include the native command and the following browser frames. They describe this device's interaction; they do not qualify a physical printed fit. Startup, opening a design and changing a dimension are separate observations.

`solidcraft-lab.js` serves the experiment's page, the canonical [valve source](../../../hardware/reference/beduan-solenoid/solidcraft/beduan-valve.json) and the pinned runtime. Its routes load assets on request and stream runtime files from the release recorded in [runtime.json](runtime.json). The browser caches those immutable files. The page installs no service worker and starts no background build, watcher or website CAD process. Its scripts are loaded only by this page.

`editor.js` loads the released upstream browser engine inside the same-origin iframe, with SolidCraft's native editor embed and browser command API. The host supplies and retains the design through that API. The iframe's base URL keeps runtime font and channel requests within the experiment.

The runtime manifest owns the upstream version, archive provenance, asset names, hashes and transport types. The GitHub release holds the upstream JavaScript, WebAssembly, fonts and license notices; WebAssembly uses gzip transport encoding. Runtime binaries stay outside the repository and website installation steps. Updates use the current upstream release matching the installed application and CLI, with new asset identities and the corresponding manifest.
