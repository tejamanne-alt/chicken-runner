"""Chicken Runner art prompt sheet: the single source for the web page and docs/art/prompt-sheet.md."""

STYLE = (
    "Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. "
    "Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted "
    "toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, "
    "light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and "
    "lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, "
    "numbers, logos, signatures, borders or watermarks."
)

TEXTURE = (
    "Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat "
    "lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and "
    "simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, "
    "kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks."
)

ANCHOR = "Use the attached A1 key art as the style reference and match it closely."

SECTIONS = [
    ("A", "Style anchors", "Make these first, in order. A0 fixes the kid's design in the pattu frock, A1 sets the look, and every later prompt matches both."),
    ("B", "Characters", "Model sheets and pose sheets. Attach your kid reference art and rooster photo where noted."),
    ("C", "Zone 1: the lane", "Levels 1 to 3. Painted houses, verandas, kolam, pots, cots and clotheslines."),
    ("D", "Zone 2: fields and canal", "Levels 4 to 6. Paddy fields, bunds, the canal, haystacks and mango trees."),
    ("E", "Zone 3: terraces and market", "Levels 7 to 9. Rooftops at sunset, the market at dusk and the lamp-lit temple steps."),
    ("F", "Story frames and screens", "The opening story, the wriggle-free gag, the loss screen and Amma's kitchen."),
    ("T", "Textures", "Seamless hand-painted textures for Blender materials. These use the texture rules instead of the scene style."),
]

L, S = "Landscape 3:2", "Square 1:1"
KID = "your kid reference art"
KIDREFS = "your four kid turnaround images"
ROOSTER = "your rooster reference photo"

PROMPTS = [
    # ------------------------------------------------------------------ A
    dict(id="A0", title="Kid in a pattu frock", file="A0_kid_pattu_frock_sheet.png", aspect=L, batch=1, attach=KIDREFS,
         use="The kid's design for every later image, and the sheet I model and rig the kid from in Blender.",
         prompt="Character model sheet for 3D modelling of the game's toddler hero, based on the four attached reference "
                "images (front, back and both side views). Keep the face, skin tone, shoulder-length wavy black hair, "
                "leopard-print hairband and chubby toddler proportions exactly as in the references, but change the outfit: "
                "replace the T-shirt, shorts, socks and sneakers with a vintage South Indian pattu frock, like one from a 1980s "
                "family photo. It is a knee-length silk frock in peacock blue with a wide contrasting border at the hem in "
                "magenta and gold zari, woven with a small temple-tower pattern; a fitted bodice with a gold zari neckline; "
                "short puffed sleeves edged in gold; and a gently gathered, flared skirt with a soft silk sheen. Bare feet with "
                "silver anklets with tiny bells. Show four views side by side at exactly the same scale and height: front, left "
                "side, right side and back, standing in a relaxed A-pose with the arms a little away from the body. "
                "Orthographic, no perspective. Even, flat lighting with no cast shadows. Plain flat light-grey background. "
                "No labels."),
    dict(id="A1", title="Key art", file="A1_key_art.png", aspect=L, batch=1, attach=f"A0, {ROOSTER}",
         use="Sets the look every other image matches, and my reference for materials and lighting in Blender.",
         prompt="Key art for the game. Side-on view of a narrow South Indian village lane in late-afternoon golden light. "
                "A small, determined toddler (drawn exactly like the attached A0 model sheet: wavy black hair, a "
                "leopard-print hairband, a peacock-blue silk pattu frock with a magenta-and-gold border swishing as they "
                "run, bare feet with silver anklets) sprints from left to right after a smug country rooster (red comb, orange neck "
                "feathers, glossy black tail, like the attached rooster photo) who glances back over his shoulder mid-stride. "
                "Around them: flat-roofed houses washed in lime-white, indigo and turmeric, white kolam patterns at the "
                "doorsteps, a stack of clay pots, a hand pump with a puddle, a rope cot where a sleepy neighbour is just "
                "waking up, a tulsi planter, coconut palms and a distant temple tower in warm haze. Dust kicked up by little "
                "feet, a few loose feathers in the air, long soft shadows. The kid is on the left third, the rooster on the right."),
    dict(id="A2", title="Colour script", file="A2_colour_script.png", aspect=L, batch=1, attach="A1",
         use="The lighting plan across the nine levels: one Blender lighting setup per zone.",
         prompt="A colour script for the whole game: nine small painted panels in a 3 by 3 grid, read left to right and top "
                "to bottom, all side-on views of one chase through a South Indian village as the day goes by. Panels 1 to 3: "
                "a village lane in warm late afternoon. Panels 4 to 6: paddy fields, an irrigation canal and mango trees at "
                "golden hour, the light turning orange. Panel 7: flat rooftops with drying red chillies at sunset. Panel 8: a "
                "weekly market at dusk with marigold garlands and glowing lanterns. Panel 9: temple steps at blue dusk lit by "
                "rows of small oil lamps. Simple shapes, all about light and colour, with tiny silhouettes of a toddler in a swishing "
                "blue silk frock chasing a rooster in every panel."),

    # ------------------------------------------------------------------ B
    dict(id="B1", title="Rooster model sheet", file="B1_rooster_model_sheet.png", aspect=L, batch=1, attach=f"A1, {ROOSTER}",
         use="Traced in Blender to model the rooster at the right proportions.",
         prompt="Character model sheet of the game's rooster for 3D modelling, based on the attached rooster photo: a proud "
                "country rooster with a big red comb and wattles, orange-gold neck feathers, a rust-red body, dark wings, a "
                "glossy black curved tail and yellow legs. Four views side by side at exactly the same scale and height: left "
                "side view, front view, back view and top view, standing in a neutral pose. Orthographic, no perspective. Even, "
                "flat lighting with no cast shadows. Plain flat light-grey background. No labels."),
    dict(id="B2", title="Rooster pose sheet", file="B2_rooster_poses.png", aspect=L, batch=1, attach="A1, B1",
         use="Key poses for the rooster's run, flutter, taunt, panic and wriggle animations.",
         prompt="Pose sheet for the same rooster as the attached model sheet, all in side view facing right, evenly spaced at "
                "the same scale on a plain flat light-grey background: 1) running with one leg forward; 2) running with the "
                "other leg forward; 3) fluttering up with wings spread and feet tucked; 4) the smug taunt, turned back to face "
                "left, chest puffed out, head thrown back, crowing; 5) panic sprint, eyes wide, feathers flying off; 6) "
                "wriggling free upside down, flapping wildly; 7) pecking at the ground; 8) standing proud on one foot. Funny, "
                "expressive body language: slapstick, never hurt."),
    dict(id="B3", title="Kid gameplay poses", file="B3_kid_poses_gameplay.png", aspect=L, batch=1, attach="A1, A0",
         use="Key poses for the nine first-prototype animations on your kid model.",
         prompt="Pose sheet for the toddler hero, keeping the design exactly as in the attached A0 model sheet (wavy black "
                "hair, leopard-print hairband, peacock-blue pattu frock with a magenta-and-gold border, bare feet with silver anklets). All side view facing right, same scale, plain flat light-grey "
                "background: 1) running, contact pose; 2) running, passing pose; 3) jumping up with arms raised; 4) falling "
                "with arms flailing; 5) landing in a squat; 6) sliding feet first on their back; 7) vaulting a low wall with "
                "both hands on top; 8) stumbling forward, off balance; 9) diving flat out with arms stretched to grab. Let the frock's skirt flare and trail with each motion."),
    dict(id="B4", title="Kid story poses and faces", file="B4_kid_story_and_faces.png", aspect=L, batch=1, attach="A1, A0",
         use="The four face expressions and the story-animation poses.",
         prompt="Second pose sheet for the same toddler, exactly as in the attached A0 model sheet, barefoot with silver anklets. Top row, four face "
                "close-ups: neutral, big cheeky grin, shocked with mouth open, straining with cheeks puffed. Bottom row, full "
                "body side views facing right: tiptoeing with exaggerated sneaky steps; lifting a big bamboo basket with both "
                "hands, straining; a startled jump; carrying a rooster proudly in both arms; cheering with fists up; sulking "
                "with arms crossed. Plain flat light-grey background, even lighting."),
    dict(id="B5", title="Neighbour", file="B5_neighbour_sheet.png", aspect=L, batch=1, attach="A1",
         use="Modelled for the basket intro: asleep on the cot, then waking with a shout.",
         prompt="Character sheet for the sleepy neighbour: a friendly middle-aged village man with a bushy moustache, a white "
                "cotton vest and a checked lungi, a little round in the middle. Left: front view and side view standing, same "
                "scale, for 3D modelling. Right: napping on a rope cot with one arm over his face, then waking up mid-shout "
                "with one arm raised, pointing. Comic and warm, never mean. Plain flat light-grey background, even lighting."),
    dict(id="B6", title="Amma", file="B6_amma_sheet.png", aspect=L, batch=2, attach="A1",
         use="Modelled for the final kitchen scene.",
         prompt="Character sheet for Amma, the toddler's mother: a warm, kind woman in her thirties wearing a cotton saree in "
                "turmeric and indigo, hair in a bun with jasmine flowers, glass bangles. Left: front view and side view "
                "standing, same scale, for 3D modelling. Right: three expressions, surprised with a hand on her cheek, "
                "laughing, and a stern raised eyebrow with hands on hips. Dignified and loving. Plain flat light-grey "
                "background, even lighting."),
    dict(id="B7", title="Village animals", file="B7_animals_sheet.png", aspect=L, batch=2, attach="A1",
         use="The sleeping dog, hens, buffalo and bullocks that become obstacles and scenery.",
         prompt="Sheet of village animals in side view facing right, at the same scale relative to each other, on a plain "
                "flat light-grey background: a street dog asleep curled in the dust; the same dog woken up and barking; three "
                "hens pecking; a water buffalo lying in a mud patch; a pair of white bullocks standing. Friendly cartoon "
                "proportions."),

    # ------------------------------------------------------------------ C
    dict(id="C1", title="Lane mood painting", file="C1_lane_mood.png", aspect=L, batch=1, attach="A1",
         use="The target for the zone 1 Blender scene: layout, lighting and atmosphere.",
         prompt="Environment painting of the village lane, side-on like a side-scrolling game level, no characters. A packed "
                "red-earth lane runs left to right. Flat-roofed houses in lime-white, indigo, turmeric and pale pink with "
                "verandas and pillars, wooden doors with mango-leaf garlands, white kolam patterns at each doorstep. Stacked "
                "clay pots, a hand pump with a puddle, a rope cot, a bicycle leaning on a wall, a tulsi planter, a clothesline "
                "of bright sarees and bamboo ladders up to the rooftops. Behind: coconut palms, then a distant temple tower and "
                "hills fading into warm haze. Late afternoon: long shadows across the lane, light shafts through the palms, "
                "dust in the air."),
    dict(id="C2", title="Lane far layer", file="C2_lane_far_layer.png", aspect=L, batch=1, attach="A1",
         use="A painted card at the back of the scene, scrolling slowest.",
         prompt="Far background layer for parallax scrolling, with no foreground and no ground: a late-afternoon sky with soft "
                "painterly clouds, low hills and a distant South Indian temple tower in silhouette, a few faraway coconut "
                "palms, all fading into warm golden haze toward the bottom. Wide and calm, so it can repeat sideways."),
    dict(id="C3", title="Lane middle layer", file="C3_lane_mid_layer.png", aspect=L, batch=1, attach="A1",
         use="A cut-out card between the far layer and the play lane. Magenta is keyed out.",
         prompt="Middle parallax layer, side-on: a row of coconut palms, banana plants and the backs of distant village "
                "houses with tiled and flat roofs, a little hazy and lower in contrast than a foreground would be. Isolated on "
                "a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground."),
    dict(id="C4", title="House kit elevations", file="C4_house_kit_elevations.png", aspect=L, batch=1, attach="A1",
         use="Traced to build the modular house kit: walls, verandas, parapets, doors and ladder.",
         prompt="Modular building kit for 3D modelling: four flat-roofed South Indian village house fronts seen straight on "
                "(front elevation, orthographic, no perspective), standing side by side on one baseline. One narrow, in "
                "lime-white. One wide, in indigo, with a shaded veranda and two pillars. One in turmeric with a small barred "
                "window and a raised sit-out platform by the door. One pale pink with steps up to the door. Each has a low "
                "parapet along the roof edge, a wooden door and a painted band at the base. A bamboo ladder leans on one wall. "
                "Even flat lighting, plain flat light-grey background, no labels."),
    dict(id="C5", title="Lane props, sheet 1", file="C5_lane_props_a.png", aspect=L, batch=1, attach="A1",
         use="Modelled as the zone 1 obstacles and set dressing.",
         prompt="Prop sheet for 3D modelling, every object in side view at the same scale, evenly spaced on a plain flat "
                "light-grey background, even lighting: a stack of three clay pots; a flat cow-dung patty; an iron hand pump "
                "with a small puddle; a wooden rope cot with a woven top; an old black bicycle; a tulsi planter on a small "
                "painted pedestal; a pair of brass water pots. Hazards (pots, dung, puddle) in warm colours with dark "
                "outlines; the helpful cot has a slight glint."),
    dict(id="C6", title="Lane props, sheet 2", file="C6_lane_props_b.png", aspect=L, batch=1, attach="A1",
         use="The bullock cart, clothesline and the bamboo basket from the intro.",
         prompt="Second prop sheet, side view, same scale, plain flat light-grey background, even lighting: a bullock cart "
                "with big wooden wheels; a clothesline on two bamboo poles with two bright sarees hanging; an upturned "
                "dome-shaped bamboo chicken basket; a pile of jute sacks; a wooden doorway with a mango-leaf garland across "
                "the top; a small roadside shrine stone with a marigold garland; a clay water pot on a stand."),
    dict(id="C7", title="Kolam decals", file="C7_kolam_decals.png", aspect=S, batch=1, attach="A1",
         use="Cut out as decals for doorsteps and the lane.",
         prompt="Six different kolam floor designs seen straight from above, drawn in clean white rice-flour lines with a few "
                "accents in turmeric, kumkum red and green, arranged in a 3 by 2 grid with space between them, on a solid flat "
                "dark-grey background so they can be cut out. Simple, bold, hand-drawn lines."),

    # ------------------------------------------------------------------ D
    dict(id="D1", title="Fields mood painting", file="D1_fields_mood.png", aspect=L, batch=2, attach="A1",
         use="The target for the zone 2 Blender scene.",
         prompt="Environment painting, side-on like a side-scrolling game level, no characters: emerald paddy fields with "
                "mirror-like water between the rows, a raised earthen bund path running left to right, an irrigation canal "
                "crossed by a narrow plank bridge, conical haystacks, a big mango tree with low climbable branches, tall palms, "
                "a stone well with a pulley, a scarecrow with a painted clay-pot head and white egrets in the water. Golden "
                "hour: the light turning orange, long reflections in the water, soft mist over the far fields."),
    dict(id="D2", title="Fields far layer", file="D2_fields_far_layer.png", aspect=L, batch=2, attach="A1",
         use="The back card for zone 2.",
         prompt="Far parallax layer with no foreground and no ground: a golden-hour sky with glowing clouds, distant blue "
                "hills, lines of palm trees across faraway fields and a flock of birds, all fading into warm haze at the "
                "bottom. Calm, so it can repeat sideways."),
    dict(id="D3", title="Fields props", file="D3_fields_props.png", aspect=L, batch=2, attach="A1",
         use="Modelled as the zone 2 obstacles: haystack, canal and plank bridge, well.",
         prompt="Prop sheet for 3D modelling, side view, same scale, plain flat light-grey background, even lighting: a conical "
                "haystack; a short stretch of irrigation canal with a narrow wooden plank bridge; a round stone well with a "
                "wooden pulley and rope; a scarecrow with a painted clay-pot head and an old shirt; a small canal sluice gate; "
                "a section of earthen bund path with grass along its edges."),
    dict(id="D4", title="Mango tree", file="D4_mango_tree.png", aspect=L, batch=2, attach="A1",
         use="Modelled with the branch route the kid climbs for mangoes.",
         prompt="Model sheet of a big old mango tree for a platform game: side view on the left, front view on the right, same "
                "scale. A thick twisted trunk, two strong low branches that form a walkable route, dense dark-green leaves and "
                "ripe mangoes that glint. Orthographic, even flat lighting, plain flat light-grey background."),

    # ------------------------------------------------------------------ E
    dict(id="E1", title="Rooftops mood painting", file="E1_rooftops_mood.png", aspect=L, batch=2, attach="A1",
         use="The target for levels 7 and the rooftop stretches.",
         prompt="Environment painting, side-on like a side-scrolling game level, no characters: a run of connected flat "
                "village rooftops at sunset with small gaps between the houses, low parapets, black cylindrical water tanks, "
                "red chillies and round papads drying on woven mats, a clothesline, a bamboo ladder, paper kites in the sky "
                "and festival bunting strung between houses. The setting sun rims everything in orange and the sky shifts from "
                "gold to rose."),
    dict(id="E2", title="Market mood painting", file="E2_market_mood.png", aspect=L, batch=2, attach="A1",
         use="The target for level 8, the market day.",
         prompt="Environment painting, side-on like a side-scrolling game level: a weekly village market at dusk, a row of "
                "stalls with striped cloth awnings at different heights, heaps of vegetables, brass and steel vessels, flower "
                "sellers with marigold and jasmine garlands, hens in woven baskets, hanging lanterns starting to glow and a "
                "busy crowd as soft silhouettes in the background."),
    dict(id="E3", title="Temple steps", file="E3_temple_steps_mood.png", aspect=L, batch=2, attach="A1",
         use="The target for level 9, the final catch.",
         prompt="Environment painting for the final level, side-on: wide stone temple steps rising from left to right toward a "
                "tall carved temple tower, rows of small clay oil lamps flickering along every step, brass bells, marigold "
                "garlands and festival bunting, a big old banyan tree to one side. Blue dusk turning to night, warm lamp light "
                "pooling on the stone, a few stars. Magical and calm."),
    dict(id="E4", title="Rooftop props", file="E4_rooftop_props.png", aspect=L, batch=2, attach="A1",
         use="Modelled as the zone 3 rooftop obstacles and dressing.",
         prompt="Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a black cylindrical "
                "plastic water tank on a low stand; a section of rooftop parapet wall with a gap; a woven mat of red chillies "
                "drying; a woven mat of round papads; a paper kite with a tail; a string of triangular festival bunting."),
    dict(id="E5", title="Market and temple props", file="E5_market_props.png", aspect=L, batch=2, attach="A1",
         use="Modelled as the bouncy awnings, stalls and lamp-lit steps.",
         prompt="Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a market stall with a "
                "striped cloth awning in two versions, one high and one low; a flower stall with marigold garlands; a woven "
                "basket of vegetables; a stack of brass vessels; a woven basket with two hens; a hanging lantern; a stone "
                "temple step segment with three clay oil lamps."),

    # ------------------------------------------------------------------ F
    dict(id="F1", title="Title screen", file="F1_title_screen.png", aspect=L, batch=2, attach="A1, A0",
         use="Staged in Blender as the title screen, with room for the logo.",
         prompt="Title screen illustration with empty space at the top centre for a logo: the toddler hero (as in the attached "
                "A0 model sheet, in the peacock-blue pattu frock) peeks mischievously from behind a low wall at an upturned bamboo basket in a neighbour's yard, "
                "and a rooster's beady eye looks back through the gaps in the weave. Late afternoon, warm light, kolam on the "
                "ground. The toddler is barefoot, with silver anklets."),
    dict(id="F2", title="Story 1: the craving", file="F2_story_craving.png", aspect=L, batch=1, attach="A1, A0",
         use="Storyboard for the opening shot of the intro cutscene.",
         prompt="Story frame, The craving: the toddler sits on the doorstep of home, nose in the air and eyes closed in bliss, "
                "as a ribbon of curry aroma, drawn as swirling golden steam with tiny spice specks, drifts over the wall from "
                "the neighbour's kitchen window. Warm afternoon. Wordless storytelling. The toddler is barefoot, with silver anklets."),
    dict(id="F3", title="Story 2: the plan", file="F3_story_plan.png", aspect=L, batch=1, attach="A1, A0, B5",
         use="Storyboard and layout for the yard where the basket intro is played.",
         prompt="Story frame, The plan: the neighbour's yard seen side-on, three upturned bamboo baskets with roosters under "
                "them, the neighbour snoring on a rope cot under a tree, and the toddler tiptoeing in on bare feet with exaggerated "
                "sneaky steps, tongue out in concentration, wincing as the bells on their silver anklets jingle. Dappled afternoon light."),
    dict(id="F4", title="Story 3: the basket", file="F4_story_basket.png", aspect=L, batch=1, attach="A1, A0",
         use="Storyboard for the hold-to-lift moment.",
         prompt="Story frame, The basket: a close side view of the toddler slowly lifting a big bamboo basket with both hands, "
                "straining; under the rim, the rooster's head and one suspicious eye peek out. Tense and funny, with soft light "
                "falling through the basket weave. The toddler is barefoot, with silver anklets."),
    dict(id="F5", title="Story 4: the escape", file="F5_story_escape.png", aspect=L, batch=1, attach="A1, A0, B5",
         use="Storyboard for the moment the chase begins.",
         prompt="Story frame, The escape: the rooster bursts out from under the basket in an explosion of feathers, wings "
                "wide, while the toddler falls back in surprise and the neighbour sits bolt upright on his cot, shouting and "
                "pointing. Dust, feathers and slapstick energy. The toddler is barefoot, with silver anklets."),
    dict(id="F6", title="Wriggle-free gag", file="F6_story_wriggle_free.png", aspect=L, batch=2, attach="A1, A0",
         use="Storyboard for the gag at the end of levels 1 to 8.",
         prompt="Gag frame: the toddler dives flat out and lands belly-down in the dust with hands closed on nothing, while "
                "the rooster pops out of their grip and flutters away overhead looking smug, a single feather floating down "
                "onto the toddler's head. The toddler is barefoot, with silver anklets."),
    dict(id="F7", title="Rooster escaped", file="F7_rooster_escaped.png", aspect=L, batch=2, attach="A1",
         use="Staged in Blender as the loss screen.",
         prompt="Loss screen illustration: the rooster stands on a rooftop parapet against a sunset sky, chest out, crowing in "
                "triumph; far below, a tiny toddler looks up with hands on hips. The toddler is barefoot, with silver anklets."),
    dict(id="F8", title="Story 6: Amma's kitchen", file="F8_story_amma_kitchen.png", aspect=L, batch=2, attach="A1, A0, B6",
         use="Storyboard for the final scene. It stops at the handover, as the design doc's risk table asks.",
         prompt="Final story frame, Amma's kitchen: a warm, lamp-lit village kitchen with a clay stove, brass and steel "
                "vessels on shelves and strings of dried chillies. The toddler proudly holds up the rooster in both arms to "
                "Amma, who looks down with surprise and a smile. Golden evening light through a small window. The toddler is barefoot, with silver anklets. Nothing shown "
                "beyond this moment."),

    # ------------------------------------------------------------------ T
    dict(id="T1", title="Red-earth lane", file="T1_tex_earth_lane.png", aspect=S, batch=1, attach="A1", block="texture",
         use="The lane material for zone 1.",
         prompt="A top-down texture of a packed red-earth village lane: terracotta soil with small pebbles, faint footprints "
                "and bicycle tracks, a few dry leaves."),
    dict(id="T2", title="Lime-washed wall", file="T2_tex_limewash_wall.png", aspect=S, batch=1, attach="A1", block="texture",
         use="The base wall material for the house kit.",
         prompt="A front-on texture of a lime-washed village wall: soft white with a faint blue tint, uneven brush strokes, "
                "small chips showing terracotta plaster underneath, slightly dirtier toward the bottom."),
    dict(id="T3", title="Coloured walls", file="T3_tex_coloured_walls.png", aspect=S, batch=1, attach="A1", block="texture",
         use="Wall variants for the house kit. I split the four squares and make each one tile.",
         prompt="Four separate wall textures in a 2 by 2 grid, each square front-on with soft uneven brush strokes: an "
                "indigo-washed wall, a turmeric-yellow wall, a pale pink wall and a weathered sea-green wall."),
    dict(id="T4", title="Wood, rope and bamboo", file="T4_tex_wood_weave.png", aspect=S, batch=1, attach="A1", block="texture",
         use="Doors, the cot, the basket and the sacks.",
         prompt="Four separate textures in a 2 by 2 grid, each square seen straight on: weathered wooden planks, the woven rope "
                "top of a cot, a bamboo basket weave and coarse jute sacking."),
    dict(id="T5", title="Roofs, floors and stone", file="T5_tex_roof_floor_stone.png", aspect=S, batch=2, attach="A1", block="texture",
         use="Thatch, roof tiles, the courtyard floor and the temple steps.",
         prompt="Four separate textures in a 2 by 2 grid, each square seen straight on: palm-leaf thatch, terracotta roof tiles, "
                "a smooth cow-dung-plastered courtyard floor in olive brown, and worn granite temple stone."),
    dict(id="T6", title="Paddy and canal water", file="T6_tex_water.png", aspect=S, batch=2, attach="A1", block="texture",
         use="The paddy and canal surfaces for zone 2.",
         prompt="Two textures side by side, each filling half the square, seen straight down: shallow paddy-field water with "
                "rows of young green rice shoots and a golden sky reflected in it; and muddy-green canal water with soft "
                "ripples and a few floating leaves."),
    dict(id="T7", title="Saree and awning fabrics", file="T7_tex_fabrics.png", aspect=S, batch=2, attach="A1", block="texture",
         use="Sarees on the clotheslines and the market awnings.",
         prompt="Four separate fabric patterns in a 2 by 2 grid, each square flat and seen straight on: kumkum red with a gold "
                "border stripe; indigo block print with small white motifs; turmeric and green checks; red-and-white market "
                "awning stripes."),
]

