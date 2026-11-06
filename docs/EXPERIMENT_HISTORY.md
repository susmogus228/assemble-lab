# Experiment history

This is the preserved chronological project log. Earlier sections describe historical states and may be superseded by later experiments. See the root README for the current entry point, installation instructions, and limitations.

# AssembleLab — research prototype

A local Bullet + Three.js feasibility prototype for robot assembly. The current experiment studies one movable 50 mm block placed on a fixed base plate. It is **not yet** the multi-part assembly system shown in the selected concept.

## Run locally (current machine)

Run `start-local.cmd` and open http://127.0.0.1:8810/. This script uses the existing GripLab conda environment on this computer; a clean standalone setup has not yet been verified. The service listens on localhost only. Adjust the Python path in the script if that environment is not present.

The setup must provide Python 3.11, PyBullet, NumPy and pybullet_data. The repository includes its Three.js browser runtime and the Panda collision meshes. See `docs/ASSET_SOURCES.md` for sources and licenses.

## What works

- Bullet simulates a Panda, gripper, movable block and fixed base. There is no robot-to-block attachment constraint.
- A scripted controller grasps, lifts, transfers, releases and retreats. It gets exact object positions from the simulation and uses inverse kinematics; it is not an ML controller.
- A learned ridge-regression model predicts an XY placement correction from simulator source and destination coordinates. It does not use vision or select the next part. A scripted controller carries out the motion.
- The UI replays the real recorded Bullet states. Seed chooses a reproducible source and target; it is not a representation of a physical environment.
- Success requires centre XY error <=12 mm, height error <=8 mm, final speed <10 mm/s and no robot contacts after a 1 second settling period. It does not yet check full assembly structure, orientation or real hardware behavior.

## First experiment

Run `python experiment.py` with the required dependencies. The program generates 20 seeded training scenes, filters demonstrations that did not reach the base (16 usable in the recorded run), then evaluates 10 separately seeded scene positions with the same scenes for both controllers. Results: scripted baseline **0/10**, learned correction **5/10**. The sample is small, uses a single block shape and fixed base, and is not an independent final test or evidence of real-world accuracy. The experiment is an initial feasibility study; the held-out set has been observed during development.

Full recorded parameters, predictions and outcomes: `outputs/residual-experiment.json`. Some placement error remains even with learned correction. Failed grasps, novel parts, multi-step state and perception require further work.

## Verification

`python -m unittest discover -s tests` checks placement decision boundaries. Both controllers have been exercised through the local API and browser replay; see the actual project report for current limitations. Do not use this software to control physical robots.

## Next engineering work

1. Verify multiple sequential placements and stable final assembly after robot release.
2. Build demonstrations with part identities, state and intended next action; split by object family and assembly rather than only position.
3. Train and compare a next-action policy against the scripted recipe on the same held-out assemblies, including failure recovery and unsupported scenarios.
4. Expand and verify the chosen interface against the approved visual reference, including target-versus-actual views and training/evaluation screens.
5. Verify portable installation, additional robot models, physical limits and safety, before considering use outside simulation.

## Two-part physics probe

`python sequence_probe.py` runs a separate, manually tuned scripted case: a robot places two blocks in sequence on a fixed plate and retreats; both positions are checked again after the second release. The historical case passed the former 12 mm positional-only check. It is no longer a valid success under the tighter criteria below. This is a feasibility example, not a general success rate. Select Two-block tower in the browser to replay it. It does not train or evaluate an assembly sequence policy. See `outputs/two-part-probe.json`.

## Collision and grasp audit

`work/collision_audit.py` exercises a cube, cylinder and sphere at three source positions each, plus a deliberately missed control for each shape. The 9 nominal trials all attained bilateral fingertip contact and a recorded centre height above 0.20 m; only 1/9 reached the 12 mm placement criterion. The 3 negative controls had no bilateral contact and no lift. Shapes have the same 50 mm diameter/height, ideal simulated materials and known simulator coordinates. The audit is a small deterministic check, not a collision certification, coverage of object rotations or an accuracy estimate. Results: `outputs/collision-audit.json`.

## Figure accuracy and physical movement

The figure experiment supports a tower and a two-block row. The controller uses exact Bullet poses, hand-tuned offsets and incremental retreat. It is not a camera system or a learned policy. Final acceptance requires each cube to be within 3 mm of its target in XY, within 4 mm vertically, within 3 degrees of yaw (modulo cube symmetry) and tilt, stationary and supported, with no robot contact. The tower also requires relative XY alignment within 3 mm and relative yaw within 3 degrees. Values are experimental tolerances, not hardware specifications.

