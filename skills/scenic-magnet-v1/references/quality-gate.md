# Generation and quality gate

## Prompt compiler

Construct the edit prompt in this order:

1. **Task and canvas:** exactly one finished 4:3 landscape product image.
2. **Object:** one connected open-contour metallic micro-landscape refrigerator magnet.
3. **Scene layers:** name the selected 2–5 source-grounded elements in depth order.
4. **Backing:** name one dominant-color tactile material.
5. **Manufacture:** name one metal family, cast thickness, stepped relief, bevels, enamel recesses, controlled highlights, and contact shadow.
6. **Mechanism:** name one supported mechanism with visible hardware, or state fixed construction.
7. **Text:** quote exact allowed text, or state no words/letters/signage.
8. **Camera:** slight top-down three-quarter product view with generous breathing room.
9. **Identity:** preserve source proportions and spatial relationships; remove clutter.
10. **Exclusions:** no badge default, flat photo, split layout, extra magnet, hand, prop, watermark, or invented place identity.

`scripts/compile_magnet_brief.py` can compile the same branches from a Scene DNA JSON card when a deterministic audit trail is useful.

## Positive visual target

The image should read first as a premium manufactured souvenir, second as a miniature landscape, and third as a faithful distillation of the source. Metal edges catch narrow highlights; enamel sits inside shallow wells; layer overlaps cast small shadows; the backing texture is visible only on inspection.

## Inspection sequence

Inspect the generated result twice:

### Normal scale

- Is there exactly one magnet and one quiet background?
- Are 2–5 scene elements connected into one object?
- Does the spatial order match the source?
- Does the silhouette come from the scene rather than a badge template?
- Do thickness, relief, bevel, metal variation, and contact shadow read physically?
- Is any mechanism mechanically plausible and scene-supported?
- Is every visible letter authorized and exact?

### Thumbnail scale

- Does the primary identity anchor remain obvious?
- Can foreground, middle, and rear relief layers still be separated?
- Does the magnet dominate without crowding the frame?
- Is the material background quiet enough to disappear behind the object?

## Deterministic frame check

When the generated image has a local path, run:

```bash
python3 scripts/analyze_magnet_frame.py /absolute/path/to/result.png
```

Interpret warnings as evidence, not automatic truth. `not_4_3`, `magnet_too_small`, `magnet_too_large`, `foreground_touches_edge`, and `background_not_quiet` identify frame-level risks; visual judgment still decides whether a correction is warranted.

## One-correction rule

Make at most one corrective edit. Name only the observed failure and lock successful attributes, for example:

```text
Preserve the selected scene elements, metal family, open contour, backing material,
camera, and all source identity. Correct only the weak physical depth: increase cast
edge thickness and stepped relief separation, with narrow bevel highlights and a
clear soft contact shadow. Change nothing else.
```

If the result remains imperfect after that edit, return the stronger version and describe the residual issue briefly. Do not enter an unbounded regeneration loop.

