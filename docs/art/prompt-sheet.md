# Chicken Runner — art prompt sheet

Image prompts for ChatGPT, written for the Blender pipeline: every image has an ID, a file name and a shape, so the images come back named for the scenes they feed. The web version has copy buttons and a checklist. Gemini versions of the same prompts, with the same IDs and file names, are in [prompt-sheet-gemini.md](prompt-sheet-gemini.md).

**Progress:** 42 of 78 images are in `ArtSource/references/` (checked 22 Nov 2026); 26 of the 45 first-batch images. First batch still to make: B8, B9, C8, C10, G1, G2, G3, G7, G8, G9, G12, G13, G15, H1, H4, H6, H7, T11, T12.

## How to use it

1. Make **A0** first, in a new ChatGPT chat, attaching your four kid turnaround images. Then make **A1**, attaching A0 and your rooster photo.
2. Stay in that chat for the rest. Each prompt below is copy-ready: it asks ChatGPT to match A1 and carries the style rules. Attach the files listed under *Attach* (A0 is the kid reference from now on).
3. Save each image with the file name shown.
4. Put the images in the repo at `ArtSource/references/` (or upload them in the chat), in batches, starting with the 45 marked *first batch*.

Regenerate an image when words or labels appear in it, when a model sheet is not side-on and orthographic, or when the background is not plain.

## A. Style anchors

Make these first, in order. A0 fixes the kid's design in the pattu frock, A1 sets the look, and every later prompt matches both.

### A0 · Kid in a pattu frock

✅ in the repo · Save as `A0_kid_pattu_frock_sheet.png` · Landscape 3:2 · first batch · Attach: your four kid turnaround images  
Used for: The kid's design for every later image, and the sheet I model and rig the kid from in Blender.

```text
Landscape 3:2 image.

Character model sheet for 3D modelling of the game's toddler hero, based on the four attached reference images (front, back and both side views). Keep the face, skin tone, shoulder-length wavy black hair, leopard-print hairband and chubby toddler proportions exactly as in the references, but change the outfit: replace the T-shirt, shorts, socks and sneakers with a vintage South Indian pattu frock, like one from a 1980s family photo. It is a knee-length silk frock in peacock blue with a wide contrasting border at the hem in magenta and gold zari, woven with a small temple-tower pattern; a fitted bodice with a gold zari neckline; short puffed sleeves edged in gold; and a gently gathered, flared skirt with a soft silk sheen. Bare feet with silver anklets with tiny bells. Show four views side by side at exactly the same scale and height: front, left side, right side and back, standing in a relaxed A-pose with the arms a little away from the body. Orthographic, no perspective. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### A1 · Key art

✅ in the repo · Save as `A1_key_art.png` · Landscape 3:2 · first batch · Attach: A0, your rooster reference photo  
Used for: Sets the look every other image matches, and my reference for materials and lighting in Blender.

```text
Landscape 3:2 image.

Key art for the game. Side-on view of a narrow South Indian village lane in late-afternoon golden light. A small, determined toddler (drawn exactly like the attached A0 model sheet: wavy black hair, a leopard-print hairband, a peacock-blue silk pattu frock with a magenta-and-gold border swishing as they run, bare feet with silver anklets) sprints from left to right after a smug country rooster (red comb, orange neck feathers, glossy black tail, like the attached rooster photo) who glances back over his shoulder mid-stride. Around them: flat-roofed houses washed in lime-white, indigo and turmeric, white kolam patterns at the doorsteps, a stack of clay pots, a hand pump with a puddle, a rope cot where a sleepy neighbour is just waking up, a tulsi planter, coconut palms and a distant temple tower in warm haze. Dust kicked up by little feet, a few loose feathers in the air, long soft shadows. The kid is on the left third, the rooster on the right.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### A2 · Colour script

