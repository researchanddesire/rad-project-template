# Assembly direction

Use the current two-piece CNC metal study in `hardware/cad/manufacturing-layout/`.
Its `README.md` and `DFM.md` control the proposal and remaining manufacturing
questions. This is **not a released build**; the old P1 kit remains superseded.

## Parts and joints

- Turned body with15 mm neck, rear shoulder/spigot and retaining-ring groove.
- Turned nose cap with motor pocket/metal stop and one offset NTC drill.
- Open flange tray with root pad, board seats and pack ribs.
- Rear cover with two proposed M2×6 screws into plastic, independent of body retention.

A standard retaining ring captures the body axially; socket bond resists twisting.
The silicone cuff bonds to the recessed metal land and meets its upper shoulder
flush. Boot, O-ring, insulation/foam, adhesives and hardware are additional items.

## Proposed order after electrical/manufacturing review

1. Stage the boot over the rear root onto the neck before fitting the tray.
   Qualify cuff stretch over the Ø24 shoulder; protect bonding surfaces.
2. Fixture/bond the Ø18 spigot into the tray's finished socket. Install/inspect
   the ring through the open rear, lugs toward the empty battery wing. This
   happens before boards/pack. Cure the factory joint before cap closing torque.
3. Pot/cure the offset NTC; leads exit beside the motor. Seat the motor on metal
   after actual case/bore/edge-fit and force checks. Potting and PCB carry no press load.
4. Prewire the cap, motor/NTC and insulated body PCB, with foam pads extending
   into the cap counterbore. Feed disconnected flange tails through the body;
   turn the whole module, seat its face O-ring/shoulders and connect tails last.
   Threadlocker is a separate qualified process, not the cavity seal.
5. Fit flange PCB and selected pack, dress/inspect the loom, then close the
   plastic cover. Fit/bond the boot cuff after inspection. Its rear service
   closure and contact/button seals must be designed before a sealed build.

## Holds

M30×1.5 fit/gaging, six mm effective male engagement, reliefs, gland tolerances,
actual motor fit, ring/plier access, bond aging, plastic bearing/creep, full boot
and reverse service require review/trials. Approximate ring/motion CAD is not
physical assembly proof. Current metal volume is32.8 cm³; material/weight remain open.

R35F/firmware still use TMP117/I²C. NTC analogue input/code, PCB tabs, loom and
charger mate need integration before ordering/power. The BOM stays human-owned.
No actual machining, print, assembly, leak, cleaning or wear result exists.