PIPELINE = [
    ("Model", "Props, buildings, the rooster, the side characters and (unless you have a model) the kid are modelled in Blender over the model sheets, at the "
              "game's scale (1 unit = 1 m), with the side view getting the most care because the camera is side-on."),
    ("Paint", "The textures become hand-painted materials. Characters and props get a toon shader with an outline, so they "
              "match the Unity toon look; backgrounds stay painterly."),
    ("Layer", "The far and middle layers become painted cards behind the 3D lane, which gives each zone its parallax depth."),
    ("Light", "Each zone gets the time of day from the colour script, with haze, light shafts and dust."),
    ("Animate", "The rooster's run, flutter, taunt, panic and wriggle come from his pose sheet. The kid's clips go on the kid's "
                "rig, and the story frames become the intro and ending cutscenes."),
    ("Export", "Models and animations go to Unity as FBX (Humanoid-ready for the kid), and the cutscenes render as video "
               "or Timeline animation."),
]

NEEDS = [
    "The rooster reference photo from the design doc. (Your four kid images are in ArtSource/supplied.)",
    "Your kid model files (FBX or .blend, with the rig) if you have them in the pattu frock. Otherwise I'll model the kid from A0.",
    "The images from this sheet, saved with the file names shown. Upload them here in batches.",
    "A yes or no on South India. The prompts use kolam, a gopuram-style temple tower and Amma; tell me if you want another region.",
]

# ---------------------------------------------------------------------- Gemini versions
# Gemini's image model works best with full sentences, positive phrasing (say what the image holds, not what it
# lacks), an explicit job for every uploaded image, and camera language. It also makes 16:9 and 21:9 images,
# which suit a side-scroller better than 3:2. Same IDs and file names as the ChatGPT versions.

