# P1 simple assembly and dry-fit kit

> Superseded as the recommended build by hardware/cad/manufacturing-layout/. This preserves the earlier scaffold and its scoped checks.

Open **[PrototypeP1.FCStd](PrototypeP1.FCStd)** for the current product assembly.
For the first physical trial, use **[P1-Dry-Fit-Kit.zip](P1-Dry-Fit-Kit.zip)**
and its [worksheet](dry-fit-kit/README.md). The kit contains native fit CAD,
26 closed STL files (27 pieces), removable populated-board/plug gauges,
quantities/checksums and finite loading evidence. It is an unpowered bench kit.

## Selected assembly

One-piece front-loading metal body, 15 mm neck, independent shell-mounted
motor and separate body/flange boards. Battery choice stays open. R38 sensor
combs/return plugs and R39 connector cages are not adopted. Insulate joints
individually and hand-dress accessible wiring; small removable silicone tacks
on jackets/housing are a proposed process. Keep the pack and release free.

The one-piece cover includes contact seats and blind magnet pockets. Contact
axes are X-32 at Z8/GND and Z12/DOCK_5V; old R2/R3 external mates do not match.
Use the candidate in `charging-cable/`. Actual contact fit, bond, holding and
sealing remain unqualified.

Charging wires and revised pack dressing are integrated: connector centre
Y-17.0/Z-12.8, unchanged body-wire/joint ends, 2.0 mm first dock-wire bends and
about 0.51 mm nominal pack-mate clearance. See `charging-wire-review.json`
and `pack-routing-review.json`. Actual exits, wire sizes, permitted bends,
trimming, insulation and closure remain receiving/trial conditions.

## What is editable

P1 retains copied source solids with placements and provenance; detailed part
history remains in [R37F](../pack-assembly-r37/power-f/ConditionalPackPowerR37.FCStd)
and its source studies. The cover has native primitive/Boolean history;
new motor, charging and pack leads have native sweep/path features. Old
cover/pack-wire roles remain hidden in Construction. Boards, metal parts,
hubs and existing joints are unchanged.

## Parts and print package

`exchange/` contains ten separately checked STEP parts. `dry-fit-kit/` is the
current printable package; use it instead of the older loose `fit-mockup/`
files. The hub STL was globally remeshed to remove open tessellation seams,
with source bounds/volume checked. Native part geometry did not change.

Import in millimetres at 100%. Review supports/orientation in the slicer and
trial threads/pilot holes without force. No actual slice or print is claimed.
Printed gauges do not establish actual connector operation, switch travel,
motor coupling, final materials, sealing or wear fit.

## Reproduce and inspect

Use `tools/prepare_simple_prototype.py` with FreeCAD's Python to rebuild P1.
`tools/simple_charging_wires_p1.py` can apply the current pack/dock routing to
an earlier P1 copy without rebuilding unchanged part exports; arguments are
source and destination assembly folders.

`tools/build_dry_fit_kit_p1.py` takes the current assembly folder, matching-cable
folder and kit output folder. `tools/check_dry_fit_loading_p1.py` takes the
kit folder. `tools/render_dry_fit_kit_p1.py` reads its temporary view meshes.
The native/mesh checks and their limits are recorded in `review.json` and the
kit manifest/loading report.

The prior P1 role geometries pass saved-shape preservation checks. New wire
roles pass nominal installed checks; three finite rigid loading studies and
four equal-length cover-wire poses pass. These are scoped digital checks.
The complete connected assembly/service trial, actual lead/connector fit,
external cable assembly and seal details remain to demonstrate physically.
The displayed 33 ×8 ×20 mm pack is a size reference, not a battery selection.
