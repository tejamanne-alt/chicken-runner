# Chicken Runner — art prompt sheet for Gemini

The same images as [the ChatGPT sheet](prompt-sheet.md), with the same IDs and file names, rewritten for Gemini's image model: full sentences, positive wording, a stated job for every uploaded image, and wider 16:9 and 21:9 shapes for the side-on scenes.

## How to use it

1. Make **A0** first, in a new Gemini chat, uploading your four kid images. Then make **A1**, uploading A0 and your rooster photo.
2. Stay in that chat. Each copied prompt says what every uploaded image is for. Upload the files under *Attach* with each prompt, A0 and A1 included: re-uploading them keeps the kid and the style closest.
3. If the shape comes out wrong, reply: *Make this same image in a 21:9 ultra-wide shape* (or the shape shown).
4. Save each image with its file name, then put them in the repo at `ArtSource/references/` or upload them here, in batches.

Start with the 45 marked *first batch*. Gemini is good at small edits, so ask for just the change: *Using the image you just made, remove the labels and keep everything else the same.* A small sparkle mark in a corner is Gemini's watermark; leave it and I'll paint it out.

**Progress:** 86 of 86 images are in `ArtSource/references/` (checked 23 Nov 2026); first batch still to make: none.

## A. Style anchors

Make these first, in order. A0 fixes the kid's design in the pattu frock, A1 sets the look, and every later prompt matches both.

### A0 · Kid in a pattu frock

✅ in the repo · Save as `A0_kid_pattu_frock_sheet.png` · 16:9 landscape · first batch · Upload: your four kid turnaround images  
Used for: The kid's design for every later image, and the sheet I model and rig the kid from in Blender.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: my four kid turnaround images, for the toddler's face, skin tone, hair, hairband and proportions (change only the outfit, as described).

Character model sheet for 3D modelling of the game's toddler hero, based on the four uploaded reference images (front, back and both side views). Keep the face, skin tone, shoulder-length wavy black hair, leopard-print hairband and chubby toddler proportions exactly as in the references, but change the outfit: replace the T-shirt, shorts, socks and sneakers with a vintage South Indian pattu frock, like one from a 1980s family photo. It is a knee-length silk frock in peacock blue with a wide contrasting border at the hem in magenta and gold zari, woven with a small temple-tower pattern; a fitted bodice with a gold zari neckline; short puffed sleeves edged in gold; and a gently gathered, flared skirt with a soft silk sheen. Bare feet with silver anklets with tiny bells. Show four views side by side at exactly the same scale and height: front, left side, right side and back, standing in a relaxed A-pose with the arms a little away from the body. Draw them perfectly flat and orthographic, like an animation model sheet, lit evenly from the front so nothing casts a shadow, on a plain light-grey background. The sheet holds only the four drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### A1 · Key art

✅ in the repo · Save as `A1_key_art.png` · 16:9 landscape · first batch · Upload: A0, your rooster reference photo  
Used for: Sets the look every other image matches, and my reference for materials and lighting in Blender.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical; my rooster photo, to match his colours and markings.

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Key art for the game. Side-on view of a narrow South Indian village lane in late-afternoon golden light. A small, determined toddler (drawn exactly like the uploaded A0 model sheet: wavy black hair, a leopard-print hairband, a peacock-blue silk pattu frock with a magenta-and-gold border swishing as they run, bare feet with silver anklets) sprints from left to right after a smug country rooster (red comb, orange neck feathers, glossy black tail, like the uploaded rooster photo) who glances back over his shoulder mid-stride. Around them: flat-roofed houses washed in lime-white, indigo and turmeric, white kolam patterns at the doorsteps, a stack of clay pots, a hand pump with a puddle, a rope cot where a sleepy neighbour is just waking up, a tulsi planter, coconut palms and a distant temple tower in warm haze. Dust kicked up by little feet, a few loose feathers in the air, long soft shadows. The kid is on the left third, the rooster on the right.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### A2 · Colour script

✅ in the repo · Save as `A2_colour_script.png` · 16:9 landscape · first batch · Upload: A1  
Used for: The lighting plan across the nine levels: one Blender lighting setup per zone.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A colour script for the whole game: nine small painted panels in a 3 by 3 grid, read left to right and top to bottom, all side-on views of one chase through a South Indian village as the day goes by. Panels 1 to 3: a village lane in warm late afternoon. Panels 4 to 6: paddy fields, an irrigation canal and mango trees at golden hour, the light turning orange. Panel 7: flat rooftops with drying red chillies at sunset. Panel 8: a weekly market at dusk with marigold garlands and glowing lanterns. Panel 9: temple steps at blue dusk lit by rows of small oil lamps. Simple shapes, all about light and colour, with tiny silhouettes of a toddler in a swishing blue silk frock chasing a rooster in every panel.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## B. Characters

Model sheets and pose sheets. Attach your kid reference art and rooster photo where noted.

### B1 · Rooster model sheet

✅ in the repo · Save as `B1_rooster_model_sheet.png` · 16:9 landscape · first batch · Upload: A1, your rooster reference photo  
Used for: Traced in Blender to model the rooster at the right proportions.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); my rooster photo, to match his colours and markings.

Character model sheet of the game's rooster for 3D modelling, based on the uploaded rooster photo: a proud country rooster with a big red comb and wattles, orange-gold neck feathers, a rust-red body, dark wings, a glossy black curved tail and yellow legs. Four views side by side at exactly the same scale and height: left side view, front view, back view and top view, standing in a neutral pose. Draw them perfectly flat and orthographic, like an animation model sheet, lit evenly from the front so nothing casts a shadow, on a plain light-grey background. The sheet holds only the four drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B2 · Rooster pose sheet

✅ in the repo · Save as `B2_rooster_poses.png` · 16:9 landscape · first batch · Upload: A1, B1  
Used for: Key poses for the rooster's run, flutter, taunt, panic and wriggle animations.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the B1 rooster model sheet, to keep the rooster's design identical.

Pose sheet for the same rooster as the uploaded model sheet, all in side view facing right, evenly spaced at the same scale on a plain flat light-grey background: 1) running with one leg forward; 2) running with the other leg forward; 3) fluttering up with wings spread and feet tucked; 4) the smug taunt, turned back to face left, chest puffed out, head thrown back, crowing; 5) panic sprint, eyes wide, feathers flying off; 6) wriggling free upside down, flapping wildly; 7) pecking at the ground; 8) standing proud on one foot. Funny, expressive body language: slapstick, never hurt.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B3 · Kid gameplay poses

✅ in the repo · Save as `B3_kid_poses_gameplay.png` · 16:9 landscape · first batch · Upload: A1, A0  
Used for: Key poses for the nine first-prototype animations on your kid model.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical.

Pose sheet for the toddler hero, keeping the design exactly as in the uploaded A0 model sheet (wavy black hair, leopard-print hairband, peacock-blue pattu frock with a magenta-and-gold border, bare feet with silver anklets). All side view facing right, same scale, plain flat light-grey background: 1) running, contact pose; 2) running, passing pose; 3) jumping up with arms raised; 4) falling with arms flailing; 5) landing in a squat; 6) sliding feet first on their back; 7) vaulting a low wall with both hands on top; 8) stumbling forward, off balance; 9) diving flat out with arms stretched to grab. Let the frock's skirt flare and trail with each motion.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B4 · Kid story poses and faces