✅ in the repo · Save as `A2_colour_script.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: The lighting plan across the nine levels: one Blender lighting setup per zone.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A colour script for the whole game: nine small painted panels in a 3 by 3 grid, read left to right and top to bottom, all side-on views of one chase through a South Indian village as the day goes by. Panels 1 to 3: a village lane in warm late afternoon. Panels 4 to 6: paddy fields, an irrigation canal and mango trees at golden hour, the light turning orange. Panel 7: flat rooftops with drying red chillies at sunset. Panel 8: a weekly market at dusk with marigold garlands and glowing lanterns. Panel 9: temple steps at blue dusk lit by rows of small oil lamps. Simple shapes, all about light and colour, with tiny silhouettes of a toddler in a swishing blue silk frock chasing a rooster in every panel.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## B. Characters

Model sheets and pose sheets. Attach your kid reference art and rooster photo where noted.

### B1 · Rooster model sheet

✅ in the repo · Save as `B1_rooster_model_sheet.png` · Landscape 3:2 · first batch · Attach: A1, your rooster reference photo  
Used for: Traced in Blender to model the rooster at the right proportions.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character model sheet of the game's rooster for 3D modelling, based on the attached rooster photo: a proud country rooster with a big red comb and wattles, orange-gold neck feathers, a rust-red body, dark wings, a glossy black curved tail and yellow legs. Four views side by side at exactly the same scale and height: left side view, front view, back view and top view, standing in a neutral pose. Orthographic, no perspective. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B2 · Rooster pose sheet

✅ in the repo · Save as `B2_rooster_poses.png` · Landscape 3:2 · first batch · Attach: A1, B1  
Used for: Key poses for the rooster's run, flutter, taunt, panic and wriggle animations.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Pose sheet for the same rooster as the attached model sheet, all in side view facing right, evenly spaced at the same scale on a plain flat light-grey background: 1) running with one leg forward; 2) running with the other leg forward; 3) fluttering up with wings spread and feet tucked; 4) the smug taunt, turned back to face left, chest puffed out, head thrown back, crowing; 5) panic sprint, eyes wide, feathers flying off; 6) wriggling free upside down, flapping wildly; 7) pecking at the ground; 8) standing proud on one foot. Funny, expressive body language: slapstick, never hurt.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B3 · Kid gameplay poses

✅ in the repo · Save as `B3_kid_poses_gameplay.png` · Landscape 3:2 · first batch · Attach: A1, A0  
Used for: Key poses for the nine first-prototype animations on your kid model.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Pose sheet for the toddler hero, keeping the design exactly as in the attached A0 model sheet (wavy black hair, leopard-print hairband, peacock-blue pattu frock with a magenta-and-gold border, bare feet with silver anklets). All side view facing right, same scale, plain flat light-grey background: 1) running, contact pose; 2) running, passing pose; 3) jumping up with arms raised; 4) falling with arms flailing; 5) landing in a squat; 6) sliding feet first on their back; 7) vaulting a low wall with both hands on top; 8) stumbling forward, off balance; 9) diving flat out with arms stretched to grab. Let the frock's skirt flare and trail with each motion.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B4 · Kid story poses and faces

✅ in the repo · Save as `B4_kid_story_and_faces.png` · Landscape 3:2 · first batch · Attach: A1, A0  
Used for: The four face expressions and the story-animation poses.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Second pose sheet for the same toddler, exactly as in the attached A0 model sheet, barefoot with silver anklets. Top row, four face close-ups: neutral, big cheeky grin, shocked with mouth open, straining with cheeks puffed. Bottom row, full body side views facing right: tiptoeing with exaggerated sneaky steps; lifting a big bamboo basket with both hands, straining; a startled jump; carrying a rooster proudly in both arms; cheering with fists up; sulking with arms crossed. Plain flat light-grey background, even lighting.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B5 · Neighbour

✅ in the repo · Save as `B5_neighbour_sheet.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Modelled for the basket intro: asleep on the cot, then waking with a shout.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character sheet for the sleepy neighbour: a friendly middle-aged village man with a bushy moustache, a white cotton vest and a checked lungi, a little round in the middle. Left: front view and side view standing, same scale, for 3D modelling. Right: napping on a rope cot with one arm over his face, then waking up mid-shout with one arm raised, pointing. Comic and warm, never mean. Plain flat light-grey background, even lighting.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B6 · Amma

✅ in the repo · Save as `B6_amma_sheet.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled for the final kitchen scene.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character sheet for Amma, the toddler's mother: a warm, kind woman in her thirties wearing a cotton saree in turmeric and indigo, hair in a bun with jasmine flowers, glass bangles. Left: front view and side view standing, same scale, for 3D modelling. Right: three expressions, surprised with a hand on her cheek, laughing, and a stern raised eyebrow with hands on hips. Dignified and loving. Plain flat light-grey background, even lighting.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B7 · Village animals

✅ in the repo · Save as `B7_animals_sheet.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The sleeping dog, hens, buffalo and bullocks that become obstacles and scenery.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Sheet of village animals in side view facing right, at the same scale relative to each other, on a plain flat light-grey background: a street dog asleep curled in the dust; the same dog woken up and barking; three hens pecking; a water buffalo lying in a mud patch; a pair of white bullocks standing. Friendly cartoon proportions.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B8 · Cows and goats

⬜ to make · Save as `B8_cows_goats.png` · Landscape 3:2 · first batch · **new** · Attach: A1, B7  
Used for: More animals, so the same one never appears twice in view.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Village livestock, drawn like the attached B7 animal sheet: a white cow with painted horns and a bell, a brown calf, a goat standing on a low wall, a goat eating leaves, a black goat kid jumping, and a buffalo standing. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B9 · Small animals and birds

⬜ to make · Save as `B9_small_animals.png` · Landscape 3:2 · first batch · **new** · Attach: A1, B7  
Used for: Life on walls and rooftops: cats, crows, parrots, hens with chicks.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Small village animals and birds, drawn like the attached B7 animal sheet: a cat asleep on a wall, three crows on a ledge, a pair of green parrots, a mother hen with five chicks, two white ducks, a peacock with its tail folded, and a striped palm squirrel. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B10 · Villagers in the background

