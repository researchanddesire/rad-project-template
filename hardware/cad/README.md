# CAD

Start with **[Manufacturing layout](manufacturing-layout/README.md)** and
`ManufacturingLayout.FCStd`. It replaces the earlier scaffold with four main
mechanical pieces: two CNC-turned metal parts and two open plastic case parts.
The cap seats the motor on metal beside a potted NTC.

The 15 mm neck remains. The body PCB uses insulation/foam support in the cap;
the open flange tray and rear cover integrate the other support features.
The rear uses a turned shoulder/spigot, standard ring, socket bond and boot cuff;
cover screws close plastic only. Read [the DFM review](manufacturing-layout/DFM.md).
The source includes four STEP parts and two flat-oriented plastic study STLs.
It is a DFM architecture study, not a build or tooling release.

Earlier P1 kits and revision folders are retained as superseded evidence.
Their closed meshes and loading samples did not establish manufacturability.
Use the current developer proposal for outstanding circuit, PCB, loom, thread,
boot/seal, supplier and physical checks. Battery choice stays open.
