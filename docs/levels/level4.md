# Level 4: The canal

The beat sheet for level 4 (zone 2). It is written by `ArtSource/tools/levels/level4.py --report` from
the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level4.json`), so it cannot drift from
it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths
and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.

Zone 2: the kid runs at 3.5 m/s, the rooster at 3.15 m/s; a held jump is 2.16 m long and 1.4 m high; the course is 295 m.

## The opening: the bund

No basket here: the chase starts on the bund between the paddies with the rooster 7 m ahead (the level's Ready
screen; tap to chase). The kid runs at a small child's real pace, 3.5 m/s, and closes on him at 0.35 m a second:
a clean run catches him at about 62 m, some 18 s in. A level still takes about a minute and a half.

## The canal

Irrigation channels cut across the bund road at the widths they really are:

* **1.2 m:** a held jump clears it (340 ms to take off); a tap lands in the water.
* **1.8 m:** a full held jump only just clears it (168 ms), so where it is first met it has the plank bridge: run
  across. Near the end one has no plank: a full jump, or a double jump to be sure (570 ms).
* **2.6 m:** only a double jump clears it (340 ms); the mangoes trace the double jump's line.
* **In the water:** never a fail. She wades at 45% speed (3.2 m lost on the widest) and steps out of the 0.28 m bed.

## What is on the road

Only what lies on a bund road between the paddies: the canals, ducks waddling up from them (at most two), cow dung,
small straw heaps at the roadside (hop onto or over), sacks of paddy waiting for the cart (a 0.8 m platform to hop
onto), and the water pots by the well, which the rooster knocks into the road. No carts stand across it any more.
Things to jump are about 4 m (a second and a bit) apart, and each chilli has 11 m or more of clear road after it.

## The shape of it

Teach (to 75 m): one new thing at a time. Practise (to 162 m): canals in rhythm with dung, ducks and haystacks, the
plank then a jump, off the sacks over a canal, three canals in a row. Test (to 295 m): the rooster's mischief by
the well, every combination, all three widths in a row, a 1.8 m canal without its plank, then the bund opens out.

## The course

| From | To | Section | What is there | Why |
|---:|---:|---|---|---|
| -10 | 8 | Bund | 4 mangoes | The bund road between the paddies: the rooster struts ahead; tap to chase. |
| 8 | 17 | FirstCanal | 1.2 m canal 12; 8 mangoes | The first canal, 1.2 m: a held jump clears it; the rooster flutters across first. |
| 17 | 27 | Plank | 1.8 m canal 21 with the plank; 4 mangoes | A 1.8 m canal, too wide for a sure jump: the plank bridge is the way across. |
| 27 | 35 | Ducks | 2 ducks 31; 5 mangoes | Two ducks waddling up from the canal across the bund: jump them. |
| 35 | 45 | Haystack | small haystack 38.5; 6 mangoes | A small haystack at the roadside: hop onto it (mangoes along its top) or over it. |
| 45 | 56 | WideCanal | 2.6 m canal 48.5; feather 1 at 49.9, 3.1 m up; 7 mangoes | The widest canal, 2.6 m: double jump (the mangoes show where), or wade. |
| 56 | 64 | Breather | chilli 56.5; 8 mangoes | Room to breathe: a wave of mangoes and the first chilli. |
| 64 | 75 | Sacks | sacks of paddy 68; feather 2 at 68.9, 3.4 m up; cow dung 72.5; 7 mangoes | Sacks of paddy waiting for the cart: hop onto them; a feather above for a double jump. Then dung. |
| 75 | 85 | CanalDung | 1.2 m canal 77; cow dung 82; 10 mangoes | A canal, then dung: jump, land, tap. |
| 85 | 98 | Haystacks | small haystack 86.5; small haystack 90.5; small haystack 94.5; feather 3 at 95.1, 3.3 m up; 9 mangoes | Three small haystacks: hop, hop, hop; a feather above the last. |
| 98 | 109 | PlankThenJump | 1.8 m canal 100 with the plank; 1.2 m canal 104.5; 9 mangoes | The plank, then a canal with no plank: walk, then jump. |
| 109 | 118 | ChilliStraight | chilli 109.5; 8 mangoes | A long straight and a chilli to win back ground. |
| 118 | 129 | SacksCanal | sacks of paddy 121; 1.2 m canal 125; 7 mangoes | Onto the sacks and off their end straight over a canal. |
| 129 | 139 | WideAgain | 2.6 m canal 131.5; 7 mangoes | The wide canal again: double jump. |
| 139 | 148 | DucksHaystack | 2 ducks 141.5; small haystack 145; 8 mangoes | Ducks crossing, then a small haystack. |
| 148 | 162 | CanalTrio | 1.2 m canal 150; 1.2 m canal 154.25; 1.2 m canal 158.5; 15 mangoes | Three 1.2 m canals in a rhythm: jump, jump, jump. |
| 162 | 175 | Mischief | cow dung 164; pot stack 168.5 (knocked in by the rooster); mischief 169; 1.2 m canal 171.8; 15 mangoes | Dung; then the rooster knocks the water pots by the well into the road; a canal after. |
| 175 | 185 | PlankHaystack | 1.8 m canal 176.5 with the plank; small haystack 181.5; 7 mangoes | The plank, then a haystack. |
| 185 | 194 | ChilliRun | chilli 185.5; 8 mangoes | A chilli and a run of mangoes. |
| 194 | 209 | CanalSacksCanal | 1.2 m canal 197; sacks of paddy 201.5; 1.2 m canal 205.5; 12 mangoes | Canal, sacks, canal. |
| 209 | 220 | WideHaystack | 2.6 m canal 210.5; small haystack 216.5; 10 mangoes | The wide canal, then a haystack straight after it. |
| 220 | 229 | DungDucks | cow dung 221.5; 2 ducks 226; 10 mangoes | Dung, then ducks: tap, jump. |
| 229 | 238 | FinalChilli | chilli 229.5; 8 mangoes | The last chilli. |
| 238 | 254 | ThreeWidths | 1.2 m canal 241; 1.8 m canal 245 with the plank; 2.6 m canal 249.5; 16 mangoes | All three canals in a row: jump the 1.2 m, walk the plank over the 1.8 m, double jump the 2.6 m. |
| 254 | 266 | HaystackDung | small haystack 255.5; cow dung 260.5; small haystack 264; 11 mangoes | Two haystacks and dung between them. |
| 266 | 276 | Sugarcane | 1.8 m canal 268.5; 2 ducks 273.5; 10 mangoes | Past the sugarcane: a 1.8 m canal with no plank (a full jump, or a double), then ducks. |
| 276 | 288 | LastWide | 2.6 m canal 278; small haystack 284; 10 mangoes | The last wide canal, and a haystack after it. |
| 288 | 305 | OpenBund | 10 mangoes | The bund opens out: if he is still ahead, he gets away at 295 m. |

## The audit

* a clean run from a 7 m start catches him after about 18 s, at about 62 m (without chillies)
* first of each: canal 12 m, bridge 21 m, ducks 31 m, haystack 39 m, sacks 68 m, dung 72 m, pots 168 m

How each challenge is cleared, and the take-off windows (how long the player has to start the move):

```
canal         12.0 m (FirstCanal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
bridge        21.0 m (Plank): a 1.8 m canal with the plank: run across (a held jump clears it)
ducks         30.7 m (Ducks): held window 224 ms, tap 32 ms
haystack      38.6 m (Haystack): small: hop onto it or over it
canal         48.5 m (WideCanal): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
sacks         68.0 m (Sacks): hop onto the sacks and run off the end
dung          72.2 m (Sacks): held window 305 ms, tap 126 ms
canal         77.0 m (CanalDung): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
dung          81.7 m (CanalDung): held window 305 ms, tap 126 ms
haystack      86.6 m (Haystacks): small: hop onto it or over it
haystack      90.6 m (Haystacks): small: hop onto it or over it
haystack      94.6 m (Haystacks): small: hop onto it or over it
bridge       100.0 m (PlankThenJump): a 1.8 m canal with the plank: run across (a held jump clears it)
canal        104.5 m (PlankThenJump): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
sacks        121.0 m (SacksCanal): hop onto the sacks and run off the end
canal        125.0 m (SacksCanal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
canal        131.5 m (WideAgain): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
ducks        141.2 m (DucksHaystack): held window 224 ms, tap 32 ms
haystack     145.1 m (DucksHaystack): small: hop onto it or over it
canal        150.0 m (CanalTrio): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
canal        154.2 m (CanalTrio): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
canal        158.5 m (CanalTrio): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
dung         163.7 m (Mischief): held window 305 ms, tap 126 ms
pots         168.3 m (Mischief): held window 226 ms, tap 13 ms
canal        171.8 m (Mischief): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
bridge       176.5 m (PlankHaystack): a 1.8 m canal with the plank: run across (a held jump clears it)
haystack     181.6 m (PlankHaystack): small: hop onto it or over it
canal        197.0 m (CanalSacksCanal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
sacks        201.5 m (CanalSacksCanal): hop onto the sacks and run off the end
canal        205.5 m (CanalSacksCanal): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
canal        210.5 m (WideHaystack): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
haystack     216.6 m (WideHaystack): small: hop onto it or over it
dung         221.2 m (DungDucks): held window 305 ms, tap 126 ms
ducks        225.7 m (DungDucks): held window 224 ms, tap 32 ms
canal        241.0 m (ThreeWidths): 1.2 m: held jump 340 ms, double jump 740 ms; wading loses 1.5 m
bridge       245.0 m (ThreeWidths): a 1.8 m canal with the plank: run across (a held jump clears it)
canal        249.5 m (ThreeWidths): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
haystack     255.6 m (HaystackDung): small: hop onto it or over it
dung         260.2 m (HaystackDung): held window 305 ms, tap 126 ms
haystack     264.1 m (HaystackDung): small: hop onto it or over it
canal        268.5 m (Sugarcane): 1.8 m: held jump 168 ms, double jump 568 ms; wading loses 2.2 m
ducks        273.2 m (Sugarcane): held window 224 ms, tap 32 ms
canal        278.0 m (LastWide): 2.6 m: needs a double jump, double jump 340 ms; wading loses 3.2 m
haystack     284.1 m (LastWide): small: hop onto it or over it
```

Problems: none.
