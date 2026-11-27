# Level 8: Market day

The beat sheet for level 8 (zone 3). It is written by `ArtSource/tools/levels/level8.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level8.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 3: the kid runs at 8 m/s, the rooster at 7.4 m/s; a held jump is 4.93 m long and 1.4 m high; the course is 700 m.

## The opening: the market gate

No basket: the chase starts on the market's cement road with the rooster 12 m ahead (the Ready screen; tap to
chase). A clean run catches him at about 149 m.

## The new things

* **Awnings:** rows of stalls at the road's edge, awnings about 2.1 m up. Run under them, or jump into one for a
  2 m bounce, from awning to awning along a line of mangoes (feathers sit high over two rows).
* **Flocks of hens** across the road: jump them, or scatter them (a stumble).
* **The hens' basket**, jumped like pots, and the fake-out: the rooster knocks one into the road behind him.

## The shape of it

Teach (to 154 m): stalls, hens, the basket, stalls with a feather, a chilli, a clothesline, pots and a basket.
Practise (to 284 m): flocks, stalls then hens, the basket among pots, a long row of awnings. Test (to 700 m): the
fake-out, flocks and awnings, a crowded road, the last rows, everything once more, then the market thins out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | MarketGate | 5 mangoes | The weekly market's cement road: the rooster struts ahead; tap to chase. |
| 14 | 40 | FirstStalls | stall 18; stall 22.583; stall 27.096; 10 mangoes | The first row of stalls: run under, or jump into an awning and bounce along. |
| 40 | 56 | Hens | 3 hens 48; 5 mangoes | A flock of hens across the road: jump them. |
| 56 | 72 | Basket | hens' basket 64; 5 mangoes | The hens' basket: jump it. |
| 72 | 102 | HighAwnings | stall 75; stall 78.504; stall 82.988; stall 86.792; feather 1 at 82.699, 4.7 m up; 13 mangoes | Four stalls: a feather high over their awnings for a bounce and a double jump. |
| 102 | 120 | Breather | chilli 103; 10 mangoes | A breather: mangoes and a chilli. |
| 120 | 136 | Clothesline | clothesline 126; 4 mangoes | A clothesline across the road: slide. |
| 136 | 154 | PotsBasket | pot stack 139; hens' basket 148; 10 mangoes | Pots, then the hens' basket. |
| 154 | 176 | Flocks | 2 hens 158; 3 hens 167; feather 3 at 167, 2.9 m up; 10 mangoes | Two flocks of hens. |
| 176 | 208 | StallsHens | stall 179; stall 183.527; stall 188.217; 2 hens 200.367; 15 mangoes | A row of stalls, then hens after it. |
| 208 | 226 | ChilliLane | chilli 209; 10 mangoes | A chilli to win back ground. |
| 226 | 252 | ClothesBasketPots | clothesline 230; hens' basket 236; pot stack 245; 14 mangoes | Clothesline, the hens' basket, pots. |
| 252 | 284 | LongAwnings | stall 255; stall 260.552; stall 265.433; feather 2 at 262.198, 4.7 m up; 12 mangoes | A long row of stalls: bounce along all of them, a feather at the top. |
| 284 | 312 | FakeOut | pot stack 288; hens' basket 296.5 (knocked in by the rooster); mischief 297.5; clothesline 306; 14 mangoes | Pots; the rooster knocks a hens' basket into the road; a clothesline. |
| 312 | 352 | FlocksAwnings | 3 hens 316; stall 321; stall 325.484; stall 329.64; stall 333.293; 2 hens 345.247; 22 mangoes | Hens, a row of stalls, hens. |
| 352 | 370 | ChilliStraight | chilli 353; 10 mangoes | A chilli and a long straight. |
| 370 | 406 | CrowdedRoad | 2 hens 374; pot stack 382; clothesline 391; hens' basket 397; 19 mangoes | Hens, pots, a clothesline, the hens' basket. |
| 406 | 440 | LastAwnings | stall 409; stall 413.69; stall 417.494; 10 mangoes | The last row of stalls. |
| 440 | 458 | FinalChilli | chilli 441; 10 mangoes | The last chilli. |
| 458 | 502 | LastTest | 3 hens 462; clothesline 471; pot stack 477; hens' basket 485; 2 hens 494; 24 mangoes | Hens, a clothesline, pots, the hens' basket, hens: everything once more. |
| 502 | 538 | StallsAgain | stall 505; stall 508.504; stall 512.988; stall 516.792; 3 hens 529.398; 18 mangoes | Stalls, then a flock after them. |
| 538 | 556 | ChilliLane2 | chilli 539; 10 mangoes | A chilli. |
| 556 | 590 | BasketsPots | hens' basket 560; hens' basket 568; pot stack 576; clothesline 585; 19 mangoes | Two hens' baskets, pots, a clothesline. |
| 590 | 626 | LastRow | stall 593; stall 597.527; stall 602.217; 10 mangoes | One more row of stalls. |
| 626 | 706 | MarketEnd | 2 hens 634; 21 mangoes | The market thins out: if he is still ahead, he gets away at 700 m. |

## The audit

* a clean run from a 12 m start catches him after about 19 s, at about 149 m (without chillies)
* first of each: awnings 18 m, hens 47 m, hensbasket 64 m, clothesline 125 m, pots 139 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
awnings       18.0 m (FirstStalls): 3 stalls: run under, or jump into an awning and bounce along them (optional)
hens          47.3 m (Hens): held window 280 ms, tap 84 ms
hensbasket    63.7 m (Basket): held window 352 ms, tap 144 ms
awnings       75.0 m (HighAwnings): 4 stalls: run under, or jump into an awning and bounce along them (optional)
clothesline  125.2 m (Clothesline): slide window 344 ms, double jump over 260 ms
pots         138.8 m (PotsBasket): held window 354 ms, tap 142 ms
hensbasket   147.7 m (PotsBasket): held window 352 ms, tap 144 ms
hens         157.5 m (Flocks): held window 325 ms, tap 129 ms
hens         166.3 m (Flocks): held window 280 ms, tap 84 ms
awnings      179.0 m (StallsHens): 3 stalls: run under, or jump into an awning and bounce along them (optional)
hens         199.9 m (StallsHens): held window 325 ms, tap 129 ms
clothesline  229.2 m (ClothesBasketPots): slide window 344 ms, double jump over 260 ms
hensbasket   235.7 m (ClothesBasketPots): held window 352 ms, tap 144 ms
pots         244.8 m (ClothesBasketPots): held window 354 ms, tap 142 ms
awnings      255.0 m (LongAwnings): 3 stalls: run under, or jump into an awning and bounce along them (optional)
pots         287.8 m (FakeOut): held window 354 ms, tap 142 ms
hensbasket   296.2 m (FakeOut): held window 352 ms, tap 144 ms
clothesline  305.1 m (FakeOut): slide window 344 ms, double jump over 260 ms
hens         315.3 m (FlocksAwnings): held window 280 ms, tap 84 ms
awnings      321.0 m (FlocksAwnings): 4 stalls: run under, or jump into an awning and bounce along them (optional)
hens         344.7 m (FlocksAwnings): held window 325 ms, tap 129 ms
hens         373.5 m (CrowdedRoad): held window 325 ms, tap 129 ms
pots         381.8 m (CrowdedRoad): held window 354 ms, tap 142 ms
clothesline  390.1 m (CrowdedRoad): slide window 344 ms, double jump over 260 ms
hensbasket   396.7 m (CrowdedRoad): held window 352 ms, tap 144 ms
awnings      409.0 m (LastAwnings): 3 stalls: run under, or jump into an awning and bounce along them (optional)
hens         461.3 m (LastTest): held window 280 ms, tap 84 ms
clothesline  470.1 m (LastTest): slide window 344 ms, double jump over 260 ms
pots         476.8 m (LastTest): held window 354 ms, tap 142 ms
hensbasket   484.7 m (LastTest): held window 352 ms, tap 144 ms
hens         493.5 m (LastTest): held window 325 ms, tap 129 ms
awnings      505.0 m (StallsAgain): 4 stalls: run under, or jump into an awning and bounce along them (optional)
hens         528.7 m (StallsAgain): held window 280 ms, tap 84 ms
hensbasket   559.7 m (BasketsPots): held window 352 ms, tap 144 ms
hensbasket   567.7 m (BasketsPots): held window 352 ms, tap 144 ms
pots         575.8 m (BasketsPots): held window 354 ms, tap 142 ms
clothesline  584.1 m (BasketsPots): slide window 344 ms, double jump over 260 ms
awnings      593.0 m (LastRow): 3 stalls: run under, or jump into an awning and bounce along them (optional)
hens         633.5 m (MarketEnd): held window 325 ms, tap 129 ms
```

Problems: none.