GEMINI_STYLE = (
    "Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, "
    "like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone "
    "cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light "
    "shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and "
    "lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image "
    "is clean artwork only: unlabeled, unsigned and borderless."
)

GEMINI_TEXTURE = (
    "Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit "
    "evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush "
    "strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum "
    "red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else."
)

GEMINI_CAMERA = ("Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in "
                 "a side-scrolling game.")

WIDE, SIXTEEN, SQUARE = "21:9 ultra-wide", "16:9 landscape", "1:1 square"
GEMINI_SHAPES = {i: SIXTEEN for i in [p["id"] for p in PROMPTS]}
GEMINI_SHAPES.update({i: WIDE for i in ["C1", "C2", "C3", "D1", "D2", "E1", "E2", "E3"]})
GEMINI_SHAPES.update({i: SQUARE for i in ["C7", "T1", "T2", "T3", "T4", "T5", "T6", "T7"]})

# Scenes that should read as a flat, side-on game level.
GEMINI_SIDE_ON = {"A1", "C1", "C2", "C3", "D1", "D2", "E1", "E2", "E3"}

# What each uploaded image is for, so Gemini uses it the right way.
GEMINI_ROLES = {
    "A1": "the A1 key art, as the style to match closely (painting style, outlines, palette and light)",
    "B1": "the B1 rooster model sheet, to keep the rooster's design identical",
    "B5": "the B5 neighbour sheet, to keep the neighbour's design identical",
    "B6": "the B6 Amma sheet, to keep Amma's design identical",
    KID: "my kid reference art, to keep the toddler's face, proportions and outfit identical",
    KIDREFS: ("my four kid turnaround images, for the toddler's face, skin tone, hair, hairband and proportions "
              "(change only the outfit, as described)"),
    "A0": "the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical",
    ROOSTER: "my rooster photo, to match his colours and markings",
}

# Negatives rewritten as positive descriptions, which Gemini follows more reliably.
GEMINI_EDITS = {
    "A0": [("Orthographic, no perspective. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels.",
            "Draw them perfectly flat and orthographic, like an animation model sheet, lit evenly from the front so nothing "
            "casts a shadow, on a plain light-grey background. The sheet holds only the four drawings, unlabeled.")],
    "B1": [("Orthographic, no perspective. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels.",
            "Draw them perfectly flat and orthographic, like an animation model sheet, lit evenly from the front so nothing "
            "casts a shadow, on a plain light-grey background. The sheet holds only the four drawings, unlabeled.")],
    "C1": [("side-on like a side-scrolling game level, no characters.",
            "side-on like a side-scrolling game level. The lane is empty for a moment, waiting for the chase.")],
    "C2": [("Far background layer for parallax scrolling, with no foreground and no ground:",
            "Far background layer for parallax scrolling, made only of sky and distance:")],
    "C3": [("Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.",
            "Everything else in the image is solid flat magenta (#FF00FF), so the trees and houses can be cut out cleanly.")],
    "C4": [("(front elevation, orthographic, no perspective)",
            "(front elevations, perfectly flat and orthographic, like an architect's drawing)"),
           ("Even flat lighting, plain flat light-grey background, no labels.",
            "Even flat lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.")],
    "D1": [("side-on like a side-scrolling game level, no characters:",
            "side-on like a side-scrolling game level, a quiet, empty landscape:")],
    "D2": [("Far parallax layer with no foreground and no ground:",
            "Far parallax layer made only of sky and distance:")],
    "E1": [("side-on like a side-scrolling game level, no characters:",
            "side-on like a side-scrolling game level, the rooftops empty for a moment:")],
    "F8": [("Nothing shown beyond this moment.",
            "The image captures only this moment of the handover.")],
}

GEMINI_HOWTO = [
    "Make <b>A0</b> first, in a new Gemini chat, uploading your four kid images. Then make <b>A1</b>, uploading A0 "
    "and your rooster photo.",
    "Stay in that chat. Each copied prompt says what every uploaded image is for. Upload the files under <i>Attach</i> "
    "with each prompt, A0 and A1 included: re-uploading them keeps the kid and the style closest.",
    "If the shape comes out wrong, reply: <i>Make this same image in a 21:9 ultra-wide shape</i> (or the shape shown).",
    "Save each image with its file name, then put them in the repo at <code>ArtSource/references/</code> or upload "
    "them here, in batches.",
]
GEMINI_FIX = ("Gemini is good at small edits, so ask for just the change: <i>Using the image you just made, remove the "
              "labels and keep everything else the same.</i> A small sparkle mark in a corner is Gemini's watermark; "
              "leave it and I'll paint it out.")

# ---------------------------------------------------------------------- variety pass
# One building per image, a parts kit for houses built in Blender, more trees, animals and background layers,
# so no street shows the same thing twice.

BUILDING_VIEW = (
    "Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer "
    "squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no "
    "corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground "
    "line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m "
    "tall). Even lighting, plain flat light-grey background, no labels."
)
GEMINI_BUILDING_VIEW = (
    "Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an "
    "architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side "
    "wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It "
    "stands on a thin ground line, drawn at the same scale and in the same painted style as the "
    "attached C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds "
    "only the building, unlabeled."
)
SHEET_VIEW = ("Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain "
              "flat light-grey background, even lighting, no labels.")
GEMINI_SHEET_VIEW = ("Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a "
                     "plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.")
GEMINI_GLOBAL_EDITS = [(BUILDING_VIEW, GEMINI_BUILDING_VIEW), (SHEET_VIEW, GEMINI_SHEET_VIEW)]

SECTIONS[-1:-1] = [
    ("G", "Village buildings", "One building per image, so every house on a street can be different. Huts, mud and tin "
                               "houses, the village head's house, shops and landmarks, all at the C4 scale."),
    ("H", "Trees and plants", "Several different trees or plants per image, so no two in view are the same, plus big "
                              "foreground plants to frame the screen edges."),
    ("K", "House parts kit", "Doors, windows, roof edges and doorstep details. Blender builds endless house variations "
                             "from these, so a long street never repeats."),
]


def building(id, title, slug, batch, use, details):
    return dict(id=id, title=title, file=f"{id}_{slug}.png", aspect=L, batch=batch, attach="A1, C4", use=use,
                prompt=details + " " + BUILDING_VIEW)


