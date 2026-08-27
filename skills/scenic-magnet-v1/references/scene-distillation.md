# Scene distillation

## Scene DNA Card

Write this internal card before prompting image generation:

```text
scene_type:
identity_anchor:
spatial_spine:
depth_layers:
dominant_color:
temperature:
candidate_elements: [{name, importance, identity_role, depth_role}]
motion_semantics:
legible_identity_text:
text_confidence:
removals:
```

Do not show the card to the user unless asked.

## Identity lock

Preserve the source's place identity through observable facts:

- the primary landmark, vehicle, terrain, facade, tree line, shoreline, or sign shape;
- the relationship between foreground base, middle identity layer, and rear silhouette;
- the dominant directional gesture: rising, curving, cascading, receding, or enclosing;
- distinctive proportions and color blocks that remain readable at small scale.

Do not invent famous architecture, mountains, signs, vehicles, people, or location names. Simplification may remove detail; it may not substitute identity.

## Selecting 2–5 elements

Rank visible elements by four questions:

1. Would the location become harder to recognize without it?
2. Does it supply a missing depth plane or physical base?
3. Does it create a useful contour, path, hinge, rail, or axis?
4. Can it survive as cast relief at thumbnail size?

Choose the smallest set that answers identity plus spatial depth. Default to three or four. Use two for extremely iconic simple scenes and five only when each layer remains separable.

### Typical combinations

| Source | Connected micro-landscape |
| --- | --- |
| Transit street | vehicle + track/road base + facade band + overhead line |
| Coast | rock shelf + wave layer + headland + one human-scale marker |
| Mountain | foreground trail + main formation + cloud/sun accent |
| Storefront | facade + doorway + sign canopy + pavement edge |
| Garden avenue | path + selected trees + cyclist/pedestrian scale cue |

## Composition

Build one connected object with a source-derived outer contour. Let the foreground act as the physical base, the identity anchor occupy the middle relief, and the rear layer complete the silhouette. Overlap layers with real stepped depth instead of placing isolated charms on a plaque.

Keep nonessential people, traffic, wires, advertisements, furniture, and repeated vegetation out. Retain a person only when the human figure is essential to the scene's identity or scale; render that figure as a tiny enamel silhouette, never a portrait.

## Thumbnail test

Mentally reduce the magnet to 15% size. The identity anchor, depth order, and outer contour must still read. If not, remove one secondary element or increase relief separation before adding detail.

