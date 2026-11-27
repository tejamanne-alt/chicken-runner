# New lessons from the trees audit (module trees)

- **A traced tube is only as thick as the circle inside the painted outline.** A braided, fluted or knobbly trunk
  traced to its medial axis came out a third too thin from the front (red down both sides of every trunk). Loft the
  trunk through its painted rows instead (`trees.trunk_runs` + `trees.loft_trunk`: each row a ring as wide as the
  painted trunk there), held to the trunk's own width where limbs or roots leave it, flaring only towards the ground,
  its top rounded off into the limbs (a flat cap shows as a ring seam).
- **Rotated leaf cards move the painting.** A card turned about its centre shows its pixels squeezed and shifted from
  the front, so an airy crown (sky between the leaves) became a muddy blob and a dense one lost its outline. Shear the
  card into depth instead (`trees.sheared_card`: every vertex at its painted x, z, only y varies): whatever its depth
  or turn, from the front it is exactly the painting. A slope near 1 (a 45 degree turn) shows the leaves at their own
  size from the side; below 0.5 it is a sliver, above about 1.6 its leaves drag into horizontal streaks.
- **Place the front shell by coverage, not at random.** Pick each front card's centre on a painted leaf pixel no card
  covers yet, until 99.6 % are covered (`Crown.cards` "front"/"back"): random placement left holes along the crown's
  edge.
- **A grey-bark colour rule also catches the shaded leaves of a grey-green crown** (h1_x: low saturation, dark). Test
  the leaves' own tint (g - b above about 10-26, or g above r) to keep them out of the wood mask, or the trunk grows
  blobby tubes in the crown and the leaves there go missing.
- **Subtract the traced wood (dilated) from the crown's leaf mask.** Some painted bark is as green-grey as the leaves;
  a card carrying it into the crown's side shows as a pale grey streak under the crown.
- **Bark projected through y smears on the sides, and on a leaning trunk squeezed about the wrong axis it picks up the
  ink outline as a black stripe.** `trees.bark_mix`: the painting squeezed towards the nearest point of the wood's own
  centre line (works for any lean or limb direction), used only where the squeezed sample lands on painted wood and
  only on faces turned front or back (|normal.y|); a seamless tile of the painted bark everywhere else.
- **Roots given a random depth each cross like sticks from the side.** Lean each root into depth in proportion to its
  painted run across (alternating sides), and put a copy of each straight behind it (same x, z, depth scaled at
  random): from the front hidden, from above a fan, from the side a flare.
- **An earth disc in a plain colour is an untextured slab from the side and above**, and set at the painted ground
  line it floats 15-30 cm above the frame's bottom on the big field trees. A painted band of red earth is a low mound
  (`trees.mound`): its rim at the band's front edge (the model's foot, within the 10 cm lift), its middle part way up
  the band, a squared tile of the painted earth all over; stones and roots set on its surface (`height(x, y)`).
