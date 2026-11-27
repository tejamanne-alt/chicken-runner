# Chicken Runner — Game Design Document

Nov 22, 2026 · @Teja Manne

## Overview

Chicken Runner is a side-scrolling chase game: a hungry village kid lifts a neighbour's chicken basket, the rooster bolts, and the player runs, jumps and climbs through an Indian village to catch it.

| Item | Decision |
| --- | --- |
| Genre | Chase runner: auto-run, level-based story mode, endless mode after launch |
| Platforms | Android and iOS, landscape |
| Engine | Unity 6.3 LTS, 2.5D (3D characters on a side-on path) |
| Session length | 30 to 90 seconds per level |
| Audience | Casual players in India first; anyone who grew up around a village |
| Kid character | Models supplied by Teja; this doc specifies what the game needs from them |

Design pillars:

1. **You chase something.** The rooster stays on screen and the gap to it is the whole game. Most runners have you flee; this one has a target.
2. **A village you recognise.** Every obstacle is a real object from an Indian village lane, field or terrace.
3. **Comedy over punishment.** A mistake costs distance, never a death screen.
4. **One thumb.** Tap, hold, swipe.

## Story and tone

The story is the familiar village tale told in six beats, and the player takes part in every one of them.

1. **The craving.** The kid smells chicken curry from a neighbour's kitchen and wants it at home. Ten-second opening, no dialogue needed.
2. **The plan.** Roosters sit under upturned bamboo baskets in the neighbour's yard. The kid tiptoes in while the neighbour naps on a cot.
3. **The basket.** The player holds to lift the basket slowly. This is playable: a smooth lift gives a short head start to the rooster, a clumsy one gives a long head start.
4. **The escape.** The rooster bursts out, the neighbour wakes and shouts, the chase begins.
5. **The chase.** Lanes, fields, canals and rooftops. The rooster wriggles free at the end of each level and flees to the next place.
6. **Amma's kitchen.** The final grab sticks. The kid carries the rooster home and hands it to Amma.

Tone: slapstick, warm, never mean. The kid is determined, the rooster is smug, the village carries on around them. All humour comes from animation and sound, so the game needs almost no text and works in any language.

## Core loop

The kid runs automatically; the player's job is to lose no speed, so the gap to the rooster closes until the kid can dive and grab it.

&#91;embedded content: level flow · 6 steps, 2 loops\]

Losing the rooster costs only a retry, and the story moves on each time the kid gets a hand on him.

- **The gap is the score.** A bar at the top shows kid, rooster and the distance between them in metres. Clean running closes it; every mistake opens it.
- **Mistakes cost distance.** Hitting a pot stack, slipping on dung, wading a canal or climbing a wall the slow way each lose 2 to 3 metres. Nothing kills the kid.
- **Skill routes save distance.** A double jump onto a roof, a slide under a clothesline or a hop across a haystack keeps full speed.
- **Chilli boost.** Red chillies give a 2-second sprint, the main way to recover from a mistake.
- **The grab.** Inside 0.8 m the kid dives automatically. In levels 1 to 8 the rooster wriggles free in a short gag and the level is won. In the last level the catch sticks.
- **Losing.** The rooster escapes if the gap passes 25 m or the course ends before the grab. The player retries the level; there are no lives.
- **Stars.** One for the grab, one for mangoes collected, one for a run without a stumble.

## Controls

Everything works with one thumb anywhere on the screen; there are no on-screen buttons.

| Action | Touch | Keyboard (editor testing) |
| --- | --- | --- |
| Jump | Tap; hold for a higher jump | Space or Up |
| Double jump | Tap again in the air | Space or Up again |
| Slide or duck | Swipe down; in the air it becomes a fast drop | Down or S |
| Climb a ladder or tree | Swipe up when beside one | Up or W |
| Vault a wall | Automatic on contact, costs about 0.45 s | Automatic |
| Lift the basket (intro) | Press and hold | Hold Space |
| Grab the rooster | Automatic dive inside 0.8 m | Automatic |

Input forgiveness: 0.1 s jump buffer and 0.08 s coyote time, so a tap slightly early or late still counts.

## The kid

The kid is a small, stubborn, fast toddler, matching the reference art: big head, short legs, sports kit, leopard-print hairband. The game needs the model below; everything else is built around it.

### What the game needs from the kid model