`work/figure_audit.py` tested two figures at three source offsets without the physical movement option: 0/6 passed. The one central tower trial achieved 2.99 mm relative XY offset but 4.41 degrees relative yaw and did not meet the per-piece placement criteria. This was a development set, including the scene used for tuning, not an independent benchmark.

When enabled, the robot grips the first cube and moves it into the second cube. In the reference case, the first moved about 70 mm, the second about 20 mm, and Bullet reported cube-to-cube contact for 241 simulation steps at 240 Hz. The subsequent assembly attempts both cubes but can fail; the demonstration does not assert that the cubes were assembled successfully. The earlier 0/6 figure audit predates this controller change and is historical.

## Faster experimental placement

Choose `Fast alignment · experimental figure` for a scripted candidate with fewer long correction stages and a near-target correction. The candidate was tuned on seed 0 / source offset (0,0); it succeeded there after the cube collision, with 1.10 mm relative XY error and 0.29° relative yaw. It failed all four other tested source offsets under the same 3 mm / 3° acceptance criteria. This is a development diagnostic, not a statistically reliable result or validation. The baseline remains selectable. The pose feedback uses exact Bullet state.

For the three scenes shared by both controllers, simulated duration was approximately 49.3 s (baseline) versus 38.9 s (candidate), counted from sampled frames; wall-clock timing varied. `outputs/controller-baseline-v2.json` and `outputs/controller-candidate-v3.json` retain individual results. Replay speed is independent of simulated physics and can be set to 1x, 2x or 4x.

## Color-selective sensing prototype

Choose `Color selection · RGB-D + laser`, select red, blue or both, and choose tower or row. A fixed overhead simulated RGB-D camera detects saturated colors from its RGB pixels and projects pixel depth into calibrated world coordinates; a wrist-mounted ray queries the Bullet scene at the candidate. If no camera detection or ray confirmation is available, no grasp is attempted for that item. The image panel displays the actual TinyRenderer frame. This is a rule-based system, not ML.

The robot still uses exact Bullet object poses after grasp for its position corrections and for evaluation, so it is not an entirely sensor-driven controller. Selection supports one instance of each color only, with prescribed order red then blue; lighting, occlusion, realistic camera noise and external images have not been evaluated. Unselected motion above 5 mm fails the trial. The ray confirms height and position near the color observation, but does not independently classify color.

In four development scenes with different selections and two source offsets, every requested color was detected and each wrist ray confirmed a point, but none of the four placements met the strict 3 mm / 3 degree figure criterion. The single-color runs left the unselected object shifted by roughly 0.19–0.22 mm. One additional browser run for blue at offset zero met the criterion; these very small, observed samples do not establish general accuracy. Full sensor cases: `outputs/color-sensor-audit.json`.

## Clutter and estimated grasp offset

The color selection UI can add 0–4 differently colored distractor cubes. The red and blue cubes remain the only selectable objects; extra objects are not same-color or user-positioned, and seed changes their positions by a small deterministic amount. Multiple same-color instances, arbitrary object count and heavy occlusion are not supported. All unselected object displacement is checked against 5 mm.

`Simulator pose` uses the exact held object's simulated pose for placement. `Estimated grasp offset` uses the initial camera/ray observation and robot joint pose, assuming that the grasped object remains fixed relative to the tool. It does not read the held object's actual pose for control after grasp; Bullet ground truth is still used for replay, checks and metrics. Neither mode is a fully vision-based feedback controller.

In a small paired development comparison, both methods found red and blue and confirmed both by laser in three tested scenes with 0, 2 and 4 distractors. Both had 0/3 complete assemblies under 3 mm / 3 degree criteria. In these specific scenes the estimated-offset mode had lower immediate per-placement XY errors than the simulator-pose baseline, but this is not evidence of general superiority. Distractors moved less than 0.5 mm in these trials. See `outputs/clutter-feedback-comparison.json`; values are immediate after placement, before the later part may disturb an earlier one.

## Reinspection, retry and same-color instances

