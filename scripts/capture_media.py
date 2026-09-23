"""Capture README screenshots and the demo GIF from a live app run.

Starts the app against a temporary database seeded with synthetic progress,
drives headless Google Chrome over the DevTools protocol, and writes images
to docs/media/. Only the bundled synthetic demo subject is shown.

Usage:
    .venv/bin/python scripts/capture_media.py

Set CHROME_PATH if Chrome is not in its default location.
"""

import asyncio
import base64
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from PIL import Image
from tornado.websocket import websocket_connect


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prepcanvas.catalog import diagnostic_questions, load_demo_subject  # noqa: E402
from prepcanvas.storage import StudyStore  # noqa: E402


MEDIA_DIR = ROOT / "docs" / "media"
DESKTOP = (1280, 860)
MOBILE = (390, 844)


def find_chrome() -> str:
    candidates = [
        os.environ.get("CHROME_PATH"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise SystemExit("Google Chrome not found. Set CHROME_PATH.")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_http(url: str, timeout: float = 30) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return response.read().decode()
        except OSError:
            time.sleep(0.3)
    raise TimeoutError(url)


def seed_progress(database: Path):
    """Synthetic progress so the overview shows a realistic, partly complete state."""
    store = StudyStore(database)
    subject = load_demo_subject()
    store.seed_demo_subject(subject)
    store.save_profile(
        subject["id"],
        {
            "id": "coach_and_recall",
            "name": "Coach + active recall",
            "description": "Alternate concise explanations with open recall and targeted feedback.",
        },
        0.5,
        3,
    )
    results = {
        "sys-1": 1, "sys-2": 1, "sys-3": 2,
        "stake-1": 1, "stake-2": 0, "stake-3": 1,
        "circ-1": 1, "circ-3": 1,
    }
    questions = {question["id"]: question for question in subject["questions"]}
    for question_id, score in results.items():
        question = questions[question_id]
        store.save_attempt(
            subject["id"],
            "practice",
            {
                "topic_id": question["topic_id"],
                "question_id": question_id,
                "score": score,
                "max_score": question["points"],
            },
        )


class Page:
    def __init__(self, connection):
        self.connection = connection
        self.next_id = 0

    async def send(self, method: str, **params):
        self.next_id += 1
        message_id = self.next_id
        await self.connection.write_message(json.dumps({"id": message_id, "method": method, "params": params}))
        while True:
            message = json.loads(await self.connection.read_message())
            if message.get("id") == message_id:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message.get("result", {})

    async def evaluate(self, expression: str):
        result = await self.send("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in result:
            raise RuntimeError(result["exceptionDetails"])
        return result["result"].get("value")

    async def viewport(self, size, scale):
        width, height = size
        await self.send(
            "Emulation.setDeviceMetricsOverride",
            width=width,
            height=height,
            deviceScaleFactor=scale,
            mobile=width < 640,
        )

    async def goto(self, url: str):
        await self.send("Page.navigate", url=url)
        await self.wait_for("document.querySelector('.st-key-page label') !== null")
        await self.settle()

    async def wait_for(self, condition: str, timeout: float = 20):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if await self.evaluate(f"Boolean({condition})"):
                return
            await asyncio.sleep(0.2)
        raise TimeoutError(condition)

    async def settle(self):
        """Wait for the Streamlit script run to finish and the page to repaint."""
        await asyncio.sleep(0.4)
        await self.wait_for("!document.querySelector('[data-testid=\"stStatusWidget\"]')")
        await asyncio.sleep(0.8)

    async def open_page(self, name: str):
        await self.evaluate(
            "[...document.querySelectorAll('.st-key-page label')]"
            f".find(label => label.innerText.trim() === {json.dumps(name)}).click()"
        )
        await self.settle()
        await self.scroll_top()

    async def choose(self, group: int, option: str):
        """Pick an option in the n-th answer radio group, skipping the page navigation."""
        await self.evaluate(
            "[...document.querySelectorAll('[data-testid=\"stMain\"] [role=\"radiogroup\"]')]"
            ".filter(radios => !radios.closest('.st-key-page'))"
            f"[{group}].querySelectorAll('label[data-baseweb=\"radio\"]')"
            f".forEach(label => {{ if (label.innerText.trim() === {json.dumps(option)}) label.click(); }})"
        )
        await asyncio.sleep(0.2)

    async def type_into(self, index: int, text: str):
        await self.evaluate(
            f"""(() => {{
                const area = document.querySelectorAll('[data-testid="stMain"] textarea')[{index}];
                const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
                area.focus();
                setter.call(area, {json.dumps(text)});
                area.dispatchEvent(new Event('input', {{ bubbles: true }}));
                area.blur();
            }})()"""
        )
        await asyncio.sleep(0.2)

    async def mouse_click(self, element: str):
        """Click the centre of an element with real mouse events; some widgets ignore element.click()."""
        box = await self.evaluate(
            f"(() => {{ const r = ({element}).getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }})()"
        )
        for event in ("mousePressed", "mouseReleased"):
            await self.send("Input.dispatchMouseEvent", type=event, x=box[0], y=box[1], button="left", clickCount=1)

    async def select(self, index: int, option: str):
        await self.mouse_click(
            f"document.querySelectorAll('[data-testid=\"stMain\"] [data-testid=\"stSelectbox\"] [data-baseweb=\"select\"]')[{index}]"
        )
        await self.wait_for("document.querySelector('[role=\"option\"]') !== null")
        await self.mouse_click(
            "[...document.querySelectorAll('[role=\"option\"]')]"
            f".find(item => item.innerText.trim().startsWith({json.dumps(option)}))"
        )
        await self.settle()

    async def click_button(self, label: str):
        await self.evaluate(
            "[...document.querySelectorAll('button')]"
            f".find(button => button.innerText.trim() === {json.dumps(label)}).click()"
        )
        await self.settle()

    async def scroll_top(self):
        await self.evaluate("document.querySelector('[data-testid=\"stMain\"]').scrollTo(0, 0)")
        await asyncio.sleep(0.2)

    async def expect_text(self, text: str):
        body = await self.evaluate("document.querySelector('[data-testid=\"stMain\"]').innerText")
        if text not in body:
            raise RuntimeError(f"Expected {text!r} on the page. Visible text ends with:\n{body[-800:]}")

    async def scroll_to_text(self, text: str, block: str = "start"):
        await self.expect_text(text)
        await self.evaluate(
            "[...document.querySelectorAll('[data-testid=\"stMain\"] *')]"
            f".filter(node => node.innerText && node.innerText.includes({json.dumps(text)})).pop()"
            f".scrollIntoView({{ block: {json.dumps(block)} }})"
        )
        await asyncio.sleep(0.4)

    async def image(self) -> Image.Image:
        result = await self.send("Page.captureScreenshot", format="png")
        return Image.open(io.BytesIO(base64.b64decode(result["data"]))).convert("RGB")

    async def save(self, name: str):
        path = MEDIA_DIR / name
        (await self.image()).save(path, optimize=True)
        print(f"  {path.relative_to(ROOT)}")


def save_gif(frames: list, name: str, width: int = 960):
    resized = [frame.resize((width, round(frame.height * width / frame.width)), Image.LANCZOS) for frame in frames]
    palette = [frame.quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE) for frame in resized]
    durations = [frame.info.get("duration", 1600) for frame in frames]
    path = MEDIA_DIR / name
    palette[0].save(path, save_all=True, append_images=palette[1:], duration=durations, loop=0, optimize=True)
    print(f"  {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


async def capture(url: str, chrome_port: int):
    targets = json.loads(wait_for_http(f"http://127.0.0.1:{chrome_port}/json/list"))
    target = next(item for item in targets if item["type"] == "page")
    connection = await websocket_connect(target["webSocketDebuggerUrl"], max_message_size=256 * 1024 * 1024)
    page = Page(connection)
    await page.send("Page.enable")
    subject = load_demo_subject()

    print("Screenshots:")
    await page.viewport(DESKTOP, 2)
    await page.goto(url)
    await page.save("overview.png")

    await page.open_page("Learn")
    await page.save("learn.png")

    await page.open_page("Practice")
    await page.select(1, "Why can improving one sustainability metric")
    await page.type_into(0, "It looks at a narrow system boundary.")
    await page.click_button("Check answer")
    await page.scroll_to_text("Partly correct", "center")
    await page.save("practice-feedback.png")

    await page.open_page("Mock exam")
    multiple_choice = [q["correct_answer"] for q in subject["questions"] if q["type"] == "multiple_choice"]
    short_answers = [q["model_answer"] for q in subject["questions"] if q["type"] == "short_answer"]
    for group, answer in enumerate(multiple_choice):
        await page.choose(group, answer)
    short_answers[-1] = "Scope 1 is direct emissions and Scope 2 is purchased energy."
    for index, answer in enumerate(short_answers):
        await page.type_into(index, answer)
    await page.click_button("Submit mock exam")
    await page.scroll_to_text("% ·")
    await page.save("mock-exam.png")

    await page.viewport(MOBILE, 3)
    await page.open_page("Overview")
    await page.save("mobile-overview.png")

    print("GIF:")
    await page.viewport(DESKTOP, 1)
    frames = []

    def frame(image, duration=1600):
        image.info["duration"] = duration
        frames.append(image)

    await page.open_page("Diagnostic")
    frame(await page.image(), 1400)
    for group, question in enumerate(diagnostic_questions(subject)):
        await page.choose(group, question["correct_answer"])
    frame(await page.image(), 1200)
    await page.click_button("Build my learning profile")
    await page.scroll_to_text("Your starting strategy", "center")
    frame(await page.image(), 2200)

    await page.open_page("Learn")
    frame(await page.image(), 2000)

    await page.open_page("Practice")
    await page.select(1, "Why can improving one sustainability metric")
    await page.type_into(0, "The metric uses a narrow boundary and ignores trade-offs elsewhere.")
    frame(await page.image(), 1400)
    await page.click_button("Check answer")
    await page.scroll_to_text("Correct ·", "center")
    frame(await page.image(), 2400)

    await page.open_page("Overview")
    frame(await page.image(), 2400)
    save_gif(frames, "demo.gif")
    connection.close()


def main():
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="prepcanvas-media-"))
    database = workdir / "media.sqlite3"
    seed_progress(database)

    app_port, chrome_port = free_port(), free_port()
    env = {**os.environ, "PREPCANVAS_DB_PATH": str(database), "PYTHONPATH": str(ROOT / "src")}
    app = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", str(ROOT / "app" / "streamlit_app.py"),
            "--server.headless", "true", "--server.port", str(app_port),
            "--browser.gatherUsageStats", "false",
        ],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    chrome = subprocess.Popen(
        [
            find_chrome(), "--headless=new", f"--remote-debugging-port={chrome_port}",
            f"--user-data-dir={workdir / 'chrome'}", "--no-first-run", "--no-default-browser-check",
            "--hide-scrollbars", "--force-color-profile=srgb", "about:blank",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        url = f"http://127.0.0.1:{app_port}"
        wait_for_http(f"{url}/_stcore/health")
        asyncio.run(capture(url, chrome_port))
    finally:
        chrome.terminate()
        app.terminate()
        chrome.wait(timeout=10)
        app.wait(timeout=10)
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