PROMPTS += [
    # ------------------------------------------------------------------ G: buildings
    building("G1", "Thatched hut", "thatched_hut", 1, "A lane house, and the model for huts built in Blender.",
             "A small mud hut with walls smoothed in red-brown earth and a band of white lime at the base, a steep "
             "palm-leaf thatch roof hanging low over the walls, a short wooden door you would duck through, a tiny window "
             "with a wooden shutter, a clay pot by the door and a pumpkin vine climbing over the thatch."),
    building("G2", "Hut with a bamboo porch", "hut_bamboo_porch", 1, "A lane house with a porch the kid can run under.",
             "A thatched mud hut with a lean-to porch of bamboo poles and a woven palm-mat roof in front, a rope cot under "
             "the porch, firewood stacked against the wall and round cow-dung cakes drying in rows on the side wall."),
    building("G3", "Orange mud house, tin roof", "mud_house_tin_roof", 1, "A lane house; also the model for tin-roof houses built in Blender.",
             "A narrow one-room house with walls plastered in orange ochre mud, a corrugated tin-sheet roof sloping to one "
             "side and weighed down with stones and an old tyre, rust streaks on the tin, a blue-painted wooden plank door, "
             "and a small window with a plank shutter propped open on a stick."),
    building("G4", "Plank and sheet house", "plank_sheet_house", 1, "A lane house that breaks up the painted rows.",
             "A patched-together house of weathered wooden planks and corrugated sheets in faded orange, blue and rust, on a "
             "low mud plinth, with an old saree hung as a curtain for a door, potted chillies on the window ledge and a "
             "plastic bucket by the step."),
    building("G5", "Village head's house", "village_head_house", 1, "The grandest house on the lane: a landmark in level 2 or 3.",
             "The biggest house on the street: two storeys, walls washed in pale yellow with maroon trim, a long sloping "
             "roof of terracotta Mangalore tiles, a deep front veranda with six carved wooden pillars, raised sit-out "
             "platforms on both sides of a big carved double door with brass studs, a brass oil lamp by the door, a tulsi "
             "planter in front and a wooden easy chair on the veranda. Grand and proud, but still a village house."),
    building("G6", "Tiled house with courtyard gate", "tiled_house_gate", 1, "A lane house with a gate and a tree behind its wall.",
             "A single-storey house with a terracotta-tiled roof sloping toward the street, a lime-washed front wall with a "
             "wooden gate into a courtyard, a mango tree peeking over the wall, a small window with blue bars and a kolam "
             "at the gate."),
    building("G7", "Provisions shop", "provisions_shop", 1, "A shopfront on the lane, with a bench and awning.",
             "A small village provisions shop: a narrow shopfront with a corrugated tin awning on wooden poles, wooden shelves "
             "of glass jars of sweets, hanging strings of snack packets and a bunch of bananas, a big brass weighing scale "
             "on the counter, a wooden bench outside and a painted signboard above with pictures of a jar and a bottle and "
             "no letters."),
    building("G8", "Tea stall", "tea_stall", 1, "A tiny stall: steam, glasses and a bench, full of life.",
             "A tiny roadside tea stall built of planks under a palm-thatch awning, a big brass kettle steaming on a clay "
             "stove, a row of small glass tumblers, a jar of biscuits, a wooden bench with a folded newspaper and a small "
             "radio on a shelf."),
    building("G9", "Tailor and cycle repair", "tailor_cycle_shop", 1, "Two tiny shops under one awning.",
             "Two tiny open-fronted shops side by side under one tin awning: a tailor's with a black treadle sewing machine "
             "and colourful fabric bolts, and a cycle-repair shop with tyres and inner tubes hanging up and a pump leaning on "
             "the wall."),
    building("G10", "Potter's house", "potters_house", 2, "Ties in with the clay-pot obstacles: the pots come from here.",
             "A potter's mud house with a thatched work shed beside it, a potter's wheel under the shed, rows of fresh "
             "unfired grey pots drying in the sun and stacks of fired terracotta pots in front."),
    building("G11", "Weaver's house", "weavers_house", 2, "A nod to the kid's pattu frock: silk being woven.",
             "A silk weaver's house with an open front room showing a wooden pit handloom with a half-woven magenta silk "
             "saree, bright silk threads stretched to dry on a frame outside, and lime-washed walls with an indigo band."),
    building("G12", "Half-built two-storey house", "half_built_house", 1, "Every real village has one; it adds height and humour.",
             "A two-storey house that is only half finished: the ground floor plastered and painted mint green with a grille "
             "window and a door, the upper floor bare red brick with steel rods sticking out of the pillar tops, a pile of "
             "sand and bricks in front and a clothesline on the roof."),
    building("G13", "Cattle shed", "cattle_shed", 1, "An open shed: hay, a trough and a calf.",
             "An open cattle shed with a palm-thatch roof on wooden posts, a stone feeding trough, hay piled at the back, a "
             "calf tied to a post and a lime-washed back wall with painted handprints."),
    building("G14", "Panchayat office", "panchayat_office", 2, "A civic building for the lane's end or the market.",
             "A small village office: a flat-roofed concrete building painted pale yellow with a green band, a veranda with "
             "square pillars, a blank notice board, a wall clock, a wooden bench outside and a hand pump beside it."),
    building("G15", "Village shrine", "village_shrine", 1, "A small roadside shrine under a tree, with bell and lamps.",
             "A small roadside shrine to the village guardian: a little whitewashed shrine with a tiny ornate tower on top, "
             "a brass bell at the entrance, marigold garlands and oil lamps, under a big tree with red and yellow threads "
             "tied round its trunk."),
    building("G16", "Overhead water tank", "water_tank_tower", 2, "A landmark on the skyline behind the houses.",
             "The village's overhead water tank: a round concrete tank on four tall concrete legs with a ladder, painted pale "
             "blue with a white band, in a small fenced plot."),

    # ------------------------------------------------------------------ H: trees and plants
    dict(id="H1", title="Neem trees", file="H1_neem_trees.png", aspect=L, batch=1, attach="A1, D4",
         use="Shade trees between houses; three different ones so they never repeat side by side.",
         prompt="Three different neem trees side by side: a big old one with a broad dome of small feathery leaves and a "
                "grey trunk, a young slender one, and one leaning with a swing tied to a branch. Drawn like the attached D4 "
                "mango tree sheet. " + SHEET_VIEW),
    dict(id="H2", title="Tamarind and drumstick trees", file="H2_tamarind_drumstick.png", aspect=L, batch=2, attach="A1, D4",
         use="More shade-tree variety.",
         prompt="Two tamarind trees with dense fine leaves and hanging brown pods, and two drumstick trees with lacy leaves "
                "and long green pods. Drawn like the attached D4 mango tree sheet. " + SHEET_VIEW),
    dict(id="H3", title="Meeting tree with platform", file="H3_peepal_platform.png", aspect=L, batch=2, attach="A1, D4",
         use="The village gathering spot: a one-off landmark.",
         prompt="A huge peepal tree with heart-shaped leaves growing from a raised square stone platform where villagers sit, "
                "a few small stone idols and lamps at its base, and red threads tied round the trunk. Drawn like the attached "
                "D4 mango tree sheet, side-on: the platform's front face square to the viewer and its top barely showing, "
                "not seen from above. " + BUILDING_VIEW),
    dict(id="H4", title="Coconut palms", file="H4_coconut_palms.png", aspect=L, batch=1, attach="A1, D4",
         use="Five different palms, so palms never look stamped.",
         prompt="Five different coconut palms: a tall straight one, one leaning far over, a pair growing from one spot, a "
                "young short palm, and one with a climber's rope ring on the trunk and coconuts in a bunch. Drawn like the "
                "attached D4 mango tree sheet. " + SHEET_VIEW),
    dict(id="H5", title="Banana, papaya and curry-leaf plants", file="H5_garden_plants.png", aspect=L, batch=2, attach="A1, D4",
         use="Small backyard plants for between houses.",
         prompt="Six small backyard plants: a banana plant with a bunch, a torn-leaf banana plant, a papaya tree with fruit, "
                "a curry-leaf bush, a clump of sugarcane and a pumpkin vine on a stick frame. " + SHEET_VIEW),
    dict(id="H6", title="Flowering bushes", file="H6_flowering_bushes.png", aspect=L, batch=1, attach="A1, D4",
         use="Colour by doors and walls; each bush different.",
         prompt="Six flowering bushes and creepers: a hibiscus bush with red flowers, a magenta bougainvillea spilling over a "
                "wall, a jasmine creeper on a bamboo frame, a pink oleander, crotons in clay pots, and a patch of orange "
                "marigolds. " + SHEET_VIEW),
    dict(id="H7", title="Foreground framing plants", file="H7_foreground_plants.png", aspect=L, batch=1, attach="A1",
         use="Big plants in front of the lane, at the screen's bottom corners, like your story frames.",
         prompt="Five large foreground plants for framing the bottom corners of a game screen, drawn bigger and a little "
                "darker than the rest of the scene, as if close to the camera: a clump of big taro leaves, a cluster of tall "
                "grass with seed heads, a corner of banana leaves, a broken corner of a lime-washed compound wall with weeds, "
                "and a mossy rock with ferns. " + SHEET_VIEW),

    # ------------------------------------------------------------------ K: house parts kit
    dict(id="K1", title="Doors and windows", file="K1_doors_windows.png", aspect=L, batch=1, attach="A1, C4",
         use="Fitted to houses Blender builds, so no two front doors match.",
         prompt="Sheet of village doors and windows for a modular house kit, each shown straight on and separate: a carved "
                "double wooden door with brass studs, a plain plank door painted blue, a green-framed door with a marigold "
                "garland, a low hut door, a doorway with a hanging saree curtain, a window with wooden shutters open, a window "
                "with blue iron bars, and a small window with a plank shutter propped open. Drawn at the scale of the attached "
                "C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels."),
    dict(id="K2", title="Roof edges and awnings", file="K2_roof_edges.png", aspect=L, batch=1, attach="A1, C4",
         use="The front edges of roofs Blender builds: thatch, tiles, tin and awnings.",
         prompt="Six roof edges and awnings for a modular house kit, each a long horizontal strip seen straight on from the "
                "front: a palm-thatch eave, a terracotta Mangalore-tile eave, a corrugated tin-sheet eave with rust, a "
                "flat-roof parapet with pots on it, a striped cloth awning and a bamboo-and-palm-mat awning. Drawn at the "
                "scale of the attached C4 house kit. Plain flat light-grey background, even lighting, no labels."),
    dict(id="K3", title="Doorstep and wall details", file="K3_wall_details.png", aspect=L, batch=2, attach="A1, C4",
         use="Small details that make every built house its own.",
         prompt="Sheet of small details for village house fronts, each separate and seen straight on: three different front "
                "steps with kolam, a raised sit-out platform, a brass wall lamp, a hanging lantern, a row of cow-dung cakes "
                "drying on a wall, a wall shelf with clay pots, a hanging bird feeder and a mango-leaf garland. Drawn at the "
                "scale of the attached C4 house kit. Plain flat light-grey background, even lighting, no labels."),

    # ------------------------------------------------------------------ more animals
    dict(id="B8", title="Cows and goats", file="B8_cows_goats.png", aspect=L, batch=1, attach="A1, B7",
         use="More animals, so the same one never appears twice in view.",
         prompt="Village livestock, drawn like the attached B7 animal sheet: a white cow with painted horns and a bell, a "
                "brown calf, a goat standing on a low wall, a goat eating leaves, a black goat kid jumping, and a buffalo "
                "standing. " + SHEET_VIEW),
    dict(id="B9", title="Small animals and birds", file="B9_small_animals.png", aspect=L, batch=1, attach="A1, B7",
         use="Life on walls and rooftops: cats, crows, parrots, hens with chicks.",
         prompt="Small village animals and birds, drawn like the attached B7 animal sheet: a cat asleep on a wall, three crows "
                "on a ledge, a pair of green parrots, a mother hen with five chicks, two white ducks, a peacock with its tail "
                "folded, and a striped palm squirrel. " + SHEET_VIEW),
    dict(id="B10", title="Villagers in the background", file="B10_villagers.png", aspect=L, batch=2, attach="A1",
         use="People going about their day behind the chase.",
         prompt="Background villagers going about their day, drawn simply and warmly in the game's style: a woman drawing a "
                "kolam, an old man sitting on a veranda with a walking stick, a man riding a bicycle with a milk can, two kids "
                "rolling a tyre with a stick, a woman carrying a water pot on her head, and a vegetable seller with a push "
                "cart. " + SHEET_VIEW),

    # ------------------------------------------------------------------ more background layers
    dict(id="C8", title="Lane middle layer 2", file="C8_lane_mid_layer_2.png", aspect=L, batch=1, attach="A1, C3",
         use="A second distance layer, so the palm band does not repeat.",
         prompt="Middle parallax layer, side-on, a different stretch from the attached C3 layer: a band of terracotta-tiled "
                "roofs and banana groves with a white overhead water tank and a few tall palms, a little hazy. Isolated on a "
                "solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground."),
    dict(id="C9", title="Lane middle layer 3", file="C9_lane_mid_layer_3.png", aspect=L, batch=2, attach="A1, C3",
         use="A third distance layer.",
         prompt="Middle parallax layer, side-on, different again from the attached C3 layer: big neem and tamarind trees "
                "over thatched roofs, a rocky hillock with a tiny white shrine on top and a line of palms. Isolated on a "
                "solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground."),

    # ------------------------------------------------------------------ more textures
    dict(id="T8", title="Corrugated tin sheet", file="T8_tex_tin_sheet.png", aspect=S, batch=1, attach="A1", block="texture",
         use="Roofs of the tin-roof houses Blender builds.",
         prompt="A front-on texture of an old corrugated tin roofing sheet: silver-grey ridges with patches of orange rust, "
                "rust streaks and a few nail heads."),
    dict(id="T9", title="Orange mud plaster", file="T9_tex_orange_mud.png", aspect=S, batch=1, attach="A1", block="texture",
         use="Walls of the orange mud houses Blender builds.",
         prompt="A front-on texture of a mud-plastered wall in warm orange ochre: hand-smoothed, with finger swirls, small "
                "cracks and a few patches where the red-brown earth shows."),
    dict(id="T10", title="Bare brick", file="T10_tex_bare_brick.png", aspect=S, batch=2, attach="A1", block="texture",
         use="Unfinished upper floors and back walls.",
         prompt="A front-on texture of an unplastered red brick wall with uneven grey mortar lines and a few chipped bricks."),
    dict(id="T11", title="Woven coconut-leaf fence", file="T11_tex_coconut_leaf_fence.png", aspect=S, batch=1, attach="A1",
         block="texture",
         use="The fences around house compounds, built in Blender: so they look woven by hand, not tiled.",
         prompt="A front-on texture of a village compound fence made of dried coconut palm leaves woven in overlapping "
                "rows: tan, straw and grey-brown leaflets folded over thin horizontal sticks, a few frayed ends and small "
                "gaps."),
    dict(id="T12", title="Plain red earth", file="T12_tex_plain_red_earth.png", aspect=S, batch=1, attach="A1, T1",
         block="texture",
         use="The grain of the lane's ground, which Blender builds without repeating: it needs earth with no marks in it.",
         prompt="A texture of bare red laterite earth seen straight down, in the colours of the attached T1 texture: fine "
                "dust, crumbs and grit, soft brush-stroke variation between deep red, red-orange and dusty orange. Only the "
                "earth itself: no footprints, tracks, leaves, plants or stones."),
    dict(id="C10", title="Ground details to scatter", file="C10_ground_details.png", aspect=L, batch=1, attach="A1, T1",
         use="Scattered one by one over the lane, each at a random turn and size, so the ground never repeats.",
         prompt="A sheet of separate ground details for a red-earth village lane, each one seen straight down and drawn in "
                "the game's painted style: a few pebbles of different sizes, a small cluster of pebbles, three dry mango "
                "leaves, a broken piece of dry coconut frond, a coconut husk, a few twigs, four small grass tufts, two "
                "weeds with tiny yellow flowers, a short stretch of bullock-cart wheel rut, a trail of bare child "
                "footprints, cow hoof prints, hen footprints, and a patch of dried, cracked mud. Spaced apart so none "
                "touch. Plain flat light-grey background, even lighting, no labels."),
]

GEMINI_SHAPES.update({p["id"]: SIXTEEN for p in PROMPTS if p["id"] not in GEMINI_SHAPES})
GEMINI_SHAPES.update({i: WIDE for i in ["C8", "C9"]})
GEMINI_SHAPES.update({i: SQUARE for i in ["T8", "T9", "T10", "T11", "T12"]})
GEMINI_SIDE_ON.update({"C8", "C9"})
GEMINI_ROLES.update({
    "C4": "the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style",
    "B7": "the B7 animal sheet, to match how animals are drawn and their scale",
    "D4": "the D4 mango tree sheet, to match how trees are drawn",
    "C3": "the C3 middle layer, to match its style and haze (but show a different stretch)",
    "T1": "the T1 earth texture, to match the colour of the red earth",
})
GEMINI_EDITS.update({
    "C8": [("Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.",
            "Everything else in the image is solid flat magenta (#FF00FF), so the layer can be cut out cleanly.")],
    "C9": [("Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.",
            "Everything else in the image is solid flat magenta (#FF00FF), so the layer can be cut out cleanly.")],
    "C10": [("Plain flat light-grey background, even lighting, no labels.",
             "Even lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.")],
    "K1": [("Plain flat light-grey background, even lighting, no labels.",
            "Even lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.")],
    "K2": [("Plain flat light-grey background, even lighting, no labels.",
            "Even lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.")],
    "K3": [("Plain flat light-grey background, even lighting, no labels.",
            "Even lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.")],
})

# The street now uses only painted houses (no houses built in 3D), so the kit pieces and textures for built houses
# wait in the second batch.
for _p in PROMPTS:
    if _p["id"] in {"K1", "K2", "T8", "T9"}:
        _p["batch"] = 2
        _p["use"] += " Only needed if houses are built in 3D again; the street uses painted houses for now."

# Images in the repo that need making again, and why. They count as still to make.
REDO = {
    "D7": "Came out as a view looking across the fields in perspective, with magenta only along the top: make it "
          "again as a flat side-on band, like C8, with magenta all round it.",
    "H3": "Came out seen from above, with the platform at an angle: make it again side-on, the platform's front face "
          "square to the viewer and its top barely showing, like the G buildings.",
}

# ------------------------------------------------------------------ zones 2 and 3, built from the art like zone 1
FRONTS_SHEET = (
    "Each building as a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel "
    "to the picture, so no side wall or gable end shows and there is no perspective. All standing on one thin ground "
    "line, at the same scale as the attached C4 house kit (doors about 2 m tall), evenly spaced and not touching. Plain "
    "flat light-grey background, even lighting, no labels and no writing on any sign."
)
GEMINI_FRONTS_SHEET = (
    "Draw each building as a flat front elevation for a side-scrolling game, like an architect's drawing: its front "
    "faces the viewer squarely, parallel to the picture plane, with no side wall or gable end showing. They all stand "
    "on one thin ground line, at the same scale as the uploaded C4 house kit (doors about 2 m tall), evenly spaced with "
    "clear gaps between them. Even lighting on a plain light-grey background; signs are blank and the image holds "
    "only the drawings, unlabeled."
)
GEMINI_GLOBAL_EDITS.append((FRONTS_SHEET, GEMINI_FRONTS_SHEET))
ZONE_23 = [
    dict(id="D5", title="Field buildings", file="D5_field_buildings.png", aspect=L, batch=2, attach="A1, C4, D1",
         use="The buildings along the zone 2 fields, so no two in view are the same.",
         prompt="Four buildings that stand at the edge of paddy fields, in the look of the attached D1 painting: a "
                "small brick pump house with a pipe pouring water into a channel; a farmer's thatched mud hut with a "
                "bamboo cattle pen beside it; a little tiled granary raised on stone stilts; and a tiny fieldside "
                "shrine of whitewashed stone with a red flag. " + FRONTS_SHEET),
    dict(id="D6", title="Crops and field edges", file="D6_crops_field_edges.png", aspect=L, batch=2, attach="A1, D1",
         use="Pieces the fields are built from: crop rows, bunds and canal banks, never the same twice.",
         prompt="Separate pieces for building paddy fields, in the look of the attached D1 painting: a strip of young "
                "green paddy in water, a strip of tall paddy, a strip of golden ripe paddy, a short stretch of raised "
                "earthen bund with grass on top, a canal bank with reeds and lotus leaves, a sugarcane patch, a small "
                "haystack, and a row of three palmyra palms. " + SHEET_VIEW),
    dict(id="D7", title="Fields middle layer", file="D7_fields_mid_layer.png", aspect=L, batch=2, attach="A1, D1, D2",
         use="The band of fields and palms right behind zone 2, between the play area and the D2 far layer.",
         prompt="Middle parallax layer for the fields, side-on: a band of paddy fields stepping away in terraces, lines "
                "of palmyra palms, a few distant farmhouses with tiled roofs and a white egret or two, in the light of "
                "the attached D1 painting and a little hazy like the D2 far layer. Isolated on a solid flat magenta "
                "(#FF00FF) background so it can be cut out. No sky and no ground."),
    dict(id="E6", title="Rooftop houses 1", file="E6_rooftop_houses_1.png", aspect=L, batch=2, attach="A1, C4, E1",
         use="The houses whose flat roofs the kid runs across in zone 3.",
         prompt="Three two-storey village houses with flat roofs you could walk on, in the look of the attached E1 "
                "painting: one with an outside staircase climbing its side wall to the roof; one with a black water "
                "tank and a clothesline on its roof; and one with a small room on the roof and a creeper hanging over "
                "the parapet. Their roofs are at slightly different heights. " + FRONTS_SHEET),
    dict(id="E7", title="Rooftop houses 2", file="E7_rooftop_houses_2.png", aspect=L, batch=2, attach="A1, C4, E1",
         use="More rooftop houses, so no two neighbours match.",
         prompt="Three more two-storey village houses with flat walkable roofs, different from each other, in the look "
                "of the attached E1 painting: one painted turquoise with a pergola of bougainvillea on the roof; one "
                "in yellow with mats of red chillies drying on the roof; and one half-plastered with a satellite dish "
                "and a parked bicycle below. Their roofs are at slightly different heights. " + FRONTS_SHEET),
    dict(id="E8", title="Market stalls 1", file="E8_market_stalls_1.png", aspect=L, batch=2, attach="A1, C4, E2",
         use="Stall fronts for the zone 3 market, so the row never repeats.",
         prompt="Four weekly-market stalls in the look of the attached E2 painting, each under a striped cloth awning "
                "of a different colour and height: a vegetable stall with heaps of tomatoes, brinjals and greens; a "
                "flower stall hung with marigold and jasmine garlands; a bangle and toy stall; and a stall of stacked "
                "steel and brass vessels. " + FRONTS_SHEET),
    dict(id="E9", title="Market stalls 2", file="E9_market_stalls_2.png", aspect=L, batch=2, attach="A1, C4, E2",
         use="More market stalls and carts.",
         prompt="Four more market stalls and carts in the look of the attached E2 painting: a tender-coconut cart with "
                "a sickle and a pile of green coconuts; a sweets and snacks stall with a big iron kadai; a fruit stall "
                "with bananas and mangoes; and a seller of woven baskets and mats under a tarpaulin. " + FRONTS_SHEET),
    dict(id="E10", title="Temple street", file="E10_temple_street.png", aspect=L, batch=2, attach="A1, C4, E3",
         use="The buildings along the way to the temple steps in level 9.",
         prompt="Four buildings on the street leading to the temple steps, in the look of the attached E3 painting at "
                "dusk with lamps lit: a stone mandapam with carved pillars; a flower shop selling garlands for the "
                "temple; a shop of brass lamps and pooja items; and a stretch of the temple tank's wall with steps "
                "and a small arched gateway. " + FRONTS_SHEET),
]
PROMPTS += ZONE_23
GEMINI_SHAPES.update({p["id"]: SIXTEEN for p in ZONE_23})
GEMINI_SHAPES["D7"] = WIDE
GEMINI_SIDE_ON.add("D7")
GEMINI_ROLES.update({
    "D1": "the D1 fields painting, to match its look and light",
    "D2": "the D2 far layer, to match its haze",
    "E1": "the E1 rooftops painting, to match its look and sunset light",
    "E2": "the E2 market painting, to match its look and dusk light",
    "E3": "the E3 temple steps painting, to match its look and lamp light",
})
GEMINI_EDITS["D7"] = [("Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.",
                       "Everything else in the image is solid flat magenta (#FF00FF), so the layer can be cut out cleanly.")]

