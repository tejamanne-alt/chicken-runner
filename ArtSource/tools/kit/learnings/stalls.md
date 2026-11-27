# New lessons from the stalls audit (stalls_cdef, stalls_ghx)

- **Poles projected through themselves show the painting's shading and whatever is painted over them on their backs.**
  A bamboo post with `K.projected` (even squeezed) carries its painted dark side as a near-black stripe down its back,
  and a back post partly hidden behind goods carries the goods (red chillies) round to its back. The front projection
  already paints every pole's front: give poles, stubs, rails and frames a tile of the painted bamboo instead
  (`stalls_cdef.pole_tile`: a narrow strip down a post's lit middle, mirrored side by side into a square; `line=` for a
  leaning pole). Never a flat `K.colour` either: it reads as orange plastic tubes from the sides.
- **A thin crop used as a ground or wall tile repeats as a grid of its marks** (`K.tile` keeps the crop's proportions,
  so a 115x24 px strip repeats every 24 px down the face). Square it first (`pole_tile`, `strip_tile`) and soften.
- **A tile crop taken across something painted in front of the surface carries it everywhere**: the bench-leg wood cut
  across the painted betel leaves striped every leg green; the earth crop with the painted scuff mark drew white
  streaks all over the ground. Check every crop for foreign objects, not only for holes.
- **The white cut-out line along the far edge of a painted ground** lands on whatever geometry stands there (a bed's
  bank) as a white streak: keep it off the front projection (`K.front_exclude`).
- **Rope beds and nets of thin tubes are all ink outline**: a string cot's woven bed of 6 mm cords reads as a black
  wire mesh. Make the bed a thin sagging sheet wearing a tile of the painted weave.
- **Stacks of folded cloth**: projected through, the stack's sides drag the front's ink and colours into streaks and dark
  blocks. Give every fold its own material, a strip of the painting at that fold's height (`fold_stack` with a
  material function): from the side the stack is the same folded sarees.
- **Heaps projected through (squeeze 1.0) smear on their sides and top** (the top row of the painting is dragged back
  over the heap). Give a heap a tile of its own painted goods, or cover it with modelled pieces all round (`pile`), and
  let the front projection paint its front. Pieces only on the front leave a smooth plain dome behind.
- **Things hung on a back wall must face outwards** (a basket hung on a peg on the back shows its mouth to the back),
  and wear a tile, not the front painting projected through the wall.
- **A wall clad in one slab reads flat even with a tile**: clad booths in boards with narrow gaps (`booth_shell`).
- **The painting's backdrop seen through gaps** (under a counter, between table legs) is sometimes opaque in the
  cut-out: the front diff shows it red. Leave the model open there; it is the painting's flaw, not the model's.
- **A display board's projected material also paints its underside**, seen from behind as smeared produce: make the
  board planks and lay the produce as a thin layer on top.
- **`K.tile` of a non-square crop stretches on horizontal faces.** Its box projection scales x and y by the crop's
  width and only z by its height, so on a top face (a bench, a table, a deck, a floor mat) a 120x15 px crop is drawn 8
  times too long front to back: streaks. For anything with a large top, use a square crop or square the strip first
  (`stalls_cdef.pole_tile`, `market_props.strip_tile`).
- **Painted ground seen from above is not a slope to build.** Stalls painted on a band of red earth, or a mat laid out
  in front of the vendor, were built on banks of earth rising to the back: from the sides a wedge of plain ground. Keep
  the ground level (a low earth patch). Where the goods must stand at their painted heights, put them on a real raked
  display stand (`stalls_ghx.raked_stand`: a bamboo-framed, mat-sided stand whose top follows the rake, then a level
  deck), or a level dais or plinth; accept the red holes where the painting shows the ground's top.
- **A figure painted in front of a raised mat sits on it**: model what she sits on (a folded mat, a dais), level.
- **Striped cloth is not a tile for `K.tile`.** Its two samplings at different scales, blended by noise, jumble
  regular stripes into a checker; and a crop taken where the painted stripes run diagonally (perspective) gives
  diagonal or chevron stripes. Take a strip across the stripes where they hang straight (just above the scallops) and
  stack it square with one sampling (`stalls_cdef.pole_tile`): back slopes and gable ends then wear clean stripes.
