# Chicken Runner — art prompt sheet for Gemini

The same images as [the ChatGPT sheet](prompt-sheet.md), with the same IDs and file names, rewritten for Gemini's image model: full sentences, positive wording, a stated job for every uploaded image, and wider 16:9 and 21:9 shapes for the side-on scenes.

## How to use it

1. Make **A1** first, in a new Gemini chat, uploading your kid art and rooster photo.
2. Stay in that chat. Each copied prompt says what every uploaded image is for. Upload the files under *Attach* with each prompt, A1 included: re-uploading it keeps the style closest.
3. If the shape comes out wrong, reply: *Make this same image in a 21:9 ultra-wide shape* (or the shape shown).
4. Save each image with its file name, then put them in the repo at `ArtSource/references/` or upload them here, in batches.

Start with the 22 marked *first batch*. Gemini is good at small edits, so ask for just the change: *Using the image you just made, remove the labels and keep everything else the same.* A small sparkle mark in a corner is Gemini's watermark; leave it and I'll paint it out.

## A. Style anchors

Make these first. A1 sets the look; every later prompt asks ChatGPT to match it.

### A1 · Key art

Save as `A1_key_art.png` · 16:9 landscape · first batch · Upload: your kid reference art, your rooster reference photo  
Used for: Sets the look every other image matches, and my reference for materials and lighting in Blender.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: my kid reference art, to keep the toddler's face, proportions and outfit identical; my rooster photo, to match his colours and markings.

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Key art for the game. Side-on view of a narrow South Indian village lane in late-afternoon golden light. A small, determined toddler (big head, short legs, sports kit, leopard-print hairband, drawn exactly like the uploaded kid reference) sprints from left to right after a smug country rooster (red comb, orange neck feathers, glossy black tail, like the uploaded rooster photo) who glances back over his shoulder mid-stride. Around them: flat-roofed houses washed in lime-white, indigo and turmeric, white kolam patterns at the doorsteps, a stack of clay pots, a hand pump with a puddle, a rope cot where a sleepy neighbour is just waking up, a tulsi planter, coconut palms and a distant temple tower in warm haze. Dust kicked up by little feet, a few loose feathers in the air, long soft shadows. The kid is on the left third, the rooster on the right.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### A2 · Colour script

Save as `A2_colour_script.png` · 16:9 landscape · first batch · Upload: A1  
Used for: The lighting plan across the nine levels: one Blender lighting setup per zone.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A colour script for the whole game: nine small painted panels in a 3 by 3 grid, read left to right and top to bottom, all side-on views of one chase through a South Indian village as the day goes by. Panels 1 to 3: a village lane in warm late afternoon. Panels 4 to 6: paddy fields, an irrigation canal and mango trees at golden hour, the light turning orange. Panel 7: flat rooftops with drying red chillies at sunset. Panel 8: a weekly market at dusk with marigold garlands and glowing lanterns. Panel 9: temple steps at blue dusk lit by rows of small oil lamps. Simple shapes, all about light and colour, with tiny silhouettes of a toddler chasing a rooster in every panel.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## B. Characters

Model sheets and pose sheets. Attach your kid reference art and rooster photo where noted.

### B1 · Rooster model sheet

Save as `B1_rooster_model_sheet.png` · 16:9 landscape · first batch · Upload: A1, your rooster reference photo  
Used for: Traced in Blender to model the rooster at the right proportions.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my rooster photo, to match his colours and markings.

Character model sheet of the game's rooster for 3D modelling, based on the uploaded rooster photo: a proud country rooster with a big red comb and wattles, orange-gold neck feathers, a rust-red body, dark wings, a glossy black curved tail and yellow legs. Four views side by side at exactly the same scale and height: left side view, front view, back view and top view, standing in a neutral pose. Draw them perfectly flat and orthographic, like an animation model sheet, lit evenly from the front so nothing casts a shadow, on a plain light-grey background. The sheet holds only the four drawings, unlabeled.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B2 · Rooster pose sheet

Save as `B2_rooster_poses.png` · 16:9 landscape · first batch · Upload: A1, B1  
Used for: Key poses for the rooster's run, flutter, taunt, panic and wriggle animations.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the B1 rooster model sheet, to keep the rooster's design identical.

Pose sheet for the same rooster as the uploaded model sheet, all in side view facing right, evenly spaced at the same scale on a plain flat light-grey background: 1) running with one leg forward; 2) running with the other leg forward; 3) fluttering up with wings spread and feet tucked; 4) the smug taunt, turned back to face left, chest puffed out, head thrown back, crowing; 5) panic sprint, eyes wide, feathers flying off; 6) wriggling free upside down, flapping wildly; 7) pecking at the ground; 8) standing proud on one foot. Funny, expressive body language: slapstick, never hurt.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B3 · Kid gameplay poses

