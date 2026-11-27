# Level 7: Rooftop run

The beat sheet for level 7 (zone 3). It is written by `ArtSource/tools/levels/level7.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level7.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 3: the kid runs at 8 m/s, the rooster at 7.4 m/s; a held jump is 4.93 m long and 1.4 m high; the course is 700 m.

## The opening: the street

No basket here: the chase starts in the street under the terraces with the rooster 12 m ahead (the level's Ready
screen; tap to chase). A clean run closes 0.6 m a second and catches him at about 149 m.

## The roofs

* **Up:** every row that does not follow a gap has the bamboo ladder on its first house: run into it and she
  climbs in 0.45 s. Without one, a double jump reaches the 2.35 m roof, or she vaults it slowly.
* **Across:** the gaps are 1.8 to 2.2 m; a held jump clears them with 370 to 420 ms to take off, a tap too. Missing
  one drops her to the lane, and the next house's wall is a slow vault.
* **On top:** black water tanks to jump like pot stacks; chilli and papad mats drying, crows on the parapets.
* **Down:** off the last row's end she drops to the lane, about 3.2 m on.
* **Between the rows:** clotheslines to slide under (learnt in level 2), pot stacks, the hens' basket.

## The shape of it

Teach (to 170 m): the ladder and one row, one gap, one tank, a clothesline back on the lane, then the long run.
Practise (to 328 m): gaps and tanks together, two clotheslines, a train of four rows. Test (to 700 m): the
rooster's mischief with the hens' basket, the long run with three tanks, rows of gaps, the last ladder.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | Street | 5 mangoes | The street under the terraces: the rooster struts ahead; tap to chase. |
| 14 | 40 | FirstRoofs | roofs 20 to 32.2 (ladder); 11 mangoes | Up the ladder onto the roofs, a run along them, and off the end. |
| 40 | 66 | FirstGap | roofs 42 to 48.1 (ladder); feather 1 at 49.15, 4.25 m up; roofs 50.15 to 57.4; 11 mangoes | Two rows with a 2 m gap between: jump it. A feather above the gap. |
| 66 | 94 | FirstTank | roofs 68 to 78.5 (ladder); water tank 74 on the roof; pot stack 88.5; 13 mangoes | A water tank on the roofs: jump it like a pot stack. |
| 94 | 112 | Clothesline | clothesline 102; 4 mangoes | Back on the lane: a clothesline across it. Slide under. |
| 112 | 130 | Breather | chilli 113; 10 mangoes | A breather: mangoes and a chilli. |
| 130 | 170 | LongRun | roofs 133 to 154.7 (ladder); water tank 138.5 on the roof; water tank 146.5 on the roof; roofs 156.894 to 164.1; 32 mangoes | The long run: eleven houses and two tanks, a gap, four more houses. |
| 170 | 190 | PotsHens | pot stack 175.5; hens' basket 184; 10 mangoes | A pot stack, then the hens' basket. |
| 190 | 238 | GapTanks | roofs 193 to 205.2 (ladder); water tank 198 on the roof; roofs 206.961 to 222.5; water tank 214.461 on the roof; roofs 224.505 to 230.1; 39 mangoes | Three rows, two gaps, a tank on the first two. |
| 238 | 262 | Clotheslines | clothesline 243; clothesline 252; feather 3 at 252, 2.9 m up; 8 mangoes | Two clotheslines: slide, slide. A feather over the second. |
| 262 | 280 | ChilliLane | chilli 263; 10 mangoes | A chilli to win back ground. |
| 280 | 332 | RoofTrain | roofs 284 to 290.6 (ladder); roofs 292.566 to 299.4; roofs 301.601 to 316.7; water tank 308.701 on the roof; feather 2 at 308.801, 5.25 m up; roofs 318.529 to 324.1; 37 mangoes | Four rows in a train: jump, jump, jump; a feather above the tank. |
| 332 | 352 | PotsPair | pot stack 336; pot stack 344; 10 mangoes | Two pot stacks. |
| 352 | 378 | Mischief | pot stack 357; hens' basket 365 (knocked in by the rooster); mischief 366; clothesline 374; 14 mangoes | A pot stack; the rooster knocks the hens' basket into the lane; a clothesline. |
| 378 | 432 | LongTanks | roofs 382 to 403.7 (ladder); water tank 387.5 on the roof; water tank 395.5 on the roof; roofs 405.894 to 419.8; water tank 412.994 on the roof; pot stack 428; 44 mangoes | The long run again, three tanks, a gap; down, and pots. |
| 432 | 452 | ChilliStraight | chilli 433; 10 mangoes | A chilli and a long straight. |
| 452 | 480 | ClothesPotsHens | clothesline 456; pot stack 462.5; hens' basket 471; 14 mangoes | Clothesline, pots, the hens' basket. |
| 480 | 530 | GapRun | roofs 482 to 489.8 (ladder); roofs 491.807 to 498.6; roofs 500.842 to 516.4; water tank 508.042 on the roof; roofs 518.186 to 523.8; 39 mangoes | Four rows, three gaps, a tank in the third row. |
| 530 | 552 | HensPots | hens' basket 535; pot stack 543.5; 10 mangoes | The hens' basket, then pots. |
| 552 | 572 | FinalChilli | chilli 553; 10 mangoes | The last chilli. |
| 572 | 636 | LastRoofs | roofs 575 to 596.7 (ladder); water tank 580.5 on the roof; water tank 588.5 on the roof; roofs 598.694 to 614.2; water tank 605.994 on the roof; roofs 616.438 to 622.0; clothesline 631; 54 mangoes | The last long run: two tanks, a gap, a tank, a gap; down, a clothesline. |
| 636 | 668 | LastTest | pot stack 639; clothesline 648; hens' basket 654; pot stack 662; 21 mangoes | Pots, a clothesline, the hens' basket, pots. |
| 668 | 706 | OpenStreet | 14 mangoes | The street opens out: if he is still ahead, he gets away at 700 m. |

## The audit

* a clean run from a 12 m start catches him after about 19 s, at about 149 m (without chillies)
* first of each: ladder 20 m, drop 32 m, roofgap 48 m, tank 74 m, pots 88 m, clothesline 101 m, hensbasket 184 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
ladder        20.0 m (FirstRoofs): up the ladder (no input: she climbs in 0.45 s), onto the roof at 20.8
drop          32.2 m (FirstRoofs): off the end of the roofs (no input), landing about 3.2 m on
ladder        42.0 m (FirstGap): up the ladder (no input: she climbs in 0.45 s), onto the roof at 42.8
roofgap       48.1 m (FirstGap): a 2.0 m gap between roofs: held 393 ms, tap 222 ms
drop          57.4 m (FirstGap): off the end of the roofs (no input), landing about 3.2 m on
ladder        68.0 m (FirstTank): up the ladder (no input: she climbs in 0.45 s), onto the roof at 68.8
tank          73.7 m (FirstTank): held window 317 ms, tap 83 ms
drop          78.5 m (FirstTank): off the end of the roofs (no input), landing about 3.2 m on
pots          88.3 m (FirstTank): held window 354 ms, tap 142 ms
clothesline  101.2 m (Clothesline): slide window 344 ms, double jump over 260 ms
ladder       133.0 m (LongRun): up the ladder (no input: she climbs in 0.45 s), onto the roof at 133.8
tank         138.2 m (LongRun): held window 317 ms, tap 83 ms
tank         146.2 m (LongRun): held window 317 ms, tap 83 ms
roofgap      154.7 m (LongRun): a 2.2 m gap between roofs: held 368 ms, tap 197 ms
drop         164.1 m (LongRun): off the end of the roofs (no input), landing about 3.2 m on
pots         175.3 m (PotsHens): held window 354 ms, tap 142 ms
hensbasket   183.7 m (PotsHens): held window 352 ms, tap 144 ms
ladder       193.0 m (GapTanks): up the ladder (no input: she climbs in 0.45 s), onto the roof at 193.8
tank         197.7 m (GapTanks): held window 317 ms, tap 83 ms
roofgap      205.2 m (GapTanks): a 1.8 m gap between roofs: held 418 ms, tap 247 ms
tank         214.2 m (GapTanks): held window 317 ms, tap 83 ms
roofgap      222.5 m (GapTanks): a 2.0 m gap between roofs: held 393 ms, tap 222 ms
drop         230.1 m (GapTanks): off the end of the roofs (no input), landing about 3.2 m on
clothesline  242.2 m (Clotheslines): slide window 344 ms, double jump over 260 ms
clothesline  251.2 m (Clotheslines): slide window 344 ms, double jump over 260 ms
ladder       284.0 m (RoofTrain): up the ladder (no input: she climbs in 0.45 s), onto the roof at 284.8
roofgap      290.6 m (RoofTrain): a 2.0 m gap between roofs: held 393 ms, tap 222 ms
roofgap      299.4 m (RoofTrain): a 2.2 m gap between roofs: held 368 ms, tap 197 ms
tank         308.4 m (RoofTrain): held window 317 ms, tap 83 ms
roofgap      316.7 m (RoofTrain): a 1.8 m gap between roofs: held 418 ms, tap 247 ms
drop         324.1 m (RoofTrain): off the end of the roofs (no input), landing about 3.2 m on
pots         335.8 m (PotsPair): held window 354 ms, tap 142 ms
pots         343.8 m (PotsPair): held window 354 ms, tap 142 ms
pots         356.8 m (Mischief): held window 354 ms, tap 142 ms
hensbasket   364.7 m (Mischief): held window 352 ms, tap 144 ms
clothesline  373.1 m (Mischief): slide window 344 ms, double jump over 260 ms
ladder       382.0 m (LongTanks): up the ladder (no input: she climbs in 0.45 s), onto the roof at 382.8
tank         387.2 m (LongTanks): held window 317 ms, tap 83 ms
tank         395.2 m (LongTanks): held window 317 ms, tap 83 ms
roofgap      403.7 m (LongTanks): a 2.2 m gap between roofs: held 368 ms, tap 197 ms
tank         412.7 m (LongTanks): held window 317 ms, tap 83 ms
drop         419.8 m (LongTanks): off the end of the roofs (no input), landing about 3.2 m on
pots         427.8 m (LongTanks): held window 354 ms, tap 142 ms
clothesline  455.1 m (ClothesPotsHens): slide window 344 ms, double jump over 260 ms
pots         462.3 m (ClothesPotsHens): held window 354 ms, tap 142 ms
hensbasket   470.7 m (ClothesPotsHens): held window 352 ms, tap 144 ms
ladder       482.0 m (GapRun): up the ladder (no input: she climbs in 0.45 s), onto the roof at 482.8
roofgap      489.8 m (GapRun): a 2.0 m gap between roofs: held 393 ms, tap 222 ms
roofgap      498.6 m (GapRun): a 2.2 m gap between roofs: held 368 ms, tap 197 ms
tank         507.8 m (GapRun): held window 317 ms, tap 83 ms
roofgap      516.4 m (GapRun): a 1.8 m gap between roofs: held 418 ms, tap 247 ms
drop         523.8 m (GapRun): off the end of the roofs (no input), landing about 3.2 m on
hensbasket   534.7 m (HensPots): held window 352 ms, tap 144 ms
pots         543.3 m (HensPots): held window 354 ms, tap 142 ms
ladder       575.0 m (LastRoofs): up the ladder (no input: she climbs in 0.45 s), onto the roof at 575.8
tank         580.2 m (LastRoofs): held window 317 ms, tap 83 ms
tank         588.2 m (LastRoofs): held window 317 ms, tap 83 ms
roofgap      596.7 m (LastRoofs): a 2.0 m gap between roofs: held 393 ms, tap 222 ms
tank         605.7 m (LastRoofs): held window 317 ms, tap 83 ms
roofgap      614.2 m (LastRoofs): a 2.2 m gap between roofs: held 368 ms, tap 197 ms
drop         622.0 m (LastRoofs): off the end of the roofs (no input), landing about 3.2 m on
clothesline  630.1 m (LastRoofs): slide window 344 ms, double jump over 260 ms
pots         638.8 m (LastTest): held window 354 ms, tap 142 ms
clothesline  647.1 m (LastTest): slide window 344 ms, double jump over 260 ms
hensbasket   653.7 m (LastTest): held window 352 ms, tap 144 ms
pots         661.8 m (LastTest): held window 354 ms, tap 142 ms
```

Problems: none.
