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

## Round 3 (bicycle, rope_cot, bullock_cart)

- **Spokes as a spoked-disc card** (`lane_props.spoke_disc`): one card per wheel, a polygon on the painted rim's inner
  ellipse (fitted to the alpha, grown by the rim band), every vertex at its painted x, z and at the depth of the
  wheel's own plane, showing the painting's own spoke pixels. Its card rule is the alpha minus the painted stroke of
  every part modelled as a solid (rasterise each tube's painted polyline at its radius + 0.5 px, `stroke_mask`, and
  plates' outlines, `poly_mask`), so a fork blade or stay is never painted onto the spokes and a solid behind shows
  through. The bicycle's front went from IoU 0.73 to 0.86 on this alone; from every side it is a spoked wheel.
- **Tube radius = painted width / 2 - the ink line** (about 1.1 px on a 1.7 m piece): every bicycle tube had the
  painted half width as its radius and showed a blue line down both sides.
- **Pairs straddling a wheel**: where the painting shows the pair apart (the fork's blades, 12 px), put each on its
  own painted line; where it shows one (the stays), keep both on the painted line, one behind the other.
- **Which half of a handlebar is near** follows from the turn: a bike whose front is further back has its near grip
  painted towards the front (left). The other way round the bar ran 0.6 m fore and aft from above.
- **A steered wheel's tilted painted ellipse is the wheel leaning on its fork**: lean it about its forward axis by
  atan(|n_x| tan(tilt)) (3.6 deg for a 6 deg tilt at a 37 deg turn); tyre, rim, spokes card and mudguard follow.
- **A painted ground band** under a level painting: hang the earth's rim to the painted ground's lower edge all
  round (`ground_edge`, `front_rim`; the back of the rim shows below the front too). Under an oblique painting, give
  the patch the painted band in plan instead (`earth_band`: its front edge at the depth the painted edge gives along
  the slope).
- **Oblique and converge: put y = 0 on the front-most painted faces** (a block's front face, not the legs' middles):
  converge scales everything in front of y = 0 up, so a block centred on y = 0 had its front face drawn 7 px wider
  than painted. Map every painted point at depth y back through both (`Xs`, `Zs` in rope_cot), cards' size too.
- **A painter's view from above is rarely one slope**: the cot's back feet rise 22 px, its far rail 38 px; the cart's
  far wheel says 0.05, its far rails 0.17. Take k from the biggest tops (a bed, a far rail) or from two ground
  contacts, and write the rest down; a level, square model cannot follow both.
- **A shallow painted top (visibility 0.17 at k 0.17) takes only a fifth of the bake's painting at front_min 0.1.**
  As its own material, the painting along the slope is exact from the front but stretched 1/k (six times) front to
  back: streaks from above. Give it an un-foreshortened tile of its painted material (the cot's weave) instead.
- **Ridged tops draw an ink line behind every ridge** from the camera (rope courses on the cot's bed came out as black
  stripes): keep tops smooth and let the texture carry the weave.
- **A `C(px, py, off)` that keeps the painted x on every plane makes a parallelogram in plan** (the cart's body: its
  far side slid 0.4 m along it, slanted ends from above). Trace on the near plane and carry the point straight across
  (`+ nrm * (off - ref)`): a true box.
- **When the painting is not one consistent view** (the cart: body side-on, far wheel drawn as for a cart turned 18
  degrees), compare the true candidates by their front IoU before choosing (side-on 0.81, 8 deg 0.79, 18 deg 0.75).
- **Legs wrapped with the painting pick up the grass painted at their feet** (green stains on their backs from the
  far side): `proj(mask=...)` without the grass pixels.
- **Never name a builder's slope `k`** when the builder also loops `for k in range(...)`: closures read the loop's
  last value (the cart's points came out metres off).
- **A front-only render** of the exported FBX (the audit's toon look, ink and slope mapping) at 2x the painting's
  size, plus painted-versus-model opaque runs per row and column and the largest red and blue blobs, turns a round in
  20 s instead of the audit's 50 s and gives the px offsets to correct.

## Round 4 (K.oblique_x on the bullock cart)

- **Fit a side step from two things of known separation at the same size**: the cart's two wheels (same radius,
  1.8 m apart on one axle). Fix the far wheel's radius to the near wheel's and fit only its centre to its visible
  rim (the alpha's outer edge, rows clear of grass and rope): 115.5 px right, 13 px up gives oblique_x 0.29, oblique
  0.033. Carry every traced point back along both (x - oblique_x y, z - oblique y) before carrying it across.
- **A side step must hold for the whole painting, not one part**: the cart's far wheel is painted stepped, its body
  is not (its far rails end with the near ones, nothing above the pole). With the step, the far wheel lands but the
  far side of the body shows 79 px beyond the near end (IoU 0.81 -> 0.79; half the step 0.77). Before adopting a
  view setting, check every far-side feature the painting shows against it; where they disagree the painting is
  inconsistent and no true model takes both.