Save as `B3_kid_poses_gameplay.png` · 16:9 landscape · first batch · Upload: A1, your kid reference art  
Used for: Key poses for the nine first-prototype animations on your kid model.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical.

Pose sheet for the toddler hero, keeping the design exactly as in the uploaded reference art (big head, short legs, sports kit, leopard-print hairband). All side view facing right, same scale, plain flat light-grey background: 1) running, contact pose; 2) running, passing pose; 3) jumping up with arms raised; 4) falling with arms flailing; 5) landing in a squat; 6) sliding feet first on their back; 7) vaulting a low wall with both hands on top; 8) stumbling forward, off balance; 9) diving flat out with arms stretched to grab.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B4 · Kid story poses and faces

Save as `B4_kid_story_and_faces.png` · 16:9 landscape · first batch · Upload: A1, your kid reference art  
Used for: The four face expressions and the story-animation poses.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical.

Second pose sheet for the same toddler, exactly as in the uploaded reference art. Top row, four face close-ups: neutral, big cheeky grin, shocked with mouth open, straining with cheeks puffed. Bottom row, full body side views facing right: tiptoeing with exaggerated sneaky steps; lifting a big bamboo basket with both hands, straining; a startled jump; carrying a rooster proudly in both arms; cheering with fists up; sulking with arms crossed. Plain flat light-grey background, even lighting.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B5 · Neighbour

Save as `B5_neighbour_sheet.png` · 16:9 landscape · first batch · Upload: A1  
Used for: Modelled for the basket intro: asleep on the cot, then waking with a shout.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Character sheet for the sleepy neighbour: a friendly middle-aged village man with a bushy moustache, a white cotton vest and a checked lungi, a little round in the middle. Left: front view and side view standing, same scale, for 3D modelling. Right: napping on a rope cot with one arm over his face, then waking up mid-shout with one arm raised, pointing. Comic and warm, never mean. Plain flat light-grey background, even lighting.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B6 · Amma

