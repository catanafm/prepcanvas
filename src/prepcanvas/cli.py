"""Command-line helpers: validate a subject package or print the chat prompt for a subject."""

import argparse
import os
import sys
from pathlib import Path

from prepcanvas.packages import PackageError, SubjectFiles, content_summary, read_package
from prepcanvas.prompts import chat_prompt


DEFAULT_PRIVATE_DIR = Path(__file__).resolve().parents[2] / "data" / "private"


def private_dir(override=None) -> Path:
    return Path(override or os.environ.get("PREPCANVAS_PRIVATE_DIR") or DEFAULT_PRIVATE_DIR)


def format_issue(issue: dict) -> str:
    return f"{issue['level'].upper():7} {issue['path']}: {issue['message']}"


def validate_command(args) -> int:
    path = Path(args.path)
    expected_id = args.subject_id
    if expected_id is None and path.name == "package.json" and path.parent.parent.name == "subjects":
        expected_id = path.parent.name
    try:
        package = read_package(path, expected_id=expected_id)
    except PackageError as error:
        for issue in error.issues:
            print(format_issue(issue))
        errors = sum(1 for issue in error.issues if issue["level"] == "error")
        print(f"\n{path}: {errors} error(s). Fix them and validate again.")
        return 1
    warnings = package.pop("_warnings")
    for issue in warnings:
        print(format_issue(issue))
    summary = content_summary(package)
    print(
        f"{path}: valid. {summary['topics']} topics, {summary['questions']} questions "
        f"({summary['source']} from materials, {summary['generated']} generated), {len(warnings)} warning(s)."
    )
    return 0


def prompt_command(args) -> int:
    files = SubjectFiles(private_dir(args.private_dir))
    brief = files.read_brief(args.subject_id) or {"id": args.subject_id, "name": args.subject_id}
    print(chat_prompt(brief, files.list_materials(args.subject_id), files.subject_dir(args.subject_id)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prepcanvas", description="PrepCanvas subject package tools.")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="Validate a subject package and print every issue.")
    validate.add_argument("path", help="Path to package.json")
    validate.add_argument("--subject-id", help="Expected package id; inferred from data/private/subjects/<id>/package.json")
    validate.set_defaults(func=validate_command)

    prompt = commands.add_parser("prompt", help="Print the chat-assistant prompt for a subject.")
    prompt.add_argument("subject_id")
    prompt.add_argument("--private-dir", help="Private data folder (default: PREPCANVAS_PRIVATE_DIR or data/private)")
    prompt.set_defaults(func=prompt_command)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
