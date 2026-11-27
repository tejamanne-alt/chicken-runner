# Level 2: Washing day

The beat sheet for level 2 (zone 1). It is written by `ArtSource/tools/levels/level2.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level2.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 1: the kid runs at 6 m/s, the rooster at 5.5 m/s; a held jump is 3.70 m long and 1.4 m high; the course is 500 m.

## The opening: washing day

No basket: the chase starts in the lane with the rooster 12 m ahead (the Ready screen; tap to chase). Sarees dry
on lines behind the lane and a woman draws the morning kolam. A clean run catches him at about 110 m.

## The new things

* **Clotheslines** (the slide): sarees across the lane from 0.7 m down to 1.6 m up. Swipe down to slide under; the
  low mangoes show the line. A double jump clears the top too (a feather sits over one).
* **The rope cot** (the bounce): run into it for a 2.4 m bounce, landing about 5 m on, with mangoes along the arc
  and a feather at its top.

## The shape of it

Teach (to 146 m): the slide alone, then in rhythm, the cot, a chilli, a line then pots, the cart. Practise (to
292 m): the cot into a line, lines with the dog, the puddle and pots, three lines in a row. Test (to 500 m): the
rooster's mischief, cot-line-cot, line-dog-line, the last cart, everything once more, then the lane opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | WashingYard | 5 mangoes | Washing day: sarees drying behind the lane, the rooster ahead; tap to chase. |
| 14 | 32 | FirstLine | clothesline 24; 4 mangoes | The first clothesline: swipe down and slide under; the low mangoes show the way. |
| 32 | 48 | Pots | pot stack 40; 5 mangoes | A pot stack: the jump again. |
| 48 | 68 | TwoLines | clothesline 54; clothesline 62; 8 mangoes | Two clotheslines 8 m apart: slide, up, slide. |
| 68 | 90 | FirstCot | rope cot 76; feather 1 at 78.8, 4.3 m up; 6 mangoes | The rope cot: run into it and bounce; a feather at the top for a double jump. |
| 90 | 106 | Breather | chilli 91; 9 mangoes | A breather: a wave of mangoes and the first chilli. |
| 106 | 126 | LinePots | clothesline 111; pot stack 119; 9 mangoes | A clothesline, then a pot stack: slide, then jump. |
| 126 | 146 | Cart | bullock cart 130; feather 2 at 134.2, 3.4 m up; 6 mangoes | The bullock cart: onto its bed and off; a feather above it. |
| 146 | 168 | CotLine | rope cot 149; clothesline 162; 10 mangoes | The cot, then a clothesline: bounce, land, slide. |
| 168 | 188 | DogLine | sleeping dog 172.5; clothesline 182; 9 mangoes | The sleeping dog, then a clothesline. |
| 188 | 210 | LinePuddle | clothesline 192; hand-pump puddle 201.5; 9 mangoes | A clothesline, then the hand-pump puddle. |
| 210 | 228 | ChilliStraight | chilli 211; 10 mangoes | A chilli and a long straight. |
| 228 | 248 | CotPots | rope cot 231; pot stack 243; 11 mangoes | The cot, then a pot stack after the landing. |
| 248 | 274 | ThreeLines | clothesline 252; clothesline 260; feather 3 at 260, 2.9 m up; clothesline 268; 12 mangoes | Three clotheslines in a row: slide, slide, slide. A feather over the middle one. |
| 274 | 292 | DungPots | cow dung 279; pot stack 286; 10 mangoes | Dung, then pots: tap, jump. |
| 292 | 318 | Mischief | hand-pump puddle 296; pot stack 306 (knocked in by the rooster); mischief 307; clothesline 314; 14 mangoes | The puddle; the rooster knocks the pots off their stand; a clothesline after. |
| 318 | 348 | CotLineCot | rope cot 321; clothesline 333; rope cot 339; 16 mangoes | Cot, clothesline, cot. |
| 348 | 366 | ChilliLane | chilli 349; 9 mangoes | A breather and a chilli. |
| 366 | 392 | LineDogLine | clothesline 370; sleeping dog 378; clothesline 387; 13 mangoes | Clothesline, dog, clothesline. |
| 392 | 414 | LastCart | bullock cart 396; pot stack 406; 11 mangoes | The last cart, and pots after it. |
| 414 | 432 | FinalChilli | chilli 415; 9 mangoes | The last chilli. |
| 432 | 472 | LastTest | clothesline 436; pot stack 443; rope cot 449; clothesline 461; cow dung 468; 24 mangoes | Clothesline, pots, the cot, a clothesline, dung: everything once more. |
| 472 | 506 | OpenLane | 12 mangoes | The lane opens out: if he is still ahead, he gets away at 500 m. |

## The audit

* a clean run from a 12 m start catches him after about 22 s, at about 134 m (without chillies)
* first of each: clothesline 23 m, pots 40 m, cot 76 m, cart 130 m, dog 172 m, puddle 201 m, dung 279 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
clothesline   23.1 m (FirstLine): slide window 258 ms, double jump over 175 ms
pots          39.8 m (Pots): held window 321 ms, tap 108 ms
clothesline   53.1 m (TwoLines): slide window 258 ms, double jump over 175 ms
clothesline   61.1 m (TwoLines): slide window 258 ms, double jump over 175 ms
cot           76.0 m (FirstCot): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
clothesline  110.2 m (LinePots): slide window 258 ms, double jump over 175 ms
pots         118.8 m (LinePots): held window 321 ms, tap 108 ms
cart         130.0 m (Cart): jump onto the bed and run off the end
cot          149.0 m (CotLine): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
clothesline  161.2 m (CotLine): slide window 258 ms, double jump over 175 ms
dog          172.1 m (DogLine): held window 313 ms, tap 125 ms
clothesline  181.2 m (DogLine): slide window 258 ms, double jump over 175 ms
clothesline  191.2 m (LinePuddle): slide window 258 ms, double jump over 175 ms
puddle       200.7 m (LinePuddle): held window 246 ms, tap 71 ms
cot          231.0 m (CotPots): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
pots         242.8 m (CotPots): held window 321 ms, tap 108 ms
clothesline  251.2 m (ThreeLines): slide window 258 ms, double jump over 175 ms
clothesline  259.1 m (ThreeLines): slide window 258 ms, double jump over 175 ms
clothesline  267.1 m (ThreeLines): slide window 258 ms, double jump over 175 ms
dung         278.7 m (DungPots): held window 413 ms, tap 233 ms
pots         285.8 m (DungPots): held window 321 ms, tap 108 ms
puddle       295.2 m (Mischief): held window 246 ms, tap 71 ms
pots         305.8 m (Mischief): held window 321 ms, tap 108 ms
clothesline  313.1 m (Mischief): slide window 258 ms, double jump over 175 ms
cot          321.0 m (CotLineCot): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
clothesline  332.1 m (CotLineCot): slide window 258 ms, double jump over 175 ms
cot          339.0 m (CotLineCot): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
clothesline  369.1 m (LineDogLine): slide window 258 ms, double jump over 175 ms
dog          377.6 m (LineDogLine): held window 313 ms, tap 125 ms
clothesline  386.1 m (LineDogLine): slide window 258 ms, double jump over 175 ms
cart         396.0 m (LastCart): jump onto the bed and run off the end
pots         405.8 m (LastCart): held window 321 ms, tap 108 ms
clothesline  435.1 m (LastTest): slide window 258 ms, double jump over 175 ms
pots         442.8 m (LastTest): held window 321 ms, tap 108 ms
cot          449.0 m (LastTest): a trampoline: run into it (no input) for a 2.4 m bounce, landing about 6.0 m on
clothesline  460.1 m (LastTest): slide window 258 ms, double jump over 175 ms
dung         467.7 m (LastTest): held window 413 ms, tap 233 ms
```

Problems: none.
