# New lessons from the lane_props audit

- **Thin parts traced by eye off a grid image land off their painted line** (the bicycle's spokes, the pump's handle
  were 6-12 px off: red on one side of the part, blue on the other in the difference map). Measure a thin part's
  middle from the painting's alpha, row by row and column by column (the opaque run's centre), or detect painted
  spokes as lines from the hub; never place them by an assumed pattern (evenly laced spokes, an even 12-spoke phase).
- **The two wheels of one vehicle need not be painted alike**: the bicycle's front wheel is steered further than the
  frame (its rim ellipse is narrower), the cart's far wheel has its spokes at a different phase from the near one.
  Fit each painted rim as its own ellipse (centre, upright radius, width ratio = cos of its turn) and each wheel's
  spokes separately.
- **A ground patch of `K.colour` reads as a plain flat disc from the side and above** (flag "flat"). A thin painted
  strip of earth cannot be `K.tile`d either (it stretches into bands, and the crop holds the prop's foot, grass and
  ink). Quilt it: small feathered dabs of only the earth pixels (no grass, no ink, no halo), laid at random, turned
  and mirrored, wrapping round, into a square seamless tile (`lane_props.quilt` / `quilt_tile`, `earth(dirt_box=)`).
  The same works for a stone block, a pedestal, blue-painted boards or a cane straw bed painted only in small patches.
  Use soft Gaussian dabs: dabs with a hard-ish round edge show as a pattern of discs.
- **Wood quilted with random turns loses its grain** (mottled, not wood); quilt wood with `turn=False` (only mirrored
  left-right) and turn the finished tile a quarter round (`upright=True`) for the stakes, posts and props whose grain
  runs up.
- **A round thing projected straight along y shows its painted rim on its sides as streaks** (the pot stack's sides
  were the painted silhouette's dark edge and highlight dragged round). Wrap the painting round it by angle instead:
  straight on up to ~60 degrees from the front, then fold back towards the middle of the painted half
  (`lane_props.proj(wrap=62, axis_y=...)`). Remember axis_y for a pot that is not on y = 0.
- **The tops of sacks, coops and crowns smear when the painting is pushed through along y** (one painted row dragged
  back over the whole top). Project the top obliquely (`proj(top_shear=k, axis_y=front)`): the top samples the
  painting further down for every metre it goes back, so it wears the thing's own texture and its stripes stay where
  they are along x. Keep k small (0.3) or a sack's top samples the sack below it.
- **The back of a part with something painted in front of it** (the lamp pillar's pedestal behind its garland and
  bell) must not wear the painting pushed through: the excluded garland is filled from its dark shadow and shows as a
  dark niche on the back. Give it its own stone tile, and model the panel (pilasters) on the back and sides.
- **A painting drawn from above in perspective is not a reason to tilt the model's ground or raise its back legs**
  (the rope cot had back legs 20 px higher and a ground tilted to match, so from the side it stood on a slope). Build
  it level and square on its front legs' footprint; the painted perspective of the bed and back legs is accepted as a
  front difference.
- **Ground patches need no bottom** (a lathe from radius 0): the bottom faces are never seen, take atlas room, and their
  UVs are stretched (the rope cot's 0.54 uv_stretch was its earth's bottom disc). Start the profile at the rim and pass
  `cap=False`.
- **The atlas packer squashes the whole model by the first material's image aspect** (kitlib `_smart_uv` ->
  `pack_islands` follows the active image): the rope cot, whose first part was a leg wearing the 1.9:1 painting, had
  half its atlas resolution one way (audit uv_stretch 0.51; most models have 1.4-2:1 anisotropy unflagged). Until the
  kit fixes it, put a part with a plain colour or a square tile first (`lane_props.square_first`, run after every
  lane_props builder by its `model` wrapper).
- **A quilt's keep rule must match the material's brightness**: a "plain" rule that drops bright pixels picks the
  shadows of a light sandstone pedestal and the dark gaps of a straw bed (both came out dark brown). Preview the quilt
  next to the painting before building.