✅ in the repo · Save as `B4_kid_story_and_faces.png` · 16:9 landscape · first batch · Upload: A1, A0  
Used for: The four face expressions and the story-animation poses.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical.

Second pose sheet for the same toddler, exactly as in the uploaded A0 model sheet, barefoot with silver anklets. Top row, four face close-ups: neutral, big cheeky grin, shocked with mouth open, straining with cheeks puffed. Bottom row, full body side views facing right: tiptoeing with exaggerated sneaky steps; lifting a big bamboo basket with both hands, straining; a startled jump; carrying a rooster proudly in both arms; cheering with fists up; sulking with arms crossed. Plain flat light-grey background, even lighting.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B5 · Neighbour

✅ in the repo · Save as `B5_neighbour_sheet.png` · 16:9 landscape · first batch · Upload: A1  
Used for: Modelled for the basket intro: asleep on the cot, then waking with a shout.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Character sheet for the sleepy neighbour: a friendly middle-aged village man with a bushy moustache, a white cotton vest and a checked lungi, a little round in the middle. Left: front view and side view standing, same scale, for 3D modelling. Right: napping on a rope cot with one arm over his face, then waking up mid-shout with one arm raised, pointing. Comic and warm, never mean. Plain flat light-grey background, even lighting.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B6 · Amma

✅ in the repo · Save as `B6_amma_sheet.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled for the final kitchen scene.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Character sheet for Amma, the toddler's mother: a warm, kind woman in her thirties wearing a cotton saree in turmeric and indigo, hair in a bun with jasmine flowers, glass bangles. Left: front view and side view standing, same scale, for 3D modelling. Right: three expressions, surprised with a hand on her cheek, laughing, and a stern raised eyebrow with hands on hips. Dignified and loving. Plain flat light-grey background, even lighting.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B7 · Village animals

✅ in the repo · Save as `B7_animals_sheet.png` · 16:9 landscape · second batch · Upload: A1  
Used for: The sleeping dog, hens, buffalo and bullocks that become obstacles and scenery.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Sheet of village animals in side view facing right, at the same scale relative to each other, on a plain flat light-grey background: a street dog asleep curled in the dust; the same dog woken up and barking; three hens pecking; a water buffalo lying in a mud patch; a pair of white bullocks standing. Friendly cartoon proportions.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B8 · Cows and goats

✅ in the repo (Usable: the cow, calf and goats cut out cleanly. The buffalo came out lost in a dust cloud, so make it again only if you want the buffalo.) · Save as `B8_cows_goats.png` · 16:9 landscape · first batch · **new** · Upload: A1, B7  
Used for: More animals, so the same one never appears twice in view.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the B7 animal sheet, to match how animals are drawn and their scale.

Village livestock, drawn like the uploaded B7 animal sheet: a white cow with painted horns and a bell, a brown calf, a goat standing on a low wall, a goat eating leaves, a black goat kid jumping, and a buffalo standing. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B9 · Small animals and birds

✅ in the repo · Save as `B9_small_animals.png` · 16:9 landscape · first batch · **new** · Upload: A1, B7  
Used for: Life on walls and rooftops: cats, crows, parrots, hens with chicks.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the B7 animal sheet, to match how animals are drawn and their scale.

Small village animals and birds, drawn like the uploaded B7 animal sheet: a cat asleep on a wall, three crows on a ledge, a pair of green parrots, a mother hen with five chicks, two white ducks, a peacock with its tail folded, and a striped palm squirrel. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### B10 · Villagers in the background

✅ in the repo · Save as `B10_villagers.png` · 16:9 landscape · second batch · **new** · Upload: A1  
Used for: People going about their day behind the chase.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Background villagers going about their day, drawn simply and warmly in the game's style: a woman drawing a kolam, an old man sitting on a veranda with a walking stick, a man riding a bicycle with a milk can, two kids rolling a tyre with a stick, a woman carrying a water pot on her head, and a vegetable seller with a push cart. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## C. Zone 1: the lane

Levels 1 to 3. Painted houses, verandas, kolam, pots, cots and clotheslines.

### C1 · Lane mood painting

✅ in the repo · Save as `C1_lane_mood.png` · 21:9 ultra-wide · first batch · Upload: A1  
Used for: The target for the zone 1 Blender scene: layout, lighting and atmosphere.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting of the village lane, side-on like a side-scrolling game level. The lane is empty for a moment, waiting for the chase. A packed red-earth lane runs left to right. Flat-roofed houses in lime-white, indigo, turmeric and pale pink with verandas and pillars, wooden doors with mango-leaf garlands, white kolam patterns at each doorstep. Stacked clay pots, a hand pump with a puddle, a rope cot, a bicycle leaning on a wall, a tulsi planter, a clothesline of bright sarees and bamboo ladders up to the rooftops. Behind: coconut palms, then a distant temple tower and hills fading into warm haze. Late afternoon: long shadows across the lane, light shafts through the palms, dust in the air.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C2 · Lane far layer

✅ in the repo · Save as `C2_lane_far_layer.png` · 21:9 ultra-wide · first batch · Upload: A1  
Used for: A painted card at the back of the scene, scrolling slowest.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Far background layer for parallax scrolling, made only of sky and distance: a late-afternoon sky with soft painterly clouds, low hills and a distant South Indian temple tower in silhouette, a few faraway coconut palms, all fading into warm golden haze toward the bottom. Wide and calm, so it can repeat sideways.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C3 · Lane middle layer

✅ in the repo · Save as `C3_lane_mid_layer.png` · 21:9 ultra-wide · first batch · Upload: A1  
Used for: A cut-out card between the far layer and the play lane. Magenta is keyed out.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Middle parallax layer, side-on: a row of coconut palms, banana plants and the backs of distant village houses with tiled and flat roofs, a little hazy and lower in contrast than a foreground would be. Everything else in the image is solid flat magenta (#FF00FF), so the trees and houses can be cut out cleanly.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C4 · House kit elevations

✅ in the repo · Save as `C4_house_kit_elevations.png` · 16:9 landscape · first batch · Upload: A1  
Used for: Traced to build the modular house kit: walls, verandas, parapets, doors and ladder.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Modular building kit for 3D modelling: four flat-roofed South Indian village house fronts seen straight on (front elevations, perfectly flat and orthographic, like an architect's drawing), standing side by side on one baseline. One narrow, in lime-white. One wide, in indigo, with a shaded veranda and two pillars. One in turmeric with a small barred window and a raised sit-out platform by the door. One pale pink with steps up to the door. Each has a low parapet along the roof edge, a wooden door and a painted band at the base. A bamboo ladder leans on one wall. Even flat lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C5 · Lane props, sheet 1

✅ in the repo · Save as `C5_lane_props_a.png` · 16:9 landscape · first batch · Upload: A1  
Used for: Modelled as the zone 1 obstacles and set dressing.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Prop sheet for 3D modelling, every object in side view at the same scale, evenly spaced on a plain flat light-grey background, even lighting: a stack of three clay pots; a flat cow-dung patty; an iron hand pump with a small puddle; a wooden rope cot with a woven top; an old black bicycle; a tulsi planter on a small painted pedestal; a pair of brass water pots. Hazards (pots, dung, puddle) in warm colours with dark outlines; the helpful cot has a slight glint.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C6 · Lane props, sheet 2

✅ in the repo · Save as `C6_lane_props_b.png` · 16:9 landscape · first batch · Upload: A1  
Used for: The bullock cart, clothesline and the bamboo basket from the intro.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Second prop sheet, side view, same scale, plain flat light-grey background, even lighting: a bullock cart with big wooden wheels; a clothesline on two bamboo poles with two bright sarees hanging; an upturned dome-shaped bamboo chicken basket; a pile of jute sacks; a wooden doorway with a mango-leaf garland across the top; a small roadside shrine stone with a marigold garland; a clay water pot on a stand.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C7 · Kolam decals

✅ in the repo · Save as `C7_kolam_decals.png` · 1:1 square · first batch · Upload: A1  
Used for: Cut out as decals for doorsteps and the lane.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Six different kolam floor designs seen straight from above, drawn in clean white rice-flour lines with a few accents in turmeric, kumkum red and green, arranged in a 3 by 2 grid with space between them, on a solid flat dark-grey background so they can be cut out. Simple, bold, hand-drawn lines.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C8 · Lane middle layer 2

✅ in the repo · Save as `C8_lane_mid_layer_2.png` · 21:9 ultra-wide · first batch · **new** · Upload: A1, C3  
Used for: A second distance layer, so the palm band does not repeat.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C3 middle layer, to match its style and haze (but show a different stretch).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Middle parallax layer, side-on, a different stretch from the uploaded C3 layer: a band of terracotta-tiled roofs and banana groves with a white overhead water tank and a few tall palms, a little hazy. Everything else in the image is solid flat magenta (#FF00FF), so the layer can be cut out cleanly.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C9 · Lane middle layer 3

✅ in the repo (Usable: the haze painted round the hillock stays in the layer as a soft patch, which suits a distant layer.) · Save as `C9_lane_mid_layer_3.png` · 21:9 ultra-wide · second batch · **new** · Upload: A1, C3  
Used for: A third distance layer.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C3 middle layer, to match its style and haze (but show a different stretch).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Middle parallax layer, side-on, different again from the uploaded C3 layer: big neem and tamarind trees over thatched roofs, a rocky hillock with a tiny white shrine on top and a line of palms. Everything else in the image is solid flat magenta (#FF00FF), so the layer can be cut out cleanly.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### C10 · Ground details to scatter

✅ in the repo · Save as `C10_ground_details.png` · 16:9 landscape · first batch · **new** · Upload: A1, T1  
Used for: Scattered one by one over the lane, each at a random turn and size, so the ground never repeats.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the T1 earth texture, to match the colour of the red earth.

A sheet of separate ground details for a red-earth village lane, each one seen straight down and drawn in the game's painted style: a few pebbles of different sizes, a small cluster of pebbles, three dry mango leaves, a broken piece of dry coconut frond, a coconut husk, a few twigs, four small grass tufts, two weeds with tiny yellow flowers, a short stretch of bullock-cart wheel rut, a trail of bare child footprints, cow hoof prints, hen footprints, and a patch of dried, cracked mud. Spaced apart so none touch. Even lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## D. Zone 2: fields and canal

Levels 4 to 6. Paddy fields, bunds, the canal, haystacks and mango trees.

### D1 · Fields mood painting

✅ in the repo · Save as `D1_fields_mood.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The target for the zone 2 Blender scene.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting, side-on like a side-scrolling game level, a quiet, empty landscape: emerald paddy fields with mirror-like water between the rows, a raised earthen bund path running left to right, an irrigation canal crossed by a narrow plank bridge, conical haystacks, a big mango tree with low climbable branches, tall palms, a stone well with a pulley, a scarecrow with a painted clay-pot head and white egrets in the water. Golden hour: the light turning orange, long reflections in the water, soft mist over the far fields.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D2 · Fields far layer

