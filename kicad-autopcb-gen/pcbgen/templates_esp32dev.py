from __future__ import annotations

from pcbgen.spec import ProjectSpec
import kicad_sch_api as ksa


def build_esp32dev_schematic(spec: ProjectSpec, out_path) -> None:
    vcc = spec.power.get("vcc_net", "+3V3")

    headers = spec.raw.get("headers", {})
    left = headers.get("left", {})
    right = headers.get("right", {})

    left_pins = int(left.get("pins", 15))
    right_pins = int(right.get("pins", 15))
    left_fp = left.get("footprint", "Connector_PinHeader_2.54mm:PinHeader_1x15_P2.54mm_Vertical")
    right_fp = right.get("footprint", "Connector_PinHeader_2.54mm:PinHeader_1x15_P2.54mm_Vertical")

    sch = ksa.create_schematic(spec.name)

    # “Devboard” is modeled as two headers + a 3V3 rail w/ decoupling.
    jl = sch.components.add(
        f"Connector_Generic:Conn_01x{left_pins}",
        "J1",
        "LEFT_HDR",
        position=(60, 60),
        footprint=left_fp,
    )
    jr = sch.components.add(
        f"Connector_Generic:Conn_01x{right_pins}",
        "J2",
        "RIGHT_HDR",
        position=(140, 60),
        footprint=right_fp,
    )

    # Power labels
    sch.labels.add(vcc, position=(90, 45))
    sch.labels.add("GND", position=(90, 50))

    # Decoupling near the “module”
    for idx, cap in enumerate(spec.decoupling, start=1):
        sch.components.add(
            "Device:C",
            f"C{idx}",
            cap.get("value", "100n"),
            position=(90, 60 + 7 * (idx - 1)),
            footprint=cap.get("footprint", "Capacitor_SMD:C_0603_1608Metric"),
        )
        sch.labels.add(vcc, position=(80, 60 + 7 * (idx - 1)))
        sch.labels.add("GND", position=(100, 60 + 7 * (idx - 1)))

    sch.save(str(out_path))
