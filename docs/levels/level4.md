# Level 4: The canal

The beat sheet for level 4 (zone 2). It is written by `ArtSource/tools/levels/level4.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level4.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 2: the kid runs at 7 m/s, the rooster at 6.4 m/s; a held jump is 4.32 m long and 1.4 m high; the course is 600 m.

## The opening: the bund

No basket here: the chase starts on the bund between the paddies with the rooster 12 m ahead (the level's Ready
screen; tap to chase). A clean run closes 0.6 m a second and catches him at about 131 m.

## The canal

* **2.5 m:** a held jump clears it (290 ms to take off); a tap lands in the water.
* **3.5 m:** a held jump is a gamble (147 ms), so the 3.5 m canals all have the plank bridge: run across.
* **4.5 m:** only a double jump clears it (405 ms); the mangoes trace the double jump's line.
* **In the water:** never a fail. She wades at 45% speed (5.5 m lost on the widest) and steps out of the 0.28 m bed.

## The shape of it

Teach (to 150 m): one new thing at a time. Practise (to 316 m): canals in rhythm with dung and haystacks, the plank
then a jump, the cart into a canal. Test (to 600 m): the rooster's mischief by the well, every combination, all
three widths in a row, then the bund opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | Bund | 5 mangoes | The bund path between the paddies: the rooster struts ahead; tap to chase. |
| 14 | 32 | FirstCanal | 2.5 m canal 22; 8 mangoes | The first canal, 2.5 m: a held jump clears it; the rooster flutters across first. |
| 32 | 50 | Plank | 3.5 m canal 40 with the plank; 5 mangoes | A 3.5 m canal, too wide for a sure jump: the plank bridge is the way across. |
| 50 | 66 | Dung | cow dung 58; 5 mangoes | Cow dung on the bund, as in the lane: a tap clears it. |
| 66 | 86 | Haystack | small haystack 74; 6 mangoes | A small haystack: hop onto it (mangoes along its top) or over it. |
| 86 | 108 | WideCanal | 4.5 m canal 95; feather 1 at 97.25, 3.4 m up; 7 mangoes | The widest canal, 4.5 m: double jump (the mangoes show where), or wade. |
| 108 | 124 | Breather | chilli 109; 10 mangoes | Room to breathe: a wave of mangoes and the first chilli. |
| 124 | 146 | Cart | bullock cart 128; feather 2 at 132.4, 3.4 m up; cow dung 140.5; 11 mangoes | The bullock cart on the bund: onto its bed; a feather above it for a double jump. |
| 146 | 166 | CanalDung | 2.5 m canal 151; cow dung 160.5; 10 mangoes | A canal, then dung: jump, land, tap. |
| 166 | 192 | Haystacks | small haystack 170; small haystack 177.5; small haystack 185; feather 3 at 185.6, 3.2 m up; 9 mangoes | Three small haystacks: hop, hop, hop; a feather above the last. |
| 192 | 214 | PlankThenJump | 3.5 m canal 195 with the plank; 2.5 m canal 205.5; 10 mangoes | The plank, then a canal with no plank: walk, then jump. |
| 214 | 232 | ChilliStraight | chilli 215; 10 mangoes | A long straight and a chilli to win back ground. |
| 232 | 254 | CartCanal | bullock cart 235; 2.5 m canal 245; 11 mangoes | Off the cart's bed and straight on over a canal. |
| 254 | 274 | WideAgain | 4.5 m canal 261; 7 mangoes | The wide canal again: double jump. |
| 274 | 292 | DungHaystack | cow dung 278.5; small haystack 285.5; 8 mangoes | Dung, then a small haystack. |
| 292 | 318 | CanalTrio | 2.5 m canal 295; 2.5 m canal 303.5; 2.5 m canal 312; 15 mangoes | Three 2.5 m canals in a rhythm: jump, jump, jump. |
| 318 | 342 | Mischief | cow dung 322; pot stack 330 (knocked in by the rooster); mischief 331; 2.5 m canal 336.5; 15 mangoes | Dung; then the rooster knocks the pots by the well into the lane; a canal after. |
| 342 | 364 | PlankHaystack | 3.5 m canal 345 with the plank; small haystack 356; 8 mangoes | The plank, then a haystack. |
| 364 | 382 | ChilliRun | chilli 365; 10 mangoes | A chilli and a run of mangoes. |
| 382 | 410 | CanalCartCanal | 2.5 m canal 385; bullock cart 393; 2.5 m canal 403; 16 mangoes | Canal, cart, canal. |
| 410 | 432 | WideHaystack | 4.5 m canal 413; small haystack 425.5; 10 mangoes | The wide canal, then a haystack straight after it. |
| 432 | 450 | DungPair | cow dung 436.5; cow dung 444; 10 mangoes | Two cow pats: tap, tap. |
| 450 | 468 | FinalChilli | chilli 451; 10 mangoes | The last chilli. |
| 468 | 500 | ThreeWidths | 2.5 m canal 471; 3.5 m canal 479.5 with the plank; 4.5 m canal 489.5; 17 mangoes | All three canals in a row: jump the 2.5 m, walk the plank, double jump the 4.5 m. |
| 500 | 522 | HaystackDung | small haystack 503.5; cow dung 510; small haystack 517.5; 11 mangoes | Two haystacks and dung between them. |
| 522 | 544 | Sugarcane | 2.5 m canal 529; cow dung 538.5; 10 mangoes | Past the sugarcane: a canal, then dung. |
| 544 | 574 | LastWide | 4.5 m canal 549; small haystack 562; 10 mangoes | The last wide canal, and a haystack after it. |
| 574 | 606 | OpenBund | 12 mangoes | The bund opens out: if he is still ahead, he gets away at 600 m. |

## The audit

* canal at 95.0 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* canal at 261.0 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* canal at 413.0 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* canal at 489.5 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* canal at 549.0 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* a clean run from a 12 m start catches him after about 19 s, at about 131 m (without chillies)
* first of each: canal 22 m, bridge 40 m, dung 58 m, haystack 74 m, cart 128 m, pots 330 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
canal         22.0 m (FirstCanal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
bridge        40.0 m (Plank): a 3.5 m canal with the plank: run across (a held jump clears it)
dung          57.7 m (Dung): held window 434 ms, tap 255 ms
haystack      74.1 m (Haystack): small: hop onto it or over it (over: 112 ms)
canal         95.0 m (WideCanal): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
cart         128.0 m (Cart): jump onto the bed and run off the end
dung         140.2 m (Cart): held window 434 ms, tap 255 ms
canal        151.0 m (CanalDung): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
dung         160.2 m (CanalDung): held window 434 ms, tap 255 ms
haystack     170.1 m (Haystacks): small: hop onto it or over it (over: 112 ms)
haystack     177.6 m (Haystacks): small: hop onto it or over it (over: 112 ms)
haystack     185.1 m (Haystacks): small: hop onto it or over it (over: 112 ms)
bridge       195.0 m (PlankThenJump): a 3.5 m canal with the plank: run across (a held jump clears it)
canal        205.5 m (PlankThenJump): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
cart         235.0 m (CartCanal): jump onto the bed and run off the end
canal        245.0 m (CartCanal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
canal        261.0 m (WideAgain): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
dung         278.2 m (DungHaystack): held window 434 ms, tap 255 ms
haystack     285.6 m (DungHaystack): small: hop onto it or over it (over: 112 ms)
canal        295.0 m (CanalTrio): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
canal        303.5 m (CanalTrio): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
canal        312.0 m (CanalTrio): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
dung         321.7 m (Mischief): held window 434 ms, tap 255 ms
pots         329.8 m (Mischief): held window 340 ms, tap 127 ms
canal        336.5 m (Mischief): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
bridge       345.0 m (PlankHaystack): a 3.5 m canal with the plank: run across (a held jump clears it)
haystack     356.1 m (PlankHaystack): small: hop onto it or over it (over: 112 ms)
canal        385.0 m (CanalCartCanal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
cart         393.0 m (CanalCartCanal): jump onto the bed and run off the end
canal        403.0 m (CanalCartCanal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
canal        413.0 m (WideHaystack): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
haystack     425.6 m (WideHaystack): small: hop onto it or over it (over: 112 ms)
dung         436.2 m (DungPair): held window 434 ms, tap 255 ms
dung         443.7 m (DungPair): held window 434 ms, tap 255 ms
canal        471.0 m (ThreeWidths): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
bridge       479.5 m (ThreeWidths): a 3.5 m canal with the plank: run across (a held jump clears it)
canal        489.5 m (ThreeWidths): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
haystack     503.6 m (HaystackDung): small: hop onto it or over it (over: 112 ms)
dung         509.7 m (HaystackDung): held window 434 ms, tap 255 ms
haystack     517.6 m (HaystackDung): small: hop onto it or over it (over: 112 ms)
canal        529.0 m (Sugarcane): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
dung         538.2 m (Sugarcane): held window 434 ms, tap 255 ms
canal        549.0 m (LastWide): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
haystack     562.1 m (LastWide): small: hop onto it or over it (over: 112 ms)
```

Problems: none.