| Item | Requirement |
| --- | --- |
| Format | FBX, 1 unit = 1 m, about 1.05 m tall, facing +Z, T-pose or A-pose |
| Rig | Unity Humanoid-compatible skeleton, at most 4 bone weights per vertex |
| Budget | Up to 15k triangles, 1 or 2 materials, one 1024 or 2048 px texture atlas |
| Face | 4 expressions as blend shapes or texture swaps: neutral, grin, shocked, straining |
| Socket | A right-hand attach bone, for carrying the rooster |
| Shading | Plain albedo texture, no baked lighting or outline; the toon shader and outline are applied in Unity |

### Animation list

| Priority | Clips |
| --- | --- |
| Needed for the first prototype | Idle, run, jump, fall, land, slide, wall vault, stumble, dive-grab |
| Needed for the story | Tiptoe, basket lift (scrubbed by the hold input), startled, wade, dung slip, ladder climb, get up after a miss, carry rooster, cheer, sulk |
| Nice to have | Double-jump tuck, look-back while running, out-of-breath idle |

If the models are 2D instead (sprite sheets or layered art), the same list applies as side-view animations, and the stack swaps the toon shader for Unity's 2D Animation package. Collision is a capsule 0.35 m wide and 1.05 m tall; sliding halves the height.

## The rooster

The rooster is the star: a country rooster with red comb, orange neck and black tail, as in the reference photo, and he must be funny within the first ten seconds.

| Behaviour | What the player sees | Why it is there |
| --- | --- | --- |
| Run | Runs about 8% slower than the kid's clean pace | Good play always closes the gap |
| Flutter | Flaps over canals and up onto roofs ahead of the kid | Shows the player the route to take |
| Panic burst | Sprints and sheds feathers when the kid gets within 2 m | Makes the last metres tense |
| Taunt | Stops, turns and crows when more than 18 m ahead | Rubber band: gives a struggling player a chance |
| Mischief | Knocks over pot stacks, startles hens, wakes the dog | Creates fresh obstacles in the kid's path |
| Fake-out | Hides in a row of baskets or a flock of hens for a moment | A change of pace once per level |
| Wriggle free | Slips out of the dive at the end of levels 1 to 8 | Carries the story to the next place |

The rooster follows a route authored per level chunk, with speed driven by the gap, so his path is predictable and his timing is not.

## World

The chase crosses three zones, each with three levels, and each zone teaches one of the kid's skills.

| Zone | Setting | Skill it teaches |
| --- | --- | --- |
| 1. The lane | Painted flat-roofed houses, verandas, kolam at doorsteps, hand pump, cots, cycles | Jump and slide |
| 2. Fields and canal | Paddy fields, bund paths, irrigation canal, haystacks, mango and palm trees, a well | Long jumps and tree climbing |
| 3. Terraces and market day | Rooftops with water tanks and drying chillies, then the weekly market and temple steps | Rooftop routes and vaulting |

### Obstacles and climbables

| Object | Zones | If you hit it | Clean way past |
| --- | --- | --- | --- |
| Clay pot stack | 1, 3 | Pots smash, stumble | Jump |
| Cow dung | 1, 2 | Slip and skid | Jump |
| Sleeping street dog | 1 | Dog barks, stumble | Jump |
| Hand pump and puddle | 1 | Stumble | Jump |
| Clothesline of sarees | 1, 3 | Tangled, stumble | Slide |
| Rope cot | 1 | Nothing: it is a trampoline | Land on it for a high bounce |
| Flat-roofed house | 1, 3 | Slow wall vault | Double jump, or ladder |
| Bamboo ladder | 1, 3 | None | Swipe up to reach the roof |
| Bullock cart | 1, 2 | Slow vault | Jump onto the bed, use it as a step |
| Haystack | 2 | Slow vault | Hop over the top |
| Irrigation canal | 2 | Wade across slowly | Jump, or take the plank bridge |
| Buffalo in a mud patch | 2 | Blocked, slow climb | Bounce off its back |
| Mango tree | 2 | None | Climb to the branch route for mangoes |
| Market stall awning | 3 | None | Bounce across awnings |
| Water tank and parapet | 3 | Stumble | Jump |

### Pickups

- **Mangoes:** the currency; lines of them mark the best route.
- **Red chillies:** 2-second sprint.
- **Tail feathers:** three hidden per level, on the harder routes; they unlock outfits.

## Levels and tuning

Story mode is nine levels; each is a course of hand-built chunks 12 to 20 m long, and a clean run ends it in about 30 seconds while a messy one takes up to 90.

