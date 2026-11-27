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
  model on flat ground, and a parallelogram plan or a ground rising towards the back looks wrong from the side.
- **A painting drawn from above is matched along its slope, not accepted as different.** It draws everything further
  back higher up (a cot's bed, a mat, a field, pebbles, a slab's top, a stall's ground). Measure that slope, set
  `K.oblique` (metres up per metre of depth: a top of known depth D painted h high gives h / D), and build the model
  true and level with every part at its real depth: the kit projects the painting along the slope, so the painted
  tops land on the real tops, and the audit compares the front along it. A thing painted higher because it stands
  further back goes further back (depth = its painted rise / oblique), never up. Lower `K.front_min` (about 0.1) so
  the tops take the painting fully. From the game's near-level camera the model then shows what the real thing would,
  with its painted top on top.
- **A painting drawn from above in perspective also draws the back smaller** (a tray's back pole 0.77 of its front
  pole, papads at the back smaller): the square model's back corners stand out past the painted ones. Never build a
  trapezoid; set `K.converge = (c, xc)` (or `(c, xc, yc)`): at depth y the painting is scaled 1 / (1 + c * y) about
  the vanishing column xc (and row yc), px. A back edge at depth D painted s times the front's length gives
  c = (1 / s - 1) / D; xc is where the front and back edges' middles meet. The kit projects and the audit compares
  with it, like `oblique`.
- **A painter standing a little to one side draws things further back shifted sideways at the same size** (a cart's
  far wheel showing beside its near one under a side-on body). Never turn or skew the model to show it; set
  `K.oblique_x` (metres right per metre of depth: the far wheel painted s m right of the near one over a track of
  T m gives s / T). It combines with `oblique` and `converge`; the audit compares with all three.
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
- Closed parts whose faces pointed inwards (stall_c_3's) render wrong or vanish in the game, which draws only a
  solid's outer faces: the kit turns every inside-out closed part outward when it joins the parts (`_outward`).
- `K.decal(image=...)` cached by `id(image)`, which Python reuses: keyed by content now.
- Review renders ran out of transparent bounces (black shards in crowns): 128 bounces.
- The review's ink outline scaled with model size: it now matches the game's (3-12 mm).
- A Blender object's matrix cannot hold a shear: setting `matrix_world` to a sheared matrix keeps only its location,
  rotation and scale, so the audit's front along the painted slope was not sheared at all (canal_piece_2 judged 0.48
  instead of 0.89). Shear the mesh data (`o.data.transform`) and shear it back after.
- `K.prism` extrudes only along y (`palms_plants.along_x`), `K.thatch`'s hip is symmetric (`market_props.lean_thatch`,
  `lane_houses.hip_thatch`), there is no hipped tiled roof in the kit (`fields.hip_roof`, `lane_houses.hip_roof_tiles`).

## 8. Process

- Measure first: `--grid`, then crop and zoom the parts. Trace shapes off the painting; do not guess.
- Build, then **audit** (`audit.py`), not only review: it renders the exported FBX the game loads, from eight directions
  and above, and compares the front with the painting.
- Look at every view of every sheet, at full size. The six-view review missed things the eight-view audit shows
  (repeating wall stains, stray blocks on a side wall, floating vine patches).
- The audit's flags are hints, not the verdict. A piece painted three-quarters on (the canal benches) is modelled
  turned in plan (level and square, rotated about the vertical, like `stalls_ghx.Turned`) so the side faces the
  painting shows are real side faces; one painted from above also gets `K.oblique` (section 4), so its tops match.
- The game's camera is nearly level: about 3.4 degrees down, 14 m back (`ChaseCamera`). It sees the lane almost
  straight on; a painting's view from above is the painter's, not the game's.
- Fix the cause, rebuild, re-audit. Expect three to six rounds; stop at eight and write down what is left.
- Builds run several at once on a 4-core machine: `KIT_THREADS=1`, one Blender process per builder.
- Edit only your own module; shared fixes go to the kit through the lead.

## 9. From the audit of all 179 (eight directions and above, every model)

Every model was audited from the exported FBX and fixed until its sheet passed or what is left was written down
(`docs/art/model-audit.md`). The rules below are what the eight module audits found more than once; each module's full
notes are in [learnings/](learnings/).

Measuring and placing
- **Measure thin parts from the painting's alpha, row by row** (the opaque run's centre and width), never by eye off
  the grid: spokes, handles, poles, twigs and limbs traced by eye sat 3-12 px off their painted line (red on one side,
  blue on the other). Detect spokes as lines from the hub; fit each wheel's ellipse on its own (two wheels of one
  vehicle are often painted differently).
- **AND every colour mask with the alpha**: transparent pixels keep colour, so fits ran out past torn leaf tips.
- **Subtract the game's ink outline from painted radii** of trunks, stems and posts (about 1.5 x the outline width):
  the painted width includes its ink line, the game draws its own outside the solid.