# Images in the repo that work, with something to know about them. They count as made.
NOTES = {
    "B8": "Usable: the cow, calf and goats cut out cleanly. The buffalo came out lost in a dust cloud, so make it again "
          "only if you want the buffalo.",
    "C9": "Usable: the haze painted round the hillock stays in the layer as a soft patch, which suits a distant layer.",
}

# ------------------------------------------------------------------ refined after the second round of images
# What went wrong last time, and what each sentence below guards against:
#   * G1, G4, G13 and B8 came back with a blurred painted backdrop or a dust cloud behind the drawing -> CLEAN_BG.
#   * D7 came back as a perspective view across the fields; C8 and C9 had haze glowing over the magenta -> BAND.
#   * H3 came back seen from above -> its own front-elevation wording, with G15 attached as the example to copy.
#   * Pieces that worked best (C8, G7, G12, G14, G15) are attached as layout examples for the new ones.
CLEAN_BG = ("Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or "
            "blurred scenery behind or around anything, and nothing cropped by the edges of the image.")
GEMINI_CLEAN_BG = ("The background is a single flat light grey all over, with no painted ground, sky, haze, dust, mist, "
                   "glow or blurred scenery anywhere, and every drawing sits wholly inside the frame.")
BAND = ("Lay it out exactly like the attached C8 layer: a side-on strip of scenery, like a flat stage backdrop, with "
        "everything standing along one straight, level ground strip near the bottom. Nothing recedes into the "
        "distance: no perspective, no fields or roads seen from above, no horizon. The strip runs off the left and "
        "right edges so it can repeat sideways. Pure flat magenta (#FF00FF) fills everything above the strip and "
        "below its ground, right up to the drawing's edges, with no haze, glow, mist or light rays over the magenta.")
GEMINI_BAND = ("Lay it out exactly like the uploaded C8 layer: a side-on strip of scenery, like a flat stage backdrop, "
               "with everything standing along one straight, level ground strip near the bottom. Everything is seen "
               "from the side at the same distance, so nothing recedes and there are no fields or roads seen from "
               "above and no horizon. The strip runs off the left and right edges so it can repeat sideways. Pure flat "
               "magenta (#FF00FF) fills everything above the strip and below its ground, right up to the drawing's "
               "edges, and the magenta stays clean, with no haze, glow, mist or light rays over it.")
TILE = ("The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density "
        "everywhere, so copies placed side by side show no seam and no obvious repeat.")
GEMINI_TILE = ("The pattern runs off all four edges with no border, frame or standout feature, at an even density "
               "everywhere, so copies placed side by side show no seam and no obvious repeat.")
STORY = ("Leave the top third as open sky or plain wall, quieter than the rest, for the game's buttons and text; the "
         "image itself has no words. The kid matches the attached A0 sheet and the rooster the attached B1 sheet.")
GEMINI_STORY = ("Keep the top third open sky or plain wall, calmer than the rest, so the game can place its buttons and "
                "text there; the image itself holds no words. The kid matches the uploaded A0 sheet and the rooster "
                "the uploaded B1 sheet.")
GEMINI_GLOBAL_EDITS += [(CLEAN_BG, GEMINI_CLEAN_BG), (BAND, GEMINI_BAND), (TILE, GEMINI_TILE), (STORY, GEMINI_STORY)]
GEMINI_ROLES.update({
    "C8": "the C8 middle layer, as the layout to copy: a flat side-on strip on magenta",
    "G7": "the G7 shop, as an example of a flat front-on building that cut out well",
    "G12": "the G12 half-built house, as an example of a flat front-on two-storey building",
    "G14": "the G14 panchayat office, as an example of a flat front-on building",
    "G15": "the G15 shrine under its tree, as the example to copy: a tree and its base drawn flat and front-on",
    "H1": "the H1 trees, to match how trees and leaves are drawn",
    "E1": "the E1 rooftops painting, to match its look and sunset light",
})

REFINED = {
    "D7": dict(attach="A1, C8, D1, D2", prompt=(
        "Middle parallax layer for the fields: in front, a long low earthen bund with grass along the bottom; behind "
        "it, a row of paddy at different heights and greens, a line of palmyra palms, two or three small farmhouses "
        "with tiled roofs half hidden by banana plants, and a white egret standing in the paddy, in the light of the "
        "attached D1 painting and a little paler than the foreground, as if a few hundred metres away. " + BAND)),
    "H3": dict(attach="A1, G15, H1, C4", prompt=(
        "A huge old peepal tree with heart-shaped leaves, its roots gripping a raised square platform of grey stone "
        "where villagers sit in the evening; a few small stone idols, clay lamps and flowers at the foot of the trunk, "
        "and red and yellow threads tied round it. Drawn flat and front-on like the attached G15 shrine, for a "
        "side-scrolling game: the platform is seen straight from the front as a low rectangle of stone about 0.8 m "
        "high and 6 m wide, with three steps in the middle, its top surface hidden behind its front edge; the tree "
        "rises from it about 12 m tall, its canopy wide and spreading. No perspective, nothing seen from above. "
        "Standing on a thin ground line at the scale of the attached C4 house kit (doors about 2 m tall). Even "
        "lighting, no labels. " + CLEAN_BG)),
    "T11": dict(prompt=(
        "A front-on texture of a village compound fence of dried coconut palm leaves woven in rows that run straight "
        "across: tan, straw and grey-brown leaflets folded over thin horizontal sticks, with a few frayed ends, small "
        "gaps and darker weathered leaves. It shows only the woven panel, filling the square: no posts, ground, sky "
        "or top edge. " + TILE)),
    "T12": dict(prompt=(
        "A texture of bare red laterite earth seen straight down from above, in the colours of the attached T1 "
        "texture: fine dust, crumbs and grit, with soft brush-stroke variation between deep red, red-orange and "
        "dusty orange. Only the earth itself: no footprints, tracks, leaves, plants, stones or cracks, and no patch "
        "darker or lighter than the rest. " + TILE)),
    "T10": dict(prompt=(
        "A front-on texture of an unplastered red brick wall: bricks of slightly different reds in straight courses, "
        "uneven grey mortar lines, a few chipped corners and a faint splash of old cement. Only the wall, filling the "
        "square. " + TILE)),
    "E6": dict(attach="A1, C4, E1, G12", prompt=(
        "Three two-storey village houses with flat roofs you could walk on, in the look of the attached E1 painting "
        "and drawn flat like the attached G12 house: one with an outside concrete staircase climbing diagonally across "
        "its front wall to the roof; one with a black water tank and a clothesline on its roof; and one with a small "
        "room on the roof and a creeper hanging over the parapet. Each roof has a low parapet, at slightly different "
        "heights from house to house. " + FRONTS_SHEET + " " + CLEAN_BG)),
    "E7": dict(attach="A1, C4, E1, G12", prompt=(
        "Three more two-storey village houses with flat walkable roofs, different from each other, in the look of the "
        "attached E1 painting and drawn flat like the attached G12 house: one painted turquoise with a pergola of "
        "bougainvillea on the roof; one in yellow with mats of red chillies drying on the roof; and one "
        "half-plastered, bricks showing on its upper floor, with a satellite dish on the roof and a bicycle leaning "
        "by the door. Each roof has a low parapet, at slightly different heights from house to house. "
        + FRONTS_SHEET + " " + CLEAN_BG)),
    "E8": dict(attach="A1, C4, E2, G7", prompt=(
        "Four weekly-market stalls in the look of the attached E2 painting and drawn flat like the attached G7 shop, "
        "each under a striped cloth awning of a different colour, the awnings at different heights and seen from the "
        "front: a vegetable stall with heaps of tomatoes, brinjals, onions and greens on a low table; a flower stall "
        "hung with marigold and jasmine garlands; a bangle and toy stall with a rack of glass bangles; and a stall of "
        "stacked steel and brass vessels. " + FRONTS_SHEET + " " + CLEAN_BG)),
    "E9": dict(attach="A1, C4, E2, G7", prompt=(
        "Four more market stalls and carts in the look of the attached E2 painting and drawn flat like the attached "
        "G7 shop: a tender-coconut cart with a pile of green coconuts and a sickle, seen from the side; a sweets and "
        "snacks stall with a big iron kadai and trays of sweets; a fruit stall with bananas, mangoes and guavas under "
        "a tarpaulin; and a seller of woven baskets and mats stacked under a bamboo frame. "
        + FRONTS_SHEET + " " + CLEAN_BG)),
    "E10": dict(attach="A1, C4, E3, G14", prompt=(
        "Four buildings on the street leading to the temple steps, in the look of the attached E3 painting at dusk "
        "with oil lamps lit, and drawn flat like the attached G14 building: a stone mandapam with a row of carved "
        "pillars; a flower shop selling garlands for the temple; a shop of brass lamps and pooja items; and a stretch "
        "of the temple tank's wall with a small arched gateway. " + FRONTS_SHEET + " " + CLEAN_BG)),
    "F7": dict(attach="A1, A0, B1, E1", prompt=(
        "Loss screen illustration, side-on like the game: the rooster stands on a rooftop parapet against a sunset "
        "sky like the attached E1 painting, chest out, wings spread, crowing in triumph; far below, a tiny toddler in "
        "the pattu frock looks up with hands on hips and a determined pout, ready to try again. The toddler is "
        "barefoot, with silver anklets. Funny and gentle, never sad. " + STORY)),
    "F8": dict(attach="A1, A0, B1, B6", prompt=(
        "Final story frame, Amma's kitchen, side-on like the game: a warm, lamp-lit village kitchen with a clay stove, "
        "brass and steel vessels on wooden shelves and strings of dried chillies. The toddler in the pattu frock "
        "proudly holds up the rooster in both arms to Amma, who matches the attached B6 sheet and looks down with "
        "surprise and a smile; the rooster looks put out. Golden evening light through a small window. The toddler "
        "is barefoot, with silver anklets. Nothing shown beyond this moment. " + STORY)),
}
for _p in PROMPTS:
    if _p["id"] in REFINED:
        _p.update(REFINED[_p["id"]])
        GEMINI_EDITS.pop(_p["id"], None)  # the old wording these fixed is gone
    if _p["id"] in {"D7", "H3", "T11", "T12", "E6", "E7", "E8", "E9", "E10", "F7", "F8", "T10"}:
        _p["refined"] = True
GEMINI_SHAPES.update({"F7": SIXTEEN, "F8": SIXTEEN, "H3": SIXTEEN})

# Cut-out pieces get the style rules without the sentence about atmospheric backgrounds: its "haze, light shafts and
# floating dust" is what painted the dust clouds and haze into the last round's sheets and bands.
_ATMOS = "Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. "
PIECE_STYLE = STYLE.replace(_ATMOS, "Paint everything crisp and clear, with visible brush texture inside each shape. ")
GEMINI_PIECE_STYLE = GEMINI_STYLE.replace(_ATMOS, "Paint everything crisp and clear, with visible brush texture inside each shape. ")
assert PIECE_STYLE != STYLE and GEMINI_PIECE_STYLE != GEMINI_STYLE
for _p in PROMPTS:
    if _p["id"] in {"D7", "H3", "E6", "E7", "E8", "E9", "E10"}:
        _p["block"] = "piece"