⬜ to make · Save as `B10_villagers.png` · Landscape 3:2 · second batch · **new** · Attach: A1  
Used for: People going about their day behind the chase.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Background villagers going about their day, drawn simply and warmly in the game's style: a woman drawing a kolam, an old man sitting on a veranda with a walking stick, a man riding a bicycle with a milk can, two kids rolling a tyre with a stick, a woman carrying a water pot on her head, and a vegetable seller with a push cart. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## C. Zone 1: the lane

Levels 1 to 3. Painted houses, verandas, kolam, pots, cots and clotheslines.

### C1 · Lane mood painting

✅ in the repo · Save as `C1_lane_mood.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: The target for the zone 1 Blender scene: layout, lighting and atmosphere.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting of the village lane, side-on like a side-scrolling game level, no characters. A packed red-earth lane runs left to right. Flat-roofed houses in lime-white, indigo, turmeric and pale pink with verandas and pillars, wooden doors with mango-leaf garlands, white kolam patterns at each doorstep. Stacked clay pots, a hand pump with a puddle, a rope cot, a bicycle leaning on a wall, a tulsi planter, a clothesline of bright sarees and bamboo ladders up to the rooftops. Behind: coconut palms, then a distant temple tower and hills fading into warm haze. Late afternoon: long shadows across the lane, light shafts through the palms, dust in the air.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C2 · Lane far layer

✅ in the repo · Save as `C2_lane_far_layer.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: A painted card at the back of the scene, scrolling slowest.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Far background layer for parallax scrolling, with no foreground and no ground: a late-afternoon sky with soft painterly clouds, low hills and a distant South Indian temple tower in silhouette, a few faraway coconut palms, all fading into warm golden haze toward the bottom. Wide and calm, so it can repeat sideways.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C3 · Lane middle layer

✅ in the repo · Save as `C3_lane_mid_layer.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: A cut-out card between the far layer and the play lane. Magenta is keyed out.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer, side-on: a row of coconut palms, banana plants and the backs of distant village houses with tiled and flat roofs, a little hazy and lower in contrast than a foreground would be. Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C4 · House kit elevations

✅ in the repo · Save as `C4_house_kit_elevations.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Traced to build the modular house kit: walls, verandas, parapets, doors and ladder.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Modular building kit for 3D modelling: four flat-roofed South Indian village house fronts seen straight on (front elevation, orthographic, no perspective), standing side by side on one baseline. One narrow, in lime-white. One wide, in indigo, with a shaded veranda and two pillars. One in turmeric with a small barred window and a raised sit-out platform by the door. One pale pink with steps up to the door. Each has a low parapet along the roof edge, a wooden door and a painted band at the base. A bamboo ladder leans on one wall. Even flat lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C5 · Lane props, sheet 1

✅ in the repo · Save as `C5_lane_props_a.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Modelled as the zone 1 obstacles and set dressing.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet for 3D modelling, every object in side view at the same scale, evenly spaced on a plain flat light-grey background, even lighting: a stack of three clay pots; a flat cow-dung patty; an iron hand pump with a small puddle; a wooden rope cot with a woven top; an old black bicycle; a tulsi planter on a small painted pedestal; a pair of brass water pots. Hazards (pots, dung, puddle) in warm colours with dark outlines; the helpful cot has a slight glint.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C6 · Lane props, sheet 2

✅ in the repo · Save as `C6_lane_props_b.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: The bullock cart, clothesline and the bamboo basket from the intro.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Second prop sheet, side view, same scale, plain flat light-grey background, even lighting: a bullock cart with big wooden wheels; a clothesline on two bamboo poles with two bright sarees hanging; an upturned dome-shaped bamboo chicken basket; a pile of jute sacks; a wooden doorway with a mango-leaf garland across the top; a small roadside shrine stone with a marigold garland; a clay water pot on a stand.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C7 · Kolam decals

✅ in the repo · Save as `C7_kolam_decals.png` · Square 1:1 · first batch · Attach: A1  
Used for: Cut out as decals for doorsteps and the lane.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Six different kolam floor designs seen straight from above, drawn in clean white rice-flour lines with a few accents in turmeric, kumkum red and green, arranged in a 3 by 2 grid with space between them, on a solid flat dark-grey background so they can be cut out. Simple, bold, hand-drawn lines.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C8 · Lane middle layer 2

⬜ to make · Save as `C8_lane_mid_layer_2.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C3  
Used for: A second distance layer, so the palm band does not repeat.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer, side-on, a different stretch from the attached C3 layer: a band of terracotta-tiled roofs and banana groves with a white overhead water tank and a few tall palms, a little hazy. Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C9 · Lane middle layer 3

⬜ to make · Save as `C9_lane_mid_layer_3.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C3  
Used for: A third distance layer.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer, side-on, different again from the attached C3 layer: big neem and tamarind trees over thatched roofs, a rocky hillock with a tiny white shrine on top and a line of palms. Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C10 · Ground details to scatter