| Level | Zone | New element |
| --- | --- | --- |
| 1 | Lane | Jump: pots, dung, dog |
| 2 | Lane | Slide: clotheslines; rope-cot bounce |
| 3 | Lane | Houses, ladders, first rooftop stretch |
| 4 | Fields | Canals and plank bridges |
| 5 | Fields | Mango trees and branch routes |
| 6 | Fields | Buffalo, haystack chains, rooster mischief |
| 7 | Terraces | Long rooftop runs, gaps between houses |
| 8 | Market | Awnings, crowds of hens, the basket fake-out |
| 9 | Temple steps | Everything, longest course, the catch that sticks |

Starting values, all to be tuned in the grey-box prototype:

| Parameter | Zone 1 | Zone 2 | Zone 3 |
| --- | --- | --- | --- |
| Kid run speed (m/s) | 6.0 | 7.0 | 8.0 |
| Rooster run speed (m/s) | 5.5 | 6.4 | 7.4 |
| Course length (m) | 500 | 600 | 700 |

| Parameter | Value |
| --- | --- |
| Starting gap | 10 m after a smooth basket lift, 14 m after a clumsy one; 12 m in levels that skip the basket |
| Single jump | 1.4 m high, about 3.7 m long at zone 1 speed |
| Double jump | 2.6 m total height |
| House roof height | 2.2 to 2.6 m, so a roof needs a double jump, a ladder or a vault |
| Canal widths | 2.5, 3.5 and 4.5 m; the widest needs a double jump |
| Stumble | 0.7 s at 45% speed, about 2.5 m lost |
| Chilli boost | +35% speed for 2.2 s, about 5 m gained |
| Taunt and escape | Rooster slows beyond 18 m; level lost beyond 25 m |

An endless mode, built from the same chunks with rising speed and a distance score, follows after launch.

## Art direction

The world takes its look from the kid's reference art: clean dark outlines, flat saturated colour, soft two-tone shading.

**The village is celebrating Pongal**, the Tamil harvest festival, in every level: the chase runs through a village in
festive mood. Mango-leaf thoranams hang over every door, marigold garlands on doors, pillars, stalls and shrines,
coloured Pongal kolams (rice flour filled with red, yellow, green and pink) before every house, tall sugarcane stalks
leaning by the doors, new clay Pongal pots boiling over on brick hearths with turmeric plants tied round their necks,
cattle dressed for Mattu Pongal (painted horns, brass bells, garlands), bunting across the lanes and over the terraces,
kites in the sky, and everyone in new clothes. The fields are at harvest; the market sells sugarcane, turmeric plants,
new pots and sweets; the temple has its Pongal pot and lamps. The neighbour's chicken curry is for the festival feast.
Every painting gets a Pongal edit (prompt sheet section P) that keeps it as it is and adds the festival, and the
hand-built models gain the decorations as real parts.

- **Rendering:** toon shading with an outline pass on characters and props, so the supplied kid model and the world read as one drawing.
- **Palette:** terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-wash house walls, paddy green, late-afternoon golden light.
- **Camera:** side-on with a slight perspective, kid on the left third. It pulls back as the gap grows so the rooster stays in frame up to about 14 m; beyond that an edge arrow shows the distance.
- **Depth:** three parallax layers behind the play lane: hills and a temple tower, then fields and palms, then huts and trees.
- **Readability rule:** anything that hurts has a dark outline and a warm colour; anything helpful (mangoes, chillies, ladders, cots) glints.
- **UI:** hand-painted signboard style, chunky rounded type. The Baloo 2 family is a good fit: it has a matching font for each of nine Indian scripts if text is localised later.

Village detail list for the art pass: bamboo chicken baskets, thatched and flat-roofed houses, doorstep kolam, tulsi planter, brass pots, cots, bullock cart, hand pump, hanging sarees, haystacks, scarecrow with a painted pot head, palm and mango trees, canal sluice, black water tanks, chillies and papad drying on terraces, market stalls with marigold garlands, festival bunting, kites; and for Pongal: thoranams, coloured kolams, sugarcane, Pongal pots on brick hearths and cattle with painted horns.

## Audio

Music is folk percussion that speeds up as the gap closes, so the player hears how close the catch is.

- **Music:** a hand-drum loop per zone with a flute or reed motif; two extra layers fade in under 5 m and under 2 m.
- **Rooster:** crow at the escape, squawk on panic, a smug cluck on the taunt.
- **Kid:** footsteps by surface (dust, mud, terrace, water), effort grunts, giggle on a chilli boost.
- **World:** pots smashing, dog bark, canal splash, cot springs, temple bell and bicycle bell in the background.
- **Voices:** the neighbour's shout at the escape and Amma calling at the end, recorded in the chosen regional language.
- **Haptics:** light tap on landings, strong pulse on a stumble and on the grab.