The simulated overhead RGB-D camera reinspects selected objects after release and reports an estimated XY error. Optional retry performs one regrasp and placement if the camera reports an error between 3 mm and 35 mm and a wrist ray confirms a hit. The retry is experimental and is off by default. Per-stage ground-truth diagnostic positions are recorded for analysis only; sensor mode does not read those positions for control.

A paired development comparison across three single-cube cases recorded final XY errors, without vs with retry: 5.69 vs 16.17 mm, 12.49 vs 12.11 mm, and 6.10 vs 13.87 mm. These are observed development cases, not a generalization estimate; the retry worsened two. Camera-derived error and physics-ground-truth error have different values and should not be conflated. See `outputs/verification-retry-comparison.json`.

Enabling the same-color scene with at least one extra cube creates two red cubes. The camera splits disconnected color regions and selects the left or right initial instance using an initial spatial anchor. This is not general identity tracking: occlusion, touching/merged colors, similar objects and later position changes can cause ambiguous detection. In the fully overlapping test scene the robot stops without grasping. If both selected cubes have the same color and one is already placed, reinspection of the second is conservatively marked ambiguous instead of treating another cube as the target.

## Experimental contact-assisted retry

The optional retry method `Simulated fingertip contacts` estimates the held object's center from ideal Bullet contact positions on both fingertips after regrasp; without both contacts it stops the retry. It uses hand-tuned placement offsets and is not a real tactile sensor or a guaranteed improvement. The camera XY error is an estimate, whereas PASS and position error use simulator ground truth.

In five small paired development/diagnostic scenes, final XY errors in mm (no retry / previous retry / contact retry) were: 5.69 / 16.17 / 1.58 (tuning scene); 12.49 / 12.11 / 19.71; 6.10 / 13.87 / 4.98; 16.07 / 17.48 / 6.22; and 7.00 / 11.81 / 26.22. Contact retry reduced XY error in 3/5 and increased it in 2/5 against no retry; only the tuning scene passed all placement criteria. This does not establish generality. Detailed cases: `outputs/contact-retry-evaluation.json`.

## Frozen comparison: bounded push

The no-retry and contact controllers were copied and hashed in `work/frozen-20261105/manifest.json`; three previously observed scenes were development, and four additional scenes were listed before freezing the bounded-push candidate. Per-stage simulated ground-truth diagnostics are in `outputs/phase-diagnostics-20261105.json`; those poses are used for analysis, not control.

The candidate uses a camera estimate and wrist ray to approach the cube, advances until Bullet reports contact with the hit body, then performs one bounded push and observes again. Bullet body identity and contact are idealized simulation information. No teleporting or direct object pose access is used by the correction itself. It is opt-in and experimental.

On four single-cube holdout scenes, final XY errors in mm for no retry / bounded push were 2.20 / 2.77, 6.65 / 5.25, 11.50 / 5.20, and 0.43 / 0.43. The last case did not trigger a correction. Both methods passed the complete 3 mm / 3 degree placement criteria in 2/4 scenes; camera estimation triggered a push in the first despite ground-truth success, and its error rose. These observations are too small to establish reliability. See `outputs/push-development.json` and `outputs/push-holdout.json`. The two-cube assembly task, real-world transfer, and robustness to general occlusion are not established by this experiment.

## Experimental top-surface verification

The optional `Top-depth verification + push` candidate keeps the original camera pipeline for finding the object, but estimates the placed object's center using the nearest-depth pixels in each detected color region. The camera still sees an idealized simulation; side faces, occlusion, lighting, depth quantization and perspective remain potential sources of error. The correction uses the same idealized Bullet ray/body identity and contact as the bounded-push baseline.

In a 9-position isolated camera check, mean XY center error was 2.61 mm for the original and 2.35 mm for top-depth; maximum error was 4.43 mm vs 3.36 mm. Some individual estimates worsened. The final candidate was frozen with its sensor code and 6 previously unobserved single-cube scenes in `work/frozen-top-depth/manifest.json`. Under the 3 mm / 3 degree placement criteria, results were 1/6 for no retry, 1/6 for the previous push and 4/6 for the new verification. One initially successful placement was disturbed by a false correction, and one remained outside tolerance. These are six simulated, single-cube cases, not a real-world or multi-cube reliability estimate. Full records: `outputs/top-depth-holdout.json`. The new method stays optional.

## Experimental tower relative-target controller

