import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def pins(lines) -> dict:
    found = {}
    for line in lines:
        match = re.fullmatch(r'\s*"?([A-Za-z0-9_.-]+)==([^"\s]+)"?,?\s*', line)
        if match:
            found[match[1].lower()] = match[2]
    return found


def test_requirements_match_pyproject_pins():
    pyproject = ROOT.joinpath("pyproject.toml").read_text(encoding="utf-8")
    declared = pins(re.findall(r'"([^"]+==[^"]+)"', pyproject))
    requirements = pins(ROOT.joinpath("requirements.txt").read_text(encoding="utf-8").splitlines())
    assert declared == requirements


def test_package_version_matches_pyproject():
    from prepcanvas import __version__

    pyproject = ROOT.joinpath("pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE)[1] == __version__