✅ in the repo · Save as `D2_fields_far_layer.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The back card for zone 2.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Far parallax layer made only of sky and distance: a golden-hour sky with glowing clouds, distant blue hills, lines of palm trees across faraway fields and a flock of birds, all fading into warm haze at the bottom. Calm, so it can repeat sideways.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D3 · Fields props

✅ in the repo · Save as `D3_fields_props.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled as the zone 2 obstacles: haystack, canal and plank bridge, well.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Prop sheet for 3D modelling, side view, same scale, plain flat light-grey background, even lighting: a conical haystack; a short stretch of irrigation canal with a narrow wooden plank bridge; a round stone well with a wooden pulley and rope; a scarecrow with a painted clay-pot head and an old shirt; a small canal sluice gate; a section of earthen bund path with grass along its edges.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D4 · Mango tree

✅ in the repo · Save as `D4_mango_tree.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled with the branch route the kid climbs for mangoes.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Model sheet of a big old mango tree for a platform game: side view on the left, front view on the right, same scale. A thick twisted trunk, two strong low branches that form a walkable route, dense dark-green leaves and ripe mangoes that glint. Orthographic, even flat lighting, plain flat light-grey background.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D5 · Field buildings

✅ in the repo · Save as `D5_field_buildings.png` · 16:9 landscape · second batch · **new** · Upload: A1, C4, D1  
Used for: The buildings along the zone 2 fields, so no two in view are the same.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style; the D1 fields painting, to match its look and light.

Four buildings that stand at the edge of paddy fields, in the look of the uploaded D1 painting: a small brick pump house with a pipe pouring water into a channel; a farmer's thatched mud hut with a bamboo cattle pen beside it; a little tiled granary raised on stone stilts; and a tiny fieldside shrine of whitewashed stone with a red flag. Draw each building as a flat front elevation for a side-scrolling game, like an architect's drawing: its front faces the viewer squarely, parallel to the picture plane, with no side wall or gable end showing. They all stand on one thin ground line, at the same scale as the uploaded C4 house kit (doors about 2 m tall), evenly spaced with clear gaps between them. Even lighting on a plain light-grey background; signs are blank and the image holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D6 · Crops and field edges

✅ in the repo · Save as `D6_crops_field_edges.png` · 16:9 landscape · second batch · **new** · Upload: A1, D1  
Used for: Pieces the fields are built from: crop rows, bunds and canal banks, never the same twice.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the D1 fields painting, to match its look and light.

Separate pieces for building paddy fields, in the look of the uploaded D1 painting: a strip of young green paddy in water, a strip of tall paddy, a strip of golden ripe paddy, a short stretch of raised earthen bund with grass on top, a canal bank with reeds and lotus leaves, a sugarcane patch, a small haystack, and a row of three palmyra palms. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### D7 · Fields middle layer

✅ in the repo · Save as `D7_fields_mid_layer.png` · 21:9 ultra-wide · second batch · **new** · Upload: A1, C8, D1, D2  
Used for: The band of fields and palms right behind zone 2, between the play area and the D2 far layer.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C8 middle layer, as the layout to copy: a flat side-on strip on magenta; the D1 fields painting, to match its look and light; the D2 far layer, to match its haze.

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Middle parallax layer for the fields: in front, a long low earthen bund with grass along the bottom; behind it, a row of paddy at different heights and greens, a line of palmyra palms, two or three small farmhouses with tiled roofs half hidden by banana plants, and a white egret standing in the paddy, in the light of the uploaded D1 painting and a little paler than the foreground, as if a few hundred metres away. Lay it out exactly like the uploaded C8 layer: a side-on strip of scenery, like a flat stage backdrop, with everything standing along one straight, level ground strip near the bottom. Everything is seen from the side at the same distance, so nothing recedes and there are no fields or roads seen from above and no horizon. The strip runs off the left and right edges so it can repeat sideways. Pure flat magenta (#FF00FF) fills everything above the strip and below its ground, right up to the drawing's edges, and the magenta stays clean, with no haze, glow, mist or light rays over it.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Paint everything crisp and clear, with visible brush texture inside each shape. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## E. Zone 3: terraces and market

Levels 7 to 9. Rooftops at sunset, the market at dusk and the lamp-lit temple steps.

### E1 · Rooftops mood painting

✅ in the repo (Usable as a mood reference; its black plastic water tanks are not used in the game.) · Save as `E1_rooftops_mood.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The target for levels 7 and the rooftop stretches.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting, side-on like a side-scrolling game level, no characters: a run of connected flat Madras-terrace village rooftops of the 1970s at sunset with small gaps between the houses, low parapets, big clay water pots, red chillies and round papads drying on woven mats, a clothesline with cotton saris, a bamboo ladder, paper kites in the sky and festival bunting strung between houses. The setting sun rims everything in orange.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E2 · Market mood painting