The `Base scan before search` mode measures the lower cube with the overhead simulated camera before scanning the next cube. It uses a unique nearby color component as the upper cube's XY target, then checks the completed structure against the original nominal goal; it does not substitute the measured base for the evaluation target. Corrections below 6 mm camera error are skipped because of measurement uncertainty. The camera-derived location and simulator-ground-truth evaluation are distinct. The ray/contact identity remains idealized Bullet information.

An initial candidate inadvertently passed back through the clutter after scanning the upper cube and displaced an unselected cube in 1/6 cases; records are in `outputs/tower-holdout-v1.json`. The order was changed, and a fresh four-case set was frozen in `work/frozen-tower-v2/manifest.json`. On those four color-selected tower scenes (0–4 distractors, including two same-color cubes), the new method reduced relative XY offset in all 4 cases versus the former top-depth controller, but neither method achieved a fully passing tower in any case. The new mode is optional and not validated for real hardware. See `outputs/tower-v2-holdout.json` and `outputs/tower-v2-development.json`.

## Tower retry safety study

Stage-level ground-truth diagnostics showed that a push aimed at a stacked upper cube can also displace the lower cube; in one development case the lower cube moved over 9 mm during the upper correction. Another scene showed lower-cube motion already during the correction descent. The existing method and the experimental `work/color_tower_v4.py` were compared on four scenes frozen before this comparison in `work/frozen-tower-v4/manifest.json`. V4 retains the previous lower-cube correction but does not push the upper cube after stacking. This is not an application default.

The previous method and V4 both produced 0/4 fully passing towers. The lower cube independently passed its nominal-position, angle, support and stability checks in 2/4 and 3/4 cases respectively. Relative XY differences, old/V4 in mm: 2.97/2.97, 12.12/12.14, 4.11/4.11 and 7.93/8.44. Thus protecting the base did not improve relative alignment. The scene set is small, uses idealized simulated RGB-D, ray and contacts, and cannot establish real-world reliability. See `outputs/tower-v4-new-scenes.json` and `outputs/tower-stage-diagnostics.json`.

