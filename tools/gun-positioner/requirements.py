"""Governing fabrication and measured commissioning requirements."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'hardware/printed-parts/fixtures/gun-positioner'
r={'status': 'Fabrication assets and commissioning specification. No printed, moving, loaded, accuracy or '
           'lifetime acceptance is recorded.',
 'print_recipe': {'material': 'Fiberon PET-GF15 rigid parts; TPU90A insulating gun pads',
                  'nozzle_mm': 0.4,
                  'abrasive_resistant': True,
                  'first_layer_mm': 0.2,
                  'normal_layer_mm': 0.24,
                  'walls': 6,
                  'top_bottom_layers': 6,
                  'infill': '40% gyroid',
                  'thin_part_rule': 'Bodies 4 mm or thinner: solid.',
                  'orientation': 'Use each part orientation in parts.json. Print pulley and belt coupon '
                                 'flat; guards open side up; fit bearings without forcing them.',
                  'support': 'No trapped support in current parts. Deburr and grade actual printed fits.',
                  'scope': 'Settings and geometric checks do not qualify strength, wear, creep or '
                           'accuracy. No printer job has been started.'},
 'fabrication': {'plate_material': '6061 aluminum, 6.35 mm',
                 'blank_tolerance_mm': 0.5,
                 'registered_hole_center_tolerance_mm': 0.25,
                 'paper_scale_check_mm': 50,
                 'paper_scale_allowed_error_mm': 0.25,
                 'source_interfaces': 'Transfer drill selected rail feet, bearing bases and switch bodies. '
                                      'Nominal catalog hole locations are not permission to force bolts '
                                      'into alignment.',
                 'thrust_seats': 'Flat metal bulkhead faces support the housing race on its10.5-16 mm '
                                 'annulus. The8.2-10.5 mm inner band is not face-supported. Center the '
                                 'housing race and qualify the actual assembled thrust reaction at the '
                                 'screening load. No counterbore is required.',
                 'fastener_rule': 'At least two full threads beyond locking nuts, no bottoming in '
                                  'purchased tapped holes, no threaded portion running in a bearing. Use '
                                  'exact joint schedule and check measured supplied stacks.',
                 'shaft_hubs': '12 mm 304 shafts have no transverse holes. Ream hub12 mm bore, saw1.5 mm '
                               'slit, and drill two4.2 mm X-axis clamp bores at Y16,Z6/19. Use two '
                               'grade12.9 M4x50 bolts per hub. Clamp with the specified25 in-lb clockwise '
                               'cam-over tool, never increasing the setting after a failed proof. Both '
                               'actual final-seat hub proofs and independent axial capture must pass '
                               'before loading.',
                 'nuts': 'One moving brass nut and two fixed retention nuts per axis: 18 total. Eight '
                         'purchased screws include eight nuts; five extra two-packs supply ten. Fixed nuts '
                         'use Loctite 243 after degreasing, 24 hour cure and witness marks. Measure thrust '
                         'stack and preload before cure.',
                 'tool_isolation': 'TPU pads separate every gun conductor and shell contact from the metal '
                                   'jaws. Verify no continuity from nozzle/electrode or intended work '
                                   'contact to the fixture; do not attach a work clip to the mount.',
                 'gauge_rear_screws': 'Four M4 rear screws attach the force gauge to the70x110 backing '
                                      'plate on41x73 centers. Use included screws only if6.35 mm plate '
                                      'plus metal washer leaves full required engagement without bottoming '
                                      'in measured sockets. Otherwise finish four spare M4x25 screws to '
                                      'that measured stack; at least4 mm engagement unless the '
                                      'manufacturer requires more.',
                 'spacer_stock': 'All8 OD metal spacers use8 OD/6 ID6063 tube, including nut frames, force '
                                 'outer/center tubes, crash ties, shield/keeper stand-offs and roll feet. '
                                 'Bolts locate plates through their holes; tubes carry clamp load. Use10 '
                                 'OD/8 ID tube for KP08 risers and axle contacts; drill hinge/swivel '
                                 'contacts to8.5 mm ID. M4 riser washers must have at least10 mm OD. '
                                 'Fiber-base and Z-gauge M6 spacers use10 OD/8 ID tube for bolt clearance. '
                                 'KP08 risers use that same source; hinge/swivel/redirect contact tubes '
                                 'are drilled8.5 ID.',
                 'fiber_swivel': 'Two fixed printed bases each sit on four10 mm metal10 OD/8 ID spacers, '
                                 'attached withM6x30 slot8 hardware. A separate M8x50 axle clamps13 mm '
                                 'lower tube,608 inner race,4 mm upper tube and washers. The rotating '
                                 'saddle carries the outer race and its two-M3 cap; fixed metal must clear '
                                 'the rotating print through360 degrees.',
                 'shaft_end_threads': {'shaft_cuts_mm': [175, 165, 130, 85],
                                       'ends_per_shaft': 2,
                                       'thread': 'M5x0.8',
                                       'usable_full_thread_depth_mm': 10,
                                       'pilot_diameter_mm': 4.2,
                                       'pilot_depth_mm': 16,
                                       'end_screw': 'M5x12',
                                       'steel_retainer_washer_mm': {'OD': 20, 'ID': 6, 'thickness': 2},
                                       'M5_flat_washer_thickness_mm': 0.8,
                                       'nominal_engagement_mm': 9.2,
                                       'nominal_bottom_margin_mm': 0.8,
                                       'finish': 'Deburr end, center accurately, drill with depth stop, '
                                                 'and tap with the sourced M5 tool. Verify at least10 mm '
                                                 'of usable full thread with a depth check; pilot depth '
                                                 'includes tap lead, not usable thread. The actual '
                                                 'measured screw reach is12 minus both washer thicknesses. '
                                                 'Require at least8 mm engagement and at least0.8 mm '
                                                 'before bottoming; reject an unmeasurable or incomplete '
                                                 'tap. Do not add transverse holes.',
                                       'scope': 'Some blind end bores overlap terminal hub seats. Use '
                                                'conservative5 mm major diameter for the local hollow '
                                                'section, and proof the actual completed shaft seat. No '
                                                'hole continues through the free loaded inter-hub span.'}},
 'motion': {'XYZ_soft_mm': [-85, 85],
            'XYZ_switch_mm': [-89, 89],
            'XYZ_metal_stop_mm': [-94, 94],
            'angular_soft_deg': {'yaw': [-20, 20], 'pitch': [-20, 10], 'roll': [-20, 20]},
            'angular_switch_deg': {'yaw': [-21, 21], 'pitch': [-21, 11], 'roll': [-21, 21]},
            'angular_stop_deg': {'yaw': [-22, 22], 'pitch': [-22, 12], 'roll': [-22, 22]},
            'rail_block_margin_at_metal_stop_mm': 22.5,
            'command_pulses_per_mm': 6400,
            'nominal_fullstep_um': 2.5,
            'scope': 'Command length is not tool pose. Observe actual loaded motion and recalibrate the '
                     'gun datum after any stop, reset or release. Single-nut backlash is assessed from '
                     'camera response; do not assume blind counted return.'},
 'overload_links': {'source_spring': 'B0B771L8G8, blue 16 OD x 8.5 ID x 20 mm free, nominal 43 N/mm',
                    'spring_quantity': 24,
                    'seated_preload_N': {'X_Y': 250,
                                         'Z_up_negative_screw_length': 250,
                                         'Z_down_positive_screw_length': 400,
                                         'pitch': 130,
                                         'yaw_roll': 100},
                    'nominal_trip_mm': {'angular': 0.3, 'XYZ': 0.75},
                    'capture_mm': 1.0,
                    'required_remaining_switch_overtravel_mm': {'angular': 0.8, 'XYZ': 0.35},
                    'spring_nominal_maximum_compression_at_capture_mm': {'X_Y_Z_up': 3.9069767441860463,
                                                                         'Z_down': 5.651162790697675,
                                                                         'pitch': 2.511627906976744,
                                                                         'yaw_roll': 2.162790697674419},
                    'spring_grade': ['Measure each spring free length, solid length and force through the '
                                     'intended working region using the guarded force fixture. Grade '
                                     'directional pairs together; do not rely on color or nominal catalog '
                                     'rate.',
                                     'Directional compression C = desired preload / (measured k1 + '
                                     'measured k2). Set outer force spacer length = 20 - C + 1.5 mm '
                                     'washer, adjusted for actual free length. Set nut outer spacer length '
                                     '= force spacer length - 10.825 mm. Use matched metal shims or '
                                     'finished tube lengths on all four ties; never use printed shims in '
                                     'the load path.',
                                     'Keep central 8.35 mm spacer unchanged: it sets fixed shoulder '
                                     'inner-face separation and +/-1.0 mm capture independently of spring '
                                     'preload.',
                                     'At capture, actual spring compression C + 1.0 mm must be below both '
                                     '8.0 mm catalog compression and actual free-minus-solid length minus '
                                     '1.0 mm clearance. Reject a spring that cannot meet force and travel '
                                     'together.',
                                     'Adjust two independent switch mounts to measured force, nominal '
                                     '+/-0.30 angular or +/-0.75 XYZ. Cam holds a flat dwell after trip; '
                                     'verify the purchased switch survives remaining travel plus 0.1 mm '
                                     'setup tolerance.'],
                    'static_test': ['Laser key off, drill motor unplugged, carriage and gun removed. Gauge '
                                    'rear backing plate is vertical in the PONY drill vise, load axis up; '
                                    'verify included M4 rear screw depth.',
                                    'The metal force-test platen reacts only on the fixed cage. Quill '
                                    'pusher contacts only the output shuttle; it must not touch end '
                                    'plates, fixed tie bolts, spacers or nut cartridge. Guard and capture '
                                    'springs. Reverse the loose link for the opposite sign.',
                                    'Read trip force while observing the loop opening. Include the '
                                    'force-tool full-scale uncertainty and fixture allowance inside the '
                                    'accepted window; nominal +/-5 N instrument allowance alone is not a '
                                    'complete uncertainty budget.'],
                    'powered_test': ['Remove vessel and real gun. Use the spare 200 mm screw in the test '
                                     'cartridge, output fork ahead of the screw tip. Clamp its fixed metal '
                                     'foot independently to the table; clamp gauge backing vertically with '
                                     'load axis down.',
                                     'The gauge compression button contacts the center of the metal output '
                                     'bridge. Both fork arms attach only to the output shuttle, outside '
                                     'the fixed cage. All fixed reaction returns through the gauge and its '
                                     'vise; no cage/output bypass is permitted. Reverse cartridge and fork '
                                     'for the other direction.',
                                     'At every permitted current, speed and acceleration, powered peak '
                                     'including tool and fixture uncertainty must be<=140 N yaw/roll,<=165 '
                                     'N pitch,<=350 N X/Y/upward Z,<=500 N downward Z. Static trip bands '
                                     'are100-140,148-165,250-350,440-500 N respectively. A low-current '
                                     'stall below preload demonstrates only the force ceiling: observe '
                                     'actual motion, pressSTOP and abort without retry. Separately open '
                                     'the loop with controlled external load or manual switch actuation to '
                                     'prove all six axes inhibit and latch. Do not increase current merely '
                                     'to force a trip.',
                                     'After any trip, mechanically support the load, disconnect power, '
                                     'recenter and inspect link, then restore a fresh observed datum. '
                                     'Motor current is not a calibrated force limiter.'],
                    'accepted_static_trip_N': {'X_Y_Z_up': [250, 350],
                                               'Z_down': [440, 500],
                                               'pitch': [148, 165],
                                               'yaw_roll': [100, 140]},
                    'powered_peak_ceiling_N': {'X_Y_Z_up': 350,
                                               'Z_down': 500,
                                               'pitch': 165,
                                               'yaw_roll': 140},
                    'Z_direction': 'Positive screw-length direction is downward gravity loading, with400 N '
                                   'seat and440-500 N static trip; the negative/upward direction '
                                   'retains250 N seat and250-350 N trip. Controller positiveZ shortens the '
                                   'screw.',
                    'compression_guard': 'Normal Z gravity places the400 mm screw in tension because its '
                                         'thrust end is at the top. Upward obstruction compression is '
                                         'bounded by350 N including uncertainty. The assumed5.5 mm root '
                                         'Euler bound is about554 N and is only a sizing screen; guarded '
                                         'powered tests must show no bow, capture impact, yielding or loss '
                                         'of load.',
                    'pitch_direction': 'Pitch uses130 N seated preload in both directions,148-165 N static '
                                       'trip and165 N powered ceiling. Its screened normal actuator force '
                                       'is100 N; yaw and roll retain100 N seats.'},
 'retention': {'type': 'Spring-loaded dry steel friction washer on the unoccupied fixed brass-nut flange. '
                       'Three independent retainers: Z, pitch and roll.',
               'spring_source': 'B0F2F2X8V7, 25 OD x 13.5 ID x 25 mm free; source rate unspecified.',
               'spring_rate_accept_N_per_mm': [20, 40],
               'washer_contact_annulus_mm': [13, 22],
               'assumed_mean_contact_radius_mm': 8.943915,
               'target_breakaway_Nm': {'z': 0.215, 'pitch': 0.07, 'roll': 0.03},
               'accepted_breakaway_Nm': {'z': [0.2, 0.23], 'pitch': [0.06, 0.08], 'roll': [0.02, 0.04]},
               'posts': 'Four M6x80 metal posts per seat, finish under-head length 72.5 mm; two M6 jam '
                        'nuts per post. Two M3x50 guide bolts per steel washer, six total. Guide holes '
                        'allow slight washer tilt and free sliding.',
               'grade': ['Grade actual spring rate over operating force range, free and solid lengths. '
                         'Finish spring-seat position by measured torque; guessed friction coefficient and '
                         'thread counts cannot accept a retainer.',
                         'Keep brass contact flange and washer grease-free. Washer may tilt to follow '
                         'flange runout; anti-rotation bolts must not bind it. Check full flange support, '
                         'pin clearance and seated washer contact through a complete turn.'],
               'torque_test': ['With screw horizontal and gun removed, fit balanced metal service lever to '
                               'rotating left flange in place of its pulley, using four M3 bolts. Pivot is '
                               'at its center; hanging mass acts at exactly 100 mm. Guard the mass and '
                               'lever.',
                               'At eight shaft phases 45 degrees apart, measure breakaway in both '
                               'directions. Use the characterized tangential cord redirect whenever the '
                               'load hole is not horizontal. Direct hanging mass is valid only at '
                               'horizontal load-hole phases. Weigh cup, cord and load; every corrected '
                               'result including uncertainty must fit its axis band.',
                               'For installed vertical Z, use the 608 cord redirect on a clamped metal '
                               'bracket. Cord at the lever must be horizontal and tangential, redirecting '
                               '90 degrees into the hanging load. Characterize wheel loss in both '
                               'directions with two 200 g cups: movement must begin with <=5 g imbalance. '
                               'This bounds torque correction by 0.00491 N m at 100 mm.',
                               'For every retainer accept only the complete torque interval [measured '
                               'torque minus uncertainty, measured torque plus uncertainty] inside its '
                               'axis band. For Z that band is0.20-0.23 N m. Include mass, lever radius, '
                               'tangent alignment, load-dependent redirect loss, bracket and dynamics; a5 '
                               'g redirect test alone does not consume the full uncertainty budget safely.',
                               'Remove service lever and redirect before powered motion. Restore pulley, '
                               'guarded belt and witness marks.'],
               'loaded_test': ['Tube removed and camera stages retracted; laser key off. Fit independent '
                               'short steel tethers and a metal support stand with maximum 5 mm catch gap. '
                               'Require at least 10 mm clearance from fixed metal along the possible catch '
                               'path.',
                               'Use the actual gun and supported cable. Check accepted gravity poses, Z '
                               'endpoints and pitch-20/+10 in a clear dry envelope. Screening envelope '
                               'is300 N Z axial force and10 N m angular output moment. Actual mass, '
                               'vertical cable pull and angular cable moments must be bounded before '
                               'loaded motion.',
                               'Set the owned 12.7 micrometre indicator on rigid metal. Record powered '
                               'baseline and camera views, cut 24 V motor power, then read at 0, 1, 5 and '
                               '10 minutes. Pass coarse screening only with no indicator-resolved growth, '
                               'no visible jump or slip, and no catch contact.',
                               'Any drift, catch contact, loose retainer, changed witness mark or '
                               'out-of-band torque fails: park on the support stand, diagnose and '
                               'requalify before loaded seam use.'],
               'indicator_resolution_um': 12.7,
               'indicator_scope': 'No resolved creep is a coarse holding screen; it does not establish 5 '
                                  'or 10 micrometre coordinate accuracy.',
               'recheck': ['Before each loaded session inspect washer, guide bolts, spring seats, witness '
                           'marks and tethers; check full-turn breakaway.',
                           'Repeat torque and loaded power-cut after first 30 minutes, hot/cold settling, '
                           'cleaning, adjustment, replacement, slip or unexplained response.'],
               'motor_margin': 'Qualify actual forward/reverse motion at the final per-axis current and '
                               'permitted speed. Retainer torque must remain in its band and below '
                               'demonstrated motor margin; no catalog holding-torque extrapolation accepts '
                               'motion.',
               'washer_source': 'B0FHPD4N73: steel M12 large washer, measured nominal13 ID x37 OD x3 mm. '
                                'Verify actual supplied bore and thickness; seat placement includes3 mm '
                                'washer.',
               'actual_load_bound': ['Weigh carried pieces separately with the qualified2 kg scale; use '
                                     'the500 N force gauge for heavier carried subassemblies. Include '
                                     'fasteners, wires, gun and supported umbilical. Bound maximum Z '
                                     'weight plus measured vertical cable pull by300 N, including '
                                     'measurement uncertainty.',
                                     'The balanced100 mm angular-load-lever has26x20 mm M5 mounting holes. '
                                     'Park and independently restrain the actual carried gun/cradle. '
                                     'Transfer the lever to the SEPARATE ANGULAR DRIVE-LEVER hub, reusing '
                                     'its four M5x45 bolts, while the output hub continues to carry the '
                                     'actual gun/cradle mass. Keep both split-clamp screws installed. '
                                     'Gauge/cord and support restrain the rotor BEFORE either actuator '
                                     'clevis is disconnected.',
                                     'At each physically accepted pose with the real gun and cable, '
                                     'measure signed tangential onset thresholds in both directions at the '
                                     'measured100 mm load radius. Use the500 N compression gauge on '
                                     'its70x110 metal backing plate, independently clamped in the vise, '
                                     'reversing its reaction side as required. For low roll forces use '
                                     'weighed cups and the characterized tangent redirect. Prevent any '
                                     'unrestrained motion; observe onset and stop before capture contact.',
                                     'Use the larger absolute threshold plus measurement and alignment '
                                     'uncertainty as a conservative gravity/cable moment bound; this '
                                     'includes bearing resistance. Convert that moment to actuator force '
                                     'using the minimum measured dL/dtheta over the accepted path, bounded '
                                     'by the conservative133.60 mm geometry lever only after the physical '
                                     'clevis dimensions agree. Add uncertainty before computing ideal '
                                     'backdrive torque F*0.002/(2*pi), and require retained minimum '
                                     'breakaway at least twice that value.',
                                     'Restore clevis and hub hardware, clamp preload and witness marks, '
                                     'then establish a fresh observed datum. The loose powered test '
                                     'fixture does not measure installed net actuator load. Endpoint cable '
                                     'pull alone cannot establish a free-couple bound.',
                                     'For Z, brace the500 mm test4040 column to the station using two '
                                     'spare matched corner brackets. Attach the70x160 gauge backing with '
                                     'twoM6x25 slot8 bolts and10 mm metal spacers; mount the gauge with '
                                     'the same four measured-depth M4 rear screws. Adjust gauge axis up '
                                     'under the retained Z-head upright using the60x40 load platen. Place '
                                     'an independent catch within1 mm, take the full load on gauge/platen, '
                                     'then disconnect the actuator output. Gauge and platen contact only '
                                     'the moving head. Record supported downward load and controlled onset '
                                     'thresholds with actual cable over accepted poses; include rail drag '
                                     'and uncertainty in the300 N bound. Restore actuator and fresh datum '
                                     'before motion. Do not use the test column for powered travel. The '
                                     'gauge backing has two12x6.5 vertical guide slots. The '
                                     'separate50.8x50.8x6.35 metal jack angle sits60 mm below its lower '
                                     'edge, mounted by twoM6x16 slot8 bolts. Its fully threaded M6x80 feed '
                                     'screw pushes only the metal backing edge. Hold the lower metal nut '
                                     'with a10 mm wrench, loosen the upper lock nut, feed no more than1/12 '
                                     'turn(0.0833 mm), and relock after each step. Guide bolts retain the '
                                     'backing laterally without bypassing axial force. Measure both '
                                     'increasing/upward and decreasing/downward onset while observing '
                                     'camera/indicator, with the catch within1 mm; stop before catch '
                                     'contact. Never loosen the column braces or lift by hand to produce a '
                                     'gauge reading.'],
               'actual_load_screen': {'Z_N': 300,
                                      'pitch_actuator_N': 100,
                                      'angular_output_moment_Nm': 10,
                                      'required_breakaway_to_ideal_backdrive_ratio': 2,
                                      'pitch_shaft_moment_Nm': 15,
                                      'pitch_minimum_breakaway_at_100N_Nm': 0.06366197723675814,
                                      'scope': 'The measured minimum breakaway, including uncertainty, '
                                               'must exceed twice the actual ideal backdrive bound as well '
                                               'as lie in the axis band. The lower0.06 N m pitch band edge '
                                               'alone does not accept the full100 N screen;100 N requires '
                                               'at least0.063662 N m before added uncertainty.'}},
 'crash_release': {'structure': 'Two seated axial pods guide four ground 8x100 mm rods; transverse '
                                'three-ball hardened V-seat magnetic plate retains the detachable gun '
                                'tray. Two guides per pod separated 30 mm; lower guide has two bronze '
                                'bushings separated 40 mm.',
                   'springs': 'Four B08FDWP3K6 springs, stated 4.68 N/mm, nominal free 25 mm. Grade actual '
                              'free, solid and rate; stated force/travel is inconsistent. Match '
                              'directional preload to real gun/cable gravity baseline.',
                   'magnets': 'Three B08LYPDYY5 steel cup magnets, 25 OD x 7.7 high, 5.6 through bore, '
                              '10.6 countersink top. Three M5x25 countersunk through-bolts. Three '
                              'carbon-steel M6-bore x25 OD x2 mm striker washers. Shim pole gaps only '
                              'after hardened seats are fully seated. Contact pull rating does not predict '
                              'nozzle release.',
                   'contact_hardware': 'Three hardened 8 mm balls and six hardened 4x20 mm dowels forming '
                                       'three V seats. Metal keepers retain dowels; retaining compound '
                                       'locates parts. Do not bear precision balls against aluminum.',
                   'capture_and_tether': 'Axial metal capture +/-1.0 mm; short independent steel tethers '
                                         'and padded metal catch support retain detached gun. Collars only '
                                         'locate rods and carry no working axial thrust.',
                   'contacts': 'Four independently mounted contacts. Hard relay channel: one bidirectional '
                               'axial COM-NC cam switch in series with one plate-presence COM-NO held '
                               'pressed when seated. Sense channel duplicates those two contacts. Each '
                               'channel opens for either axial sign or plate release/missing plate.',
                   'accepted_added_nozzle_force_N': [20, 30],
                   'qualification': ['Laser key off, vessel removed, real gun and supported umbilical '
                                     'installed. The two spare metal jaw bars and TPU pads clamp a safe '
                                     'rigid body area. Two outboard metal fork arms and bridge apply cord '
                                     'load at the measured virtual nozzle endpoint after consumable wire '
                                     'is removed. Nothing presses nozzle optics, guide, trigger or vents.',
                                     'At each accepted pose record gravity/cable baseline while seated '
                                     'with zero added external load. Added nozzle force is the hanging '
                                     'cord load, not a total gauge reading with an estimated gun weight '
                                     'subtracted. Grade both axial signs and transverse directions; redo '
                                     'baseline after cable or pose change.',
                                     'Warm owned scale for two minutes on a level draft-free surface. '
                                     'Check0/500/1000/1500/2000 g ascending and descending for three '
                                     'cycles using statedM1 1 kg and statedM2 reference set. Every error '
                                     'must be<=0.3 g and zero return0.0+/-0.1 g. If span fails, calibrate '
                                     'with1 kg and repeat. The listed classes have no certificates; '
                                     'preserve that qualification limit.',
                                     'Weigh complete cup/cord plus each aliquot separately below2 kg, then '
                                     'sum verified masses. Allow1.0 g uncertainty per aliquot including '
                                     'reference, resolution, zero and span; sum linearly and multiply '
                                     'by0.00980665 N/g. Record the bracket between last held and first '
                                     'released mass steps.',
                                     'Characterize bidirectional redirect loss using200 g cups and<=5 g '
                                     'imbalance, and again at the intended2-3 kg load because bearing '
                                     'friction grows with load. Add load-dependent loss, cord alignment, '
                                     'actual eye position, release bracket and dynamics into totalU. '
                                     'Accept only the complete[F-U,F+U] interval inside20-30 N. Repeat '
                                     'zero/1 kg checks each session. The500 N gauge cannot accept this '
                                     'small-force band.',
                                     'Verify seated working stiffness and running guide clearance '
                                     'separately. Both independent electrical channels must open at axial '
                                     'trip or plate separation/missing plate. Recalibrate actual tool and '
                                     'camera datum after every release.',
                                     'Release cuts positioner motor power; operator stops the independent '
                                     'pedal rotator during dry testing. No live welding integration is '
                                     'included.']},
 'working_path': {'candidate_angles_deg': {'yaw': [-5, 5], 'pitch': [-10, 10], 'roll': [-5, 5]},
                  'endpoint_offsets_mm': [-0.25, 0.25],
                  'XYZ': 'Correlated compensation from actual calibrated gun transform to keep the '
                         'endpoint at the seam.',
                  'required_clearance': 'CAD proxy screen plus physical static sweep of actual gun, tray, '
                                        'fixture, vessel, camera lenses and umbilical. Full independent '
                                        'travel box is not a loaded seam envelope.',
                  'wire_scope': 'Consumable wire intended to contact seam is excluded from solid-body '
                                'clearance; its endpoint must be observed in both views.',
                  'fiber': 'Independent boom with two swivel saddles; active optical fiber radius at least '
                           '350 mm and no twist throughout accepted path. Boom dimensions alone do not '
                           'accept cable routing.'},
 'thermal_gate': {'motor_case_max_C': 50,
                  'stability': 'Across three consecutive5-minute intervals at final current, rate and '
                               'duty, no increasing trend beyond documented instrument and contact '
                               'repeatability uncertainty. Reading plus uncertainty stays<=50 C. Repeat '
                               'response, retention and datum checks after settling.'},
 'work_coordinate': {'required_mm': 0.01,
                     'design_target_mm': 0.005,
                     'scope': 'Requires observed actual dot, wire endpoint and seam localization, '
                              'calibrated two-view geometry, independently bounded measurement uncertainty '
                              'and loaded settling. CAD and nominal command resolution cannot qualify it.'},
 'stopped_assembly_support': 'A clamped metal Z-deck support and metal stand under the cradle support '
                             'stopped assembly. Remove only after loaded holding and clear dry motion '
                             'gates pass.',
 'shaft_hub_qualification': {'clamp_tool': {'name': 'LEXIVON cam-over screwdriver',
                                            'asin': 'B0H958ZSXW',
                                            'bit_set_asin': 'B0D4TDR7M8',
                                            'bit': '3 mm hex',
                                            'setting_in_lbf': 25,
                                            'nominal_Nm': 2.824620725,
                                            'clockwise_upper_with_4pct_Nm': 2.937605554,
                                            'absolute_ceiling_Nm': 3.0,
                                            'procedure': 'Hold the locking nut and drive the M4 head '
                                                         'clockwise. Alternate the two bolts through 10, '
                                                         '20, then 25 in-lb stages using the calibrated '
                                                         'cam-over screwdriver and H3 bit. The 25 in-lb '
                                                         'nominal is 2.824620725 Nm; the stated +4% '
                                                         'clockwise upper bound is 2.937605554 Nm, below '
                                                         'the absolute 3.0 Nm ceiling. Prevailing nylock '
                                                         'torque is included and lowers preload. Retain '
                                                         'tool serial, certificate and setting. Failed '
                                                         'grip rejects the joint; do not increase the '
                                                         'setting.'},
                             'proof_part': 'hub-proof-lever',
                             'saddle_part': 'hub-proof-load-saddle',
                             'fixture': 'hub-clamp-proof',
                             'nominal_radius_mm': 140,
                             'interval_Nm_by_hub': {'yaw-output-hub': [25.2, 27.5],
                                                    'yaw-lever-hub': [25.2, 27.5],
                                                    'pitch-lever-hub': [30, 32.5],
                                                    'pitch-output-hub--1': [30, 32.5],
                                                    'pitch-output-hub-1': [25.2, 27.5],
                                                    'roll-lever-hub': [25.2, 27.5],
                                                    'roll-output-hub': [25.2, 27.5]},
                             'nominal_force_N': {'high_pitch_path': 224, 'other_path': 188},
                             'actual_seats': [{'hub': 'yaw-output-hub',
                                               'shaft_length_mm': 175,
                                               'specimen_mm': [0, 25],
                                               'companion_mm': [26, 51],
                                               'bearing_center_mm': 66.35},
                                              {'hub': 'yaw-lever-hub',
                                               'shaft_length_mm': 175,
                                               'specimen_mm': [100, 125],
                                               'companion_mm': [74, 99],
                                               'bearing_center_mm': 58.65},
                                              {'hub': 'pitch-lever-hub',
                                               'shaft_length_mm': 130,
                                               'specimen_mm': [10, 35],
                                               'companion_mm': [36, 61],
                                               'bearing_center_mm': 76.35},
                                              {'hub': 'pitch-output-hub--1',
                                               'shaft_length_mm': 130,
                                               'specimen_mm': [105, 130],
                                               'companion_mm': [79, 104],
                                               'bearing_center_mm': 63.65},
                                              {'hub': 'pitch-output-hub-1',
                                               'shaft_length_mm': 85,
                                               'specimen_mm': [0, 25],
                                               'companion_mm': [26, 51],
                                               'bearing_center_mm': 66.35},
                                              {'hub': 'roll-lever-hub',
                                               'shaft_length_mm': 165,
                                               'specimen_mm': [51, 76],
                                               'companion_mm': [77, 102],
                                               'bearing_center_mm': 117.35},
                                              {'hub': 'roll-output-hub',
                                               'shaft_length_mm': 165,
                                               'specimen_mm': [134, 159],
                                               'companion_mm': [108, 133],
                                               'bearing_center_mm': 92.65}],
                             'geometry': {'specimen_mm': [0, 25],
                                          'face_gap_mm': 1,
                                          'companion_mm': [26, 51],
                                          'loaded_lever_mm': [-6.35, 0],
                                          'reaction_plate_mm': [51, 57.35],
                                          'bearing_center_mm': 66.35,
                                          'bearing_axial_envelope_mm': [58.35, 74.35],
                                          'bearing_footprint_mm': {'across_shaft': 71, 'along_shaft': 16},
                                          'gauge_force_axial_plane_mm': -3.175,
                                          'conservative_force_plane_to_reacted_hub_boundary_mm': 32.35,
                                          'shaft_axis_height_mm': 75.35,
                                          'support_foot': 'pitch-bearing-foot',
                                          'foot_beam_holes_mm': [[0, -20, 8.5], [0, 20, 8.5]],
                                          'riser_mm': 10,
                                          'beam': 'Reuse500 mm Z-test column horizontally',
                                          'reaction_plate': 'angular-lever',
                                          'vise_grip_area_global_X_mm': [95, 130],
                                          'gauge_cap_backplate_holes_mm': [[-28, 48.2, 5.5],
                                                                           [28, 48.2, 5.5]],
                                          'rear_M4_to_cap_M5_washer_center_distance_mm': 13.896762213120235,
                                          'rear_screw_sets': 'Four dedicated proof M4x25 screws are '
                                                             'finished for the 6.35 mm plate, 7 mm rear '
                                                             'spacers and two 1 mm large washers; the '
                                                             'normal four-screw gauge set is separate. '
                                                             'Verify actual reach, at least 4 mm '
                                                             'engagement and nonbottoming socket depth.'},
                             'sequence': ['Complete centered end taps, mark every final seat and record '
                                          'shaft straightness/runout baseline with the owned indicator. A '
                                          'resolution12.7 um tool can only reject resolved changes; it '
                                          'cannot establish micrometre straightness.',
                                          'Install the specimen on its actual final marked seat. Place a '
                                          'companion hub on the same completed shaft with a visible1 mm '
                                          'face gap; adjust the far bearing using the per-seat table. No '
                                          'specimen-to-companion face contact.',
                                          'Remove every shaft-end washer and capture tube that could touch '
                                          'the proof lever/specimen. Independently support actual carried '
                                          'masses; this loose horizontal fixture carries no gun. Place a '
                                          'noncontact catch under shaft/hubs and a lever stop that cannot '
                                          'carry force during a reading.',
                                          'Use one borrowed KP001 on a borrowed90x60 foot with two10 mm '
                                          'metal risers/M6x40 bolts. Two spare M8x16/slot8 joints hold its '
                                          'centerline beam holes. Positively secure the horizontal column '
                                          'and the purchased vise through actual factory slots using two '
                                          'temporarily reused M8x75 bench anchors. Verify actual grip and '
                                          'two protruding threads.',
                                          'Bolt the reaction angular-lever plate to the companion with '
                                          'four M5x45; vise grips only its free metal area. Bolt the300x30 '
                                          'proof lever to the ungripped specimen with four M5x45. No vise '
                                          'pressure touches either hub or the bare shaft.',
                                          'Transfer two metal angles and two M5x20 bridge joints from the '
                                          'powered-fork fixture to the symmetric proof saddle. One M5x25 '
                                          'cross tie attaches both angle legs at the140 mm lever hole. The '
                                          'horizontal bridge centers the gauge force in the lever '
                                          'midplane, not on an offset bolt end.',
                                          'Mount the500 N gauge to its70x110 backing with four7 mm rear '
                                          'spacers and allocated M4x25 screws finished to actual socket '
                                          'depth. The70 mm formed-angle cap uses two M5x25; quill contacts '
                                          'only the cap centered on the gauge axis. Gauge probe contacts '
                                          'only the saddle. Drill motor unplugged. Tare and span/check the '
                                          'gauge per its documented uncertainty.',
                                          'Measure actual pivot-to-force radius, force alignment and total '
                                          'force uncertainty. Quasi-statically advance the manual quill to '
                                          'the intended force without impact; hold10 s in each sign. Move '
                                          'saddle/gauge to the opposite140 mm hole for the reverse sign. '
                                          'Accept only the full computed torque interval within that hub '
                                          'band. A high-path224 N example with radius140+/-0.5 mm, '
                                          'force+/-5 N and<=3 degree tangency has30.509..32.175 Nm before '
                                          'any additional uncertainty; the example does not replace the '
                                          'actual bounds.',
                                          'Reject visible witness slip, contact bypass, yielding, opening, '
                                          'residual twist or straightness/runout growth resolved after '
                                          'unloading. Gauge/load/angle uncertainty and actual contact '
                                          'geometry are recorded.',
                                          'Every hub must be the ungripped specimen on its own final '
                                          'completed shaft seat. Testing another seat or another shaft '
                                          'does not qualify friction equivalence. Restore positive end '
                                          'capture, clamp tool setting/witnesses, all actuator joints and '
                                          'a fresh observed datum.'],
                             'warm_cycle_recheck': 'Repeat both signed10 s proof ramps after50 supervised '
                                                   'reversals within a physically accepted dry subset and '
                                                   'settled measured temperature, preserving the actual '
                                                   'clamp setting and recording specimen temperature '
                                                   'during the proof. If dismantling/cooling prevents '
                                                   'testing the intended warm condition, that temperature '
                                                   'range remains unqualified. Repeat after retightening, '
                                                   'sliding a hub, cleaning, release or witness movement. '
                                                   'This is screening, not lifetime acceptance.',
                             'scope': 'Combined bending/torsion/contact arithmetic uses205 MPa nominal304 '
                                      'yield and conservative5 mm bored end section. Contact pressure, '
                                      'friction, material temper, tip geometry and residual stress are not '
                                      'certified by that screen; actual no-slip/no-set proof and accepted '
                                      'load paths govern.'},
 'shaft_axial_capture': {'tube_stock': '20 OD /12 ID aluminum, finish bore12.5 mm',
                         'nominal_lengths_mm_by_shaft': {'yaw': [35.15, 16, 14.65, 11.5],
                                                         'pitch-negative': [9.5, 15.15, 25.15],
                                                         'pitch-positive': [25.15, 11.5],
                                                         'roll': [21.5, 12, 27.15, 1.15, 5.5]},
                         'pieces': 14,
                         'finished_total_mm': 231.04999999999998,
                         'roll_front_bearing_center_mm': -122,
                         'steel_end_washers': 8,
                         'end_screws': 'Eight M5x12',
                         'fit': 'Finish each stack to delivered bearing inner-race faces. Tubes contact '
                                'only inner race, metal plate, hub or end washer. Relieve/chamfer20 mm OD '
                                'to actual inner-race face; no seal or outer-race load. Nominal one-side '
                                'gaps0.5 mm; actual captured excursion must stay<=1 mm. Qualify free '
                                'rotation cold and warm with no rubbing.',
                         'positive_path': 'Each shaft is bounded by its two bolted steel end washers and '
                                          'metal tubes against the bearing inner races. Terminal '
                                          'hubs/output plates are bounded by those end washers, tubes and '
                                          'inner races; internal drive hubs are bounded between the two '
                                          'adjacent inner races. Clamp friction and bearing setscrews are '
                                          'not the safety retention path.',
                         'acceptance': 'Each actual shaft/hub metal capture path and both force signs must '
                                       'pass the complete measured450..500 N interval for10 s without a '
                                       'force bypass, catch contact, yielding, release or resolved '
                                       'permanent change; retained movement is at most1 mm. Actual '
                                       'delivered stack and gauge thread/uncertainty checks govern.',
                         'steel_end_washer_spec': {'asin': 'B0DYK1PVYB',
                                                   'material': '304 stainless steel',
                                                   'OD_mm': 20,
                                                   'ID_mm': 6,
                                                   'thickness_mm': 2,
                                                   'quantity': 8,
                                                   'pack_quantity': 60,
                                                   'flat_M5_washer_mm': 0.8,
                                                   'end_bolt': 'M5x12',
                                                   'nominal_engagement_mm': 9.2,
                                                   'usable_full_thread_mm': 10,
                                                   'pilot_diameter_mm': 4.2,
                                                   'pilot_depth_mm': 16,
                                                   'minimum_engagement_mm': 8,
                                                   'minimum_bottom_margin_mm': 0.8},
                         'fixture': 'shaft-capture-proof',
                         'interface_parts': {'interface': 'shaft-capture-interface',
                                             'bridge': 'shaft-capture-bridge',
                                             'bridge_tubes': 'capture-bridge-spacer',
                                             'gauge_back': 'installed-Z-gauge-back',
                                             'gauge_cap': 'proof-gauge-quill-cap',
                                             'column': 'Reuse 500 mm installed Z test column',
                                             'gauge_coupler': {'asin': 'B0DHGXW6G9',
                                                               'material': '304 stainless steel',
                                                               'thread': 'M6x1.0',
                                                               'length_mm': 20,
                                                               'across_flats_mm': 10,
                                                               'quantity': 1,
                                                               'pack_quantity': 6},
                                             'gauge_stud': 'One M6x16 with one1 mm washer',
                                             'catch_upper': 'capture-catch-upper',
                                             'catch_lower': 'Reuse drive-test-foot',
                                             'catch_tubes': 'capture-catch-spacer'},
                         'fixture_geometry': {'interface_blank_mm': [100, 60, 6.35],
                                              'interface_center_clearance_mm': 22,
                                              'hub_M5_pattern_mm': [26, 20],
                                              'M3_tie_pattern_mm': [60, 40],
                                              'bridge_blank_mm': [100, 60, 6.35],
                                              'bridge_center_hole_mm': 6.5,
                                              'bridge_spacers_mm': 75,
                                              'bridge_tie_stack_mm': 92.7,
                                              'tie_slack_mm': 0.2,
                                              'shaft_axis_Y_mm': -78.175,
                                              'chosen_end_Z_mm': 200,
                                              'canonical_bearing_u_mm': 65,
                                              'bearing_risers_mm': 12.825,
                                              'guide_spacers_mm': 9.825,
                                              'nominal_bridge_inner_Z_mm': 281.35,
                                              'nominal_coupling_Z_mm': [287.7, 307.7],
                                              'nominal_gauge_body_Z_mm': [315.7, 445.7],
                                              'gauge_back_center_Z_mm': 380.7,
                                              'jack_feed_point_Y_mm': -53,
                                              'catch_gap_each_side_mm': 0.75,
                                              'catch_spacer_mm': 7.85,
                                              'minimum_worst_keeper_head_to_bridge_mm': 22.55},
                         'interface_face_by_hub': [{'hub': 'yaw-output-hub',
                                                    'face_u_mm': 0,
                                                    'nearest_end_u_mm': 0,
                                                    'outward_sign': -1},
                                                   {'hub': 'yaw-lever-hub',
                                                    'face_u_mm': 125,
                                                    'nearest_end_u_mm': 175,
                                                    'outward_sign': 1},
                                                   {'hub': 'pitch-lever-hub',
                                                    'face_u_mm': 10,
                                                    'nearest_end_u_mm': 0,
                                                    'outward_sign': -1},
                                                   {'hub': 'pitch-output-hub--1',
                                                    'face_u_mm': 130,
                                                    'nearest_end_u_mm': 130,
                                                    'outward_sign': 1},
                                                   {'hub': 'pitch-output-hub-1',
                                                    'face_u_mm': 0,
                                                    'nearest_end_u_mm': 0,
                                                    'outward_sign': -1},
                                                   {'hub': 'roll-lever-hub',
                                                    'face_u_mm': 51,
                                                    'nearest_end_u_mm': 0,
                                                    'outward_sign': -1},
                                                   {'hub': 'roll-output-hub',
                                                    'face_u_mm': 159,
                                                    'nearest_end_u_mm': 165,
                                                    'outward_sign': 1}],
                         'temporary_hardware': {'M5x80': {'quantity': 4,
                                                          'reuse_from': 'angular-output-cheek-cross-ties'},
                                                'M3x100': {'quantity': 4, 'reuse_from': 'crash-cage-ties'},
                                                'M5x35': {'quantity': 2,
                                                          'reuse_from': 'roll-foot-through-anchor'},
                                                'M6x16_gauge_interface': 1,
                                                'M6x1_coupling': 1,
                                                'M6x25_guides': 2,
                                                'M6x40_bearing_support': 2,
                                                'M8x16_slot8_bearing_foot': 2,
                                                'M8x75_vise_anchors': {'quantity': 2,
                                                                       'reuse_from': 'station-bench-anchors'}},
                         'sequence': ['Before carrying a gun, assemble each real completed shaft, '
                                      'bearings, hubs, actual output plate, end washers and graded capture '
                                      'tubes. Record straightness and witness baseline. Choose the nearer '
                                      'shaft end using the face table and point that end upward. No actual '
                                      'carried gravity load is present.',
                                      'Place the 100x60 interface on the chosen near hub face. Its22 mm '
                                      'aperture clears the keeper. If the actual output plate occupies '
                                      'that face, stack the interface outside it; retain both actual plate '
                                      'and interface with four borrowed M5x80 through the hub. Other '
                                      'internal hubs remain retained; inspect all actual capture paths. Do '
                                      'not grip bare shaft or hub in a vise.',
                                      'Four75 mm metal tubes at60x40 stations join the closed bridge with '
                                      'four borrowed M3x100 ties and their ordinary7 OD washers on the3.4 '
                                      'mm plate holes. Set0.2 mm locating slack. The maximum shaft tail51 '
                                      'mm leaves22.55 mm clearance to the full2 mm keeper,0.8 mm flat and5 '
                                      'mm bolt head. No bridge, tie, washer or sensor contact with shaft, '
                                      'keeper or housing.',
                                      'Secure the real bearing feet to the independently braced500 mm '
                                      'column. Canonical85 mm shaft uses service bearing centeru65 and '
                                      'two12.825 mm metal risers. Its axis is Y=-78.175. Use M6x40 through '
                                      'bearing feet and spare M8x16/slot8 joints through the foot '
                                      'centerline8.5 mm holes; other axes retain their actual service feet '
                                      'and bearing separations.',
                                      'Join the independent catch plates at their farX=-50 stations with '
                                      'two7.85 mm tubes and borrowed M5x35. Vise grips joined far metal '
                                      'only, positively mounted through its actual factory slots with two '
                                      'reused M8x75 anchors. Set0.75 mm nominal gap on both sides of the '
                                      'moving interface, with shaft/keeper clear. Grade actual gap so '
                                      'capture plus elastic movement remains less than the catch gap and '
                                      'the secondary bound remains at most1 mm. Catch must never carry '
                                      'measured proof force.',
                                      'Only after catch and bearing support are secured, loosen inspected '
                                      'hub clamps and bearing setscrews enough to remove friction preload. '
                                      'Verify free, centered movement to the metal capture without '
                                      'binding. The symmetric coaxial bridge, not an eccentric plate push, '
                                      'applies force.',
                                      'Mount the gauge to70x160 slotted backing with the dedicated proof '
                                      'four-screw set, four7 mm rear spacers and two12 OD washers under '
                                      'each M4 head. Verify15.35 mm external grip, actual socket depth, at '
                                      'least4 mm engagement and no bottoming. Two9.825 mm guide '
                                      'tubes/M6x25 joints align the backing; washer clearance permits free '
                                      'axial slide without a bypass.',
                                      'Fit one M6x16 through the6.35 mm closed bridge with one1 mm washer. '
                                      'Bought20 mm M6x1 steel coupling nut positively retains this bolt '
                                      'and joins the received gauge load shaft. Verify thread identity, at '
                                      'least6 mm engagement at each end, end separation, no bottoming, '
                                      'witness and coaxial force. Reference bridge engagement is8.65 mm '
                                      'and gauge engagement7 mm, leaving4.35 mm between ends. Do not use a '
                                      'hook, cord or end-bolt contact.',
                                      'Compression: withdraw the manual jack and advance the unplugged '
                                      'drill quill against only the metal gauge cap, moving the body down '
                                      'toward the bridge. Tension: retract the quill clear and advance the '
                                      'existing fully threaded M6 jack against the backing lower edge, '
                                      'moving the body upward away from the bridge. Hold only the working '
                                      'nut against rotation; wrench supplies no axial support. Feed no '
                                      'more than1/12 turn,0.0833 mm, while observing force. Backing slots '
                                      'retain laterally without clamping; keep casing, keeper and tie '
                                      'tails clear.',
                                      'Tare/check gauge and calculate total force uncertainty. For each '
                                      'actual hub path and both signs, quasi-statically load to an '
                                      'interval wholly450..500 N and hold10 s.475 N nominal with5 N tool '
                                      'uncertainty is only an example; fixture, alignment, calibration and '
                                      'peak effects also enter. Accept no yielding, tap damage, release, '
                                      'rubbing, catch contact or resolved residual/straightness growth, '
                                      'with at most1 mm retained movement. Stop immediately on a fault.',
                                      'Unload, restore the actual service joints, end capture and25 in-lb '
                                      'clamp setting/witnesses. Restore borrowed fixture hardware to its '
                                      'named service joint before assembling a gun. Record both signed '
                                      'results and fresh observed datum. This is axial-retention '
                                      'screening, not a bearing-life or motion-accuracy acceptance.'],
                         'press_relative_height_fit': 'Unplug the press and place the quill at mid-stroke. '
                                                      'The canonical cap is455.7 mm above the column-base '
                                                      'datum; this is not a same-bench fit claim for the '
                                                      'compact press. Positively anchor/bracket the test '
                                                      'column below the press work-surface datum as '
                                                      'required, using existing matched brackets/kit '
                                                      'joints and independently anchored catch. Align the '
                                                      'gauge coupling and allow at least10 mm downward '
                                                      'quill travel onto the metal cap. No loose blocks, '
                                                      'hand support, case contact or loaded-column '
                                                      'repositioning. Manual tension jack operation keeps '
                                                      'quill clear.'},
 'belt_guard_attachment': {'bulkhead_holes_mm': [[-5, 13, 3.4], [5, 13, 3.4]],
                           'guard_holes_local_mm': [[-5, -7, 3.4], [5, -7, 3.4]],
                           'matched_angle_parts': ['guard-thrust-angle-minus', 'guard-thrust-angle-plus'],
                           'transfer_drill': 'Fit each right-side upper angle to its sharedM6 post, then '
                                             'transfer the3.4 mm guard hole from the bulkhead through that '
                                             'foot. Registered local positions areX+/-7,Y9. Deburr before '
                                             'assembling nut/washer.',
                           'M3_to_M6_center_distance_mm': 11.40175425099138,
                           'washer_edge_clearance_mm': 1.90175425099138,
                           'spacer_to_thrust_radial_clearance_mm': 1.92838827718412,
                           'M3x25_grip_mm': 23.525,
                           'thread_protrusion_mm': 1.475,
                           'small_angle_total': 149,
                           'plain_angle_quantity': 137,
                           'guard_angle_quantity_each': 6}}
(OUT/"requirements.json").write_text(json.dumps(r,indent=2)+"\n")
