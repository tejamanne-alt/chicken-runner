# Level 9: The temple steps

The beat sheet for level 9 (zone 3). It is written by `ArtSource/tools/levels/level9.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level9.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 3: the kid runs at 3.5 m/s, the rooster at 3.15 m/s; a held jump is 2.16 m long and 1.4 m high; the course is 300 m.

## The opening: the temple street

No basket: the chase starts in the temple street at festival time with the rooster 7 m ahead (the Ready screen;
tap to chase). The kid runs 3.5 m/s, a small child's real pace, and the rooster 3.15: a clean run catches him at
about 62 m. The course runs 340 m, the longest, about a minute and a half and a bit.

## The temple steps

* Five flights. Six steps of 0.25 m (low enough to walk up), a landing 1.5 m up with its lamps, six steps down:
  14.4 m in all, about four seconds of running.
* Mangoes along the landing; on two flights the festival's new clay pots are stacked up there, to jump; a feather
  above the first.

## The rest of the street

Three rooftop stretches (a ladder, a water tank, a 1.2 m gap, a second row, the drop), three rows of stalls to
bounce along, and only what lies in a real temple street, about 4 m (a second and a bit) apart: the vendors' hens
and their baskets, a goat kid, cow dung, the puddle round the hand pump, a dog asleep, sacks of paddy unloaded for
a shop, a heap of building sand, two neems by the temple whose low limbs she slides under, and the rooster's
mischief with a hens' basket. The washing lines across the street and the pot stacks in it are gone.

## The shape of it

The whole game once more on the way to the temple: steps, hens and a dog, a rooftop stretch, a neem, the awnings,
the mischief, steps with pots, hens, a goat and a basket, the roofs again, sacks, dung and a neem, steps then
stalls, a crowded street, the last rooftops, steps with pots again, the last awnings, everything once more, the
temple's own steps, and the temple court.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 6 | TempleStreet | 4 mangoes | The temple street at festival time: the rooster struts ahead; tap to chase. |
| 6 | 26 | FirstSteps | temple steps 9 to 23.4; feather 1 at 16.2, 3.6 m up; 7 mangoes | The first temple steps: up (walked), along the landing, and down. A feather. |
| 26 | 35 | HensDog | 2 hens 28.5; sleeping dog 32.5; 10 mangoes | Two of a vendor's hens, then a dog asleep in the street. |
| 35 | 53 | Rooftops | roofs 36.5 to 43.1 (ladder); water tank 39.8 on the roof; roofs 44.266 to 49.9; 18 mangoes | Up a ladder onto the terraces, a tank, a gap, and down. |
| 53 | 61 | Neem | low neem branch 57; 3 mangoes | A neem by the temple, its low limb across the street: slide. |
| 61 | 70 | Breather | chilli 61.5; 10 mangoes | A breather: mangoes and a chilli. |
| 70 | 83 | Awnings | stall 71.5; stall 75.656; feather 2 at 75.567, 4.7 m up; 6 mangoes | The flower and brass-vessel stalls: bounce along the awnings. A feather. |
| 83 | 97 | Mischief | hand-pump puddle 87.5; hens' basket 91.5 (knocked in by the rooster); mischief 92; 1 goat kid 95.5; 15 mangoes | The hand-pump puddle; the rooster knocks a hens' basket into the road; a goat kid. |
| 97 | 116 | StepsWithPots | temple steps 99 to 113.4; pot stack 106.2 on the roof; 7 mangoes | Temple steps with the festival's new pots stacked on the landing: jump them up there. |
| 116 | 125 | ChilliLane | chilli 116.5; 9 mangoes | A chilli to win back ground. |
| 125 | 138 | Flocks | 2 hens 128.5; 1 goat kid 132.5; hens' basket 136.5; feather 3 at 136.5, 2.9 m up; 15 mangoes | Two hens, a goat kid, the hens' basket; a feather over the basket. |
| 138 | 156 | RoofsAgain | roofs 139.5 to 146.1 (ladder); water tank 142.8 on the roof; roofs 147.266 to 152.9; 18 mangoes | The terraces again. |
| 156 | 170 | SacksDungNeem | sacks of paddy 158.5; cow dung 163.5; low neem branch 168; 10 mangoes | Sacks of paddy unloaded for a shop, cow dung, the second neem's low limb. |
| 170 | 179 | ChilliStraight | chilli 170.5; 9 mangoes | A chilli and a straight. |
| 179 | 208 | StepsAwnings | temple steps 180 to 194.4; stall 196.9; stall 202.243; 13 mangoes | Temple steps, then a row of stalls. |
| 208 | 225 | CrowdedStreet | 2 hens 211; hens' basket 215; heap of building sand 219; sleeping dog 223; 20 mangoes | Hens, their basket, a heap of building sand, a dog asleep. |
| 225 | 234 | FinalChilli | chilli 225.5; 9 mangoes | A chilli. |
| 234 | 252 | LastRoofs | roofs 235 to 241.6 (ladder); water tank 238.3 on the roof; roofs 242.766 to 248.4; 18 mangoes | The last rooftops. |
| 252 | 270 | StepsAgain | temple steps 253 to 267.4; pot stack 260.2 on the roof; 7 mangoes | Another flight, the festival's pots on its landing. |
| 270 | 282 | LastAwnings | stall 271; stall 276.552; 7 mangoes | The last row of stalls. |
| 282 | 303 | LastTest | 2 hens 285; 1 goat kid 289; hand-pump puddle 293; hens' basket 297; 1 hens 301; 25 mangoes | Everything once more: hens, a goat kid, the puddle, the basket, a hen. |
| 303 | 323 | TempleApproach | temple steps 305 to 319.4; 7 mangoes | The temple's own steps, the last flight. |
| 323 | 345 | TempleCourt | 12 mangoes | The temple court: if he is still ahead, he gets away at 340 m. |

## The audit

* a clean run from a 7 m start catches him after about 18 s, at about 62 m (without chillies)
* first of each: steps 9 m, hens 28 m, dog 32 m, ladder 36 m, tank 40 m, roofgap 43 m, drop 50 m, lowbranch 56 m, awnings 72 m, puddle 87 m, hensbasket 91 m, goats 95 m, pots 106 m, sacks 158 m, dung 163 m, sand 219 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
steps          9.0 m (FirstSteps): 6 steps up (walked), a 6 m landing 1.5 m up, and down
hens          28.1 m (HensDog): held window 212 ms, tap 21 ms
dog           32.1 m (HensDog): held window 207 ms, tap 19 ms
ladder        36.5 m (Rooftops): up the ladder (no input: she climbs in 0.45 s), onto the roof at 37.3
tank          39.6 m (Rooftops): held window 209 ms, a tap cannot clear it
roofgap       43.1 m (Rooftops): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
drop          49.9 m (Rooftops): off the end of the roofs (no input), landing about 1.4 m on
lowbranch     56.5 m (Neem): slide window 186 ms, double jump over 102 ms
awnings       71.5 m (Awnings): 2 stalls: run under, or jump into an awning and bounce along them (optional)
puddle        87.0 m (Mischief): held window 214 ms, tap 39 ms
hensbasket    91.2 m (Mischief): held window 216 ms, tap 12 ms
goats         95.3 m (Mischief): held window 270 ms, tap 74 ms
steps         99.0 m (StepsWithPots): 6 steps up (walked), a 6 m landing 1.5 m up, and down
pots         106.0 m (StepsWithPots): held window 226 ms, tap 13 ms
hens         128.2 m (Flocks): held window 213 ms, tap 21 ms
goats        132.3 m (Flocks): held window 270 ms, tap 74 ms
hensbasket   136.2 m (Flocks): held window 216 ms, tap 12 ms
ladder       139.5 m (RoofsAgain): up the ladder (no input: she climbs in 0.45 s), onto the roof at 140.3
tank         142.6 m (RoofsAgain): held window 209 ms, a tap cannot clear it
roofgap      146.1 m (RoofsAgain): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
drop         152.9 m (RoofsAgain): off the end of the roofs (no input), landing about 1.4 m on
sacks        158.5 m (SacksDungNeem): hop onto the sacks and run off the end
dung         163.2 m (SacksDungNeem): held window 305 ms, tap 126 ms
lowbranch    167.4 m (SacksDungNeem): slide window 186 ms, double jump over 102 ms
steps        180.0 m (StepsAwnings): 6 steps up (walked), a 6 m landing 1.5 m up, and down
awnings      196.9 m (StepsAwnings): 2 stalls: run under, or jump into an awning and bounce along them (optional)
hens         210.7 m (CrowdedStreet): held window 213 ms, tap 21 ms
hensbasket   214.7 m (CrowdedStreet): held window 216 ms, tap 12 ms
sand         218.7 m (CrowdedStreet): held window 213 ms, tap 21 ms
dog          222.6 m (CrowdedStreet): held window 207 ms, tap 19 ms
ladder       235.0 m (LastRoofs): up the ladder (no input: she climbs in 0.45 s), onto the roof at 235.8
tank         238.1 m (LastRoofs): held window 209 ms, a tap cannot clear it
roofgap      241.6 m (LastRoofs): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
drop         248.4 m (LastRoofs): off the end of the roofs (no input), landing about 1.4 m on
steps        253.0 m (StepsAgain): 6 steps up (walked), a 6 m landing 1.5 m up, and down
pots         260.0 m (StepsAgain): held window 226 ms, tap 13 ms
awnings      271.0 m (LastAwnings): 2 stalls: run under, or jump into an awning and bounce along them (optional)
hens         284.6 m (LastTest): held window 212 ms, tap 21 ms
goats        288.8 m (LastTest): held window 270 ms, tap 74 ms
puddle       292.6 m (LastTest): held window 214 ms, tap 39 ms
hensbasket   296.7 m (LastTest): held window 216 ms, tap 12 ms
hens         300.8 m (LastTest): held window 298 ms, tap 107 ms
steps        305.0 m (TempleApproach): 6 steps up (walked), a 6 m landing 1.5 m up, and down
```

Problems: none.
