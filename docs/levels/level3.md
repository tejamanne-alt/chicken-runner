# Level 3: Up on the roofs

The beat sheet for level 3 (zone 1). It is written by `ArtSource/tools/levels/level3.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level3.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 1: the kid runs at 6 m/s, the rooster at 5.5 m/s; a held jump is 3.70 m long and 1.4 m high; the course is 500 m.

## The opening: the street

No basket: the chase starts in a street of flat-roofed houses with the rooster 12 m ahead (the Ready screen; tap
to chase). A clean run catches him at about 110 m.

## The roofs

* **Up:** the bamboo ladder on a row's first house (run into it: a 0.45 s climb), or a rope cot set just before a
  row with no ladder (its 2.9 m bounce lands her on the 2.35 m roof).
* **Across:** gaps of 1.8 to 2.2 m between rows: a held jump.
* **On top:** pot stacks drying on the roofs: jump them as on the lane.
* **Down:** off the end of a row, landing about 2.4 m on.

## The shape of it

Teach (to 148 m): the ladder and a row, the first gap, a clothesline, the cot up onto a roof, pots on a roof.
Practise (to 272 m): two gaps, the cot then a gap, the dog and a line. Test (to 500 m): the rooster's mischief, a
train of four rows, the cot onto a long row, the last ladder, then the lane opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | Street | 5 mangoes | A street of flat-roofed houses: the rooster struts ahead; tap to chase. |
| 14 | 38 | FirstLadder | roofs 20 to 27.8 (ladder); 7 mangoes | The first ladder: run into it and she climbs; along the roofs, and off the end. |
| 38 | 62 | FirstGap | roofs 41 to 45.9 (ladder); feather 1 at 46.809, 4.25 m up; roofs 47.709 to 53.3; 9 mangoes | Two rows with a 1.8 m gap: jump across. A feather above the gap. |
| 62 | 78 | Clothesline | clothesline 70; 4 mangoes | Back on the lane: a clothesline. Slide. |
| 78 | 102 | CotUp | rope cot 82; roofs 84.9 to 93.2; 11 mangoes | A rope cot before a house with no ladder: bounce up onto its roof. |
| 102 | 118 | Breather | chilli 103; 9 mangoes | A breather: mangoes and a chilli. |
| 118 | 148 | RoofPots | roofs 121 to 133.2 (ladder); pot stack 127 on the roof; cow dung 142.5; 17 mangoes | A long row with a pot stack drying on the roof: jump it up there. |
| 148 | 182 | GapGap | roofs 151 to 157.6 (ladder); roofs 159.566 to 165.2; roofs 167.361 to 171.3; 17 mangoes | Three rows, two gaps. |
| 182 | 200 | LinePots | clothesline 186; pot stack 194; 9 mangoes | A clothesline, then pots. |
| 200 | 234 | CotUpGap | rope cot 203; feather 2 at 205.6, 4.4 m up; roofs 205.9 to 211.5; roofs 213.295 to 223.2; pot stack 218.895 on the roof; 22 mangoes | The cot up onto a roof, a gap, and a pot stack on the next roof. |
| 234 | 252 | ChilliStraight | chilli 235; 10 mangoes | A chilli and a long straight. |
| 252 | 272 | DogLine | sleeping dog 256.5; clothesline 266; 9 mangoes | The dog, then a clothesline. |
| 272 | 298 | Mischief | cow dung 276; pot stack 284 (knocked in by the rooster); mischief 285; 10 mangoes | Dung; the rooster knocks the pots off their stand; then a ladder. |
| 298 | 344 | RoofTrain | roofs 300 to 306.6 (ladder); roofs 308.566 to 314.2; roofs 316.361 to 327.6; pot stack 321.761 on the roof; feather 3 at 321.861, 5.25 m up; roofs 329.351 to 333.7; 33 mangoes | Four rows in a train, a pot stack on the third: jump, jump, jump, and down. |
| 344 | 362 | ChilliLane | chilli 345; 9 mangoes | A breather and a chilli. |
| 362 | 390 | LinePotsDog | clothesline 366; pot stack 373.5; sleeping dog 381.5; 14 mangoes | Clothesline, pots, the dog. |
| 390 | 430 | CotRoofs | rope cot 393; roofs 395.9 to 409.8; pot stack 403.5 on the roof; roofs 411.787 to 417.4; 21 mangoes | The cot up, a long row with pots on it, a gap, and down. |
| 430 | 446 | FinalChilli | chilli 431; 8 mangoes | The last chilli. |
| 446 | 474 | LastRow | roofs 449 to 462.4 (ladder); 14 mangoes | The last ladder, a long row, and down onto the open lane. |
| 474 | 506 | OpenLane | 12 mangoes | The lane opens out: if he is still ahead, he gets away at 500 m. |

## The audit

* a clean run from a 12 m start catches him after about 22 s, at about 134 m (without chillies)
* first of each: ladder 20 m, drop 28 m, roofgap 46 m, clothesline 69 m, cot 82 m, pots 127 m, dung 142 m, dog 256 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
ladder        20.0 m (FirstLadder): up the ladder (no input: she climbs in 0.45 s), onto the roof at 20.8
drop          27.8 m (FirstLadder): off the end of the roofs (no input), landing about 2.4 m on
ladder        41.0 m (FirstGap): up the ladder (no input: she climbs in 0.45 s), onto the roof at 41.8
roofgap       45.9 m (FirstGap): a 1.8 m gap between roofs: held 353 ms, tap 182 ms
drop          53.3 m (FirstGap): off the end of the roofs (no input), landing about 2.4 m on
clothesline   69.2 m (Clothesline): slide window 258 ms, double jump over 175 ms
cot           82.0 m (CotUp): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
drop          93.2 m (CotUp): off the end of the roofs (no input), landing about 2.4 m on
ladder       121.0 m (RoofPots): up the ladder (no input: she climbs in 0.45 s), onto the roof at 121.8
pots         126.8 m (RoofPots): held window 321 ms, tap 108 ms
drop         133.2 m (RoofPots): off the end of the roofs (no input), landing about 2.4 m on
dung         142.2 m (RoofPots): held window 412 ms, tap 233 ms
ladder       151.0 m (GapGap): up the ladder (no input: she climbs in 0.45 s), onto the roof at 151.8
roofgap      157.6 m (GapGap): a 2.0 m gap between roofs: held 320 ms, tap 149 ms
roofgap      165.2 m (GapGap): a 2.2 m gap between roofs: held 287 ms, tap 116 ms
drop         171.3 m (GapGap): off the end of the roofs (no input), landing about 2.4 m on
clothesline  185.2 m (LinePots): slide window 258 ms, double jump over 175 ms
pots         193.8 m (LinePots): held window 321 ms, tap 108 ms
cot          203.0 m (CotUpGap): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
roofgap      211.5 m (CotUpGap): a 1.8 m gap between roofs: held 353 ms, tap 183 ms
pots         218.7 m (CotUpGap): held window 321 ms, tap 108 ms
drop         223.2 m (CotUpGap): off the end of the roofs (no input), landing about 2.4 m on
dog          256.1 m (DogLine): held window 313 ms, tap 125 ms
clothesline  265.1 m (DogLine): slide window 258 ms, double jump over 175 ms
dung         275.7 m (Mischief): held window 413 ms, tap 233 ms
pots         283.8 m (Mischief): held window 321 ms, tap 108 ms
ladder       300.0 m (RoofTrain): up the ladder (no input: she climbs in 0.45 s), onto the roof at 300.8
roofgap      306.6 m (RoofTrain): a 2.0 m gap between roofs: held 320 ms, tap 149 ms
roofgap      314.2 m (RoofTrain): a 2.2 m gap between roofs: held 287 ms, tap 116 ms
pots         321.5 m (RoofTrain): held window 321 ms, tap 108 ms
roofgap      327.6 m (RoofTrain): a 1.8 m gap between roofs: held 353 ms, tap 182 ms
drop         333.7 m (RoofTrain): off the end of the roofs (no input), landing about 2.4 m on
clothesline  365.1 m (LinePotsDog): slide window 258 ms, double jump over 175 ms
pots         373.3 m (LinePotsDog): held window 321 ms, tap 108 ms
dog          381.1 m (LinePotsDog): held window 313 ms, tap 125 ms
cot          393.0 m (CotRoofs): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
pots         403.3 m (CotRoofs): held window 321 ms, tap 108 ms
roofgap      409.8 m (CotRoofs): a 2.0 m gap between roofs: held 320 ms, tap 149 ms
drop         417.4 m (CotRoofs): off the end of the roofs (no input), landing about 2.4 m on
ladder       449.0 m (LastRow): up the ladder (no input: she climbs in 0.45 s), onto the roof at 449.8
drop         462.4 m (LastRow): off the end of the roofs (no input), landing about 2.4 m on
```

Problems: none.
