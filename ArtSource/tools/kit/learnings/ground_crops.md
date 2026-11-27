# New lessons from the ground_crops audit

- **UV stretch from a wide painting** (fixed in the kit now, `kitlib._smart_uv`): Blender's `pack_islands` scales
  islands by the aspect of their material's image, so a model whose parts carry a wide painting (any projected
  material) got islands stretched by about the aspect squared (the crop strips' tops 30:1: blurred one way, sharp
  the other). Rule: check `uv_stretch` and `uv_squash` in every audit; a face stretched over 3:1 is a defect even
  when it looks fine at the sheet's size.
- **A slab's walls must follow its top**: a ridged or rumpled top sheet over four flat-topped side quads leaves
  see-through slits where a ridge meets the end wall (white scallops along the bed's ends). Build the bed as one
  closed mesh: the top grid, and walls hung from its boundary vertices down to the foot (`ground_crops.field_bed`).
- **Cut ends of a strip: carry the painted band round, do not project it**: a straight projection paints one column
  of the front band across the whole end (horizontal stripes). Sample the band along the end at its painted scale
  (`ground_crops.side_band`): the ends show the same layers of soil, water and mud.
- **A field's top seen only as a thin band**: a crop of the band (10 px tall) used as a tile reads as planks. Quilt
  a square tile from random small patches of the band, turned and flipped (`ground_crops.quilt`); keep the patches
  unturned for fibre or grain (`turn=False`).
- **Rows behind a painted row**: plant them on the painted plants' columns, mostly the same painted plant as the one
  in front (`crop_rows(same=0.75..0.9)`), turned less than 40 degrees and a little smaller: from the front they hide
  behind the painted ones (as a real field does seen along its rows); random plants between them fill the painted
  gaps (front spill 0.36 on the banana grove).
- **The front row is cards seen edge on from the side**: cross every front plant with itself turned square to the
  painting and set going back from it (`crop_rows(front_cross=True)`), or the side views show a fence of slivers.
- **Cards wider than 1024 px**: the leaves texture is downscaled to `leaves` (1024 by default); thin blade tips of a
  1200 px painting fall under the alpha cut and the front loses them (red tips all along the diff). Use
  `@model(..., leaves=2048)` for paintings wider than 1024 px.
- **Front cards must reach the painting's edges**: cards cut from x0..x1 inside the painted extent cut the end
  plants' leaves off straight (red leaves at the ends, a straight edge in the side views). Take the end cards out to
  the painted extent.
- **Halo vs white parts**: `no_halo`'s haze rule (pale, unsaturated anywhere) takes the white of cotton bolls with
  it. Remove the halo by flood from the transparent outside through pale grey pixels (`ground_crops.halo_free`):
  white parts inside their own ink line stay.
- **Flat pieces have no ink line in the game** (`ArtModels.Place` outline 0 when flat): the ring of blue round a
  flat piece in the audit's difference map is the audit's ink, not the model. Do not shrink a flat piece's outline
  to cancel it. Round props do get the ink: a 0.2 m prop's 3 mm ink is a visible share of its outline.
- **Do not let a part down to the ground to meet the frame's foot** (the coconut's lower half, the husk's keel):
  keep the painted outline; the record's lift sets the model down. Letting it down puts blue under it in the front.
- **Angle-wrapping a round thing distorts its front**: mapping angle round the axis linearly to the painted x moves
  every painted feature outwards on the front (a point 30 degrees round shows the painting at 0.33 of the radius
  instead of 0.5). Map exactly (sin) over the front 45 degrees and linearly beyond (`wrapped`, `axis_wrap`).
- **A nut or pod painted lying at a slant**: wrap the painting round its own long axis, not the vertical: fibres
  that run along the axis then continue round it and the mirrored back half meets the front along fibres, not
  across them (the coconut's chevrons at its sides).
- **scipy's `binary_erosion(m, iterations=0)` erodes until nothing is left** (iterations < 1 means "repeat until it
  stops changing"). Guard every `iterations=erode` with `if erode > 0` (a quilt found "no clean patch" from it).
- **Opaque haze between stems is projected onto the stems behind**: the sugarcane painting has opaque pale grey gaps
  between its canes; the front projection (and a rind sampled down a painted column that runs through such a gap)
  painted white stripes on canes behind. Take the haze off the projection (`ground_crops.haze_free`) and sample a
  rind only from columns with no pale pixels (measure them).
- **No bed or mound the painting does not have**: the sugarcane stand and the tufts and weeds had a plain dark slab or
  mound under them (blue in the difference map, a plain-colour face from the side). Stand them on the ground from
  their painted feet; the record's lift sets them down.
- **Turned copies of a tuft round its foot**: keep them between 35 and 145 degrees (never near face-on, where a
  mirrored copy pokes out beside the painted outline) and a little smaller: from the front they sit inside the
  painted fan.
- **A traced line drifts off the painted one**: the twigs' hand-traced centre lines ran 3-6 px off the painted twigs
  (blue on one side, red on the other all along). Snap each traced point across to the middle of the painted run
  and take its half-width from the painting (`twigs.snap`).
- **A card turned square to the painting still shows a sliver from the front** if it is a degree or two off: keep
  crossed cards at exactly 90 degrees (+-1.5) where the painted gaps must stay open (banana crowns).
- **A plant behind must have its card's foot where the painted foot is**: a card cut down to the painted foot but
  stood on the bed's top (a few px lower) shows its crown below the painted one, in every gap.
- **The record's lift is the model's lowest point, cards included**: a hidden part (an anchor) or a transparent card
  bottom reaching below the painted foot sets the lift wrong (a 1 mm anchor under z = 0 gave lift 0 and left the
  tufts hovering 1-1.5 cm). Put the lowest part exactly at the painted foot (1 mm under it) and end every card's box
  at the lowest painted pixel; check the record's lift after the build.

## Round 3: paintings drawn from above (crop_strip_2, pebbles, pebble_cluster, K.oblique)

- **An object's matrix cannot hold a shear**: Blender keeps only location, rotation and scale, so a shear set on
  `matrix_world` turns and stretches the model instead (k 0.58: (0, 1, 0) went to (0, 1.12, 0.30)). Shear the mesh
  data (the lead fixed the audit's oblique front this way). Check any oblique comparison against a hand computation of
  z + k y for one part before trusting it.
- **Choose the slope from the painting's own geometry**: a field's top of known depth (painted depth / real depth:
  crop_strip_2 0.35); loose stones: the slope that makes them about as deep as wide in plan (pebbles 0.58, the cluster
  0.73). The stones' heights do not depend on the slope (only their plan depth does).
- **A thing painted from above stands at depth = (its painted foot's rise) / k, plus its own radius** (the painted
  foot is the front of its foot circle), and its real height is its painted height less k times that radius.
- **Lying stones on an oblique painting** (`lying_stone`): build each column of the painted outline as a section:
  foot on the ground at the painted bottom's depth, back mirrored about the line through the painted left and right
  ends, height solved so its top, seen along the slope, is the painted top. Cap the depth only where the painted top
  leaves no room (85 %), or round pebbles get flat, D-shaped backs; ellipse sections stand taller than boxier ones for
  the same outline.
- **Take a solid's outline from the whole painted alpha** (shared ink lines split to the nearest part), and pull it in
  by the game's ink only where the game draws it (top and sides), not at a foot standing on the ground (red line under
  every stone otherwise).
- **On a low slope every standing thing hides a long strip of ground behind it** (k 0.35: a 0.18 m hill hides 0.5 m).
  The kit's projection cannot reach it and it falls back to the own material: pale strips from every side. Give the
  ground's own material the painting along the slope from an earth-only source (standing things inpainted,
  `cv2.inpaint`), and paint the standing things with their own oblique materials (`slope_earth`, `wrapped(oblique=k)`).
- **Excluding things from a projection along a slope stretches whatever lies just outside the exclusion** by 1/k
  (a painted outline 1 px outside a stubble's box became a long dark line on the ground): exclude with a 3 px margin.
- **Turned cards on an oblique model** (a fan of ears and its turned copies): move every vertex down by k times how
  far back it is from the card's axis, so each copy lies on the painted fan along the slope.
- **Mirrored front and back meet in chevrons** where the painted strokes slant (a stook's flanks): blend a squared,
  unturned quilt from the thing's upright middle over the sides (50-75 degrees round) (`wrapped(side=)`).
- **Wide paintings bend their ground** (curvilinear perspective): crop_strip_2's field top is painted 86 px deep in the
  middle and 25 px at the ends. Follow the painted back edge (the field rounds off at its ends) and bulge it behind a
  back stook only within that stook's painted width at the back edge's row, so the bulge stays hidden from the front.
- **Measure each stook's bell row by row against the sky**: the painted bells are wider than a cone, five axes were
  2-5 px off and three feet up to 13 px off. A painted thing whose foot is hidden behind a stook must stand behind that
  stook; check every placed part for collisions with the others.
