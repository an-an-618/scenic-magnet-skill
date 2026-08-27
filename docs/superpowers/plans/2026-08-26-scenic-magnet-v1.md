# Scenic Magnet v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and locally install `$scenic-magnet-v1`, a one-step Codex image skill that turns a supplied photo into a 4:3 product photograph of a scene-derived metallic miniature-landscape refrigerator magnet on a dominant-color material background.

**Architecture:** Keep the executable skill contract small and route detailed decisions into three references: scene distillation, material/mechanism design, and quality control. Use built-in image generation in edit mode for pixels, plus a read-only Pillow analyzer for deterministic checks of frame ratio, approximate magnet occupancy, edge clearance, and background quietness. Behavioral contract tests protect the direct-generation, no-invented-text, optional-mechanism, and privacy rules.

**Tech Stack:** Codex Skill Markdown, built-in image generation, Python 3.10+, Pillow, `unittest`, official Codex skill scaffold and validator.

**Spec:** `docs/superpowers/specs/2026-08-26-scenic-magnet-design.md`

## Global Constraints

- Output is always one 4:3 landscape finished image, never a Before/After comparison.
- The skill generates directly without candidates or a confirmation gate.
- The magnet condenses 2–5 source-grounded elements into one connected miniature landscape.
- Background color derives from the source photo's largest effective color; exactly one main material is used.
- Use no more than two metal colors and make thickness, bevels, relief, highlights, and contact shadow visible.
- Mechanisms are optional and appear only when the scene naturally supports rotation, opening, sliding, or pulling.
- Default to no text; preserve only exact user text or clearly legible identity-bearing source signage.
- Never publish, commit, or copy user photos without per-image public authorization.
- Automatic correction is limited to one observed failure.

---

### Task 1: Establish RED Behavioral Contracts

**Files:**
- Create: `.gitignore`
- Create: `evals/scenarios.md`
- Create: `evals/expected-behavior.md`
- Create: `evals/baseline-observations.md`
- Create: `tests/test_skill_contract.py`

**Interfaces:**
- Consumes: the approved design spec.
- Produces: scenario IDs `SM-01` through `SM-08` and failing contract tests that later consume `skills/scenic-magnet-v1/SKILL.md` and the three reference files.

- [ ] **Step 1: Create privacy-safe repository ignores and evaluation scenarios**

Write `.gitignore` with:

```gitignore
.DS_Store
.deps/
__pycache__/
*.pyc
output/
tmp/
evals/local/
evals/test-images.local.md
```

Write `evals/scenarios.md` covering:

```markdown
| ID | Source class | Required behavior | Forbidden behavior |
|---|---|---|---|
| SM-01 | Landmark street scene | Build a 2–5 element connected miniature landscape | Reduce the scene to one isolated badge icon |
| SM-02 | Transit scene | Preserve the vehicle plus defining spatial base | Paste a miniature photograph onto metal |
| SM-03 | Natural landscape | Use terrain, water, and one identity-bearing formation | Invent an unrelated famous landmark |
| SM-04 | Scene with motion semantics | Add at most one visible, plausible mechanism | Add a mechanism without an axle, hinge, rail, or slot |
| SM-05 | Scene without motion semantics | Use no mechanism | Force a decorative moving part |
| SM-06 | Clear dominant source color | Derive one quiet tactile background from that color | Choose an unrelated branded backdrop |
| SM-07 | Ambiguous or unreadable text | Omit text | Guess, translate, or autocomplete lettering |
| SM-08 | Any valid source | Generate one 4:3 result immediately | Return candidates or ask for confirmation |
```

- [ ] **Step 2: Write contract tests before the skill exists**

Create `tests/test_skill_contract.py` with tests that load the future skill files and assert:

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "scenic-magnet-v1" / "SKILL.md"
REFERENCE_NAMES = {
    "scene-distillation.md",
    "material-and-mechanism.md",
    "quality-gate.md",
}


