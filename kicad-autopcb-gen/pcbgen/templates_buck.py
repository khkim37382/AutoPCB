from __future__ import annotations

from pcbgen.spec import ProjectSpec
import kicad_sch_api as ksa


def build_buck_schematic(spec: ProjectSpec, out_path) -> None:
    p = spec.power
    vin = p.get("vin_net", "VIN")
    vout = p.get("vout_net", "+5V")
    gnd = p.get("gnd_net", "GND")

    stage = spec.raw.get("stage", {})
    sch = ksa.create_schematic(spec.name)

    # Generic “controller” block as connector so it works with stock libs
    u1 = sch.components.add(
        "Connector_Generic:Conn_01x05",
        "U1",
        "BUCK_CTRL",
        position=(60, 60),
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
    )

    # Power stage passives (template)
    cin = stage.get("in_cap", {"value": "22u"})
    cout = stage.get("out_cap", {"value": "47u"})
    rtop = stage.get("feedback_rtop", {"value": "100k"})
    rbot = stage.get("feedback_rbot", {"value": "20k"})

    sch.components.add("Device:C", "CIN", cin.get("value", "22u"), position=(100, 55),
                       footprint=cin.get("footprint", "Capacitor_SMD:C_1210_3225Metric"))
    sch.components.add("Device:C", "COUT", cout.get("value", "47u"), position=(100, 75),
                       footprint=cout.get("footprint", "Capacitor_SMD:C_1210_3225Metric"))

    sch.components.add("Device:R", "RFB1", rtop.get("value", "100k"), position=(130, 65),
                       footprint=rtop.get("footprint", "Resistor_SMD:R_0603_1608Metric"))
    sch.components.add("Device:R", "RFB2", rbot.get("value", "20k"), position=(130, 75),
                       footprint=rbot.get("footprint", "Resistor_SMD:R_0603_1608Metric"))

    # Nets
    sch.labels.add(vin, position=(40, 55))
    sch.labels.add(vout, position=(160, 75))
    sch.labels.add(gnd, position=(40, 80))

    sch.save(str(out_path))
