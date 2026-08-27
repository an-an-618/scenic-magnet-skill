#!/usr/bin/env python3
"""Compile a Scene DNA card into a deterministic Scenic Magnet brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


def _selected_elements(elements: list[dict[str, Any]]) -> list[str]:
    ranked = sorted(
        elements,
        key=lambda item: float(item.get("importance", 0.0)),
        reverse=True,
    )
    selected = [
        str(item["name"]).strip()
        for item in ranked
        if float(item.get("importance", 0.0)) >= 0.50
        and str(item.get("name", "")).strip()
    ][:5]
    if len(selected) < 2:
        selected = [
            str(item["name"]).strip()
            for item in ranked[:2]
            if str(item.get("name", "")).strip()
        ]
    if len(selected) < 2:
        raise ValueError("A Scenic Magnet brief requires at least two named scene elements")
    return selected


def _background_material(scene: dict[str, Any]) -> str:
    color = str(scene.get("dominant_color", "neutral")).lower()
    scene_type = str(scene.get("scene_type", "")).lower()
    if any(token in color for token in ("ocean", "blue", "cyan", "azure")):
        return "ocean-blue silk paper"
    if any(token in color for token in ("green", "moss", "forest")):
        return "muted green wool felt"
    if any(token in color for token in ("red", "crimson", "burgundy")):
        return "deep red woven paper"
    if any(token in color for token in ("yellow", "ochre", "amber", "orange")):
        return "ochre corrugated art paper"
    if any(token in scene_type for token in ("historic", "heritage", "old town")):
        return "warm neutral linen paper"
    return "neutral textured museum board"


def _metal_finishes(scene: dict[str, Any]) -> list[str]:
    scene_type = str(scene.get("scene_type", "")).lower()
    temperature = str(scene.get("temperature", "")).lower()
    if any(token in scene_type for token in ("mountain", "industrial", "night")):
        return ["gunmetal", "oxidized copper"]
    if temperature == "warm" or any(
        token in scene_type for token in ("historic", "heritage", "old town")
    ):
        return ["antique brass", "warm gold"]
    return ["brushed nickel", "darkened silver"]


def _mechanism(scene: dict[str, Any]) -> str | None:
    semantics = " ".join(str(value).lower() for value in scene.get("motion_semantics", []))
    if not semantics:
        return None
    if any(token in semantics for token in ("vehicle", "track", "tram", "train")):
        return "short guided slider"
    if any(token in semantics for token in ("door", "window", "open", "reveal")):
        return "miniature hinge"
    if any(token in semantics for token in ("wheel", "rotate", "spin", "windmill")):
        return "single pivot wheel"
    if any(token in semantics for token in ("tide", "wave", "current", "water")):
        return "sliding tide layer"
    return None


def _text(scene: dict[str, Any]) -> str | None:
    supplied = str(scene.get("user_text") or "").strip()
    if supplied:
        return supplied
    confidence = float(scene.get("text_confidence", 0.0))
    legible = str(scene.get("legible_identity_text") or "").strip()
    return legible if legible and confidence >= 0.95 else None


def compile_brief(scene: dict[str, Any]) -> dict[str, Any]:
    elements = _selected_elements(list(scene.get("elements", [])))
    material = _background_material(scene)
    metals = _metal_finishes(scene)[:2]
    mechanism = _mechanism(scene)
    text = _text(scene)
    mechanism_clause = (
        f"Integrate one physically plausible {mechanism} with visible hardware."
        if mechanism
        else "Use a fixed construction with no decorative moving mechanism."
    )
    text_clause = (
        f"Preserve only this exact text: {json.dumps(text, ensure_ascii=False)}."
        if text
        else "Use no words, letters, captions, logos, or invented signage."
    )
    prompt = " ".join(
        [
            "Edit the supplied photograph into exactly one finished 4:3 landscape product image.",
            "Show one centered manufactured refrigerator magnet as a connected open-contour metallic micro-landscape.",
            f"Build the scene from these source-grounded layers: {', '.join(elements)}.",
            f"Stage it alone on quiet {material} derived from the source's dominant color.",
            f"Use only {', '.join(metals)} with cast thickness, stepped relief, bevels, fine enamel insets, controlled highlights, and a soft contact shadow.",
            mechanism_clause,
            text_clause,
            "Use a slight top-down three-quarter product view and generous breathing room.",
            "Preserve scene identity and spatial relationships while removing clutter and nonessential people.",
            "Do not create a round badge, coin, shield, flat photo cutout, split before/after layout, hand, prop, watermark, or extra magnet.",
        ]
    )
    return {
        "candidate_count": 1,
        "requires_confirmation": False,
        "canvas": "4:3 landscape",
        "scene_elements": elements,
        "background_material": material,
        "metal_finishes": metals,
        "mechanism": mechanism,
        "text": text,
        "prompt": prompt,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile a Scenic Magnet generation brief from a Scene DNA JSON object."
    )
    parser.add_argument(
        "scene_json",
        nargs="?",
        type=Path,
        help="JSON file path; reads stdin when omitted",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = args.scene_json.read_text(encoding="utf-8") if args.scene_json else sys.stdin.read()
    print(json.dumps(compile_brief(json.loads(raw)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