Save as `B6_amma_sheet.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled for the final kitchen scene.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Character sheet for Amma, the toddler's mother: a warm, kind woman in her thirties wearing a cotton saree in turmeric and indigo, hair in a bun with jasmine flowers, glass bangles. Left: front view and side view standing, same scale, for 3D modelling. Right: three expressions, surprised with a hand on her cheek, laughing, and a stern raised eyebrow with hands on hips. Dignified and loving. Plain flat light-grey background, even lighting.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B7 · Village animals

Save as `B7_animals_sheet.png` · 16:9 landscape · second batch · Upload: A1  
Used for: The sleeping dog, hens, buffalo and bullocks that become obstacles and scenery.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Sheet of village animals in side view facing right, at the same scale relative to each other, on a plain flat light-grey background: a street dog asleep curled in the dust; the same dog woken up and barking; three hens pecking; a water buffalo lying in a mud patch; a pair of white bullocks standing. Friendly cartoon proportions.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## C. Zone 1: the lane

Levels 1 to 3. Painted houses, verandas, kolam, pots, cots and clotheslines.

### C1 · Lane mood painting

Save as `C1_lane_mood.png` · 21:9 ultra-wide · first batch · Upload: A1  
Used for: The target for the zone 1 Blender scene: layout, lighting and atmosphere.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting of the village lane, side-on like a side-scrolling game level. The lane is empty for a moment, waiting for the chase. A packed red-earth lane runs left to right. Flat-roofed houses in lime-white, indigo, turmeric and pale pink with verandas and pillars, wooden doors with mango-leaf garlands, white kolam patterns at each doorstep. Stacked clay pots, a hand pump with a puddle, a rope cot, a bicycle leaning on a wall, a tulsi planter, a clothesline of bright sarees and bamboo ladders up to the rooftops. Behind: coconut palms, then a distant temple tower and hills fading into warm haze. Late afternoon: long shadows across the lane, light shafts through the palms, dust in the air.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C2 · Lane far layer

Save as `C2_lane_far_layer.png` · 21:9 ultra-wide · first batch · Upload: A1  
Used for: A painted card at the back of the scene, scrolling slowest.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Far background layer for parallax scrolling, made only of sky and distance: a late-afternoon sky with soft painterly clouds, low hills and a distant South Indian temple tower in silhouette, a few faraway coconut palms, all fading into warm golden haze toward the bottom. Wide and calm, so it can repeat sideways.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C3 · Lane middle layer

Save as `C3_lane_mid_layer.png` · 21:9 ultra-wide · first batch · Upload: A1  
Used for: A cut-out card between the far layer and the play lane. Magenta is keyed out.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Middle parallax layer, side-on: a row of coconut palms, banana plants and the backs of distant village houses with tiled and flat roofs, a little hazy and lower in contrast than a foreground would be. Everything else in the image is solid flat magenta (#FF00FF), so the trees and houses can be cut out cleanly.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C4 · House kit elevations

Save as `C4_house_kit_elevations.png` · 16:9 landscape · first batch · Upload: A1  
Used for: Traced to build the modular house kit: walls, verandas, parapets, doors and ladder.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Modular building kit for 3D modelling: four flat-roofed South Indian village house fronts seen straight on (front elevations, perfectly flat and orthographic, like an architect's drawing), standing side by side on one baseline. One narrow, in lime-white. One wide, in indigo, with a shaded veranda and two pillars. One in turmeric with a small barred window and a raised sit-out platform by the door. One pale pink with steps up to the door. Each has a low parapet along the roof edge, a wooden door and a painted band at the base. A bamboo ladder leans on one wall. Even flat lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C5 · Lane props, sheet 1

Save as `C5_lane_props_a.png` · 16:9 landscape · first batch · Upload: A1  
Used for: Modelled as the zone 1 obstacles and set dressing.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Prop sheet for 3D modelling, every object in side view at the same scale, evenly spaced on a plain flat light-grey background, even lighting: a stack of three clay pots; a flat cow-dung patty; an iron hand pump with a small puddle; a wooden rope cot with a woven top; an old black bicycle; a tulsi planter on a small painted pedestal; a pair of brass water pots. Hazards (pots, dung, puddle) in warm colours with dark outlines; the helpful cot has a slight glint.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C6 · Lane props, sheet 2

Save as `C6_lane_props_b.png` · 16:9 landscape · first batch · Upload: A1  
Used for: The bullock cart, clothesline and the bamboo basket from the intro.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Second prop sheet, side view, same scale, plain flat light-grey background, even lighting: a bullock cart with big wooden wheels; a clothesline on two bamboo poles with two bright sarees hanging; an upturned dome-shaped bamboo chicken basket; a pile of jute sacks; a wooden doorway with a mango-leaf garland across the top; a small roadside shrine stone with a marigold garland; a clay water pot on a stand.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C7 · Kolam decals

Save as `C7_kolam_decals.png` · 1:1 square · first batch · Upload: A1  
Used for: Cut out as decals for doorsteps and the lane.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Six different kolam floor designs seen straight from above, drawn in clean white rice-flour lines with a few accents in turmeric, kumkum red and green, arranged in a 3 by 2 grid with space between them, on a solid flat dark-grey background so they can be cut out. Simple, bold, hand-drawn lines.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## D. Zone 2: fields and canal

Levels 4 to 6. Paddy fields, bunds, the canal, haystacks and mango trees.

### D1 · Fields mood painting

Save as `D1_fields_mood.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The target for the zone 2 Blender scene.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting, side-on like a side-scrolling game level, a quiet, empty landscape: emerald paddy fields with mirror-like water between the rows, a raised earthen bund path running left to right, an irrigation canal crossed by a narrow plank bridge, conical haystacks, a big mango tree with low climbable branches, tall palms, a stone well with a pulley, a scarecrow with a painted clay-pot head and white egrets in the water. Golden hour: the light turning orange, long reflections in the water, soft mist over the far fields.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D2 · Fields far layer

Save as `D2_fields_far_layer.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The back card for zone 2.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Far parallax layer made only of sky and distance: a golden-hour sky with glowing clouds, distant blue hills, lines of palm trees across faraway fields and a flock of birds, all fading into warm haze at the bottom. Calm, so it can repeat sideways.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D3 · Fields props

Save as `D3_fields_props.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled as the zone 2 obstacles: haystack, canal and plank bridge, well.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Prop sheet for 3D modelling, side view, same scale, plain flat light-grey background, even lighting: a conical haystack; a short stretch of irrigation canal with a narrow wooden plank bridge; a round stone well with a wooden pulley and rope; a scarecrow with a painted clay-pot head and an old shirt; a small canal sluice gate; a section of earthen bund path with grass along its edges.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D4 · Mango tree