- **Model the stall where the painted posts are.** A turned stall (`stalls_ghx.Turned`) whose angle and size were set
  by eye stood a few cm off every painted post (red/blue pairs down each post). Solve the turn and the half-width from
  the painted posts' centres (front pair and back pair at one height), and stand the posts at the painted feet's
  height (within the game's 10 cm lift) rather than stretching them to z = 0.
- **Squared thatch strips need softening.** Squaring a thin thatch strip stops it stretching down the slopes, but its
  dark painted ticks then repeat in rows; soften 0.4-0.5.

## Round 3: paintings drawn from above and in perspective (K.oblique, K.converge)

- **Measure the slope off round and square things drawn from above, then check it on a second one.** The cage's base
  ring (127 px across, 38-46 px deep) and its feeding cup gave 0.30 for the astrologer; the stool's square seat gave
  0.20-0.30 for the barber. A top of known shape is the measure; the painted ground band is not (its depth is unknown).
- **The painter draws the back narrower too: fit the convergence to the painted edges, and check that it makes the
  plan square.** Lines of one real x (a mat's sides, a bench's ends, a stall's post pairs) meet at the vanishing
  column; their painted spacing at two depths gives c. The astrologer's mat came out 2.97 by 2.87 m with c fitted to
  its two painted sides: square, as a straw mat is. That is the check that the slope and the convergence are right.
- **Decide whether the painting is one camera.** With a vanishing row (`K.converge = (c, xc, yc)`) the kit draws a
  true perspective whose horizon is at row yc + k / c: things above it are seen from below. Use it only when the
  painting agrees (the astrologer's umbrella shows its underside above the horizon). The barber's and the cloth
  seller's roofs and the paan seller's umbrella are drawn from above though their horizon (from the posts, the cot,
  the bench) runs below them: a painter's view. Give those a convergence in width only (`(c, xc)`), with the slope
  measured where the objects are (an object grows in plan by f = 1 + c * y, so the slope inside it is k * f).
- **Build the structure in real coordinates, the objects round their own anchors.** Posts, beams, roofs, benches and
  cots are placed at their real x, y, z from the painting (xk, yk, zk: through the slope and the convergence) and come
  out square. A basket, a stool, a cutter or a figure is built in the painting's scale round its foot (zo / yo, the
  slope alone) and set at its real place and size as a whole (`stalls_cdef.place`): its shape stays true, it grows
  with its depth, and its own texture follows (`proj_at`, `built_at`). An object spread deep in depth (an umbrella
  leaning back 2 m) is fitted in real coordinates instead, through the same mapping.
- **Cut-outs are mapped exactly.** A figure's or a leaf's card set at its real place is re-mapped vertex by vertex
  so that it is drawn exactly where it is painted (a card spread in depth, or turned in plan, otherwise drifts a few
  px towards the vanishing column: red and blue down one side of the vendor).
- **Big faces under a perspective need vertices.** The audit maps the mesh vertex by vertex: a mat or ground top of
  one face is drawn straight between its corners and its texture warps. Grid them (`topped(grid=12)`).
- **The kit's front projection judges visibility from above along the slope.** An umbrella's underside above the
  horizon is never "visible" to it, and its top faces that map onto the painted outline catch the outline's halo as
  white rings. Give the underside its own projected material (the painting through the perspective, point by point)
  and keep the painted underside and the canopy's outline band off the front projection.
- **(Superseded in round 4.)** A painted ground band that runs to the frame's edges looks like a fan under a
  converging painting; do not build the fan (see round 4 below).
- **Thin wires (a birdcage) as tubes are all ink outline in the game; as ribbon cards of a painted wire strip they
  are the painted wire** (`stalls_cdef.ribbon`, `birdcage(wire=...)`).
- **Watch variable names in builders**: a `for k in range(9)` loop silently replaced the slope k and threw half of
  stall_low 11 m below the ground.

## Round 4 (lead review of round 3)

- **No fan-shaped ground, ever.** A ground band painted to the frame's edges at every depth becomes a trapezoid
  under any convergence: from above and the sides a red carpet, and in the game it spills into the next slots. Build
  a true rectangle no wider than the frame, as deep as the painted band at the frame's middle, and accept the red
  wedges at the band's two far ends (write them in the verdict).
- **Real proportions beat the front match.** Under a converging painting an object drawn as large as the structure
  around it comes out bigger than real (the barber's stool with a 0.74 m seat, a 0.7 m basin, back-row sacks over
  1 m across). Painted size and height cannot both match a real size at any depth (moving it forward draws it lower,
  moving it back draws it smaller), so build it at a real size where the painted one stands (`place(size_cap=)`,
  and squeeze its projected material onto it) and accept the red round it.
- **An object built smaller than painted leaves its painted pixels behind.** The front projection along the slope
  lands them on the ground top behind it: ghost legs, a ghost basin rim, post stripes on the earth. Put every such
  object's painted region (and posts standing on a ground top) in `K.front_exclude`, and give the ground top a fill
  of its own earth there (`slope_proj(fill=, boxes=)`), so it shows the ground, not a ghost.
- **A sack's rolled mouth stands r in front of and behind its centre**: on a sloped painting its front and back
  heights are the painted rows at those depths (`zo(f, y - r)`, `zo(b, y + r)`), or every back rim sits k * r too
  high (blue arcs over the back row).
- **A flat colour sampled off the painting must be sampled on the part**: the cot's back feet took an orange
  sampled off the earth and read as orange pots from behind.
- **Splayed rafters carry a splayed cloth.** A low stall's awning whose front rafters splay out ends over the post at
  its ridge and past it at its hem: a constant-width cloth stuck out 16 px past the painted ridge end.
- **Fill the gaps in a painted top by blending its own colour across them, row by row** (`slope_source`): one median
  for a whole gap picked up the painted shade beside it and left a dark, straight-edged patch on the earth where the
  stool had been painted.