- **A platform painted from above with its top receding (h3_1's diamond katte) must still be level.** The things
  standing on its painted top then stand lower than painted: give each its own projection of its painted place moved
  down with it (`K.projected(..., dz=...)`) and put both its painted box and its new box in `K.front_exclude`, so
  neither it nor the trunk behind it gets the wrong pixels from the front.
- **Frayed rope ends as 1 mm tubes read as four stiff black legs under a swing seat**: crossed cards of the painted
  fray.
- **Sheared cards are for the shell only.** A crown of cards all sheared into depth is exactly the painting from
  the front, but from the side and above the deep ones drag their leaves into horizontal streaks. Shear the front
  and back shells (each at least 0.45 into depth, or it is a sliver from the side, at most 1.0), and turn the
  volume cards inside truly (rotated about their centres): the shell hides them from the front, so their turn does
  not change the painting, and from the side their leaves are at their own size.
- **Twigs too thin for tubes go on the cards**: the wood mask minus its opening by the tube radius (`min_r_px`) is
  added to the leaf mask, or the painted twig tips are missing (red) from the front. Thin tubes under 2 cm read as
  black lines anyway (the drumstick trees' twigs).
- **Hand-traced limb strokes reach over the sky painted between limbs**: clip each stroke's radius to the distance
  to the painting's edge (not sky, not halo) at that point (`_peepal_tree.fit`). Not the trunk where something is
  painted in front of it (the shrine): there the painting's edge is the shrine's, and the trunk became a spindle.
- **Limbs turned towards the camera poke out of the trunk as pale stubs from the front**; turn the copies only to
  the sides and back (the front shell of cards hides the crown's front half anyway).
- **Painted pebbles and earth round a root's tip are projected onto the root reaching over them** (white claws on
  the banyan's roots): make the ground band transparent in the projection source outside the (dilated) wood mask,
  after the mound and stones have taken their tiles from it.
- **Loose bits of root painted apart at the foot** (tips showing between grass) become loose sticks on the ground:
  keep only the mask components joined to the trunk below the root line.
- **Cards that carry what solid blades leave of a painted rosette** (thin tips, ink) belong at the depth of the blade
  nearest to them (`trees.blade_depth`), not at a random depth in the shell, or they float beside the plant.
- **A strip of earth mirror-stacked into a square makes rows of the same pebbles (a herringbone)**: quilt it
  (random feathered patches, wrapped) instead (`trees.strip_tile(..., quilt=True)`).
- **Low plants on cards at independent random depths read as patches hanging at every depth** from the side; give
  neighbouring cards a shared depth (a slow wave along x, `trees.clumps`) so they read as clumps.
- **A crown with sky painted between its limbs** (the shrine's peepal): nothing hides a turned volume card or a
  limb copy that reaches into such a gap. Keep rotated volume cards a card's size away from large interior gaps
  (`Crown.avoid_gaps`), end a turned limb copy where its point cannot hide, and make each copy (and any thread loop
  round a limb) no thicker than the painting is solid where it shows from the front (distance to the nearest sky or
  halo pixel). Only for crowns with real painted gaps: on an airy crown (field_tree_2) the same rule blocked two
  thirds of it.
- **Touching pods (or fruit) painted in a bunch skeletonise as one fat pod.** Trace those bunches by hand off the
  grid and build them as drawn (no polyline smoothing, which squared their rounded ends).

## Round 2 (shrine_tree)

- **Find which part shows where with a part-ID pass, not by guessing.** Build the parts (with `K.fuse` patched to a
  no-op, so every tube stays its own object), give each a flat emission colour that encodes its index, render the
  front orthographic in the painting's frame (Cycles, 1 sample, denoising off, box filter 0.01, view transform Raw),
  and count the IDs over the painting's sky pixels. The shrine's "band of wood in the sky" was found in one render.
- **A turned limb copy checked only at its points jumps across a painted gap.** Two points either side of the sky
  can both hide behind painted wood while the straight tube between them crosses the sky (a 40 x 80 px band of bark
  left of the tower). Check every few px along each stretch and end the copy where the stretch would show; taper a
  copy cut short into a tip (`_peepal_tree(seg_hide=True)`), or it ends in a sawn-off disc under the crown.
- **A chain of discs is wider than the tube it stands for.** `raster` draws each stroke point as a disc; where a
  fitted radius grows fast, the discs reach back along the stroke past the tube, so the crown's cards left out
  crescents of painted wood the tube did not cover (red). Leave out exactly the tube's outline (`raster_tubes`).
- **Fit a limb that borders painted sky by moving its centre, not only its radius.** Clipping a traced radius to the
  distance to the nearest sky kept the traced centre, so a limb with sky on one side came out as thin as that side
  allows on both (sky along it). `fit_limb` measures the painted run across the limb at every 8 px (each side no
  further than the traced radius), centres the tube in it and takes half of it less the game's ink line. Limbs with
  skeins of thread hanging under them are fitted against the painting with the gaps between strands closed
  horizontally, or the halo between strands thins the limb.
- **A trunk hidden behind something is still seen from the back: give it relief that the toon look shows.** Lofted
  through its painted rows where sky bounds it (`trunk_rows`) and free below the shrine's roof, the trunk read as a
  plain column until its ribs stood out by their whole radius: ribs (stems grown together, winding a little, their
  feet flaring into buttresses) with their axes on the trunk's surface fold away at their flanks and get contour ink
  lines from the sides and back; ribs sunk halfway in read as a smooth cylinder. Keep every rib inside the painted
  width where the trunk shows from the front.
- **Things hung on a crown's wood (skeins of thread) do not belong on the crown's cards.** Any front-shell card whose
  box reached them carried strands out to the crown's front, 2 m before the trunk. Copy their pixels into an empty
  corner of the painting, cut their own cards from the copy (`sheared_card(uv_shift=)`), and keep them out of the
  crown's leaf mask; place each at the depth of the trunk or limb it hangs from.
- **Keep turned volume cards off painted gaps by their footprint, not by a margin.** A margin of a card's size round
  every gap (`avoid_gaps`) left the shrine's crown hollow in the middle (seen from the side) once its smaller gaps
  counted; checking each card's turned box against the painting's sky and halo (`gap_exact`) keeps cards right up
  to the gaps and none in them.
- **Flat top cards are horizontal streaks from the side where the crown is sparse.** Tip them 25-30 degrees (each
  its own way: `top_tilt`) and keep them near the top surface (`top_u`); once tipped they show from the front, so
  keep each below the painted top along its whole turned width.
- **Closed tube loops waste the atlas.** Threads round a trunk unwrapped into ring-shaped islands whose empty middles
  took about a fifth of a 2048 atlas, and short tube arcs with their island margins took more; three-sided closed
  loops (no face lying flat) unwrap into a few thin arcs. Drop faces nothing sees (bottom caps on the ground, the
  trunk inside the shrine, the earth under it, tier bottoms on the roof: 150 to 115 m2 here): the painting on what
  is seen gets sharper.
- **Small turned things painted in front are traced, not generic.** A generic finial lathe drew a zigzag ink outline
  over five pot-and-bud finials, the bell was a cone, and a tube through a few points made the marigold swag a stiff
  W: trace each profile off the painting (radii less the ink line) and string a garland as balls along its traced
  swag.
- **The painted foot is the earth's front edge, for every part.** The shrine body, threshold and trunk start there;
  the voxel remesh pushed the fused trunk's roots 7 cm below it (lift 0), so clamp fused wood to the foot. A
  mound's halo cleaning also clears a white wall standing on it from the projection (`mound(keep_boxes=)`).
