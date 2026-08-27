# 景铸 · Scenic Magnet

Turn a supplied photograph directly into a 4:3 product image of a premium metallic micro-landscape refrigerator magnet.

Scenic Magnet does not shrink the whole photograph into a badge. It identifies the scene's spatial DNA, keeps 2–5 identity-bearing elements, reconnects them as stepped metal relief, and stages the object on one quiet tactile backing derived from the source's dominant effective color.

## What it makes

- One finished 4:3 landscape image, with no candidate or confirmation turn.
- One connected, source-derived magnet with an open silhouette rather than a default coin, shield, or plaque.
- Cast thickness, beveled edges, enamel recesses, controlled metal highlights, and a real contact shadow.
- A single scene-matched backing material such as silk paper, felt, corrugated art paper, woven paper, linen paper, or museum board.
- An optional rotating, sliding, opening, or pulling mechanism only when the source scene naturally supports it.
- No text by default; only exact user text or clearly legible identity-bearing source text may survive.

## How it works

```text
photo
→ read the Scene DNA
→ select 2–5 connected identity layers
→ choose one dominant-color material and one metal family
→ add zero or one scene-supported mechanism
→ generate one 4:3 product image directly
→ inspect at normal and thumbnail scale
→ correct at most one observed failure
```

The source remains the authority. The skill may simplify, merge, or remove detail, but it must not invent a landmark, location name, vehicle, building, or portrait.

## Install locally

Copy the installable skill from this checkout:

```bash
mkdir -p ~/.codex/skills
cp -R skills/scenic-magnet-v1 ~/.codex/skills/
```

Restart Codex if the skill does not appear immediately.

The optional frame analyzer uses Pillow. Image generation can continue with visual QA when Pillow is unavailable; do not install dependencies silently during a user task.

## Use

Upload a photo and invoke:

```text
Use $scenic-magnet-v1 to turn this photo into a scenic metal fridge magnet.
```

The skill generates the finished preview directly. It does not ask the user to choose among candidates.

## Repository

```text
skills/scenic-magnet-v1/   installable skill
tests/                      deterministic compiler and analyzer tests
evals/                      behavioral scenarios; local media stays ignored
docs/                       design and implementation plans
```

## Privacy and example media

Source photos and generated previews are used only for the requested task. They are not copied into the repository, committed, published, or reused as showcase media without explicit per-image authorization.

Permission to test an image locally is not permission to publish it. Before/after showcase rights are separate from the repository's code and documentation.

