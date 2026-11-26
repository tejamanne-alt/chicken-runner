# The model kit: every piece hand-built in Blender, textured from its painting

Each painted piece of scenery (not the people, not the animals) is modelled part by part in a Blender script, the way a
3D artist would build it from the painting: real walls, roofs, posts, steps, pots, cloth, baskets and heaps of goods,
leaves and flowers as cut-out cards. The model is textured from the painting itself, so it has the painting's own
colours, brushwork and light, and from the game's camera it **is** the painting; from every other side it is the same
thing, painted by the same hand.

```bash
ArtSource/blender/venv/bin/python ArtSource/tools/kit/build.py --only house_pink --review /tmp/review   # one model
ArtSource/blender/venv/bin/python ArtSource/tools/kit/build.py --only house_pink --grid /tmp/grid       # measuring grid
ArtSource/blender/venv/bin/python ArtSource/tools/kit/build.py --module lane_houses --all --review /tmp/review
ArtSource/blender/venv/bin/python ArtSource/tools/kit/build.py --merge          # records into models.json
```

(`ArtSource/blender/venv` is any Python with `bpy` 5.x, numpy, scipy and Pillow.) Outputs:
`Assets/ChickenRunner/Art/Models/<folder>/<name>.fbx` + `<name>.jpg` (the baked atlas) + `<name>_leaves.png` (when it has
cards), and `ArtSource/models_kit/<name>.json`. `--merge` puts the records in `models.json` with `"source": "blender"`;
`ArtModels` then stands the model wherever the game used the card.

## How a model is made

1. **Measure the painting.** `--grid DIR` writes `DIR/<name>_grid.png`: the cut-out with a labelled pixel grid. Look at it
   (zoom into crops when parts are small) and write down every part: its box in pixels, its shape, what it is made of.
