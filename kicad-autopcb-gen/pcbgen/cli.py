import argparse
from pathlib import Path

import yaml

from pcbgen.spec import ProjectSpec
from pcbgen.kicad_project import generate_project
from pcbgen.ai_spec import spec_from_prompt


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate a KiCad 9 project from YAML spec OR natural-language prompt (offline parser)."
    )

    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--spec", help="Path to YAML spec")
    src.add_argument("--prompt", help="Natural language description of the PCB to generate")

    ap.add_argument("--out", required=True, help="Output directory (project folder will be created here)")
    ap.add_argument("--ai", action="store_true", help="Optional: enable AI layout planning (if you later add it).")
    ap.add_argument("--hint", default="", help="Optional hint (compact/neat/left-header/etc.)")

    args = ap.parse_args()
    out_dir = Path(args.out).expanduser().resolve()

    # Load YAML spec OR generate spec from prompt (offline)
    if args.spec:
        spec_path = Path(args.spec).expanduser().resolve()
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit("Spec YAML must be a mapping at the top level.")
    else:
        data = spec_from_prompt(args.prompt)
        if not isinstance(data, dict):
            raise SystemExit("Prompt parsing failed (did not return an object).")

    # stash flags in spec so templates can use them
    data["_use_ai"] = bool(args.ai)
    data["_hint"] = str(args.hint)

    name = str(data.get("name", "")).strip()
    board_type = str(data.get("type", "")).strip()
    if not name or not board_type:
        raise SystemExit("Spec must include: name, type")

    spec = ProjectSpec(name=name, type=board_type, raw=data)
    generate_project(spec, out_dir)

    print(f"Generated project at: {out_dir}")


if __name__ == "__main__":
    main()
