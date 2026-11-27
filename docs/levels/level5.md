# Level 5: Mango trees

The beat sheet for level 5 (zone 2). It is written by `ArtSource/tools/levels/level5.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level5.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 2: the kid runs at 7 m/s, the rooster at 6.4 m/s; a held jump is 4.32 m long and 1.4 m high; the course is 600 m.

## The opening: the grove

No basket: the chase starts on the bund road into the mango grove with the rooster 12 m ahead (the Ready screen;
tap to chase). A clean run catches him at about 131 m.

## The branches

* A mango tree's branch reaches over the road from 1 m to 5 m past its trunk, 2.3 m up, mangoes along it.
* Jump at it and she pulls herself up (a quick climb), runs along it and drops off its end; or she runs on under.
* A small haystack just before a branch is a step up to it, and so is a cart's bed.
* The rooster flutters up onto every branch and down off its end.

## The shape of it

Teach (to 146 m): a tree with a haystack step, a canal, a branch with no step, dung, a chilli, a tree with a
feather, the plank. Practise (to 300 m): the cart as a step, canals and dung, haystacks, a tree then a canal, an
orchard of three trees. Test (to 600 m): the rooster's mischief by the well, the wide canal and a tree, trees and
stacks, the last trees and canals, then the road opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | Grove | 5 mangoes | The bund road into the mango grove: the rooster struts ahead; tap to chase. |
| 14 | 36 | FirstTree | small haystack 18.2; mango tree and branch 21; 3 mangoes | The first mango tree, a haystack before it: hop onto the stack, jump at the branch. |
| 36 | 52 | Canal | 2.5 m canal 42; 5 mangoes | A 2.5 m canal: jump it. |
| 52 | 74 | Branch | mango tree and branch 56 | A branch with no step: jump straight up at it. |
| 74 | 90 | Dung | cow dung 82; 5 mangoes | Cow dung on the road. |
| 90 | 106 | Breather | chilli 91; 9 mangoes | A breather: mangoes and a chilli. |
| 106 | 128 | TreeFeather | small haystack 109.2; mango tree and branch 112; feather 1 at 116.3, 3.2 m up; 3 mangoes | A tree with a feather above its branch: up, along, a double jump at the end. |
| 128 | 146 | Plank | 3.5 m canal 134 with the plank; 5 mangoes | The plank over a 3.5 m canal. |
| 146 | 172 | CartTree | bullock cart 149; mango tree and branch 154; 6 mangoes | The cart's bed as the step: off it and up onto the branch. |
| 172 | 192 | CanalDung | 2.5 m canal 176; cow dung 186; 10 mangoes | A canal, then dung. |
| 192 | 214 | Haystacks | small haystack 196; small haystack 204; 6 mangoes | Two small haystacks: hop, hop. |
| 214 | 240 | TreeCanal | mango tree and branch 217; 2.5 m canal 231.5; 5 mangoes | A tree, then a canal after its branch. |
| 240 | 258 | ChilliStraight | chilli 241; 10 mangoes | A chilli and a long straight. |
| 258 | 300 | Orchard | mango tree and branch 262; mango tree and branch 273; mango tree and branch 284; feather 2 at 277.3, 3.2 m up | Three trees in a row: branch to branch, a feather above the middle one. |
| 300 | 324 | Mischief | cow dung 304; pot stack 312 (knocked in by the rooster); mischief 313; 2.5 m canal 318.5; 15 mangoes | Dung; the rooster knocks the pots by the well into the road; a canal after. |
| 324 | 356 | WideTree | 4.5 m canal 327; feather 3 at 329.25, 3.4 m up; small haystack 340.2; mango tree and branch 343; 10 mangoes | The wide canal (double jump, a feather at its top), then a tree. |
| 356 | 374 | ChilliRun | chilli 357; 10 mangoes | A chilli and a run of mangoes. |
| 374 | 398 | CartCanal | bullock cart 377; 2.5 m canal 388; 11 mangoes | The cart, then a canal. |
| 398 | 438 | TreesAndStacks | mango tree and branch 401; small haystack 415; small haystack 422.2; mango tree and branch 425; 6 mangoes | A tree, a haystack, a tree. |
| 438 | 456 | FinalChilli | chilli 439; 10 mangoes | The last chilli. |
| 456 | 478 | PlankDung | 3.5 m canal 459 with the plank; cow dung 471; 10 mangoes | The plank, then dung. |
| 478 | 522 | LastTrees | small haystack 480.2; mango tree and branch 483; 2.5 m canal 497.5; mango tree and branch 506; 8 mangoes | The last two trees, a canal between them. |
| 522 | 544 | DungStack | cow dung 526; small haystack 534; 8 mangoes | Dung, then a haystack. |
| 544 | 574 | LastWide | 4.5 m canal 549; 7 mangoes | The last wide canal. |
| 574 | 606 | OpenGrove | 12 mangoes | The road opens out: if he is still ahead, he gets away at 600 m. |

## The audit

* canal at 327.0 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* canal at 549.0 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* a clean run from a 12 m start catches him after about 19 s, at about 131 m (without chillies)
* first of each: haystack 18 m, branch 22 m, canal 42 m, dung 82 m, bridge 134 m, cart 149 m, pots 312 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
haystack      18.3 m (FirstTree): small: hop onto it or over it (over: 112 ms)
branch        22.0 m (FirstTree): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
canal         42.0 m (Canal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
branch        57.0 m (Branch): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
dung          81.7 m (Dung): held window 434 ms, tap 255 ms
haystack     109.3 m (TreeFeather): small: hop onto it or over it (over: 112 ms)
branch       113.0 m (TreeFeather): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
bridge       134.0 m (Plank): a 3.5 m canal with the plank: run across (a held jump clears it)
cart         149.0 m (CartTree): jump onto the bed and run off the end
branch       155.0 m (CartTree): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
canal        176.0 m (CanalDung): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
dung         185.7 m (CanalDung): held window 434 ms, tap 255 ms
haystack     196.1 m (Haystacks): small: hop onto it or over it (over: 112 ms)
haystack     204.1 m (Haystacks): small: hop onto it or over it (over: 112 ms)
branch       218.0 m (TreeCanal): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
canal        231.5 m (TreeCanal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
branch       263.0 m (Orchard): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
branch       274.0 m (Orchard): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
branch       285.0 m (Orchard): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
dung         303.7 m (Mischief): held window 434 ms, tap 255 ms
pots         311.8 m (Mischief): held window 340 ms, tap 127 ms
canal        318.5 m (Mischief): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
canal        327.0 m (WideTree): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
haystack     340.3 m (WideTree): small: hop onto it or over it (over: 112 ms)
branch       344.0 m (WideTree): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
cart         377.0 m (CartCanal): jump onto the bed and run off the end
canal        388.0 m (CartCanal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
branch       402.0 m (TreesAndStacks): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
haystack     415.1 m (TreesAndStacks): small: hop onto it or over it (over: 112 ms)
haystack     422.3 m (TreesAndStacks): small: hop onto it or over it (over: 112 ms)
branch       426.0 m (TreesAndStacks): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
bridge       459.0 m (PlankDung): a 3.5 m canal with the plank: run across (a held jump clears it)
dung         470.7 m (PlankDung): held window 434 ms, tap 255 ms
haystack     480.3 m (LastTrees): small: hop onto it or over it (over: 112 ms)
branch       484.0 m (LastTrees): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
canal        497.5 m (LastTrees): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
branch       507.0 m (LastTrees): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
dung         525.7 m (DungStack): held window 434 ms, tap 255 ms
haystack     534.1 m (DungStack): small: hop onto it or over it (over: 112 ms)
canal        549.0 m (LastWide): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
```

Problems: none.