2. **Write the builder** in your category module: `@model("<name>", "<folder>", kind=..., atlas=...)` on a function
   `fn(K)`. Work in the painting's pixels: `P = K.paint`; `P.x(px)`, `P.z(py)` turn a pixel into metres in the model
   (x across, z up; the painting's frame spans x -W/2..W/2, z 0..H at y = 0); `P.m(dpx)` a length; `P.pt(px, py, y)` a
   point. **y is depth: the front is -Y (towards the camera), the back +Y.**
3. **Build it.** `--review DIR` writes `DIR/<name>.jpg`: the painting, the model from the front at the same size, then
   from the front-left, front-right, side, back and above, shaded like the game (toon light, ink outline).
4. **Compare and fix** until both hold:
   - the model's front is the painting: same outline, every part in its place, nothing smeared, no holes;
   - every other view looks like the same object painted by the same artist: solid, believable depth, the same
     materials continuing round the sides and back, details where a real one would have them (a back door, a side
     window, posts at the back corners, the far side of a stall), nothing flat, stretched, striped or repeating.
   Expect three to six rounds per model. Look at every sheet you make.

## What the kit does for you (kitlib.py)

**Texturing, baked into one atlas per model** (`finish()`): (1) each part's own material; (2) the painting projected
from the front onto every surface the camera sees squarely and unblocked, where the painting is opaque; (3) a little
ambient occlusion. So model the shapes faithfully and give every part a material that matches its painted surface; the
front takes care of itself.

Materials (all return a material to pass to a primitive):
- `K.tile(box_px, size=None, vary=0.0, soften=0.0)`: the painting inside `box_px` made seamless and box-projected at its
  painted scale. For walls, roofs, thatch, wood, cloth, stone, earth: the side and back of a thing. Pick the **largest
  clean patch** of that surface (no door, no shadow, no plant, no neighbour); `soften` 0.3-0.6 pulls its stains towards
  its average so it doesn't repeat visibly (walls want it); `vary` adds soft painterly variation.
- `K.colour(box_px or (r, g, b) linear, vary=0.06, pct=50)`: a flat colour picked from the painting (median of the box,
  or a percentile with `pct`), softly varied. For small parts, trims, insides, iron.
- `K.projected(axis_x=metres, squeeze=0.93, keep=[boxes], exclude=[boxes], inset=4)`: the painting projected straight
  through the model along y, so the back of a round or turned thing (pot, post, trunk, basket, heap, sack) shows the
  same bands and colours as its front. `keep`: only the object's own pixels; `exclude`: things painted in front of it
  (grass, a person); everything else is filled from the nearest kept pixel. Use this for anything round.
- `K.decal(box_px)` + `K.quad(corners, mat)` or `K.panel(box_px, y, depth=0)`: a rectangle of the painting on a face:
  repeat a painted door, window, sign or shutter on the back or side, or make a painted board a real slab.

Geometry (metres; every call returns the part, a Blender object):
- `K.box(x0, x1, y0, y1, z0, z1, mat, bevel=0)`, `K.block(cx, cy, cz, sx, sy, sz, mat, rot=(deg, deg, deg), bevel,
  jitter)`, `K.prism(outline[(x, z)], y0, y1, mat)` (gables, arches, cut-out profiles extruded in depth)
- `K.lathe(profile[(r, z)], mat, segments, centre=(x, y, z), wobble, scale_y, cap)`: pots, pillars, posts, lamps,
  vessels, baskets, haystacks, domes. Trace the profile off the painting's outline.
- `K.tube(points[(x, y, z)], radius or [radii], mat, segments, taper)`: bamboo, poles, rope, rails, wires, branches,
  garlands, handles.
- `K.sheet(fn(u, v) -> (x, y, z), nu, nv, mat, thickness)`: any curved surface; `K.cloth(...)` (awnings that sag),
  `K.tiled_roof(...)` (half-round country tiles), `K.thatch(...)` (lumpy straw with a ragged fringe, `hip`),
  `K.corrugated(...)` (tin sheet), `K.grid_plane(...)` (mats, ground).
- `K.boulder(cx, cy, cz, sx, sy, sz, mat)` (stones, rocks), `K.fuse([parts], voxel, faces)` (melt a trunk, its limbs
  and roots into one seamless surface), `K.cut(part, x0, x1, y0, y1, z0, z1)` (a recess: doors, windows, vents, niches;
  cut deeper than what you put inside it, never flush), `K.copy(part, dx, dy, dz, rot_z)`, `K.mirror_x(part)`.
- Cards (cut-out, both sides, drawn from the painting with its alpha): `K.card_from_painting(box_px, centre, yaw,
  pitch, normal=...)` puts the painting inside `box_px` where it is painted (centre `P.pt` of the box's middle) so from
  the front it lines up; `K.canopy(region_px, depth, n, size_px, yaw, pitch, centre_px)` fills a crown, bush or flower
  heap with such cards through its depth. `K.leaves_only(box_px, keep=plant_pixels|foliage_pixels|fn)` makes the cards
  show only the plant inside that box (not the wall or ground painted behind it); with any `leaves_only` rule, cards
  show **nothing** from outside the rule boxes. `foliage_pixels` is for tree crowns (leaves only, no bark, no fruit:
  model the fruit). Use cards for leaves, fronds, flowers, grass, straw tufts, hanging garlands of loose flowers,
  feathers of a kite's tail: anything thin and ragged. Never for walls, posts or goods.
- Model settings: `K.front_exclude = [boxes]` (parts of the painting NOT to project from the front: a person or animal
  standing in front, a neighbour's ladder at the edge), `K.front_projection = False` (a model of only projected round
  parts), `K.front_min` (default 0.25), `K.ao` (default 0.45).

## Conventions

- `kind="building"`: its front wall on y = 0, everything else behind it (+Y), porches, steps and pots out in front
  (-Y). `kind="prop"`: centred on y = 0. `kind="flat"`: lies on the ground (kolams, prints, ruts: a thin slab, the
  painting on top, its edges a little rough).
- Real size comes from the painting's frame (`P.W`, `P.H` metres): never rescale. Choose depths that real things have
  (a village house 4-6 m deep, a stall 1.5-2.5 m, a pot as deep as it is wide, a tree crown about 0.75 of its width).
- `atlas=1024` for props, `2048` for buildings, stalls and trees. Faces: props under about 6k, buildings and stalls
  under 20k, trees under 25k with cards.
- **People and animals are not modelled.** A stall with a vendor: build the stall, its counter, mat and goods; put the
  vendor's box in `K.front_exclude`, and model what would be behind them (the mat, the goods, the floor). A cart with
  bullocks: the cart only. A basket of hens: the basket, its straw, no hens.
- No text, logos or invented signage beyond what is painted.

## Lessons already learnt

- A recess (door, window) must be cut deeper than the panel inside it, or the two faces fight and the painting misses.
- A tile with a door, a vent, a kolam border or a neighbour's ladder in it repeats that thing all over the sides:
  crop around it.
- A card whose box runs past the painting's edge used to wrap round to the other side: `card_from_painting` now clamps.
- A round thing's painted outline smears over its sides unless the projection is squeezed (`squeeze` ~0.9-0.94) and
  its `keep` box is the object alone.
- Pure black shards in a review of a tree were Cycles running out of transparent bounces (fixed in review.py), not the
  model.
- Trunks of many tubes leave seams and ink in their crotches: `K.fuse` them.

## Examples

- `lane_props.py`: `pot_stack` (turned shapes with `projected`, a ground patch with pebbles and grass cards).
- `lane_houses.py`: `house_pink` (a flat-roofed house: walls, plinth, cornice, coping, corner pillars, recessed door in
  its frame, vents, sunshade, garland, steps, a back door, barred side windows, a potted hibiscus and a jasmine vine
  as masked cards).
- `trees.py`: `tree_mango_2` (a fused trunk of painted limbs, a card crown, modelled mangoes, boulders, undergrowth).