✅ in the repo (Usable as a mood reference only; its striped awnings are not used.) · Save as `E2_market_mood.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The target for level 8, the market day.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting, side-on like a side-scrolling game level: a weekly village market at dusk, a row of stalls under plain faded cotton awnings, palm-leaf mats and thatch at different heights, heaps of vegetables, brass and steel vessels, flower sellers with marigold and jasmine garlands, hens in woven baskets, hanging lanterns starting to glow and a busy crowd as soft silhouettes in the background.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E3 · Temple steps

✅ in the repo · Save as `E3_temple_steps_mood.png` · 21:9 ultra-wide · second batch · Upload: A1  
Used for: The target for level 9, the final catch.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Frame it from the side at eye level with a long lens, so the perspective stays flat, like a level in a side-scrolling game.

Environment painting for the final level, side-on: wide stone temple steps rising from left to right toward a tall carved temple tower, rows of small clay oil lamps flickering along every step, brass bells, marigold garlands and festival bunting, a big old banyan tree to one side. Blue dusk turning to night, warm lamp light pooling on the stone, a few stars. Magical and calm.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E4 · Rooftop props

✅ in the repo (Usable, except the black plastic water tank, which is too modern and not used.) · Save as `E4_rooftop_props.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled as the zone 3 rooftop obstacles and dressing.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a big clay water pot on a low stone stand; a section of rooftop parapet wall with a gap; a woven mat of red chillies drying; a woven mat of round papads; a paper kite with a tail; a string of triangular festival bunting.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E5 · Market and temple props

✅ in the repo (Usable, except the two red-and-white striped stalls, which are not used.) · Save as `E5_market_props.png` · 16:9 landscape · second batch · Upload: A1  
Used for: Modelled as the bouncy awnings, stalls and lamp-lit steps.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a market stall under a plain faded indigo cotton awning on bamboo poles, in two versions, one high and one low; a flower stall with marigold garlands; a woven basket of vegetables; a stack of brass vessels; a woven basket with two hens; a hanging lantern; a stone temple step segment with three clay oil lamps.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E6 · Village houses with roof terraces 1

✅ in the repo · Save as `E6_rooftop_houses_1.png` · 21:9 ultra-wide · second batch · **new** · Upload: A1, C4, E1, G10  
Used for: The houses whose flat roofs the kid runs across in zone 3.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style; the E1 rooftops painting, to match its look and sunset light; the G10 potter's house, as an example of a wide, low village house drawn flat and front-on.

Two single-storey village houses of the 1970s, each wide and low the way rural houses are: about 12 m wide and 4 m from the ground to the top of its roof parapet, three times as wide as it is tall. Their flat lime-plastered roofs are terraces a child could run along. In the look of the uploaded E1 painting, drawn flat like the uploaded G10 house. The first is lime-washed, with a long front veranda (thinnai) of raised platforms either side of the door under a sloping terracotta-tiled lean-to on wooden pillars, a kolam at the steps, a tulsi planter, cow-dung cakes drying on its end wall, stone steps climbing the end wall to the roof, and a small haystack and big clay pots on the terrace. The second is mud-plastered in ochre with a red-oxide plinth, a pumpkin creeper spreading over its roof, paddy and coconut fronds drying on the terrace, and a thatched cattle shed built onto one end with a calf tied to a post. Draw them big, side by side with a clear gap between them, so together they fill most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, rather than a narrow, tall town house. Draw each as a flat front elevation for a side-scrolling game, like an architect's drawing: its front faces the viewer squarely, parallel to the picture plane, with no side wall or gable end showing. They all stand on one thin ground line, at the same scale as the uploaded C4 house kit (doors about 2 m tall). Even lighting on a plain light-grey background; signs are blank and the image holds only the drawings, unlabeled. The background is a single flat light grey all over, with no painted ground, sky, haze, dust, mist, glow or blurred scenery anywhere, and every drawing sits wholly inside the frame.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Paint everything crisp and clear, with visible brush texture inside each shape. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E7 · Village houses with roof terraces 2

✅ in the repo · Save as `E7_rooftop_houses_2.png` · 21:9 ultra-wide · second batch · **new** · Upload: A1, C4, E1, G10  
Used for: More rooftop houses, so no two neighbours match.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style; the E1 rooftops painting, to match its look and sunset light; the G10 potter's house, as an example of a wide, low village house drawn flat and front-on.

Two more single-storey village houses of the 1970s, different from each other, each wide and low: about 11 m wide and 4 m to the top of its roof parapet. Their flat roofs are terraces a child could run along. In the look of the uploaded E1 painting, drawn flat like the uploaded G10 house. The first is pale blue lime wash with green-painted wooden shutters, a long low veranda, a bamboo ladder leaning up to the roof, and red chillies and round papads drying on woven mats on the terrace. The second is an old house, its lime wash flaking to show the brick, with a small thatched room on one corner of its roof, firewood stacked on the terrace, a jasmine creeper over the parapet, a rope cot leaning against the front wall and hens pecking by the door. Draw them big, side by side with a clear gap between them, so together they fill most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, rather than a narrow, tall town house. Draw each as a flat front elevation for a side-scrolling game, like an architect's drawing: its front faces the viewer squarely, parallel to the picture plane, with no side wall or gable end showing. They all stand on one thin ground line, at the same scale as the uploaded C4 house kit (doors about 2 m tall). Even lighting on a plain light-grey background; signs are blank and the image holds only the drawings, unlabeled. The background is a single flat light grey all over, with no painted ground, sky, haze, dust, mist, glow or blurred scenery anywhere, and every drawing sits wholly inside the frame.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Paint everything crisp and clear, with visible brush texture inside each shape. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E8 · Shandy stalls 1

