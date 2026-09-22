import json
from pathlib import Path

import pytest


@pytest.fixture
def demo_subject():
    path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "prepcanvas"
        / "demo_data"
        / "sustainable_business.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))
