# Chicken Runner — art prompt sheet

Image prompts for ChatGPT, written for the Blender pipeline: every image has an ID, a file name and a shape, so the images come back named for the scenes they feed. The web version has copy buttons and a checklist. Gemini versions of the same prompts, with the same IDs and file names, are in [prompt-sheet-gemini.md](prompt-sheet-gemini.md).

## How to use it

1. Make **A1** first, in a new ChatGPT chat, attaching your kid reference art and rooster photo.
2. Stay in that chat for the rest. Each prompt below is copy-ready: it asks ChatGPT to match A1 and carries the style rules. Attach the files listed under *Attach*.
3. Save each image with the file name shown.
4. Upload the images in batches, starting with the 22 marked *first batch*.

Regenerate an image when words or labels appear in it, when a model sheet is not side-on and orthographic, or when the background is not plain.

## A. Style anchors

Make these first. A1 sets the look; every later prompt asks ChatGPT to match it.

### A1 · Key art

Save as `A1_key_art.png` · Landscape 3:2 · first batch · Attach: your kid reference art, your rooster reference photo  
Used for: Sets the look every other image matches, and my reference for materials and lighting in Blender.

```text
Landscape 3:2 image.

Key art for the game. Side-on view of a narrow South Indian village lane in late-afternoon golden light. A small, determined toddler (big head, short legs, sports kit, leopard-print hairband, drawn exactly like the attached kid reference) sprints from left to right after a smug country rooster (red comb, orange neck feathers, glossy black tail, like the attached rooster photo) who glances back over his shoulder mid-stride. Around them: flat-roofed houses washed in lime-white, indigo and turmeric, white kolam patterns at the doorsteps, a stack of clay pots, a hand pump with a puddle, a rope cot where a sleepy neighbour is just waking up, a tulsi planter, coconut palms and a distant temple tower in warm haze. Dust kicked up by little feet, a few loose feathers in the air, long soft shadows. The kid is on the left third, the rooster on the right.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### A2 · Colour script

Save as `A2_colour_script.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: The lighting plan across the nine levels: one Blender lighting setup per zone.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A colour script for the whole game: nine small painted panels in a 3 by 3 grid, read left to right and top to bottom, all side-on views of one chase through a South Indian village as the day goes by. Panels 1 to 3: a village lane in warm late afternoon. Panels 4 to 6: paddy fields, an irrigation canal and mango trees at golden hour, the light turning orange. Panel 7: flat rooftops with drying red chillies at sunset. Panel 8: a weekly market at dusk with marigold garlands and glowing lanterns. Panel 9: temple steps at blue dusk lit by rows of small oil lamps. Simple shapes, all about light and colour, with tiny silhouettes of a toddler chasing a rooster in every panel.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## B. Characters

Model sheets and pose sheets. Attach your kid reference art and rooster photo where noted.

### B1 · Rooster model sheet

Save as `B1_rooster_model_sheet.png` · Landscape 3:2 · first batch · Attach: A1, your rooster reference photo  
Used for: Traced in Blender to model the rooster at the right proportions.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character model sheet of the game's rooster for 3D modelling, based on the attached rooster photo: a proud country rooster with a big red comb and wattles, orange-gold neck feathers, a rust-red body, dark wings, a glossy black curved tail and yellow legs. Four views side by side at exactly the same scale and height: left side view, front view, back view and top view, standing in a neutral pose. Orthographic, no perspective. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B2 · Rooster pose sheet

Save as `B2_rooster_poses.png` · Landscape 3:2 · first batch · Attach: A1, B1  
Used for: Key poses for the rooster's run, flutter, taunt, panic and wriggle animations.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Pose sheet for the same rooster as the attached model sheet, all in side view facing right, evenly spaced at the same scale on a plain flat light-grey background: 1) running with one leg forward; 2) running with the other leg forward; 3) fluttering up with wings spread and feet tucked; 4) the smug taunt, turned back to face left, chest puffed out, head thrown back, crowing; 5) panic sprint, eyes wide, feathers flying off; 6) wriggling free upside down, flapping wildly; 7) pecking at the ground; 8) standing proud on one foot. Funny, expressive body language: slapstick, never hurt.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B3 · Kid gameplay poses

