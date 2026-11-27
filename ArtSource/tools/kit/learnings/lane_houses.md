# New lessons from the lane_houses audit

- **plant_pixels keeps cream and golden walls.** Its "white" rule takes cream lime wash (min > 190, low saturation)
  and its "golden" rule takes turmeric/ochre plaster, so a climber or bush card cut over such a wall shows square
  patches of wall with straight edges from the side. On cream walls mask with leaves + vivid petals only
  (`lane_houses.bloom_pixels`); on yellow/ochre walls with leaves from hue 50 up (`lane_houses.green_pixels`).
- **A climber's big front card must not span other painted things.** A card box over a vine that also covers the
  garland, sunshade and jamb carries their pixels (the mask keeps red/orange petals) and shows them again, displaced,
  from the side as an orange ghost on the jamb. Split the box round them.
- **Climbers round a corner hug the corner.** Side-wall cards scattered over the wall at random depths read as loose
  floating patches. Put them at the front corner, deepest at the top, few low down, plus some trailing along a ledge
  (`lane_houses.corner_climber`), as ragged blob cards.
- **Small tiles quilt.** A clean but small crop (under ~25 px) box-projected at its painted size repeats every 15-20 cm
  as a quilted grid on a long plinth: give it `size` 0.5 m or more (the red oxide is smooth anyway) and soften.
- **Crops near a painting's edge take the neighbour.** A wall crop that starts a few px from the cut-out's edge picks
  up the neighbour's ladder rung ends or the outline ink; they repeat as rows of small "blocks" on the side walls.
- **A back door decal needs steps.** A door copied onto the back wall at the front door's height (above a plinth) has
  its sill 0.7-0.8 m up the wall: add plain steps up to it.
- **A thick hip end stands out past the painted hip line.** `hip_thatch` (and any solidified roof mat) puts half its
  thickness outside the surface, so from the front the hip ends show as a blue band 10-15 cm wide outside the painted
  roof's sloping ends (worst on stepped/tiered painted ends). Pull the hip ends in by about half the thickness
  (`lane_houses.hip_thatch(pull=...)`), and keep fronds/fringe cards on a hip end from hanging below its eave.
- **Marks in a plaster crop repeat as a grid of dots.** Even a "clean" crop of lime wash has speckles and dashes that
  read as a regular dot pattern on a 4 m side wall. Take them out before tiling: replace every pixel far from the
  crop's smoothed colour with that colour (`lane_houses.clean_tile`). It cannot clean big things (a leaf cluster, a
  shadow): those still need cropping round.
- **A thin plaster column stretched to a wall shows mirror seams.** Use `clean_tile` with a `size`, or a strip tile
  stacked side by side for columns (`lane_houses.strip_tile` now stacks columns as well as bands).
- **The earth strip under a building (10-40 px tall) streaks across its ground slab's top** when used as a plain
  K.tile: stack it square (`strip_tile`).
- **Things painted in front of a recess ghost onto its back wall.** A kettle, steam, glasses or a jar standing in a
  hatch: where the model is narrower than the painted outline, the front projection paints the rest of the
  painted object (its outline, a handle, steam) onto the back wall of the recess, visible from every side view.
  Put those objects' boxes in `K.front_exclude` (they carry their own projected materials anyway).
- **Corrugated tin deeper than ~1 cm goes half dark from the side**: the toon light shades every other facet. Real
  tin is ~18 mm peak to peak: amp 0.009.
- **A small hovering hardware part is "loose"**: a bar on the back of a door 4 cm off the battens counts as loose
  parts. Seat it on a batten in staples.
- **Modelled corrugations go black from the side.** A tin roof or awning corrugated all the way up shows, from the
  side views, as a dark brown/black band: the ink outline hull pokes out of every ridge seen at a grazing angle.
  Model the corrugation only along the eave (where it gives the painted scalloped edge) and let the texture carry it
  above (`lane_houses.corrugation`). Same for hip/ridge caps: a 35-50 mm cap tube stands a blue band outside the
  painted roof edge; keep them 18-30 mm and seated on the line.
- **Hay heaps need their own projected paint.** Excluding a heap's painted box from the front projection (to keep
  flat hay off the wall behind) also removes the paint from the heap's own front: give the heap
  `projected` hay about its own axis (squeeze ~0.9) so it is the painting from the front and hay all round.
- **Mirrored strip rows of strand textures make chevrons.** Thatch or grass strips stacked as mirror images zigzag
  into herringbone; stack them the same way up, shifted and cross-faded (`strip_tile(mirror=False)`).
- **Scattered cards must sit on what they belong to.** Hay tufts placed at random depths over a heap's painted box
  float as pale paper bits once the heap is a real (smaller) solid: place each on the heap's surface.
- **Extrapolated poles leave the building.** A scaffold pole traced from its painted top and bottom and then carried
  on down to the floor can exit through a wall when it is a diagonal brace; end braces where they are painted, on the
  member they rest on.
- **A skirting or dado box runs through doors and alcoves.** A lime skirting (or a dado band) modelled as one box
  round the walls sits in front of every recessed door and alcove's foot. From the front the projection hides it;
  from 12 degrees up and from the sides it shows as a white bar across the door's foot or a block in the alcove
  (the cycle shop's pump stood in one). Cut the skirting with the door's and alcove's cutters. Likewise put back-door
  decals in front of the skirting (2 cm off the wall), or their feet vanish into it.
- **Excluding a modelled object's box from the front projection is a trade.** It removes the ghost of the object on
  the wall behind (seen from the side) but the wall then shows its own material where the model is narrower than
  the painted object (thin tyres, spokes), which the difference map shows as yellow. Exclude by the object's own
  pixels (`lane_houses.exclude_where`) rather than its box, so only what is right behind it changes.
- **A perspective painting's foot line is not the ground.** Where the painting shows the house's plinth ending well
  above the frame's bottom (the steps and a planter in front reach lower: the painting looks down), the true model's
  plinth reaches the ground and shows as a blue band under the painted plinth. It cannot be lifted (floating) and
  must not be sloped; accept it and say why.
- **A round heap takes the front painting all round its flanks.** With front_min 0.1, every face of a dome turned
  less than ~84 degrees from the camera takes the painting, so from the side its flanks show the painting dragged
  sideways into vertical streaks (a "beehive"). Excluding the heap from the front bake fixes the sides but loses the
  painting at the front. Build a heap that sits against a wall as its painted outline carried straight back with
  rounded edges (`K.prism` + bevel): the front face takes the painting, the sides and top face away and take the
  material's tile.
- **Palm fronds on thatch need a closed mask.** `olive_leaf_pixels` keeps only the leaflets, so a frond card shows a
  scatter of green bits; close the mask over the straw between leaflets (`lane_houses.frond_pixels`). Lay back-slope
  frond cards well clear of a lumpy thick thatch (0.5 m above the surface line), or the lumps poke through them.
- **Turned posts and pillars pick up the halo.** The white halo beside a painted pillar or pole projects onto it as a
  white stripe down its side: use a halo-free projection (`lane_houses.projected_solid`).
- **Cut-outs with erased neighbours keep ghosts.** Where a neighbouring prop (a ladder) was erased from a cut-out,
  a faint ghost of it can stay in the painting; the front projection reproduces it. That needs a cleaner cut-out,
  not a model change: report it.
