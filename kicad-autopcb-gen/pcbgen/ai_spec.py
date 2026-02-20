from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


# Keep schema around for your own sanity (we won’t send it anywhere now)
SPEC_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string", "enum": ["i2c_breakout", "esp32_devboard", "buck_module"]},
        "power": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "vcc_net": {"type": "string"},
                "vin_net": {"type": "string"},
                "vout_net": {"type": "string"},
                "gnd_net": {"type": "string"},
            },
            "required": ["vcc_net", "vin_net", "vout_net", "gnd_net"],
        },
        "i2c": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "header_pins": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 6},
                "pullups_ohms": {"type": "integer"},
                "add_pullups": {"type": "boolean"},
            },
            "required": ["header_pins", "pullups_ohms", "add_pullups"],
        },
        "decoupling": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"value": {"type": "string"}, "footprint": {"type": "string"}},
                "required": ["value", "footprint"],
            },
        },
        "connectors": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"header_footprint": {"type": "string"}},
            "required": ["header_footprint"],
        },
        "headers": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "left": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"pins": {"type": "integer"}, "footprint": {"type": "string"}},
                    "required": ["pins", "footprint"],
                },
                "right": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"pins": {"type": "integer"}, "footprint": {"type": "string"}},
                    "required": ["pins", "footprint"],
                },
            },
            "required": ["left", "right"],
        },
        "stage": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "in_cap": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"value": {"type": "string"}, "footprint": {"type": "string"}},
                    "required": ["value", "footprint"],
                },
                "out_cap": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"value": {"type": "string"}, "footprint": {"type": "string"}},
                    "required": ["value", "footprint"],
                },
                "feedback_rtop": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"value": {"type": "string"}, "footprint": {"type": "string"}},
                    "required": ["value", "footprint"],
                },
                "feedback_rbot": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"value": {"type": "string"}, "footprint": {"type": "string"}},
                    "required": ["value", "footprint"],
                },
            },
            "required": ["in_cap", "out_cap", "feedback_rtop", "feedback_rbot"],
        },
    },
    "required": ["name", "type", "power", "i2c", "decoupling", "connectors", "headers", "stage"],
}


def _slug_name(text: str) -> str:
    t = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip())
    t = re.sub(r"_+", "_", t).strip("_")
    return (t[:32] if t else "GeneratedBoard")


def _find_voltage(text: str) -> str:
    # Look for 3.3V / 5V etc.
    m = re.search(r"\b(1\.8|2\.5|3\.0|3\.3|5|12)\s*v\b", text)
    if m:
        v = m.group(1)
        if v == "5":
            return "+5V"
        if v == "12":
            return "+12V"
        if v == "3.3":
            return "+3V3"
        if v == "3.0":
            return "+3V0"
        if v == "2.5":
            return "+2V5"
        if v == "1.8":
            return "+1V8"
    return "+3V3"


def _parse_pullup_ohms(text: str) -> Tuple[bool, int]:
    # Detect pullups and value like 4.7k / 10k / 4700
    if "pullup" not in text and "pull-up" not in text:
        return (False, 4700)

    m = re.search(r"\b(\d+(\.\d+)?)\s*(k|kohm|kΩ)\b", text)
    if m:
        val = float(m.group(1))
        return (True, int(round(val * 1000)))

    m2 = re.search(r"\b(\d{3,6})\s*(ohm|Ω)?\b", text)
    if m2:
        ohms = int(m2.group(1))
        # sanity bounds for pullups
        if 200 <= ohms <= 200000:
            return (True, ohms)

    return (True, 4700)


def _cap_footprint_for(value: str) -> str:
    # very rough mapping; you can improve later
    v = value.lower().replace(" ", "")
    if "1210" in v:
        return "Capacitor_SMD:C_1210_3225Metric"
    if "0805" in v:
        return "Capacitor_SMD:C_0805_2012Metric"
    # larger caps usually 0805/1206; but default 0603 is fine for decoupling
    if v.endswith("u") and any(v.startswith(x) for x in ["10", "22", "47", "100"]):
        return "Capacitor_SMD:C_0805_2012Metric"
    return "Capacitor_SMD:C_0603_1608Metric"


def _parse_decoupling(text: str) -> List[str]:
    # look for "100n + 1u", "100n and 10u", etc.
    # return list of strings like ["100n","1u"]
    vals: List[str] = []

    # common pattern: 100n + 1u
    m = re.findall(r"\b(\d+(\.\d+)?)\s*(n|u)\b", text)
    for g in m:
        num = g[0]
        unit = g[2]
        vals.append(f"{num}{unit}")

    # If user didn't specify any, choose sane defaults
    if not vals:
        return ["100n", "1u"]

    # Keep only reasonable decoupling-like caps
    filtered: List[str] = []
    for v in vals:
        if v.endswith("n"):
            filtered.append(v)
        elif v.endswith("u"):
            filtered.append(v)
    # de-dup preserving order
    out: List[str] = []
    for v in filtered:
        if v not in out:
            out.append(v)

    # ensure at least 100n exists
    if not any(v.endswith("n") for v in out):
        out.insert(0, "100n")

    return out[:4]


def _choose_board_type(text: str) -> str:
    t = text.lower()
    if "buck" in t or "converter" in t or "regulator" in t:
        return "buck_module"
    if "esp32" in t or "devboard" in t or "dev board" in t:
        return "esp32_devboard"
    if "i2c" in t or "sda" in t or "scl" in t or "imu" in t or "sensor" in t:
        return "i2c_breakout"
    # default
    return "i2c_breakout"