Save as `B3_kid_poses_gameplay.png` · Landscape 3:2 · first batch · Attach: A1, your kid reference art  
Used for: Key poses for the nine first-prototype animations on your kid model.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Pose sheet for the toddler hero, keeping the design exactly as in the attached reference art (big head, short legs, sports kit, leopard-print hairband). All side view facing right, same scale, plain flat light-grey background: 1) running, contact pose; 2) running, passing pose; 3) jumping up with arms raised; 4) falling with arms flailing; 5) landing in a squat; 6) sliding feet first on their back; 7) vaulting a low wall with both hands on top; 8) stumbling forward, off balance; 9) diving flat out with arms stretched to grab.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B4 · Kid story poses and faces

Save as `B4_kid_story_and_faces.png` · Landscape 3:2 · first batch · Attach: A1, your kid reference art  
Used for: The four face expressions and the story-animation poses.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Second pose sheet for the same toddler, exactly as in the attached reference art. Top row, four face close-ups: neutral, big cheeky grin, shocked with mouth open, straining with cheeks puffed. Bottom row, full body side views facing right: tiptoeing with exaggerated sneaky steps; lifting a big bamboo basket with both hands, straining; a startled jump; carrying a rooster proudly in both arms; cheering with fists up; sulking with arms crossed. Plain flat light-grey background, even lighting.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B5 · Neighbour

Save as `B5_neighbour_sheet.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Modelled for the basket intro: asleep on the cot, then waking with a shout.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character sheet for the sleepy neighbour: a friendly middle-aged village man with a bushy moustache, a white cotton vest and a checked lungi, a little round in the middle. Left: front view and side view standing, same scale, for 3D modelling. Right: napping on a rope cot with one arm over his face, then waking up mid-shout with one arm raised, pointing. Comic and warm, never mean. Plain flat light-grey background, even lighting.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B6 · Amma

Save as `B6_amma_sheet.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled for the final kitchen scene.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character sheet for Amma, the toddler's mother: a warm, kind woman in her thirties wearing a cotton saree in turmeric and indigo, hair in a bun with jasmine flowers, glass bangles. Left: front view and side view standing, same scale, for 3D modelling. Right: three expressions, surprised with a hand on her cheek, laughing, and a stern raised eyebrow with hands on hips. Dignified and loving. Plain flat light-grey background, even lighting.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B7 · Village animals

Save as `B7_animals_sheet.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The sleeping dog, hens, buffalo and bullocks that become obstacles and scenery.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Sheet of village animals in side view facing right, at the same scale relative to each other, on a plain flat light-grey background: a street dog asleep curled in the dust; the same dog woken up and barking; three hens pecking; a water buffalo lying in a mud patch; a pair of white bullocks standing. Friendly cartoon proportions.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## C. Zone 1: the lane

Levels 1 to 3. Painted houses, verandas, kolam, pots, cots and clotheslines.

### C1 · Lane mood painting

Save as `C1_lane_mood.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: The target for the zone 1 Blender scene: layout, lighting and atmosphere.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting of the village lane, side-on like a side-scrolling game level, no characters. A packed red-earth lane runs left to right. Flat-roofed houses in lime-white, indigo, turmeric and pale pink with verandas and pillars, wooden doors with mango-leaf garlands, white kolam patterns at each doorstep. Stacked clay pots, a hand pump with a puddle, a rope cot, a bicycle leaning on a wall, a tulsi planter, a clothesline of bright sarees and bamboo ladders up to the rooftops. Behind: coconut palms, then a distant temple tower and hills fading into warm haze. Late afternoon: long shadows across the lane, light shafts through the palms, dust in the air.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C2 · Lane far layer

Save as `C2_lane_far_layer.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: A painted card at the back of the scene, scrolling slowest.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Far background layer for parallax scrolling, with no foreground and no ground: a late-afternoon sky with soft painterly clouds, low hills and a distant South Indian temple tower in silhouette, a few faraway coconut palms, all fading into warm golden haze toward the bottom. Wide and calm, so it can repeat sideways.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C3 · Lane middle layer

Save as `C3_lane_mid_layer.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: A cut-out card between the far layer and the play lane. Magenta is keyed out.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer, side-on: a row of coconut palms, banana plants and the backs of distant village houses with tiled and flat roofs, a little hazy and lower in contrast than a foreground would be. Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C4 · House kit elevations