# ------------------------------------------------------------------ the era: a village of the 1970s and 1980s
# Every prompt now says when it's set, so no image comes back with modern things in it.
ERA = ("The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and "
       "terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing "
       "modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey "
       "buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.")
GEMINI_ERA = ("It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud "
              "and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and "
              "palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic "
              "buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water "
              "tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.")
STYLE = STYLE.replace("Art style:", ERA + "\n\nArt style:", 1)
GEMINI_STYLE = GEMINI_ERA + " " + GEMINI_STYLE
TEXTURE = TEXTURE + " Only materials a 1970s village would have."
GEMINI_TEXTURE = GEMINI_TEXTURE + " Only materials a 1970s village would have."
PIECE_STYLE = STYLE.replace(_ATMOS, "Paint everything crisp and clear, with visible brush texture inside each shape. ")
GEMINI_PIECE_STYLE = GEMINI_STYLE.replace(_ATMOS, "Paint everything crisp and clear, with visible brush texture inside each shape. ")

# Zone 3 rows: rural buildings are wide and low, so these ask for fewer, bigger pieces per image, each much wider
# than tall, with its size in metres, filling the image's width (the first round came back as narrow town houses).
WIDE_FRONTS = (
    "Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one "
    "is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. "
    "Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the "
    "picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at "
    "the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even "
    "lighting, no labels and no writing on any sign."
)
GEMINI_WIDE_FRONTS = (
    "Draw them big, side by side with a clear gap between them, so together they fill most of the image's width. Each "
    "one is wide and low, much wider than it is tall, as rural village buildings are, rather than a narrow, tall town "
    "house. Draw each as a flat front elevation for a side-scrolling game, like an architect's drawing: its front faces "
    "the viewer squarely, parallel to the picture plane, with no side wall or gable end showing. They all stand on one "
    "thin ground line, at the same scale as the uploaded C4 house kit (doors about 2 m tall). Even lighting on a plain "
    "light-grey background; signs are blank and the image holds only the drawings, unlabeled."
)
GEMINI_GLOBAL_EDITS.append((WIDE_FRONTS, GEMINI_WIDE_FRONTS))

VINTAGE = {
    "E6": dict(title="Village houses with roof terraces 1", attach="A1, C4, E1, G10", prompt=(
        "Two single-storey village houses of the 1970s, each wide and low the way rural houses are: about 12 m wide and "
        "4 m from the ground to the top of its roof parapet, three times as wide as it is tall. Their flat "
        "lime-plastered roofs are terraces a child could run along. In the look of the attached E1 painting, drawn flat "
        "like the attached G10 house. The first is lime-washed, with a long front veranda (thinnai) of raised platforms "
        "either side of the door under a sloping terracotta-tiled lean-to on wooden pillars, a kolam at the steps, a "
        "tulsi planter, cow-dung cakes drying on its end wall, stone steps climbing the end wall to the roof, and a small "
        "haystack and big clay pots on the terrace. The second is mud-plastered in ochre with a red-oxide plinth, a "
        "pumpkin creeper spreading over its roof, paddy and coconut fronds drying on the terrace, and a thatched cattle "
        "shed built onto one end with a calf tied to a post. " + WIDE_FRONTS + " " + CLEAN_BG)),
    "E7": dict(title="Village houses with roof terraces 2", attach="A1, C4, E1, G10", prompt=(
        "Two more single-storey village houses of the 1970s, different from each other, each wide and low: about 11 m "
        "wide and 4 m to the top of its roof parapet. Their flat roofs are terraces a child could run along. In the look "
        "of the attached E1 painting, drawn flat like the attached G10 house. The first is pale blue lime wash with "
        "green-painted wooden shutters, a long low veranda, a bamboo ladder leaning up to the roof, and red chillies "
        "and round papads drying on woven mats on the terrace. The second is an old house, its lime wash flaking to "
        "show the brick, with a small thatched room on one corner of its roof, firewood stacked on the terrace, a "
        "jasmine creeper over the parapet, a rope cot leaning against the front wall and hens pecking by the door. "
        + WIDE_FRONTS + " " + CLEAN_BG)),
    "E8": dict(title="Shandy stalls 1", attach="A1, C4, E2, E5", prompt=(
        "Three stalls at a 1970s weekly village shandy held on open ground under the trees, in the look of the attached "
        "E2 painting and drawn like the attached E5 props. Each is wide and low, about 5 m wide and under 3 m tall, "
        "nearly twice as wide as it is tall, its goods spread out along the ground: a vegetable seller's long rows of "
        "tomatoes, brinjals, onions, gourds and greens heaped on jute sacks under a wide faded striped cotton awning on "
        "four bamboo poles; a flower seller sitting among baskets, marigold and jasmine garlands hung along a long "
        "bamboo pole under a woven palm-leaf mat; and a brass and copper vessel seller's pots and lamps laid out on a "
        "long mat under a low thatched shade. " + WIDE_FRONTS + " " + CLEAN_BG)),
    "E9": dict(title="Shandy stalls 2", attach="A1, C4, E2, E5", prompt=(
        "Three more stalls and carts at a 1970s weekly village shandy, in the look of the attached E2 painting and drawn "
        "like the attached E5 props. Each is wide and low, about 5 m wide and under 3 m tall: a bullock cart loaded "
        "with tender coconuts, seen from the side, its two bullocks resting beside it; a sweets seller with a big iron "
        "kadai over a wood fire and trays of jalebis and murukku under a long cloth awning; and a potter's clay pots, "
        "lamps and toys laid out in rows on the ground under a big black cloth umbrella and a palm-leaf shade. "
        + WIDE_FRONTS + " " + CLEAN_BG)),
    "E10": dict(title="Village temple lane", attach="A1, C4, E3, G15", prompt=(
        "Three buildings on the lane to the village temple, simple and old, in the look of the attached E3 painting at "
        "dusk, lit only by oil lamps, and drawn flat like the attached G15 shrine. Each is wide and low: a long stone "
        "mandapam (pillared hall), about 14 m wide and 5 m tall, with a row of carved pillars under a flat stone roof; "
        "a long thatched shed, about 10 m wide, where the village's wooden temple chariot is kept, its carved front "
        "peeping out; and a 12 m stretch of the temple tank's stone wall with steps going down and a small arched "
        "gateway, oil lamps along its ledge. " + WIDE_FRONTS + " " + CLEAN_BG)),
    "G12": dict(file="G12_house_being_built.png", title="House being built", prompt=(
        "A village house being built the 1970s way: walls of sun-dried mud bricks halfway up, a bamboo scaffold lashed "
        "with coir rope, a wooden door frame already standing in place, a heap of mud mixed with straw, and stacks of "
        "terracotta roof tiles and wooden rafters waiting beside it. " + BUILDING_VIEW)),
    "G16": dict(file="G16_stone_lamp_pillar.png", title="Stone lamp pillar", prompt=(
        "A tall carved stone lamp pillar (deepa stambha) on a stepped stone base, about 9 m high, with little stone "
        "ledges for oil lamps all the way up, a small brass bell and marigold garlands tied at its foot: a landmark "
        "seen over the rooftops. " + BUILDING_VIEW)),
    "E1": dict(prompt=(
        "Environment painting, side-on like a side-scrolling game level, no characters: a run of connected flat "
        "Madras-terrace village rooftops of the 1970s at sunset with small gaps between the houses, low parapets, big "
        "clay water pots, red chillies and round papads drying on woven mats, a clothesline with cotton saris, a bamboo "
        "ladder, paper kites in the sky and festival bunting strung between houses. The setting sun rims everything in "
        "orange.")),
    "E4": dict(prompt=(
        "Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a big clay water pot on a "
        "low stone stand; a section of rooftop parapet wall with a gap; a woven mat of red chillies drying; a woven mat "
        "of round papads; a paper kite with a tail; a string of triangular festival bunting.")),
    "G4": dict(prompt=next(p for p in PROMPTS if p["id"] == "G4")["prompt"].replace("a plastic bucket", "a brass bucket")),
    "G14": dict(prompt=next(p for p in PROMPTS if p["id"] == "G14")["prompt"].replace(
        "a flat-roofed concrete building", "a flat-roofed, lime-plastered building of the 1970s")),
}
for _p in PROMPTS:
    if _p["id"] in VINTAGE:
        _p.update(VINTAGE[_p["id"]])
        GEMINI_EDITS.pop(_p["id"], None)
        _p["refined"] = True
GEMINI_ROLES.setdefault("G5", "the G5 village head's house, as an example of a flat front-on two-storey house of the time")
GEMINI_ROLES.setdefault("E5", "the E5 market props, to match how the stalls and goods are drawn")

# Made images with modern things in them: G12 (a half-built concrete house) and G16 (an overhead water tank) are
# replaced by new subjects; E1's black water tanks and E4's are simply left unused.
REDO.update({
    "G12": "The half-built concrete house is too modern for a 1970s village: make the new subject, a house being built "
           "with mud bricks and a bamboo scaffold.",
    "G16": "The overhead water tank is too modern for a 1970s village: make the new subject, a stone lamp pillar.",
})
NOTES.update({
    "E1": "Usable as a mood reference; its black plastic water tanks are not used in the game.",
    "E4": "Usable, except the black plastic water tank, which is too modern and not used.",
})

GEMINI_SHAPES.update({i: WIDE for i in ["E6", "E7", "E8", "E9", "E10"]})  # wide images for wide buildings
GEMINI_ROLES["G10"] = "the G10 potter's house, as an example of a wide, low village house drawn flat and front-on"
GEMINI_ROLES["G15"] = "the G15 shrine under its tree, as an example of a tree and a village building drawn flat and front-on"

# ------------------------------------------------------------------ no striped awnings
# Red-and-white striped awnings look like a modern or Western market, not a 1970s Indian village. Shades are plain
# faded cotton (indigo, turmeric, madder red or undyed), woven palm-leaf mats, thatch or a black cloth umbrella.
NO_STRIPES = (" Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf "
              "mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.")
ERA = ERA + NO_STRIPES
GEMINI_ERA = GEMINI_ERA + NO_STRIPES
STYLE = STYLE.replace("Art style:", NO_STRIPES.strip() + "\n\nArt style:", 1)
GEMINI_STYLE = GEMINI_STYLE.replace("Render it as", NO_STRIPES.strip() + " Render it as", 1)
PIECE_STYLE = STYLE.replace(_ATMOS, "Paint everything crisp and clear, with visible brush texture inside each shape. ")
GEMINI_PIECE_STYLE = GEMINI_STYLE.replace(_ATMOS, "Paint everything crisp and clear, with visible brush texture inside each shape. ")
for _p in PROMPTS:
    _p["prompt"] = (_p["prompt"]
                    .replace("a row of stalls with striped cloth awnings at different heights",
                             "a row of stalls under plain faded cotton awnings, palm-leaf mats and thatch at different "
                             "heights")
                    .replace("a market stall with a striped cloth awning in two versions, one high and one low",
                             "a market stall under a plain faded indigo cotton awning on bamboo poles, in two versions, "
                             "one high and one low")
                    .replace("red-and-white market awning stripes", "a plain faded madder-red cotton awning cloth")
                    .replace("a striped cloth awning and a bamboo-and-palm-mat awning",
                             "a plain faded cotton awning and a bamboo-and-palm-mat awning")
                    .replace("under a wide faded striped cotton awning on four bamboo poles",
                             "under a wide plain awning of faded indigo cotton on four bamboo poles")
                    .replace("under a long cloth awning", "under a long plain, undyed cotton awning"))
    if _p["id"] in {"E2", "E5", "T7", "K2", "E8", "E9"}:
        _p["refined"] = True
for _k in ["E2", "E5", "T7", "K2", "E8", "E9"]:
    GEMINI_EDITS.pop(_k, None)

NOTES.update({
    "E2": "Usable as a mood reference only; its striped awnings are not used.",
    "E5": "Usable, except the two red-and-white striped stalls, which are not used.",
    "E8": "Usable, except the vegetable stall's red-and-white striped awning, which is not used.",
    "E9": "Usable, except the sweets stall's red-and-white striped awning, which is not used.",
})

# ------------------------------------------------------------------ the rooster's turnaround, one view per image
# For modelling the rooster in 3D: four separate, identically framed views with the beak closed (B1 put all views on
# one sheet, with the beak open in a grin).
TURN = ("One rooster only, the whole body in frame with nothing cropped. Frame it exactly the same way as the other three "
        "views of this set, so they line up when stacked: feet standing on a thin ground line 10% up from the bottom edge, "
        "the top of the comb 12% down from the top edge, the body centred. Orthographic, no perspective, as in an "
        "animation model sheet. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels "
        "and no text.")
GEMINI_TURN = ("Show one rooster only, its whole body in frame. Frame it exactly the same way as the other three views of "
               "this set, so they line up when stacked: its feet stand on a thin ground line 10% up from the bottom edge, "
               "the top of its comb is 12% down from the top edge, and its body is centred. Draw it perfectly flat and "
               "orthographic, like an animation model sheet, lit evenly from the front so nothing casts a shadow, on a "
               "plain light-grey background; the image holds only the rooster, unlabeled.")
GEMINI_GLOBAL_EDITS.append((TURN, GEMINI_TURN))
_ROOSTER_LOOK = ("exactly as designed in the attached B1 model sheet: the same big red comb and wattles, orange-gold neck "
                 "feathers, rust-red body, dark wings, glossy black curved tail and yellow legs, in the same proportions "
                 "and colours")
_CLOSED = ("Its beak is closed: no open mouth, no grin and no crowing, a calm, neutral face with the eyes open. It stands "
           "in a neutral pose, wings folded against its body, both feet flat on the ground a little apart, tail held up "
           "naturally.")
