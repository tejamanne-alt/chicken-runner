# New lessons from the palms_plants audit (append to LEARNINGS.md)

## Texturing
- **The front projection paints the ink outline down the sides of round parts.** `K.front_min` (default 0.25) lets
  faces turned up to ~75 degrees from the camera take the painting, so the painted outline at a trunk's silhouette
  shows as a dark wavy seam down its side (h4_1 left view). On models with trunks, stems, pots, boulders set
  `K.front_min = 0.55`: the squeezed own-material carries the sides, the toon outline draws the edge.
- **Decal quads get the game's ink outline.** A patch of fallen plaster or a crack as `K.quad` + decal is a separate
  thin surface: the ink shell draws a dark frame round it, so it reads as a little door or window (h7_4's back). Lay
  such patches on as cut-out cards (no ink line; only the painted brick shows, with its ragged edge:
  `palms_plants.patch_card`) or cut them into the face.
- **A boulder's back and ends**: a tile cropped from the painted top repeats as horizontal bands. Project the boulder's
  own painted pixels straight through it (squeezed to its axis) on faces looking along y, and blend into a tile of
  the same stone by the face normal on its ends and top (`palms_plants.round_material`).

## Cards
- **Crossed tuft cards (yaw 0 and +-60) are doubles from the front**: the turned cards show the painted tuft squeezed
  to half its width beside itself, a ghosted grey haze over the grass. Wrap each tuft round its own upright axis
  (front and back halves of a squat cylinder, `palms_plants.tufts` / `wrap_card`): from the front exactly the
  painting, round from the side.
- **A tuft card's box must hold the whole tuft.** Boxes drawn round the base of the grass cut every blade with a
  straight edge (h6_1, h5_5: the boxes were even beside the painted tufts). Measure the tuft on the grid; the mask
  cuts the blades, not the box.
- **`binary_opening` on a leaf mask erases thin spiky tips** (the palmyras' fan leaflets, 2-3 px at that scale):
  the fans lost their spiky outline. Drop specks by connected-component size instead.
- **A frond ribbon centred on its painted spine misses the leaflets hanging below the rachis** (red along every
  frond's lower edge). Fit each side's width to the painted leaf mask, out along the perpendicular to where the leaf
  ends, allowing small gaps between leaflets (`palms_plants.fit_widths`; front holes 0.09 -> 0.04).
- **Volume cards cut at their own spot give banded side views**: from the side a bush shows only the colours along
  the painted outline's edge (rows of flowers, rows of leaves). Cards turned side-on (edge-on from the front, so
  they hide in the crown there) may carry a patch from anywhere inside the painted crown (`side_cards`).
- **Cards turned far from the front show displaced content through the gaps** of a sparse plant (oleander,
  jasmine): keep volume cards within ~30 degrees of facing front and let the side-on cards give the depth.
- **Grass clumps wrapped round one axis are mirror images from the side** (a Rorschach blot) and their cross cards
  ghost the front. Build a clump from its own blades: trace the painted blades (`trees.blades_cover`) and lay one
  card ribbon along each, leaning out of the root into the depth (`palms_plants.blade_cards`).
- **Copies placed round the back must clear the solid**: ferns "behind" a boulder at a radius inside it were hidden,
  the back bare. And a copy cut from a box that stops above the ground floats when stood elsewhere: use boxes that run
  down to the plant's root.
- **Turned frond copies must fit the painted leaves, not the whole alpha**: a copy tested against the painting's alpha
  can lie over a trunk or a gap between crowns and show there from the front. Test against the leaf mask (dilated a
  little) and ask 95 percent.

## Geometry
- **A cap stone sloped up to the back to show its painted top is a slope to match perspective** (h7_4): level it,
  give it a low hipped top, and accept the painted top band missing from the front.
- **Earth discs under plants the painting stands on nothing** spill a brown band below the painted foot and read as a
  flat plain disc from the sides and above; leave them out unless the painting has earth (then tile it).

## Added during the later rounds
- **Colour masks see the rgb of transparent pixels.** A cut-out's fully transparent pixels still hold colours (often
  the green of the leaf they were cut from): a colour test (`leafy`, `g > r`) without `& alpha` marks them as leaf, so
  anything fitted or measured on the mask runs out into empty space (h5_2's fronds were fitted 40 px past their
  torn tips). AND every colour mask with the painting's alpha.
- **A tube as wide as the painted trunk is wider than the painting in the game**: the painted width includes its ink
  line, and the game draws its own outline (3-12 mm) outside the solid. Take the outline's width off painted radii of
  trunks and stems (`palms_plants.ink_px`, about 1.5 x the outline), less where a voxel fuse shrinks them anyway.
- **Patches laid on the back of a solid (brick showing through plaster, cracks) as cut-out cards need texture that
  no other card shows**: a card's box in the painting is shown by every card rule covering it. Copy the patch into an
  empty corner of the leaves texture (the painting) and point the card there (`palms_plants.stash`).
- **A side-on card in a bush (edge-on from the front) still has width in depth**: wider than the crown's depth there,
  it sticks out of the crown's sides as a flat sliver. Clamp it to the crown's depth and bank it about the line of
  sight so it also reads from above.
- **Turned copies of the painted fans/leaves round the back of a crown**: a mirror image front to back of a fan
  seen from the side looks like an ink blot (h7_1's colocasia). Turn the copy half round the heart instead (still
  tested to lie over the painted crown from the front).
- **Tufts wrapped round an axis at full depth are hollow rings** from the side and from above (a fern clump as an
  upright tube, h7_5). Keep the wrap shallow (depth about 0.35) and put one card through it side-on.
- **Leaves painted over a pumpkin (or any solid) must be in front of it**: cards placed at the trellis depth lay
  behind the pumpkins hanging in front of it, and the pumpkin hid the painted leaf (h5_6). Place a card over a solid
  in front of that solid.
- **`np.interp` needs its sample points increasing.** Interpolating x along a hooked stalk by py (the stalk rises,
  then hangs) silently gives nonsense, and the banana hands were placed beside the painted bunch. Interpolate along
  the monotonic part (from the hook's top down) or by arc length.
- **Fitting a frond's width "out along the perpendicular until the leaf ends" runs into the next frond** where
  fronds overlap or a torn banana leaf's strips slant: give every painted leaf pixel to its nearest painted spine
  first, then take each side's width at a station as the farthest of that spine's own pixels lying across from it
  (`palms_plants.fit_widths_owned`; banana front holes 0.16 -> 0.08, bottle palm 0.02 -> 0.004 in the coverage test).
