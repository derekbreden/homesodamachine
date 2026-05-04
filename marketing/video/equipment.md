# Video Equipment & Settings

Living gear list and capture settings for the marketing video pipeline. Updates in place as gear changes; revisit when buying new equipment, switching cameras, or learning a setting that should default differently.

## Gear

- **Camera.** GoPro HERO13 Black on baseball cap clip mount. Body-stabilized POV is the default angle for shop/build content. Adventure Kit 3.0 head strap (purchased with the camera) is the alternative if the cap mount ever shifts mid-session.
- **Audio.** DJI Mic Mini, 1 TX + 1 RX. USB-C receiver plugs direct into the iPhone. Used for narration audio (live or post-recorded).
- **iPhone.** Capture device for DJI Mic audio AND the editor (iMovie). Quik app handles wireless GoPro → cloud → Photos transfer. iCloud absorbs short-term Photos bloat; once a video ships to YouTube, source clips can be deleted locally.
- **HERO13 storage.** SanDisk Ultra Fit 256 GB USB-3.1 ([B07857Y17V](https://www.amazon.com/dp/B07857Y17V)) for offload (and the same model serves the Bambu H2C front USB for print timelapses).
- **GoPro Quik cloud subscription.** Active. Auto-syncs footage to phone on home-wifi reconnect, removes the manual "open Quik, transfer" step from the evening workflow.

## HERO13 capture settings

| Setting | Pick | Why |
|---|---|---|
| Resolution + Aspect Ratio | **2.7K 8:7** at 30 fps | 8:7 is the full HERO13 sensor — most pixels GoPro can capture. 2.7K gives headroom to crop to 16:9 horizontal *or* 9:16 vertical without quality loss, while keeping file sizes sane. 5.3K 8:7 also works but eats storage 2–3× faster — overkill for talking-head and table-work content. |
| Frame rate | **30 fps** | Baseline. Bump to 60 fps only on clips where slow-mo might matter (welding sparks, fluid splash). |
| Digital Lens | **Linear** | HERO13 lens menu offers HyperView / Wide / Linear / Linear + Horizon Lock / Narrow. Avoid HyperView and Wide — both heavily distort the frame and make hands at the table look like sausages. Linear digitally undistorts so a soldering iron looks like a soldering iron. Skip "Linear + Horizon Lock" — it crops more aggressively and adds rotation correction that misbehaves on head tilt. Plain Linear is right. |
| HyperSmooth | **On** (or AutoBoost) | HERO13 options are Off / On / AutoBoost / Boost. Cap mount is body-stabilized; On is enough. AutoBoost uses available pixels for slightly better stabilization on bumpier moments. Avoid Boost in this mode — it crops ~30% and defeats the 8:7 capture cushion. **Switch to Boost when you take the camera off the cap and handhold for a close-up** (weld-joint inspection, settings screen of the welder, etc.) — handheld shake is meaningfully worse than head-mounted, and the cropped FOV is acceptable for closeups. |
| HDR | **Off** | Wasted bitrate at this content type. |
| Audio | Default (Stereo) | Fine for ambient (tool clicks, welder hum). Real audio comes from the DJI Mic via the iPhone. |
| Orientation | **Auto** | Settings → Preferences → General → Orientation. Auto handles minor head tilt. "Locked Landscape" is for special use cases — not these. |
| Voice Control | **On** | Preferences → Voice Control. "GoPro start recording" / "GoPro stop recording" works hands-free for solder/weld/torch moments. |

**To check or change on the camera:** From the capture screen, tap the bottom strip showing current settings (e.g. "5.3K | 30 | W") to access Resolution, Aspect Ratio, Framerate, and Digital Lens. For Orientation and Voice Control: swipe down from the top → gear icon → Preferences → General.
