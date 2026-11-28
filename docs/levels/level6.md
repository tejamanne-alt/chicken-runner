# Level 6: Buffalo and haystacks

The beat sheet for level 6 (zone 2). It is written by `ArtSource/tools/levels/level6.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level6.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 2: the kid runs at 3.5 m/s, the rooster at 3.15 m/s; a held jump is 2.16 m long and 1.4 m high; the course is 295 m.

## The opening: the pond

No basket: the chase starts on the road by the buffalo pond with the rooster 7 m ahead (the Ready screen; tap to
chase). The kid runs at a small child's real pace, 3.5 m/s, against his 3.15: a clean run catches him at about
62 m, some 18 s in.

## The new things

* **The buffalo:** its back is 1.1 m up. Jump onto it (291 ms to take off) for a 2.6 m bounce, landing about
  3.5 m on (mangoes trace it; a feather sits above one for a double jump at the top of the bounce); run into it
  and she climbs over, slowly.
* **Haystack chains:** small straw heaps (1.05 m: hop onto or over) and big ones (1.85 m: a double jump onto the
  top, or a slow vault), 2.75 m apart.
* **The rooster's mischief** by a farmer's hut: he knocks the hens' basket into the road behind him.

## What is on the road

Only what lies on a field road at harvest: the buffaloes in their mud, the straw heaps, the canals (1.2 m to jump,
1.8 m with the plank, 2.6 m to double jump or wade), sacks of paddy waiting for the cart, cow dung, ducks, a goat
kid and a mango branch over the road. Things to jump are about 4 m apart, and each chilli has 11 m or more clear
after it.

## The shape of it

Teach (to 70 m): the buffalo, small stacks, a big stack, a chilli, a chain, a canal. Practise (to 133 m): the
buffalo with a feather, dung and stacks, the wide canal, a buffalo into stacks, a branch. Test (to 295 m): the
mischief, two buffaloes, a big chain, the sacks and canals, the plank and a goat kid, everything once more, the
last buffalo, then the fields open out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 7 | Pond | 4 mangoes | The road by the buffalo pond, haystacks drying: the rooster struts ahead; tap to chase. |
| 7 | 16 | FirstBuffalo | buffalo 11; 5 mangoes | The first buffalo: jump onto its back and it bounces you high. |
| 16 | 26 | SmallStacks | small haystack 17.5; small haystack 21.5; 6 mangoes | Two small haystacks: hop, hop. |
| 26 | 36 | BigStack | big haystack 28; feather 1 at 29.395, 3.7 m up; 5 mangoes | A big haystack: a double jump onto it (the mangoes show it). A feather above it. |
| 36 | 44 | Breather | chilli 36.5; 8 mangoes | A breather: mangoes and a chilli. |
| 44 | 63 | Chain | small haystack 47.5; big haystack 51.417; small haystack 56.363; big haystack 60.28; 16 mangoes | A haystack chain: small, big, small, big. |
| 63 | 70 | Canal | 1.2 m canal 66; 5 mangoes | A 1.2 m canal. |
| 70 | 79 | BuffaloFeather | buffalo 72.5; feather 2 at 75, 5.2 m up; 5 mangoes | A buffalo, a feather above its bounce for a double jump at the top. |
| 79 | 89 | DungStack | cow dung 80; small haystack 84; 8 mangoes | Dung, then a small haystack. |
| 89 | 96 | WideCanal | 2.6 m canal 89.5; 7 mangoes | The wide canal: double jump, or wade. |
| 96 | 107 | ChilliStraight | chilli 96.5; 9 mangoes | A chilli and a long straight. |
| 107 | 121 | BuffaloStacks | buffalo 108.5; small haystack 114; big haystack 117.5; 13 mangoes | A buffalo, then a small and a big haystack. |
| 121 | 133 | Branch | small haystack 122.5; mango tree and branch 124.3; 4 mangoes | A mango tree, a haystack as the step up to its branch. |
| 133 | 146 | Mischief | cow dung 134; hens' basket 138.5 (knocked in by the rooster); mischief 139; 1.2 m canal 142; 15 mangoes | Dung; the rooster knocks the hens' basket by the farmer's hut into the road; a canal after. |
| 146 | 157 | TwoBuffaloes | buffalo 146.3; buffalo 152; 10 mangoes | Two buffaloes: bounce, land, bounce. |
| 157 | 171 | BigChain | big haystack 158.5; small haystack 163.445; big haystack 167.363; feather 3 at 168.758, 3.7 m up; 13 mangoes | Big, small, big: a feather above the last. |
| 171 | 180 | ChilliLane | chilli 171.5; 7 mangoes | A chilli to win back ground. |
| 180 | 191 | SacksCanal | sacks of paddy 182.5; 1.2 m canal 186.5; 7 mangoes | The harvest's sacks of paddy waiting for the cart: onto them, then a canal. |
| 191 | 203 | BuffaloWide | buffalo 192; 2.6 m canal 198; 12 mangoes | A buffalo, then the wide canal. |
| 203 | 216 | StacksDung | small haystack 204; cow dung 208.5; big haystack 212.5; 13 mangoes | Small, dung, big. |
| 216 | 226 | PlankGoat | 1.8 m canal 218 with the plank; 1 goat kid 223; 9 mangoes | The plank over a 1.8 m canal, then a goat kid wandering across. |
| 226 | 235 | FinalChilli | chilli 226.5; 7 mangoes | The last chilli. |
| 235 | 262 | LastTest | buffalo 238; small haystack 243.5; big haystack 247.417; 1.2 m canal 252; 2 ducks 257; 23 mangoes | A buffalo, a small and a big stack, a canal, ducks: everything once more. |
| 262 | 274 | LastBuffalo | cow dung 264; buffalo 268; 10 mangoes | Dung, and the last buffalo to bounce off. |
| 274 | 305 | OpenFields | 14 mangoes | The fields open out: if he is still ahead, he gets away at 295 m. |

## The audit

* a clean run from a 7 m start catches him after about 18 s, at about 62 m (without chillies)
* first of each: buffalo 11 m, haystack 18 m, canal 66 m, dung 80 m, branch 125 m, hensbasket 138 m, sacks 182 m, bridge 218 m, goats 223 m, ducks 257 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
buffalo       11.4 m (FirstBuffalo): jump onto its back (291 ms) for a 2.6 m bounce, landing about 3.5 m on; or a slow climb over
haystack      17.6 m (SmallStacks): small: hop onto it or over it
haystack      21.6 m (SmallStacks): small: hop onto it or over it
haystack      28.2 m (BigStack): big: hop onto it or over it
haystack      47.6 m (Chain): small: hop onto it or over it
haystack      51.6 m (Chain): big: hop onto it or over it
haystack      56.5 m (Chain): small: hop onto it or over it
haystack      60.5 m (Chain): big: hop onto it or over it
canal         66.0 m (Canal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
buffalo       72.9 m (BuffaloFeather): jump onto its back (291 ms) for a 2.6 m bounce, landing about 3.5 m on; or a slow climb over
dung          79.7 m (DungStack): held window 305 ms, tap 126 ms
haystack      84.1 m (DungStack): small: hop onto it or over it
canal         89.5 m (WideCanal): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
buffalo      108.9 m (BuffaloStacks): jump onto its back (291 ms) for a 2.6 m bounce, landing about 3.5 m on; or a slow climb over
haystack     114.1 m (BuffaloStacks): small: hop onto it or over it
haystack     117.7 m (BuffaloStacks): big: hop onto it or over it
haystack     122.6 m (Branch): small: hop onto it or over it
branch       125.3 m (Branch): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
dung         133.7 m (Mischief): held window 305 ms, tap 126 ms
hensbasket   138.2 m (Mischief): held window 216 ms, tap 12 ms
canal        142.0 m (Mischief): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
buffalo      146.7 m (TwoBuffaloes): jump onto its back (291 ms) for a 2.6 m bounce, landing about 3.5 m on; or a slow climb over
buffalo      152.4 m (TwoBuffaloes): jump onto its back (291 ms) for a 2.6 m bounce, landing about 3.5 m on; or a slow climb over
haystack     158.7 m (BigChain): big: hop onto it or over it
haystack     163.6 m (BigChain): small: hop onto it or over it
haystack     167.6 m (BigChain): big: hop onto it or over it
sacks        182.5 m (SacksCanal): hop onto the sacks and run off the end
canal        186.5 m (SacksCanal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
buffalo      192.4 m (BuffaloWide): jump onto its back (291 ms) for a 2.6 m bounce, landing about 3.5 m on; or a slow climb over
canal        198.0 m (BuffaloWide): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
haystack     204.1 m (StacksDung): small: hop onto it or over it
dung         208.2 m (StacksDung): held window 305 ms, tap 126 ms
haystack     212.7 m (StacksDung): big: hop onto it or over it
bridge       218.0 m (PlankGoat): a 1.8 m canal with the plank: run across (a held jump clears it)
goats        222.8 m (PlankGoat): held window 270 ms, tap 74 ms
buffalo      238.4 m (LastTest): jump onto its back (291 ms) for a 2.6 m bounce, landing about 3.5 m on; or a slow climb over
haystack     243.6 m (LastTest): small: hop onto it or over it
haystack     247.6 m (LastTest): big: hop onto it or over it
canal        252.0 m (LastTest): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
ducks        256.7 m (LastTest): held window 224 ms, tap 32 ms
dung         263.7 m (LastBuffalo): held window 305 ms, tap 126 ms
buffalo      268.4 m (LastBuffalo): jump onto its back (291 ms) for a 2.6 m bounce, landing about 3.5 m on; or a slow climb over
```

Problems: none.
