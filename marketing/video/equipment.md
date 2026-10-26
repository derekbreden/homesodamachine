# Video Equipment & Settings

Living gear list and capture settings for the marketing video pipeline. Updates in place as gear changes; revisit when buying new equipment, switching cameras, or learning a setting that should default differently.

## Gear

- **Tripod camera.** Canon EOS R50 V with the RF-S 14-30mm F4-6.3 IS STM PZ kit lens ([B0F258T13X](https://www.amazon.com/dp/B0F258T13X)) for fixed shots: explanation closeups, details, results and anything else framed from a tripod. The lens focuses to 0.15 m at 0.38× at 30 mm, close enough for weld-joint details without a macro lens.
- **POV camera.** GoPro HERO13 Black on baseball cap clip mount. Body-stabilized POV is the default angle for hands-on shop/build content, and the GoPro doubles as a second fixed wide angle on a tripod. Adventure Kit 3.0 head strap (purchased with the camera) is the alternative if the cap mount ever shifts mid-session.
- **Support and light.** SmallRig CT25 horizontal overhead tripod ([B0F8TDJH4J](https://www.amazon.com/dp/B0F8TDJH4J)) for looking down or obliquely into bench work, SmallRig CT-10 tripod ([B0B63VTW46](https://www.amazon.com/dp/B0B63VTW46)) for a fixed wide view, and the NEEWER NL-192AI two-panel bi-color LED kit ([B08TMBXLGD](https://www.amazon.com/dp/B08TMBXLGD)) for key and fill.
- **Audio.** DJI Mic Mini, 1 TX + 1 RX. USB-C receiver plugs direct into the iPhone. Used for narration audio (live or post-recorded).
- **iPhone.** Capture device for DJI Mic audio AND the editor (iMovie). Quik app handles wireless GoPro → cloud → Photos transfer. iCloud absorbs short-term Photos bloat; once a video ships to YouTube, source clips can be deleted locally.
- **HERO13 storage.** SanDisk Ultra Fit 256 GB USB-3.1 ([B07857Y17V](https://www.amazon.com/dp/B07857Y17V)) for offload (and the same model serves the Bambu H2C front USB for print timelapses).
- **R50 V storage.** SanDisk Extreme 128 GB SD card, UHS-I V30 ([B0G8LT6J46](https://www.amazon.com/dp/B0G8LT6J46)). The Anker USB-C dual-slot reader ([B07NW8RPYN](https://www.amazon.com/dp/B07NW8RPYN)) copies it to the Mac, which has no card slot; the reader takes the GoPro's microSD too.
- **GoPro Quik cloud subscription.** Active. Auto-syncs footage to phone on home-wifi reconnect, removes the manual "open Quik, transfer" step from the evening workflow.

## HERO13 capture settings

| Setting | Pick | Why |
|---|---|---|
| Resolution + Aspect Ratio | **4K 16:9** at 30 fps for horizontal shop videos | Gives room for a detail crop in a 1080p edit and works with the Linear digital lens. Full-sensor 8:7 video is available at 4K and 5.3K in supported frame rates; use a digital lens offered by that preset. |
| Frame rate | **30 fps** | Baseline. Use 60 fps for specific motion intended to play at half speed. |
| Digital Lens | **Linear** for the 16:9 profile | Shows mechanical geometry without the wide lens's fisheye appearance. Use the lens options offered by the selected resolution and aspect ratio; fixed explanation shots benefit from a composition without automatic horizon correction. |
| HyperSmooth | **On** for cap or handheld footage; **Off** on a rigid support | Fixed explanation shots need a stable composition for arrows and labels. Use the R50 V for small details that the stock GoPro lens cannot render sharply. |
| HDR | **Off** | Standard SDR footage combines with the R50 V's Standard Picture Style footage and phone inserts in the existing edit pipeline. |
| Audio | Default (Stereo) | Fine for ambient (tool clicks, welder hum). Real audio comes from the DJI Mic via the iPhone. |
| Orientation | **Auto** | Settings → Preferences → General → Orientation. Auto handles minor head tilt. "Locked Landscape" is for special use cases — not these. |
| Voice Control | **On** | Preferences → Voice Control. "GoPro start recording" / "GoPro stop recording" works hands-free for solder/weld/torch moments. |

**To check or change on the camera:** From the capture screen, tap the bottom strip showing current settings (e.g. "5.3K | 30 | W") to access Resolution, Aspect Ratio, Framerate, and Digital Lens. For Orientation and Voice Control: swipe down from the top → gear icon → Preferences → General.

GoPro documents the supported full-sensor modes in [HERO13 Black 8:7 Sensor Information](https://community.gopro.com/s/article/HERO13-Black-8-7-Sensor-Information?language=en_US) and exposure, color, and bitrate settings in [Advanced Protune Controls](https://community.gopro.com/s/article/HERO13-Black-Advanced-Protune-Controls-Explained?language=en_US).

## R50 V capture settings

Menu names are Canon's, from the [R50 V manual](https://cam.start.canon/en/C021/manual/html/UG-04_Shooting_0040.html).

| Setting | Pick | Why |
|---|---|---|
| Movie rec. size | **3840×2160, 29.97 fps, Standard (Long GOP)** | Matches the GoPro's 4K 30 fps. This size reads the full sensor width; 59.94 fps crops it. |
| Movie rec. format | **XF-AVC S YCC420 8bit** | H.264, the format Canon lists with the widest playback compatibility; Canon notes its 10-bit formats assume computer editing and may not play back in some software. |
| Color mode | **Picture Style: Standard**, HDR shooting (PQ) **Off** | Standard SDR that cuts with the GoPro footage without grading. |
| Exposure | **Movie manual exposure: 1/60 s, f/8 to start, lowest ISO that exposes well** | Exposure stays fixed through a hold, which keeps a clean plate stable for graphics. Close toward f/11 when a closeup's depth of field is too thin. |
| Zebra settings | **On** | Shows where stainless highlights clip. |
| White balance | **Color temperature 5600 K** | Matches the NEEWER panels at 5600 K. |
| Focus | **Focus mode MF**, MF peaking **On** | A fixed closeup shouldn't hunt. Set the kit lens's shared focus/control ring to focus in the camera menu; magnified view checks the edge. |
| IS mode | **Movie digital IS Off** | Canon recommends it off on a tripod; it magnifies the image and adds grain. |
| Tally lamp | **On** | The front lamp shows recording from the bench. |
| Auto pwr off temp. | **High** for long sessions | Extends recording time before a heat shutdown; Canon cautions the camera and card run hotter. |

## Carbonator weld capture

[Carbonator weld filming plan](carbonator-weld-shooting-plan.md) covers the shot list, fixed closeups for graphics, dry demonstrations, audio, and the solo shoot sequence. The guide uses the two tripods, the lights and both cameras: the GoPro holds the overall position and the R50 V the detail position, while the iPhone records the DJI mic. Process framing stays below shoulder level, including reflections and entry or exit.

Closeup setup instructions apply with the laser disabled. Active-process cameras require a position and optical protection suitable for that laser and use, as described in the filming plan.
