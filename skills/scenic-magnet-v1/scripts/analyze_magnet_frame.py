#!/usr/bin/env python3
"""Inspect Scenic Magnet framing and background quietness without editing pixels."""

from __future__ import annotations

import argparse
from collections import deque
import json
import math
from pathlib import Path
import statistics
from typing import Iterable

from PIL import Image, ImageFilter


TARGET_RATIO = 4 / 3
RATIO_TOLERANCE = 0.015
COLOR_DISTANCE_THRESHOLD = 42.0
BACKGROUND_VARIANCE_LIMIT = 32.0
MIN_FOREGROUND_FRACTION = 0.40
MAX_FOREGROUND_FRACTION = 0.70
MIN_EDGE_CLEARANCE = 0.02
MIN_COMPONENT_PIXELS = 9
MIN_COMPONENT_FRACTION = 0.0002


def _pixels(image: Image.Image) -> Iterable[tuple[int, int, int]]:
    if hasattr(image, "get_flattened_data"):
        return image.get_flattened_data()
    return image.getdata()


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


def _neighbors(
    index: int, x: int, y: int, width: int, height: int
) -> Iterable[int]:
    if x > 0:
        yield index - 1
    if x + 1 < width:
        yield index + 1
    if y > 0:
        yield index - width
    if y + 1 < height:
        yield index + width


def _remove_small_components(mask: list[bool], size: tuple[int, int]) -> list[bool]:
    width, height = size
    minimum = max(
        MIN_COMPONENT_PIXELS,
        math.ceil(width * height * MIN_COMPONENT_FRACTION),
    )
    visited = bytearray(len(mask))
    cleaned = [False] * len(mask)

    for start, active in enumerate(mask):
        if not active or visited[start]:
            continue
        visited[start] = 1
        queue = deque([start])
        component: list[int] = []
        while queue:
            index = queue.popleft()
            component.append(index)
            x, y = index % width, index // width
            for neighbor in _neighbors(index, x, y, width, height):
                if mask[neighbor] and not visited[neighbor]:
                    visited[neighbor] = 1
                    queue.append(neighbor)
        if len(component) >= minimum:
            for index in component:
                cleaned[index] = True
    return cleaned


def build_foreground_mask(
    image: Image.Image, background: tuple[int, int, int]
) -> list[bool]:
    raw = Image.new("L", image.size)
    raw.putdata(
        [
            255 if color_distance(pixel, background) >= COLOR_DISTANCE_THRESHOLD else 0
            for pixel in _pixels(image)
        ]
    )
    filtered = raw.filter(ImageFilter.MedianFilter(size=5))
    mask = [value >= 128 for value in _pixels(filtered)]
    return _remove_small_components(mask, image.size)


def mask_bbox(mask: list[bool], size: tuple[int, int]) -> list[int] | None:
    width, _ = size
    active = [index for index, value in enumerate(mask) if value]
    if not active:
        return None
    xs = [index % width for index in active]
    ys = [index // width for index in active]
    return [min(xs), min(ys), max(xs), max(ys)]


def _scale_bbox(
    bbox: list[int] | None,
    analysis_size: tuple[int, int],
    original_size: tuple[int, int],
) -> list[int] | None:
    if bbox is None:
        return None
    analysis_width, analysis_height = analysis_size
    original_width, original_height = original_size
    scale_x = original_width / analysis_width
    scale_y = original_height / analysis_height
    return [
        math.floor(bbox[0] * scale_x),
        math.floor(bbox[1] * scale_y),
        min(original_width - 1, math.ceil((bbox[2] + 1) * scale_x) - 1),
        min(original_height - 1, math.ceil((bbox[3] + 1) * scale_y) - 1),
    ]


def analyze_image(path: Path | str, max_edge: int = 640) -> dict[str, object]:
    source_path = Path(path)
    with Image.open(source_path) as source:
        original = source.convert("RGB")

    analysis = original.copy()
    analysis.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    border = sample_border_rgb(analysis)
    background = median_rgb(border)
    variance = statistics.fmean(
        color_distance(pixel, background) for pixel in border
    )
    mask = build_foreground_mask(analysis, background)
    analysis_bbox = mask_bbox(mask, analysis.size)
    bbox = _scale_bbox(analysis_bbox, analysis.size, original.size)
    if analysis_bbox is None:
        bbox_fraction = 0.0
        clearance = 1.0
    else:
        bbox_width = analysis_bbox[2] - analysis_bbox[0] + 1
        bbox_height = analysis_bbox[3] - analysis_bbox[1] + 1
        bbox_fraction = bbox_width * bbox_height / (analysis.width * analysis.height)
        clearance = min(
            analysis_bbox[0] / analysis.width,
            analysis_bbox[1] / analysis.height,
            (analysis.width - analysis_bbox[2] - 1) / analysis.width,
            (analysis.height - analysis_bbox[3] - 1) / analysis.height,
        )

    aspect_ratio = original.width / original.height
    is_4_3 = abs(aspect_ratio - TARGET_RATIO) <= RATIO_TOLERANCE
    warnings: list[str] = []
    if not is_4_3:
        warnings.append("not_4_3")
    if bbox_fraction < MIN_FOREGROUND_FRACTION:
        warnings.append("magnet_too_small")
    if bbox_fraction > MAX_FOREGROUND_FRACTION:
        warnings.append("magnet_too_large")
    if clearance < MIN_EDGE_CLEARANCE:
        warnings.append("foreground_touches_edge")
    if variance > BACKGROUND_VARIANCE_LIMIT:
        warnings.append("background_not_quiet")

    return {
        "width": original.width,
        "height": original.height,
        "aspect_ratio": round(aspect_ratio, 6),
        "is_4_3": is_4_3,
        "background_rgb": list(background),
        "background_edge_variance": round(variance, 3),
        "foreground_bbox": bbox,
        "foreground_bbox_fraction": round(bbox_fraction, 6),
        "foreground_edge_clearance": round(clearance, 6),
        "warnings": warnings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect 4:3 framing, approximate magnet occupancy, edge clearance, "
            "and background quietness without editing the source image."
        )
    )
    parser.add_argument("image", type=Path)
    parser.add_argument("--max-edge", type=int, default=640)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(
        json.dumps(
            analyze_image(args.image, max_edge=args.max_edge),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
