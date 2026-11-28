# Level 5: Mango trees

The beat sheet for level 5 (zone 2). It is written by `ArtSource/tools/levels/level5.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level5.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 2: the kid runs at 3.5 m/s, the rooster at 3.15 m/s; a held jump is 2.16 m long and 1.4 m high; the course is 295 m.

## The opening: the grove

No basket: the chase starts on the bund road into the mango grove with the rooster 7 m ahead (the Ready screen;
tap to chase). The kid runs at a small child's real pace, 3.5 m/s, against his 3.15: a clean run catches him at
about 62 m, some 18 s in.

## The branches

* A mango tree's branch reaches over the road from 1 m to 5 m past its trunk, 2.3 m up, mangoes along it.
* Jump at it and she pulls herself up (a quick climb), runs along it and drops off its end; or she runs on under.
* From the road, a double jump gets her up from anywhere in the 2.9 m before the branch; a single jump only from
  two narrow spots. So most trees have a step before them, as a field road really has:
  * a **small haystack**, its end 1.6 m short of the branch: hop onto it and jump again from its top (226 ms);
  * **sacks of paddy** waiting for the cart (0.8 m), the branch 2.2 m on from where they start: hop onto them and
    jump again from anywhere on them (217 ms).
* In the orchard the trees stand 6 m apart, 2 m between branches: jump from one branch to the next (360 ms).
* The rooster flutters up onto every branch and down off its end (in the orchard, branch to branch; at the sacks,
  one arc over them and up).

## What is on the road

Only what lies on a field road: the canals (1.2 m to jump, 1.8 m with the plank, 2.6 m to double jump or wade),
ducks waddling up from them, cow dung, small straw heaps, the sacks of paddy, and the water pots by the well, which
the rooster knocks into the road. Things to jump are about 4 m apart, and each chilli has 11 m or more clear after it.

## The shape of it

Teach (to 78 m): a tree with a haystack step, a canal, a branch with no step, dung, a chilli, a tree with a
feather, the plank. Practise (to 153 m): the sacks as a step, canals and dung, haystacks, a tree then a canal, an
orchard of three trees, branch to branch. Test (to 295 m): the rooster's mischief by the well, the wide canal and a
tree, ducks and a canal, trees and steps, the last trees and canals, then the road opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 8 | Grove | 4 mangoes | The bund road into the mango grove: the rooster struts ahead; tap to chase. |
| 8 | 20 | FirstTree | small haystack 11.7; mango tree and branch 13.5; 4 mangoes | The first mango tree, a haystack before it: hop onto the stack, jump at the branch, run along it for the mangoes. |
| 20 | 29 | Canal | 1.2 m canal 23.5; 5 mangoes | A 1.2 m canal: jump it. |
| 29 | 41 | Branch | mango tree and branch 31 | A branch with no step: a double jump gets her up (or a well-timed jump). |
| 41 | 49 | Dung | cow dung 44.5; 5 mangoes | Cow dung on the road. |
| 49 | 57 | Breather | chilli 49.5; 8 mangoes | A breather: mangoes and a chilli. |
| 57 | 69 | TreeFeather | small haystack 60.7; mango tree and branch 62.5; feather 1 at 66.8, 3.2 m up; 4 mangoes | A tree with a haystack step and a feather above its branch: up, along, a double jump at the end. |
| 69 | 78 | Plank | 1.8 m canal 71.5 with the plank; 4 mangoes | The plank over a 1.8 m canal. |
| 78 | 90 | SacksTree | sacks of paddy 80; mango tree and branch 81.2; 3 mangoes | Sacks of paddy waiting for the cart as the step: onto them, and up onto the branch. |
| 90 | 99 | CanalDung | 1.2 m canal 90.5; cow dung 95; 10 mangoes | A canal, then dung. |
| 99 | 108 | Haystacks | small haystack 100; small haystack 104; 6 mangoes | Two small haystacks: hop, hop. |
| 108 | 122 | TreeCanal | mango tree and branch 110; 1.2 m canal 118.5; 5 mangoes | A tree, then a canal after its branch. |
| 122 | 131 | ChilliStraight | chilli 122.5; 7 mangoes | A chilli and a long straight. |
| 131 | 153 | Orchard | mango tree and branch 133; mango tree and branch 139; mango tree and branch 145; feather 2 at 143.3, 3.2 m up; 6 mangoes | Three trees in a row, 2 m between their branches: branch to branch, a feather above the middle one. |
| 153 | 166 | Mischief | cow dung 156; pot stack 160.5 (knocked in by the rooster); mischief 161; 1.2 m canal 164; 15 mangoes | Dung; the rooster knocks the water pots by the well into the road; a canal after. |
| 166 | 183 | WideTree | 2.6 m canal 168; feather 3 at 169.4, 3.1 m up; small haystack 174; mango tree and branch 175.8; 11 mangoes | The wide canal (double jump, a feather at its top), then a tree with a haystack step. |
| 183 | 192 | ChilliRun | chilli 183.5; 7 mangoes | A chilli and a run of mangoes. |
| 192 | 204 | DucksCanal | 2 ducks 195; 1.2 m canal 198.5; 10 mangoes | Ducks waddling up from the canal: jump them, then the canal. |
| 204 | 226 | TreesAndStacks | mango tree and branch 205; small haystack 213.5; sacks of paddy 217.5; mango tree and branch 218.7; 6 mangoes | A tree, a haystack, then sacks as the step up to another tree. |
| 226 | 235 | FinalChilli | chilli 226.5; 7 mangoes | The last chilli. |
| 235 | 246 | PlankDung | 1.8 m canal 238 with the plank; cow dung 243; 9 mangoes | The plank, then dung. |
| 246 | 268 | LastTrees | small haystack 248.2; mango tree and branch 250; 1.2 m canal 258; mango tree and branch 261; 9 mangoes | The last two trees (a haystack before the first), a canal between them. |
| 268 | 278 | DungStack | cow dung 270.5; small haystack 274; 8 mangoes | Dung, then a haystack. |
| 278 | 290 | LastWide | 2.6 m canal 280; 7 mangoes | The last wide canal. |
| 290 | 305 | OpenGrove | 9 mangoes | The road opens out: if he is still ahead, he gets away at 295 m. |

## The audit

* a clean run from a 7 m start catches him after about 18 s, at about 62 m (without chillies)
* first of each: haystack 12 m, branch 14 m, canal 24 m, dung 44 m, bridge 72 m, sacks 80 m, pots 160 m, ducks 195 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
haystack      11.8 m (FirstTree): small: hop onto it or over it
branch        14.5 m (FirstTree): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
canal         23.5 m (Canal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
branch        32.0 m (Branch): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
dung          44.2 m (Dung): held window 305 ms, tap 126 ms
haystack      60.8 m (TreeFeather): small: hop onto it or over it
branch        63.5 m (TreeFeather): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
bridge        71.5 m (Plank): a 1.8 m canal with the plank: run across (a held jump clears it)
sacks         80.0 m (SacksTree): hop onto the sacks and run off the end
branch        82.2 m (SacksTree): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
canal         90.5 m (CanalDung): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
dung          94.7 m (CanalDung): held window 305 ms, tap 126 ms
haystack     100.1 m (Haystacks): small: hop onto it or over it
haystack     104.1 m (Haystacks): small: hop onto it or over it
branch       111.0 m (TreeCanal): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
canal        118.5 m (TreeCanal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
branch       134.0 m (Orchard): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
branch       140.0 m (Orchard): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
branch       146.0 m (Orchard): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
dung         155.7 m (Mischief): held window 305 ms, tap 126 ms
pots         160.3 m (Mischief): held window 226 ms, tap 13 ms
canal        164.0 m (Mischief): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
canal        168.0 m (WideTree): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
haystack     174.1 m (WideTree): small: hop onto it or over it
branch       176.8 m (WideTree): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
ducks        194.7 m (DucksCanal): held window 224 ms, tap 32 ms
canal        198.5 m (DucksCanal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
branch       206.0 m (TreesAndStacks): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
haystack     213.6 m (TreesAndStacks): small: hop onto it or over it
sacks        217.5 m (TreesAndStacks): hop onto the sacks and run off the end
branch       219.7 m (TreesAndStacks): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
bridge       238.0 m (PlankDung): a 1.8 m canal with the plank: run across (a held jump clears it)
dung         242.7 m (PlankDung): held window 305 ms, tap 126 ms
haystack     248.3 m (LastTrees): small: hop onto it or over it
branch       251.0 m (LastTrees): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
canal        258.0 m (LastTrees): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
branch       262.0 m (LastTrees): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
dung         270.2 m (DungStack): held window 305 ms, tap 126 ms
haystack     274.1 m (DungStack): small: hop onto it or over it
canal        280.0 m (LastWide): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
```

Problems: none.
