# Learnings: what went wrong building the 179 models, and how to avoid it

Every mistake found while building and reviewing the hand-made models (by the builders, in their reports, and by the
reviews of their sheets), with the rule that avoids it. **Read all of it before building or fixing any model, and check
every model against the audit checklist at the end.** Add to it whenever something new goes wrong.

## 1. The bar

- From the game's camera the model **is** the painting: same outline, every part in its place, nothing smeared, no
  holes, no extra bits.
- From every other side (eight directions round it and from above) it is **the same object, painted by the same hand**:
  solid, believable depth, the painting's own materials continuing round, the details a real one would have there.
- "Naive" (the user's word for rejected attempts) means: a painting extruded or inflated, AI-generated blobs, flat
  plain faces, smeared sides, cards seen edge-on, anything that only works from the front.

## 2. Texturing: projections

- **Projected material on a box's sides or top smears** one column or row of the painting into stripes (`K.projected`
  only works through round things along y). Give box bodies, slabs, walls and tops a **tile** or colour; let the front
  projection paint the front.
- **Round things** (pots, posts, trunks, baskets, heaps, sacks): `K.projected` with `squeeze` 0.9-0.94 about the
  object's own axis and `keep` = the object's own pixels, or the painted ink outline smears over the sides.
- **Leaning poles and trunks** need the projection squeezed about the pole's own slanted axis (`stalls_ghx.pole`,
  `lean_projected`), not the vertical.
- **Long objects** (benches, carts, cots): projection streaks on faces turned to plus or minus x; mirror the hidden half
  or give the ends a box-projected side tile (`lane_props.proj`).
- **The cut-outs keep a pale halo and haze** round their outlines and between leaves. Projected onto geometry near an
  edge it shows as white blotches and scratches (the potter's shed roof, straw cards, a tree's bark in the gaps): clean
  it first (`lane_houses.halo_exclude`, `trees.clear_sky`, `fields.no_halo`, `ground_crops.clean_front`).
- **Things painted in front of a part** (a vendor, a plant, cloth over a post, fronds over a beam) are projected onto it
  by the front projection: put them in `K.front_exclude` or split the part's `keep` boxes round them.
- **A figure's polygon** (`K.figure`) also switches off the front projection for whatever stands in front of the figure
  (a table front, cups): give those parts their own projected material or a panel.
- **A wall behind a figure** needs its own fill (`stalls_cdef.wall_behind`), or a man-shaped tone patch shows on it from
  the side.

## 3. Texturing: tiles and colours

- **Never leave a face a flat plain colour** that is a large surface: it reads as untextured ("plain beige slab",
  "flat orange wedge"). Every wall, roof, slab top, bank and ground patch takes a tile of its painted material.
- **Crop the largest clean patch**: no door, vent, kolam border, neighbour's ladder, shadow, plant or ink line in it, or
  it repeats all over the sides.