def _parse_header_pins(text: str, board_type: str) -> int:
    t = text.lower()
    # Try "4-pin", "6 pin", etc.
    m = re.search(r"\b(\d+)\s*-\s*pin\b|\b(\d+)\s*pin\b", t)
    if m:
        n = int(m.group(1) or m.group(2))
        if 2 <= n <= 20:
            return n

    # For I2C, default 4 pins
    if board_type == "i2c_breakout":
        return 4
    return 15


def _make_base_spec(name: str, board_type: str, vcc_net: str) -> Dict[str, Any]:
    # Because schema is strict, we must fill everything even if unused.
    base: Dict[str, Any] = {
        "name": name,
        "type": board_type,
        "power": {"vcc_net": vcc_net, "vin_net": "VIN", "vout_net": vcc_net, "gnd_net": "GND"},
        "i2c": {"header_pins": ["VCC", "GND", "SDA", "SCL"], "pullups_ohms": 4700, "add_pullups": False},
        "decoupling": [
            {"value": "100n", "footprint": "Capacitor_SMD:C_0603_1608Metric"},
            {"value": "1u", "footprint": "Capacitor_SMD:C_0603_1608Metric"},
        ],
        "connectors": {"header_footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"},
        "headers": {
            "left": {"pins": 0, "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical"},
            "right": {"pins": 0, "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical"},
        },
        "stage": {
            "in_cap": {"value": "22u", "footprint": "Capacitor_SMD:C_1210_3225Metric"},
            "out_cap": {"value": "47u", "footprint": "Capacitor_SMD:C_1210_3225Metric"},
            "feedback_rtop": {"value": "100k", "footprint": "Resistor_SMD:R_0603_1608Metric"},
            "feedback_rbot": {"value": "20k", "footprint": "Resistor_SMD:R_0603_1608Metric"},
        },
    }
    return base


def spec_from_prompt(prompt: str) -> Dict[str, Any]:
    """
    OFFLINE: Convert natural language prompt -> spec dict for generator.
    Deterministic keyword/regex parser.
    """
    text = prompt.strip()
    tl = text.lower()

    board_type = _choose_board_type(text)
    vcc_net = _find_voltage(tl)
    name = _slug_name(text)

    spec = _make_base_spec(name=name, board_type=board_type, vcc_net=vcc_net)

    # Decoupling caps
    cap_vals = _parse_decoupling(tl)
    spec["decoupling"] = [{"value": v, "footprint": _cap_footprint_for(v)} for v in cap_vals]

    # I2C breakout specifics
    if board_type == "i2c_breakout":
        hpins = _parse_header_pins(tl, board_type)
        # If user asked for 6-pin, we’ll add extra pins after SCL
        if hpins == 4:
            header_pins = ["VCC", "GND", "SDA", "SCL"]
        elif hpins == 5:
            header_pins = ["VCC", "GND", "SDA", "SCL", "INT"]
        else:
            header_pins = ["VCC", "GND", "SDA", "SCL", "INT", "ADDR"][:hpins]

        add_pullups, pull_ohms = _parse_pullup_ohms(tl)
        spec["i2c"] = {
            "header_pins": header_pins,
            "pullups_ohms": int(pull_ohms),
            "add_pullups": bool(add_pullups),
        }

        # Header footprint matches pin count
        if hpins == 4:
            fp = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
        elif hpins == 5:
            fp = "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical"
        elif hpins == 6:
            fp = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"
        else:
            fp = "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"
        spec["connectors"]["header_footprint"] = fp

    # ESP32 devboard specifics
    if board_type == "esp32_devboard":
        # Try to detect header length like "1x19" or "1x15"
        m = re.search(r"\b1x(\d{1,2})\b", tl)
        pins = int(m.group(1)) if m else 15
        if pins < 6:
            pins = 15
        fp = f"Connector_PinHeader_2.54mm:PinHeader_1x{pins}_P2.54mm_Vertical"
        spec["headers"] = {
            "left": {"pins": pins, "footprint": fp},
            "right": {"pins": pins, "footprint": fp},
        }
        # often no I2C pullups on generic devboard
        spec["i2c"]["add_pullups"] = False

    # Buck module specifics
    if board_type == "buck_module":
        # Detect output voltage, default +5V
        vout = "+5V"
        if "3.3" in tl:
            vout = "+3V3"
        if "12" in tl:
            vout = "+12V"
        spec["power"]["vin_net"] = "VIN"
        spec["power"]["vout_net"] = vout
        spec["power"]["vcc_net"] = vout  # unused but schema requires
        spec["power"]["gnd_net"] = "GND"

        # Try to detect in/out caps like "22u in, 47u out"
        cin = re.search(r"\b(\d+(\.\d+)?)\s*u\b.*\bin\b", tl)
        cout = re.search(r"\b(\d+(\.\d+)?)\s*u\b.*\bout\b", tl)
        if cin:
            spec["stage"]["in_cap"]["value"] = f"{cin.group(1)}u"
            spec["stage"]["in_cap"]["footprint"] = _cap_footprint_for(spec["stage"]["in_cap"]["value"])
        if cout:
            spec["stage"]["out_cap"]["value"] = f"{cout.group(1)}u"
            spec["stage"]["out_cap"]["footprint"] = _cap_footprint_for(spec["stage"]["out_cap"]["value"])

    return spec
