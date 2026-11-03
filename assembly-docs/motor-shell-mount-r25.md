# Independent motor module R25

Development assembly target. This replaces the rejected shared motor/PCB
keeper. Follow the named candidate and its developer evidence before using
these steps; this is not a complete build release.

## Separate assemblies

The electronics carrier retains the body PCB and battery space. Its old motor
saddles and bridge are removed. The independent metal motor module seats on
the body rim, keys against rotation and is captured by a shoulder inside the
nose cap. The motor clamp uses one M2 screw and one nut budget. Flexible leads
join the assemblies; no motor-retention load goes through the PCB keeper.

The flange of the motor mount is 1.10 mm thick nominally. This places the cap
0.10 mm forward of its earlier position when the internal seat contacts the
mount. The offset is integral to the part; no extra shim washer is required
at nominal dimensions. The cap's inherited 0.75 mm thread advances by 48°
for this offset. The body and motor module remain stationary as it closes.

## Target sequence

1. Inspect the actual motor capsule, leads/flare, clamp, nut, screw and seating
   faces. Establish the clamp's travel with a measured dummy capsule first.
   Confirm the motor variant against the supplier drawing; the inferred lead
   flare in CAD is not a controlled radial maximum.
2. On the bench, slide the motor forward into the clamp from its rear opening
   until it reaches the front locating stop. Keep the two leads behind it.
   Fit the nut in the relieved pocket and tighten from above. Establish a
   non-damaging clamp setting by measurement; no generic M2 tightening torque
   is approved for this thin split sleeve and encapsulated motor.
3. Separately load the body PCB and pack arrangement into the electronics
   carrier, install the nominal plugs, then lower its PCB-only keeper. Retain
   it with the original two screw budgets. Pack/NTC retention and actual
   supported wires are still being designed; an allowance box is not a pack.
4. Front-load the electronics cartridge into the metal body. Then insert the
   motor module from the front, aligning its rounded internal key. Seat the
   annular flange on the body rim. Actual motor leads and strain relief must
   be dressed before this step can become a complete build instruction.
5. Fit the stationary tip support/sensor and its four-wire route once that
   revised design is available. The current tip envelopes alone do not
   provide support or the thermal interface.
6. Close the cap around the stationary module. Confirm both seating annuli
   contact and the earlier external shoulder does not bottom first. Do not
   infer clamp preload from closure torque alone. A suitable thread/locking
   and sealing process remains to be selected.

The listed digital positions cover only rigid nominal shapes. Real wiring,
gripping, tolerances, screw drive, seals, force and physical assembly still
need their own checks. Fit the local flange controls and flexible connection
only after those revised interfaces are defined.

## Disabled fit and attended bench checks

Check annular contact and cap-stop priority after finishing the actual parts.
Confirm clearance between the motor mount, electronics support and pack.
The proposed functional seating dimensions and stack are recorded in
`hardware/design/motor-shell-mount-r25/critical-interfaces-proposal.json`.
Supplier feedback may require changing these limits.

Use the provisional disabled 2 N axial pull screen in both directions to
look for motor slip or damage. This is a bench-screen target, not a product
load rating. Establish free-motor current/vibration first, then compare under
the same drive after mounting. Investigate binding, current change, abnormal
noise, heating or loosening before continuing the agreed PWM/duty-cycle test.
Measure housing and electronics-support acceleration to assess vibration
transfer; the CAD load path does not prove transmission efficiency.

Battery selection remains OPEN. The human-owned BOM is unchanged. No
electrical operation, endurance, physical fit or wear result is claimed.