⬜ to make · Save as `C10_ground_details.png` · Landscape 3:2 · first batch · **new** · Attach: A1, T1  
Used for: Scattered one by one over the lane, each at a random turn and size, so the ground never repeats.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A sheet of separate ground details for a red-earth village lane, each one seen straight down and drawn in the game's painted style: a few pebbles of different sizes, a small cluster of pebbles, three dry mango leaves, a broken piece of dry coconut frond, a coconut husk, a few twigs, four small grass tufts, two weeds with tiny yellow flowers, a short stretch of bullock-cart wheel rut, a trail of bare child footprints, cow hoof prints, hen footprints, and a patch of dried, cracked mud. Spaced apart so none touch. Plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## D. Zone 2: fields and canal

Levels 4 to 6. Paddy fields, bunds, the canal, haystacks and mango trees.

### D1 · Fields mood painting

✅ in the repo · Save as `D1_fields_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for the zone 2 Blender scene.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting, side-on like a side-scrolling game level, no characters: emerald paddy fields with mirror-like water between the rows, a raised earthen bund path running left to right, an irrigation canal crossed by a narrow plank bridge, conical haystacks, a big mango tree with low climbable branches, tall palms, a stone well with a pulley, a scarecrow with a painted clay-pot head and white egrets in the water. Golden hour: the light turning orange, long reflections in the water, soft mist over the far fields.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D2 · Fields far layer

✅ in the repo · Save as `D2_fields_far_layer.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The back card for zone 2.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Far parallax layer with no foreground and no ground: a golden-hour sky with glowing clouds, distant blue hills, lines of palm trees across faraway fields and a flock of birds, all fading into warm haze at the bottom. Calm, so it can repeat sideways.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D3 · Fields props

✅ in the repo · Save as `D3_fields_props.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled as the zone 2 obstacles: haystack, canal and plank bridge, well.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet for 3D modelling, side view, same scale, plain flat light-grey background, even lighting: a conical haystack; a short stretch of irrigation canal with a narrow wooden plank bridge; a round stone well with a wooden pulley and rope; a scarecrow with a painted clay-pot head and an old shirt; a small canal sluice gate; a section of earthen bund path with grass along its edges.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D4 · Mango tree

✅ in the repo · Save as `D4_mango_tree.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled with the branch route the kid climbs for mangoes.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Model sheet of a big old mango tree for a platform game: side view on the left, front view on the right, same scale. A thick twisted trunk, two strong low branches that form a walkable route, dense dark-green leaves and ripe mangoes that glint. Orthographic, even flat lighting, plain flat light-grey background.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## E. Zone 3: terraces and market

Levels 7 to 9. Rooftops at sunset, the market at dusk and the lamp-lit temple steps.

### E1 · Rooftops mood painting

✅ in the repo · Save as `E1_rooftops_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for levels 7 and the rooftop stretches.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting, side-on like a side-scrolling game level, no characters: a run of connected flat village rooftops at sunset with small gaps between the houses, low parapets, black cylindrical water tanks, red chillies and round papads drying on woven mats, a clothesline, a bamboo ladder, paper kites in the sky and festival bunting strung between houses. The setting sun rims everything in orange and the sky shifts from gold to rose.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E2 · Market mood painting

✅ in the repo · Save as `E2_market_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for level 8, the market day.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting, side-on like a side-scrolling game level: a weekly village market at dusk, a row of stalls with striped cloth awnings at different heights, heaps of vegetables, brass and steel vessels, flower sellers with marigold and jasmine garlands, hens in woven baskets, hanging lanterns starting to glow and a busy crowd as soft silhouettes in the background.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E3 · Temple steps

✅ in the repo · Save as `E3_temple_steps_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for level 9, the final catch.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting for the final level, side-on: wide stone temple steps rising from left to right toward a tall carved temple tower, rows of small clay oil lamps flickering along every step, brass bells, marigold garlands and festival bunting, a big old banyan tree to one side. Blue dusk turning to night, warm lamp light pooling on the stone, a few stars. Magical and calm.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E4 · Rooftop props

✅ in the repo · Save as `E4_rooftop_props.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled as the zone 3 rooftop obstacles and dressing.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a black cylindrical plastic water tank on a low stand; a section of rooftop parapet wall with a gap; a woven mat of red chillies drying; a woven mat of round papads; a paper kite with a tail; a string of triangular festival bunting.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E5 · Market and temple props

