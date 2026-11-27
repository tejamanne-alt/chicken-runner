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