✅ in the repo (Usable, except the vegetable stall's red-and-white striped awning, which is not used.) · Save as `E8_market_stalls_1.png` · 21:9 ultra-wide · second batch · **new** · Upload: A1, C4, E2, E5  
Used for: Stall fronts for the zone 3 market, so the row never repeats.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style; the E2 market painting, to match its look and dusk light; the E5 market props, to match how the stalls and goods are drawn.

Three stalls at a 1970s weekly village shandy held on open ground under the trees, in the look of the uploaded E2 painting and drawn like the uploaded E5 props. Each is wide and low, about 5 m wide and under 3 m tall, nearly twice as wide as it is tall, its goods spread out along the ground: a vegetable seller's long rows of tomatoes, brinjals, onions, gourds and greens heaped on jute sacks under a wide plain awning of faded indigo cotton on four bamboo poles; a flower seller sitting among baskets, marigold and jasmine garlands hung along a long bamboo pole under a woven palm-leaf mat; and a brass and copper vessel seller's pots and lamps laid out on a long mat under a low thatched shade. Draw them big, side by side with a clear gap between them, so together they fill most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, rather than a narrow, tall town house. Draw each as a flat front elevation for a side-scrolling game, like an architect's drawing: its front faces the viewer squarely, parallel to the picture plane, with no side wall or gable end showing. They all stand on one thin ground line, at the same scale as the uploaded C4 house kit (doors about 2 m tall). Even lighting on a plain light-grey background; signs are blank and the image holds only the drawings, unlabeled. The background is a single flat light grey all over, with no painted ground, sky, haze, dust, mist, glow or blurred scenery anywhere, and every drawing sits wholly inside the frame.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Paint everything crisp and clear, with visible brush texture inside each shape. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E9 · Shandy stalls 2

✅ in the repo (Usable, except the sweets stall's red-and-white striped awning, which is not used.) · Save as `E9_market_stalls_2.png` · 21:9 ultra-wide · second batch · **new** · Upload: A1, C4, E2, E5  
Used for: More market stalls and carts.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style; the E2 market painting, to match its look and dusk light; the E5 market props, to match how the stalls and goods are drawn.

Three more stalls and carts at a 1970s weekly village shandy, in the look of the uploaded E2 painting and drawn like the uploaded E5 props. Each is wide and low, about 5 m wide and under 3 m tall: a bullock cart loaded with tender coconuts, seen from the side, its two bullocks resting beside it; a sweets seller with a big iron kadai over a wood fire and trays of jalebis and murukku under a long plain, undyed cotton awning; and a potter's clay pots, lamps and toys laid out in rows on the ground under a big black cloth umbrella and a palm-leaf shade. Draw them big, side by side with a clear gap between them, so together they fill most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, rather than a narrow, tall town house. Draw each as a flat front elevation for a side-scrolling game, like an architect's drawing: its front faces the viewer squarely, parallel to the picture plane, with no side wall or gable end showing. They all stand on one thin ground line, at the same scale as the uploaded C4 house kit (doors about 2 m tall). Even lighting on a plain light-grey background; signs are blank and the image holds only the drawings, unlabeled. The background is a single flat light grey all over, with no painted ground, sky, haze, dust, mist, glow or blurred scenery anywhere, and every drawing sits wholly inside the frame.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Paint everything crisp and clear, with visible brush texture inside each shape. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### E10 · Village temple lane

✅ in the repo · Save as `E10_temple_street.png` · 21:9 ultra-wide · second batch · **new** · Upload: A1, C4, E3, G15  
Used for: The buildings along the way to the temple steps in level 9.

```text
Create a 21:9 ultra-wide image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style; the E3 temple steps painting, to match its look and lamp light; the G15 shrine under its tree, as an example of a tree and a village building drawn flat and front-on.

Three buildings on the lane to the village temple, simple and old, in the look of the uploaded E3 painting at dusk, lit only by oil lamps, and drawn flat like the uploaded G15 shrine. Each is wide and low: a long stone mandapam (pillared hall), about 14 m wide and 5 m tall, with a row of carved pillars under a flat stone roof; a long thatched shed, about 10 m wide, where the village's wooden temple chariot is kept, its carved front peeping out; and a 12 m stretch of the temple tank's stone wall with steps going down and a small arched gateway, oil lamps along its ledge. Draw them big, side by side with a clear gap between them, so together they fill most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, rather than a narrow, tall town house. Draw each as a flat front elevation for a side-scrolling game, like an architect's drawing: its front faces the viewer squarely, parallel to the picture plane, with no side wall or gable end showing. They all stand on one thin ground line, at the same scale as the uploaded C4 house kit (doors about 2 m tall). Even lighting on a plain light-grey background; signs are blank and the image holds only the drawings, unlabeled. The background is a single flat light grey all over, with no painted ground, sky, haze, dust, mist, glow or blurred scenery anywhere, and every drawing sits wholly inside the frame.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Paint everything crisp and clear, with visible brush texture inside each shape. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## F. Story frames and screens

The opening story, the wriggle-free gag, the loss screen and Amma's kitchen.

### F1 · Title screen

✅ in the repo · Save as `F1_title_screen.png` · 16:9 landscape · second batch · Upload: A1, A0  
Used for: Staged in Blender as the title screen, with room for the logo.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical.

Title screen illustration with empty space at the top centre for a logo: the toddler hero (as in the uploaded A0 model sheet, in the peacock-blue pattu frock) peeks mischievously from behind a low wall at an upturned bamboo basket in a neighbour's yard, and a rooster's beady eye looks back through the gaps in the weave. Late afternoon, warm light, kolam on the ground. The toddler is barefoot, with silver anklets.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F2 · Story 1: the craving

✅ in the repo · Save as `F2_story_craving.png` · 16:9 landscape · first batch · Upload: A1, A0  
Used for: Storyboard for the opening shot of the intro cutscene.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical.

Story frame, The craving: the toddler sits on the doorstep of home, nose in the air and eyes closed in bliss, as a ribbon of curry aroma, drawn as swirling golden steam with tiny spice specks, drifts over the wall from the neighbour's kitchen window. Warm afternoon. Wordless storytelling. The toddler is barefoot, with silver anklets.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F3 · Story 2: the plan

✅ in the repo · Save as `F3_story_plan.png` · 16:9 landscape · first batch · Upload: A1, A0, B5  
Used for: Storyboard and layout for the yard where the basket intro is played.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical; the B5 neighbour sheet, to keep the neighbour's design identical.

Story frame, The plan: the neighbour's yard seen side-on, three upturned bamboo baskets with roosters under them, the neighbour snoring on a rope cot under a tree, and the toddler tiptoeing in on bare feet with exaggerated sneaky steps, tongue out in concentration, wincing as the bells on their silver anklets jingle. Dappled afternoon light.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F4 · Story 3: the basket

✅ in the repo · Save as `F4_story_basket.png` · 16:9 landscape · first batch · Upload: A1, A0  
Used for: Storyboard for the hold-to-lift moment.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical.

Story frame, The basket: a close side view of the toddler slowly lifting a big bamboo basket with both hands, straining; under the rim, the rooster's head and one suspicious eye peek out. Tense and funny, with soft light falling through the basket weave. The toddler is barefoot, with silver anklets.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F5 · Story 4: the escape

✅ in the repo · Save as `F5_story_escape.png` · 16:9 landscape · first batch · Upload: A1, A0, B5  
Used for: Storyboard for the moment the chase begins.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical; the B5 neighbour sheet, to keep the neighbour's design identical.

Story frame, The escape: the rooster bursts out from under the basket in an explosion of feathers, wings wide, while the toddler falls back in surprise and the neighbour sits bolt upright on his cot, shouting and pointing. Dust, feathers and slapstick energy. The toddler is barefoot, with silver anklets.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F6 · Wriggle-free gag

✅ in the repo · Save as `F6_story_wriggle_free.png` · 16:9 landscape · second batch · Upload: A1, A0  
Used for: Storyboard for the gag at the end of levels 1 to 8.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical.

Gag frame: the toddler dives flat out and lands belly-down in the dust with hands closed on nothing, while the rooster pops out of their grip and flutters away overhead looking smug, a single feather floating down onto the toddler's head. The toddler is barefoot, with silver anklets.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F7 · Rooster escaped

✅ in the repo · Save as `F7_rooster_escaped.png` · 16:9 landscape · second batch · Upload: A1, A0, B1, E1  
Used for: Staged in Blender as the loss screen.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical; the B1 rooster model sheet, to keep the rooster's design identical; the E1 rooftops painting, to match its look and sunset light.

Loss screen illustration, side-on like the game: the rooster stands on a rooftop parapet against a sunset sky like the uploaded E1 painting, chest out, wings spread, crowing in triumph; far below, a tiny toddler in the pattu frock looks up with hands on hips and a determined pout, ready to try again. The toddler is barefoot, with silver anklets. Funny and gentle, never sad. Keep the top third open sky or plain wall, calmer than the rest, so the game can place its buttons and text there; the image itself holds no words. The kid matches the uploaded A0 sheet and the rooster the uploaded B1 sheet.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### F8 · Story 6: Amma's kitchen

✅ in the repo · Save as `F8_story_amma_kitchen.png` · 16:9 landscape · second batch · Upload: A1, A0, B1, B6  
Used for: Storyboard for the final scene. It stops at the handover, as the design doc's risk table asks.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the A0 kid model sheet, to keep the toddler's face, hair, hairband, proportions and pattu frock identical; the B1 rooster model sheet, to keep the rooster's design identical; the B6 Amma sheet, to keep Amma's design identical.

Final story frame, Amma's kitchen, side-on like the game: a warm, lamp-lit village kitchen with a clay stove, brass and steel vessels on wooden shelves and strings of dried chillies. The toddler in the pattu frock proudly holds up the rooster in both arms to Amma, who matches the uploaded B6 sheet and looks down with surprise and a smile; the rooster looks put out. Golden evening light through a small window. The toddler is barefoot, with silver anklets. Nothing shown beyond this moment. Keep the top third open sky or plain wall, calmer than the rest, so the game can place its buttons and text there; the image itself holds no words. The kid matches the uploaded A0 sheet and the rooster the uploaded B1 sheet.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## G. Village buildings

One building per image, so every house on a street can be different. Huts, mud and tin houses, the village head's house, shops and landmarks, all at the C4 scale.

### G1 · Thatched hut

✅ in the repo · Save as `G1_thatched_hut.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: A lane house, and the model for huts built in Blender.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A small mud hut with walls smoothed in red-brown earth and a band of white lime at the base, a steep palm-leaf thatch roof hanging low over the walls, a short wooden door you would duck through, a tiny window with a wooden shutter, a clay pot by the door and a pumpkin vine climbing over the thatch. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G2 · Hut with a bamboo porch

✅ in the repo · Save as `G2_hut_bamboo_porch.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: A lane house with a porch the kid can run under.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A thatched mud hut with a lean-to porch of bamboo poles and a woven palm-mat roof in front, a rope cot under the porch, firewood stacked against the wall and round cow-dung cakes drying in rows on the side wall. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G3 · Orange mud house, tin roof

✅ in the repo · Save as `G3_mud_house_tin_roof.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: A lane house; also the model for tin-roof houses built in Blender.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A narrow one-room house with walls plastered in orange ochre mud, a corrugated tin-sheet roof sloping to one side and weighed down with stones and an old tyre, rust streaks on the tin, a blue-painted wooden plank door, and a small window with a plank shutter propped open on a stick. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G4 · Plank and sheet house

✅ in the repo · Save as `G4_plank_sheet_house.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: A lane house that breaks up the painted rows.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A patched-together house of weathered wooden planks and corrugated sheets in faded orange, blue and rust, on a low mud plinth, with an old saree hung as a curtain for a door, potted chillies on the window ledge and a brass bucket by the step. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G5 · Village head's house

✅ in the repo · Save as `G5_village_head_house.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: The grandest house on the lane: a landmark in level 2 or 3.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

The biggest house on the street: two storeys, walls washed in pale yellow with maroon trim, a long sloping roof of terracotta Mangalore tiles, a deep front veranda with six carved wooden pillars, raised sit-out platforms on both sides of a big carved double door with brass studs, a brass oil lamp by the door, a tulsi planter in front and a wooden easy chair on the veranda. Grand and proud, but still a village house. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G6 · Tiled house with courtyard gate

✅ in the repo · Save as `G6_tiled_house_gate.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: A lane house with a gate and a tree behind its wall.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A single-storey house with a terracotta-tiled roof sloping toward the street, a lime-washed front wall with a wooden gate into a courtyard, a mango tree peeking over the wall, a small window with blue bars and a kolam at the gate. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G7 · Provisions shop

✅ in the repo · Save as `G7_provisions_shop.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: A shopfront on the lane, with a bench and awning.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A small village provisions shop: a narrow shopfront with a corrugated tin awning on wooden poles, wooden shelves of glass jars of sweets, hanging strings of snack packets and a bunch of bananas, a big brass weighing scale on the counter, a wooden bench outside and a painted signboard above with pictures of a jar and a bottle and no letters. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G8 · Tea stall

✅ in the repo · Save as `G8_tea_stall.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: A tiny stall: steam, glasses and a bench, full of life.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A tiny roadside tea stall built of planks under a palm-thatch awning, a big brass kettle steaming on a clay stove, a row of small glass tumblers, a jar of biscuits, a wooden bench with a folded newspaper and a small radio on a shelf. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G9 · Tailor and cycle repair

✅ in the repo · Save as `G9_tailor_cycle_shop.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: Two tiny shops under one awning.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

Two tiny open-fronted shops side by side under one tin awning: a tailor's with a black treadle sewing machine and colourful fabric bolts, and a cycle-repair shop with tyres and inner tubes hanging up and a pump leaning on the wall. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G10 · Potter's house

✅ in the repo · Save as `G10_potters_house.png` · 16:9 landscape · second batch · **new** · Upload: A1, C4  
Used for: Ties in with the clay-pot obstacles: the pots come from here.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A potter's mud house with a thatched work shed beside it, a potter's wheel under the shed, rows of fresh unfired grey pots drying in the sun and stacks of fired terracotta pots in front. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G11 · Weaver's house

✅ in the repo · Save as `G11_weavers_house.png` · 16:9 landscape · second batch · **new** · Upload: A1, C4  
Used for: A nod to the kid's pattu frock: silk being woven.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A silk weaver's house with an open front room showing a wooden pit handloom with a half-woven magenta silk saree, bright silk threads stretched to dry on a frame outside, and lime-washed walls with an indigo band. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G12 · House being built

✅ in the repo · Save as `G12_house_being_built.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: Every real village has one; it adds height and humour.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A village house being built the 1970s way: walls of sun-dried mud bricks halfway up, a bamboo scaffold lashed with coir rope, a wooden door frame already standing in place, a heap of mud mixed with straw, and stacks of terracotta roof tiles and wooden rafters waiting beside it. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G13 · Cattle shed

✅ in the repo · Save as `G13_cattle_shed.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: An open shed: hay, a trough and a calf.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

An open cattle shed with a palm-thatch roof on wooden posts, a stone feeding trough, hay piled at the back, a calf tied to a post and a lime-washed back wall with painted handprints. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G14 · Panchayat office

✅ in the repo · Save as `G14_panchayat_office.png` · 16:9 landscape · second batch · **new** · Upload: A1, C4  
Used for: A civic building for the lane's end or the market.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A small village office: a flat-roofed, lime-plastered building of the 1970s painted pale yellow with a green band, a veranda with square pillars, a blank notice board, a wall clock, a wooden bench outside and a hand pump beside it. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G15 · Village shrine

✅ in the repo · Save as `G15_village_shrine.png` · 16:9 landscape · first batch · **new** · Upload: A1, C4  
Used for: A small roadside shrine under a tree, with bell and lamps.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A small roadside shrine to the village guardian: a little whitewashed shrine with a tiny ornate tower on top, a brass bell at the entrance, marigold garlands and oil lamps, under a big tree with red and yellow threads tied round its trunk. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### G16 · Stone lamp pillar

✅ in the repo · Save as `G16_stone_lamp_pillar.png` · 16:9 landscape · second batch · **new** · Upload: A1, C4  
Used for: A landmark on the skyline behind the houses.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A tall carved stone lamp pillar (deepa stambha) on a stepped stone base, about 9 m high, with little stone ledges for oil lamps all the way up, a small brass bell and marigold garlands tied at its foot: a landmark seen over the rooftops. Show only this one building, as a front elevation for a side-scrolling game: perfectly flat and orthographic like an architect's front elevation. The front wall faces the viewer squarely, parallel to the picture plane; neither side wall shows, and the roof is seen only from the front, with no corner or gable end turned toward the viewer. It stands on a thin ground line, drawn at the same scale and in the same painted style as the uploaded C4 house kit (its doors are about 2 m tall). Even lighting on a plain light-grey background; the image holds only the building, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## H. Trees and plants

Several different trees or plants per image, so no two in view are the same, plus big foreground plants to frame the screen edges.

### H1 · Neem trees

✅ in the repo · Save as `H1_neem_trees.png` · 16:9 landscape · first batch · **new** · Upload: A1, D4  
Used for: Shade trees between houses; three different ones so they never repeat side by side.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the D4 mango tree sheet, to match how trees are drawn.

Three different neem trees side by side: a big old one with a broad dome of small feathery leaves and a grey trunk, a young slender one, and one leaning with a swing tied to a branch. Drawn like the uploaded D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### H2 · Tamarind and drumstick trees

✅ in the repo · Save as `H2_tamarind_drumstick.png` · 16:9 landscape · second batch · **new** · Upload: A1, D4  
Used for: More shade-tree variety.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the D4 mango tree sheet, to match how trees are drawn.

Two tamarind trees with dense fine leaves and hanging brown pods, and two drumstick trees with lacy leaves and long green pods. Drawn like the uploaded D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### H3 · Meeting tree with platform

✅ in the repo · Save as `H3_peepal_platform.png` · 16:9 landscape · second batch · **new** · Upload: A1, G15, H1, C4  
Used for: The village gathering spot: a one-off landmark.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the G15 shrine under its tree, as an example of a tree and a village building drawn flat and front-on; the H1 trees, to match how trees and leaves are drawn; the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

A huge old peepal tree with heart-shaped leaves, its roots gripping a raised square platform of grey stone where villagers sit in the evening; a few small stone idols, clay lamps and flowers at the foot of the trunk, and red and yellow threads tied round it. Drawn flat and front-on like the uploaded G15 shrine, for a side-scrolling game: the platform is seen straight from the front as a low rectangle of stone about 0.8 m high and 6 m wide, with three steps in the middle, its top surface hidden behind its front edge; the tree rises from it about 12 m tall, its canopy wide and spreading. No perspective, nothing seen from above. Standing on a thin ground line at the scale of the uploaded C4 house kit (doors about 2 m tall). Even lighting, no labels. The background is a single flat light grey all over, with no painted ground, sky, haze, dust, mist, glow or blurred scenery anywhere, and every drawing sits wholly inside the frame.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Paint everything crisp and clear, with visible brush texture inside each shape. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### H4 · Coconut palms

✅ in the repo · Save as `H4_coconut_palms.png` · 16:9 landscape · first batch · **new** · Upload: A1, D4  
Used for: Five different palms, so palms never look stamped.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the D4 mango tree sheet, to match how trees are drawn.

Five different coconut palms: a tall straight one, one leaning far over, a pair growing from one spot, a young short palm, and one with a climber's rope ring on the trunk and coconuts in a bunch. Drawn like the uploaded D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### H5 · Banana, papaya and curry-leaf plants

✅ in the repo · Save as `H5_garden_plants.png` · 16:9 landscape · second batch · **new** · Upload: A1, D4  
Used for: Small backyard plants for between houses.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the D4 mango tree sheet, to match how trees are drawn.

Six small backyard plants: a banana plant with a bunch, a torn-leaf banana plant, a papaya tree with fruit, a curry-leaf bush, a clump of sugarcane and a pumpkin vine on a stick frame. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### H6 · Flowering bushes

✅ in the repo · Save as `H6_flowering_bushes.png` · 16:9 landscape · first batch · **new** · Upload: A1, D4  
Used for: Colour by doors and walls; each bush different.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the D4 mango tree sheet, to match how trees are drawn.

Six flowering bushes and creepers: a hibiscus bush with red flowers, a magenta bougainvillea spilling over a wall, a jasmine creeper on a bamboo frame, a pink oleander, crotons in clay pots, and a patch of orange marigolds. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### H7 · Foreground framing plants

✅ in the repo · Save as `H7_foreground_plants.png` · 16:9 landscape · first batch · **new** · Upload: A1  
Used for: Big plants in front of the lane, at the screen's bottom corners, like your story frames.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Five large foreground plants for framing the bottom corners of a game screen, drawn bigger and a little darker than the rest of the scene, as if close to the camera: a clump of big taro leaves, a cluster of tall grass with seed heads, a corner of banana leaves, a broken corner of a lime-washed compound wall with weeds, and a mossy rock with ferns. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain light-grey background with even lighting; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## K. House parts kit

Doors, windows, roof edges and doorstep details. Blender builds endless house variations from these, so a long street never repeats.

### K1 · Doors and windows

✅ in the repo · Save as `K1_doors_windows.png` · 16:9 landscape · second batch · **new** · Upload: A1, C4  
Used for: Fitted to houses Blender builds, so no two front doors match. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

Sheet of village doors and windows for a modular house kit, each shown straight on and separate: a carved double wooden door with brass studs, a plain plank door painted blue, a green-framed door with a marigold garland, a low hut door, a doorway with a hanging saree curtain, a window with wooden shutters open, a window with blue iron bars, and a small window with a plank shutter propped open. Drawn at the scale of the uploaded C4 house kit (doors about 2 m tall). Even lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### K2 · Roof edges and awnings

✅ in the repo · Save as `K2_roof_edges.png` · 16:9 landscape · second batch · **new** · Upload: A1, C4  
Used for: The front edges of roofs Blender builds: thatch, tiles, tin and awnings. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

Six roof edges and awnings for a modular house kit, each a long horizontal strip seen straight on from the front: a palm-thatch eave, a terracotta Mangalore-tile eave, a corrugated tin-sheet eave with rust, a flat-roof parapet with pots on it, a plain faded cotton awning and a bamboo-and-palm-mat awning. Drawn at the scale of the uploaded C4 house kit. Plain flat light-grey background, even lighting, no labels.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

### K3 · Doorstep and wall details

✅ in the repo · Save as `K3_wall_details.png` · 16:9 landscape · second batch · **new** · Upload: A1, C4  
Used for: Small details that make every built house its own.

```text
Create a 16:9 landscape image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the C4 house kit, to match its scale (doors about 2 m tall), its front-on drawing and its painted style.

Sheet of small details for village house fronts, each separate and seen straight on: three different front steps with kolam, a raised sit-out platform, a brass wall lamp, a hanging lantern, a row of cow-dung cakes drying on a wall, a wall shelf with clay pots, a hanging bird feeder and a mango-leaf garland. Drawn at the scale of the uploaded C4 house kit. Even lighting on a plain light-grey background; the sheet holds only the drawings, unlabeled.

It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, chairs, sheets or black water tanks, no half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village, like a painted toy diorama. Characters and props have clean dark outlines, flat saturated colours and soft two-tone cel shading. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. The palette is terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls and paddy green, under warm golden light. The mood is warm, gentle, funny and immersive. The image is clean artwork only: unlabeled, unsigned and borderless.
```

## T. Textures

Seamless hand-painted textures for Blender materials. These use the texture rules instead of the scene style.

### T1 · Red-earth lane

✅ in the repo · Save as `T1_tex_earth_lane.png` · 1:1 square · first batch · Upload: A1  
Used for: The lane material for zone 1.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A top-down texture of a packed red-earth village lane: terracotta soil with small pebbles, faint footprints and bicycle tracks, a few dry leaves.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T2 · Lime-washed wall

✅ in the repo · Save as `T2_tex_limewash_wall.png` · 1:1 square · first batch · Upload: A1  
Used for: The base wall material for the house kit.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A front-on texture of a lime-washed village wall: soft white with a faint blue tint, uneven brush strokes, small chips showing terracotta plaster underneath, slightly dirtier toward the bottom.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T3 · Coloured walls

✅ in the repo · Save as `T3_tex_coloured_walls.png` · 1:1 square · first batch · Upload: A1  
Used for: Wall variants for the house kit. I split the four squares and make each one tile.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Four separate wall textures in a 2 by 2 grid, each square front-on with soft uneven brush strokes: an indigo-washed wall, a turmeric-yellow wall, a pale pink wall and a weathered sea-green wall.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T4 · Wood, rope and bamboo

✅ in the repo · Save as `T4_tex_wood_weave.png` · 1:1 square · first batch · Upload: A1  
Used for: Doors, the cot, the basket and the sacks.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Four separate textures in a 2 by 2 grid, each square seen straight on: weathered wooden planks, the woven rope top of a cot, a bamboo basket weave and coarse jute sacking.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T5 · Roofs, floors and stone

✅ in the repo · Save as `T5_tex_roof_floor_stone.png` · 1:1 square · second batch · Upload: A1  
Used for: Thatch, roof tiles, the courtyard floor and the temple steps.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Four separate textures in a 2 by 2 grid, each square seen straight on: palm-leaf thatch, terracotta roof tiles, a smooth cow-dung-plastered courtyard floor in olive brown, and worn granite temple stone.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T6 · Paddy and canal water

✅ in the repo · Save as `T6_tex_water.png` · 1:1 square · second batch · Upload: A1  
Used for: The paddy and canal surfaces for zone 2.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Two textures side by side, each filling half the square, seen straight down: shallow paddy-field water with rows of young green rice shoots and a golden sky reflected in it; and muddy-green canal water with soft ripples and a few floating leaves.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T7 · Saree and awning fabrics

✅ in the repo · Save as `T7_tex_fabrics.png` · 1:1 square · second batch · Upload: A1  
Used for: Sarees on the clotheslines and the market awnings.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

Four separate fabric patterns in a 2 by 2 grid, each square flat and seen straight on: kumkum red with a gold border stripe; indigo block print with small white motifs; turmeric and green checks; a plain faded madder-red cotton awning cloth.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T8 · Corrugated tin sheet

✅ in the repo · Save as `T8_tex_tin_sheet.png` · 1:1 square · second batch · **new** · Upload: A1  
Used for: Roofs of the tin-roof houses Blender builds. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A front-on texture of an old corrugated tin roofing sheet: silver-grey ridges with patches of orange rust, rust streaks and a few nail heads.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T9 · Orange mud plaster

✅ in the repo · Save as `T9_tex_orange_mud.png` · 1:1 square · second batch · **new** · Upload: A1  
Used for: Walls of the orange mud houses Blender builds. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A front-on texture of a mud-plastered wall in warm orange ochre: hand-smoothed, with finger swirls, small cracks and a few patches where the red-brown earth shows.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T10 · Bare brick

✅ in the repo · Save as `T10_tex_bare_brick.png` · 1:1 square · second batch · **new** · Upload: A1  
Used for: Unfinished upper floors and back walls.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A front-on texture of an unplastered red brick wall: bricks of slightly different reds in straight courses, uneven grey mortar lines, a few chipped corners and a faint splash of old cement. Only the wall, filling the square. The pattern runs off all four edges with no border, frame or standout feature, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T11 · Woven coconut-leaf fence

✅ in the repo · Save as `T11_tex_coconut_leaf_fence.png` · 1:1 square · first batch · **new** · Upload: A1  
Used for: The fences around house compounds, built in Blender: so they look woven by hand, not tiled.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light).

A front-on texture of a village compound fence of dried coconut palm leaves woven in rows that run straight across: tan, straw and grey-brown leaflets folded over thin horizontal sticks, with a few frayed ends, small gaps and darker weathered leaves. It shows only the woven panel, filling the square: no posts, ground, sky or top edge. The pattern runs off all four edges with no border, frame or standout feature, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

### T12 · Plain red earth

✅ in the repo · Save as `T12_tex_plain_red_earth.png` · 1:1 square · first batch · **new** · Upload: A1, T1  
Used for: The grain of the lane's ground, which Blender builds without repeating: it needs earth with no marks in it.

```text
Create a 1:1 square image.

Use the images I've uploaded: the A1 key art, as the style to match closely (painting style, outlines, palette and light); the T1 earth texture, to match the colour of the red earth.

A texture of bare red laterite earth seen straight down from above, in the colours of the uploaded T1 texture: fine dust, crumbs and grit, with soft brush-stroke variation between deep red, red-orange and dusty orange. Only the earth itself: no footprints, tracks, leaves, plants, stones or cracks, and no patch darker or lighter than the rest. The pattern runs off all four edges with no border, frame or standout feature, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Make it a seamless, tileable texture for a 3D game, seen perfectly straight on (straight down for floors) and lit evenly and flatly, so the surface shows no cast shadows, perspective or vignette. Hand-paint it with visible brush strokes and simplified shapes that still read at small size, in a palette of terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white and paddy green. The texture fills the square edge to edge and the image holds nothing else. Only materials a 1970s village would have.
```

