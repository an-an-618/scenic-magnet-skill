from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    PROJECT_ROOT
    / "skills"
    / "scenic-magnet-v1"
    / "scripts"
    / "analyze_magnet_frame.py"
)


def load_analyzer(test_case: unittest.TestCase):
    test_case.assertTrue(
        SCRIPT_PATH.exists(),
        f"Production analyzer does not exist: {SCRIPT_PATH}",
    )
    spec = importlib.util.spec_from_file_location("analyze_magnet_frame", SCRIPT_PATH)
    test_case.assertIsNotNone(spec)
    test_case.assertIsNotNone(spec.loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AnalyzeMagnetFrameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_analyzer(self)
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.temp_path = Path(self.tempdir.name)

    def write_image(self, image: Image.Image, name: str) -> Path:
        path = self.temp_path / name
        image.save(path)
        return path

    def quiet_canvas(self) -> Image.Image:
        return Image.new("RGB", (400, 300), "#b48a5a")

    def test_reports_centered_foreground_on_quiet_background(self) -> None:
        image = self.quiet_canvas()
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((80, 45, 320, 255), radius=12, fill="#2b3948")

        report = self.module.analyze_image(self.write_image(image, "centered.png"))

        self.assertTrue(report["is_4_3"])
        self.assertEqual(report["foreground_bbox"], [80, 45, 320, 255])
        self.assertGreaterEqual(report["foreground_bbox_fraction"], 0.40)
        self.assertLessEqual(report["foreground_bbox_fraction"], 0.65)
        self.assertEqual(report["warnings"], [])

    def test_warns_when_canvas_is_not_four_by_three(self) -> None:
        image = Image.new("RGB", (300, 300), "#b48a5a")
        ImageDraw.Draw(image).rectangle((60, 45, 240, 255), fill="#2b3948")

        report = self.module.analyze_image(self.write_image(image, "square.png"))

        self.assertFalse(report["is_4_3"])
        self.assertIn("not_4_3", report["warnings"])

    def test_warns_when_magnet_is_too_small(self) -> None:
        image = self.quiet_canvas()
        ImageDraw.Draw(image).rectangle((175, 130, 225, 170), fill="#2b3948")

        report = self.module.analyze_image(self.write_image(image, "tiny.png"))

        self.assertIn("magnet_too_small", report["warnings"])

    def test_warns_when_magnet_is_too_large(self) -> None:
        image = self.quiet_canvas()
        ImageDraw.Draw(image).rectangle((10, 10, 390, 290), fill="#2b3948")

        report = self.module.analyze_image(self.write_image(image, "large.png"))

        self.assertIn("magnet_too_large", report["warnings"])

    def test_warns_when_foreground_touches_canvas_edge(self) -> None:
        image = self.quiet_canvas()
        ImageDraw.Draw(image).rectangle((0, 45, 240, 255), fill="#2b3948")

        report = self.module.analyze_image(self.write_image(image, "edge.png"))

        self.assertIn("foreground_touches_edge", report["warnings"])

    def test_warns_when_background_border_is_not_quiet(self) -> None:
        image = self.quiet_canvas()
        draw = ImageDraw.Draw(image)
        draw.rectangle((80, 45, 320, 255), fill="#2b3948")
        for x in range(9, 391, 2):
            draw.point((x, 9), fill="#f4d35e")
            draw.point((x, 290), fill="#145da0")
        for y in range(9, 291, 2):
            draw.point((9, y), fill="#f4d35e")
            draw.point((390, y), fill="#145da0")

        report = self.module.analyze_image(self.write_image(image, "noisy.png"))

        self.assertIn("background_not_quiet", report["warnings"])

    def test_cli_prints_json_without_modifying_source(self) -> None:
        image = self.quiet_canvas()
        ImageDraw.Draw(image).rectangle((80, 45, 320, 255), fill="#2b3948")
        path = self.write_image(image, "cli.png")
        before = hashlib.sha256(path.read_bytes()).hexdigest()

        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(path)],
            check=False,
            capture_output=True,
            text=True,
        )

        after = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["width"], 400)
        self.assertEqual(payload["height"], 300)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