Two additional development-only experiments, a higher lower-cube retry threshold (`work/color_tower_v3.py`) and a live two-fingertip contact estimate (`work/color_tower_v5.py`), did not show a robust improvement and were not promoted. Results: `outputs/tower-v3-development.json` and `outputs/tower-contact-development.json`. The main limitation is estimating the actual held object pose through grasp and release, including occlusion and slip; the simulated contact estimate itself requires calibration and validation. Research context: Morgan et al., "Vision-driven Compliant Manipulation for Reliable, High-Precision Assembly Tasks" (https://www.roboticsproceedings.org/rss17/p070.pdf) and Yu et al., "Realtime State Estimation with Tactile and Visual Sensing" (https://arxiv.org/abs/1803.08014). Neither demonstrates the performance of this prototype.

## Experimental tracking while holding a cube

A probe of the existing overhead camera on three development scenes found no unique held-cube detection in 66 sampled control observations: the hand occluded the relevant view. The experimental side RGB-D camera `work/held_camera.py` observes a colored visible surface and assumes a 50 mm axis-aligned cube; it subtracts 25 mm along X to estimate the center. Its color/geometry gate rejects missing or multiple nearby candidates, but if tracking fails the candidate falls back to the previous fixed grasp offset. It does not estimate orientation or protect against all mistaken color associations. The camera is simulated, not part of the original app UI. Bullet pose readings in the candidate are recorded only for offline accuracy evaluation, not used to calculate commands.

The candidate `work/color_tower_held_v2.py` was selected before four fresh paired scenes, with exact file hashes and inputs in `work/frozen-held-v2/manifest.json`. Both baseline and candidate achieved 0/4 complete towers; the bottom cube independently passed all checks in 0/4 versus 2/4. Relative XY errors in mm were baseline/candidate: 8.52/13.83, 9.58/20.33, 380.33/6.93 and 6.79/4.43. In the third scene the baseline also displaced an unselected cube by 88.7 mm. All candidate samples produced a gated detection (88/88), but this alone does not prove correct identity; mean held-position XY errors per scene were 2.01, 2.84, 1.75 and 4.34 mm, with individual errors up to 10.29 mm. Results are small-sample simulation evidence, not proof of reliability. Raw outcomes and phase diagnostics: `outputs/held-tracking-new-scenes.json`; initial visibility and tuning probes: `outputs/held-visibility-development.json`, `outputs/held-side-development.json` and `outputs/held-tracking-v2-development.json`.

The tracked version remains an offline experiment and has not replaced the application controller. Continuous localization alone did not make placement reliable: the control update and descent, grasp slip, partial occlusion, mistaken target association and subsequent contact must be addressed and tested together. Neither this experiment nor its idealized sensors validates behavior on a real robot.
## Guarded staged descent experiment

`work/color_tower_guarded_v1.py` is an offline candidate derived from the preceding held-tracking experiment. It bounds each XY update to 2 mm at gain 0.25, descends in six stages and checks a simulated side-camera observation plus both fingertip contact forces at each checkpoint. At least two of three force samples must be bilateral. The contact body identity is an idealization taken from the simulated wrist ray. These checks are sampled between movement stages, not monitored continuously. Missing or ambiguous camera evidence or missing bilateral contact aborts the attempt before release; the simulation is stopped in its present state and this is not an engineered safe stop for a physical robot. Ground-truth pose is logged only for offline evaluation.

In four fresh paired scenes fixed in `work/frozen-guarded-v1/manifest.json`, the previous tracked method and guarded candidate both completed 0/4 towers. Final relative XY error in mm, previous/guarded: 10.44/4.53, 13.87/9.89, 56.66/4.86 and 6.05/9.80. The bottom cube independently passed all placement checks in 1/4 previous versus 0/4 guarded. Unselected cubes moved at most 0.58 mm in this small set. The guarded candidate therefore improved relative alignment in three scenes but did not meet the assembly goal and degraded one previously passing bottom-cube check. It was not promoted to the app.

All 144 checkpoint observations were accepted in these four scenes; this is not a measured detection rate for actual loss of grasp. Unit tests simulate lost contacts and lost camera observations and verify that the controller aborts without releasing. Neither mock tests nor idealized Bullet contact identity establish robustness to sensor noise or real-robot safety. Details: `outputs/guarded-descent-new-scenes.json`, `outputs/guarded-descent-development.json`, `tests/test_hold_guard.py`, and `tests/test_guarded_motion.py`. The diagnostic `command` field in `outputs/hold-phase-diagnostics.json` inadvertently duplicates the observed object position and is not a valid motion command; it must not be used to analyze commands. Background reading: Calandra et al., "More Than a Feeling: Learning to Grasp and Regrasp Using Vision and Touch" (https://ieeexplore.ieee.org/document/8403291/).

## High-resolution base observation experiment

The opt-in `High-resolution camera + guarded motion` mode uses the same staged, contact-gated movement as the guarded candidate, but raises the simulated overhead RGB-D observation resolution from 256x256 to 512x512 for placement verification and lower-cube localization. The user must select two cubes and enable retry to reproduce the paired experiments; the UI fixes sensor feedback and tower layout for this mode. The previous `Base scan before search` remains available. The side camera, grasp/contact assumptions and no-hardware-validation limitations described above still apply.

On 16 isolated development positions and yaw angles without hand occlusion, mean/max XY error was 2.29/4.44 mm at 256 pixels and 1.03/1.70 mm at 512 pixels. Mean snapshot time on this machine was approximately 27 ms and 103 ms respectively; this is not a general performance guarantee. See `outputs/base-camera-resolution-development.json`. A more distant correction approach did not show a consistent improvement on previously observed scenes: `outputs/base-approach-development.json`.

The high-resolution candidate was fixed before four new paired scenes in `work/frozen-base-camera-v1/manifest.json`. Under the same nominal position, relative offset, angle, stability, support and unselected-cube checks, the guarded baseline passed 0/4 full towers and 1/4 bottom-cube checks; the high-resolution candidate passed 1/4 full towers and 4/4 bottom-cube checks. Relative XY errors in mm, baseline/high-resolution: 6.39/13.84, 10.70/11.14, 11.30/1.73 and 3.17/6.50. The upper cube is still unreliable; 4 scenes are not enough to establish general performance. Maximum unselected movement was 0.58 mm in these scenes. Full records: `outputs/base-camera-new-scenes.json`. For the passing example choose seed 719, 4 additional cubes, the experimental mode and retry enabled; it is one observed test case, not a reliability claim.

## Upper-cube grip-force investigation

For the prior four scenes, `outputs/upper-phase-diagnostics.json` records upper-cube movement through grasp, lift, alignment, descent and release. In one failing scene relative XY error had already grown to 21.71 mm by the end of alignment; release changed relative error by about 0.50 mm and retreat by 0.01 mm. These measurements indicate that the main error in that scene developed before release. Motion and contacts are from Bullet and do not establish real-world behavior.

The 8 N upper-finger force limit (`work/color_tower_upper_force_v1.py`) was compared with the existing 50 N limit while retaining the original 50 N lower-piece limit; exact code hashes and four new paired scenes were frozen in `work/frozen-upper-force-v1/manifest.json`. Both methods passed 0/4 complete towers. Relative XY errors in mm for current/8 N were 10.35/10.48, unavailable/unavailable (both stopped after loss of grasp or camera observation during lift), 13.65/8.30 and 4.47/1.33. Thus the change improved alignment in two completed scenes, but the last scene's bottom cube moved from 1.73 mm to 5.00 mm from the nominal target. In the stopped scene the candidate displaced an unselected cube by 5.64 mm, above the 5 mm permitted maximum; the current method displaced it by 4.34 mm. The partial result's `piece_checks` are conservatively false after an aborted two-piece sequence; `base_xy_error_mm` measures XY only and is not a full bottom-piece pass. See `outputs/upper-force-new-scenes.json`.

The 8 N candidate is not exposed in the application because it did not establish an overall improvement and a development case dropped the upper cube after release. A 16 N upper-only candidate also failed all four development scenes, including one stop and one upper cube left at table height. Development results: `outputs/upper-force-development.json`, `outputs/upper-force-v2-development.json`, and `outputs/finger-force-development.json`. A real simulated grasp-loss regression case is checked in `tests/test_actual_grasp_loss.py`. The grasp guard uses idealized Bullet body identity and sampled contact observations; it is not continuous slip detection or a real-robot safety system.

## Coupled-finger grip experiment

The original Panda finger joints were actuated independently. The experimental controller `work/color_tower_coupled_v1.py` links the two Panda finger joints through a Bullet gear constraint, modelling mechanically coordinated fingers. There is no constraint between the object and the hand; the object remains a free dynamic body. The UI offers `Coupled fingers + guarded motion` as an opt-in research mode, with two cubes, sensor feedback and tower layout. It is not the default.

The isolated one-cube experiment uses known initial object locations to isolate physical retention, not camera localization. Abrupt versus smooth transport did not reliably reduce movement (`outputs/single-grasp-development.json`). In six fixed new paired trials, both independent and coupled grips retained the cube and maintained sampled bilateral contact, but maximum displacement relative to the grasp frame from its post-lift position, sampled every eight simulation steps, was 25.82–30.71 mm without finger coupling and 0.60–1.16 mm with coupling. See `outputs/single-grasp-coupling-new.json` and `work/frozen-single-coupling/manifest.json`. This is a small idealized test; relative movement is not a validated tactile slip metric and can include rocking.

On six new paired tower scenes frozen in `work/frozen-tower-coupled-v1/manifest.json`, the previous independent-finger controller passed 1/6 complete towers and the coupled candidate passed 0/6; bottom cubes independently passed 4/6 and 5/6 respectively. Relative offsets in mm (independent/coupled): 17.38/4.61, 2.54/5.30, 5.41/4.28, 11.33/7.68, 5.37/5.08, 8.57/7.28. The candidate improved relative offset in five cases but regressed the sole previously passing tower. The grip improvement therefore does not establish improved assembly success. Full outcomes: `outputs/tower-coupled-new-scenes.json`; development: `outputs/tower-coupled-development.json`. In the UI, seed 727 with one additional red cube and retry enabled is an observed development success, while seed 907 shows a holdout failure; neither represents a reliability estimate. No real hardware or sensor-noise validation has been performed.

## Two-view upper-cube alignment experiment

The opt-in `Two-view alignment + coupled fingers` mode preserves the coupled-finger and lower-cube behavior while estimating the upper 50 mm cube from simulated side views in X and Y. It selects an actually visible color pixel near the component center before reading depth; a component's median pixel can otherwise lie on an occluding gripper and sample background depth. The method assumes the known axis-aligned cube geometry. It rejects ambiguous or disagreeing camera evidence; after a valid two-view observation it can propagate the last estimated tool-relative offset for up to two missing checkpoints. Contact checks use idealized Bullet information. Simulator ground truth is logged only for offline evaluation. On a stop the UI shows the reason and avoids presenting a final XY error for a partial assembly. The previous single-view mode remains selectable.

On six fresh paired scenes frozen in `work/frozen-multiview-v5/manifest.json`, the single-view controller passed 0/6 complete towers; the two-view candidate passed 1/6 and stopped in 2/6 during upper lift because the side-camera observations conflicted despite bilateral contacts. On the four scenes where both methods reached completion, their relative XY offsets in mm were single/two-view: 4.05/2.60, 3.27/2.73, 4.04/2.83 and 4.53/3.05. On the same four scenes mean upper-cube camera XY error averaged 4.18 mm vs 1.31 mm; these are conditional on the two-view controller completing, not a six-scene average. All completed two-view trials used 18 observed samples and no predicted samples. Maximum unselected movement was 0.50 mm. One of the four completed assemblies failed because the bottom cube was outside nominal position tolerance; another missed relative alignment by about 0.05 mm. The small sample and idealized cameras do not establish general or real-robot reliability. Full results: `outputs/multiview-alignment-new-scenes.json`.

To reproduce the passing example in the UI: select color selection, `Two-view alignment + coupled fingers`, retry on, seed 1013 and two additional cubes. Seed 1009 with no extra cubes demonstrates a camera-conflict stop. These are individual scenes, not performance guarantees. Unit tests cover visible-pixel selection, missing/ambiguous views and bounded prediction; they are not a validation of real sensors. Research context: Morgan et al., "Vision-driven Compliant Manipulation for Reliable, High-Precision Assembly Tasks" (https://www.roboticsproceedings.org/rss17/p070.pdf).

## Surface tracking and reobservation experiment

The opt-in `Surface tracking + reobserve` mode estimates the held upper cube's center from simulated colored 3D surface points in two views instead of treating one partially visible point as the center of a face. A 50 mm, nearly axis-aligned cube is assumed. A shape-consistency check requires at least 90% of each selected cloud to fall within the proposed XY footprint with tolerance; this is not proof of correct object identity or complete robustness to noise. There is no constraint between the cube and the arm. Bullet ground truth is logged for offline evaluation only; camera selection and placement do not read it.

If observations conflict immediately after the upper cube is lifted and simulated bilateral grasp is confirmed, the controller may try up to three predefined observation waypoints at height. Robot and held-object contacts with other bodies are checked at every recovery simulation step, and four consecutive samples without both finger contacts stop the recovery. It remeasures after each waypoint and stops if evidence remains ambiguous. This is an idealized simulation-only contact check, not a real robot safety controller; the fallback is not attempted near the target surface or for every possible failure. The original two-view mode remains available.

On six new paired scenes frozen in `work/frozen-surface-v1/manifest.json`, the previous method passed 1/6 full towers and stopped once after conflicting camera estimates; surface tracking passed 2/6 and had no stops. On the five scenes where both completed, relative offsets in mm were previous/surface: 2.05/1.58, 2.61/1.35, 3.29/1.70, 0.50/0.21, 2.81/1.76. Mean upper-camera XY error averaged across those matched scenes was 0.94/0.18 mm; these are conditional estimates on idealized samples, not a six-scene or real-world accuracy guarantee. Maximum unselected movement was 0.50 mm. Full records: `outputs/surface-v1-new-scenes.json`. No new-scene trial invoked an observation waypoint, so recovery effectiveness is not established by that benchmark. A mocked conflict triggered the maneuver, and a mocked unexpected contact stopped it before upper release in `tests/test_surface_recovery_integration.py`.

Three small high-altitude viewpoints alone did not resolve either known 1009 or 1019 conflict (`outputs/reobserve-v2-development.json`). A wider face-geometry point gate resolved them but a constructed wrong observation could pass with 20 mm center error; it is not exposed as the surface method. The surface estimator adds cloud-wide consistency and rejects the constructed inconsistent-cloud example, but can still fail under occlusion, wrong segmentation, similar objects or wrong size/orientation. See `tests/test_held_surface_cloud.py` and `outputs/surface-guarded-development.json`.

To review in the UI, choose `Color selection`, `Surface tracking + reobserve`, enable retry, seed 1223, one additional cube, and `Make first extra cube red`. This is one successful held-out scene, not a performance guarantee. Seed 1201 with zero extra cubes shows an unsuccessful tower. Research context: [Cheng et al., active vision under occlusions](https://proceedings.mlr.press/v87/cheng18a.html); that paper does not validate this controller.
