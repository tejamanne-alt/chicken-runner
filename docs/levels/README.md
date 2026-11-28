# The nine levels

Every level is designed beat by beat in `ArtSource/tools/levels/levelN.py`, on the shared `levelkit.py`, and audited
with the game's own numbers before the game is built from it. Build Game (`GameBuilder.Plans`) lays one chunk per
section of each plan, with the same `Kit` calls the hand-written chunks use, so the plan only says where things go.

Every level runs at a small child's real pace, 3.5 m/s (Kick Off's kid's pace on screen), and everything in the road
is something a village street really has: a dog asleep in the dust, the puddle round the hand pump, cow dung, hens,
ducks and a goat kid crossing, the potter's pots drying, a heap of sand where a house is going up, sacks of paddy
waiting for the cart, a neem's low branch. No carts parked across the road and no washing strung over it: the kit
refuses both.

| Level | Zone | Course | New | Beat sheet |
|---|---|---|---|---|
| 1. Pots and the sleeping dog | Lane | 290 m | the basket intro; the jump | [level1.md](level1.md) |
| 2. Washing day | Lane | 290 m | the slide (a neem's low branches); the rope-cot bounce | [level2.md](level2.md) |
| 3. Up on the roofs | Lane | 290 m | ladders, rows of houses, gaps; a cot onto a roof | [level3.md](level3.md) |
| 4. The canal | Fields | 295 m | irrigation channels of 1.2, 1.8 (the plank) and 2.6 m | [level4.md](level4.md) |
| 5. Mango trees | Fields | 295 m | branch routes; haystacks and sacks as steps up | [level5.md](level5.md) |
| 6. Buffalo and haystacks | Fields | 295 m | the buffalo bounce; haystack chains | [level6.md](level6.md) |
| 7. Rooftop run | Terraces | 300 m | long roof runs, gaps, water tanks | [level7.md](level7.md) |
| 8. Market day | Market | 300 m | awnings to bounce along; hens and their baskets | [level8.md](level8.md) |
| 9. The temple steps | Temple | 340 m | temple steps; everything once more | [level9.md](level9.md) |

```bash
python ArtSource/tools/levels/level4.py --report     # the Blender venv's python; writes Art/Levels/level4.json and level4.md
```

## What the audit checks

`levelkit.audit` reads the zone's tuning (`ChaseTuning` with `ForZone`'s overrides), the jump maths (`JumpMath`) and
the kid's body (`KidController`: radius, ground-ray inset, step and slide heights) from the C#, and flies the kid's
feet through held, tapped and double jumps. A plan fails if:

- a jump has under 0.2 s to take off and clear an obstacle (a held jump), a canal, a roof gap or a buffalo's back;
- after clearing one thing at the latest moment, there is under 0.5 m left to react (0.3 s) and still clear the next;
- two things to jump stand under 0.7 s of running apart (2.45 m at 3.5 m/s);
- the rooster has no hop over something in the lane, or his hop passes inside it (0.15 m clear of its top), or he has
  no flutter up onto a roof row, across a gap or down off its end;
- a roof row has no way up (a ladder, a gap from the row before, or a rope cot just before it);
- a row after a gap is short enough to be jumped clean over, or a tank stands too near a row's ends;
- a chilli's boost (2.2 s at +35%) runs into the next obstacle;
- a mango sits inside a wall, a roof or a stack, or a feather is out of reach of a double jump (or a bounce);
- a mischief spot's target is not there or not hidden; the three feathers are not all there.

It also checks, once the builder runs, that roof rows, haystacks, stalls and the buffalo come out exactly as wide as
the plan placed them (from the same picture sizes), and logs an error if not.

## Rules of thumb it taught

- **Spacing follows the pace.** At 3.5 m/s two pot stacks need about 4 m start to start (a held jump is 2.2 m long
  and reacting takes 1 m): the 6.5 m of the old 6 m/s design, in the same seconds.
- **Small things only, at a child's pace.** The jump keeps its time in the air at any speed, so at 3.5 m/s it covers
  less ground: a held jump clears 0.9 m of puddle, a curled-up dog or two hens with a fair window, not three hens
  abreast or a 1.6 m puddle. That is also what a small child can really jump.
- **Rows after gaps must be long.** A latest-moment jump across a roof gap lands well into the next row; a row
  shorter than that is jumped clean over.
- **Bounces carry.** A cot's 2.4 m bounce lands about 3 m on at 3.5 m/s; leave that room, and reaction room, after it.
- **The rooster's hops are sines.** A hop as high as an obstacle at its middle is lower at its edges: size it from
  the edges ((top + 0.25) / sin(pi * run-up / length)). The audit found `Kit.Haystack`'s hop passing inside big stacks.
- **Standing litter reads as an obstacle.** Tufts, husks and pebbles (volume models) stay 0.9 m off the running line;
  flat leaves and prints may cross it.

## The view and the road

The camera frames as Kick Off's gameplay does on a phone (`ChaseCamera`, measured from a screenshot of it): the kid
24% of the screen tall, her feet 17% up it and 40% across, following the ground she runs on; for the 1.08 m kid that is
34 degrees, about 7.3 m back, 4.5 m of height at the lane. Each zone's village road runs along the lane
(`PaintedGround`'s road band, tiles from `ArtSource/tools/models/road_textures.py`): the lane's hardened mud street, the
fields' cart track, the market's cement road, from z -1.25 to z 2.05, which fills the screen from 9% to 27% of its
height as Kick Off's pavement does, with mud side lanes back between the houses.
