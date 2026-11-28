# Level 1: Pots and the sleeping dog

The beat sheet for level 1 (zone 1). It is written by `ArtSource/tools/levels/level1.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level1.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 1: the kid runs at 3.5 m/s, the rooster at 3.2 m/s; a held jump is 2.16 m long and 1.4 m high; the course is 290 m.

## The opening: the neighbour's yard

The neighbour naps on his rope cot behind the lane, just past the basket; his hens peck about. The kid tiptoes in
from -4.4 m to the bamboo basket the rooster is sitting under (a tap hurries her). The player holds to lift it by its near rim; it turns
up on its far rim over 1.6 s of holding. Letting go part way drops it back with a clunk, and the neighbour stirs.
Fully up, the rooster bursts out and sprints off, the kid flings the basket aside, and the neighbour wakes shouting.

* A lift with no drop gives the rooster a **6 m** head start; any drop gives him **8 m**.
* A retry skips the opening and keeps the head start it earned; loading the level again plays it again.
* The rules are `Core/BasketLift.cs` (tested in `BasketLiftTests`); the flow is `GameFlow`'s Intro state; the
  basket, its hinge and the neighbour's two cut-outs are `BasketIntro`.

## The shape of it

Everything runs at a small child's real pace (3.5 m/s, as Kick Off's kid) and everything in the road is what lies
in a village street: the potter's pots drying, a dog asleep in the dust, cow dung, the hand pump's puddle, hens and
a goat kid crossing, sacks of paddy waiting for the cart, a heap of sand where a house is going up.

Teach (to about 90 m): one new thing at a time, each first on its own with room around it, the rooster hopping
it first to show the way and mangoes tracing the jump. Practise (to 177 m): the same things in pairs and rhythms,
about 4 m (a second and a bit) apart. Test (to 290 m): the rooster's mischief, the potter's four stacks, the last
sacks, then the lane opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 10 | Yard | the basket 0.55; the neighbour 2.6; 4 mangoes | The neighbour naps on his cot; hens peck about; hold to lift the basket. |
| 10 | 20 | FirstPot | pot stack 15.5; 8 mangoes | The potter's pots drying by the road: one stack alone, the rooster hops it. |
| 20 | 30 | TwoPots | pot stack 23; pot stack 27; 10 mangoes | Two pot stacks 4 m apart: jump, land, jump. |
| 30 | 39 | Dung | cow dung 34; 8 mangoes | Cow dung: low, a tap clears it; miss it and she slips. |
| 39 | 50 | SleepingDog | sleeping dog 44; feather 1 at 44.1, 2.8 m up; 8 mangoes | The dog asleep in the dust: long, so hold the jump. A feather above it. |
| 50 | 59 | Breather | chilli 50.6; 7 mangoes | Room to breathe: a wave of mangoes and the first chilli. |
| 59 | 69 | HandPump | hand-pump puddle 64.5; 5 mangoes | The puddle round the hand pump: wide and low, hold the jump. |
| 69 | 78 | GoatKid | 1 goat kid 73.5; 5 mangoes | A goat kid wandering across the street: jump it. |
| 78 | 89 | Sacks | sacks of paddy 82; feather 2 at 82.9, 3.2 m up; 2 mangoes | Sacks of paddy waiting for the cart: hop onto them, run off the end. A feather. |
| 89 | 102 | PotsDungPots | pot stack 92; cow dung 96; pot stack 100; 15 mangoes | Pots, dung, pots: the first rhythm. |
| 102 | 113 | DogHens | sleeping dog 105; 2 hens 109.5; 10 mangoes | The dog, then two hens pecking in the road. |
| 113 | 120 | Lane | 6 mangoes | A short run of mangoes. |
| 120 | 134 | PotTrio | pot stack 123; pot stack 127; feather 3 at 127.1, 2.8 m up; pot stack 131; 15 mangoes | Three pot stacks in rhythm; a feather at the top of a double jump over the middle. |
| 134 | 145 | PuddleDog | hand-pump puddle 137.5; sleeping dog 141.8; 10 mangoes | The puddle, then the dog. |
| 145 | 157 | SandHeap | heap of building sand 148.5; sacks of paddy 152.5; 7 mangoes | A house being built: a heap of sand at the road's edge, then the sacks. |
| 157 | 167 | ChilliStraight | chilli 157.8; 7 mangoes | A long straight and a chilli to win back ground. |
| 167 | 177 | DungPair | cow dung 170; cow dung 174; 10 mangoes | Two cow pats: tap, tap. |
| 177 | 190 | Mischief | hand-pump puddle 180; pot stack 186 (knocked in by the rooster); mischief 186.6; 10 mangoes | The puddle; then the rooster knocks a pot stack off its stand into the lane. |
| 190 | 201 | DogDung | sleeping dog 193.5; cow dung 197.5; 10 mangoes | The dog and the dung. |
| 201 | 211 | ChilliLane | chilli 201.8; 6 mangoes | A breather and a chilli. |
| 211 | 229 | PotQuartet | pot stack 214; pot stack 218; pot stack 222; pot stack 226; 20 mangoes | Four of the potter's stacks, 4 m apart. |
| 229 | 242 | GoatSacks | 1 goat kid 232.5; sacks of paddy 236.5; 7 mangoes | A goat kid, then the last sacks. |
| 242 | 256 | DogDungPots | sleeping dog 245; cow dung 249; pot stack 253; 15 mangoes | Dog, dung, pots. |
| 256 | 266 | FinalChilli | chilli 256.8; 6 mangoes | The last chilli. |
| 266 | 279 | PuddlePots | hand-pump puddle 269.5; pot stack 273.8; pot stack 277.8; 15 mangoes | The puddle and two pots: the last test. |
| 279 | 300 | OpenLane | 10 mangoes | The lane opens out: if he is still ahead, he gets away at 290 m. |

## The audit

* a clean run from a 6 m start catches him after about 17 s, at about 61 m (without chillies)
* a clean run from a 8 m start catches him after about 24 s, at about 84 m (without chillies)
* first of each: pots 15 m, dung 34 m, dog 44 m, puddle 64 m, goats 73 m, sacks 82 m, hens 109 m, sand 148 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
pots          15.3 m (FirstPot): held window 226 ms, tap 13 ms
pots          22.8 m (TwoPots): held window 226 ms, tap 13 ms
pots          26.8 m (TwoPots): held window 226 ms, tap 13 ms
dung          33.7 m (Dung): held window 305 ms, tap 126 ms
dog           43.6 m (SleepingDog): held window 207 ms, tap 19 ms
puddle        64.0 m (HandPump): held window 214 ms, tap 39 ms
goats         73.3 m (GoatKid): held window 270 ms, tap 74 ms
sacks         82.0 m (Sacks): hop onto the sacks and run off the end
pots          91.8 m (PotsDungPots): held window 226 ms, tap 13 ms
dung          95.7 m (PotsDungPots): held window 305 ms, tap 126 ms
pots          99.8 m (PotsDungPots): held window 226 ms, tap 13 ms
dog          104.6 m (DogHens): held window 207 ms, tap 19 ms
hens         109.2 m (DogHens): held window 213 ms, tap 21 ms
pots         122.8 m (PotTrio): held window 226 ms, tap 13 ms
pots         126.8 m (PotTrio): held window 226 ms, tap 13 ms
pots         130.8 m (PotTrio): held window 226 ms, tap 13 ms
puddle       137.1 m (PuddleDog): held window 214 ms, tap 39 ms
dog          141.4 m (PuddleDog): held window 207 ms, tap 19 ms
sand         148.2 m (SandHeap): held window 213 ms, tap 21 ms
sacks        152.5 m (SandHeap): hop onto the sacks and run off the end
dung         169.7 m (DungPair): held window 305 ms, tap 126 ms
dung         173.7 m (DungPair): held window 305 ms, tap 126 ms
puddle       179.6 m (Mischief): held window 214 ms, tap 39 ms
pots         185.8 m (Mischief): held window 226 ms, tap 13 ms
dog          193.1 m (DogDung): held window 207 ms, tap 19 ms
dung         197.2 m (DogDung): held window 305 ms, tap 126 ms
pots         213.8 m (PotQuartet): held window 226 ms, tap 13 ms
pots         217.8 m (PotQuartet): held window 226 ms, tap 13 ms
pots         221.8 m (PotQuartet): held window 226 ms, tap 13 ms
pots         225.8 m (PotQuartet): held window 226 ms, tap 13 ms
goats        232.3 m (GoatSacks): held window 270 ms, tap 74 ms
sacks        236.5 m (GoatSacks): hop onto the sacks and run off the end
dog          244.6 m (DogDungPots): held window 207 ms, tap 19 ms
dung         248.7 m (DogDungPots): held window 305 ms, tap 126 ms
pots         252.8 m (DogDungPots): held window 226 ms, tap 13 ms
puddle       269.1 m (PuddlePots): held window 214 ms, tap 39 ms
pots         273.6 m (PuddlePots): held window 226 ms, tap 13 ms
pots         277.6 m (PuddlePots): held window 226 ms, tap 13 ms
```

Problems: none.
