# Level 3: Up on the roofs

The beat sheet for level 3 (zone 1). It is written by `ArtSource/tools/levels/level3.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level3.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 1: the kid runs at 3.5 m/s, the rooster at 3.2 m/s; a held jump is 2.16 m long and 1.4 m high; the course is 290 m.

## The opening: the street

No basket: the chase starts in a street of flat-roofed houses with the rooster 7 m ahead (the Ready screen; tap
to chase). A clean run catches him at about 72 m.

## The roofs

* **Up:** the bamboo ladder on a row's first house (run into it: a 0.45 s climb), or a rope cot pushed against
  the wall of a house with no ladder: she bounces off its near end 2.4 m up and steps onto the 2.35 m roof as she
  meets the wall (a double jump in the bounce makes it sure; without one a late bounce is a slow vault).
* **Across:** gaps of 1.2 to 1.3 m between rows: a held jump (310 to 340 ms to take off), or even a tap.
* **On top:** the black water tanks on their stands: jump them as on the road.
* **Down:** off the end of a row, landing about 1.4 m on.

## The road between

Only what lies in a village street: the dog asleep in the dust, cow dung, hens and a goat kid crossing, the hand
pump's puddle, a heap of sand where a house is going up, and two neems with a low limb across the road to slide
under (level 2's lesson). Nothing hangs across the road and there are no pots: the rooster's mischief is the
hens' basket, knocked off a doorstep into the road behind him.

## The shape of it

Everything runs at a small child's real pace (3.5 m/s); things to jump are about 4 m (a second and a bit) apart.
Teach (to 88 m): the ladder and a row, the first gap, a neem, the cot up onto a roof, a tank on a roof. Practise
(to 160 m): two gaps, the sand heap and hens, the cot then a gap, the dog and a neem. Test (to 290 m): the
rooster's mischief, a train of four rows, the pump, a goat kid and the dog, the cot onto a long row, the last
ladder, then the lane opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 8 | Street | 5 mangoes | A street of flat-roofed houses: the rooster struts ahead; tap to chase. |
| 8 | 22 | FirstLadder | roofs 11 to 16.1 (ladder); 5 mangoes | The first ladder: run into it and she climbs; along the roofs, and off the end. |
| 22 | 37 | FirstGap | roofs 24 to 28.9 (ladder); feather 1 at 29.509, 5.15 m up; roofs 30.109 to 34.5; 13 mangoes | Two rows with a 1.2 m gap: jump across. A feather above the gap. |
| 37 | 46 | Neem | low neem branch 41.5; 3 mangoes | Back on the road: a neem's low limb across it. Slide. |
| 46 | 60 | CotUp | rope cot 48; roofs 49.9 to 55.5; 10 mangoes | A rope cot pushed against a house with no ladder: run into it and bounce up onto its roof. |
| 60 | 70 | Breather | chilli 60.6; 8 mangoes | A breather: mangoes and a chilli. |
| 70 | 88 | RoofTank | roofs 72 to 79.8 (ladder); water tank 76 on the roof; cow dung 84.5; 15 mangoes | A long row with a water tank on the roof: jump it up there. Dung after the drop. |
| 88 | 106 | GapGap | roofs 89 to 92.9 (ladder); roofs 94.069 to 98.0; roofs 99.307 to 102.2; 16 mangoes | Three rows, two gaps. |
| 106 | 117 | SandHens | heap of building sand 109; 2 hens 113.5; 10 mangoes | A house going up: a heap of its sand in the road, then two hens. |
| 117 | 137 | CotUpGap | rope cot 119; feather 2 at 120.7, 4.3 m up; roofs 120.9 to 126.5; roofs 127.695 to 133.3; water tank 131.195 on the roof; 20 mangoes | The cot up onto a roof (a feather above the wall), a gap, and a tank on the next roof. |
| 137 | 148 | ChilliStraight | chilli 137.6; 11 mangoes | A chilli and a long straight. |
| 148 | 160 | DogNeem | sleeping dog 151.5; low neem branch 156; 8 mangoes | The dog asleep in the dust, then a neem's low limb. |
| 160 | 172 | Mischief | cow dung 162.5; hens' basket 167 (knocked in by the rooster); mischief 167.6; 10 mangoes | Dung; then the rooster knocks the hens' basket off a doorstep into the road. |
| 172 | 198 | RoofTrain | roofs 174 to 177.9 (ladder); roofs 179.069 to 183.0; roofs 184.307 to 192.6; water tank 187.807 on the roof; feather 3 at 187.907, 5.15 m up; roofs 193.799 to 196.7; 27 mangoes | Four rows in a train, a tank on the third: jump, jump, jump, and down. |
| 198 | 210 | ChilliLane | chilli 198.6; 11 mangoes | A breather and a chilli. |
| 210 | 224 | PumpGoatDog | hand-pump puddle 213; 1 goat kid 217.5; sleeping dog 222; 15 mangoes | The hand pump's puddle, a goat kid, the dog. |
| 224 | 246 | CotRoofs | rope cot 226; roofs 227.9 to 236.2; water tank 232.2 on the roof; roofs 237.392 to 241.3; 18 mangoes | The cot up, a long row with a tank on it, a gap, and down. |
| 246 | 256 | FinalChilli | chilli 246.6; 9 mangoes | The last chilli. |
| 256 | 272 | LastRow | roofs 258 to 267.5 (ladder); 11 mangoes | The last ladder, a long row, and down onto the open road. |
| 272 | 296 | OpenLane | 12 mangoes | The lane opens out: if he is still ahead, he gets away at 290 m. |

## The audit

* a clean run from a 7 m start catches him after about 21 s, at about 72 m (without chillies)
* first of each: ladder 11 m, drop 16 m, roofgap 29 m, lowbranch 41 m, cot 48 m, tank 76 m, dung 84 m, sand 109 m, hens 113 m, dog 151 m, hensbasket 167 m, puddle 213 m, goats 217 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
ladder        11.0 m (FirstLadder): up the ladder (no input: she climbs in 0.45 s), onto the roof at 11.8
drop          16.1 m (FirstLadder): off the end of the roofs (no input), landing about 1.4 m on
ladder        24.0 m (FirstGap): up the ladder (no input: she climbs in 0.45 s), onto the roof at 24.8
roofgap       28.9 m (FirstGap): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
drop          34.5 m (FirstGap): off the end of the roofs (no input), landing about 1.4 m on
lowbranch     41.0 m (Neem): slide window 186 ms, double jump over 102 ms
cot           48.0 m (CotUp): a trampoline: run into it (no input) for a 2.6 m bounce up onto the roofs, landing about 2.2 m on
drop          55.5 m (CotUp): off the end of the roofs (no input), landing about 1.4 m on
ladder        72.0 m (RoofTank): up the ladder (no input: she climbs in 0.45 s), onto the roof at 72.8
tank          75.8 m (RoofTank): held window 209 ms, a tap cannot clear it
drop          79.8 m (RoofTank): off the end of the roofs (no input), landing about 1.4 m on
dung          84.2 m (RoofTank): held window 305 ms, tap 126 ms
ladder        89.0 m (GapGap): up the ladder (no input: she climbs in 0.45 s), onto the roof at 89.8
roofgap       92.9 m (GapGap): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
roofgap       98.0 m (GapGap): a 1.3 m gap between roofs: held 311 ms, tap 140 ms
drop         102.2 m (GapGap): off the end of the roofs (no input), landing about 1.4 m on
sand         108.7 m (SandHens): held window 213 ms, tap 21 ms
hens         113.2 m (SandHens): held window 213 ms, tap 21 ms
cot          119.0 m (CotUpGap): a trampoline: run into it (no input) for a 2.6 m bounce up onto the roofs, landing about 2.2 m on
roofgap      126.5 m (CotUpGap): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
tank         131.0 m (CotUpGap): held window 209 ms, a tap cannot clear it
drop         133.3 m (CotUpGap): off the end of the roofs (no input), landing about 1.4 m on
dog          151.1 m (DogNeem): held window 207 ms, tap 19 ms
lowbranch    155.4 m (DogNeem): slide window 186 ms, double jump over 102 ms
dung         162.2 m (Mischief): held window 305 ms, tap 126 ms
hensbasket   166.7 m (Mischief): held window 216 ms, tap 12 ms
ladder       174.0 m (RoofTrain): up the ladder (no input: she climbs in 0.45 s), onto the roof at 174.8
roofgap      177.9 m (RoofTrain): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
roofgap      183.0 m (RoofTrain): a 1.3 m gap between roofs: held 311 ms, tap 140 ms
tank         187.6 m (RoofTrain): held window 209 ms, a tap cannot clear it
roofgap      192.6 m (RoofTrain): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
drop         196.7 m (RoofTrain): off the end of the roofs (no input), landing about 1.4 m on
puddle       212.6 m (PumpGoatDog): held window 214 ms, tap 39 ms
goats        217.3 m (PumpGoatDog): held window 270 ms, tap 74 ms
dog          221.6 m (PumpGoatDog): held window 207 ms, tap 19 ms
cot          226.0 m (CotRoofs): a trampoline: run into it (no input) for a 2.6 m bounce up onto the roofs, landing about 2.2 m on
tank         232.0 m (CotRoofs): held window 209 ms, a tap cannot clear it
roofgap      236.2 m (CotRoofs): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
drop         241.3 m (CotRoofs): off the end of the roofs (no input), landing about 1.4 m on
ladder       258.0 m (LastRow): up the ladder (no input: she climbs in 0.45 s), onto the roof at 258.8
drop         267.5 m (LastRow): off the end of the roofs (no input), landing about 1.4 m on
```

Problems: none.
