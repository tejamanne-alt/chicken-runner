# Level 6: Buffalo and haystacks

The beat sheet for level 6 (zone 2). It is written by `ArtSource/tools/levels/level6.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level6.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 2: the kid runs at 7 m/s, the rooster at 6.4 m/s; a held jump is 4.32 m long and 1.4 m high; the course is 600 m.

## The opening: the pond

No basket: the chase starts on the road by the buffalo pond with the rooster 12 m ahead (the Ready screen; tap to
chase). A clean run catches him at about 131 m.

## The new things

* **The buffalo:** its back is 1.1 m up. Jump onto it for a 2.6 m bounce, landing about 7 m on (mangoes trace it,
  a feather sits at the top of one); run into it and she climbs over, slowly.
* **Haystack chains:** small stacks (1.05 m: hop onto or over) and big ones (1.85 m: a double jump).
* **The rooster's mischief** by the well.

## The shape of it

Teach (to 144 m): the buffalo, small stacks, a big stack, a chilli, a chain, a canal. Practise (to 280 m): the
buffalo with a feather, dung and stacks, the wide canal, a buffalo into stacks, a branch. Test (to 600 m): the
mischief, two buffaloes, a big chain, the cart and canals, everything once more, then the fields open out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | Pond | 5 mangoes | The road by the buffalo pond, haystacks drying: the rooster struts ahead; tap to chase. |
| 14 | 38 | FirstBuffalo | buffalo 22; 6 mangoes | The first buffalo: jump onto its back and it bounces you high. |
| 38 | 56 | SmallStacks | small haystack 42; small haystack 50; 6 mangoes | Two small haystacks: hop, hop. |
| 56 | 78 | BigStack | big haystack 63; feather 1 at 64.395, 3.7 m up; 5 mangoes | A big haystack: a double jump (the mangoes show it). A feather above it. |
| 78 | 94 | Breather | chilli 79; 9 mangoes | A breather: mangoes and a chilli. |
| 94 | 128 | Chain | small haystack 97; big haystack 103.667; small haystack 111.363; big haystack 118.03; 16 mangoes | A haystack chain: small, big, small, big. |
| 128 | 144 | Canal | 2.5 m canal 134; 5 mangoes | A 2.5 m canal. |
| 144 | 166 | BuffaloFeather | buffalo 148; feather 2 at 152.215, 4.4 m up; 6 mangoes | A buffalo with a feather at the top of its bounce. |
| 166 | 186 | DungStack | cow dung 170; small haystack 178; 8 mangoes | Dung, then a small haystack. |
| 186 | 208 | WideCanal | 4.5 m canal 192; 7 mangoes | The wide canal: double jump, or wade. |
| 208 | 226 | ChilliStraight | chilli 209; 10 mangoes | A chilli and a long straight. |
| 226 | 258 | BuffaloStacks | buffalo 229; small haystack 241; big haystack 249; 14 mangoes | A buffalo, then a small and a big haystack. |
| 258 | 280 | Branch | small haystack 261.2; mango tree and branch 264; 3 mangoes | A mango tree, a haystack as the step up to its branch. |
| 280 | 304 | Mischief | cow dung 284; pot stack 292 (knocked in by the rooster); mischief 293; 2.5 m canal 298.5; 15 mangoes | Dung; the rooster knocks the pots by the well into the road; a canal after. |
| 304 | 334 | TwoBuffaloes | buffalo 307; buffalo 320; 12 mangoes | Two buffaloes: bounce, land, bounce. |
| 334 | 370 | BigChain | big haystack 337; small haystack 344.695; big haystack 351.363; feather 3 at 352.758, 3.7 m up; 13 mangoes | Big, small, big: a feather above the last. |
| 370 | 388 | ChilliLane | chilli 371; 10 mangoes | A chilli to win back ground. |
| 388 | 412 | CartCanal | bullock cart 391; 2.5 m canal 402; 11 mangoes | The cart, then a canal. |
| 412 | 446 | BuffaloWide | buffalo 415; 4.5 m canal 429; 13 mangoes | A buffalo, then the wide canal. |
| 446 | 474 | StacksDung | small haystack 449; cow dung 457.5; big haystack 465; 13 mangoes | Small, dung, big. |
| 474 | 492 | FinalChilli | chilli 475; 10 mangoes | The last chilli. |
| 492 | 542 | LastTest | buffalo 495; small haystack 507; big haystack 513.667; 2.5 m canal 524.363; 19 mangoes | A buffalo, a chain, a canal: everything once more. |
| 542 | 606 | OpenFields | 14 mangoes | The fields open out: if he is still ahead, he gets away at 600 m. |

## The audit

* canal at 192.0 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* canal at 429.0 (4.5 m): a held jump is a gamble (5 ms); the double jump is the way
* a clean run from a 12 m start catches him after about 19 s, at about 131 m (without chillies)
* first of each: buffalo 22 m, haystack 42 m, canal 134 m, dung 170 m, branch 265 m, pots 292 m, cart 391 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
buffalo       22.4 m (FirstBuffalo): jump onto its back (214 ms) for a 2.6 m bounce, landing about 6.8 m on; or a slow climb over
haystack      42.1 m (SmallStacks): small: hop onto it or over it (over: 112 ms)
haystack      50.1 m (SmallStacks): small: hop onto it or over it (over: 112 ms)
haystack      63.2 m (BigStack): big: hop onto it or over it (over: 149 ms)
haystack      97.1 m (Chain): small: hop onto it or over it (over: 112 ms)
haystack     103.9 m (Chain): big: hop onto it or over it (over: 149 ms)
haystack     111.5 m (Chain): small: hop onto it or over it (over: 112 ms)
haystack     118.2 m (Chain): big: hop onto it or over it (over: 149 ms)
canal        134.0 m (Canal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
buffalo      148.4 m (BuffaloFeather): jump onto its back (214 ms) for a 2.6 m bounce, landing about 6.8 m on; or a slow climb over
dung         169.7 m (DungStack): held window 434 ms, tap 255 ms
haystack     178.1 m (DungStack): small: hop onto it or over it (over: 112 ms)
canal        192.0 m (WideCanal): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
buffalo      229.4 m (BuffaloStacks): jump onto its back (214 ms) for a 2.6 m bounce, landing about 6.8 m on; or a slow climb over
haystack     241.1 m (BuffaloStacks): small: hop onto it or over it (over: 112 ms)
haystack     249.2 m (BuffaloStacks): big: hop onto it or over it (over: 149 ms)
haystack     261.3 m (Branch): small: hop onto it or over it (over: 112 ms)
branch       265.0 m (Branch): optional: jump at the branch to pull up onto it (mangoes along it), or run on under it
dung         283.7 m (Mischief): held window 434 ms, tap 255 ms
pots         291.8 m (Mischief): held window 340 ms, tap 127 ms
canal        298.5 m (Mischief): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
buffalo      307.4 m (TwoBuffaloes): jump onto its back (214 ms) for a 2.6 m bounce, landing about 6.8 m on; or a slow climb over
buffalo      320.4 m (TwoBuffaloes): jump onto its back (214 ms) for a 2.6 m bounce, landing about 6.8 m on; or a slow climb over
haystack     337.2 m (BigChain): big: hop onto it or over it (over: 149 ms)
haystack     344.8 m (BigChain): small: hop onto it or over it (over: 112 ms)
haystack     351.6 m (BigChain): big: hop onto it or over it (over: 149 ms)
cart         391.0 m (CartCanal): jump onto the bed and run off the end
canal        402.0 m (CartCanal): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
buffalo      415.4 m (BuffaloWide): jump onto its back (214 ms) for a 2.6 m bounce, landing about 6.8 m on; or a slow climb over
canal        429.0 m (BuffaloWide): 4.5 m: held jump 5 ms, double jump 405 ms; wading loses 5.5 m
haystack     449.1 m (StacksDung): small: hop onto it or over it (over: 112 ms)
dung         457.2 m (StacksDung): held window 434 ms, tap 255 ms
haystack     465.2 m (StacksDung): big: hop onto it or over it (over: 149 ms)
buffalo      495.4 m (LastTest): jump onto its back (214 ms) for a 2.6 m bounce, landing about 6.8 m on; or a slow climb over
haystack     507.1 m (LastTest): small: hop onto it or over it (over: 112 ms)
haystack     513.9 m (LastTest): big: hop onto it or over it (over: 149 ms)
canal        524.4 m (LastTest): 2.5 m: held jump 290 ms, double jump 690 ms; wading loses 3.1 m
```

Problems: none.