Save as `C4_house_kit_elevations.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Traced to build the modular house kit: walls, verandas, parapets, doors and ladder.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Modular building kit for 3D modelling: four flat-roofed South Indian village house fronts seen straight on (front elevation, orthographic, no perspective), standing side by side on one baseline. One narrow, in lime-white. One wide, in indigo, with a shaded veranda and two pillars. One in turmeric with a small barred window and a raised sit-out platform by the door. One pale pink with steps up to the door. Each has a low parapet along the roof edge, a wooden door and a painted band at the base. A bamboo ladder leans on one wall. Even flat lighting, plain flat light-grey background, no labels.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C5 · Lane props, sheet 1

Save as `C5_lane_props_a.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Modelled as the zone 1 obstacles and set dressing.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet for 3D modelling, every object in side view at the same scale, evenly spaced on a plain flat light-grey background, even lighting: a stack of three clay pots; a flat cow-dung patty; an iron hand pump with a small puddle; a wooden rope cot with a woven top; an old black bicycle; a tulsi planter on a small painted pedestal; a pair of brass water pots. Hazards (pots, dung, puddle) in warm colours with dark outlines; the helpful cot has a slight glint.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C6 · Lane props, sheet 2

Save as `C6_lane_props_b.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: The bullock cart, clothesline and the bamboo basket from the intro.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Second prop sheet, side view, same scale, plain flat light-grey background, even lighting: a bullock cart with big wooden wheels; a clothesline on two bamboo poles with two bright sarees hanging; an upturned dome-shaped bamboo chicken basket; a pile of jute sacks; a wooden doorway with a mango-leaf garland across the top; a small roadside shrine stone with a marigold garland; a clay water pot on a stand.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C7 · Kolam decals

Save as `C7_kolam_decals.png` · Square 1:1 · first batch · Attach: A1  
Used for: Cut out as decals for doorsteps and the lane.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Six different kolam floor designs seen straight from above, drawn in clean white rice-flour lines with a few accents in turmeric, kumkum red and green, arranged in a 3 by 2 grid with space between them, on a solid flat dark-grey background so they can be cut out. Simple, bold, hand-drawn lines.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## D. Zone 2: fields and canal

Levels 4 to 6. Paddy fields, bunds, the canal, haystacks and mango trees.

### D1 · Fields mood painting

Save as `D1_fields_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for the zone 2 Blender scene.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting, side-on like a side-scrolling game level, no characters: emerald paddy fields with mirror-like water between the rows, a raised earthen bund path running left to right, an irrigation canal crossed by a narrow plank bridge, conical haystacks, a big mango tree with low climbable branches, tall palms, a stone well with a pulley, a scarecrow with a painted clay-pot head and white egrets in the water. Golden hour: the light turning orange, long reflections in the water, soft mist over the far fields.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D2 · Fields far layer

Save as `D2_fields_far_layer.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The back card for zone 2.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Far parallax layer with no foreground and no ground: a golden-hour sky with glowing clouds, distant blue hills, lines of palm trees across faraway fields and a flock of birds, all fading into warm haze at the bottom. Calm, so it can repeat sideways.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D3 · Fields props

Save as `D3_fields_props.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled as the zone 2 obstacles: haystack, canal and plank bridge, well.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet for 3D modelling, side view, same scale, plain flat light-grey background, even lighting: a conical haystack; a short stretch of irrigation canal with a narrow wooden plank bridge; a round stone well with a wooden pulley and rope; a scarecrow with a painted clay-pot head and an old shirt; a small canal sluice gate; a section of earthen bund path with grass along its edges.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D4 · Mango tree

Save as `D4_mango_tree.png` · Landscape 3:2 · second batch · Attach: A1  
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

Save as `E1_rooftops_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for levels 7 and the rooftop stretches.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting, side-on like a side-scrolling game level, no characters: a run of connected flat village rooftops at sunset with small gaps between the houses, low parapets, black cylindrical water tanks, red chillies and round papads drying on woven mats, a clothesline, a bamboo ladder, paper kites in the sky and festival bunting strung between houses. The setting sun rims everything in orange and the sky shifts from gold to rose.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E2 · Market mood painting

Save as `E2_market_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for level 8, the market day.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting, side-on like a side-scrolling game level: a weekly village market at dusk, a row of stalls with striped cloth awnings at different heights, heaps of vegetables, brass and steel vessels, flower sellers with marigold and jasmine garlands, hens in woven baskets, hanging lanterns starting to glow and a busy crowd as soft silhouettes in the background.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E3 · Temple steps

