# The nine levels

Every level is designed beat by beat in `ArtSource/tools/levels/levelN.py`, on the shared `levelkit.py`, and audited
with the game's own numbers before the game is built from it. Build Game (`GameBuilder.Plans`) lays one chunk per
section of each plan, with the same `Kit` calls the hand-written chunks use, so the plan only says where things go.

| Level | Zone | Course | New | Beat sheet |
|---|---|---|---|---|
| 1. Pots and the sleeping dog | Lane, 6 m/s | 500 m | the basket intro; the jump | [level1.md](level1.md) |
| 2. Washing day | Lane, 6 m/s | 500 m | the slide (clotheslines); the rope-cot bounce | [level2.md](level2.md) |
| 3. Up on the roofs | Lane, 6 m/s | 500 m | ladders, rows of houses, gaps; a cot onto a roof | [level3.md](level3.md) |
| 4. The canal | Fields, 7 m/s | 600 m | canals of 2.5, 3.5 (the plank) and 4.5 m | [level4.md](level4.md) |
| 5. Mango trees | Fields, 7 m/s | 600 m | branch routes; haystacks and carts as steps up | [level5.md](level5.md) |
| 6. Buffalo and haystacks | Fields, 7 m/s | 600 m | the buffalo bounce; haystack chains | [level6.md](level6.md) |
| 7. Rooftop run | Terraces, 8 m/s | 700 m | long roof runs, gaps, water tanks | [level7.md](level7.md) |
| 8. Market day | Market, 8 m/s | 700 m | awnings to bounce along; flocks of hens | [level8.md](level8.md) |
| 9. The temple steps | Temple, 8 m/s | 800 m | temple steps; everything once more | [level9.md](level9.md) |

```bash
python ArtSource/tools/levels/level4.py --report     # the Blender venv's python; writes Art/Levels/level4.json and level4.md
```

## What the audit checks

`levelkit.audit` reads the zone's tuning (`ChaseTuning` with `ForZone`'s overrides), the jump maths (`JumpMath`) and
the kid's body (`KidController`: radius, ground-ray inset, step and slide heights) from the C#, and flies the kid's
feet through held, tapped and double jumps. A plan fails if:

- a jump has under 0.2 s to take off and clear an obstacle (a held jump), a canal, a roof gap or a buffalo's back;
- after clearing one thing at the latest moment, there is under 0.5 m left to react (0.3 s) and still clear the next;
- two things to jump stand under 4.5 m apart;
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

- **Spacing grows with speed.** At 6 m/s two pot stacks need about 6.5 m start to start; at 8 m/s, 8 m (a held jump
  is 4.9 m long and reacting takes 2.4 m). A tank needs 7 m before a roof gap and 7 m into the row after one.
- **Rows after gaps must be long.** A latest-moment jump across a 2 m gap lands about 3 m into the next row; a row
  shorter than that is jumped clean over.
- **Bounces carry far.** A cot's 2.4 m bounce lands about 5 m on at 6 m/s; the buffalo's 2.6 m bounce about 7 m on
  at 7 m/s; leave that room, and reaction room, after them.
- **The rooster's hops are sines.** A hop as high as an obstacle at its middle is lower at its edges: size it from
  the edges ((top + 0.25) / sin(pi * run-up / length)). The audit found `Kit.Haystack`'s hop passing inside big stacks.
- **Standing litter reads as an obstacle.** Tufts, husks and pebbles (volume models) stay 0.9 m off the running line;
  flat leaves and prints may cross it.

## The view and the road

The camera frames as Kick Off's does (`ChaseCamera`): 34 degrees, about 10 m back, 5.4 m of height at the lane, the
kid on the left third and about a fifth of the screen tall, following the ground she runs on. Each zone's village road
runs along the lane (`PaintedGround`'s road band, tiles from `ArtSource/tools/models/road_textures.py`): the lane's
hardened mud street, the fields' cart track, the market's cement road, from z -2.4 to z 1.0, with mud side lanes back
between the houses.