✅ in the repo · Save as `E5_market_props.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled as the bouncy awnings, stalls and lamp-lit steps.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a market stall with a striped cloth awning in two versions, one high and one low; a flower stall with marigold garlands; a woven basket of vegetables; a stack of brass vessels; a woven basket with two hens; a hanging lantern; a stone temple step segment with three clay oil lamps.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## F. Story frames and screens

The opening story, the wriggle-free gag, the loss screen and Amma's kitchen.

### F1 · Title screen

✅ in the repo · Save as `F1_title_screen.png` · Landscape 3:2 · second batch · Attach: A1, A0  
Used for: Staged in Blender as the title screen, with room for the logo.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Title screen illustration with empty space at the top centre for a logo: the toddler hero (as in the attached A0 model sheet, in the peacock-blue pattu frock) peeks mischievously from behind a low wall at an upturned bamboo basket in a neighbour's yard, and a rooster's beady eye looks back through the gaps in the weave. Late afternoon, warm light, kolam on the ground. The toddler is barefoot, with silver anklets.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F2 · Story 1: the craving

✅ in the repo · Save as `F2_story_craving.png` · Landscape 3:2 · first batch · Attach: A1, A0  
Used for: Storyboard for the opening shot of the intro cutscene.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The craving: the toddler sits on the doorstep of home, nose in the air and eyes closed in bliss, as a ribbon of curry aroma, drawn as swirling golden steam with tiny spice specks, drifts over the wall from the neighbour's kitchen window. Warm afternoon. Wordless storytelling. The toddler is barefoot, with silver anklets.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F3 · Story 2: the plan

✅ in the repo · Save as `F3_story_plan.png` · Landscape 3:2 · first batch · Attach: A1, A0, B5  
Used for: Storyboard and layout for the yard where the basket intro is played.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The plan: the neighbour's yard seen side-on, three upturned bamboo baskets with roosters under them, the neighbour snoring on a rope cot under a tree, and the toddler tiptoeing in on bare feet with exaggerated sneaky steps, tongue out in concentration, wincing as the bells on their silver anklets jingle. Dappled afternoon light.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F4 · Story 3: the basket

✅ in the repo · Save as `F4_story_basket.png` · Landscape 3:2 · first batch · Attach: A1, A0  
Used for: Storyboard for the hold-to-lift moment.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The basket: a close side view of the toddler slowly lifting a big bamboo basket with both hands, straining; under the rim, the rooster's head and one suspicious eye peek out. Tense and funny, with soft light falling through the basket weave. The toddler is barefoot, with silver anklets.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F5 · Story 4: the escape

✅ in the repo · Save as `F5_story_escape.png` · Landscape 3:2 · first batch · Attach: A1, A0, B5  
Used for: Storyboard for the moment the chase begins.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The escape: the rooster bursts out from under the basket in an explosion of feathers, wings wide, while the toddler falls back in surprise and the neighbour sits bolt upright on his cot, shouting and pointing. Dust, feathers and slapstick energy. The toddler is barefoot, with silver anklets.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F6 · Wriggle-free gag

✅ in the repo · Save as `F6_story_wriggle_free.png` · Landscape 3:2 · second batch · Attach: A1, A0  
Used for: Storyboard for the gag at the end of levels 1 to 8.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Gag frame: the toddler dives flat out and lands belly-down in the dust with hands closed on nothing, while the rooster pops out of their grip and flutters away overhead looking smug, a single feather floating down onto the toddler's head. The toddler is barefoot, with silver anklets.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F7 · Rooster escaped

⬜ to make · Save as `F7_rooster_escaped.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Staged in Blender as the loss screen.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Loss screen illustration: the rooster stands on a rooftop parapet against a sunset sky, chest out, crowing in triumph; far below, a tiny toddler looks up with hands on hips. The toddler is barefoot, with silver anklets.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F8 · Story 6: Amma's kitchen

⬜ to make · Save as `F8_story_amma_kitchen.png` · Landscape 3:2 · second batch · Attach: A1, A0, B6  
Used for: Storyboard for the final scene. It stops at the handover, as the design doc's risk table asks.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Final story frame, Amma's kitchen: a warm, lamp-lit village kitchen with a clay stove, brass and steel vessels on shelves and strings of dried chillies. The toddler proudly holds up the rooster in both arms to Amma, who looks down with surprise and a smile. Golden evening light through a small window. The toddler is barefoot, with silver anklets. Nothing shown beyond this moment.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## G. Village buildings

One building per image, so every house on a street can be different. Huts, mud and tin houses, the village head's house, shops and landmarks, all at the C4 scale.

### G1 · Thatched hut

🔁 make again: Came out three-quarter on, showing a side wall: make it again as a straight front view. · Save as `G1_thatched_hut.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house, and the model for huts built in Blender.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A small mud hut with walls smoothed in red-brown earth and a band of white lime at the base, a steep palm-leaf thatch roof hanging low over the walls, a short wooden door you would duck through, a tiny window with a wooden shutter, a clay pot by the door and a pumpkin vine climbing over the thatch. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G2 · Hut with a bamboo porch

🔁 make again: Came out three-quarter on, showing a side wall: make it again as a straight front view. · Save as `G2_hut_bamboo_porch.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house with a porch the kid can run under.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A thatched mud hut with a lean-to porch of bamboo poles and a woven palm-mat roof in front, a rope cot under the porch, firewood stacked against the wall and round cow-dung cakes drying in rows on the side wall. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G3 · Orange mud house, tin roof

