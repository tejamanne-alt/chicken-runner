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

## Round 2 (h5_2, the torn banana)
- **Most of a cut-out's "front holes" round leaves can be its pale fringe, not the geometry.** The cut-outs keep a
  1-2 px opaque pale-grey rim outside the painted ink line (and grey between ink and rim); leaf masks drop it as halo,
  so every leaf edge reads red: h5_2's crown lost 7 % of its painted pixels that way, the ribbons only 0.5 %. Take the
  opaque pixels within 2 px of the card mask that it leaves out, paint them over in the painting (`P.img`) with the
  ink beside them, and add them to the mask (`palms_plants.fringe`, with an `allow` mask so the stem, fruit and stone
  beside the leaves are not inked). Measure this first: split the holes into "not in the mask" and "in the mask but
  no card there". Rasterising the built parts, and the cards through their UVs against the leaves texture, onto the
  painting's frame (the game's ink grown round the solids) predicts the audit's holes and spill in seconds, no bake.
- **A torn leaf is one card cut by its own pixels, not a ribbon.** A ribbon's straight edges cut across slanting
  strips and their tips; widening it shows other leaves through its gaps at its depth. Give every painted pixel to
  one leaf (regions cut apart by the ink outlines, each to the spine running through it: `leaf_owners`; nearest-spine
  alone hands a strip hanging below one midrib to the leaf below and splits it in depth), then cover exactly those
  pixels with a grid of small cells whose vertices sit at their painted (x, z) and at the depth of the leaf's shape
  there (station along the midrib, distance across it: `StripCard`, `leaf_depth`). Cells that would also show a
  neighbour's pixels split into 2-3 px sub-cells (no confetti from the side); the coarse cell beside takes the split
  edge's vertices (no T-junction cracks). h5_2: front holes 0.08 -> 0.012, IoU 0.89 -> 0.97.
- **Trace midribs where they are painted**: a banana leaf spreading sideways has its midrib along its upper edge, the
  strips hanging below it; spines drawn through the middle of the strips fold the leaf in the wrong place.
- **A piece of a leaf cut off from its midrib in the painting (the join hidden behind another leaf) floats from the
  side** at its own leaf's depth: give it to the leaf it touches most (it then lies on that leaf).
- **Ink, do not open, the haze in a torn leaf's narrow slits.** Left out of the mask, each slit reads as a row of red
  specks along every tear (holes 0.012 -> 0.023); inked with the rim it reads as the painted line between two strips.
- **Copies round the back of a gappy crown: trim them cell by cell** to where the painting hides them (each shown
  texel lands on painted alpha and behind the front card there), keep the cells joined to the base. Aim each copy at
  its own bearing round the back: left to choose freely, the best-hidden copies all point straight back (edge-on from
  the front) and the crown is a Y from above.
- **Card faces must face the camera they are painted for.** A card whose winding faces away from the front gets its
  shading normal flipped by Cycles, and the audit's toon shades it as if lit from behind: the whole crown came out a
  shade darker (colour median 2 -> 9). Wind cell quads counter-clockwise as seen from the front.
- **A tube along a slanting centre line tips its rings**, and a tipped ring reaches past the painted outline above and
  below it (blue under the bunch). Stack level rings from the painted rows instead (`row_solid`): the stem's sheath
  tips and the bunch's outline then match row by row.
- **Grass masks: greener than red.** `leafy`-style tests pass the beige stone tops and the olive stem inside a tuft's
  box, and the tuft card carries them off into the air beside the solid; and blades end in long inked tips (keep the
  dark pixels within ~12 px of a blade, above the stones, off the stem's outline).
- **A banana bunch = its painted body (flattened, from the painted rows) + the painted bananas traced one by one as
  tubes lying on its front + more fingers round its back kept inside the outline** (the narrowest row a finger rises
  through holds it). Generic rings of fingers round the stalk never match the painted outline.
- **A stem's sides wrapped by angle, not squeezed through.** `axis_material` (the painting pushed through along y,
  squeezed to the axis) drags the painted sheath edges near the outline round the sides as a pale U-shaped arch
  and bands; wrapping by angle (`wrap_material`: straight on to 64 degrees, then the painted half laid evenly round)
  shows the sheaths' own diagonal lines going round the stem.
- **What is not leaf but lies beside a leaf rides on that leaf's card** (the inside of a stalk's hook, fruit tips
  above a bunch, the stalk between them): it is given to the nearest leaf and stands at that leaf's depth, a dark
  dash floating beside the bunch from the side (h5_1). Keep it off the card mask (`banana_torn(cut_polys=...)`,
  the bunch's own outline rather than an ellipse round it) and model it, or leave it as haze.
- **A trimmed copy keeps one piece**: the cells left between the hidden ones fall into scraps near the base, and
  each scrap floats on its own from the side. Keep only the largest piece joined to the base.
- **Strip cards scale with the leaf**: broad, little-torn leaves (h5_1) take 8 px cells (4 px where leaves meet),
  narrow torn strips (h5_2) 6 px (3 px); h5_1's front holes 0.06 -> 0.008, IoU 0.93 -> 0.985, at 12.8k faces.
- **A tube traced on a painted stalk is as wide as the painted run including its pale rim**: the audit counts the
  rim as painting, so a tube of the inked width alone leaves red on both sides; add 1-2 px to painted radii of
  stalks and fruit, and run traced fruit 2-3 px past their measured tips to the ink.
