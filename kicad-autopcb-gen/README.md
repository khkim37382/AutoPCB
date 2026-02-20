# kicad-autopcb-gen (KiCad 9)

Generates a KiCad project folder from a YAML spec:
- Creates .kicad_pro + .kicad_sch (with decoupling/pullups template) + starter .kicad_pcb
- Supports 3 board types:
  - i2c_breakout
  - esp32_devboard (header-based placeholder)
  - buck_module

## Why one manual step?
KiCad’s normal workflow is to sync schematic->pcb using "Update PCB from Schematic".
There isn't a stable headless CLI equivalent in KiCad 9 yet, so you do that once in the GUI.

## Quickstart
pip install -e .
pcbgen --spec examples/i2c_breakout.yaml --out out/MyI2CBoard

Open out/MyI2CBoard/MyI2CBoard.kicad_pro in KiCad 9.
Then PCB Editor → Tools → Update PCB from Schematic.

## Startup direction (where to take it next)
- Add an IPC/AI mode:
  - KiCad 9 IPC API exists but requires a running KiCad GUI and is PCB-editor focused right now.
- Add placement automation:
  - After footprints are imported, a PCB action plugin (or IPC client) can place footprints by rules.
- Add real part selection:
  - Swap "generic connectors" for real symbols via library search + constraints.