Save as `E3_temple_steps_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for level 9, the final catch.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting for the final level, side-on: wide stone temple steps rising from left to right toward a tall carved temple tower, rows of small clay oil lamps flickering along every step, brass bells, marigold garlands and festival bunting, a big old banyan tree to one side. Blue dusk turning to night, warm lamp light pooling on the stone, a few stars. Magical and calm.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E4 · Rooftop props

Save as `E4_rooftop_props.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled as the zone 3 rooftop obstacles and dressing.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a black cylindrical plastic water tank on a low stand; a section of rooftop parapet wall with a gap; a woven mat of red chillies drying; a woven mat of round papads; a paper kite with a tail; a string of triangular festival bunting.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E5 · Market and temple props

Save as `E5_market_props.png` · Landscape 3:2 · second batch · Attach: A1  
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

Save as `F1_title_screen.png` · Landscape 3:2 · second batch · Attach: A1, your kid reference art  
Used for: Staged in Blender as the title screen, with room for the logo.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Title screen illustration with empty space at the top centre for a logo: the toddler hero (as in the attached reference art) peeks mischievously from behind a low wall at an upturned bamboo basket in a neighbour's yard, and a rooster's beady eye looks back through the gaps in the weave. Late afternoon, warm light, kolam on the ground.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F2 · Story 1: the craving

Save as `F2_story_craving.png` · Landscape 3:2 · first batch · Attach: A1, your kid reference art  
Used for: Storyboard for the opening shot of the intro cutscene.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The craving: the toddler sits on the doorstep of home, nose in the air and eyes closed in bliss, as a ribbon of curry aroma, drawn as swirling golden steam with tiny spice specks, drifts over the wall from the neighbour's kitchen window. Warm afternoon. Wordless storytelling.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F3 · Story 2: the plan

Save as `F3_story_plan.png` · Landscape 3:2 · first batch · Attach: A1, your kid reference art, B5  
Used for: Storyboard and layout for the yard where the basket intro is played.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The plan: the neighbour's yard seen side-on, three upturned bamboo baskets with roosters under them, the neighbour snoring on a rope cot under a tree, and the toddler tiptoeing in with exaggerated sneaky steps, tongue out in concentration. Dappled afternoon light.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F4 · Story 3: the basket

Save as `F4_story_basket.png` · Landscape 3:2 · first batch · Attach: A1, your kid reference art  
Used for: Storyboard for the hold-to-lift moment.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The basket: a close side view of the toddler slowly lifting a big bamboo basket with both hands, straining; under the rim, the rooster's head and one suspicious eye peek out. Tense and funny, with soft light falling through the basket weave.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F5 · Story 4: the escape

Save as `F5_story_escape.png` · Landscape 3:2 · first batch · Attach: A1, your kid reference art, B5  
Used for: Storyboard for the moment the chase begins.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The escape: the rooster bursts out from under the basket in an explosion of feathers, wings wide, while the toddler falls back in surprise and the neighbour sits bolt upright on his cot, shouting and pointing. Dust, feathers and slapstick energy.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F6 · Wriggle-free gag

Save as `F6_story_wriggle_free.png` · Landscape 3:2 · second batch · Attach: A1, your kid reference art  
Used for: Storyboard for the gag at the end of levels 1 to 8.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Gag frame: the toddler dives flat out and lands belly-down in the dust with hands closed on nothing, while the rooster pops out of their grip and flutters away overhead looking smug, a single feather floating down onto the toddler's head.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F7 · Rooster escaped