- **Fully opaque crops only**: a patch with transparent holes or halo (gaps in a weave, the cut-out edge) turns pale or
  white (fill first: `stalls_cdef.ktile`; check the crop's alpha).
- **Thin strips stretch into streaks** on wide faces (a cornice or coping strip used on a slab top reads as planks):
  mirror-stack the strip into a square first (`market_props.strip_tile`, `fields.squared`, `sq_tile`).
- **Visible repeats**: a stain or a light patch in a tile repeats in a grid across a long wall (the pink house's
  triangles). `soften` 0.3-0.6 pulls the tile to its average; the kit's tile samples twice at different scales, but a
  strong mark still repeats: crop round it, or soften more.
- **Faint repeating bands** on long slopes and backs (earth banks, block courses): use a bigger crop and soften.
- **The painting's shaded side is not a material.** Where a painting shows a building's side wall in shadow (grey-violet),
  that is light, not paint: never take a tile from it, never project it onto a real side wall. Exclude it and give all
  walls the lit plaster or stone; the game's toon light shades them (the granary and field shrine had grey walls).
- **Wrong material for the kind**: check what the painting shows: a thatched roof must be thatch from every side (the
  chariot shed came out as shingles), a stone roof slab stone (the mandapam's was planks).

## 4. Geometry

- **True, level, square.** No shears, slopes or skews to make a perspective painting line up: the game stands every
  model on flat ground, and a parallelogram plan or a ground rising towards the back looks wrong from the side. Where
  the painting draws a side face or a top in perspective, exclude those pixels and accept that the front differs there.
- **The base sits on the ground** (z = 0): no floating, no tilted ground patch to match a painted foot, no raised mound
  under a prop unless the painting has one. Most paintings stand the foot 2-5 cm above their bottom edge (the shadow is
  painted below it); the record's `lift` (the lowest point, up to 10 cm) sets the model down onto the ground in the
  game, so keep the painting's frame and do not shift the model. More than 10 cm off the ground is floating.
- **Recesses** (doors, windows, vents, niches) are cut deeper than the panel inside them, or the faces fight.
- **`K.cut` cutters are not parts**: if parts are turned or moved after cutting, move the cutters with them
  (`fields.with_cutters`), or the holes land in the wrong place.
- **Real thickness**: walls, broken walls, cloth that is seen edge-on, mats, signs. A wall seen from the side as a thin
  slab is wrong (the ruined pillar needed bricks running through its whole thickness).
- **Hidden backs are still seen**: the back of every building has its own door or window, side walls a window, backs of
  stalls posts, crates, the back of the counter; a mandapam is pillared all round; a pump house has a vent. Plain backs
  are naive.
- **Thin tubes become black lines**: the game draws an ink outline (up to 12 mm) round every solid; a stalk or wire
  thinner than about 2 cm is all outline. Make thin things cards, or thicker and coloured.
- **Spokes**: as tubes they read dark and dense; as alpha cards 1-2 px wide they break up. Use few, thicker spokes or a
  spoked disc.
- **Fuse thick wood only** (`K.fuse` voxel remesh bloats thin limbs and is slow); leave twigs as tubes.
- **Generic geometry where the painting has specific shapes** (generic fish, generic boulders, generic banana hands):
  trace the painted shapes (`stalls_cdef.blobs`, `on_heap`, `trees.Wood`).
- Face budgets: props about 6k (8k for detailed ones), buildings and stalls 20k, trees 25k including cards. A blob card
  is one 9-sided face but about 7 triangles.
- Drop bottom faces of parts standing on the ground (`lane_houses.drop_ground_faces`): they waste atlas space.

## 5. Cards (leaves, fronds, flowers, grass, figures)

- **Cards show nothing outside their rule boxes**, and overlapping `leaves_only` rules combine pixel by pixel: two
  overlapping rules can erase each other, and a figure box overlapping a leaf box wipes pixels out. Merge every rule
  into one mask at the end (`stalls_cdef.unify_cards`, `lane_props.card_mask_all`).
- **Rectangular cards give square, cut-off silhouettes** from the side, back and above. Use ragged blob cards
  (`trees.blob_card`), keep every card's box inside the painted foliage, use smaller cards near the edge, and make the
  rule box larger than the plant so the mask, not the box, does the cutting.
- **Card normals point out from the crown's middle** so the toon light shades the crown as one mass.
- **Leaf masks**: `plant_pixels` misses olive and khaki leaves (`lane_houses.olive_leaf_pixels`); `foliage_pixels`
  excludes bark and fruit (model the fruit).
- **Cards seen edge-on** are slivers (colocasia leaves from the side, sorghum heads, the clothesline's cloths): cross
  them, curve them, or make them solid.
- **Flat ribbons look like paper**: garlands are round strands of flower heads (`stalls_ghx.bead_garland`), not flat
  strips with cut ends.
- **People and animals** stay painted cut-outs inside the model: `K.figure` or, when they overlap, `market_props.figures`
  (one shared mask, so neither slices the other: the coconut cart's bullock head was cut in two). Never leave them
  out (the hens basket is the hens obstacle; the kavalai's bullocks pull the rope). Leaves texture 2048 for figures.
- Cards past the painting's edge used to wrap round to the other side: `card_from_painting` clamps them now.

## 6. Flat and standing ground pieces

- Pieces painted from above (kolams, prints, leaves, twigs, ruts, cracked mud) are `kind="flat"`: built standing like
  their painting, the game lays them face up.
- Pieces painted from the side (tufts, weeds, pebbles, husks, coconuts) are props: the game stands them.

## 7. The kit (fixed bugs: do not reintroduce)

- `_smart_uv` ran with aspect correction, squashing the atlas into a sliver for wide paintings: `correct_aspect=False`.
- `Kit.rng` was seeded from the salted `hash()`, so builds differed every run: `zlib.crc32(name)`.
- The UV packer (`pack_islands`) stretched each island by the aspect of its faces' material image, whatever
  `correct_aspect` says, so a wide painting as a part's material squashed whole atlases one way (h7_5 3.3:1, stall_d_1,
  field_tree_6, hens_basket 1.7:1): `_smart_uv` now points every face at an image-less material while it unwraps and
  packs. The audit's `uv_squash` (the area-weighted median stretch, above 1.3) catches it.
- The unwrap's 60-degree angle limit projected a bevelled box's big faces along its 45-degree bevel, squashing half of
  it 1.41:1 (the parapet): `_smart_uv` unwraps at 44 degrees, which also halves the stretch over pots and posts.
- `K.tile`'s box projection maps a top face's depth with the crop's width, so a wide, short crop stretched 2-4 times
  front to back on every top (slab tops, decks and tables read as planks): it now repeats the seamless crop into a
  near-square image first. Modules' own squaring helpers (`sq_tile`, `strip_tile`, `squared`) still work.
- `K.decal(image=...)` cached by `id(image)`, which Python reuses: keyed by content now.
- Review renders ran out of transparent bounces (black shards in crowns): 128 bounces.
- The review's ink outline scaled with model size: it now matches the game's (3-12 mm).
- `K.prism` extrudes only along y (`palms_plants.along_x`), `K.thatch`'s hip is symmetric (`market_props.lean_thatch`,
  `lane_houses.hip_thatch`), there is no hipped tiled roof in the kit (`fields.hip_roof`, `lane_houses.hip_roof_tiles`).

## 8. Process

- Measure first: `--grid`, then crop and zoom the parts. Trace shapes off the painting; do not guess.
- Build, then **audit** (`audit.py`), not only review: it renders the exported FBX the game loads, from eight directions
  and above, and compares the front with the painting.
- Look at every view of every sheet, at full size. The six-view review missed things the eight-view audit shows
  (repeating wall stains, stray blocks on a side wall, floating vine patches).
- The audit's flags are hints, not the verdict. A piece painted three-quarters on or in perspective (the canal
  benches) cannot match its painted top when built true and level: model it turned in plan (level and square, rotated
  about the vertical, like `stalls_ghx.Turned`) so the side faces the painting shows are real side faces, and accept
  what is left.
- Fix the cause, rebuild, re-audit. Expect three to six rounds; stop at eight and write down what is left.
- Builds run several at once on a 4-core machine: `KIT_THREADS=1`, one Blender process per builder.
- Edit only your own module; shared fixes go to the kit through the lead.

## 9. The audit checklist (a model passes only if every answer is yes)

Front (the painting's frame, and the difference map):
1. The outline matches: no red (missing) and no blue (extra) areas beyond a thin edge.
2. Every painted part is in its place, at its size; nothing smeared, doubled or misplaced; no yellow patches beyond
   small line misalignments.
3. People and animals painted in it are there, whole.

Every one of the eight side views and the view from above:
4. No smears or streaks: no surface where the painting is dragged across into stripes.
5. No large flat plain faces: every big surface carries its painted material.
6. No visibly repeating texture (the same stain or patch in a grid).
7. No wrong materials: walls the lit plaster, stone, mud or brick of the painting; roofs what the painting shows.
8. No holes, see-through gaps (unless real), inside-out faces, black shards or stray dark areas.
9. No floating or loose parts, nothing sunk into the ground, the base flat on the ground.
10. Thin parts read as what they are: no black-line stalks, no paper-thin slabs where a solid is meant.
11. Cards: leafy outlines, no straight cut edges or square corners, no slivers dominating a view.
12. The back and sides have what a real one would have (doors, windows, posts, goods, foliage), not a plain block.
13. Proportions are real: depth believable for the thing, nothing stretched or squashed.