class SkillContractTests(unittest.TestCase):
    def read_skill(self) -> str:
        return SKILL.read_text(encoding="utf-8")

    def test_skill_routes_to_all_required_references(self) -> None:
        text = self.read_skill()
        for name in REFERENCE_NAMES:
            self.assertIn(name, text)

    def test_direct_generation_has_no_candidate_gate(self) -> None:
        text = self.read_skill().lower()
        self.assertIn("generate directly", text)
        self.assertIn("do not return candidates", text)

    def test_core_visual_contract_is_explicit(self) -> None:
        text = self.read_skill().lower()
        for phrase in ("4:3", "2–5", "one main material", "two metal colors"):
            self.assertIn(phrase.lower(), text)

    def test_optional_mechanism_and_text_rules_are_explicit(self) -> None:
        text = self.read_skill().lower()
        self.assertIn("mechanism is optional", text)
        self.assertIn("default to no text", text)

    def test_split_screen_and_badge_defaults_are_forbidden(self) -> None:
        text = self.read_skill().lower()
        self.assertIn("before/after", text)
        self.assertIn("round badge", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests and verify RED**

Run:

```bash
python3 -m unittest tests/test_skill_contract.py -v
```

Expected: errors caused by the absent `skills/scenic-magnet-v1/SKILL.md`, proving the new behavior is not yet deployable.

- [ ] **Step 4: Record baseline evidence**

Write `evals/baseline-observations.md` stating that the skill and analyzer do not yet exist, the supplied badge references are visual references rather than publishable fixtures, and live image tests must remain local unless separately authorized.

- [ ] **Step 5: Commit RED artifacts**

```bash
git add .gitignore evals tests/test_skill_contract.py
git commit -m "test: define Scenic Magnet behavior contracts"
```

---

### Task 2: Build the Read-Only Magnet Frame Analyzer with TDD

**Files:**
- Create: `tests/test_analyze_magnet_frame.py`
- Create: `skills/scenic-magnet-v1/scripts/analyze_magnet_frame.py`

**Interfaces:**
- Consumes: an output image path.
- Produces: `analyze_image(path: Path | str, max_edge: int = 640) -> dict[str, object]` and CLI JSON containing `width`, `height`, `aspect_ratio`, `is_4_3`, `background_rgb`, `background_edge_variance`, `foreground_bbox`, `foreground_bbox_fraction`, `foreground_edge_clearance`, and `warnings`.

- [ ] **Step 1: Write synthetic-image tests first**

Create `tests/test_analyze_magnet_frame.py` using Pillow to generate controlled 400×300 images. Cover:

```python
def test_reports_centered_foreground_on_quiet_background():
    image = Image.new("RGB", (400, 300), "#b48a5a")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((80, 45, 320, 255), radius=12, fill="#2b3948")
    report = analyze_image(write_image(image, "centered.png"))
    assert report["is_4_3"] is True
    assert report["foreground_bbox"] == [80, 45, 320, 255]
    assert 0.40 <= report["foreground_bbox_fraction"] <= 0.65
    assert report["warnings"] == []
```

Also test: square input yields `not_4_3`; tiny foreground yields `magnet_too_small`; oversized foreground yields `magnet_too_large`; touching the edge yields `foreground_touches_edge`; noisy border yields `background_not_quiet`; CLI output is valid JSON and does not change the source hash.

- [ ] **Step 2: Run analyzer tests and verify RED**

Run:

```bash
python3 -m unittest tests/test_analyze_magnet_frame.py -v
```

Expected: `ModuleNotFoundError` or explicit missing-production-script failure.

- [ ] **Step 3: Implement minimal analyzer**

Implement these focused functions in `analyze_magnet_frame.py`:

```python
TARGET_RATIO = 4 / 3
RATIO_TOLERANCE = 0.015
COLOR_DISTANCE_THRESHOLD = 42.0

def sample_border_rgb(
    image: Image.Image, inset_fraction: float = 0.03
) -> list[tuple[int, int, int]]:
    width, height = image.size
    inset = max(1, round(min(width, height) * inset_fraction))
    step = max(1, min(width, height) // 200)
    pixels = image.load()
    top_y, bottom_y = inset, height - inset - 1
    left_x, right_x = inset, width - inset - 1
    samples = [pixels[x, top_y] for x in range(left_x, right_x + 1, step)]
    samples += [pixels[x, bottom_y] for x in range(left_x, right_x + 1, step)]
    samples += [pixels[left_x, y] for y in range(top_y, bottom_y + 1, step)]
    samples += [pixels[right_x, y] for y in range(top_y, bottom_y + 1, step)]
    return samples

def median_rgb(samples: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    return tuple(round(statistics.median(channel)) for channel in zip(*samples))

def color_distance(
    a: tuple[int, int, int], b: tuple[int, int, int]
) -> float:
    return math.sqrt(sum((left - right) ** 2 for left, right in zip(a, b)))

def build_foreground_mask(
    image: Image.Image, background: tuple[int, int, int]
) -> list[bool]:
    raw = Image.new("L", image.size)
    raw.putdata([
        255 if color_distance(pixel, background) >= COLOR_DISTANCE_THRESHOLD else 0
        for pixel in image.getdata()
    ])
    cleaned = raw.filter(ImageFilter.MedianFilter(size=5))
    return [value >= 128 for value in cleaned.getdata()]

def mask_bbox(mask: list[bool], size: tuple[int, int]) -> list[int] | None:
    width, _ = size
    points = [(index % width, index // width) for index, value in enumerate(mask) if value]
    if not points:
        return None
    xs, ys = zip(*points)
    return [min(xs), min(ys), max(xs), max(ys)]

def analyze_image(path: Path | str, max_edge: int = 640) -> dict[str, object]:
    source_path = Path(path)
    with Image.open(source_path) as source:
        original = source.convert("RGB")
    analysis = original.copy()
    analysis.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    border = sample_border_rgb(analysis)
    background = median_rgb(border)
    variance = statistics.fmean(color_distance(pixel, background) for pixel in border)
    mask = build_foreground_mask(analysis, background)
    bbox = mask_bbox(mask, analysis.size)
    bbox_fraction = 0.0 if bbox is None else (
        (bbox[2] - bbox[0] + 1) * (bbox[3] - bbox[1] + 1)
        / (analysis.width * analysis.height)
    )
    clearance = 1.0 if bbox is None else min(
        bbox[0] / analysis.width,
        bbox[1] / analysis.height,
        (analysis.width - bbox[2] - 1) / analysis.width,
        (analysis.height - bbox[3] - 1) / analysis.height,
    )
    warnings = []
    if abs(original.width / original.height - TARGET_RATIO) > RATIO_TOLERANCE:
        warnings.append("not_4_3")
    if bbox_fraction < 0.40:
        warnings.append("magnet_too_small")
    if bbox_fraction > 0.70:
        warnings.append("magnet_too_large")
    if clearance < 0.02:
        warnings.append("foreground_touches_edge")
    if variance > 32.0:
        warnings.append("background_not_quiet")
    return {
        "width": original.width,
        "height": original.height,
        "aspect_ratio": round(original.width / original.height, 6),
        "is_4_3": "not_4_3" not in warnings,
        "background_rgb": list(background),
        "background_edge_variance": round(variance, 3),
        "foreground_bbox": bbox,
        "foreground_bbox_fraction": round(bbox_fraction, 6),
        "foreground_edge_clearance": round(clearance, 6),
        "warnings": warnings,
    }
```

Use border median as the background estimate, Euclidean RGB distance for the approximate foreground mask, a small connected-component cutoff to discard texture noise, and bounding-box area divided by canvas area for occupancy. Emit warnings with exact names from Step 1. Never write to the source image.

- [ ] **Step 4: Run analyzer tests and verify GREEN**

Run:

```bash
python3 -m unittest tests/test_analyze_magnet_frame.py -v
```

Expected: all analyzer tests pass.

- [ ] **Step 5: Commit analyzer**

```bash
git add tests/test_analyze_magnet_frame.py skills/scenic-magnet-v1/scripts/analyze_magnet_frame.py
git commit -m "feat: add Scenic Magnet frame analyzer"
```

---

### Task 3: Scaffold and Implement the Skill Contract

**Files:**
- Create: `skills/scenic-magnet-v1/SKILL.md`
- Create: `skills/scenic-magnet-v1/agents/openai.yaml`
- Create: `skills/scenic-magnet-v1/references/scene-distillation.md`
- Create: `skills/scenic-magnet-v1/references/material-and-mechanism.md`
- Create: `skills/scenic-magnet-v1/references/quality-gate.md`
- Modify: `tests/test_skill_contract.py`

**Interfaces:**
- Consumes: one supplied photograph and the three required reference files.
- Produces: a direct built-in image-generation edit call and one 4:3 final image after at most one targeted correction.

- [ ] **Step 1: Read current skill-authoring instructions completely**

Read the official `skill-creator` and `writing-skills` instructions before creating the scaffold. Use the official initializer when available; do not invent frontmatter fields.

- [ ] **Step 2: Initialize the official scaffold**

Run the official initializer with:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/init_skill.py" \
  scenic-magnet-v1 \
  --path skills \
  --resources scripts,references \
  --interface 'display_name=景铸 · Scenic Magnet' \
  --interface 'short_description=将照片直接铸成4:3立体金属微缩景观冰箱贴' \
  --interface 'default_prompt=Use $scenic-magnet-v1 to transform this photo directly into a 4:3 product photograph of a scene-derived metallic miniature-landscape refrigerator magnet.'
```

If the initializer refuses because the analyzer directory already exists, initialize in a temporary directory and copy only the missing scaffold files into the tracked folder.

- [ ] **Step 3: Write the compact SKILL.md contract**

The final `SKILL.md` must include:

- a description triggered by photo-to-metallic-miniature-magnet requests;
- required complete reading of all three references;
- required use of built-in image generation in edit mode;
- exact non-negotiable table for direct generation, 4:3, 2–5 elements, one main background material, no more than two metal colors, optional mechanism, default no text, and at most one correction;
- a 10-step workflow from source inspection to final display;
- a six-part prompt compiler;
- privacy and delivery rules.

Keep `SKILL.md` under 500 lines and route detailed visual language to references.

- [ ] **Step 4: Write scene-distillation reference**

Define the Scene DNA Card, 2–5 element selection, source-fidelity lock, human handling, connected-manufacturing outline, deletion hierarchy, and failure corrections. Include explicit rules forbidding invented landmarks and ordinary-person portrait reconstruction.

- [ ] **Step 5: Write material-and-mechanism reference**

Define the controlled metal palette, enamel behavior, relief layers, thickness and bevel cues, dominant-color material background mapping, optional mechanism decision tree, 3/4 product photography, and hard avoids for plastic, flat stickers, round badges, hands, props, and split screens.

- [ ] **Step 6: Write quality-gate reference**

Define preflight, normal-scale inspection, thumbnail inspection, analyzer use, targeted correction table, stop rules, and honest delivery. State that analyzer evidence does not replace aesthetic judgment.

- [ ] **Step 7: Run all contract tests and official validation**

Run:

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=.deps python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/scenic-magnet-v1
```

Expected: all tests pass and validator prints `Skill is valid!`.

- [ ] **Step 8: Commit the skill implementation**

```bash
git add skills tests
git commit -m "feat: implement Scenic Magnet v1 skill"
```

---

### Task 4: Document, Package, and Install Locally

**Files:**
- Create: `README.md`
- Create: `README.zh-CN.md`
- Create locally only: `evals/test-images.local.md`

**Interfaces:**
- Consumes: the validated skill directory.
- Produces: user-facing usage docs, a clean installable zip, and a globally installed local skill.

- [ ] **Step 1: Write bilingual user documentation**

Document the one-step workflow, 4:3 output, scene DNA concept, material system, optional mechanisms, no-invented-text rule, privacy boundary, structure, local installation, and analyzer dependency. Do not claim public examples or GitHub installation before those artifacts exist.

- [ ] **Step 2: Record reference inputs privately**

Create gitignored `evals/test-images.local.md` listing the three supplied composite reference images as local visual references only. Explicitly state they are not public fixtures and are not copied into the repository.

- [ ] **Step 3: Build a clean installable archive**

Create `/private/tmp/scenic-magnet-release/scenic-magnet-v1.zip` containing only `scenic-magnet-v1/`, excluding `__pycache__`, `.pyc`, tests, evals, reference photos, and repository docs. Verify with `unzip -l` and `unzip -t`.

- [ ] **Step 4: Install into the global Codex skills directory**

Copy the validated skill to `${CODEX_HOME:-$HOME/.codex}/skills/scenic-magnet-v1`, preserving any unrelated skills. If an existing version is present, compare it first and replace only this exact directory after user-authorized escalation.

- [ ] **Step 5: Validate installed artifact**

Run the official validator against the installed directory and compare it recursively with the repository skill, excluding caches. Expected: `Skill is valid!` and no content differences.

- [ ] **Step 6: Commit documentation**

```bash
git add README.md README.zh-CN.md
git commit -m "docs: add Scenic Magnet usage and packaging guide"
```

---

### Task 5: Run Local Visual Acceptance Test

**Files:**
- Create locally only: `evals/local/` outputs and notes.
- Modify after observed failures only: the minimum relevant skill/reference file.

**Interfaces:**
- Consumes: the three supplied visual references and the installed `$scenic-magnet-v1` workflow.
- Produces: at least one 4:3 preview demonstrating the new system, plus normal-scale, thumbnail, and analyzer evidence.

- [ ] **Step 1: Select a suitable local source from the references**

Use the source-photo half of one supplied composite only as a private local test. Do not copy the composite or crop into the repository. Prefer a transit scene because it exercises scene distillation, dominant color, metallic detail, and an optional sliding mechanism.

- [ ] **Step 2: Generate directly with no candidate turn**

Use built-in image generation in edit mode. The prompt must specify a 4:3 landscape product photograph, a connected 2–5 element miniature landscape, source-derived background color and one material, no more than two metal colors, and the scene-appropriate mechanism decision. Do not reproduce the reference badge layout, captions, watermarks, or split screen.

- [ ] **Step 3: Inspect and analyze**

Inspect the output at normal size and thumbnail scale. If a local output path is available, run:

```bash
python3 skills/scenic-magnet-v1/scripts/analyze_magnet_frame.py /absolute/path/to/output.png
```

Record whether the scene identity, connected outline, material contrast, thickness, lighting, optional mechanism, no-text rule, and 4:3 composition pass.

- [ ] **Step 4: Apply at most one targeted correction**

Correct only a concrete observed failure from `quality-gate.md`. Repeat the source identity, 2–5 core elements, text rule, and exact material contract in the correction prompt.

- [ ] **Step 5: Run final verification**

Run all unit tests, official validation, installed-artifact comparison, archive integrity check, repository privacy scan for local clipboard paths, and `git diff --check`. Do not call the skill complete unless every command exits successfully and any visual limitation is reported honestly.

- [ ] **Step 6: Commit only durable, authorized changes**

Commit code or documentation corrections. Do not commit test photos, generated previews, or local evaluation notes without explicit per-image publication authorization.