🔁 make again: Came out three-quarter on, showing a side wall: make it again as a straight front view. · Save as `G3_mud_house_tin_roof.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house; also the model for tin-roof houses built in Blender.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A narrow one-room house with walls plastered in orange ochre mud, a corrugated tin-sheet roof sloping to one side and weighed down with stones and an old tyre, rust streaks on the tin, a blue-painted wooden plank door, and a small window with a plank shutter propped open on a stick. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G4 · Plank and sheet house

✅ in the repo · Save as `G4_plank_sheet_house.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house that breaks up the painted rows.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A patched-together house of weathered wooden planks and corrugated sheets in faded orange, blue and rust, on a low mud plinth, with an old saree hung as a curtain for a door, potted chillies on the window ledge and a plastic bucket by the step. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G5 · Village head's house

✅ in the repo · Save as `G5_village_head_house.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: The grandest house on the lane: a landmark in level 2 or 3.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

The biggest house on the street: two storeys, walls washed in pale yellow with maroon trim, a long sloping roof of terracotta Mangalore tiles, a deep front veranda with six carved wooden pillars, raised sit-out platforms on both sides of a big carved double door with brass studs, a brass oil lamp by the door, a tulsi planter in front and a wooden easy chair on the veranda. Grand and proud, but still a village house. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G6 · Tiled house with courtyard gate

✅ in the repo · Save as `G6_tiled_house_gate.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house with a gate and a tree behind its wall.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A single-storey house with a terracotta-tiled roof sloping toward the street, a lime-washed front wall with a wooden gate into a courtyard, a mango tree peeking over the wall, a small window with blue bars and a kolam at the gate. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G7 · Provisions shop

⬜ to make · Save as `G7_provisions_shop.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A shopfront on the lane, with a bench and awning.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A small village provisions shop: a narrow shopfront with a corrugated tin awning on wooden poles, wooden shelves of glass jars of sweets, hanging strings of snack packets and a bunch of bananas, a big brass weighing scale on the counter, a wooden bench outside and a painted signboard above with pictures of a jar and a bottle and no letters. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G8 · Tea stall

⬜ to make · Save as `G8_tea_stall.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A tiny stall: steam, glasses and a bench, full of life.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A tiny roadside tea stall built of planks under a palm-thatch awning, a big brass kettle steaming on a clay stove, a row of small glass tumblers, a jar of biscuits, a wooden bench with a folded newspaper and a small radio on a shelf. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G9 · Tailor and cycle repair

⬜ to make · Save as `G9_tailor_cycle_shop.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: Two tiny shops under one awning.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Two tiny open-fronted shops side by side under one tin awning: a tailor's with a black treadle sewing machine and colourful fabric bolts, and a cycle-repair shop with tyres and inner tubes hanging up and a pump leaning on the wall. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G10 · Potter's house

⬜ to make · Save as `G10_potters_house.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: Ties in with the clay-pot obstacles: the pots come from here.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A potter's mud house with a thatched work shed beside it, a potter's wheel under the shed, rows of fresh unfired grey pots drying in the sun and stacks of fired terracotta pots in front. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G11 · Weaver's house

⬜ to make · Save as `G11_weavers_house.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: A nod to the kid's pattu frock: silk being woven.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A silk weaver's house with an open front room showing a wooden pit handloom with a half-woven magenta silk saree, bright silk threads stretched to dry on a frame outside, and lime-washed walls with an indigo band. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G12 · Half-built two-storey house

⬜ to make · Save as `G12_half_built_house.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: Every real village has one; it adds height and humour.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A two-storey house that is only half finished: the ground floor plastered and painted mint green with a grille window and a door, the upper floor bare red brick with steel rods sticking out of the pillar tops, a pile of sand and bricks in front and a clothesline on the roof. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G13 · Cattle shed

⬜ to make · Save as `G13_cattle_shed.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: An open shed: hay, a trough and a calf.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

An open cattle shed with a palm-thatch roof on wooden posts, a stone feeding trough, hay piled at the back, a calf tied to a post and a lime-washed back wall with painted handprints. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G14 · Panchayat office

⬜ to make · Save as `G14_panchayat_office.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: A civic building for the lane's end or the market.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A small village office: a flat-roofed concrete building painted pale yellow with a green band, a veranda with square pillars, a blank notice board, a wall clock, a wooden bench outside and a hand pump beside it. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G15 · Village shrine

⬜ to make · Save as `G15_village_shrine.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A small roadside shrine under a tree, with bell and lamps.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A small roadside shrine to the village guardian: a little whitewashed shrine with a tiny ornate tower on top, a brass bell at the entrance, marigold garlands and oil lamps, under a big tree with red and yellow threads tied round its trunk. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G16 · Overhead water tank

⬜ to make · Save as `G16_water_tank_tower.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: A landmark on the skyline behind the houses.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

The village's overhead water tank: a round concrete tank on four tall concrete legs with a ladder, painted pale blue with a white band, in a small fenced plot. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## H. Trees and plants

Several different trees or plants per image, so no two in view are the same, plus big foreground plants to frame the screen edges.

### H1 · Neem trees

