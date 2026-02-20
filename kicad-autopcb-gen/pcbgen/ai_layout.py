from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from openai import OpenAI


@dataclass
class LayoutPlan:
    header_xy: tuple[int, int]
    caps_origin_xy: tuple[int, int]
    pullups_origin_xy: tuple[int, int]
    labels_left_x: int
    labels_right_x: int
    row0_y: int
    row_dy: int


def _default_plan() -> LayoutPlan:
    return LayoutPlan(
        header_xy=(80, 60),
        caps_origin_xy=(170, 55),
        pullups_origin_xy=(170, 85),
        labels_left_x=40,
        labels_right_x=230,
        row0_y=55,
        row_dy=12,
    )


def plan_layout(board_type: str, spec: Dict[str, Any], hint: str = "") -> LayoutPlan:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _default_plan()

    client = OpenAI()

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "header_xy": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
            "caps_origin_xy": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
            "pullups_origin_xy": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
            "labels_left_x": {"type": "integer"},
            "labels_right_x": {"type": "integer"},
            "row0_y": {"type": "integer"},
            "row_dy": {"type": "integer"},
        },
        "required": [
            "header_xy",
            "caps_origin_xy",
            "pullups_origin_xy",
            "labels_left_x",
            "labels_right_x",
            "row0_y",
            "row_dy",
        ],
    }

    prompt = f"""
Plan a neat schematic layout for board type "{board_type}".

Constraints:
- Put the main connector/header on the left.
- Group decoupling caps together on the right, aligned vertically.
- Group pullups (if present) below the decoupling group.
- Keep everything aligned to a grid, avoid overlap, keep spacing consistent.

Hint (optional): {hint}

Spec:
{json.dumps(spec, indent=2)}

Return ONLY JSON matching this schema:
{json.dumps(schema)}
"""

    try:
        resp = client.responses.create(
            model="gpt-5.2",
            input=prompt,
            text={"format": {"type": "json_schema", "name": "layout_plan", "schema": schema}},
        )
        data = json.loads(resp.output_text)

        return LayoutPlan(
            header_xy=(int(data["header_xy"][0]), int(data["header_xy"][1])),
            caps_origin_xy=(int(data["caps_origin_xy"][0]), int(data["caps_origin_xy"][1])),
            pullups_origin_xy=(int(data["pullups_origin_xy"][0]), int(data["pullups_origin_xy"][1])),
            labels_left_x=int(data["labels_left_x"]),
            labels_right_x=int(data["labels_right_x"]),
            row0_y=int(data["row0_y"]),
            row_dy=int(data["row_dy"]),
        )
    except Exception:
        return _default_plan()
