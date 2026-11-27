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

## Round 3: drying trays painted from above (chilli_mat, papad_mat), rebuilt level with K.oblique

- **Measure the slope from round things lying flat.** A disc lying on the ground (a papad, a plate, a lid) is painted
  as an ellipse exactly `oblique` times as high as it is wide; fit the ellipses to their painted rims (score each
  candidate ellipse by the darkness along its best-matching half, so the parts hidden under its neighbours do not
  count) and take the ones that lie flat (here 0.51-0.56, k = 0.55). One drawn taller is tilted up (sin t + k cos t =
  ratio), one drawn flatter rests its front edge on another; which rim is drawn over which gives the stacking.
  The depth of everything else then follows from where it is painted (depth = painted rise / k).
- **K.oblique undoes the painter's "further back is higher", not "further back is smaller".** A painting in true
  perspective also draws the back narrower (the trays' back pole 0.77 as long as the front): a square model's back
  corners stand past the painted ones and the audit's front keeps blue wedges. Say so in the verdict; do not make the
  model a trapezoid to hide it (kit request: a convergence term).
- **Converging painted edges must be kept off a level top.** The painted side poles run on the slant across where the
  level mat is; projected, they would draw a second pole on the mat beside the real one (seen from above). Exclude them
  (front_exclude polygons along the painted pole) and let the top's own material show there.
- **The own material of a top painted from above: the painting reflected back into itself, without the goods.** Where
  the projection does not land (the strip the front pole hides, the corners past the painted ones, the excluded
  poles), a tile of the weave reads as a different mat and the plain painting smears one row. Map the slope ray's
  painted pixel and reflect it at the painted frame's inner edges (`market_props.mat_mirrored`); first replace the
  goods (papads, chillies) in that source with the painted weave quilted from between them
  (`market_props.weave_fill`), or half papads appear painted flat on the mat beside the real ones.
- **A heap under a slope projection: build its height in painted coordinates and find the surface by a fixed point**
  (z = z_mat + h(painted pixel the ray at that height reaches)), damped, with h sampled bilinearly: a nearest-pixel h
  terraces the heap into steps the projection turns into stripes. Its back must fall more gently than the view's
  slope (thin it out towards the back over the painted rows): a back that falls as steeply as the rays gets the few
  painted rows of its crest smeared down it.
- **`K.front_min` and the vis ramp**: a level top faces the slope at sin(atan k) (0.48 at k = 0.55); the projection's
  weight is (vis - front_min) / 0.3, so front_min above about 0.15 already blends a level top with its own material
  (washed out goods). Keep 0.1 and make the shapes face the slope instead.
- **Bamboo poles: wrap the bamboo round the pole by angle about its own axis** (`market_props.bamboo_wrap`): a strip
  along the painted pole's lit middle, its shading across evened out and blurred round, laid along the pole; box
  projection lays the node marks along a pole that runs front to back. Add low node rings where the painting draws
  them.
- **3D goods on a painted heap carry the game's ink**: pods along the painted chillies' bright cores sat above the
  painted bodies (the highlight is off-centre) and drew black arcs above them. Centre each pod across the painted body
  (scan its red across the core) and make it as thick as the body inside its ink line.

## Round 4: the same trays with K.converge

- **Fit the convergence to straight painted edges that run back** (side poles, a bench's rails, a field's edges):
  real straight lines at x0 seen as xc + (x0 - xc) / (1 + q * (v - z)), v the painted height, z the line's real
  height; fit q, xc and each x0 to the cut-out's outline (not the centre line: the outline is what the audit compares),
  with the game's ink (about 1.7 px here) inside it. Then c = q * k. Both trays: 0.9 px rms.
- **Measure the slope again once the narrowing is known.** A round thing lying flat is painted k * f times as high as
  wide (f = 1 + c * y where it lies): without f the back papads read as tilted (0.64-0.67) and k came out too high
  (0.55); with it all seven read flat at 0.46-0.52 (k = 0.49). If the heights do not shrink with the widths, leave the
  row term out (this painter shrinks only across).
- **Where parts cross at the back corners, decide which is on top from the painting.** Side poles laid over the back
  pole stood up past it as bumps in the front; the painting draws the back pole over them. A pole lifted onto others
  also lifts whatever rides over it (the papads poked above the painting): here every pole lies on the ground, butted
  and lashed.
- **Goods painted over an edge drape over it.** A papad painted reaching over the back pole, lifted over it and kept
  flat, ends higher than painted; draped down behind the pole it ends at the pole's top as painted. The draped part
  faces away from the painter: give it a tile of the goods, and take the goods' own projected material from the goods'
  pixels only (filled outwards), or it wears the pole painted under it.
- **Size the goods with the narrowing where they lie** (R * f), or the back ones come out small; from above the
  papads were then round.