Save as `D4_mango_tree.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled with the branch route the kid climbs for mangoes.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Model sheet of a big old mango tree for a platform game: side view on the left, front view on the right, same scale. A thick twisted trunk, two strong low branches that form a walkable route, dense dark-green leaves and ripe mangoes that glint. Orthographic, even flat lighting, plain flat light-grey background.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## E. Zone 3: terraces and market

Levels 7 to 9. Rooftops at sunset, the market at dusk and the lamp-lit temple steps.

### E1 · Rooftops mood painting

Save as `E1_rooftops_mood.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The target for levels 7 and the rooftop stretches.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting, side-on like a side-scrolling game level, the rooftops empty for a moment: a run of connected flat village rooftops at sunset with small gaps between the houses, low parapets, black cylindrical water tanks, red chillies and round papads drying on woven mats, a clothesline, a bamboo ladder, paper kites in the sky and festival bunting strung between houses. The setting sun rims everything in orange and the sky shifts from gold to rose.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E2 · Market mood painting

Save as `E2_market_mood.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The target for level 8, the market day.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting, side-on like a side-scrolling game level: a weekly village market at dusk, a row of stalls with striped cloth awnings at different heights, heaps of vegetables, brass and steel vessels, flower sellers with marigold and jasmine garlands, hens in woven baskets, hanging lanterns starting to glow and a busy crowd as soft silhouettes in the background.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E3 · Temple steps

Save as `E3_temple_steps_mood.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The target for level 9, the final catch.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting for the final level, side-on: wide stone temple steps rising from left to right toward a tall carved temple tower, rows of small clay oil lamps flickering along every step, brass bells, marigold garlands and festival bunting, a big old banyan tree to one side. Blue dusk turning to night, warm lamp light pooling on the stone, a few stars. Magical and calm.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E4 · Rooftop props

Save as `E4_rooftop_props.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled as the zone 3 rooftop obstacles and dressing.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a black cylindrical plastic water tank on a low stand; a section of rooftop parapet wall with a gap; a woven mat of red chillies drying; a woven mat of round papads; a paper kite with a tail; a string of triangular festival bunting.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E5 · Market and temple props

Save as `E5_market_props.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled as the bouncy awnings, stalls and lamp-lit steps.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a market stall with a striped cloth awning in two versions, one high and one low; a flower stall with marigold garlands; a woven basket of vegetables; a stack of brass vessels; a woven basket with two hens; a hanging lantern; a stone temple step segment with three clay oil lamps.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## F. Story frames and screens

The opening story, the wriggle-free gag, the loss screen and Amma's kitchen.

### F1 · Title screen

Save as `F1_title_screen.png` · 16:9 landscape · second batch · Upload: A1, your kid reference art  
Used for: Staged in Blender as the title screen, with room for the logo.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical.

Title screen illustration with empty space at the top centre for a logo: the toddler hero (as in the uploaded reference art) peeks mischievously from behind a low wall at an upturned bamboo basket in a neighbour's yard, and a rooster's beady eye looks back through the gaps in the weave. Late afternoon, warm light, kolam on the ground.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F2 · Story 1: the craving

Save as `F2_story_craving.png` · 16:9 landscape · first batch · Upload: A1, your kid reference art  
Used for: Storyboard for the opening shot of the intro cutscene.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical.

Story frame, The craving: the toddler sits on the doorstep of home, nose in the air and eyes closed in bliss, as a ribbon of curry aroma, drawn as swirling golden steam with tiny spice specks, drifts over the wall from the neighbour's kitchen window. Warm afternoon. Wordless storytelling.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F3 · Story 2: the plan

Save as `F3_story_plan.png` · 16:9 landscape · first batch · Upload: A1, your kid reference art, B5  
Used for: Storyboard and layout for the yard where the basket intro is played.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical; the B5 neighbour sheet, to keep the neighbour's design identical.

Story frame, The plan: the neighbour's yard seen side-on, three upturned bamboo baskets with roosters under them, the neighbour snoring on a rope cot under a tree, and the toddler tiptoeing in with exaggerated sneaky steps, tongue out in concentration. Dappled afternoon light.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F4 · Story 3: the basket

Save as `F4_story_basket.png` · 16:9 landscape · first batch · Upload: A1, your kid reference art  
Used for: Storyboard for the hold-to-lift moment.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical.

Story frame, The basket: a close side view of the toddler slowly lifting a big bamboo basket with both hands, straining; under the rim, the rooster's head and one suspicious eye peek out. Tense and funny, with soft light falling through the basket weave.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F5 · Story 4: the escape