- **A turned piece (three-quarters on) is solved from its painted posts or corners**: build it square, then turn every
  part and cutter about the nearest corner, T(corner) R(-phi) S_x(1/cos phi) T(-corner) (`fields.turn`,
  `stalls_ghx.Turned`). Front matches rose from 0.57-0.75 to 0.84-0.93.
- **`np.interp` needs increasing sample points** (a hooked stalk gave nonsense); `binary_erosion(iterations=0)` erodes
  everything: guard both.

Ground and lift
- **No earth disc, mound, bed or slab the painting does not have**: they read as plain discs from the side and spill
  below the foot. Where the painting has earth, tile it with the painted soil (quilted) and keep its rim at the foot.
- **Ground painted from above is not a slope to build**: keep it level, with `K.oblique` so its painted top lands on
  the level top; stand goods at their real depth and height (a dais, plinth or raked stand where the painting has
  one, `stalls_ghx.raked_stand`).
- **Cards count for the lift**: end every card and figure polygon at the painted foot, or the lift goes to 0 and the
  model floats by its foot height. Check the record's lift after a build.

Projection
- **Never push the painting straight through a turned body**: it drags one column round the sides (pots, tanks, sacks,
  heaps, cloth stacks). Wrap it by angle: straight on over the front 45-70 degrees (exact, by sine), then the painted
  half laid evenly round (`market_props.wrapped`, `lane_props.proj(wrap=)`, `ground_crops.wrapped`); for a nut lying at
  a slant, round its own axis. Tops pushed through smear: project them on a slant (`proj(top_shear=)`).
- **Projected solids take the painting only on faces turned front and back** (`fields.proj_tiles`, `trees.bark_mix`),
  a tile everywhere else; raise `K.front_min` to 0.55 on trunks, posts, pots and boulders, or the painted ink outline
  runs down their sides as a dark seam.
- **Never project through a pole, and never give it a flat colour** (orange plastic): a squared strip of the painted
  pole's lit middle (`stalls_cdef.pole_tile`).
- **Painted light is not a material**: shadow, lamp glow, a ground shadow band. Crop clear of it.
- **Exclude what stands in front of a recess or a wall by its own pixels** (`lane_houses.exclude_where`), not by a box:
  a box leaves a pale rectangle; nothing leaves a ghost of the kettle, wheel or tyres on the wall behind.
