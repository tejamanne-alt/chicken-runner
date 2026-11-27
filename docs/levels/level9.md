# Level 9: The temple steps

The beat sheet for level 9 (zone 3). It is written by `ArtSource/tools/levels/level9.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level9.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 3: the kid runs at 8 m/s, the rooster at 7.4 m/s; a held jump is 4.93 m long and 1.4 m high; the course is 700 m.

## The opening: the temple street

No basket: the chase starts in the temple street at festival time with the rooster 12 m ahead (the Ready screen;
tap to chase). A clean run catches him at about 149 m; the course runs 800 m, the longest.

## The temple steps

* Six steps of 0.25 m (low enough to walk up), a landing 1.5 m up with its lamps, six steps down: 14.4 m in all.
* Mangoes along the landing; on two flights a pot stack waits up there to jump; a feather above the first.

## The shape of it

The whole game once more on the way to the temple: steps, hens and pots, a rooftop stretch (ladder, tank, gap),
a clothesline, the awnings, the mischief, steps with pots, flocks, the roofs again, lines and pots, steps then
stalls, a crowded street, the last rooftops, two flights of steps, the last awnings, everything once more, the
temple's own steps, and the temple court.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | TempleStreet | 5 mangoes | The temple street at festival time: the rooster struts ahead; tap to chase. |
| 14 | 46 | FirstSteps | temple steps 20 to 34.4; feather 1 at 27.2, 3.6 m up; 7 mangoes | The first temple steps: up (walked), along the landing, and down. |
| 46 | 66 | HensPots | 3 hens 50; pot stack 59; 10 mangoes | Hens, then pots. |
| 66 | 106 | Rooftops | roofs 68 to 81.4 (ladder); water tank 74 on the roof; roofs 83.401 to 91.7; 15 mangoes | Up a ladder onto the terraces, a tank, a gap, and down. |
| 106 | 122 | Clothesline | clothesline 113; 4 mangoes | A clothesline: slide. |
| 122 | 140 | Breather | chilli 123; 10 mangoes | A breather: mangoes and a chilli. |
| 140 | 170 | Awnings | stall 143; stall 146.856; stall 151.083; feather 2 at 148.593, 4.7 m up; 9 mangoes | A row of stalls: bounce along the awnings. |
| 170 | 198 | Mischief | pot stack 174; hens' basket 182.5 (knocked in by the rooster); mischief 183.5; clothesline 192; 14 mangoes | Pots; the rooster knocks a hens' basket into the road; a clothesline. |
| 198 | 230 | StepsWithPots | temple steps 203 to 217.4; pot stack 210.2 on the roof; 7 mangoes | Temple steps with a pot stack on the landing: jump it up there. |
| 230 | 248 | ChilliLane | chilli 231; 10 mangoes | A chilli to win back ground. |
| 248 | 274 | Flocks | 2 hens 252; 3 hens 260.5; hens' basket 269; feather 3 at 269, 2.9 m up; 15 mangoes | Two flocks and a basket. |
| 274 | 314 | RoofsAgain | roofs 277 to 290.4 (ladder); water tank 283 on the roof; roofs 292.401 to 300.7; 15 mangoes | The terraces again. |
| 314 | 340 | LinesPots | clothesline 318; pot stack 324.5; clothesline 334; 13 mangoes | Clothesline, pots, clothesline. |
| 340 | 358 | ChilliStraight | chilli 341; 10 mangoes | A chilli and a long straight. |
| 358 | 402 | StepsAwnings | temple steps 361 to 375.4; stall 379.4; stall 384.443; stall 387.947; 17 mangoes | Temple steps, then a row of stalls. |
| 402 | 438 | CrowdedStreet | 3 hens 410; hens' basket 418; pot stack 426; clothesline 435; 19 mangoes | Hens, the basket, pots, a clothesline. |
| 438 | 458 | FinalChilli | chilli 441; 10 mangoes | A chilli. |
| 458 | 500 | LastRoofs | roofs 461 to 474.4 (ladder); water tank 467 on the roof; roofs 476.401 to 484.7; 15 mangoes | The last rooftops. |
| 500 | 544 | StepsTwice | temple steps 503 to 517.4; temple steps 521.4 to 535.8; pot stack 528.6 on the roof; 14 mangoes | Two flights of steps, pots on the second landing. |
| 544 | 578 | LastAwnings | stall 547; stall 552.252; stall 556.833; 11 mangoes | The last row of stalls. |
| 578 | 596 | ChilliLane2 | chilli 579; 10 mangoes | One more chilli. |
| 596 | 646 | LastTest | 3 hens 600; pot stack 608; clothesline 617; hens' basket 623; 2 hens 632; 30 mangoes | Everything once more: hens, pots, a clothesline, the basket, hens. |
| 646 | 686 | TempleApproach | temple steps 652 to 666.4; 7 mangoes | The temple's own steps, the last flight. |
| 686 | 806 | TempleCourt | 20 mangoes | The temple court: if he is still ahead, he gets away at 800 m. |

## The audit

* a clean run from a 12 m start catches him after about 19 s, at about 149 m (without chillies)
* first of each: steps 20 m, hens 49 m, pots 59 m, ladder 68 m, tank 74 m, roofgap 81 m, drop 92 m, clothesline 112 m, awnings 143 m, hensbasket 182 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
steps         20.0 m (FirstSteps): 6 steps up (walked), a 6 m landing 1.5 m up, and down
hens          49.3 m (HensPots): held window 280 ms, tap 84 ms
pots          58.8 m (HensPots): held window 354 ms, tap 142 ms
ladder        68.0 m (Rooftops): up the ladder (no input: she climbs in 0.45 s), onto the roof at 68.8
tank          73.7 m (Rooftops): held window 317 ms, tap 83 ms
roofgap       81.4 m (Rooftops): a 2.0 m gap between roofs: held 393 ms, tap 222 ms
drop          91.7 m (Rooftops): off the end of the roofs (no input), landing about 3.2 m on
clothesline  112.2 m (Clothesline): slide window 344 ms, double jump over 260 ms
awnings      143.0 m (Awnings): 3 stalls: run under, or jump into an awning and bounce along them (optional)
pots         173.8 m (Mischief): held window 354 ms, tap 142 ms
hensbasket   182.2 m (Mischief): held window 352 ms, tap 144 ms
clothesline  191.2 m (Mischief): slide window 344 ms, double jump over 260 ms
steps        203.0 m (StepsWithPots): 6 steps up (walked), a 6 m landing 1.5 m up, and down
pots         210.0 m (StepsWithPots): held window 354 ms, tap 142 ms
hens         251.5 m (Flocks): held window 325 ms, tap 129 ms
hens         259.8 m (Flocks): held window 280 ms, tap 84 ms
hensbasket   268.7 m (Flocks): held window 352 ms, tap 144 ms
ladder       277.0 m (RoofsAgain): up the ladder (no input: she climbs in 0.45 s), onto the roof at 277.8
tank         282.7 m (RoofsAgain): held window 317 ms, tap 83 ms
roofgap      290.4 m (RoofsAgain): a 2.0 m gap between roofs: held 393 ms, tap 222 ms
drop         300.7 m (RoofsAgain): off the end of the roofs (no input), landing about 3.2 m on
clothesline  317.1 m (LinesPots): slide window 344 ms, double jump over 260 ms
pots         324.3 m (LinesPots): held window 354 ms, tap 142 ms
clothesline  333.1 m (LinesPots): slide window 344 ms, double jump over 260 ms
steps        361.0 m (StepsAwnings): 6 steps up (walked), a 6 m landing 1.5 m up, and down
awnings      379.4 m (StepsAwnings): 3 stalls: run under, or jump into an awning and bounce along them (optional)
hens         409.3 m (CrowdedStreet): held window 280 ms, tap 84 ms
hensbasket   417.7 m (CrowdedStreet): held window 352 ms, tap 144 ms
pots         425.8 m (CrowdedStreet): held window 354 ms, tap 142 ms
clothesline  434.1 m (CrowdedStreet): slide window 344 ms, double jump over 260 ms
ladder       461.0 m (LastRoofs): up the ladder (no input: she climbs in 0.45 s), onto the roof at 461.8
tank         466.7 m (LastRoofs): held window 317 ms, tap 83 ms
roofgap      474.4 m (LastRoofs): a 2.0 m gap between roofs: held 393 ms, tap 222 ms
drop         484.7 m (LastRoofs): off the end of the roofs (no input), landing about 3.2 m on
steps        503.0 m (StepsTwice): 6 steps up (walked), a 6 m landing 1.5 m up, and down
steps        521.4 m (StepsTwice): 6 steps up (walked), a 6 m landing 1.5 m up, and down
pots         528.4 m (StepsTwice): held window 354 ms, tap 142 ms
awnings      547.0 m (LastAwnings): 3 stalls: run under, or jump into an awning and bounce along them (optional)
hens         599.3 m (LastTest): held window 280 ms, tap 84 ms
pots         607.8 m (LastTest): held window 354 ms, tap 142 ms
clothesline  616.1 m (LastTest): slide window 344 ms, double jump over 260 ms
hensbasket   622.7 m (LastTest): held window 352 ms, tap 144 ms
hens         631.5 m (LastTest): held window 325 ms, tap 129 ms
steps        652.0 m (TempleApproach): 6 steps up (walked), a 6 m landing 1.5 m up, and down
```

Problems: none.