Save as `F5_story_escape.png` · 16:9 landscape · first batch · Upload: A1, your kid reference art, B5  
Used for: Storyboard for the moment the chase begins.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical; the B5 neighbour sheet, to keep the neighbour's design identical.

Story frame, The escape: the rooster bursts out from under the basket in an explosion of feathers, wings wide, while the toddler falls back in surprise and the neighbour sits bolt upright on his cot, shouting and pointing. Dust, feathers and slapstick energy.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F6 · Wriggle-free gag

Save as `F6_story_wriggle_free.png` · 16:9 landscape · second batch · Upload: A1, your kid reference art  
Used for: Storyboard for the gag at the end of levels 1 to 8.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical.

Gag frame: the toddler dives flat out and lands belly-down in the dust with hands closed on nothing, while the rooster pops out of their grip and flutters away overhead looking smug, a single feather floating down onto the toddler's head.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F7 · Rooster escaped

Save as `F7_rooster_escaped.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Staged in Blender as the loss screen.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Loss screen illustration: the rooster stands on a rooftop parapet against a sunset sky, chest out, crowing in triumph; far below, a tiny toddler looks up with hands on hips.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F8 · Story 6: Amma's kitchen

Save as `F8_story_amma_kitchen.png` · 16:9 landscape · second batch · Upload: A1, your kid reference art, B6  
Used for: Storyboard for the final scene. It stops at the handover, as the design doc's risk table asks.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my kid reference art, to keep the toddler's face, proportions and outfit identical; the B6 Amma sheet, to keep Amma's design identical.

Final story frame, Amma's kitchen: a warm, lamp-lit village kitchen with a clay stove, brass and steel vessels on shelves and strings of dried chillies. The toddler proudly holds up the rooster in both arms to Amma, who looks down with surprise and a smile. Golden evening light through a small window. The image captures only this moment of the handover.

Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## T. Textures

Seamless hand-painted textures for Blender materials. These use the texture rules instead of the scene style.

### T1 · Red-earth lane

Save as `T1_tex_earth_lane.png` · 1:1 square · first batch · Upload: A1  
Used for: The lane material for zone 1.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A top-down texture of a packed red-earth village lane: terracotta soil with small pebbles, faint footprints and bicycle tracks, a few dry leaves.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else.
```

### T2 · Lime-washed wall

Save as `T2_tex_limewash_wall.png` · 1:1 square · first batch · Upload: A1  
Used for: The base wall material for the house kit.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A front-on texture of a lime-washed village wall: soft white with a faint blue tint, uneven brush strokes, small chips showing terracotta plaster underneath, slightly dirtier toward the bottom.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else.
```

### T3 · Coloured walls

Save as `T3_tex_coloured_walls.png` · 1:1 square · first batch · Upload: A1  
Used for: Wall variants for the house kit. I split the four squares and make each one tile.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Four separate wall textures in a 2 by 2 grid, each square front-on with soft uneven brush strokes: an indigo-washed wall, a turmeric-yellow wall, a pale pink wall and a weathered sea-green wall.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else.
```

### T4 · Wood, rope and bamboo

Save as `T4_tex_wood_weave.png` · 1:1 square · first batch · Upload: A1  
Used for: Doors, the cot, the basket and the sacks.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Four separate textures in a 2 by 2 grid, each square seen straight on: weathered wooden planks, the woven rope top of a cot, a bamboo basket weave and coarse jute sacking.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else.
```

### T5 · Roofs, floors and stone

Save as `T5_tex_roof_floor_stone.png` · 1:1 square · second batch · Upload: A1  
Used for: Thatch, roof tiles, the courtyard floor and the temple steps.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Four separate textures in a 2 by 2 grid, each square seen straight on: palm-leaf thatch, terracotta roof tiles, a smooth cow-dung-plastered courtyard floor in olive brown, and worn granite temple stone.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else.
```

### T6 · Paddy and canal water

Save as `T6_tex_water.png` · 1:1 square · second batch · Upload: A1  
Used for: The paddy and canal surfaces for zone 2.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Two textures side by side, each filling half the square, seen straight down: shallow paddy-field water with rows of young green rice shoots and a golden sky reflected in it; and muddy-green canal water with soft ripples and a few floating leaves.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else.
```

### T7 · Saree and awning fabrics

Save as `T7_tex_fabrics.png` · 1:1 square · second batch · Upload: A1  
Used for: Sarees on the clotheslines and the market awnings.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Four separate fabric patterns in a 2 by 2 grid, each square flat and seen straight on: kumkum red with a gold border stripe; indigo block print with small white motifs; turmeric and green checks; red-and-white market awning stripes.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else.
```

