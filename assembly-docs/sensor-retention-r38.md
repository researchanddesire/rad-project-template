# R38 shared sensor-joint comb

Use `hardware/cad/joint-retention-r38/sensor-c/RetainedSensorJointsR38.FCStd`
with the unchanged R35F boards and R37 pack-adapter recipe. C supplies a keyed
four-lap comb, a separate return-junction plug, five compliant-pad targets,
an integral hub post/slot and one M1.6 ×4 screw allowance. Battery OPEN;
human-owned product BOM unchanged.

## Proposed assembly stage

1. Complete and inspect the four insulated sensor laps and return junction
   using the R36/R37 fixture recipe. Match their finished sizes to the native
   budgets before fitting retainers. Leave the three outer covers off.
2. Prepare/attach the four lap pad targets to the comb and the return pad to
   the plug. Material, attachment/cure, final thickness and preload must be
   established on coupons. Native pads touch nominal joint envelopes without
   compression; do not assume CAD proves grip or jacket protection.
3. Lower the return pad and separate plug together through the upward service
   column. The plug is installed before the comb; its top will be captured by
   the comb bridge. Ten listed rigid offsets to 16 mm above installed clear
   the current geometry with comb/screw waiting.
4. Slide the comb and four pads in from a +Y offset toward its installed position (−Y),
   aligning the integral tab with its slot and the screw pocket with its post.
   Eight listed offsets to 4 mm outward clear with the return plug in place.
   Sleeve budgets sit between the end stops; wire exits pass through the
   smaller throats. Confirm the actual formed harness and pad fit rather than
   forcing it to the process envelopes.
5. Fit the candidate screw after checking the actual screw/head profile,
   clearance, hub material, Ø1.25 mm pilot and torque on coupons. The model
   provides a Ø3.2 ×1.6 mm head allowance, not a selected supplier fastener.
   The locating tab provides the rotation stop. A generic Ø1.4 tip/Ø3 shaft
   has five clear listed approaches; match the real driver and handle.
6. Inspect joint separation, insulation, attachment and wire exits. Establish
   pull/slip, vibration, creep and service acceptance before relying on this
   support. The hard-blocker samples demonstrate nominal enclosure only.

The source hub's named capture/end-seat/lid-post regions retain their
material. The local comb pocket/post/key-slot still require material/load
review. These steps address this sensor-retention stage; they do not complete
body/hub loading, power mate/lap restraint or the outer cover/seal sequence.
The motor keeps its separate shell clamp.

The cable topology/starting lengths and child BOM remain those of
`hardware/cables/pack-adapter-r37/`; no cable source or human BOM edit follows
from this retention study. No live battery connection or physical test has
occurred.
