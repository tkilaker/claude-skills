#!/usr/bin/env python3
"""Build a personal-style PDF from Markdown with Pandoc and Eisvogel."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "eisvogel" / "eisvogel.latex"
DEFAULT_STYLE = SKILL_ROOT / "assets" / "styles" / "tim-default.yaml"
DEFAULT_FROM = "markdown+yaml_metadata_block+tex_math_dollars+raw_tex+smart"


def existing_path(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {value}")
    return path


def parse_key_value(value: str) -> str:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected KEY=VALUE")
    key, raw = value.split("=", 1)
    if not key.strip():
        raise argparse.ArgumentTypeError("metadata or variable key cannot be empty")
    return f"{key.strip()}={raw}"


def build_command(args: argparse.Namespace) -> list[str]:
    input_path = args.input.resolve()
    output_path = args.output or input_path.with_suffix(".pdf")
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resource_paths = [input_path.parent.resolve(), Path.cwd().resolve()]
    resource_paths.extend(path.expanduser().resolve() for path in args.resource_path)
    resource_value = os.pathsep.join(dict.fromkeys(str(path) for path in resource_paths))

    cmd = [
        "pandoc",
        str(input_path),
        "--standalone",
        "--from",
        args.from_format,
        "--output",
        str(output_path),
        "--template",
        str(args.template.resolve()),
        "--pdf-engine",
        args.pdf_engine,
        "--syntax-highlighting",
        args.syntax_highlighting,
        "--metadata-file",
        str(args.style.resolve()),
        "--resource-path",
        resource_value,
    ]

    for metadata_file in args.metadata_file:
        cmd.extend(["--metadata-file", str(metadata_file.expanduser().resolve())])
    for item in args.metadata:
        cmd.extend(["--metadata", item])
    for item in args.variable:
        cmd.extend(["--variable", item])
    if args.toc:
        cmd.append("--toc")
    if args.number_sections:
        cmd.append("--number-sections")
    if args.extra:
        cmd.extend(args.extra[1:] if args.extra[:1] == ["--"] else args.extra)

    return cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a styled PDF from Markdown using the bundled Eisvogel template."
    )
    parser.add_argument("input", type=existing_path, help="Markdown source file")
    parser.add_argument("-o", "--output", type=Path, help="Output PDF path")
    parser.add_argument("--style", type=existing_path, default=DEFAULT_STYLE)
    parser.add_argument("--template", type=existing_path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--metadata-file", type=existing_path, action="append", default=[])
    parser.add_argument("--metadata", type=parse_key_value, action="append", default=[])
    parser.add_argument("--variable", type=parse_key_value, action="append", default=[])
    parser.add_argument("--resource-path", type=existing_path, action="append", default=[])
    parser.add_argument("--pdf-engine", default="xelatex")
    parser.add_argument("--from-format", default=DEFAULT_FROM)
    parser.add_argument("--syntax-highlighting", default="idiomatic")
    parser.add_argument("--toc", action="store_true")
    parser.add_argument("--number-sections", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print the command only")
    args, extra = parser.parse_known_args()
    args.extra = extra
    return args


def main() -> int:
    args = parse_args()

    if shutil.which("pandoc") is None:
        print("pandoc is not installed or not on PATH", file=sys.stderr)
        return 1
    if shutil.which(args.pdf_engine) is None:
        print(f"{args.pdf_engine} is not installed or not on PATH", file=sys.stderr)
        return 1

    cmd = build_command(args)
    print(" ".join(subprocess.list2cmdline([part]) for part in cmd))
    if args.dry_run:
        return 0

    completed = subprocess.run(cmd, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
