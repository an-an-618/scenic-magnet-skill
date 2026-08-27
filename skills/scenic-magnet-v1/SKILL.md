---
name: scenic-magnet-v1
description: Use when a user supplies a photo and asks for a refrigerator magnet, souvenir magnet, metallic scenic miniature, travel keepsake, landmark relief, or photo-to-product transformation.
---

# 景铸 · Scenic Magnet

## Overview

Transform a source photo into one manufactured micro-landscape magnet. Preserve the place through decisive spatial relationships, not literal photo reduction.

## Output contract

Produce exactly one finished image with this shape:

- 4:3 landscape product photograph; no candidate sheet or confirmation gate.
- One central open-contour fridge magnet built from 2–5 source-grounded scene elements.
- One quiet tactile background whose hue comes from the source's largest effective color.
- At most two coherent metal finishes with visible thickness, relief, bevels, highlights, and contact shadow.
- One mechanism only when the source naturally supports motion or reveal; otherwise use none.
- No text by default. Preserve exact user text, or clearly legible identity-bearing source text, without completion or translation.

The result is a connected miniature landscape, not a round badge, coin, shield, flat photo cutout, split Before/After composition, or framed screenshot.

## Workflow

1. Inspect every supplied source with image viewing at original detail. If a required source is unavailable, ask for that file; otherwise continue without questions.
2. Read [scene-distillation.md](references/scene-distillation.md). Build the Scene DNA Card internally and choose the 2–5 elements that carry identity and depth.
3. Read [material-and-mechanism.md](references/material-and-mechanism.md). Choose one backing material, one metal family, an open silhouette, and zero or one semantically justified mechanism.
4. Read [quality-gate.md](references/quality-gate.md). Compile a positive edit prompt and call the built-in image-generation tool once with the source image attached. Generate directly; do not return candidates or ask for approval.
5. Inspect the result at normal and thumbnail scale. If a local result path exists, run `scripts/analyze_magnet_frame.py RESULT` for framing evidence.
6. If one observed failure blocks the contract, make one targeted edit that names only that failure and preserves everything else. Do not restart for speculative improvement.
7. Return the finished preview. Do not copy source photos, generated previews, or private paths into the repository or publish them without per-image authorization.

## Quick reference

| Decision | Default |
| --- | --- |
| Scene | 2–5 connected elements |
| Background | one dominant-color tactile material |
| Metal | one family, maximum two finishes |
| Mechanism | none unless motion/reveal is intrinsic |
| Text | none unless exact and reliable |
| People | remove; retain only identity-essential tiny enamel silhouettes |
| Camera | slight top-down 3/4; near-front only for strong symmetry |
| Correction | maximum one observed, targeted fix |

## Common mistakes

- Preserve every object and the magnet becomes a miniature photograph. Reduce to the identity-bearing relationship.
- Add a novelty hinge or spinner without scene semantics and the product becomes gimmicky. Use fixed relief instead.
- Render metal as smooth gray plastic. Specify cast edge thickness, machining variation, enamel recesses, highlights, and contact shadow.
- Guess a location label. Omit uncertain lettering.