⬜ to make · Save as `H1_neem_trees.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D4  
Used for: Shade trees between houses; three different ones so they never repeat side by side.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three different neem trees side by side: a big old one with a broad dome of small feathery leaves and a grey trunk, a young slender one, and one leaning with a swing tied to a branch. Drawn like the attached D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H2 · Tamarind and drumstick trees

⬜ to make · Save as `H2_tamarind_drumstick.png` · Landscape 3:2 · second batch · **new** · Attach: A1, D4  
Used for: More shade-tree variety.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Two tamarind trees with dense fine leaves and hanging brown pods, and two drumstick trees with lacy leaves and long green pods. Drawn like the attached D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H3 · Meeting tree with platform

⬜ to make · Save as `H3_peepal_platform.png` · Landscape 3:2 · second batch · **new** · Attach: A1, D4  
Used for: The village gathering spot: a one-off landmark.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A huge peepal tree with heart-shaped leaves growing from a raised square stone platform where villagers sit, a few small stone idols and lamps at its base, and red threads tied round the trunk. Drawn like the attached D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H4 · Coconut palms

⬜ to make · Save as `H4_coconut_palms.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D4  
Used for: Five different palms, so palms never look stamped.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Five different coconut palms: a tall straight one, one leaning far over, a pair growing from one spot, a young short palm, and one with a climber's rope ring on the trunk and coconuts in a bunch. Drawn like the attached D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H5 · Banana, papaya and curry-leaf plants

⬜ to make · Save as `H5_garden_plants.png` · Landscape 3:2 · second batch · **new** · Attach: A1, D4  
Used for: Small backyard plants for between houses.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Six small backyard plants: a banana plant with a bunch, a torn-leaf banana plant, a papaya tree with fruit, a curry-leaf bush, a clump of sugarcane and a pumpkin vine on a stick frame. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H6 · Flowering bushes

⬜ to make · Save as `H6_flowering_bushes.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D4  
Used for: Colour by doors and walls; each bush different.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Six flowering bushes and creepers: a hibiscus bush with red flowers, a magenta bougainvillea spilling over a wall, a jasmine creeper on a bamboo frame, a pink oleander, crotons in clay pots, and a patch of orange marigolds. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H7 · Foreground framing plants

⬜ to make · Save as `H7_foreground_plants.png` · Landscape 3:2 · first batch · **new** · Attach: A1  
Used for: Big plants in front of the lane, at the screen's bottom corners, like your story frames.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Five large foreground plants for framing the bottom corners of a game screen, drawn bigger and a little darker than the rest of the scene, as if close to the camera: a clump of big taro leaves, a cluster of tall grass with seed heads, a corner of banana leaves, a broken corner of a lime-washed compound wall with weeds, and a mossy rock with ferns. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## K. House parts kit

Doors, windows, roof edges and doorstep details. Blender builds endless house variations from these, so a long street never repeats.

### K1 · Doors and windows

⬜ to make · Save as `K1_doors_windows.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: Fitted to houses Blender builds, so no two front doors match. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Sheet of village doors and windows for a modular house kit, each shown straight on and separate: a carved double wooden door with brass studs, a plain plank door painted blue, a green-framed door with a marigold garland, a low hut door, a doorway with a hanging saree curtain, a window with wooden shutters open, a window with blue iron bars, and a small window with a plank shutter propped open. Drawn at the scale of the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### K2 · Roof edges and awnings

⬜ to make · Save as `K2_roof_edges.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: The front edges of roofs Blender builds: thatch, tiles, tin and awnings. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Six roof edges and awnings for a modular house kit, each a long horizontal strip seen straight on from the front: a palm-thatch eave, a terracotta Mangalore-tile eave, a corrugated tin-sheet eave with rust, a flat-roof parapet with pots on it, a striped cloth awning and a bamboo-and-palm-mat awning. Drawn at the scale of the attached C4 house kit. Plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### K3 · Doorstep and wall details

⬜ to make · Save as `K3_wall_details.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: Small details that make every built house its own.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Sheet of small details for village house fronts, each separate and seen straight on: three different front steps with kolam, a raised sit-out platform, a brass wall lamp, a hanging lantern, a row of cow-dung cakes drying on a wall, a wall shelf with clay pots, a hanging bird feeder and a mango-leaf garland. Drawn at the scale of the attached C4 house kit. Plain flat light-grey background, even lighting, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## T. Textures

Seamless hand-painted textures for Blender materials. These use the texture rules instead of the scene style.

### T1 · Red-earth lane

✅ in the repo · Save as `T1_tex_earth_lane.png` · Square 1:1 · first batch · Attach: A1  
Used for: The lane material for zone 1.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A top-down texture of a packed red-earth village lane: terracotta soil with small pebbles, faint footprints and bicycle tracks, a few dry leaves.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T2 · Lime-washed wall

✅ in the repo · Save as `T2_tex_limewash_wall.png` · Square 1:1 · first batch · Attach: A1  
Used for: The base wall material for the house kit.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of a lime-washed village wall: soft white with a faint blue tint, uneven brush strokes, small chips showing terracotta plaster underneath, slightly dirtier toward the bottom.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T3 · Coloured walls

