# Level 1: Pots and the sleeping dog

The beat sheet for level 1 (zone 1). It is written by `ArtSource/tools/levels/level1.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level1.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 1: the kid runs at 6 m/s, the rooster at 5.5 m/s; a held jump is 3.70 m long and 1.4 m high; the course is 500 m.

## The opening: the neighbour's yard

The neighbour naps on his rope cot behind the lane; his hens peck about. The kid tiptoes in from -4.4 m to the
bamboo basket the rooster is sitting under (a tap hurries her). The player holds to lift it by its near rim; it turns
up on its far rim over 1.6 s of holding. Letting go part way drops it back with a clunk, and the neighbour stirs.
Fully up, the rooster bursts out and sprints off, the kid flings the basket aside, and the neighbour wakes shouting.

* A lift with no drop gives the rooster a **10 m** head start; any drop gives him **14 m**.
* A retry skips the opening and keeps the head start it earned; loading the level again plays it again.
* The rules are `Core/BasketLift.cs` (tested in `BasketLiftTests`); the flow is `GameFlow`'s Intro state; the
  basket, its hinge and the neighbour's two cut-outs are `BasketIntro`.

## The shape of it

Teach (to about 140 m): one new thing at a time, each first on its own with room around it, the rooster hopping
it first to show the way and mangoes tracing the jump. Practise (to 300 m): the same things in pairs and rhythms.
Test (to 500 m): the rooster's mischief, trios, the last cart, then the lane opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 14 | Yard | the basket 0.7; the neighbour -2.4; 6 mangoes | The neighbour naps on his cot; hens peck about; hold to lift the basket. |
| 14 | 32 | FirstPot | pot stack 23; 8 mangoes | One pot stack alone: the rooster hops it, mangoes trace the jump. |
| 32 | 50 | TwoPots | pot stack 38; pot stack 45; 10 mangoes | Two pot stacks 7 m apart: jump, land, jump. |
| 50 | 66 | Dung | cow dung 57; 9 mangoes | Cow dung: low, a tap clears it; miss it and she slips. |
| 66 | 86 | SleepingDog | sleeping dog 74; feather 1 at 74.1, 2.8 m up; 8 mangoes | The sleeping dog: long, so hold the jump. A feather above for a double jump. |
| 86 | 102 | Breather | chilli 95; 8 mangoes | Room to breathe: a wave of mangoes and the first chilli. |
| 102 | 122 | HandPump | hand-pump puddle 114; 5 mangoes | The hand-pump puddle: wide and low, only a held jump clears it. |
| 122 | 142 | Cart | bullock cart 127; feather 2 at 131.2, 3.4 m up; 7 mangoes | The bullock cart: jump onto its bed, run off the end. A feather for a double jump. |
| 142 | 164 | PotsDungPots | pot stack 148; cow dung 154.5; pot stack 161; 15 mangoes | Pots, dung, pots: 6.5 m apart, the first rhythm. |
| 164 | 184 | DogPots | sleeping dog 170.5; pot stack 177.5; 10 mangoes | The dog, then a pot stack. |
| 184 | 198 | Lane | 8 mangoes | A short run of mangoes. |
| 198 | 220 | PotTrio | pot stack 204; pot stack 210.5; feather 3 at 210.6, 2.8 m up; pot stack 217; 15 mangoes | Three pot stacks in rhythm; a feather at the top of a double jump over the middle. |
| 220 | 240 | PuddleDog | hand-pump puddle 226.5; sleeping dog 234.5; 10 mangoes | The puddle, then the dog. |
| 240 | 262 | CartPots | bullock cart 244; pot stack 253; 12 mangoes | The cart as a step: off its bed straight into a jump over pots. |
| 262 | 280 | ChilliStraight | chilli 263.5; 10 mangoes | A long straight and a chilli to win back ground. |
| 280 | 298 | DungPair | cow dung 286; cow dung 292; 10 mangoes | Two cow pats: tap, tap. |
| 298 | 320 | Mischief | hand-pump puddle 303.5; pot stack 313 (knocked in by the rooster); mischief 314; 10 mangoes | The puddle; then the rooster knocks a pot stack off its stand into the lane. |
| 320 | 340 | DogDung | sleeping dog 326.5; cow dung 333.5; 10 mangoes | The dog and the dung. |
| 340 | 360 | ChilliLane | chilli 341.5; 9 mangoes | A breather and a chilli. |
| 360 | 386 | PotQuartet | pot stack 364; pot stack 370.5; pot stack 377; pot stack 383.5; 20 mangoes | Four pot stacks, 6.5 m apart. |
| 386 | 408 | LastCart | bullock cart 390; pot stack 399; 12 mangoes | The last cart, and pots after it. |
| 408 | 432 | DogDungPots | sleeping dog 413.5; cow dung 420.5; pot stack 427; 15 mangoes | Dog, dung, pots. |
| 432 | 450 | FinalChilli | chilli 433.5; 9 mangoes | The last chilli. |
| 450 | 472 | PuddlePots | hand-pump puddle 456; pot stack 463.5; pot stack 470; 15 mangoes | The puddle and two pots: the last test. |
| 472 | 506 | OpenLane | 12 mangoes | The lane opens out: if he is still ahead, he gets away at 500 m. |

## The audit

* a clean run from a 10 m start catches him after about 18 s, at about 110 m (without chillies)
* a clean run from a 14 m start catches him after about 26 s, at about 158 m (without chillies)
* first of each: pots 23 m, dung 57 m, dog 74 m, puddle 113 m, cart 127 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
pots          22.8 m (FirstPot): held window 321 ms, tap 108 ms
pots          37.8 m (TwoPots): held window 321 ms, tap 108 ms
pots          44.8 m (TwoPots): held window 321 ms, tap 108 ms
dung          56.7 m (Dung): held window 412 ms, tap 233 ms
dog           73.5 m (SleepingDog): held window 312 ms, tap 125 ms
puddle       113.2 m (HandPump): held window 246 ms, tap 71 ms
cart         127.0 m (Cart): jump onto the bed and run off the end
pots         147.8 m (PotsDungPots): held window 321 ms, tap 108 ms
dung         154.2 m (PotsDungPots): held window 412 ms, tap 233 ms
pots         160.8 m (PotsDungPots): held window 321 ms, tap 108 ms
dog          170.1 m (DogPots): held window 313 ms, tap 125 ms
pots         177.3 m (DogPots): held window 321 ms, tap 108 ms
pots         203.8 m (PotTrio): held window 321 ms, tap 108 ms
pots         210.3 m (PotTrio): held window 321 ms, tap 108 ms
pots         216.8 m (PotTrio): held window 321 ms, tap 108 ms
puddle       225.7 m (PuddleDog): held window 246 ms, tap 71 ms
dog          234.1 m (PuddleDog): held window 313 ms, tap 125 ms
cart         244.0 m (CartPots): jump onto the bed and run off the end
pots         252.8 m (CartPots): held window 321 ms, tap 108 ms
dung         285.7 m (DungPair): held window 413 ms, tap 233 ms
dung         291.7 m (DungPair): held window 413 ms, tap 233 ms
puddle       302.7 m (Mischief): held window 246 ms, tap 71 ms
pots         312.8 m (Mischief): held window 321 ms, tap 108 ms
dog          326.1 m (DogDung): held window 313 ms, tap 125 ms
dung         333.2 m (DogDung): held window 413 ms, tap 233 ms
pots         363.8 m (PotQuartet): held window 321 ms, tap 108 ms
pots         370.3 m (PotQuartet): held window 321 ms, tap 108 ms
pots         376.8 m (PotQuartet): held window 321 ms, tap 108 ms
pots         383.3 m (PotQuartet): held window 321 ms, tap 108 ms
cart         390.0 m (LastCart): jump onto the bed and run off the end
pots         398.8 m (LastCart): held window 321 ms, tap 108 ms
dog          413.1 m (DogDungPots): held window 313 ms, tap 125 ms
dung         420.2 m (DogDungPots): held window 413 ms, tap 233 ms
pots         426.8 m (DogDungPots): held window 321 ms, tap 108 ms
puddle       455.2 m (PuddlePots): held window 246 ms, tap 71 ms
pots         463.3 m (PuddlePots): held window 321 ms, tap 108 ms
pots         469.8 m (PuddlePots): held window 321 ms, tap 108 ms
```

Problems: none.
