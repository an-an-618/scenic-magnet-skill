# Scenic Magnet behavior scenarios

These scenarios define the public behavior of `$scenic-magnet-v1`. They are deliberately source-grounded: the skill may simplify and redesign relationships, but it must not invent the identity of a place.

| ID | Source situation | Expected behavior | Failure mode caught |
| --- | --- | --- | --- |
| SM-01 | A landmark scene with several recognizable parts | Distill 2–5 connected elements into one open-contour micro-landscape magnet | Reducing the scene to a single badge-like icon |
| SM-02 | A transit scene with a vehicle, track/base, and city context | Preserve the vehicle plus a structural base/context layer | Pasting a flat photo of the vehicle onto a plaque |
| SM-03 | A natural scene with terrain, water, and a formation | Preserve the terrain/water/formation relationship without inventing a landmark | Hallucinating buildings, signs, or attractions |
| SM-04 | A scene with clear motion semantics | Add at most one plausible scene-supported mechanism | Adding multiple novelty mechanisms |
| SM-05 | A still scene without motion semantics | Omit the mechanism | Forcing a spinner, slider, or hinge onto every result |
| SM-06 | A scene with one dominant color | Use that hue family for one quiet tactile backing material | Choosing an unrelated or visually noisy background |
| SM-07 | Text is absent or unreadable | Omit text | Guessing a place name or fabricating signage |
| SM-08 | Any valid user photo | Generate one finished 4:3 landscape product image directly | Returning candidates or asking for confirmation |