✅ in the repo · Save as `T3_tex_coloured_walls.png` · Square 1:1 · first batch · Attach: A1  
Used for: Wall variants for the house kit. I split the four squares and make each one tile.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate wall textures in a 2 by 2 grid, each square front-on with soft uneven brush strokes: an indigo-washed wall, a turmeric-yellow wall, a pale pink wall and a weathered sea-green wall.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T4 · Wood, rope and bamboo

✅ in the repo · Save as `T4_tex_wood_weave.png` · Square 1:1 · first batch · Attach: A1  
Used for: Doors, the cot, the basket and the sacks.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate textures in a 2 by 2 grid, each square seen straight on: weathered wooden planks, the woven rope top of a cot, a bamboo basket weave and coarse jute sacking.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T5 · Roofs, floors and stone

✅ in the repo · Save as `T5_tex_roof_floor_stone.png` · Square 1:1 · second batch · Attach: A1  
Used for: Thatch, roof tiles, the courtyard floor and the temple steps.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate textures in a 2 by 2 grid, each square seen straight on: palm-leaf thatch, terracotta roof tiles, a smooth cow-dung-plastered courtyard floor in olive brown, and worn granite temple stone.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T6 · Paddy and canal water

✅ in the repo · Save as `T6_tex_water.png` · Square 1:1 · second batch · Attach: A1  
Used for: The paddy and canal surfaces for zone 2.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Two textures side by side, each filling half the square, seen straight down: shallow paddy-field water with rows of young green rice shoots and a golden sky reflected in it; and muddy-green canal water with soft ripples and a few floating leaves.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T7 · Saree and awning fabrics

✅ in the repo · Save as `T7_tex_fabrics.png` · Square 1:1 · second batch · Attach: A1  
Used for: Sarees on the clotheslines and the market awnings.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate fabric patterns in a 2 by 2 grid, each square flat and seen straight on: kumkum red with a gold border stripe; indigo block print with small white motifs; turmeric and green checks; red-and-white market awning stripes.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T8 · Corrugated tin sheet

⬜ to make · Save as `T8_tex_tin_sheet.png` · Square 1:1 · second batch · **new** · Attach: A1  
Used for: Roofs of the tin-roof houses Blender builds. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of an old corrugated tin roofing sheet: silver-grey ridges with patches of orange rust, rust streaks and a few nail heads.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T9 · Orange mud plaster

⬜ to make · Save as `T9_tex_orange_mud.png` · Square 1:1 · second batch · **new** · Attach: A1  
Used for: Walls of the orange mud houses Blender builds. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of a mud-plastered wall in warm orange ochre: hand-smoothed, with finger swirls, small cracks and a few patches where the red-brown earth shows.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T10 · Bare brick

⬜ to make · Save as `T10_tex_bare_brick.png` · Square 1:1 · second batch · **new** · Attach: A1  
Used for: Unfinished upper floors and back walls.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of an unplastered red brick wall with uneven grey mortar lines and a few chipped bricks.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T11 · Woven coconut-leaf fence

⬜ to make · Save as `T11_tex_coconut_leaf_fence.png` · Square 1:1 · first batch · **new** · Attach: A1  
Used for: The fences around house compounds, built in Blender: so they look woven by hand, not tiled.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of a village compound fence made of dried coconut palm leaves woven in overlapping rows: tan, straw and grey-brown leaflets folded over thin horizontal sticks, a few frayed ends and small gaps.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T12 · Plain red earth

⬜ to make · Save as `T12_tex_plain_red_earth.png` · Square 1:1 · first batch · **new** · Attach: A1, T1  
Used for: The grain of the lane's ground, which Blender builds without repeating: it needs earth with no marks in it.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of bare red laterite earth seen straight down, in the colours of the attached T1 texture: fine dust, crumbs and grit, soft brush-stroke variation between deep red, red-orange and dusty orange. Only the earth itself: no footprints, tracks, leaves, plants or stones.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

## What happens in Blender

1. **Model.** Props, buildings, the rooster, the side characters and (unless you have a model) the kid are modelled in Blender over the model sheets, at the game's scale (1 unit = 1 m), with the side view getting the most care because the camera is side-on.
2. **Paint.** The textures become hand-painted materials. Characters and props get a toon shader with an outline, so they match the Unity toon look; backgrounds stay painterly.
3. **Layer.** The far and middle layers become painted cards behind the 3D lane, which gives each zone its parallax depth.
4. **Light.** Each zone gets the time of day from the colour script, with haze, light shafts and dust.
5. **Animate.** The rooster's run, flutter, taunt, panic and wriggle come from his pose sheet. The kid's clips go on the kid's rig, and the story frames become the intro and ending cutscenes.
6. **Export.** Models and animations go to Unity as FBX (Humanoid-ready for the kid), and the cutscenes render as video or Timeline animation.

## What I need from you

- The rooster reference photo from the design doc. (Your four kid images are in ArtSource/supplied.)
- Your kid model files (FBX or .blend, with the rig) if you have them in the pattu frock. Otherwise I'll model the kid from A0.
- The images from this sheet, saved with the file names shown. Upload them here in batches.
- A yes or no on South India. The prompts use kolam, a gopuram-style temple tower and Amma; tell me if you want another region.
