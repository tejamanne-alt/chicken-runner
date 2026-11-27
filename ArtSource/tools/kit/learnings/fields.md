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
