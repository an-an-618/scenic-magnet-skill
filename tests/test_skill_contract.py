import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "skills" / "scenic-magnet-v1" / "scripts" / "compile_magnet_brief.py"


def load_compiler(test_case: unittest.TestCase):
    test_case.assertTrue(
        COMPILER.exists(),
        f"Scenic Magnet prompt compiler does not exist: {COMPILER}",
    )
    spec = importlib.util.spec_from_file_location("compile_magnet_brief", COMPILER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_scene(**overrides):
    scene = {
        "scene_type": "coastal transit",
        "dominant_color": "muted ocean blue",
        "temperature": "cool",
        "elements": [
            {"name": "tram", "importance": 0.98},
            {"name": "curving track", "importance": 0.86},
            {"name": "coastal railing", "importance": 0.72},
            {"name": "distant headland", "importance": 0.61},
            {"name": "road sign", "importance": 0.31},
            {"name": "parked car", "importance": 0.18},
        ],
        "motion_semantics": [],
        "legible_identity_text": None,
        "user_text": None,
    }
    scene.update(overrides)
    return scene


class ScenicMagnetContractTests(unittest.TestCase):
    def setUp(self):
        self.compiler = load_compiler(self)

    def test_returns_one_direct_result_without_confirmation(self):
        brief = self.compiler.compile_brief(sample_scene())
        self.assertEqual(brief["candidate_count"], 1)
        self.assertFalse(brief["requires_confirmation"])

    def test_uses_landscape_four_by_three_canvas(self):
        brief = self.compiler.compile_brief(sample_scene())
        self.assertEqual(brief["canvas"], "4:3 landscape")

    def test_selects_between_two_and_five_source_elements(self):
        brief = self.compiler.compile_brief(sample_scene())
        self.assertEqual(
            brief["scene_elements"],
            ["tram", "curving track", "coastal railing", "distant headland"],
        )

    def test_omits_mechanism_without_motion_semantics(self):
        brief = self.compiler.compile_brief(sample_scene())
        self.assertIsNone(brief["mechanism"])

    def test_chooses_one_plausible_mechanism_for_motion_scene(self):
        brief = self.compiler.compile_brief(
            sample_scene(motion_semantics=["vehicle follows a track", "sea breeze"])
        )
        self.assertEqual(brief["mechanism"], "short guided slider")

    def test_omits_unreadable_and_unsupplied_text(self):
        brief = self.compiler.compile_brief(
            sample_scene(legible_identity_text="uncertain partial letters")
        )
        self.assertIsNone(brief["text"])

    def test_preserves_exact_user_supplied_text(self):
        brief = self.compiler.compile_brief(sample_scene(user_text="JEJU 2026"))
        self.assertEqual(brief["text"], "JEJU 2026")

    def test_uses_one_quiet_scene_matched_background_material(self):
        brief = self.compiler.compile_brief(sample_scene())
        self.assertEqual(brief["background_material"], "ocean-blue silk paper")

    def test_limits_metal_palette_to_two_finishes(self):
        brief = self.compiler.compile_brief(sample_scene())
        self.assertEqual(brief["metal_finishes"], ["brushed nickel", "darkened silver"])
        self.assertLessEqual(len(brief["metal_finishes"]), 2)


if __name__ == "__main__":
    unittest.main()
