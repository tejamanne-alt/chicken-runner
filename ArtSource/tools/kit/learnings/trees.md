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
