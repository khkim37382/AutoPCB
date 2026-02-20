from __future__ import annotations

from pathlib import Path
import json

from pcbgen.spec import ProjectSpec
from pcbgen.templates_i2c import build_i2c_schematic
from pcbgen.templates_esp32dev import build_esp32dev_schematic
from pcbgen.templates_buck import build_buck_schematic


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _kicad_pro_minimal(project_name: str) -> str:
    # Minimal .kicad_pro that KiCad 9 will accept in most installs.
    # If your KiCad complains, fallback is:
    # 1) Create a new empty project in KiCad GUI
    # 2) Replace the .kicad_sch/.kicad_pcb with generated ones
    return json.dumps(
        {
            "meta": {"filename": f"{project_name}.kicad_pro", "version": 1},
            "project": {"title": project_name},
            "cvpcb": {},
            "pcbnew": {},
            "schematic": {},
        },
        indent=2,
    )


def _sym_lib_table_default() -> str:
    # Use global libs; keep project table minimal.
    return '(sym_lib_table\n)\n'


def _fp_lib_table_default() -> str:
    return '(fp_lib_table\n)\n'


def _starter_pcb(project_name: str) -> str:
    return """(kicad_pcb (version 20231120) (generator "pcbgen")
  (general (thickness 1.6))
  (paper "A4")
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user)
    (44 "Edge.Cuts" user)
    (46 "B.CrtYd" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (usegerberattributes true)
      (usegerberadvancedattributes true)
      (creategerberjobfile true)
      (outputdirectory "")
    )
  )
  (gr_rect (start 0 0) (end 60 40)
    (stroke (width 0.15) (type solid))
    (fill none)
    (layer "Edge.Cuts")
  )
)
"""



def generate_project(spec: ProjectSpec, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    name = spec.name
    _write_text(out_dir / f"{name}.kicad_pro", _kicad_pro_minimal(name))
    _write_text(out_dir / "sym-lib-table", _sym_lib_table_default())
    _write_text(out_dir / "fp-lib-table", _fp_lib_table_default())
    _write_text(out_dir / f"{name}.kicad_pcb", _starter_pcb(name))

    if spec.type == "i2c_breakout":
        build_i2c_schematic(spec, out_dir / f"{name}.kicad_sch")
    elif spec.type == "esp32_devboard":
        build_esp32dev_schematic(spec, out_dir / f"{name}.kicad_sch")
    elif spec.type == "buck_module":
        build_buck_schematic(spec, out_dir / f"{name}.kicad_sch")
    else:
        raise ValueError(f"Unknown board type: {spec.type}")