## Screens and flow

A new player reaches the first chase in under 20 seconds: title, a wordless story strip, the basket, then running.

| Screen | Contents |
| --- | --- |
| Title | Logo, the kid peeking at a basket, Play, settings |
| Village map | A footpath through the three zones with nine stops, stars per stop, outfits button |
| Basket intro | Level 1 only: hold to lift. Later levels open on the rooster already running |
| Chase HUD | Gap bar with metres, mango count, feather pips, pause. Nothing else |
| Level won | The wriggle-free gag, stars, mangoes earned, Next |
| Rooster escaped | The rooster crowing from a rooftop, Retry, Map |
| Outfits | Kid costumes bought with mangoes and feathers |
| Settings | Music, sound, haptics, language |

## Tech stack

The game is built in Unity 6.3 LTS with the Universal Render Pipeline, C# and Unity's own packages wherever one exists.

| Layer | Choice | Notes |
| --- | --- | --- |
| Engine | [Unity 6.3 LTS](https://unity.com/releases/unity-6/support) | The current long-term release, supported until December 2027; support for 6.0 LTS ended in October 2026 |
| Licence | [Unity Personal](https://unity.com/products/unity-personal) | Free while revenue and funding in the last 12 months stay under 200,000 USD |
| Language and backend | C#, IL2CPP, ARM64 | Needed for both stores |
| Rendering | Universal Render Pipeline, forward renderer | One directional light, blob shadows on low-end phones |
| Toon look | [Unity Toon Shader](https://docs.unity3d.com/Packages/com.unity.toonshader@0.13/manual/index.html) | Cel shading and outlines; still a preview package, so the fallback is a small Shader Graph toon shader with an inverted-hull outline |
| Characters | Humanoid rig, Animator Controller, Timeline | Animator for gameplay states; Timeline for the basket intro and the wriggle-free gags |
| Camera | Cinemachine | Follow camera that frames kid and rooster together and pulls back with the gap |
| Input | Input System package | Tap, hold and swipe on touch; keyboard in the editor |
| Movement | Custom kinematic controller with raycasts | No rigidbody physics, so jumps feel identical on every device |
| Levels | Chunk prefabs, ScriptableObject level definitions, object pooling | Designers reorder chunks without touching code |
| UI | uGUI with TextMesh Pro, [Baloo 2 fonts](https://github.com/EkType/Baloo2) | Open Font License |
| Audio | Unity Audio Mixer | Layered music stems driven by the gap |
| Effects | Built-in Particle System | Dust, feathers, splashes, pot shards |
| Save data | JSON file in the persistent data path | Stars, mangoes, outfits; cloud save later |
| Ads | [Unity LevelPlay mediation with the AdMob adapter](https://docs.unity.com/grow/levelplay/sdk/unity/networks/guides/google-admob) | Rewarded and interstitial; added in the last milestone |
| Analytics and crashes | Firebase Analytics and Crashlytics | Level funnel, fail points, crash reports |
| Version control | Git with Git LFS | Unity Version Control is the alternative |
| Android build | App bundle, [target API level 36](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en) | Google Play requires API 36 for new apps and updates since 31 August 2026 |
| iOS build | Xcode project from Unity, TestFlight | Built on a Mac |

## Project architecture

Three scenes (Boot, Menu, Chase) and one Chase scene for every level: a level is data, a list of chunks plus tuning values.

| System | Responsibility |
| --- | --- |
| GameFlow | State machine for a level: intro, chase, grab, result |
| ChaseDirector | Tracks the gap, decides win and loss, drives music intensity and camera framing |
| KidController | Kinematic motor plus states: run, air, slide, vault, climb, wade, stumble, dive |
| RoosterBrain | Follows the route authored in each chunk; speed and behaviours depend on the gap |
| LevelStreamer | Spawns chunks ahead of the rooster, recycles them behind the kid through a pool |
| Chunk prefab | Ground and platform colliders, obstacle and pickup markers, rooster waypoints |
| Obstacle | One component driven by an ObstacleDefinition asset: penalty type, effect, sound |
| Economy and SaveService | Mangoes, feathers, stars, outfits, saved as JSON |
| HUD | Reads ChaseDirector; holds no game logic |
| AudioDirector | Music layers, surface footsteps, voice barks |
| Ads and Analytics | Behind interfaces with empty stand-ins, so the game runs without any SDK installed |

All numbers from the tuning tables live in one TuningConfig asset per zone, editable in the Inspector while the game is running.

## Progression and monetisation

The game is free; progress comes from stars and outfits, and ads are opt-in rewards first.

- **Stars** open the next zone: 5 of 9 stars for the fields, 12 of 18 for the terraces.
- **Mangoes and feathers** buy outfits for the kid: school uniform, festival clothes, raincoat, cricket whites. Outfits are cosmetic only.
- **Rewarded ads:** a second chance once per level (the rooster stops to taunt and the gap resets to 12 m), and double mangoes on the result screen.
- **Interstitial ads:** at most one after every third level result, never between a loss and a retry.
- **One purchase:** remove interstitials and get a golden-rooster outfit.

The ad plan depends on the audience decision in the risks section; it changes if the game is declared as made for children.

## Scope and milestones

The first shippable version is one zone and three levels; the plan below is sized in weekend sessions and each milestone has a gate that must pass before the next starts.

1. **Grey-box chase, 1 weekend.** Capsule kid, capsule rooster, gap bar, jump and slide, six chunks. Gate: the chase is fun with no art at all.
2. **Kid in the game, 2 weekends.** Supplied model, animation states, vault, ladder, canal wade, basket intro. Gate: the run, jump and dive feel right at 6 m/s.
3. **Zone 1 complete, 2 weekends.** Lane art set, rooster model and behaviours, HUD, audio pass, levels 1 to 3. Gate: five outside players finish level 1 without help.
4. **Store-ready slice, 1 to 2 weekends.** Save data, results, ads behind a flag, analytics, Android internal test and TestFlight builds. Gate: no crash in 50 sessions.
5. **Zones 2 and 3, 3 to 4 weekends.** Fields, terraces, market, levels 4 to 9, outfits, final catch scene. Gate: level funnel data shows where players stop.
6. **After launch.** Endless mode, more outfits, regional voice packs.

Out of scope for version 1: multiplayer, a level editor, daily challenges, leaderboards.

## Risks

The biggest risk is that without a funny, readable rooster this is one more endless-runner clone; the rest are about cost and store rules.

| Risk | Why it matters | What to do |
| --- | --- | --- |
| The rooster is not entertaining | The chase target is the only thing that separates this from every other runner | Build his behaviours in milestone 1, before any art |
| Climbing fights the auto-run | Stopping to climb kills the feeling of speed | No climb longer than 0.5 s; every wall has a full-speed route |
| Art volume | About 60 props and three backgrounds is the largest cost for a solo developer | Ship zone 1 first; build houses from a modular kit; reuse props across zones |
| Kid animation quality | A toddler's proportions retarget poorly from stock humanoid clips | Test the supplied model with the nine prototype clips before making the rest |
| Audience and ads | A toddler hero and cartoon art read as a children's game, and both stores apply stricter ad and data rules to those | Decide the declared audience before adding ads; LevelPlay can pass AdMob's child-directed flag if needed |
| The premise | A child taking a neighbour's rooster for the pot is funny to people who know the tale; some parents, reviewers and advertisers will read it as theft and animal harm | Keep the catch slapstick, show nothing after the handover, and decide the ending below |
| One joke over nine levels | Repetition by the second zone | Each zone adds a rooster trick; cut to six levels if playtests show fatigue |
| Preview toon shader | Unity Toon Shader may change between versions | Keep the Shader Graph fallback ready |

## Open decisions

These seven choices change the build, so they are worth settling before milestone 2.

- [ ] Kid models: rigged 3D, which this doc assumes, or 2D sprites?
- [ ] Rooster model: made in the same pipeline as the kid, or sourced separately?
- [ ] The kid's name, and whether the sports kit stays as the default outfit.
- [ ] Region: which language for the neighbour's shout, Amma's call and the signboards?
- [ ] Ending: Amma cooks the rooster as in the tale, or a twist where she marches the kid back to return it?
- [ ] Declared audience: general or children. This sets the ad plan.
- [ ] The neighbour: only a voice, or a second chaser behind the kid?

## Sources

- [Unity 6 release support](https://unity.com/releases/unity-6/support): LTS versions and support dates
- [Unity Personal](https://unity.com/products/unity-personal): eligibility limit
- [Unity Toon Shader manual](https://docs.unity3d.com/Packages/com.unity.toonshader@0.13/manual/index.html): pipelines supported, preview status
- [LevelPlay: Google AdMob integration](https://docs.unity.com/grow/levelplay/sdk/unity/networks/guides/google-admob): ad formats and child-directed setting
- [Google Play target API level requirements](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en): API 36 from 31 August 2026
- [Baloo 2 on GitHub](https://github.com/EkType/Baloo2): scripts covered and licence
