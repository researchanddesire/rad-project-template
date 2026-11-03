# Validation

Current work is a two-piece CNC metal / flange-joint study, not a build release.
The old P1 scaffold fit-kit recommendation remains withdrawn.

## Evidence and limits

| Area | Evidence / remaining work |
| --- | --- |
| Geometry | Four valid native solids, STEP readbacks and closed plastic STLs. Current `review.json` records hashes and assembly overlap checks. |
| Machining | Turned body features and accessible cap bores proposed; one offset sensor drill. CAD thread envelopes require a machining callout and supplier review. |
| Rear joint | Shoulder/spigot/ring, bond space and boot cuff section modeled. Catalog nominal dimensions do not prove ring expansion, tool access, strength, creep or sealing. |
| Motion | Finite rigid-module loading/rotation samples and a simplified ring-tool envelope are screens only. No full thread, elastic ring, flexible loom or hands/tool trial. |
| Tray/cover | Open drafted geometry and flat print poses; no slicer/physical print or molding approval. |
| Electronics | R35F/bench work is historical. New NTC circuit/code and PCB tabs are not implemented. |
| Product | No fabrication, powered test, finished-material, leak, cleaning or wear result. |

## Next checks

1. Machinist review: stock/workholding, straight bore, sensor drill/web/remaining
   wall, thread engagement/runouts, gland corners and polish allowances.
2. Select actual ring/material/finish, apply catalog tolerances and groove edge
   limits. Establish axial/bending/torsion loads, then test root-pad bearing,
   ring retention and wet/aged socket bond. Do not use catalog thrust as the
   finished assembly rating.
3. Finish boot/cuff bond, rear service closure and contact/button seals. Check
   worst-case O-ring squeeze/fill and cap closing process; test cleaning/leaks.
4. Measure motor case/fit/press force and sensor response with motor off/on.
   Check the new metal volume/selected material weight before wear studies.
5. Revise NTC circuit/code, PCB tabs, loom and charging mate; repeat applicable
   ERC/DRC and bench fault checks before ordering or energizing.
6. Slice and perform a complete unpowered assembly/service trial with the actual
   ring, pliers, foam, wiring and pack before functional/endurance testing.

Build the developer site with `mkdocs build --strict -f developer-docs/mkdocs.yml`.
CAD, battery endurance and physical wear acceptance remain separate evidence.
