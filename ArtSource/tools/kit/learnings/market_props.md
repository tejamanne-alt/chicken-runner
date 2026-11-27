# New lessons from the market_props audit

- **A straight projection through a turned body drags one column across its sides.** `K.projected` (even squeezed)
  maps every point of a pot's or tank's side, from about 60 to 120 degrees round, to the same few columns near the
  painted edge: from the side the body shows horizontal streaks, and any dark reflection or highlight painted near the
  edge becomes a smeared oval. Use `market_props.wrapped()`: it is the straight projection up to 70 degrees either side
  of the front (so it meets the painting's front with no seam), and beyond that lays the painted half evenly round the
  sides and the back.
- **Model the top of a tank or vessel as painted, not as a wall carrying the painted top.** A cylinder taken straight
  up to the lugs' height wore the painted dome as a picture; from the side it showed a pale bar (the shoulder's
  highlight). Build the rim, the dome and the lugs as their own shapes, and give the dome a material kept to the
  dome's own painted pixels.
- **A cut-out's grid cells spill across a shared outline.** `market_props.figures` kept every grid cell its outline
  touched; with one shared mask, the cells along an outline two figures share (a pair of bullocks, two hens) show a
  strip of the other figure's pixels at the wrong depth: a stair of white blocks from the side. Pass `exact=True`
  (cells clipped to the polygon).
- **A figure card standing square to the camera is a stick from the side.** Turn it in plan a little (figures' yaw,
  20-30 degrees, head towards the camera): its painted x and z are kept, so the front is unchanged, and from the side
  it is a narrow animal, not a line.
- **A tile crop next to a figure picks up the figure.** The hens' nest tile reached 4 px into the white hen's cream
  bottom and the whole nest read pale. Crop straw (and every material) well clear of anything painted over it.
- **Straw or grass tubes thinner than 2 cm are ink scratches** (already a rule for stalks): use cut-out wisps from
  the painting, masked to the material's own colour (`golden_pixels`, not `straw_pixels`, where orange feathers would
  pass as straw).
- **Painted light is not a material either.** Lamp glow painted on a wall (the tank's terraces) inside a tile crop
  repeats as orange smears along every tread; projected onto the 45-degree bevel of a lip it smears from above. Crop
  tiles clear of painted glow, and raise `K.front_min` (0.6-0.7) on models whose bevelled edges would catch it.
- **A thin coping or cornice strip on a wide top reads as planks** even mirror-squared, when the strip carries block
  joints: give a wide top the wall's own stone tile and let the front projection paint the strip's face.
- **A carving decal copied round a pillar carries what is painted in front of it.** The mandapam's front pillars have
  lamps burning before their middle cubes; decals of those cubes put a glowing lamp on every side and on every back
  pillar. Copy round a cube whose painting has nothing in front (`carved_pillar(mid=...)`).
- **Two parts on one spot get no painting.** Two inner pillars computed to the same x (two rows mirrored about the
  middle) shadowed each other in the bake's visibility pass and showed bare stone in the painting's dark doorway.
  Dedupe positions, and leave out parts the painting shows empty.
- **Check a tile crop's alpha, not only its look.** The market houses' plaster is speckled with transparent holes
  (the cut-out keyed out pale stains): crops 75-94% opaque turned walls and decks pale and blotchy and repeated a grid
  of light marks. Measure opacity (`(crop alpha > 127).mean()`), pick fully opaque crops, or fill the specks first
  (`market_props.ftile`).
- **The cut-out's holes show through on the front too.** Where the painting itself is transparent inside a wall, the
  bake falls back to the wall's own tile, a pale patch in the painted wall. Put a `market_props.skin` (the painting
  with its specks filled, on a face just in front of the wall, openings left out) over such walls.
- **The audit's repeat measure fires on real symmetry** (two identical windows either side of a door): judge it by eye.
- **Bevelled boxes can halve a texture one way.** With `smart_project(angle_limit=60, area_weight=0)`, a 45-degree
  bevel's normal can be picked as a projection and the big faces beside it projected along it (cos 45: uv_squash
  1.41 on parapet_gap even after the material-aspect fix). Check the audit's squash; until the kit changes, leave
  bevels off a model that shows it.
- **Coplanar front faces get no painting.** A parapet band whose face lay exactly in the walls' face (the walls' box
  reached up behind it) shadowed itself in the bake's visibility pass, so the painting was not projected there (a
  plain band where the vine and fronds are painted). Set such a face a few mm proud, or stop the box behind it.
- **Cards count for the lift.** The record's lift is the lowest point of the model and its cards: a figure or plant
  card reaching below the painted foot (into the painted shadow) makes the lift 0 and the whole building floats by
  its foot height. End figure polygons and plant cards at the painted foot (`stand_on` only moves solid parts).
- **A thatch tile from a strip mirror-stacked reads as a woven mat.** The chariot shed's rake band, mirror-stacked
  (strip_tile), made rows of light and dark bands across the roof. For straw, use the band's rows evened out and
  stacked with random slides along the straws (`market_props.strand_tile`), so the straws run down the slope with no
  rows.
- **Damage painted on the front belongs on the back too.** A house painted with its plaster fallen away to brick all
  over the front was plain cream behind. Trace a few of the painted patches and lay them on the back and sides
  (`market_props.wall_patch`): the same house, painted by the same hand.
- **Drying trays and terraces painted from above in perspective are trapezoids on the painting**: build the frame a
  true rectangle (the front edge's painted length), and the roof terrace's side parapets straight back, and accept
  the wedges the difference map shows at the back corners.
- **Pick tile crops by measurement, not by eye.** A crop's opacity, its low-frequency spread (stains, drips, shade)
  and its fine detail can be scored over the whole painting in a second (`mp_audit/findclean.py` in the scratchpad):
  a clean, lit, fully opaque patch with some fine texture is the tile; a featureless one reads as flat, a stained one
  repeats.