TURNAROUND = [
    dict(id="B11", title="Rooster turnaround: front", file="B11_rooster_front.png", aspect=S, batch=1, attach="A1, B1",
         use="The front view for modelling the rooster in 3D, lined up with B12-B14.",
         prompt=("Turnaround view for 3D modelling: the game's rooster seen exactly from the front, facing the viewer, "
                 + _ROOSTER_LOOK + ". " + _CLOSED + " " + TURN)),
    dict(id="B12", title="Rooster turnaround: back", file="B12_rooster_back.png", aspect=S, batch=1, attach="A1, B1",
         use="The back view for modelling the rooster in 3D, lined up with B11, B13 and B14.",
         prompt=("Turnaround view for 3D modelling: the game's rooster seen exactly from behind, its tail toward the "
                 "viewer and its head facing away, " + _ROOSTER_LOOK + ". The beak is closed and hidden behind the head. "
                 "It stands in a neutral pose, wings folded against its body, both feet flat on the ground a little "
                 "apart, tail held up naturally. " + TURN)),
    dict(id="B13", title="Rooster turnaround: left side", file="B13_rooster_left.png", aspect=S, batch=1,
         attach="A1, B1",
         use="The left side view for modelling the rooster in 3D, lined up with B11, B12 and B14.",
         prompt=("Turnaround view for 3D modelling: the game's rooster seen exactly from its left side, in profile, "
                 "facing left: its beak points to the left edge of the image and its tail to the right, "
                 + _ROOSTER_LOOK + ". " + _CLOSED + " " + TURN)),
    dict(id="B14", title="Rooster turnaround: right side", file="B14_rooster_right.png", aspect=S, batch=1,
         attach="A1, B1",
         use="The right side view for modelling the rooster in 3D, and the way it faces as it runs in the game.",
         prompt=("Turnaround view for 3D modelling: the game's rooster seen exactly from its right side, in profile, "
                 "facing right: its beak points to the right edge of the image and its tail to the left, "
                 + _ROOSTER_LOOK + ". This is its own right side, not a mirrored copy of the left view. " + _CLOSED
                 + " " + TURN)),
]
PROMPTS += TURNAROUND
GEMINI_SHAPES.update({p["id"]: SQUARE for p in TURNAROUND})
for _p in TURNAROUND:
    _p["refined"] = True
for _p in PROMPTS:
    if _p["id"] == "B1":
        _p["use"] = ("The rooster's design, kept the same in every later image. For modelling, use the four separate views "
                     "with the beak closed, B11-B14.")
for _p in TURNAROUND:
    _p["block"] = "piece"  # crisp, no painted haze or dust around the rooster

# ------------------------------------------------------------------ B13, B14 again: clean model-sheet views
# B13 and B14 came back with a painted ground, sky and haze, the legs fading into mist and the comb blurred. Character
# views get a style block without the village setting (which invites scenery), and the prompts insist on sharp legs
# and feet on the line, attaching the good B11 front view as the framing to copy.
CHARACTER_STYLE = PIECE_STYLE.split("Art style:", 1)[1].strip()
CHARACTER_STYLE = "Art style: " + CHARACTER_STYLE
GEMINI_CHARACTER_STYLE = GEMINI_PIECE_STYLE[GEMINI_PIECE_STYLE.index("Render it as"):]
SHARP = ("Everything is drawn sharp and complete, with clean outlines: both yellow legs and all the toes in full, "
         "standing on the line, nothing blurred, faded or in motion, the comb crisp. There is no scenery at all: no "
         "ground, earth, grass, sky, clouds, mist or haze, only the flat light-grey background and the thin ground line, "
         "framed like the attached B11 front view.")
GEMINI_SHARP = ("Draw everything sharp and complete with clean outlines: both yellow legs and all the toes in full, "
                "standing on the line, and the comb crisp, with nothing blurred, faded or in motion. Leave out scenery "
                "entirely, so the image holds only the flat light-grey background and the thin ground line, framed like "
                "the uploaded B11 front view.")
GEMINI_GLOBAL_EDITS.append((SHARP, GEMINI_SHARP))
GEMINI_ROLES["B11"] = "the B11 front view, as the framing and plain background to copy"
for _p in PROMPTS:
    if _p["id"] in {"B11", "B12", "B13", "B14"}:
        _p["block"] = "character"
    if _p["id"] in {"B13", "B14"}:
        _p["attach"] = "A1, B1, B11"
        _p["prompt"] = _p["prompt"].replace(" " + TURN, " " + SHARP + " " + TURN)
REDO.update({
    "B13": "Came out with a painted ground and haze, the legs fading away and the comb blurred: make it again with the "
           "updated prompt, attaching B11.",
    "B14": "Came out with a painted ground and haze, the legs fading away and the comb blurred: make it again with the "
           "updated prompt, attaching B11.",
})
# Character views: no setting or ground in the style either, colours from the character's own sheet.
CHARACTER_STYLE = (CHARACTER_STYLE
                   .replace(" set in a South Indian village", "")
                   .replace("Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed "
                            "walls, paddy green, warm golden light.", "Colours exactly as in the attached model sheet."))
GEMINI_CHARACTER_STYLE = (GEMINI_CHARACTER_STYLE
                          .replace(" set in a South Indian village", "")
                          .replace("The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo "
                                   "and lime-washed walls and paddy green, under warm golden light.",
                                   "Keep the colours exactly as in the uploaded model sheet."))
assert "red-earth" not in CHARACTER_STYLE and "red-earth" not in GEMINI_CHARACTER_STYLE

# ------------------------------------------------------------------ more shandy stalls, so none repeats in view
MORE_STALLS = [
    dict(id="E11", title="Shandy stalls 3", file="E11_shandy_stalls_3.png", aspect=L, batch=1, attach="A1, C4, E2, E8",
         use="More stalls for the market, so no stall comes back within two screens.",
         prompt=("Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the "
                 "same way. Each is wide and low, about 5 m wide and under 3 m tall, its goods spread along the ground: a "
                 "spice and grain seller with heaps of red chillies, turmeric, tamarind and rice in open jute sacks and "
                 "brass measuring pots, under a plain faded turmeric-yellow cotton awning on bamboo poles; a betel-leaf "
                 "and areca-nut seller sitting on a raised wooden plank under a woven palm-leaf umbrella; and a cloth "
                 "seller with folded cotton saris and veshtis piled on a rope cot under a low thatched shade. "
                 + WIDE_FRONTS + " " + CLEAN_BG)),
    dict(id="E12", title="Shandy stalls 4", file="E12_shandy_stalls_4.png", aspect=L, batch=1, attach="A1, C4, E2, E8",
         use="More stalls for the market, so no stall comes back within two screens.",
         prompt=("Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the "
                 "same way. Each is wide and low, about 5 m wide and under 3 m tall: a palm-fruit seller with bunches of "
                 "palmyra fruit and tender nungu in cane baskets under a palm-frond shade; a buttermilk and jaggery "
                 "seller with big clay pots on a stand and blocks of jaggery on banana leaves, under a plain faded "
                 "indigo cotton awning; and a basket weaver with bamboo baskets, winnowing trays and mats stacked high "
                 "around them, under a thatched shade. " + WIDE_FRONTS + " " + CLEAN_BG)),
]
PROMPTS += MORE_STALLS
GEMINI_SHAPES.update({p["id"]: WIDE for p in MORE_STALLS})
GEMINI_ROLES.setdefault("E8", "the E8 shandy stalls, to match how the stalls are drawn and sized")
for _p in MORE_STALLS:
    _p["block"] = "piece"
    _p["refined"] = True

# Enough stalls for an unbroken row: with E11-E14 there are 16 kinds, so stalls can stand side by side, as at a real
# shandy, and none comes back within two screens.
_ALONGSIDE = (" These stalls will stand side by side in a long row with stalls from the other sheets, so each is "
              "complete on its own, its shade and goods inside its own width.")
for _p in PROMPTS:
    if _p["id"] in {"E11", "E12"}:
        _p["prompt"] = _p["prompt"].replace(" " + WIDE_FRONTS, _ALONGSIDE + " " + WIDE_FRONTS)
        _p["use"] = "More stalls, so the market's stalls can stand side by side with none repeating within two screens."
MORE_STALLS_2 = [
    dict(id="E13", title="Shandy stalls 5", file="E13_shandy_stalls_5.png", aspect=L, batch=1, attach="A1, C4, E2, E8",
         use="More stalls, so the market's stalls can stand side by side with none repeating within two screens.",
         prompt=("Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the "
                 "same way. Each is wide and low, about 5 m wide and under 3 m tall: a vegetable seller with heaps of "
                 "brinjals, ladies' fingers, drumsticks, gourds, onions and greens on jute sacks and banana leaves, "
                 "under a plain faded madder-red cotton awning on bamboo poles; a groundnut seller roasting peanuts in "
                 "hot sand in a big iron pan over a clay stove, with paper cones; and a parrot astrologer sitting on a "
                 "mat under a black cloth umbrella, a green parrot in a small cane cage and a fan of fortune cards with "
                 "pictures and no writing." + _ALONGSIDE + " " + WIDE_FRONTS + " " + CLEAN_BG)),
    dict(id="E14", title="Shandy stalls 6", file="E14_shandy_stalls_6.png", aspect=L, batch=1, attach="A1, C4, E2, E8",
         use="More stalls, so the market's stalls can stand side by side with none repeating within two screens.",
         prompt=("Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the "
                 "same way. Each is wide and low, about 5 m wide and under 3 m tall: a sweets and snacks seller with "
                 "trays of murukku, laddus and jalebis and glass jars on a wooden plank, under a plain undyed cotton "
                 "awning; a sugarcane-juice seller with a hand-cranked iron press on a wooden stand, a bundle of "
                 "sugarcane and brass tumblers, under a woven palm-leaf shade; and a seller of korai-grass mats, palm "
                 "brooms and coir rope, rolled and stacked under a low thatched shade." + _ALONGSIDE + " "
                 + WIDE_FRONTS + " " + CLEAN_BG)),
]
PROMPTS += MORE_STALLS_2
GEMINI_SHAPES.update({p["id"]: WIDE for p in MORE_STALLS_2})
for _p in MORE_STALLS_2:
    _p["block"] = "piece"
    _p["refined"] = True

# ------------------------------------------------------------------ still more shandy stalls (E15-E18)
def _stalls(ident, sheet_no, three):
    return dict(id=ident, title=f"Shandy stalls {sheet_no}", file=f"{ident}_shandy_stalls_{sheet_no}.png", aspect=L,
                batch=1, attach="A1, C4, E2, E8",
                use="More stalls, so the market's stalls can stand side by side with none repeating within two screens.",
                prompt=("Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but "
                        "drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall: " + three
                        + _ALONGSIDE + " " + WIDE_FRONTS + " " + CLEAN_BG))


MORE_STALLS_3 = [
    _stalls("E15", 7, "a dried-fish seller with salted fish laid out on palm-leaf mats and in cane baskets, under a low "
                      "thatched shade; a bangle and kumkum seller with wooden racks of glass bangles and brass bowls of "
                      "kumkum, turmeric and sandal paste, under a plain faded indigo cotton awning; and a banana seller "
                      "with whole green and yellow bunches hanging from a bamboo frame, under a palm-frond shade."),
    _stalls("E16", 8, "a cobbler sitting under a big black cloth umbrella with leather sandals and his tools on a mat; "
                      "a village barber's spot under a palm-leaf shade, a small wooden stool, a mirror hung on a pole and "
                      "a brass bowl of water; and a knife and sickle sharpener with a pedal-driven grindstone on a "
                      "wooden frame, blades laid out on a cloth."),
    _stalls("E17", 9, "a salt seller with a white heap of sea salt on a bullock cart, a wooden measure and a sack; a "
                      "cattle-fair seller of brass cattle bells, painted horn caps and coir ropes hung from a bamboo "
                      "frame under a plain undyed cotton awning; and a toy seller with lacquered wooden toys, spinning "
                      "tops, clay whistles and a tall pole of paper windmills, under a palm-leaf shade."),
    _stalls("E18", 10, "an idli and dosa woman with a clay stove, an iron griddle and stacks of banana leaves, under a "
                       "thatched lean-to; a herb and village-medicine seller with dried roots, barks and leaves in cane "
                       "trays and small brass boxes, under a plain faded turmeric-yellow cotton awning; and a pickle "
                       "seller with big glazed stoneware jars (bharanis) and cloth-tied lids on a wooden plank, under a "
                       "woven palm-leaf shade."),
]
PROMPTS += MORE_STALLS_3
GEMINI_SHAPES.update({p["id"]: WIDE for p in MORE_STALLS_3})
for _p in MORE_STALLS_3:
    _p["block"] = "piece"
    _p["refined"] = True

