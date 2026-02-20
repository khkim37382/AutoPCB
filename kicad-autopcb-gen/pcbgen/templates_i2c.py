from __future__ import annotations

from pcbgen.spec import ProjectSpec
from pcbgen.ai_layout import plan_layout

import kicad_sch_api as ksa


def build_i2c_schematic(spec: ProjectSpec, out_path) -> None:
    power = spec.power
    vcc = power.get("vcc_net", "+3V3")

    i2c = spec.raw.get("i2c", {})
    pullups = int(i2c.get("pullups_ohms", 4700))
    add_pullups = bool(i2c.get("add_pullups", True))

    connectors = spec.raw.get("connectors", {})
    hdr_fp = connectors.get(
        "header_footprint",
        "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    )

    use_ai = bool(spec.raw.get("_use_ai", False))
    hint = str(spec.raw.get("_hint", ""))

    plan = plan_layout("i2c_breakout", spec.raw, hint) if use_ai else None
    if plan is None:
        # deterministic fallback
        class _P:
            header_xy = (80, 60)
            caps_origin_xy = (170, 55)
            pullups_origin_xy = (170, 85)
            labels_left_x = 40
            labels_right_x = 230
            row0_y = 55
            row_dy = 12
        plan = _P()

    sch = ksa.create_schematic(spec.name)

    hx, hy = plan.header_xy
    cx, cy = plan.caps_origin_xy
    px, py = plan.pullups_origin_xy
    lx = plan.labels_left_x
    rx = plan.labels_right_x
    row0 = plan.row0_y
    dy = plan.row_dy

    # Header J1 (Conn_01x04)
    sch.components.add(
        "Connector_Generic:Conn_01x04",
        "J1",
        "I2C",
        position=(hx, hy),
        footprint=hdr_fp,
    )

    # Neat net labels on the left
    sch.labels.add(vcc, position=(lx, row0 + 0 * dy))
    sch.labels.add("SDA", position=(lx, row0 + 1 * dy))
    sch.labels.add("SCL", position=(lx, row0 + 2 * dy))
    sch.labels.add("GND", position=(lx, row0 + 3 * dy))

    # Short wires from labels into the page (purely for visual clarity)
    for i in range(4):
        y = row0 + i * dy
        sch.wires.add(start=(lx + 10, y), end=(hx - 10, y))

    # Decoupling caps stacked on the right
    # Put VCC label on left of caps, GND on right, aligned
    for idx, cap in enumerate(spec.decoupling, start=1):
        y = cy + (idx - 1) * dy
        sch.components.add(
            "Device:C",
            f"C{idx}",
            cap.get("value", "100n"),
            position=(cx, y),
            footprint=cap.get("footprint", "Capacitor_SMD:C_0603_1608Metric"),
        )
        sch.labels.add(vcc, position=(cx - 25, y))
        sch.labels.add("GND", position=(cx + 25, y))

    # Optional pullups (two resistors) aligned under caps
    if add_pullups:
        # R1: VCC->SDA, R2: VCC->SCL (symbol orientation isn’t perfect but layout is clean)
        sch.components.add(
            "Device:R",
            "R1",
            f"{pullups}",
            position=(px, py),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )
        sch.labels.add(vcc, position=(px - 25, py))
        sch.labels.add("SDA", position=(px + 25, py))

        sch.components.add(
            "Device:R",
            "R2",
            f"{pullups}",
            position=(px, py + dy),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )
        sch.labels.add(vcc, position=(px - 25, py + dy))
        sch.labels.add("SCL", position=(px + 25, py + dy))

    sch.save(str(out_path))