Save as `F7_rooster_escaped.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Staged in Blender as the loss screen.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Loss screen illustration: the rooster stands on a rooftop parapet against a sunset sky, chest out, crowing in triumph; far below, a tiny toddler looks up with hands on hips.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F8 · Story 6: Amma's kitchen

Save as `F8_story_amma_kitchen.png` · Landscape 3:2 · second batch · Attach: A1, your kid reference art, B6  
Used for: Storyboard for the final scene. It stops at the handover, as the design doc's risk table asks.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Final story frame, Amma's kitchen: a warm, lamp-lit village kitchen with a clay stove, brass and steel vessels on shelves and strings of dried chillies. The toddler proudly holds up the rooster in both arms to Amma, who looks down with surprise and a smile. Golden evening light through a small window. Nothing shown beyond this moment.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## T. Textures

Seamless hand-painted textures for Blender materials. These use the texture rules instead of the scene style.

### T1 · Red-earth lane

Save as `T1_tex_earth_lane.png` · Square 1:1 · first batch · Attach: A1  
Used for: The lane material for zone 1.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A top-down texture of a packed red-earth village lane: terracotta soil with small pebbles, faint footprints and bicycle tracks, a few dry leaves.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T2 · Lime-washed wall

Save as `T2_tex_limewash_wall.png` · Square 1:1 · first batch · Attach: A1  
Used for: The base wall material for the house kit.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of a lime-washed village wall: soft white with a faint blue tint, uneven brush strokes, small chips showing terracotta plaster underneath, slightly dirtier toward the bottom.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T3 · Coloured walls

Save as `T3_tex_coloured_walls.png` · Square 1:1 · first batch · Attach: A1  
Used for: Wall variants for the house kit. I split the four squares and make each one tile.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate wall textures in a 2 by 2 grid, each square front-on with soft uneven brush strokes: an indigo-washed wall, a turmeric-yellow wall, a pale pink wall and a weathered sea-green wall.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T4 · Wood, rope and bamboo

Save as `T4_tex_wood_weave.png` · Square 1:1 · first batch · Attach: A1  
Used for: Doors, the cot, the basket and the sacks.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate textures in a 2 by 2 grid, each square seen straight on: weathered wooden planks, the woven rope top of a cot, a bamboo basket weave and coarse jute sacking.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T5 · Roofs, floors and stone

Save as `T5_tex_roof_floor_stone.png` · Square 1:1 · second batch · Attach: A1  
Used for: Thatch, roof tiles, the courtyard floor and the temple steps.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate textures in a 2 by 2 grid, each square seen straight on: palm-leaf thatch, terracotta roof tiles, a smooth cow-dung-plastered courtyard floor in olive brown, and worn granite temple stone.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T6 · Paddy and canal water

Save as `T6_tex_water.png` · Square 1:1 · second batch · Attach: A1  
Used for: The paddy and canal surfaces for zone 2.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Two textures side by side, each filling half the square, seen straight down: shallow paddy-field water with rows of young green rice shoots and a golden sky reflected in it; and muddy-green canal water with soft ripples and a few floating leaves.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

### T7 · Saree and awning fabrics

Save as `T7_tex_fabrics.png` · Square 1:1 · second batch · Attach: A1  
Used for: Sarees on the clotheslines and the market awnings.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate fabric patterns in a 2 by 2 grid, each square flat and seen straight on: kumkum red with a gold border stripe; indigo block print with small white motifs; turmeric and green checks; red-and-white market awning stripes.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks.
```

## What happens in Blender

1. **Model.** Props, buildings, the rooster and the side characters are modelled in Blender over the model sheets, at the game's scale (1 unit = 1 m), with the side view getting the most care because the camera is side-on.
2. **Paint.** The textures become hand-painted materials. Characters and props get a toon shader with an outline, so they match the Unity toon look; backgrounds stay painterly.
3. **Layer.** The far and middle layers become painted cards behind the 3D lane, which gives each zone its parallax depth.
4. **Light.** Each zone gets the time of day from the colour script, with haze, light shafts and dust.
5. **Animate.** The rooster's run, flutter, taunt, panic and wriggle come from his pose sheet. The kid's clips go on your model's rig, and the story frames become the intro and ending cutscenes.
6. **Export.** Models and animations go to Unity as FBX (Humanoid-ready for the kid), and the cutscenes render as video or Timeline animation.

## What I need from you

- Your kid model files (FBX or .blend), with the rig if it has one.
- The kid reference art and the rooster reference photo from the design doc.
- The images from this sheet, saved with the file names shown. Upload them here in batches.
- A yes or no on South India. The prompts use kolam, a gopuram-style temple tower and Amma; tell me if you want another region.
