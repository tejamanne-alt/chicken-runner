# Level 7: Rooftop run

The beat sheet for level 7 (zone 3). It is written by `ArtSource/tools/levels/level7.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level7.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 3: the kid runs at 3.5 m/s, the rooster at 3.15 m/s; a held jump is 2.16 m long and 1.4 m high; the course is 300 m.

## The opening: the street

No basket here: the chase starts in the street under the terraces with the rooster 7 m ahead (the level's Ready
screen; tap to chase). The kid runs 3.5 m/s, a small child's real pace, and the rooster 3.15: a clean run closes
0.35 m a second and catches him at about 62 m. The course is 300 m, about a minute and a half.

## The roofs

* **Up:** every row that does not follow a gap has the bamboo ladder on its first house: run into it and she
  climbs in 0.45 s. Without one, a double jump reaches the 2.35 m roof, or she vaults it slowly.
* **Across:** the gaps are 1.1 to 1.3 m, a real gap between two houses; a held jump clears them with 310 to 370 ms
  to take off, a tap with 140 to 200 ms. Missing one drops her to the lane, and the next house's wall is a slow vault.
* **On top:** black water tanks to jump; chilli and papad mats drying, crows on the parapets.
* **Down:** off a row's end she drops to the lane, about 1.4 m on.
* **Rows:** two to five houses (a house front keeps its size, so the rows are shorter than at the old pace, and
  take about as long to run).

## The street between the rows

Only what lies in a real street, spaced about 4 m (a second and a bit) apart: a vendor's hens and their basket, a
goat kid crossing, cow dung, the puddle round the hand pump, a dog asleep, sacks of paddy unloaded at the roadside
for a shop (hop onto them and off), a heap of sand where a house is going up, and one roadside neem whose low
limb she slides under. The washing lines strung across the street are gone, and so are the pot stacks.

## The shape of it

Teach (to 85 m): the ladder and one row, one gap, one tank, the neem back on the lane, a chilli, then the long run.
Practise (to 181 m): a goat and the basket, gaps and tanks together, the sacks and the dog, a train of four rows.
Test (to 300 m): the rooster's mischief with the hens' basket, the long run with three tanks, the sand heap and the
dog, the last long run, the last three things in the street, and the street opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 6 | Street | 4 mangoes | The street under the terraces: the rooster struts ahead; tap to chase. |
| 6 | 19 | FirstRoofs | roofs 8 to 14.6 (ladder); 7 mangoes | Up the ladder onto the roofs, a run along them, and off the end. |
| 19 | 33 | FirstGap | roofs 20.6 to 24.1 (ladder); feather 1 at 24.652, 4.25 m up; roofs 25.252 to 29.6; 8 mangoes | Two rows with a 1.2 m gap between: jump it. A feather above the gap. |
| 33 | 49 | FirstTank | roofs 35.7 to 42.3 (ladder); water tank 39.1 on the roof; 1 hens 47; 13 mangoes | A water tank on the roofs: jump it. Down, and a vendor's hen in the street. |
| 49 | 57 | Neem | low neem branch 53; feather 3 at 53, 2.9 m up; 3 mangoes | A roadside neem's low limb across the street: slide under. A feather above it. |
| 57 | 66 | Breather | chilli 57.5; 9 mangoes | A breather: mangoes and a chilli. |
| 66 | 87 | LongRun | roofs 67.5 to 78.0 (ladder); water tank 71 on the roof; water tank 75 on the roof; roofs 79.304 to 84.9; 25 mangoes | The long run: five houses and two tanks, a gap, three more houses. |
| 87 | 98 | GoatBasket | 1 goat kid 90.5; hens' basket 94.5; 10 mangoes | A goat kid crossing, then the hens' basket. |
| 98 | 123 | GapTanks | roofs 99.5 to 106.1 (ladder); water tank 103 on the roof; roofs 107.266 to 115.6; water tank 111.466 on the roof; roofs 116.659 to 119.6; 28 mangoes | Three rows, two gaps, a tank on the first two. |
| 123 | 136 | ShopSacks | sacks of paddy 126; sleeping dog 132; 7 mangoes | Sacks of paddy unloaded at the roadside for a shop: hop on and off. A dog asleep. |
| 136 | 145 | ChilliLane | chilli 136.5; 9 mangoes | A chilli to win back ground. |
| 145 | 174 | RoofTrain | roofs 146 to 150.9 (ladder); roofs 152.109 to 157.7; roofs 159.004 to 167.3; water tank 163.004 on the roof; feather 2 at 163.104, 5.25 m up; roofs 168.397 to 171.3; 33 mangoes | Four rows in a train: jump, jump, jump; a feather above the tank. |
| 174 | 183 | DungHens | cow dung 177; 2 hens 181; 10 mangoes | Cow dung, then two hens pecking in the street. |
| 183 | 196 | Mischief | hand-pump puddle 186.5; hens' basket 190.5 (knocked in by the rooster); mischief 191; 1 goat kid 194.5; 15 mangoes | The hand-pump puddle; the rooster knocks the hens' basket into the street; a goat kid. |
| 196 | 222 | LongTanks | roofs 197.5 to 208.0 (ladder); water tank 201 on the roof; water tank 205 on the roof; roofs 209.204 to 216.5; water tank 213.004 on the roof; 27 mangoes | The long run again: three tanks and a gap, then down. |
| 222 | 235 | SandDogBasket | heap of building sand 225; sleeping dog 229; hens' basket 233; 15 mangoes | A house going up (its sand heap), the dog, the hens' basket. |
| 235 | 244 | FinalChilli | chilli 235.5; 9 mangoes | The last chilli. |
| 244 | 277 | LastRoofs | roofs 245.5 to 256.0 (ladder); water tank 249 on the roof; water tank 253 on the roof; roofs 257.204 to 265.5; water tank 261.404 on the roof; roofs 266.797 to 272.4; 38 mangoes | The last long run: two tanks, a gap, a tank, a gap; down. |
| 277 | 290 | LastTest | hens' basket 280; 1 goat kid 284; cow dung 288; 15 mangoes | The hens' basket, a goat kid, cow dung: the last test. |
| 290 | 308 | OpenStreet | 10 mangoes | The street opens out: if he is still ahead, he gets away at 300 m. |

## The audit

* a clean run from a 7 m start catches him after about 18 s, at about 62 m (without chillies)
* first of each: ladder 8 m, drop 15 m, roofgap 24 m, tank 39 m, hens 47 m, lowbranch 52 m, goats 90 m, hensbasket 94 m, sacks 126 m, dog 132 m, dung 177 m, puddle 186 m, sand 225 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
ladder         8.0 m (FirstRoofs): up the ladder (no input: she climbs in 0.45 s), onto the roof at 8.8
drop          14.6 m (FirstRoofs): off the end of the roofs (no input), landing about 1.4 m on
ladder        20.6 m (FirstGap): up the ladder (no input: she climbs in 0.45 s), onto the roof at 21.4
roofgap       24.1 m (FirstGap): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
drop          29.6 m (FirstGap): off the end of the roofs (no input), landing about 1.4 m on
ladder        35.7 m (FirstTank): up the ladder (no input: she climbs in 0.45 s), onto the roof at 36.5
tank          38.9 m (FirstTank): held window 209 ms, a tap cannot clear it
drop          42.3 m (FirstTank): off the end of the roofs (no input), landing about 1.4 m on
hens          46.8 m (FirstTank): held window 298 ms, tap 107 ms
lowbranch     52.5 m (Neem): slide window 186 ms, double jump over 102 ms
ladder        67.5 m (LongRun): up the ladder (no input: she climbs in 0.45 s), onto the roof at 68.3
tank          70.8 m (LongRun): held window 209 ms, a tap cannot clear it
tank          74.8 m (LongRun): held window 209 ms, a tap cannot clear it
roofgap       78.0 m (LongRun): a 1.3 m gap between roofs: held 311 ms, tap 140 ms
drop          84.9 m (LongRun): off the end of the roofs (no input), landing about 1.4 m on
goats         90.3 m (GoatBasket): held window 270 ms, tap 74 ms
hensbasket    94.2 m (GoatBasket): held window 216 ms, tap 12 ms
ladder        99.5 m (GapTanks): up the ladder (no input: she climbs in 0.45 s), onto the roof at 100.3
tank         102.8 m (GapTanks): held window 209 ms, a tap cannot clear it
roofgap      106.1 m (GapTanks): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
tank         111.2 m (GapTanks): held window 209 ms, a tap cannot clear it
roofgap      115.6 m (GapTanks): a 1.1 m gap between roofs: held 368 ms, tap 197 ms
drop         119.6 m (GapTanks): off the end of the roofs (no input), landing about 1.4 m on
sacks        126.0 m (ShopSacks): hop onto the sacks and run off the end
dog          131.6 m (ShopSacks): held window 207 ms, tap 19 ms
ladder       146.0 m (RoofTrain): up the ladder (no input: she climbs in 0.45 s), onto the roof at 146.8
roofgap      150.9 m (RoofTrain): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
roofgap      157.7 m (RoofTrain): a 1.3 m gap between roofs: held 311 ms, tap 140 ms
tank         162.8 m (RoofTrain): held window 209 ms, a tap cannot clear it
roofgap      167.3 m (RoofTrain): a 1.1 m gap between roofs: held 368 ms, tap 197 ms
drop         171.3 m (RoofTrain): off the end of the roofs (no input), landing about 1.4 m on
dung         176.7 m (DungHens): held window 305 ms, tap 126 ms
hens         180.7 m (DungHens): held window 213 ms, tap 21 ms
puddle       186.1 m (Mischief): held window 214 ms, tap 39 ms
hensbasket   190.2 m (Mischief): held window 216 ms, tap 12 ms
goats        194.3 m (Mischief): held window 270 ms, tap 74 ms
ladder       197.5 m (LongTanks): up the ladder (no input: she climbs in 0.45 s), onto the roof at 198.3
tank         200.8 m (LongTanks): held window 209 ms, a tap cannot clear it
tank         204.8 m (LongTanks): held window 209 ms, a tap cannot clear it
roofgap      208.0 m (LongTanks): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
tank         212.8 m (LongTanks): held window 209 ms, a tap cannot clear it
drop         216.5 m (LongTanks): off the end of the roofs (no input), landing about 1.4 m on
sand         224.7 m (SandDogBasket): held window 213 ms, tap 21 ms
dog          228.6 m (SandDogBasket): held window 207 ms, tap 19 ms
hensbasket   232.7 m (SandDogBasket): held window 216 ms, tap 12 ms
ladder       245.5 m (LastRoofs): up the ladder (no input: she climbs in 0.45 s), onto the roof at 246.3
tank         248.8 m (LastRoofs): held window 209 ms, a tap cannot clear it
tank         252.8 m (LastRoofs): held window 209 ms, a tap cannot clear it
roofgap      256.0 m (LastRoofs): a 1.2 m gap between roofs: held 340 ms, tap 169 ms
tank         261.2 m (LastRoofs): held window 209 ms, a tap cannot clear it
roofgap      265.5 m (LastRoofs): a 1.3 m gap between roofs: held 311 ms, tap 140 ms
drop         272.4 m (LastRoofs): off the end of the roofs (no input), landing about 1.4 m on
hensbasket   279.7 m (LastTest): held window 216 ms, tap 12 ms
goats        283.8 m (LastTest): held window 270 ms, tap 74 ms
dung         287.7 m (LastTest): held window 305 ms, tap 126 ms
```

Problems: none.
