# New lessons from the fields audit (fields.py)

- **Grain-only stone goes pale and plain.** Taking only a patch's fine detail (the patch less its blur) and laying it
  on its median colour neutralises the painted tones: the canal slabs came out pinkish-beige and nearly plain. Keep
  the painted patch itself (its blotches and darker edges) and only flatten the light falling across a thin strip
  (`fields.quilt(..., flatten=)`, `speckle(sigma=None, flatten=)`); give the sides the painted side face's darker
  stone, not the top's.
- **Turning a whole three-quarters building**: build it square in painted coordinates, then transform every part
  (and its cutters, `with_cutters`) by T(corner) R(-phi) S_x(1/cos phi) T(-corner) about the nearest corner: the turned
  front lands back on the painted front, the side's projected length is D sin phi (pick phi from the painted side's
  width), and nothing else in the builder changes (`field_bldg_2`, `field_bldg_3`). Leave props painted in front
  (a ladder, heaps) out of the transform. Remove the front exclusion of the side: it is real now.
- **A regular pattern (brick bond, coursed stone) must be sampled once.** `K.tile`'s two blended scales ghost a
  regular pattern into doubled half-bricks; use a single-sample box projection whose z offset lines the courses up
  with the painted ones (`fields.pattern_tile`). Build the bond from the painting's own bricks or from random
  patches of the painted wall with its joints filtered out (`fields.brick_bond(source=delined(...))`).
- **Thin ink lines inside a tile crop repeat as a grid** (bank hatching, cracks, wall joints): median-filter them out
  first (`fields.delined`), keep the blotches.
- **Projected solids cut from a section** (canal banks, rocks): project the painting only on faces turned to the front
  and back, and tile the rest (`fields.proj_tiles`); a projection on the cut ends or tops drags one column into
  streaks. Blur the fill outside `keep` (`fields.filled_source`) or it radiates streaks.
- **Long thin strips quilted** (squares cut from the strip, each turned a random quarter turn, feathered: `fields.quilt`)
  give a direction-free tile for a surface turned in plan; but squares under ~12 cm with strong contrast read as a
  checker grid on small parts (granary staddles): use rolled-row `speckle` there.
- **Patches of plain colour under props** (earth discs under haystacks, well, scarecrow) read as flat plain faces from
  every side and spill below the painting: drop them unless painted; when painted, tile them with the painted soil.
- **End caps of swept banks** smoothed with the faces round them shade as a pinwheel: split the cap's rim edges so it
  smooths on its own (`fields.bank`).
- **Water cut-out cards**: a leaf rule must drop the brick or rust painted round the water, and fill the painted
  translucency pinholes (`fields.water_pixels`), or the card shows red specks and holes.
- **The audit's `repeat` and `streaks` metrics** read a regular brick bond and real wood grain as repeats/streaks; look
  at the view before acting on them.

## Round 3 (paintings drawn from above, three-quarters on: canal_piece_2, canal_piece_3, field_shrine, granary)

- **Fit the slope, the turn and the sizes together, not one by one.** Draw each part's box hull along the slope
  (u = x, v = z + oblique * y) and maximise its IoU with the painted alpha plus a small weight on painted corners
  (slab ends, pier and step feet) by Nelder-Mead: k, the turn, every length and the origin come out at once and
  agree (canal_piece_2: k 0.281, turn 49.95, 18 corners within 5-10 px; canal_piece_3: k 0.292). Drop the painted
  ground line from the mask first. Then build the fitted numbers level and square. Fronts went 0.28 -> 0.91 and
  0.57 -> 0.96.
- **A Blender object's matrix cannot hold a shear**: `o.matrix_world = shear @ o.matrix_world` silently drops it (the
  audit's first oblique front did this: IoU 0.48 instead of 0.89). Shear the mesh data, and put it back after.
- **Take the painted ink out of what is projected** when the model matches only to a few px (`fields.deink`: thin
  lines darker than the paint round them, and the cut-out's rim, filled from the paint round them): an ink line
  landing 3 px off an edge reads as a dark stripe along a top seen from the side. `lines=False` keeps a wall's
  coursing and only drops the rim; `region=` limits it (a building's round posts).
- **A part drawn steeper than the rest of the painting's slope** (canal_piece_3's tray, in its own perspective) cannot
  take the front projection: map the painting onto it by its own painted corners (`fields.quad_mapped`: bilinear in
  plan between its painted top and foot corners) and exclude it from the front projection; where the level part is
  lower than the painted one, fill the strip with the painting just above it, reflected (`fields.strip_fill`), so
  the stone behind runs on and no painted rim lands on the wall.
- **A thing standing on the ground behind (a pot) goes back by its painted foot**: its foot ring's painted centre
  height / k is its depth; trace its profile and lower it by k * depth.
- **Three-quarters at eye level (no slope)**: turn about the front right corner with the 1/cos stretch, and give the
  painted right side to the real side face with its shade taken off (`fields.relight`: channel by channel to the lit
  material's median, at 0.8, the painted detail kept), not excluded: the side keeps its painted coursing, damp and
  tiles, and the toon light shades it. Place round and square parts (staddles, finials, caps) after the turn at
  their turned positions, or the stretch draws them out. Measure each tier's real half width from its painted
  outline row by row: (right - left) / 2 / (cos + sin).
- **Box projection smears a tile crop on a 45-degree roof slope** into orange mush. Lay a periodic patch of the
  painted tiles (sheared upright, cut at its painted column lines and row arcs, here 3 x 2 tiles) by each slope's own
  UVs, one texture column on each corrugation (`hip_roof(pattern=)`).
- **Flag and cloth cards**: drop the painted pole from the card's rule (left of the pole's line) and every speck under
  ~40 px (by component size), or a second pole and dots ride round with the card.
- `K.converge` was tried in the canal_piece_2 fit: c 0.03/m and no gain; these paintings are parallel views.