- **Two parts on one spot, or a face coplanar with the wall below it, get no painting** (the bake's visibility pass):
  dedupe, set faces a few mm proud.
- **The cut-out's own holes and halo**: fill specks before tiling (`market_props.ftile`), skin speckled walls
  (`market_props.skin`), remove the halo by a flood from the outside (`ground_crops.halo_free`) so white parts (cotton
  bolls) survive, and take opaque haze between stems off the projection.

Tiles
- **Pick crops by measurement**: fully opaque (check the alpha), lit, no stains, ink lines, neighbours, figures or glow;
  then clean the marks out (`lane_houses.clean_tile`, `fields.delined`). A small clean crop repeats as a quilt grid:
  give it a bigger `size`.
- **Quilt, do not stretch**: a thin painted strip (earth under a prop, a field's top, a plinth) quilted from soft
  feathered patches into a square tile (`lane_props.quilt_tile`, `ground_crops.quilt`, `fields.quilt`); wood and straw
  quilted unturned so the grain stays one way. Mirror-stacked strips make chevrons and herringbones.
- **Regular patterns are sampled once**: brick bonds, coursed stone and striped cloth ghost under `K.tile`'s two
  blended samplings; lay a bond from the painted bricks with its courses on the painted ones (`fields.brick_bond`,
  `pattern_tile`).
- **Stone keeps its painted tones**: grain-only stone goes pale and plain. Sides take the painted side face's darker
  stone. Damage painted on the front (fallen plaster, brick) goes on the back and sides too (`market_props.wall_patch`).
- **Thatch**: straws run down the slope with no rows (`market_props.strand_tile`); soften squared thatch 0.4-0.5.

Geometry
- **Rope beds, nets, straw, stems and wires of thin tubes are all ink**: a sheet with the painted weave, cut-out wisps,
  card ribbons.
- **Corrugated tin goes black from the side** where it is modelled all the way up: corrugate the eave only (9 mm).
- **A thick roof mat's hip ends stand out past the painted hip** by half its thickness: pull them in.
- **Heaps against a wall are their painted outline carried back** with rounded edges, wearing a tile of their goods;
  heaps standing free get pieces or a tile all round, not only on the front. Things hung on a back wall face outwards.
- **Skirtings and dados are cut at doors and alcoves**; a back door copied onto the back wall gets steps.
- **Slabs and beds are one closed mesh** whose walls hang from the top's edge (slits open where a ridged top meets a
  flat end wall); cut ends carry the painted band round at its scale (`ground_crops.side_band`).

Cards
- **Shear the front and back shells of a crown into depth** (`trees.sheared_card`: every vertex at its painted x, z):
  from the front exactly the painting. Turn only the volume cards inside, which the shell hides. Place shell cards by
  coverage until 99.6 % of the painted leaves are covered.
- **Fit frond and leaf widths to the pixels each spine owns** (`palms_plants.fit_widths_owned`), not to the painted
  rachis alone (leaflets hanging below it went missing).
- **Tufts wrap round their own stem** (shallow, about 0.35 deep, one card through it side-on); never crossed cards
  (squeezed doubles from the front), never boxes smaller than the tuft. Grass clumps are their own traced blades.
- **Side-on cards in a bush carry patches from inside the crown**, clamped to the crown's depth; volume cards stay within
  about 30 degrees of the front in sparse plants; copies round the back turn half round, never mirror (ink blots).
- **Masks**: `plant_pixels` keeps cream lime wash and turmeric plaster as petals (use leaves and vivid petals only on
  such walls); drop specks by component size, never by opening (thin tips vanish); subtract the traced wood from the
  leaf mask; put twigs too thin for tubes on the cards.
- **Figures**: `market_props.figures(exact=True)` when two share an outline; turn figure cards 20-30 degrees in plan so
  they are not sticks from the side.
- **Decal quads get an ink frame** in the game: lay patches (cracks, fallen plaster) as cut-out cards instead.
- **Leaves texture 2048** for paintings wider than 1024 px.

Paintings drawn from above (the last round: cot, cart, bicycle, mats, stones, fields, canal pieces, stalls, platform)
- **Fit the painter's view first, then build true numbers.** Take the slope from things of known shape: a disc lying
  flat (papad, plate, lid) is painted `oblique` times as high as it is wide; a top of known depth; two ground contacts
  of one part (a cart's wheels). Fit slope, turn and sizes together against the painted outline and corners (hull
  IoU, Nelder-Mead: `fields`); fit `converge` to straight edges running back. Re-measure the slope once the narrowing
  is known (the back papads read tilted until it was). Front matches rose from 0.10-0.84 to 0.87-0.98.
- **Every painted point goes back through the view before it is built**: depth = painted rise / k (plus its own
  radius for a round foot), real height = painted height - k x that radius; with `converge`, y = 0 on the front-most
  painted faces, sizes scaled by 1 + c y where they stand. Never let a point keep its painted x on every plane: a
  cart's body became a parallelogram in plan.
- **A view setting must hold for the whole painting**: check every far-side feature against it. Where a painter mixed
  views (the cart: body side-on, far wheel drawn as if turned; the cot: back legs drawn longer), compare the true
  candidates by their front match and write the rest down; never skew the model to follow both.
- **Tops along the slope**: keep `front_min` about 0.1 (a level top faces the slope at sin(atan k)); a very shallow
  top (k below about 0.2) takes little of the bake, so give it an un-foreshortened tile of its painted material.
  Ridged tops draw an ink line behind every ridge: keep them smooth, the texture carries the weave.
- **What the projection cannot reach** (ground hidden behind standing things, a mat under its front pole): give it
  the painting along the slope from a source with the standing things inpainted, or reflected back into the painted
  top without its goods (`ground_crops.slope_earth`, `market_props.mat_mirrored`). Exclusions along a slope stretch
  their neighbours by 1/k: exclude with a 3 px margin.
- **A part drawn steeper than the rest** (a tray in its own perspective) takes the painting by its own painted
  corners (`fields.quad_mapped`), excluded from the front projection.
- **Take the painted ink out of what is projected** where the model matches to a few px (`fields.deink`): an ink line
  3 px off an edge reads as a dark stripe along a top seen from the side.
- **No fan-shaped ground, ever**: a ground band painted to the frame's edges becomes a trapezoid under any
  convergence. Build a true rectangle no wider than the frame and accept the red wedges at the band's far ends.
- **Real proportions beat the front match**: a painter often draws an object bigger than the structure round it
  allows (a stool with a 0.74 m seat). Build it at a real size where the painted one stands and accept the red round
  it; put its painted region in `K.front_exclude` and fill the ground there with its own earth, or the projection
  leaves a ghost of it on the ground behind.
- **Decide whether the painting is one camera**: `converge` with a vanishing row is a true perspective (things above
  its horizon seen from below); a painter's view (a roof drawn from above over posts whose horizon runs below it)
  takes width only, `(c, xc)`. Check it by the plan: a mat or bench fitted through it comes out square.
- **Spoked wheels are spoked-disc cards** in the wheel's own plane showing the painting's spokes minus every solid's
  painted stroke (`lane_props.spoke_disc`); tube radius is the painted half width less the ink line.

The audit itself
- **Its flags are hints**: `repeat` fires on a regular brick bond and on real symmetry, `streaks` on real wood grain.
  Judge each view by eye. A model with `oblique` is compared along its painted slope, and with `converge` drawn
  smaller further back (the sheet says so); its `size` is its height along the slope.

## 10. The audit checklist (a model passes only if every answer is yes)

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