# ------------------------------------------------------------------ more for zone 2: fields and canal (D8-D13)
_FIELD_LOOK = "in the look of the attached D1 painting, a 1970s South Indian farming village"
FIELDS_MORE = [
    dict(id="D8", title="Field buildings 2", file="D8_field_buildings_2.png", aspect=L, batch=1, attach="A1, C4, D1, D5",
         use="More buildings along the far edge of the fields, so none repeats in view.",
         prompt=("Three more structures that stand at the edge of paddy fields, " + _FIELD_LOOK + ", drawn like the "
                 "attached D5 buildings: a kavalai well, a stone well with a sloping earth ramp where a pair of bullocks "
                 "draws up a big leather water bag on a rope over a wooden pulley frame; a farmer's watch platform "
                 "(paran), a small thatched hut raised high on four bamboo poles with a bamboo ladder; and a round "
                 "threshing floor of beaten earth with a stone roller, heaps of paddy straw and a winnowing basket, "
                 "beside a small thatched shed for the plough and tools." + _ALONGSIDE.replace("stalls", "pieces")
                 + " " + WIDE_FRONTS + " " + CLEAN_BG)),
    dict(id="D9", title="Canal pieces", file="D9_canal_pieces.png", aspect=L, batch=1, attach="A1, D1, D3",
         use="Things along the canals: water lifts, a stone bridge, a bathing ghat, so every canal crossing differs.",
         prompt=("Four separate pieces for the irrigation canals, " + _FIELD_LOOK + ", drawn side-on like the "
                 "attached D3 props, each standing on its own short stretch of canal bank: a picottah (etram), a long "
                 "wooden counterpoise pole on a forked post with a clay pot on one end and a stone weight on the other, "
                 "for lifting water from the canal; a narrow bridge of two long granite slabs on stone piers; a few "
                 "stone steps (a ghat) going down into the water, with a flat washing stone and a brass pot; and a "
                 "small wooden shutter sluice set in a brick wall across a channel. " + SHEET_VIEW + " " + CLEAN_BG)),
    dict(id="D10", title="Life in the fields", file="D10_field_life.png", aspect=L, batch=1, attach="A1, B7, B10",
         use="People and animals working the fields in the background, so the fields feel lived in.",
         prompt=("Separate figures for the fields, " + _FIELD_LOOK + ", drawn like the attached B7 animals and B10 "
                 "villagers, side view: a farmer ploughing with two white bullocks and a wooden plough; three women in "
                 "saris bent over transplanting paddy seedlings in a row; a herd boy with a stick and four goats; a "
                 "water buffalo wallowing in mud up to its back with an egret on it; a duck herder with a long bamboo "
                 "stick and a flock of ducks; and a farmer carrying a bundle of paddy sheaves on his head. "
                 + SHEET_VIEW + " " + CLEAN_BG)),
    dict(id="D11", title="Field trees and plants", file="D11_field_trees.png", aspect=L, batch=1, attach="A1, D4, H1",
         use="Trees and bushes that grow along field bunds and canals, so the far edge of the fields never repeats.",
         prompt=("Separate trees and plants that grow along field bunds and canals, " + _FIELD_LOOK + ", drawn like "
                 "the attached D4 and H1 trees, side view: a lone banyan with hanging aerial roots; a thorny babul "
                 "(karuvelam) tree; a tall clump of bamboo; a screwpine (thazhai) bush with long spiky leaves at the "
                 "water's edge; a row of young casuarina trees; and a hedge of agave and cactus. " + SHEET_VIEW + " "
                 + CLEAN_BG)),
    dict(id="D12", title="More crops", file="D12_more_crops.png", aspect=L, batch=1, attach="A1, D1, D6",
         use="More crops to plant field by field, so each field looks different.",
         prompt=("Separate horizontal strips of crops for building fields, " + _FIELD_LOOK + ", drawn like the "
                 "attached D6 strips, each a long low strip seen from the side: a seedbed of dense, bright green paddy "
                 "seedlings in water; a harvested field with stubble and sheaves of paddy stacked in small heaps; tall "
                 "sorghum (cholam) with heavy seed heads; low groundnut plants in rows; cotton plants with white bolls; "
                 "and a strip of banana plants. " + SHEET_VIEW + " " + CLEAN_BG)),
    dict(id="D13", title="Fields middle layer 2", file="D13_fields_mid_layer_2.png", aspect=L, batch=1,
         attach="A1, C8, D1, D7",
         use="A second band of distant fields, so the one behind the fields doesn't repeat.",
         prompt=("Middle parallax layer for the fields, different from the attached D7 band: in front, a long low "
                 "earthen bund with grass; behind it, golden ripe paddy, a few haystacks, a small hamlet of thatched "
                 "huts under coconut palms, a canal with a granite slab bridge, a herd of grazing cattle and a line of "
                 "palmyra palms, in the light of the attached D1 painting and a little paler than the foreground, as "
                 "if a few hundred metres away. " + BAND)),
]
PROMPTS += FIELDS_MORE
GEMINI_SHAPES.update({p["id"]: SIXTEEN for p in FIELDS_MORE})
GEMINI_SHAPES.update({"D8": WIDE, "D13": WIDE})
GEMINI_SIDE_ON.add("D13")
GEMINI_ROLES.update({
    "D3": "the D3 field props, to match how they are drawn",
    "D5": "the D5 field buildings, to match how they are drawn and sized",
    "D6": "the D6 crop strips, to match how the strips are drawn",
    "D7": "the D7 fields band, to match its style (but show a different stretch)",
    "B10": "the B10 villagers, to match how people are drawn",
})
for _p in FIELDS_MORE:
    _p["block"] = "piece"
    _p["refined"] = True
# D8 holds a tall watch platform, so it uses the plain front-on sheet wording, not "wide and low".
for _p in FIELDS_MORE:
    if _p["id"] == "D8":
        _p["prompt"] = _p["prompt"].replace(_ALONGSIDE.replace("stalls", "pieces") + " " + WIDE_FRONTS,
                                            " Each piece complete on its own, with a clear gap between them. " + FRONTS_SHEET)
        assert "wide and low" not in _p["prompt"]

# ------------------------------------------------------------------ second round of D and E sheets: what came back wrong
# D9 came back as cut-away blocks of earth seen from above at an angle, with blurred water under them; E17 and E18 came
# back as whole market scenes of many small stalls (one of them striped). Their prompts now say so plainly.
_EXACTLY_THREE = (" Exactly these three stalls and nothing else: not a market scene, no other stalls, no crowd; each "
                  "one big, with at most its one seller.")
for _p in PROMPTS:
    if _p["id"] in {"E17", "E18"}:
        _p["prompt"] = _p["prompt"].replace(_ALONGSIDE, _EXACTLY_THREE + _ALONGSIDE)
    if _p["id"] == "D9":
        _p["prompt"] = _p["prompt"].replace(
            "drawn side-on like the attached D3 props, each standing on its own short stretch of canal bank:",
            "each drawn exactly from the side as a flat elevation, like the attached D3 props: no cut-away block of "
            "earth, no view from above, no water drawn under it, each standing on one thin ground line:")
        assert "cut-away" in _p["prompt"]
REDO.update({
    "D9": "Came out as cut-away blocks of earth seen from above at an angle, with blurred water under them: make it "
          "again with the updated prompt, each piece flat and side-on on a ground line.",
    "E17": "Came out as a whole market of many small stalls (one with a striped awning): make it again with the updated "
           "prompt, exactly three big stalls.",
    "E18": "Came out as a whole market of many small stalls (one with a striped awning): make it again with the updated "
           "prompt, exactly three big stalls.",
})

# ------------------------------------------------------------------ M: textures for the 3D kid, rooster and pickups
# The kid, the rooster and the pickups are now 3D models (built in Blender, toon-shaded with outlines, as the design doc
# first planned). Their shapes come from the A0 and B11-B14 turnarounds; these images give them their painted surfaces.
SECTIONS.append(("M", "3D model textures", "Painted surfaces for the 3D kid, rooster and pickups. The models are "
                 "already built in flat colours; each image swaps in on its own as it arrives."))
_FLAT_FRONT = ("Seen exactly straight on, filling the square, even flat lighting with no shading, shadows, highlights "
               "or folds, so it can be wrapped around a 3D model.")
MODEL_TEXTURES = [
    dict(id="M1", title="Kid's faces", file="M1_kid_faces.png", aspect=S, batch=1, attach="A0, A1", block="character",
         use="Painted onto the 3D kid's face: neutral while she runs, a grin when she grabs the rooster, shocked when "
             "she stumbles, straining on a vault or climb.",
         prompt=("Four faces of the game's toddler hero from the attached A0 sheet (her front view), in a 2 by 2 grid of equal squares: "
                 "top left neutral and determined, top right a big open grin, bottom left shocked with round eyes and an "
                 "open mouth, bottom right straining with eyes squeezed and teeth gritted. Each face seen exactly from the "
                 "front, centred in its square and the same size, showing only the face on her warm brown skin: eyes, "
                 "eyebrows, nose, mouth and cheeks, with no hair, ears, hairband or neck, and the skin colour running to the "
                 "edges of each square. Even flat lighting, no shading on the face, clean dark outlines on the features. "
                 "Plain, no background.")),
    dict(id="M2", title="Frock silk", file="M2_frock_silk.png", aspect=S, batch=1, attach="A0, A1", block="texture",
         use="The 3D kid's frock: the body of the skirt, bodice and sleeves.",
         prompt=("A texture of the peacock-blue pattu silk of the kid's frock in the attached A0 sheet: a soft silk sheen "
                 "painted in two or three close blues, with tiny gold zari dots (butis) scattered evenly. "
                 + _FLAT_FRONT + " " + TILE)),
    dict(id="M3", title="Zari border", file="M3_zari_border.png", aspect=L, batch=1, attach="A0, A1", block="texture",
         use="The wide band at the hem of the 3D kid's frock, and the gold edging of the neckline and sleeves.",
         prompt=("A long woven border band from the hem of the kid's frock in the attached A0 sheet, filling the whole "
                 "image: magenta silk with gold zari, a row of small temple-tower motifs between two thin gold lines. "
                 "Seen straight on, perfectly flat and even, no folds or shading. The pattern repeats seamlessly from the "
                 "left edge to the right edge; the top and bottom edges are the band's own straight gold edges.")),
    dict(id="M4", title="Hair", file="M4_hair.png", aspect=S, batch=1, attach="A0, A1", block="texture",
         use="The 3D kid's shoulder-length wavy black hair.",
         prompt=("A texture of the kid's glossy black wavy hair from the attached A0 sheet: soft waves of strands all "
                 "running top to bottom, painted in near-black and deep blue-brown with a few soft lighter strokes. "
                 + _FLAT_FRONT + " " + TILE)),
    dict(id="M5", title="Leopard hairband", file="M5_leopard_print.png", aspect=S, batch=1, attach="A0, A1", block="texture",
         use="The 3D kid's hairband.",
         prompt=("A texture of the leopard print of the kid's hairband in the attached A0 sheet: golden-yellow fabric with "
                 "brown and black rosettes, drawn with clean painted edges. " + _FLAT_FRONT + " " + TILE)),
    dict(id="M6", title="Rooster body feathers", file="M6_rooster_body.png", aspect=S, batch=1, attach="B1, B11, A1",
         block="texture",
         use="The 3D rooster's body, back and wings.",
         prompt=("A texture of the rooster's body plumage from the attached B1 sheet: overlapping rows of rounded "
                 "deep red-chestnut feathers, each with a slightly darker edge, like scales, all pointing the same way "
                 "(down the image). " + _FLAT_FRONT + " " + TILE)),
    dict(id="M7", title="Rooster neck hackles", file="M7_rooster_hackles.png", aspect=S, batch=1, attach="B1, B11, A1",
         block="texture",
         use="The 3D rooster's neck and the saddle feathers over its back.",
         prompt=("A texture of the rooster's neck hackles from the attached B1 sheet: long, narrow, pointed feathers in "
                 "glowing orange-gold with lighter golden tips, layered and all flowing downward. " + _FLAT_FRONT + " "
                 + TILE)),
    dict(id="M8", title="Rooster tail feathers", file="M8_rooster_tail.png", aspect=S, batch=1, attach="B1, B11, A1",
         block="texture",
         use="The 3D rooster's sickle tail feathers.",
         prompt=("A texture of the rooster's tail feathers from the attached B1 sheet: long glossy black feathers side by "
                 "side running top to bottom, with an iridescent green and blue-violet sheen along their middles. "
                 + _FLAT_FRONT + " " + TILE)),
    dict(id="M9", title="Mango skin", file="M9_mango_skin.png", aspect=S, batch=1, attach="A1", block="texture",
         use="The 3D mangoes the kid collects.",
         prompt=("A texture of ripe Alphonso mango skin: warm golden yellow blending into orange and a soft red blush, "
                 "with tiny pale speckles and a gentle painted sheen. " + _FLAT_FRONT + " " + TILE)),
    dict(id="M10", title="Golden tail feather", file="M10_tail_feather.png", aspect=S, batch=1, attach="B1, A1", block="piece",
         use="The hidden tail feather pickup: a card on the 3D feather.",
         prompt=("One single long curved tail feather from the rooster in the attached B1 sheet, lying flat and seen "
                 "straight on, its quill at the bottom and its tip curving up to the top right, filling the square: glossy "
                 "black-green at the tip shading to orange-gold and russet near the quill. Clean dark outline, flat even "
                 "light, no shadow. " + CLEAN_BG)),
]
PROMPTS += MODEL_TEXTURES
GEMINI_SHAPES.update({p["id"]: SQUARE for p in MODEL_TEXTURES})
GEMINI_SHAPES["M3"] = SIXTEEN
for _p in MODEL_TEXTURES:
    _p["refined"] = True

# ------------------------------------------------------------------ the festival: the village is celebrating Pongal
# Every new image is made for the festival; the images already made get edited for it (pongal.py, section P).
FESTIVE = ("The village is celebrating Pongal, the harvest festival: mango-leaf thoranams over the doors, marigold "
           "garlands, coloured kolams, tall sugarcane stalks, new clay Pongal pots boiling over on brick hearths, "
           "cattle with painted horns and bells, bunting and kites, everyone in new clothes.")
GEMINI_FESTIVE = ("The village is celebrating Pongal, the harvest festival, with mango-leaf thoranams over the doors, "
                  "marigold garlands, coloured kolams, tall sugarcane stalks, new clay Pongal pots boiling over on brick "
                  "hearths, cattle with painted horns and bells, bunting and kites, and everyone in new clothes.")
STYLE = STYLE.replace(ERA, ERA + " " + FESTIVE)
PIECE_STYLE = PIECE_STYLE.replace(ERA, ERA + " " + FESTIVE)
GEMINI_STYLE = GEMINI_STYLE.replace(GEMINI_ERA, GEMINI_ERA + " " + GEMINI_FESTIVE)
GEMINI_PIECE_STYLE = GEMINI_PIECE_STYLE.replace(GEMINI_ERA, GEMINI_ERA + " " + GEMINI_FESTIVE)
