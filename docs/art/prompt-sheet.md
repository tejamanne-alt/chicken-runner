# Chicken Runner — art prompt sheet

Image prompts for ChatGPT, written for the Blender pipeline: every image has an ID, a file name and a shape, so the images come back named for the scenes they feed. The web version has copy buttons and a checklist. Gemini versions of the same prompts, with the same IDs and file names, are in [prompt-sheet-gemini.md](prompt-sheet-gemini.md).

**Progress:** 102 of 114 images are in `ArtSource/references/` (checked 27 Nov 2026); 61 of the 73 first-batch images. First batch still to make: E17, E18, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10.

**The village is celebrating Pongal.** Every image already made gets a festive edit in [section P](#p-pongal-the-festive-repaint) (keep the picture, add the festival); every new image is made for the festival.

## How to use it

1. Make **A0** first, in a new ChatGPT chat, attaching your four kid turnaround images. Then make **A1**, attaching A0 and your rooster photo.
2. Stay in that chat for the rest. Each prompt below is copy-ready: it asks ChatGPT to match A1 and carries the style rules. Attach the files listed under *Attach* (A0 is the kid reference from now on).
3. Save each image with the file name shown.
4. Put the images in the repo at `ArtSource/references/` (or upload them in the chat), in batches, starting with the 73 marked *first batch*.

Regenerate an image when words or labels appear in it, when a model sheet is not side-on and orthographic, or when the background is not plain.

## A. Style anchors

Make these first, in order. A0 fixes the kid's design in the pattu frock, A1 sets the look, and every later prompt matches both.

### A0 · Kid in a pattu frock

✅ in the repo · Save as `A0_kid_pattu_frock_sheet.png` · Landscape 3:2 · first batch · Attach: your four kid turnaround images  
Used for: The kid's design for every later image, and the sheet I model and rig the kid from in Blender.

```text
Landscape 3:2 image.

Character model sheet for 3D modelling of the game's toddler hero, based on the four attached reference images (front, back and both side views). Keep the face, skin tone, shoulder-length wavy black hair, leopard-print hairband and chubby toddler proportions exactly as in the references, but change the outfit: replace the T-shirt, shorts, socks and sneakers with a vintage South Indian pattu frock, like one from a 1980s family photo. It is a knee-length silk frock in peacock blue with a wide contrasting border at the hem in magenta and gold zari, woven with a small temple-tower pattern; a fitted bodice with a gold zari neckline; short puffed sleeves edged in gold; and a gently gathered, flared skirt with a soft silk sheen. Bare feet with silver anklets with tiny bells. Show four views side by side at exactly the same scale and height: front, left side, right side and back, standing in a relaxed A-pose with the arms a little away from the body. Orthographic, no perspective. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### A1 · Key art

✅ in the repo · Save as `A1_key_art.png` · Landscape 3:2 · first batch · Attach: A0, your rooster reference photo  
Used for: Sets the look every other image matches, and my reference for materials and lighting in Blender.

```text
Landscape 3:2 image.

Key art for the game. Side-on view of a narrow South Indian village lane in late-afternoon golden light. A small, determined toddler (drawn exactly like the attached A0 model sheet: wavy black hair, a leopard-print hairband, a peacock-blue silk pattu frock with a magenta-and-gold border swishing as they run, bare feet with silver anklets) sprints from left to right after a smug country rooster (red comb, orange neck feathers, glossy black tail, like the attached rooster photo) who glances back over his shoulder mid-stride. Around them: flat-roofed houses washed in lime-white, indigo and turmeric, white kolam patterns at the doorsteps, a stack of clay pots, a hand pump with a puddle, a rope cot where a sleepy neighbour is just waking up, a tulsi planter, coconut palms and a distant temple tower in warm haze. Dust kicked up by little feet, a few loose feathers in the air, long soft shadows. The kid is on the left third, the rooster on the right.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### A2 · Colour script

✅ in the repo · Save as `A2_colour_script.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: The lighting plan across the nine levels: one Blender lighting setup per zone.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A colour script for the whole game: nine small painted panels in a 3 by 3 grid, read left to right and top to bottom, all side-on views of one chase through a South Indian village as the day goes by. Panels 1 to 3: a village lane in warm late afternoon. Panels 4 to 6: paddy fields, an irrigation canal and mango trees at golden hour, the light turning orange. Panel 7: flat rooftops with drying red chillies at sunset. Panel 8: a weekly market at dusk with marigold garlands and glowing lanterns. Panel 9: temple steps at blue dusk lit by rows of small oil lamps. Simple shapes, all about light and colour, with tiny silhouettes of a toddler in a swishing blue silk frock chasing a rooster in every panel.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## B. Characters

Model sheets and pose sheets. Attach your kid reference art and rooster photo where noted.

### B1 · Rooster model sheet

✅ in the repo · Save as `B1_rooster_model_sheet.png` · Landscape 3:2 · first batch · Attach: A1, your rooster reference photo  
Used for: The rooster's design, kept the same in every later image. For modelling, use the four separate views with the beak closed, B11-B14.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character model sheet of the game's rooster for 3D modelling, based on the attached rooster photo: a proud country rooster with a big red comb and wattles, orange-gold neck feathers, a rust-red body, dark wings, a glossy black curved tail and yellow legs. Four views side by side at exactly the same scale and height: left side view, front view, back view and top view, standing in a neutral pose. Orthographic, no perspective. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B2 · Rooster pose sheet

✅ in the repo · Save as `B2_rooster_poses.png` · Landscape 3:2 · first batch · Attach: A1, B1  
Used for: Key poses for the rooster's run, flutter, taunt, panic and wriggle animations.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Pose sheet for the same rooster as the attached model sheet, all in side view facing right, evenly spaced at the same scale on a plain flat light-grey background: 1) running with one leg forward; 2) running with the other leg forward; 3) fluttering up with wings spread and feet tucked; 4) the smug taunt, turned back to face left, chest puffed out, head thrown back, crowing; 5) panic sprint, eyes wide, feathers flying off; 6) wriggling free upside down, flapping wildly; 7) pecking at the ground; 8) standing proud on one foot. Funny, expressive body language: slapstick, never hurt.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B3 · Kid gameplay poses

✅ in the repo · Save as `B3_kid_poses_gameplay.png` · Landscape 3:2 · first batch · Attach: A1, A0  
Used for: Key poses for the nine first-prototype animations on your kid model.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Pose sheet for the toddler hero, keeping the design exactly as in the attached A0 model sheet (wavy black hair, leopard-print hairband, peacock-blue pattu frock with a magenta-and-gold border, bare feet with silver anklets). All side view facing right, same scale, plain flat light-grey background: 1) running, contact pose; 2) running, passing pose; 3) jumping up with arms raised; 4) falling with arms flailing; 5) landing in a squat; 6) sliding feet first on their back; 7) vaulting a low wall with both hands on top; 8) stumbling forward, off balance; 9) diving flat out with arms stretched to grab. Let the frock's skirt flare and trail with each motion.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B4 · Kid story poses and faces

✅ in the repo · Save as `B4_kid_story_and_faces.png` · Landscape 3:2 · first batch · Attach: A1, A0  
Used for: The four face expressions and the story-animation poses.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Second pose sheet for the same toddler, exactly as in the attached A0 model sheet, barefoot with silver anklets. Top row, four face close-ups: neutral, big cheeky grin, shocked with mouth open, straining with cheeks puffed. Bottom row, full body side views facing right: tiptoeing with exaggerated sneaky steps; lifting a big bamboo basket with both hands, straining; a startled jump; carrying a rooster proudly in both arms; cheering with fists up; sulking with arms crossed. Plain flat light-grey background, even lighting.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B5 · Neighbour

✅ in the repo · Save as `B5_neighbour_sheet.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Modelled for the basket intro: asleep on the cot, then waking with a shout.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character sheet for the sleepy neighbour: a friendly middle-aged village man with a bushy moustache, a white cotton vest and a checked lungi, a little round in the middle. Left: front view and side view standing, same scale, for 3D modelling. Right: napping on a rope cot with one arm over his face, then waking up mid-shout with one arm raised, pointing. Comic and warm, never mean. Plain flat light-grey background, even lighting.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B6 · Amma

✅ in the repo · Save as `B6_amma_sheet.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled for the final kitchen scene.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Character sheet for Amma, the toddler's mother: a warm, kind woman in her thirties wearing a cotton saree in turmeric and indigo, hair in a bun with jasmine flowers, glass bangles. Left: front view and side view standing, same scale, for 3D modelling. Right: three expressions, surprised with a hand on her cheek, laughing, and a stern raised eyebrow with hands on hips. Dignified and loving. Plain flat light-grey background, even lighting.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B7 · Village animals

✅ in the repo · Save as `B7_animals_sheet.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The sleeping dog, hens, buffalo and bullocks that become obstacles and scenery.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Sheet of village animals in side view facing right, at the same scale relative to each other, on a plain flat light-grey background: a street dog asleep curled in the dust; the same dog woken up and barking; three hens pecking; a water buffalo lying in a mud patch; a pair of white bullocks standing. Friendly cartoon proportions.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B8 · Cows and goats

✅ in the repo (Usable: the cow, calf and goats cut out cleanly. The buffalo came out lost in a dust cloud, so make it again only if you want the buffalo.) · Save as `B8_cows_goats.png` · Landscape 3:2 · first batch · **new** · Attach: A1, B7  
Used for: More animals, so the same one never appears twice in view.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Village livestock, drawn like the attached B7 animal sheet: a white cow with painted horns and a bell, a brown calf, a goat standing on a low wall, a goat eating leaves, a black goat kid jumping, and a buffalo standing. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B9 · Small animals and birds

✅ in the repo · Save as `B9_small_animals.png` · Landscape 3:2 · first batch · **new** · Attach: A1, B7  
Used for: Life on walls and rooftops: cats, crows, parrots, hens with chicks.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Small village animals and birds, drawn like the attached B7 animal sheet: a cat asleep on a wall, three crows on a ledge, a pair of green parrots, a mother hen with five chicks, two white ducks, a peacock with its tail folded, and a striped palm squirrel. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B10 · Villagers in the background

✅ in the repo · Save as `B10_villagers.png` · Landscape 3:2 · second batch · **new** · Attach: A1  
Used for: People going about their day behind the chase.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Background villagers going about their day, drawn simply and warmly in the game's style: a woman drawing a kolam, an old man sitting on a veranda with a walking stick, a man riding a bicycle with a milk can, two kids rolling a tyre with a stick, a woman carrying a water pot on her head, and a vegetable seller with a push cart. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B11 · Rooster turnaround: front

✅ in the repo · Save as `B11_rooster_front.png` · Square 1:1 · first batch · **new** · Attach: A1, B1  
Used for: The front view for modelling the rooster in 3D, lined up with B12-B14.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Turnaround view for 3D modelling: the game's rooster seen exactly from the front, facing the viewer, exactly as designed in the attached B1 model sheet: the same big red comb and wattles, orange-gold neck feathers, rust-red body, dark wings, glossy black curved tail and yellow legs, in the same proportions and colours. Its beak is closed: no open mouth, no grin and no crowing, a calm, neutral face with the eyes open. It stands in a neutral pose, wings folded against its body, both feet flat on the ground a little apart, tail held up naturally. One rooster only, the whole body in frame with nothing cropped. Frame it exactly the same way as the other three views of this set, so they line up when stacked: feet standing on a thin ground line 10% up from the bottom edge, the top of the comb 12% down from the top edge, the body centred. Orthographic, no perspective, as in an animation model sheet. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels and no text.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Colours exactly as in the attached model sheet. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B12 · Rooster turnaround: back

✅ in the repo · Save as `B12_rooster_back.png` · Square 1:1 · first batch · **new** · Attach: A1, B1  
Used for: The back view for modelling the rooster in 3D, lined up with B11, B13 and B14.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Turnaround view for 3D modelling: the game's rooster seen exactly from behind, its tail toward the viewer and its head facing away, exactly as designed in the attached B1 model sheet: the same big red comb and wattles, orange-gold neck feathers, rust-red body, dark wings, glossy black curved tail and yellow legs, in the same proportions and colours. The beak is closed and hidden behind the head. It stands in a neutral pose, wings folded against its body, both feet flat on the ground a little apart, tail held up naturally. One rooster only, the whole body in frame with nothing cropped. Frame it exactly the same way as the other three views of this set, so they line up when stacked: feet standing on a thin ground line 10% up from the bottom edge, the top of the comb 12% down from the top edge, the body centred. Orthographic, no perspective, as in an animation model sheet. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels and no text.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Colours exactly as in the attached model sheet. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B13 · Rooster turnaround: left side

✅ in the repo · Save as `B13_rooster_left.png` · Square 1:1 · first batch · **new** · Attach: A1, B1, B11  
Used for: The left side view for modelling the rooster in 3D, lined up with B11, B12 and B14.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Turnaround view for 3D modelling: the game's rooster seen exactly from its left side, in profile, facing left: its beak points to the left edge of the image and its tail to the right, exactly as designed in the attached B1 model sheet: the same big red comb and wattles, orange-gold neck feathers, rust-red body, dark wings, glossy black curved tail and yellow legs, in the same proportions and colours. Its beak is closed: no open mouth, no grin and no crowing, a calm, neutral face with the eyes open. It stands in a neutral pose, wings folded against its body, both feet flat on the ground a little apart, tail held up naturally. Everything is drawn sharp and complete, with clean outlines: both yellow legs and all the toes in full, standing on the line, nothing blurred, faded or in motion, the comb crisp. There is no scenery at all: no ground, earth, grass, sky, clouds, mist or haze, only the flat light-grey background and the thin ground line, framed like the attached B11 front view. One rooster only, the whole body in frame with nothing cropped. Frame it exactly the same way as the other three views of this set, so they line up when stacked: feet standing on a thin ground line 10% up from the bottom edge, the top of the comb 12% down from the top edge, the body centred. Orthographic, no perspective, as in an animation model sheet. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels and no text.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Colours exactly as in the attached model sheet. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### B14 · Rooster turnaround: right side

✅ in the repo · Save as `B14_rooster_right.png` · Square 1:1 · first batch · **new** · Attach: A1, B1, B11  
Used for: The right side view for modelling the rooster in 3D, and the way it faces as it runs in the game.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Turnaround view for 3D modelling: the game's rooster seen exactly from its right side, in profile, facing right: its beak points to the right edge of the image and its tail to the left, exactly as designed in the attached B1 model sheet: the same big red comb and wattles, orange-gold neck feathers, rust-red body, dark wings, glossy black curved tail and yellow legs, in the same proportions and colours. This is its own right side, not a mirrored copy of the left view. Its beak is closed: no open mouth, no grin and no crowing, a calm, neutral face with the eyes open. It stands in a neutral pose, wings folded against its body, both feet flat on the ground a little apart, tail held up naturally. Everything is drawn sharp and complete, with clean outlines: both yellow legs and all the toes in full, standing on the line, nothing blurred, faded or in motion, the comb crisp. There is no scenery at all: no ground, earth, grass, sky, clouds, mist or haze, only the flat light-grey background and the thin ground line, framed like the attached B11 front view. One rooster only, the whole body in frame with nothing cropped. Frame it exactly the same way as the other three views of this set, so they line up when stacked: feet standing on a thin ground line 10% up from the bottom edge, the top of the comb 12% down from the top edge, the body centred. Orthographic, no perspective, as in an animation model sheet. Even, flat lighting with no cast shadows. Plain flat light-grey background. No labels and no text.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Colours exactly as in the attached model sheet. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
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

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C2 · Lane far layer

✅ in the repo · Save as `C2_lane_far_layer.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: A painted card at the back of the scene, scrolling slowest.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Far background layer for parallax scrolling, with no foreground and no ground: a late-afternoon sky with soft painterly clouds, low hills and a distant South Indian temple tower in silhouette, a few faraway coconut palms, all fading into warm golden haze toward the bottom. Wide and calm, so it can repeat sideways.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C3 · Lane middle layer

✅ in the repo · Save as `C3_lane_mid_layer.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: A cut-out card between the far layer and the play lane. Magenta is keyed out.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer, side-on: a row of coconut palms, banana plants and the backs of distant village houses with tiled and flat roofs, a little hazy and lower in contrast than a foreground would be. Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C4 · House kit elevations

✅ in the repo · Save as `C4_house_kit_elevations.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Traced to build the modular house kit: walls, verandas, parapets, doors and ladder.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Modular building kit for 3D modelling: four flat-roofed South Indian village house fronts seen straight on (front elevation, orthographic, no perspective), standing side by side on one baseline. One narrow, in lime-white. One wide, in indigo, with a shaded veranda and two pillars. One in turmeric with a small barred window and a raised sit-out platform by the door. One pale pink with steps up to the door. Each has a low parapet along the roof edge, a wooden door and a painted band at the base. A bamboo ladder leans on one wall. Even flat lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C5 · Lane props, sheet 1

✅ in the repo · Save as `C5_lane_props_a.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: Modelled as the zone 1 obstacles and set dressing.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet for 3D modelling, every object in side view at the same scale, evenly spaced on a plain flat light-grey background, even lighting: a stack of three clay pots; a flat cow-dung patty; an iron hand pump with a small puddle; a wooden rope cot with a woven top; an old black bicycle; a tulsi planter on a small painted pedestal; a pair of brass water pots. Hazards (pots, dung, puddle) in warm colours with dark outlines; the helpful cot has a slight glint.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C6 · Lane props, sheet 2

✅ in the repo · Save as `C6_lane_props_b.png` · Landscape 3:2 · first batch · Attach: A1  
Used for: The bullock cart, clothesline and the bamboo basket from the intro.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Second prop sheet, side view, same scale, plain flat light-grey background, even lighting: a bullock cart with big wooden wheels; a clothesline on two bamboo poles with two bright sarees hanging; an upturned dome-shaped bamboo chicken basket; a pile of jute sacks; a wooden doorway with a mango-leaf garland across the top; a small roadside shrine stone with a marigold garland; a clay water pot on a stand.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C7 · Kolam decals

✅ in the repo · Save as `C7_kolam_decals.png` · Square 1:1 · first batch · Attach: A1  
Used for: Cut out as decals for doorsteps and the lane.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Six different kolam floor designs seen straight from above, drawn in clean white rice-flour lines with a few accents in turmeric, kumkum red and green, arranged in a 3 by 2 grid with space between them, on a solid flat dark-grey background so they can be cut out. Simple, bold, hand-drawn lines.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C8 · Lane middle layer 2

✅ in the repo · Save as `C8_lane_mid_layer_2.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C3  
Used for: A second distance layer, so the palm band does not repeat.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer, side-on, a different stretch from the attached C3 layer: a band of terracotta-tiled roofs and banana groves with a white overhead water tank and a few tall palms, a little hazy. Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C9 · Lane middle layer 3

✅ in the repo (Usable: the haze painted round the hillock stays in the layer as a soft patch, which suits a distant layer.) · Save as `C9_lane_mid_layer_3.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C3  
Used for: A third distance layer.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer, side-on, different again from the attached C3 layer: big neem and tamarind trees over thatched roofs, a rocky hillock with a tiny white shrine on top and a line of palms. Isolated on a solid flat magenta (#FF00FF) background so it can be cut out. No sky and no ground.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### C10 · Ground details to scatter

✅ in the repo · Save as `C10_ground_details.png` · Landscape 3:2 · first batch · **new** · Attach: A1, T1  
Used for: Scattered one by one over the lane, each at a random turn and size, so the ground never repeats.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A sheet of separate ground details for a red-earth village lane, each one seen straight down and drawn in the game's painted style: a few pebbles of different sizes, a small cluster of pebbles, three dry mango leaves, a broken piece of dry coconut frond, a coconut husk, a few twigs, four small grass tufts, two weeds with tiny yellow flowers, a short stretch of bullock-cart wheel rut, a trail of bare child footprints, cow hoof prints, hen footprints, and a patch of dried, cracked mud. Spaced apart so none touch. Plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

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

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D2 · Fields far layer

✅ in the repo · Save as `D2_fields_far_layer.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The back card for zone 2.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Far parallax layer with no foreground and no ground: a golden-hour sky with glowing clouds, distant blue hills, lines of palm trees across faraway fields and a flock of birds, all fading into warm haze at the bottom. Calm, so it can repeat sideways.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D3 · Fields props

✅ in the repo · Save as `D3_fields_props.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled as the zone 2 obstacles: haystack, canal and plank bridge, well.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet for 3D modelling, side view, same scale, plain flat light-grey background, even lighting: a conical haystack; a short stretch of irrigation canal with a narrow wooden plank bridge; a round stone well with a wooden pulley and rope; a scarecrow with a painted clay-pot head and an old shirt; a small canal sluice gate; a section of earthen bund path with grass along its edges.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D4 · Mango tree

✅ in the repo · Save as `D4_mango_tree.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled with the branch route the kid climbs for mangoes.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Model sheet of a big old mango tree for a platform game: side view on the left, front view on the right, same scale. A thick twisted trunk, two strong low branches that form a walkable route, dense dark-green leaves and ripe mangoes that glint. Orthographic, even flat lighting, plain flat light-grey background.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D5 · Field buildings

✅ in the repo · Save as `D5_field_buildings.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4, D1  
Used for: The buildings along the zone 2 fields, so no two in view are the same.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Four buildings that stand at the edge of paddy fields, in the look of the attached D1 painting: a small brick pump house with a pipe pouring water into a channel; a farmer's thatched mud hut with a bamboo cattle pen beside it; a little tiled granary raised on stone stilts; and a tiny fieldside shrine of whitewashed stone with a red flag. Each building as a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All standing on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall), evenly spaced and not touching. Plain flat light-grey background, even lighting, no labels and no writing on any sign.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D6 · Crops and field edges

✅ in the repo · Save as `D6_crops_field_edges.png` · Landscape 3:2 · second batch · **new** · Attach: A1, D1  
Used for: Pieces the fields are built from: crop rows, bunds and canal banks, never the same twice.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Separate pieces for building paddy fields, in the look of the attached D1 painting: a strip of young green paddy in water, a strip of tall paddy, a strip of golden ripe paddy, a short stretch of raised earthen bund with grass on top, a canal bank with reeds and lotus leaves, a sugarcane patch, a small haystack, and a row of three palmyra palms. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D7 · Fields middle layer

✅ in the repo · Save as `D7_fields_mid_layer.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C8, D1, D2  
Used for: The band of fields and palms right behind zone 2, between the play area and the D2 far layer.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer for the fields: in front, a long low earthen bund with grass along the bottom; behind it, a row of paddy at different heights and greens, a line of palmyra palms, two or three small farmhouses with tiled roofs half hidden by banana plants, and a white egret standing in the paddy, in the light of the attached D1 painting and a little paler than the foreground, as if a few hundred metres away. Lay it out exactly like the attached C8 layer: a side-on strip of scenery, like a flat stage backdrop, with everything standing along one straight, level ground strip near the bottom. Nothing recedes into the distance: no perspective, no fields or roads seen from above, no horizon. The strip runs off the left and right edges so it can repeat sideways. Pure flat magenta (#FF00FF) fills everything above the strip and below its ground, right up to the drawing's edges, with no haze, glow, mist or light rays over the magenta.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D8 · Field buildings 2

✅ in the repo · Save as `D8_field_buildings_2.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, D1, D5  
Used for: More buildings along the far edge of the fields, so none repeats in view.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more structures that stand at the edge of paddy fields, in the look of the attached D1 painting, a 1970s South Indian farming village, drawn like the attached D5 buildings: a kavalai well, a stone well with a sloping earth ramp where a pair of bullocks draws up a big leather water bag on a rope over a wooden pulley frame; a farmer's watch platform (paran), a small thatched hut raised high on four bamboo poles with a bamboo ladder; and a round threshing floor of beaten earth with a stone roller, heaps of paddy straw and a winnowing basket, beside a small thatched shed for the plough and tools. Each piece complete on its own, with a clear gap between them. Each building as a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All standing on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall), evenly spaced and not touching. Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D9 · Canal pieces

✅ in the repo · Save as `D9_canal_pieces.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D1, D3  
Used for: Things along the canals: water lifts, a stone bridge, a bathing ghat, so every canal crossing differs.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate pieces for the irrigation canals, in the look of the attached D1 painting, a 1970s South Indian farming village, each drawn exactly from the side as a flat elevation, like the attached D3 props: no cut-away block of earth, no view from above, no water drawn under it, each standing on one thin ground line: a picottah (etram), a long wooden counterpoise pole on a forked post with a clay pot on one end and a stone weight on the other, for lifting water from the canal; a narrow bridge of two long granite slabs on stone piers; a few stone steps (a ghat) going down into the water, with a flat washing stone and a brass pot; and a small wooden shutter sluice set in a brick wall across a channel. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D10 · Life in the fields

✅ in the repo · Save as `D10_field_life.png` · Landscape 3:2 · first batch · **new** · Attach: A1, B7, B10  
Used for: People and animals working the fields in the background, so the fields feel lived in.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Separate figures for the fields, in the look of the attached D1 painting, a 1970s South Indian farming village, drawn like the attached B7 animals and B10 villagers, side view: a farmer ploughing with two white bullocks and a wooden plough; three women in saris bent over transplanting paddy seedlings in a row; a herd boy with a stick and four goats; a water buffalo wallowing in mud up to its back with an egret on it; a duck herder with a long bamboo stick and a flock of ducks; and a farmer carrying a bundle of paddy sheaves on his head. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D11 · Field trees and plants

✅ in the repo · Save as `D11_field_trees.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D4, H1  
Used for: Trees and bushes that grow along field bunds and canals, so the far edge of the fields never repeats.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Separate trees and plants that grow along field bunds and canals, in the look of the attached D1 painting, a 1970s South Indian farming village, drawn like the attached D4 and H1 trees, side view: a lone banyan with hanging aerial roots; a thorny babul (karuvelam) tree; a tall clump of bamboo; a screwpine (thazhai) bush with long spiky leaves at the water's edge; a row of young casuarina trees; and a hedge of agave and cactus. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D12 · More crops

✅ in the repo · Save as `D12_more_crops.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D1, D6  
Used for: More crops to plant field by field, so each field looks different.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Separate horizontal strips of crops for building fields, in the look of the attached D1 painting, a 1970s South Indian farming village, drawn like the attached D6 strips, each a long low strip seen from the side: a seedbed of dense, bright green paddy seedlings in water; a harvested field with stubble and sheaves of paddy stacked in small heaps; tall sorghum (cholam) with heavy seed heads; low groundnut plants in rows; cotton plants with white bolls; and a strip of banana plants. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### D13 · Fields middle layer 2

✅ in the repo · Save as `D13_fields_mid_layer_2.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C8, D1, D7  
Used for: A second band of distant fields, so the one behind the fields doesn't repeat.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Middle parallax layer for the fields, different from the attached D7 band: in front, a long low earthen bund with grass; behind it, golden ripe paddy, a few haystacks, a small hamlet of thatched huts under coconut palms, a canal with a granite slab bridge, a herd of grazing cattle and a line of palmyra palms, in the light of the attached D1 painting and a little paler than the foreground, as if a few hundred metres away. Lay it out exactly like the attached C8 layer: a side-on strip of scenery, like a flat stage backdrop, with everything standing along one straight, level ground strip near the bottom. Nothing recedes into the distance: no perspective, no fields or roads seen from above, no horizon. The strip runs off the left and right edges so it can repeat sideways. Pure flat magenta (#FF00FF) fills everything above the strip and below its ground, right up to the drawing's edges, with no haze, glow, mist or light rays over the magenta.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## E. Zone 3: terraces and market

Levels 7 to 9. Rooftops at sunset, the market at dusk and the lamp-lit temple steps.

### E1 · Rooftops mood painting

✅ in the repo (Usable as a mood reference; its black plastic water tanks are not used in the game.) · Save as `E1_rooftops_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for levels 7 and the rooftop stretches.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting, side-on like a side-scrolling game level, no characters: a run of connected flat Madras-terrace village rooftops of the 1970s at sunset with small gaps between the houses, low parapets, big clay water pots, red chillies and round papads drying on woven mats, a clothesline with cotton saris, a bamboo ladder, paper kites in the sky and festival bunting strung between houses. The setting sun rims everything in orange.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E2 · Market mood painting

✅ in the repo (Usable as a mood reference only; its striped awnings are not used.) · Save as `E2_market_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for level 8, the market day.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting, side-on like a side-scrolling game level: a weekly village market at dusk, a row of stalls under plain faded cotton awnings, palm-leaf mats and thatch at different heights, heaps of vegetables, brass and steel vessels, flower sellers with marigold and jasmine garlands, hens in woven baskets, hanging lanterns starting to glow and a busy crowd as soft silhouettes in the background.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E3 · Temple steps

✅ in the repo · Save as `E3_temple_steps_mood.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: The target for level 9, the final catch.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Environment painting for the final level, side-on: wide stone temple steps rising from left to right toward a tall carved temple tower, rows of small clay oil lamps flickering along every step, brass bells, marigold garlands and festival bunting, a big old banyan tree to one side. Blue dusk turning to night, warm lamp light pooling on the stone, a few stars. Magical and calm.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E4 · Rooftop props

✅ in the repo (Usable, except the black plastic water tank, which is too modern and not used.) · Save as `E4_rooftop_props.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled as the zone 3 rooftop obstacles and dressing.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a big clay water pot on a low stone stand; a section of rooftop parapet wall with a gap; a woven mat of red chillies drying; a woven mat of round papads; a paper kite with a tail; a string of triangular festival bunting.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E5 · Market and temple props

✅ in the repo (Usable, except the two red-and-white striped stalls, which are not used.) · Save as `E5_market_props.png` · Landscape 3:2 · second batch · Attach: A1  
Used for: Modelled as the bouncy awnings, stalls and lamp-lit steps.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Prop sheet, side view, same scale, plain flat light-grey background, even lighting: a market stall under a plain faded indigo cotton awning on bamboo poles, in two versions, one high and one low; a flower stall with marigold garlands; a woven basket of vegetables; a stack of brass vessels; a woven basket with two hens; a hanging lantern; a stone temple step segment with three clay oil lamps.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E6 · Village houses with roof terraces 1

✅ in the repo · Save as `E6_rooftop_houses_1.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4, E1, G10  
Used for: The houses whose flat roofs the kid runs across in zone 3.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Two single-storey village houses of the 1970s, each wide and low the way rural houses are: about 12 m wide and 4 m from the ground to the top of its roof parapet, three times as wide as it is tall. Their flat lime-plastered roofs are terraces a child could run along. In the look of the attached E1 painting, drawn flat like the attached G10 house. The first is lime-washed, with a long front veranda (thinnai) of raised platforms either side of the door under a sloping terracotta-tiled lean-to on wooden pillars, a kolam at the steps, a tulsi planter, cow-dung cakes drying on its end wall, stone steps climbing the end wall to the roof, and a small haystack and big clay pots on the terrace. The second is mud-plastered in ochre with a red-oxide plinth, a pumpkin creeper spreading over its roof, paddy and coconut fronds drying on the terrace, and a thatched cattle shed built onto one end with a calf tied to a post. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E7 · Village houses with roof terraces 2

✅ in the repo · Save as `E7_rooftop_houses_2.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4, E1, G10  
Used for: More rooftop houses, so no two neighbours match.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Two more single-storey village houses of the 1970s, different from each other, each wide and low: about 11 m wide and 4 m to the top of its roof parapet. Their flat roofs are terraces a child could run along. In the look of the attached E1 painting, drawn flat like the attached G10 house. The first is pale blue lime wash with green-painted wooden shutters, a long low veranda, a bamboo ladder leaning up to the roof, and red chillies and round papads drying on woven mats on the terrace. The second is an old house, its lime wash flaking to show the brick, with a small thatched room on one corner of its roof, firewood stacked on the terrace, a jasmine creeper over the parapet, a rope cot leaning against the front wall and hens pecking by the door. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E8 · Shandy stalls 1

✅ in the repo (Usable, except the vegetable stall's red-and-white striped awning, which is not used.) · Save as `E8_market_stalls_1.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4, E2, E5  
Used for: Stall fronts for the zone 3 market, so the row never repeats.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three stalls at a 1970s weekly village shandy held on open ground under the trees, in the look of the attached E2 painting and drawn like the attached E5 props. Each is wide and low, about 5 m wide and under 3 m tall, nearly twice as wide as it is tall, its goods spread out along the ground: a vegetable seller's long rows of tomatoes, brinjals, onions, gourds and greens heaped on jute sacks under a wide plain awning of faded indigo cotton on four bamboo poles; a flower seller sitting among baskets, marigold and jasmine garlands hung along a long bamboo pole under a woven palm-leaf mat; and a brass and copper vessel seller's pots and lamps laid out on a long mat under a low thatched shade. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E9 · Shandy stalls 2

✅ in the repo (Usable, except the sweets stall's red-and-white striped awning, which is not used.) · Save as `E9_market_stalls_2.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4, E2, E5  
Used for: More market stalls and carts.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls and carts at a 1970s weekly village shandy, in the look of the attached E2 painting and drawn like the attached E5 props. Each is wide and low, about 5 m wide and under 3 m tall: a bullock cart loaded with tender coconuts, seen from the side, its two bullocks resting beside it; a sweets seller with a big iron kadai over a wood fire and trays of jalebis and murukku under a long plain, undyed cotton awning; and a potter's clay pots, lamps and toys laid out in rows on the ground under a big black cloth umbrella and a palm-leaf shade. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E10 · Village temple lane

✅ in the repo · Save as `E10_temple_street.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4, E3, G15  
Used for: The buildings along the way to the temple steps in level 9.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three buildings on the lane to the village temple, simple and old, in the look of the attached E3 painting at dusk, lit only by oil lamps, and drawn flat like the attached G15 shrine. Each is wide and low: a long stone mandapam (pillared hall), about 14 m wide and 5 m tall, with a row of carved pillars under a flat stone roof; a long thatched shed, about 10 m wide, where the village's wooden temple chariot is kept, its carved front peeping out; and a 12 m stretch of the temple tank's stone wall with steps going down and a small arched gateway, oil lamps along its ledge. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E11 · Shandy stalls 3

✅ in the repo · Save as `E11_shandy_stalls_3.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, E2, E8  
Used for: More stalls, so the market's stalls can stand side by side with none repeating within two screens.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall, its goods spread along the ground: a spice and grain seller with heaps of red chillies, turmeric, tamarind and rice in open jute sacks and brass measuring pots, under a plain faded turmeric-yellow cotton awning on bamboo poles; a betel-leaf and areca-nut seller sitting on a raised wooden plank under a woven palm-leaf umbrella; and a cloth seller with folded cotton saris and veshtis piled on a rope cot under a low thatched shade. These stalls will stand side by side in a long row with stalls from the other sheets, so each is complete on its own, its shade and goods inside its own width. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E12 · Shandy stalls 4

✅ in the repo · Save as `E12_shandy_stalls_4.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, E2, E8  
Used for: More stalls, so the market's stalls can stand side by side with none repeating within two screens.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall: a palm-fruit seller with bunches of palmyra fruit and tender nungu in cane baskets under a palm-frond shade; a buttermilk and jaggery seller with big clay pots on a stand and blocks of jaggery on banana leaves, under a plain faded indigo cotton awning; and a basket weaver with bamboo baskets, winnowing trays and mats stacked high around them, under a thatched shade. These stalls will stand side by side in a long row with stalls from the other sheets, so each is complete on its own, its shade and goods inside its own width. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E13 · Shandy stalls 5

✅ in the repo · Save as `E13_shandy_stalls_5.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, E2, E8  
Used for: More stalls, so the market's stalls can stand side by side with none repeating within two screens.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall: a vegetable seller with heaps of brinjals, ladies' fingers, drumsticks, gourds, onions and greens on jute sacks and banana leaves, under a plain faded madder-red cotton awning on bamboo poles; a groundnut seller roasting peanuts in hot sand in a big iron pan over a clay stove, with paper cones; and a parrot astrologer sitting on a mat under a black cloth umbrella, a green parrot in a small cane cage and a fan of fortune cards with pictures and no writing. These stalls will stand side by side in a long row with stalls from the other sheets, so each is complete on its own, its shade and goods inside its own width. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E14 · Shandy stalls 6

✅ in the repo · Save as `E14_shandy_stalls_6.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, E2, E8  
Used for: More stalls, so the market's stalls can stand side by side with none repeating within two screens.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall: a sweets and snacks seller with trays of murukku, laddus and jalebis and glass jars on a wooden plank, under a plain undyed cotton awning; a sugarcane-juice seller with a hand-cranked iron press on a wooden stand, a bundle of sugarcane and brass tumblers, under a woven palm-leaf shade; and a seller of korai-grass mats, palm brooms and coir rope, rolled and stacked under a low thatched shade. These stalls will stand side by side in a long row with stalls from the other sheets, so each is complete on its own, its shade and goods inside its own width. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E15 · Shandy stalls 7

✅ in the repo · Save as `E15_shandy_stalls_7.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, E2, E8  
Used for: More stalls, so the market's stalls can stand side by side with none repeating within two screens.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall: a dried-fish seller with salted fish laid out on palm-leaf mats and in cane baskets, under a low thatched shade; a bangle and kumkum seller with wooden racks of glass bangles and brass bowls of kumkum, turmeric and sandal paste, under a plain faded indigo cotton awning; and a banana seller with whole green and yellow bunches hanging from a bamboo frame, under a palm-frond shade. These stalls will stand side by side in a long row with stalls from the other sheets, so each is complete on its own, its shade and goods inside its own width. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E16 · Shandy stalls 8

✅ in the repo · Save as `E16_shandy_stalls_8.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, E2, E8  
Used for: More stalls, so the market's stalls can stand side by side with none repeating within two screens.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall: a cobbler sitting under a big black cloth umbrella with leather sandals and his tools on a mat; a village barber's spot under a palm-leaf shade, a small wooden stool, a mirror hung on a pole and a brass bowl of water; and a knife and sickle sharpener with a pedal-driven grindstone on a wooden frame, blades laid out on a cloth. These stalls will stand side by side in a long row with stalls from the other sheets, so each is complete on its own, its shade and goods inside its own width. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E17 · Shandy stalls 9

🔁 make again: Came out as a whole market of many small stalls (one with a striped awning): make it again with the updated prompt, exactly three big stalls. · prompt updated · Save as `E17_shandy_stalls_9.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, E2, E8  
Used for: More stalls, so the market's stalls can stand side by side with none repeating within two screens.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall: a salt seller with a white heap of sea salt on a bullock cart, a wooden measure and a sack; a cattle-fair seller of brass cattle bells, painted horn caps and coir ropes hung from a bamboo frame under a plain undyed cotton awning; and a toy seller with lacquered wooden toys, spinning tops, clay whistles and a tall pole of paper windmills, under a palm-leaf shade. Exactly these three stalls and nothing else: not a market scene, no other stalls, no crowd; each one big, with at most its one seller. These stalls will stand side by side in a long row with stalls from the other sheets, so each is complete on its own, its shade and goods inside its own width. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### E18 · Shandy stalls 10

🔁 make again: Came out as a whole market of many small stalls (one with a striped awning): make it again with the updated prompt, exactly three big stalls. · prompt updated · Save as `E18_shandy_stalls_10.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4, E2, E8  
Used for: More stalls, so the market's stalls can stand side by side with none repeating within two screens.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three more stalls at a 1970s weekly village shandy, different from the attached E8 stalls but drawn the same way. Each is wide and low, about 5 m wide and under 3 m tall: an idli and dosa woman with a clay stove, an iron griddle and stacks of banana leaves, under a thatched lean-to; a herb and village-medicine seller with dried roots, barks and leaves in cane trays and small brass boxes, under a plain faded turmeric-yellow cotton awning; and a pickle seller with big glazed stoneware jars (bharanis) and cloth-tied lids on a wooden plank, under a woven palm-leaf shade. Exactly these three stalls and nothing else: not a market scene, no other stalls, no crowd; each one big, with at most its one seller. These stalls will stand side by side in a long row with stalls from the other sheets, so each is complete on its own, its shade and goods inside its own width. Draw them big, side by side with a clear gap between them, together filling most of the image's width. Each one is wide and low, much wider than it is tall, as rural village buildings are, never a narrow, tall town house. Each is a flat front elevation for a side-scrolling game: its front faces the viewer squarely, parallel to the picture, so no side wall or gable end shows and there is no perspective. All stand on one thin ground line, at the same scale as the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels and no writing on any sign. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
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

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F2 · Story 1: the craving

✅ in the repo · Save as `F2_story_craving.png` · Landscape 3:2 · first batch · Attach: A1, A0  
Used for: Storyboard for the opening shot of the intro cutscene.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The craving: the toddler sits on the doorstep of home, nose in the air and eyes closed in bliss, as a ribbon of curry aroma, drawn as swirling golden steam with tiny spice specks, drifts over the wall from the neighbour's kitchen window. Warm afternoon. Wordless storytelling. The toddler is barefoot, with silver anklets.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F3 · Story 2: the plan

✅ in the repo · Save as `F3_story_plan.png` · Landscape 3:2 · first batch · Attach: A1, A0, B5  
Used for: Storyboard and layout for the yard where the basket intro is played.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The plan: the neighbour's yard seen side-on, three upturned bamboo baskets with roosters under them, the neighbour snoring on a rope cot under a tree, and the toddler tiptoeing in on bare feet with exaggerated sneaky steps, tongue out in concentration, wincing as the bells on their silver anklets jingle. Dappled afternoon light.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F4 · Story 3: the basket

✅ in the repo · Save as `F4_story_basket.png` · Landscape 3:2 · first batch · Attach: A1, A0  
Used for: Storyboard for the hold-to-lift moment.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The basket: a close side view of the toddler slowly lifting a big bamboo basket with both hands, straining; under the rim, the rooster's head and one suspicious eye peek out. Tense and funny, with soft light falling through the basket weave. The toddler is barefoot, with silver anklets.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F5 · Story 4: the escape

✅ in the repo · Save as `F5_story_escape.png` · Landscape 3:2 · first batch · Attach: A1, A0, B5  
Used for: Storyboard for the moment the chase begins.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Story frame, The escape: the rooster bursts out from under the basket in an explosion of feathers, wings wide, while the toddler falls back in surprise and the neighbour sits bolt upright on his cot, shouting and pointing. Dust, feathers and slapstick energy. The toddler is barefoot, with silver anklets.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F6 · Wriggle-free gag

✅ in the repo · Save as `F6_story_wriggle_free.png` · Landscape 3:2 · second batch · Attach: A1, A0  
Used for: Storyboard for the gag at the end of levels 1 to 8.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Gag frame: the toddler dives flat out and lands belly-down in the dust with hands closed on nothing, while the rooster pops out of their grip and flutters away overhead looking smug, a single feather floating down onto the toddler's head. The toddler is barefoot, with silver anklets.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F7 · Rooster escaped

✅ in the repo · Save as `F7_rooster_escaped.png` · Landscape 3:2 · second batch · Attach: A1, A0, B1, E1  
Used for: Staged in Blender as the loss screen.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Loss screen illustration, side-on like the game: the rooster stands on a rooftop parapet against a sunset sky like the attached E1 painting, chest out, wings spread, crowing in triumph; far below, a tiny toddler in the pattu frock looks up with hands on hips and a determined pout, ready to try again. The toddler is barefoot, with silver anklets. Funny and gentle, never sad. Leave the top third as open sky or plain wall, quieter than the rest, for the game's buttons and text; the image itself has no words. The kid matches the attached A0 sheet and the rooster the attached B1 sheet.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### F8 · Story 6: Amma's kitchen

✅ in the repo · Save as `F8_story_amma_kitchen.png` · Landscape 3:2 · second batch · Attach: A1, A0, B1, B6  
Used for: Storyboard for the final scene. It stops at the handover, as the design doc's risk table asks.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Final story frame, Amma's kitchen, side-on like the game: a warm, lamp-lit village kitchen with a clay stove, brass and steel vessels on wooden shelves and strings of dried chillies. The toddler in the pattu frock proudly holds up the rooster in both arms to Amma, who matches the attached B6 sheet and looks down with surprise and a smile; the rooster looks put out. Golden evening light through a small window. The toddler is barefoot, with silver anklets. Nothing shown beyond this moment. Leave the top third as open sky or plain wall, quieter than the rest, for the game's buttons and text; the image itself has no words. The kid matches the attached A0 sheet and the rooster the attached B1 sheet.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## G. Village buildings

One building per image, so every house on a street can be different. Huts, mud and tin houses, the village head's house, shops and landmarks, all at the C4 scale.

### G1 · Thatched hut

✅ in the repo · Save as `G1_thatched_hut.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house, and the model for huts built in Blender.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A small mud hut with walls smoothed in red-brown earth and a band of white lime at the base, a steep palm-leaf thatch roof hanging low over the walls, a short wooden door you would duck through, a tiny window with a wooden shutter, a clay pot by the door and a pumpkin vine climbing over the thatch. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G2 · Hut with a bamboo porch

✅ in the repo · Save as `G2_hut_bamboo_porch.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house with a porch the kid can run under.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A thatched mud hut with a lean-to porch of bamboo poles and a woven palm-mat roof in front, a rope cot under the porch, firewood stacked against the wall and round cow-dung cakes drying in rows on the side wall. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G3 · Orange mud house, tin roof

✅ in the repo · Save as `G3_mud_house_tin_roof.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house; also the model for tin-roof houses built in Blender.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A narrow one-room house with walls plastered in orange ochre mud, a corrugated tin-sheet roof sloping to one side and weighed down with stones and an old tyre, rust streaks on the tin, a blue-painted wooden plank door, and a small window with a plank shutter propped open on a stick. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G4 · Plank and sheet house

✅ in the repo · Save as `G4_plank_sheet_house.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house that breaks up the painted rows.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A patched-together house of weathered wooden planks and corrugated sheets in faded orange, blue and rust, on a low mud plinth, with an old saree hung as a curtain for a door, potted chillies on the window ledge and a brass bucket by the step. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G5 · Village head's house

✅ in the repo · Save as `G5_village_head_house.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: The grandest house on the lane: a landmark in level 2 or 3.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

The biggest house on the street: two storeys, walls washed in pale yellow with maroon trim, a long sloping roof of terracotta Mangalore tiles, a deep front veranda with six carved wooden pillars, raised sit-out platforms on both sides of a big carved double door with brass studs, a brass oil lamp by the door, a tulsi planter in front and a wooden easy chair on the veranda. Grand and proud, but still a village house. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G6 · Tiled house with courtyard gate

✅ in the repo · Save as `G6_tiled_house_gate.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A lane house with a gate and a tree behind its wall.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A single-storey house with a terracotta-tiled roof sloping toward the street, a lime-washed front wall with a wooden gate into a courtyard, a mango tree peeking over the wall, a small window with blue bars and a kolam at the gate. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G7 · Provisions shop

✅ in the repo · Save as `G7_provisions_shop.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A shopfront on the lane, with a bench and awning.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A small village provisions shop: a narrow shopfront with a corrugated tin awning on wooden poles, wooden shelves of glass jars of sweets, hanging strings of snack packets and a bunch of bananas, a big brass weighing scale on the counter, a wooden bench outside and a painted signboard above with pictures of a jar and a bottle and no letters. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G8 · Tea stall

✅ in the repo · Save as `G8_tea_stall.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A tiny stall: steam, glasses and a bench, full of life.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A tiny roadside tea stall built of planks under a palm-thatch awning, a big brass kettle steaming on a clay stove, a row of small glass tumblers, a jar of biscuits, a wooden bench with a folded newspaper and a small radio on a shelf. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G9 · Tailor and cycle repair

✅ in the repo · Save as `G9_tailor_cycle_shop.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: Two tiny shops under one awning.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Two tiny open-fronted shops side by side under one tin awning: a tailor's with a black treadle sewing machine and colourful fabric bolts, and a cycle-repair shop with tyres and inner tubes hanging up and a pump leaning on the wall. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G10 · Potter's house

✅ in the repo · Save as `G10_potters_house.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: Ties in with the clay-pot obstacles: the pots come from here.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A potter's mud house with a thatched work shed beside it, a potter's wheel under the shed, rows of fresh unfired grey pots drying in the sun and stacks of fired terracotta pots in front. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G11 · Weaver's house

✅ in the repo · Save as `G11_weavers_house.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: A nod to the kid's pattu frock: silk being woven.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A silk weaver's house with an open front room showing a wooden pit handloom with a half-woven magenta silk saree, bright silk threads stretched to dry on a frame outside, and lime-washed walls with an indigo band. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G12 · House being built

✅ in the repo · Save as `G12_house_being_built.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: Every real village has one; it adds height and humour.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A village house being built the 1970s way: walls of sun-dried mud bricks halfway up, a bamboo scaffold lashed with coir rope, a wooden door frame already standing in place, a heap of mud mixed with straw, and stacks of terracotta roof tiles and wooden rafters waiting beside it. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G13 · Cattle shed

✅ in the repo · Save as `G13_cattle_shed.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: An open shed: hay, a trough and a calf.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

An open cattle shed with a palm-thatch roof on wooden posts, a stone feeding trough, hay piled at the back, a calf tied to a post and a lime-washed back wall with painted handprints. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G14 · Panchayat office

✅ in the repo · Save as `G14_panchayat_office.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: A civic building for the lane's end or the market.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A small village office: a flat-roofed, lime-plastered building of the 1970s painted pale yellow with a green band, a veranda with square pillars, a blank notice board, a wall clock, a wooden bench outside and a hand pump beside it. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G15 · Village shrine

✅ in the repo · Save as `G15_village_shrine.png` · Landscape 3:2 · first batch · **new** · Attach: A1, C4  
Used for: A small roadside shrine under a tree, with bell and lamps.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A small roadside shrine to the village guardian: a little whitewashed shrine with a tiny ornate tower on top, a brass bell at the entrance, marigold garlands and oil lamps, under a big tree with red and yellow threads tied round its trunk. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### G16 · Stone lamp pillar

✅ in the repo · Save as `G16_stone_lamp_pillar.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: A landmark on the skyline behind the houses.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A tall carved stone lamp pillar (deepa stambha) on a stepped stone base, about 9 m high, with little stone ledges for oil lamps all the way up, a small brass bell and marigold garlands tied at its foot: a landmark seen over the rooftops. Show only this one building, as a flat front elevation for a side-scrolling game: its front wall faces the viewer squarely, parallel to the picture, so neither side wall shows and the roof is seen only from the front, with no corner or gable end turned toward the viewer (no three-quarter view, no perspective). Standing on a thin ground line, drawn at the same scale and in the same painted style as the attached C4 house kit (its doors are about 2 m tall). Even lighting, plain flat light-grey background, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## H. Trees and plants

Several different trees or plants per image, so no two in view are the same, plus big foreground plants to frame the screen edges.

### H1 · Neem trees

✅ in the repo · Save as `H1_neem_trees.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D4  
Used for: Shade trees between houses; three different ones so they never repeat side by side.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Three different neem trees side by side: a big old one with a broad dome of small feathery leaves and a grey trunk, a young slender one, and one leaning with a swing tied to a branch. Drawn like the attached D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H2 · Tamarind and drumstick trees

✅ in the repo · Save as `H2_tamarind_drumstick.png` · Landscape 3:2 · second batch · **new** · Attach: A1, D4  
Used for: More shade-tree variety.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Two tamarind trees with dense fine leaves and hanging brown pods, and two drumstick trees with lacy leaves and long green pods. Drawn like the attached D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H3 · Meeting tree with platform

✅ in the repo · Save as `H3_peepal_platform.png` · Landscape 3:2 · second batch · **new** · Attach: A1, G15, H1, C4  
Used for: The village gathering spot: a one-off landmark.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A huge old peepal tree with heart-shaped leaves, its roots gripping a raised square platform of grey stone where villagers sit in the evening; a few small stone idols, clay lamps and flowers at the foot of the trunk, and red and yellow threads tied round it. Drawn flat and front-on like the attached G15 shrine, for a side-scrolling game: the platform is seen straight from the front as a low rectangle of stone about 0.8 m high and 6 m wide, with three steps in the middle, its top surface hidden behind its front edge; the tree rises from it about 12 m tall, its canopy wide and spreading. No perspective, nothing seen from above. Standing on a thin ground line at the scale of the attached C4 house kit (doors about 2 m tall). Even lighting, no labels. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H4 · Coconut palms

✅ in the repo · Save as `H4_coconut_palms.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D4  
Used for: Five different palms, so palms never look stamped.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Five different coconut palms: a tall straight one, one leaning far over, a pair growing from one spot, a young short palm, and one with a climber's rope ring on the trunk and coconuts in a bunch. Drawn like the attached D4 mango tree sheet. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H5 · Banana, papaya and curry-leaf plants

✅ in the repo · Save as `H5_garden_plants.png` · Landscape 3:2 · second batch · **new** · Attach: A1, D4  
Used for: Small backyard plants for between houses.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Six small backyard plants: a banana plant with a bunch, a torn-leaf banana plant, a papaya tree with fruit, a curry-leaf bush, a clump of sugarcane and a pumpkin vine on a stick frame. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H6 · Flowering bushes

✅ in the repo · Save as `H6_flowering_bushes.png` · Landscape 3:2 · first batch · **new** · Attach: A1, D4  
Used for: Colour by doors and walls; each bush different.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Six flowering bushes and creepers: a hibiscus bush with red flowers, a magenta bougainvillea spilling over a wall, a jasmine creeper on a bamboo frame, a pink oleander, crotons in clay pots, and a patch of orange marigolds. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### H7 · Foreground framing plants

✅ in the repo · Save as `H7_foreground_plants.png` · Landscape 3:2 · first batch · **new** · Attach: A1  
Used for: Big plants in front of the lane, at the screen's bottom corners, like your story frames.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Five large foreground plants for framing the bottom corners of a game screen, drawn bigger and a little darker than the rest of the scene, as if close to the camera: a clump of big taro leaves, a cluster of tall grass with seed heads, a corner of banana leaves, a broken corner of a lime-washed compound wall with weeds, and a mossy rock with ferns. Each item in side view, at the same scale relative to each other, evenly spaced and separate, on a plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## K. House parts kit

Doors, windows, roof edges and doorstep details. Blender builds endless house variations from these, so a long street never repeats.

### K1 · Doors and windows

✅ in the repo · Save as `K1_doors_windows.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: Fitted to houses Blender builds, so no two front doors match. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Sheet of village doors and windows for a modular house kit, each shown straight on and separate: a carved double wooden door with brass studs, a plain plank door painted blue, a green-framed door with a marigold garland, a low hut door, a doorway with a hanging saree curtain, a window with wooden shutters open, a window with blue iron bars, and a small window with a plank shutter propped open. Drawn at the scale of the attached C4 house kit (doors about 2 m tall). Plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### K2 · Roof edges and awnings

✅ in the repo · Save as `K2_roof_edges.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: The front edges of roofs Blender builds: thatch, tiles, tin and awnings. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Six roof edges and awnings for a modular house kit, each a long horizontal strip seen straight on from the front: a palm-thatch eave, a terracotta Mangalore-tile eave, a corrugated tin-sheet eave with rust, a flat-roof parapet with pots on it, a plain faded cotton awning and a bamboo-and-palm-mat awning. Drawn at the scale of the attached C4 house kit. Plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Backgrounds are painterly and atmospheric, with visible brush texture, soft haze in the distance, light shafts and floating dust. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### K3 · Doorstep and wall details

✅ in the repo · Save as `K3_wall_details.png` · Landscape 3:2 · second batch · **new** · Attach: A1, C4  
Used for: Small details that make every built house its own.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

Sheet of small details for village house fronts, each separate and seen straight on: three different front steps with kolam, a raised sit-out platform, a brass wall lamp, a hanging lantern, a row of cow-dung cakes drying on a wall, a wall shelf with clay pots, a hanging bird feeder and a mango-leaf garland. Drawn at the scale of the attached C4 house kit. Plain flat light-grey background, even lighting, no labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

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

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T2 · Lime-washed wall

✅ in the repo · Save as `T2_tex_limewash_wall.png` · Square 1:1 · first batch · Attach: A1  
Used for: The base wall material for the house kit.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of a lime-washed village wall: soft white with a faint blue tint, uneven brush strokes, small chips showing terracotta plaster underneath, slightly dirtier toward the bottom.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T3 · Coloured walls

✅ in the repo · Save as `T3_tex_coloured_walls.png` · Square 1:1 · first batch · Attach: A1  
Used for: Wall variants for the house kit. I split the four squares and make each one tile.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate wall textures in a 2 by 2 grid, each square front-on with soft uneven brush strokes: an indigo-washed wall, a turmeric-yellow wall, a pale pink wall and a weathered sea-green wall.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T4 · Wood, rope and bamboo

✅ in the repo · Save as `T4_tex_wood_weave.png` · Square 1:1 · first batch · Attach: A1  
Used for: Doors, the cot, the basket and the sacks.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate textures in a 2 by 2 grid, each square seen straight on: weathered wooden planks, the woven rope top of a cot, a bamboo basket weave and coarse jute sacking.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T5 · Roofs, floors and stone

✅ in the repo · Save as `T5_tex_roof_floor_stone.png` · Square 1:1 · second batch · Attach: A1  
Used for: Thatch, roof tiles, the courtyard floor and the temple steps.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate textures in a 2 by 2 grid, each square seen straight on: palm-leaf thatch, terracotta roof tiles, a smooth cow-dung-plastered courtyard floor in olive brown, and worn granite temple stone.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T6 · Paddy and canal water

✅ in the repo · Save as `T6_tex_water.png` · Square 1:1 · second batch · Attach: A1  
Used for: The paddy and canal surfaces for zone 2.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Two textures side by side, each filling half the square, seen straight down: shallow paddy-field water with rows of young green rice shoots and a golden sky reflected in it; and muddy-green canal water with soft ripples and a few floating leaves.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T7 · Saree and awning fabrics

✅ in the repo · Save as `T7_tex_fabrics.png` · Square 1:1 · second batch · Attach: A1  
Used for: Sarees on the clotheslines and the market awnings.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four separate fabric patterns in a 2 by 2 grid, each square flat and seen straight on: kumkum red with a gold border stripe; indigo block print with small white motifs; turmeric and green checks; a plain faded madder-red cotton awning cloth.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T8 · Corrugated tin sheet

✅ in the repo · Save as `T8_tex_tin_sheet.png` · Square 1:1 · second batch · **new** · Attach: A1  
Used for: Roofs of the tin-roof houses Blender builds. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of an old corrugated tin roofing sheet: silver-grey ridges with patches of orange rust, rust streaks and a few nail heads.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T9 · Orange mud plaster

✅ in the repo · Save as `T9_tex_orange_mud.png` · Square 1:1 · second batch · **new** · Attach: A1  
Used for: Walls of the orange mud houses Blender builds. Only needed if houses are built in 3D again; the street uses painted houses for now.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of a mud-plastered wall in warm orange ochre: hand-smoothed, with finger swirls, small cracks and a few patches where the red-brown earth shows.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T10 · Bare brick

✅ in the repo · Save as `T10_tex_bare_brick.png` · Square 1:1 · second batch · **new** · Attach: A1  
Used for: Unfinished upper floors and back walls.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of an unplastered red brick wall: bricks of slightly different reds in straight courses, uneven grey mortar lines, a few chipped corners and a faint splash of old cement. Only the wall, filling the square. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T11 · Woven coconut-leaf fence

✅ in the repo · Save as `T11_tex_coconut_leaf_fence.png` · Square 1:1 · first batch · **new** · Attach: A1  
Used for: The fences around house compounds, built in Blender: so they look woven by hand, not tiled.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A front-on texture of a village compound fence of dried coconut palm leaves woven in rows that run straight across: tan, straw and grey-brown leaflets folded over thin horizontal sticks, with a few frayed ends, small gaps and darker weathered leaves. It shows only the woven panel, filling the square: no posts, ground, sky or top edge. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### T12 · Plain red earth

✅ in the repo · Save as `T12_tex_plain_red_earth.png` · Square 1:1 · first batch · **new** · Attach: A1, T1  
Used for: The grain of the lane's ground, which Blender builds without repeating: it needs earth with no marks in it.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of bare red laterite earth seen straight down from above, in the colours of the attached T1 texture: fine dust, crumbs and grit, with soft brush-stroke variation between deep red, red-orange and dusty orange. Only the earth itself: no footprints, tracks, leaves, plants, stones or cracks, and no patch darker or lighter than the rest. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

## M. 3D model textures

Painted surfaces for the 3D kid, rooster and pickups. The models are already built in flat colours; each image swaps in on its own as it arrives.

### M1 · Kid's faces

⬜ to make · prompt updated · Save as `M1_kid_faces.png` · Square 1:1 · first batch · Attach: A0, A1  
Used for: Painted onto the 3D kid's face: neutral while she runs, a grin when she grabs the rooster, shocked when she stumbles, straining on a vault or climb.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

Four faces of the game's toddler hero from the attached A0 sheet (her front view), in a 2 by 2 grid of equal squares: top left neutral and determined, top right a big open grin, bottom left shocked with round eyes and an open mouth, bottom right straining with eyes squeezed and teeth gritted. Each face seen exactly from the front, centred in its square and the same size, showing only the face on her warm brown skin: eyes, eyebrows, nose, mouth and cheeks, with no hair, ears, hairband or neck, and the skin colour running to the edges of each square. Even flat lighting, no shading on the face, clean dark outlines on the features. Plain, no background.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Colours exactly as in the attached model sheet. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### M2 · Frock silk

⬜ to make · prompt updated · Save as `M2_frock_silk.png` · Square 1:1 · first batch · Attach: A0, A1  
Used for: The 3D kid's frock: the body of the skirt, bodice and sleeves.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of the peacock-blue pattu silk of the kid's frock in the attached A0 sheet: a soft silk sheen painted in two or three close blues, with tiny gold zari dots (butis) scattered evenly. Seen exactly straight on, filling the square, even flat lighting with no shading, shadows, highlights or folds, so it can be wrapped around a 3D model. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### M3 · Zari border

⬜ to make · prompt updated · Save as `M3_zari_border.png` · Landscape 3:2 · first batch · Attach: A0, A1  
Used for: The wide band at the hem of the 3D kid's frock, and the gold edging of the neckline and sleeves.

```text
Landscape 3:2 image.

Use the attached A1 key art as the style reference and match it closely.

A long woven border band from the hem of the kid's frock in the attached A0 sheet, filling the whole image: magenta silk with gold zari, a row of small temple-tower motifs between two thin gold lines. Seen straight on, perfectly flat and even, no folds or shading. The pattern repeats seamlessly from the left edge to the right edge; the top and bottom edges are the band's own straight gold edges.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### M4 · Hair

⬜ to make · prompt updated · Save as `M4_hair.png` · Square 1:1 · first batch · Attach: A0, A1  
Used for: The 3D kid's shoulder-length wavy black hair.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of the kid's glossy black wavy hair from the attached A0 sheet: soft waves of strands all running top to bottom, painted in near-black and deep blue-brown with a few soft lighter strokes. Seen exactly straight on, filling the square, even flat lighting with no shading, shadows, highlights or folds, so it can be wrapped around a 3D model. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### M5 · Leopard hairband

⬜ to make · prompt updated · Save as `M5_leopard_print.png` · Square 1:1 · first batch · Attach: A0, A1  
Used for: The 3D kid's hairband.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of the leopard print of the kid's hairband in the attached A0 sheet: golden-yellow fabric with brown and black rosettes, drawn with clean painted edges. Seen exactly straight on, filling the square, even flat lighting with no shading, shadows, highlights or folds, so it can be wrapped around a 3D model. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### M6 · Rooster body feathers

⬜ to make · prompt updated · Save as `M6_rooster_body.png` · Square 1:1 · first batch · Attach: B1, B11, A1  
Used for: The 3D rooster's body, back and wings.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of the rooster's body plumage from the attached B1 sheet: overlapping rows of rounded deep red-chestnut feathers, each with a slightly darker edge, like scales, all pointing the same way (down the image). Seen exactly straight on, filling the square, even flat lighting with no shading, shadows, highlights or folds, so it can be wrapped around a 3D model. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### M7 · Rooster neck hackles

⬜ to make · prompt updated · Save as `M7_rooster_hackles.png` · Square 1:1 · first batch · Attach: B1, B11, A1  
Used for: The 3D rooster's neck and the saddle feathers over its back.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of the rooster's neck hackles from the attached B1 sheet: long, narrow, pointed feathers in glowing orange-gold with lighter golden tips, layered and all flowing downward. Seen exactly straight on, filling the square, even flat lighting with no shading, shadows, highlights or folds, so it can be wrapped around a 3D model. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### M8 · Rooster tail feathers

⬜ to make · prompt updated · Save as `M8_rooster_tail.png` · Square 1:1 · first batch · Attach: B1, B11, A1  
Used for: The 3D rooster's sickle tail feathers.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of the rooster's tail feathers from the attached B1 sheet: long glossy black feathers side by side running top to bottom, with an iridescent green and blue-violet sheen along their middles. Seen exactly straight on, filling the square, even flat lighting with no shading, shadows, highlights or folds, so it can be wrapped around a 3D model. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### M9 · Mango skin

⬜ to make · prompt updated · Save as `M9_mango_skin.png` · Square 1:1 · first batch · Attach: A1  
Used for: The 3D mangoes the kid collects.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

A texture of ripe Alphonso mango skin: warm golden yellow blending into orange and a soft red blush, with tiny pale speckles and a gentle painted sheen. Seen exactly straight on, filling the square, even flat lighting with no shading, shadows, highlights or folds, so it can be wrapped around a 3D model. The pattern runs off all four edges with no border, frame or single feature in the middle, at an even density everywhere, so copies placed side by side show no seam and no obvious repeat.

Texture rules: seamless and tileable for a 3D game, seen straight on (straight down for floors), even flat lighting with no cast shadows, no perspective and no vignette. Hand-painted with visible brush strokes and simplified shapes that still read at small size. Colours from this palette: terracotta, red earth, turmeric, kumkum red, indigo, lime-wash white, paddy green. No text, logos or watermarks. Only materials a 1970s village would have.
```

### M10 · Golden tail feather

⬜ to make · prompt updated · Save as `M10_tail_feather.png` · Square 1:1 · first batch · Attach: B1, A1  
Used for: The hidden tail feather pickup: a card on the 3D feather.

```text
Square 1:1 image.

Use the attached A1 key art as the style reference and match it closely.

One single long curved tail feather from the rooster in the attached B1 sheet, lying flat and seen straight on, its quill at the bottom and its tip curving up to the top right, filling the square: glossy black-green at the tip shading to orange-gold and russet near the quill. Clean dark outline, flat even light, no shadow. Keep the background one flat light-grey everywhere: no painted ground, sky, haze, dust, mist, glow or blurred scenery behind or around anything, and nothing cropped by the edges of the image.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Paint everything crisp and clear, with visible brush texture inside each shape. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. Mood: warm, gentle, funny and immersive. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## P. Pongal: the festive repaint

The whole village is celebrating Pongal, the harvest festival. Each prompt below edits a painting you have already made: it keeps the picture exactly as it is, so its cut-outs and the Blender models traced from it still fit, and adds the festival in the same painted style: mango-leaf thoranams over the doors, marigold garlands, coloured Pongal kolams, tall sugarcane stalks, new clay Pongal pots boiling over on brick hearths with a turmeric plant tied round their necks, cattle with painted horns, bells and garlands, new festival clothes, bunting and kites. Gemini keeps the rest of a picture best: use it for these edits.

1. Attach the painting named in the prompt, from `ArtSource/references/` (it is the image you made before).
2. Paste the prompt. Gemini keeps everything else in place best; in ChatGPT, use its edit mode on the attached image.
3. Check it against the old one (flip between the two): nothing may move, grow, shrink or disappear; only the festival touches are new. If something moved, reply: *Put the … back exactly where it is in the image I uploaded, and keep the decorations.*
4. Save it under the **same file name**, replacing the old painting (the old one stays in the repo's history), and put it in `ArtSource/references/` or upload it here, in batches. Start with A1, then the lane (C, G, K), the fields (D), the market and temple (E), the people and animals (B) and the story (F).
5. I then cut the pieces out again and add the new decorations to each Blender model as real parts: thoranams as hanging leaf strings, sugarcane, pots on hearths and garlands modelled, the kolams and painted horns as the painting itself.

Left as they are: A0 and the kid sheets, the rooster (B1-B4, B11-B14), B9's small animals, the far trees and plants (D4, D6, D11, D12, H1, H2, H4-H7), the ground details (C10), K2's roof edges, the textures (T) and the 3D textures (M): there is nothing on them to celebrate, or they are not seen in the festival's scenes.

### P1 · A1 · Key art

⬜ to make · Save as `A1_key_art.png` (replacing A1) · Landscape 3:2 · Attach: `A1_key_art.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (A1_key_art.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: on every house a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; in front of one house, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it; strings of small triangular cloth bunting in red, yellow, green and blue strung across overhead the lane; a few diamond-shaped paper kites with long tails high in the sky. Keep the toddler and the rooster exactly as they are.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P2 · A2 · Colour script

⬜ to make · Save as `A2_colour_script.png` (replacing A2) · Landscape 3:2 · Attach: `A2_colour_script.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (A2_colour_script.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: in the lane panels, mango-leaf thoranams over the doors, coloured kolams and bunting across the lane; in a yard, a Pongal pot boiling over on a brick hearth beside sugarcane stalks; in the field panels, cattle with brightly painted horns and garlands and sheaves of harvested paddy; over the rooftops, paper kites; at the market and the temple, more marigold garlands, sugarcane bundles and oil lamps.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P3 · B5 · Neighbour

⬜ to make · Save as `B5_neighbour_sheet.png` (replacing B5) · Landscape 3:2 · Attach: `B5_neighbour_sheet.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (B5_neighbour_sheet.png) so it shows the village on Pongal, the harvest festival. Keep every figure exactly as it is: the same faces, bodies, poses, expressions and places on the sheet, the same painted style and the same plain light-grey background; change only what is described here.

Add only these Pongal festival touches, painted in the same style and light as the rest: dress him for Pongal: a crisp new white veshti with a thin gold border instead of the checked lungi, a new white cotton shirt over the vest, a white sandal-paste stripe and a red kumkum dot on his forehead, and a small marigold garland round his neck in the standing views.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P4 · B6 · Amma

⬜ to make · Save as `B6_amma_sheet.png` (replacing B6) · Landscape 3:2 · Attach: `B6_amma_sheet.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (B6_amma_sheet.png) so it shows the village on Pongal, the harvest festival. Keep every figure exactly as it is: the same faces, bodies, poses, expressions and places on the sheet, the same painted style and the same plain light-grey background; change only what is described here.

Add only these Pongal festival touches, painted in the same style and light as the rest: dress her for Pongal: a new silk saree in turmeric yellow with a broad magenta and gold border instead of the cotton one, a thicker string of jasmine round her bun, small gold earrings, a few more glass bangles, and a red kumkum dot with a little turmeric on her forehead.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P5 · B7 · Village animals

⬜ to make · Save as `B7_animals_sheet.png` (replacing B7) · Landscape 3:2 · Attach: `B7_animals_sheet.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (B7_animals_sheet.png) so it shows the village on Pongal, the harvest festival. Keep every figure exactly as it is: the same faces, bodies, poses, expressions and places on the sheet, the same painted style and the same plain light-grey background; change only what is described here.

Add only these Pongal festival touches, painted in the same style and light as the rest: the pair of white bullocks dressed for Mattu Pongal: horns painted in bright bands of red, blue and green with shining brass tips, a marigold garland and a string of brass bells round the neck, and a red kumkum dot on the forehead; the water buffalo with its horns painted red and a marigold garland round its neck. Leave the dog and the hens as they are.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P6 · B8 · Cows and goats

⬜ to make · Save as `B8_cows_goats.png` (replacing B8) · Landscape 3:2 · Attach: `B8_cows_goats.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (B8_cows_goats.png) so it shows the village on Pongal, the harvest festival. Keep every figure exactly as it is: the same faces, bodies, poses, expressions and places on the sheet, the same painted style and the same plain light-grey background; change only what is described here.

Add only these Pongal festival touches, painted in the same style and light as the rest: the white cow dressed for Mattu Pongal: horns painted in bright bands of red, blue and green with shining brass tips, a marigold garland and a string of brass bells round the neck, and a red kumkum dot on the forehead; the calf with a small marigold garland and one brass bell; the standing buffalo with its horns painted red and a garland round its neck. Leave the goats as they are.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P7 · B10 · Villagers in the background

⬜ to make · Save as `B10_villagers.png` (replacing B10) · Landscape 3:2 · Attach: `B10_villagers.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (B10_villagers.png) so it shows the village on Pongal, the harvest festival. Keep every figure exactly as it is: the same faces, bodies, poses, expressions and places on the sheet, the same painted style and the same plain light-grey background; change only what is described here.

Add only these Pongal festival touches, painted in the same style and light as the rest: everyone in new, brighter Pongal clothes (new cotton and silk saris, crisp white veshtis); the woman drawing a kolam now draws a big coloured Pongal kolam with red, yellow and green powder; the woman with the water pot carries a new clay Pongal pot with a turmeric plant tied round its neck; the vegetable seller's cart is heaped with sugarcane stalks, turmeric plants and bananas; the milkman has two sugarcane stalks tied along his bicycle.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P8 · C1 · Lane mood painting

⬜ to make · Save as `C1_lane_mood.png` (replacing C1) · Landscape 3:2 · Attach: `C1_lane_mood.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (C1_lane_mood.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: on every house a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; in front of one house, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it; strings of small triangular cloth bunting in red, yellow, green and blue strung across overhead the lane; a few diamond-shaped paper kites with long tails high in the sky.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P9 · C2 · Lane far layer

⬜ to make · Save as `C2_lane_far_layer.png` (replacing C2) · Landscape 3:2 · Attach: `C2_lane_far_layer.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (C2_lane_far_layer.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: a few diamond-shaped paper kites with long tails high in the sky, and a long string of bunting hanging from the distant temple tower.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P10 · C3 · Lane middle layer

⬜ to make · Save as `C3_lane_mid_layer.png` (replacing C3) · Landscape 3:2 · Attach: `C3_lane_mid_layer.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (C3_lane_mid_layer.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every shape in the same place, at the same size and in the same outline, the same painted style, colours and haze, and the same flat magenta background.

Add only these Pongal festival touches, painted in the same style and light as the rest: strings of small triangular cloth bunting between the roofs, mango-leaf thoranams under the eaves where a doorway shows, and two paper kites flying just above the roofs, inside the cut-out.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P11 · C4 · House kit elevations

⬜ to make · Save as `C4_house_kit_elevations.png` (replacing C4) · Landscape 3:2 · Attach: `C4_house_kit_elevations.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (C4_house_kit_elevations.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: on each of the four houses a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; in front of the lime-white house's door, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P12 · C5 · Lane props, sheet 1

⬜ to make · Save as `C5_lane_props_a.png` (replacing C5) · Landscape 3:2 · Attach: `C5_lane_props_a.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (C5_lane_props_a.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: the top pot of the clay pot stack decorated as a Pongal pot, painted with white lime stripes and red kumkum dots, with a turmeric plant tied round its neck; a marigold garland hung on the hand pump; two sugarcane stalks tied along the bicycle's carrier; a marigold garland and a sprig of mango leaves on the tulsi planter, with a small coloured kolam on its pedestal; a turmeric smear and red kumkum dots on the necks of the brass water pots. Leave the dung and the cot as they are.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P13 · C6 · Lane props, sheet 2

⬜ to make · Save as `C6_lane_props_b.png` (replacing C6) · Landscape 3:2 · Attach: `C6_lane_props_b.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (C6_lane_props_b.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: the bullock cart's wheels and frame painted with turmeric-yellow and kumkum-red stripes, with two sugarcane stalks and a bunch of mango leaves tied to it; new bright silk sarees on the clothesline; two sugarcane stalks and a turmeric plant leaning on the jute sacks; the doorway's mango-leaf garland fresher, with a marigold garland too and a coloured kolam at its step; fresh turmeric and kumkum on the shrine stone with a lit clay lamp before it; a turmeric plant tied round the neck of the pot on the stand. Leave the chicken basket as it is.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P14 · C7 · Kolam decals

⬜ to make · Save as `C7_kolam_decals.png` (replacing C7) · Square 1:1 · Attach: `C7_kolam_decals.png`

```text
Square 1:1 image, the same shape as the attached one.

Edit the attached image (C7_kolam_decals.png) so it shows the village on Pongal, the harvest festival. Keep the six designs exactly where they are, at the same size and with the same white outlines, on the same flat dark-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: make all six into Pongal kolams: fill the white line designs with bright coloured powder (red, yellow, green, pink and orange), and work a small Pongal pot with sugarcane stalks, or a rising sun, into the middle of three of them.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P15 · C8 · Lane middle layer 2

⬜ to make · Save as `C8_lane_mid_layer_2.png` (replacing C8) · Landscape 3:2 · Attach: `C8_lane_mid_layer_2.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (C8_lane_mid_layer_2.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every shape in the same place, at the same size and in the same outline, the same painted style, colours and haze, and the same flat magenta background.

Add only these Pongal festival touches, painted in the same style and light as the rest: strings of small triangular cloth bunting between the roofs, mango-leaf thoranams under the eaves where a doorway shows, and a thin wisp of smoke from a Pongal hearth behind one house.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P16 · C9 · Lane middle layer 3

⬜ to make · Save as `C9_lane_mid_layer_3.png` (replacing C9) · Landscape 3:2 · Attach: `C9_lane_mid_layer_3.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (C9_lane_mid_layer_3.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every shape in the same place, at the same size and in the same outline, the same painted style, colours and haze, and the same flat magenta background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of bunting and a marigold garland on the tiny white shrine, mango-leaf thoranams under the thatched eaves, and two paper kites caught high in the tamarind tree.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P17 · D1 · Fields mood painting

⬜ to make · Save as `D1_fields_mood.png` (replacing D1) · Landscape 3:2 · Attach: `D1_fields_mood.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D1_fields_mood.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: sheaves of harvested paddy stacked along the bund; the scarecrow wearing a marigold garland and a new bright towel round its neck; a pair of grazing bullocks by the well with horns painted in bright bands of red, blue and green with shining brass tips, a marigold garland and a string of brass bells round the neck, and a red kumkum dot on the forehead; beside the farmhouse, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it and two sugarcane stalks; a mango-leaf thoranam and a marigold garland on the well's pulley frame; a few diamond-shaped paper kites with long tails high in the sky.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P18 · D2 · Fields far layer

⬜ to make · Save as `D2_fields_far_layer.png` (replacing D2) · Landscape 3:2 · Attach: `D2_fields_far_layer.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D2_fields_far_layer.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: a few diamond-shaped paper kites with long tails high in the sky.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P19 · D3 · Fields props

⬜ to make · Save as `D3_fields_props.png` (replacing D3) · Landscape 3:2 · Attach: `D3_fields_props.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D3_fields_props.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a small marigold garland round the top of the haystack; a mango-leaf thoranam and a marigold garland on the well's pulley frame, with turmeric and kumkum dots on the well's stone rim; the scarecrow wearing a marigold garland and a new bright towel round its neck; a mango-leaf thoranam across the sluice gate's frame; a small coloured kolam on the bund path. Leave the canal and plank bridge as they are.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P20 · D5 · Field buildings

⬜ to make · Save as `D5_field_buildings.png` (replacing D5) · Landscape 3:2 · Attach: `D5_field_buildings.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D5_field_buildings.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a mango-leaf thoranam over the pump house door, with turmeric and kumkum dots on its wall; at the farmer's hut a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door, and beside its cattle pen a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it; a marigold garland and turmeric and kumkum dots on the granary's posts; the shrine with fresh marigold garlands, a lit clay lamp and a new red flag.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P21 · D7 · Fields middle layer

⬜ to make · Save as `D7_fields_mid_layer.png` (replacing D7) · Landscape 3:2 · Attach: `D7_fields_mid_layer.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D7_fields_mid_layer.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every shape in the same place, at the same size and in the same outline, the same painted style, colours and haze, and the same flat magenta background.

Add only these Pongal festival touches, painted in the same style and light as the rest: mango-leaf thoranams on the farmhouse doors, a thin wisp of smoke from a Pongal hearth in each farmhouse yard, and a few cut paddy sheaves stacked on the bund.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P22 · D8 · Field buildings 2

⬜ to make · Save as `D8_field_buildings_2.png` (replacing D8) · Landscape 3:2 · Attach: `D8_field_buildings_2.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D8_field_buildings_2.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: the kavalai's bullocks with horns painted in bright bands of red, blue and green with shining brass tips, a marigold garland and a string of brass bells round the neck, and a red kumkum dot on the forehead; a mango-leaf thoranam across the well's pulley frame; a thoranam on the watch hut's ladder; at the threshing floor, a coloured kolam beside the paddy heaps and a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it, with two sugarcane stalks beside it.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P23 · D9 · Canal pieces

⬜ to make · Save as `D9_canal_pieces.png` (replacing D9) · Landscape 3:2 · Attach: `D9_canal_pieces.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D9_canal_pieces.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a marigold garland and a turmeric and kumkum mark on the picottah's post; a turmeric plant tied round the neck of the brass pot on the washing steps; a mango-leaf thoranam across the sluice gate's frame. Leave the slab bridge as it is.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P24 · D10 · Life in the fields

⬜ to make · Save as `D10_field_life.png` (replacing D10) · Landscape 3:2 · Attach: `D10_field_life.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D10_field_life.png) so it shows the village on Pongal, the harvest festival. Keep every figure exactly as it is: the same faces, bodies, poses, expressions and places on the sheet, the same painted style and the same plain light-grey background; change only what is described here.

Add only these Pongal festival touches, painted in the same style and light as the rest: the ploughing bullocks and the kavalai bullocks with horns painted in bright bands of red, blue and green with shining brass tips, a marigold garland and a string of brass bells round the neck, and a red kumkum dot on the forehead; the three women in new bright saris; small marigold garlands on the herd boy's goats; the wallowing buffalo with its horns painted red; the farmer carrying a bundle of cut paddy with two sugarcane stalks.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P25 · D13 · Fields middle layer 2

⬜ to make · Save as `D13_fields_mid_layer_2.png` (replacing D13) · Landscape 3:2 · Attach: `D13_fields_mid_layer_2.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (D13_fields_mid_layer_2.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every shape in the same place, at the same size and in the same outline, the same painted style, colours and haze, and the same flat magenta background.

Add only these Pongal festival touches, painted in the same style and light as the rest: the grazing cattle with brightly painted horns, mango-leaf thoranams on the hut doors, thin wisps of smoke from Pongal hearths in the hamlet, and two paper kites just above the palms.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P26 · E1 · Rooftops mood painting

⬜ to make · Save as `E1_rooftops_mood.png` (replacing E1) · Landscape 3:2 · Attach: `E1_rooftops_mood.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E1_rooftops_mood.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: more paper kites in the sunset sky; on one terrace, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it, with two sugarcane stalks; mango-leaf thoranams over the doors up to the roofs; coloured kolams on the terraces.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P27 · E2 · Market mood painting

⬜ to make · Save as `E2_market_mood.png` (replacing E2) · Landscape 3:2 · Attach: `E2_market_mood.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E2_market_mood.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: tall bundles of sugarcane standing upright at the stalls; turmeric plants and new clay Pongal pots for sale; more marigold garlands; a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; strings of small triangular cloth bunting in red, yellow, green and blue strung across overhead the market.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P28 · E3 · Temple steps

⬜ to make · Save as `E3_temple_steps_mood.png` (replacing E3) · Landscape 3:2 · Attach: `E3_temple_steps_mood.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E3_temple_steps_mood.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: a big coloured Pongal kolam on the bottom step; tall sugarcane stalks tied either side of the temple gateway, with mango-leaf thoranams across it; beside the steps, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it; more marigold garlands on the bells.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P29 · E4 · Rooftop props

⬜ to make · Save as `E4_rooftop_props.png` (replacing E4) · Landscape 3:2 · Attach: `E4_rooftop_props.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E4_rooftop_props.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: the big clay water pot painted with white lime stripes and red kumkum dots, with a turmeric plant tied round its neck; more colours in the bunting. Leave the parapet, the mats and the kite as they are.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P30 · E5 · Market and temple props

⬜ to make · Save as `E5_market_props.png` (replacing E5) · Landscape 3:2 · Attach: `E5_market_props.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E5_market_props.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: on both stalls under the indigo awning and on the flower stall, a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; a coloured kolam and a marigold garland on the temple step segment. Leave the baskets, vessels and lantern as they are.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P31 · E6 · Village houses with roof terraces 1

⬜ to make · Save as `E6_rooftop_houses_1.png` (replacing E6) · Landscape 3:2 · Attach: `E6_rooftop_houses_1.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E6_rooftop_houses_1.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: on both houses a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; in front of the first house, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it; strings of small triangular cloth bunting along the roof parapets.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P32 · E7 · Village houses with roof terraces 2

⬜ to make · Save as `E7_rooftop_houses_2.png` (replacing E7) · Landscape 3:2 · Attach: `E7_rooftop_houses_2.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E7_rooftop_houses_2.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: on both houses a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; on the first house's terrace, beside the drying mats, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it; strings of small triangular cloth bunting along the roof parapets.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P33 · E8 · Shandy stalls 1

⬜ to make · Save as `E8_market_stalls_1.png` (replacing E8) · Landscape 3:2 · Attach: `E8_market_stalls_1.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E8_market_stalls_1.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; bunches of turmeric plants and ginger among the vegetables; more marigold and jasmine garlands at the flower seller's.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P34 · E9 · Shandy stalls 2

⬜ to make · Save as `E9_market_stalls_2.png` (replacing E9) · Landscape 3:2 · Attach: `E9_market_stalls_2.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E9_market_stalls_2.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; the coconut cart's bullocks with horns painted in bright bands of red, blue and green with shining brass tips, a marigold garland and a string of brass bells round the neck, and a red kumkum dot on the forehead; the potter's new pots painted with white lime stripes and red kumkum dots, some with turmeric plants tied round their necks, for Pongal.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P35 · E10 · Village temple lane

⬜ to make · Save as `E10_temple_street.png` (replacing E10) · Landscape 3:2 · Attach: `E10_temple_street.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E10_temple_street.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: mango-leaf thoranams strung between the mandapam's pillars and marigold garlands round them, with lit clay lamps on the plinth; a thoranam across the chariot shed's front and sugarcane stalks tied either side; lit lamps and a coloured kolam on the temple tank's steps.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P36 · E11 · Shandy stalls 3

⬜ to make · Save as `E11_shandy_stalls_3.png` (replacing E11) · Landscape 3:2 · Attach: `E11_shandy_stalls_3.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E11_shandy_stalls_3.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; bunches of turmeric plants for sale beside the spice seller's heaps.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P37 · E12 · Shandy stalls 4

⬜ to make · Save as `E12_shandy_stalls_4.png` (replacing E12) · Landscape 3:2 · Attach: `E12_shandy_stalls_4.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E12_shandy_stalls_4.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; a few sugarcane pieces and bananas beside the jaggery blocks.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P38 · E13 · Shandy stalls 5

⬜ to make · Save as `E13_shandy_stalls_5.png` (replacing E13) · Landscape 3:2 · Attach: `E13_shandy_stalls_5.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E13_shandy_stalls_5.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; bunches of turmeric plants and sugarcane stalks among the vegetables.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P39 · E14 · Shandy stalls 6

⬜ to make · Save as `E14_shandy_stalls_6.png` (replacing E14) · Landscape 3:2 · Attach: `E14_shandy_stalls_6.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E14_shandy_stalls_6.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; a taller bundle of sugarcane at the juice seller's, and a tray of sweet Pongal in a brass dish among the sweets.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P40 · E15 · Shandy stalls 7

⬜ to make · Save as `E15_shandy_stalls_7.png` (replacing E15) · Landscape 3:2 · Attach: `E15_shandy_stalls_7.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E15_shandy_stalls_7.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; more garlands and bowls of turmeric and kumkum at the bangle seller's.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P41 · E16 · Shandy stalls 8

⬜ to make · Save as `E16_shandy_stalls_8.png` (replacing E16) · Landscape 3:2 · Attach: `E16_shandy_stalls_8.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E16_shandy_stalls_8.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P42 · E17 · Shandy stalls 9

⬜ to make · Save as `E17_shandy_stalls_9.png` (replacing E17) · Landscape 3:2 · Attach: `E17_shandy_stalls_9.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E17_shandy_stalls_9.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; the cattle-fair seller's horn caps in brighter colours, with strings of brass bells and coloured tassels for Mattu Pongal.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P43 · E18 · Shandy stalls 10

⬜ to make · Save as `E18_shandy_stalls_10.png` (replacing E18) · Landscape 3:2 · Attach: `E18_shandy_stalls_10.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (E18_shandy_stalls_10.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the ground in front of each stall; a few banana leaves of sweet Pongal beside the idlis.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P44 · F1 · Title screen

⬜ to make · Save as `F1_title_screen.png` (replacing F1) · Landscape 3:2 · Attach: `F1_title_screen.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (F1_title_screen.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: a coloured Pongal kolam on the ground instead of the white one, a mango-leaf thoranam over the yard's gate, sugarcane stalks leaning on the low wall, and in the background a Pongal pot boiling over on a brick hearth.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P45 · F2 · Story 1: the craving

⬜ to make · Save as `F2_story_craving.png` (replacing F2) · Landscape 3:2 · Attach: `F2_story_craving.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (F2_story_craving.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: a coloured Pongal kolam on the doorstep, a mango-leaf thoranam over the door, two sugarcane stalks leaning beside it, and a mango-leaf thoranam over the neighbour's kitchen window.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P46 · F3 · Story 2: the plan

⬜ to make · Save as `F3_story_plan.png` (replacing F3) · Landscape 3:2 · Attach: `F3_story_plan.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (F3_story_plan.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: a coloured Pongal kolam in the yard, a mango-leaf thoranam over the yard's gate, sugarcane stalks leaning on the wall, and a marigold garland on the tree's trunk.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P47 · F4 · Story 3: the basket

⬜ to make · Save as `F4_story_basket.png` (replacing F4) · Landscape 3:2 · Attach: `F4_story_basket.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (F4_story_basket.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: the edge of a coloured Pongal kolam on the ground and a few marigold petals scattered there.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P48 · F5 · Story 4: the escape

⬜ to make · Save as `F5_story_escape.png` (replacing F5) · Landscape 3:2 · Attach: `F5_story_escape.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (F5_story_escape.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: the coloured Pongal kolam in the yard scattered by the rooster in puffs of coloured powder, and a sugarcane stalk toppling against the wall.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P49 · F6 · Wriggle-free gag

⬜ to make · Save as `F6_story_wriggle_free.png` (replacing F6) · Landscape 3:2 · Attach: `F6_story_wriggle_free.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (F6_story_wriggle_free.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: a puff of coloured kolam powder rising where the toddler lands, and a few marigold petals in the air.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P50 · F7 · Rooster escaped

⬜ to make · Save as `F7_rooster_escaped.png` (replacing F7) · Landscape 3:2 · Attach: `F7_rooster_escaped.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (F7_rooster_escaped.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: strings of triangular cloth bunting along the parapet and paper kites in the sunset sky.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P51 · F8 · Story 6: Amma's kitchen

⬜ to make · Save as `F8_story_amma_kitchen.png` (replacing F8) · Landscape 3:2 · Attach: `F8_story_amma_kitchen.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (F8_story_amma_kitchen.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: the same composition and framing, every building, object, person and animal in the same place, at the same size and in the same shape, and the same painted style, colours and light.

Add only these Pongal festival touches, painted in the same style and light as the rest: a Pongal feast: a brass pot of sweet Pongal on the stove, pieces of sugarcane and bananas on banana leaves on the floor, a mango-leaf thoranam over the kitchen door and a coloured kolam by the stove.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P52 · G1 · Thatched hut

⬜ to make · Save as `G1_thatched_hut.png` (replacing G1) · Landscape 3:2 · Attach: `G1_thatched_hut.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G1_thatched_hut.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; beside the door, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P53 · G2 · Hut with a bamboo porch

⬜ to make · Save as `G2_hut_bamboo_porch.png` (replacing G2) · Landscape 3:2 · Attach: `G2_hut_bamboo_porch.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G2_hut_bamboo_porch.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; marigold garlands round the porch posts; beside the porch, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P54 · G3 · Orange mud house, tin roof

⬜ to make · Save as `G3_mud_house_tin_roof.png` (replacing G3) · Landscape 3:2 · Attach: `G3_mud_house_tin_roof.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G3_mud_house_tin_roof.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P55 · G4 · Plank and sheet house

⬜ to make · Save as `G4_plank_sheet_house.png` (replacing G4) · Landscape 3:2 · Attach: `G4_plank_sheet_house.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G4_plank_sheet_house.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; a new bright saree as the door curtain.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P56 · G5 · Village head's house

⬜ to make · Save as `G5_village_head_house.png` (replacing G5) · Landscape 3:2 · Attach: `G5_village_head_house.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G5_village_head_house.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door, with more thoranams strung between the veranda pillars and marigold garlands round every pillar; the brass lamp by the door lit; in front of the steps, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it, in brass, larger than the others.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P57 · G6 · Tiled house with courtyard gate

⬜ to make · Save as `G6_tiled_house_gate.png` (replacing G6) · Landscape 3:2 · Attach: `G6_tiled_house_gate.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G6_tiled_house_gate.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: over the courtyard gate and at it, a string of fresh mango leaves (a thoranam) hung across the top of the gate, a marigold garland swagged over the gate, a bright Pongal kolam on the ground in front of the gate, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the gate.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P58 · G7 · Provisions shop

⬜ to make · Save as `G7_provisions_shop.png` (replacing G7) · Landscape 3:2 · Attach: `G7_provisions_shop.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G7_provisions_shop.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the awning's edge, a marigold garland on the signboard, bundles of sugarcane for sale leaning against the bench, bunches of turmeric plants hanging with the snacks, and a coloured kolam in front.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P59 · G8 · Tea stall

⬜ to make · Save as `G8_tea_stall.png` (replacing G8) · Landscape 3:2 · Attach: `G8_tea_stall.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G8_tea_stall.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the thatch's edge, a marigold garland on the kettle's shelf, two sugarcane stalks leaning beside the bench, and a coloured kolam in front.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P60 · G9 · Tailor and cycle repair

⬜ to make · Save as `G9_tailor_cycle_shop.png` (replacing G9) · Landscape 3:2 · Attach: `G9_tailor_cycle_shop.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G9_tailor_cycle_shop.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of mango leaves along the awning's edge, new bright festival blouses and a silk saree hung up at the tailor's, a marigold garland on the sewing machine and on the cycle pump, and a coloured kolam in front of each shop.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P61 · G10 · Potter's house

⬜ to make · Save as `G10_potters_house.png` (replacing G10) · Landscape 3:2 · Attach: `G10_potters_house.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G10_potters_house.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; at the front, rows of new Pongal pots painted with white lime stripes and red kumkum dots, some with turmeric plants tied round their necks; a mango-leaf thoranam along the work shed's eave.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P62 · G11 · Weaver's house

⬜ to make · Save as `G11_weavers_house.png` (replacing G11) · Landscape 3:2 · Attach: `G11_weavers_house.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G11_weavers_house.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door; a finished magenta silk saree hung up beside the door.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P63 · G12 · House being built

⬜ to make · Save as `G12_house_being_built.png` (replacing G12) · Landscape 3:2 · Attach: `G12_house_being_built.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G12_house_being_built.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a mango-leaf thoranam and a marigold garland on the standing door frame, and a small coloured kolam on the ground before it (the blessing for a new house).

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P64 · G13 · Cattle shed

⬜ to make · Save as `G13_cattle_shed.png` (replacing G13) · Landscape 3:2 · Attach: `G13_cattle_shed.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G13_cattle_shed.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: for Mattu Pongal, the calf with its small horns painted red and green, a marigold garland and a brass bell; a mango-leaf thoranam along the shed's eave; turmeric and kumkum dots on the posts; two sugarcane stalks tied to the front posts; a coloured kolam in front.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P65 · G14 · Panchayat office

⬜ to make · Save as `G14_panchayat_office.png` (replacing G14) · Landscape 3:2 · Attach: `G14_panchayat_office.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G14_panchayat_office.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: mango-leaf thoranams along the veranda, marigold garlands round the pillars, two sugarcane stalks either side of the steps, a coloured kolam in front, and a string of triangular cloth bunting along the roof.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P66 · G15 · Village shrine

⬜ to make · Save as `G15_village_shrine.png` (replacing G15) · Landscape 3:2 · Attach: `G15_village_shrine.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G15_village_shrine.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: more marigold garlands, every oil lamp lit, two sugarcane stalks tied either side of the entrance, a coloured kolam in front, and beside it a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P67 · G16 · Stone lamp pillar

⬜ to make · Save as `G16_stone_lamp_pillar.png` (replacing G16) · Landscape 3:2 · Attach: `G16_stone_lamp_pillar.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (G16_stone_lamp_pillar.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a small flame lit on every lamp ledge, more marigold garlands at its foot, two sugarcane stalks tied either side of the base, and a coloured kolam round the base.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P68 · H3 · Meeting tree with platform

⬜ to make · Save as `H3_peepal_platform.png` (replacing H3) · Landscape 3:2 · Attach: `H3_peepal_platform.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (H3_peepal_platform.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: fresh marigold garlands on the stone idols, the clay lamps lit, two sugarcane stalks leaning on the platform, and a coloured kolam on the ground in front of it.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P69 · K1 · Doors and windows

⬜ to make · Save as `K1_doors_windows.png` (replacing K1) · Landscape 3:2 · Attach: `K1_doors_windows.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (K1_doors_windows.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: a string of fresh mango leaves across the top of every door, and marigold garlands on the carved double door and the blue plank door.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
```

### P70 · K3 · Doorstep and wall details

⬜ to make · Save as `K3_wall_details.png` (replacing K3) · Landscape 3:2 · Attach: `K3_wall_details.png`

```text
Landscape 3:2 image, the same shape as the attached one.

Edit the attached image (K3_wall_details.png) so it shows the village on Pongal, the harvest festival. Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same shape, the same gaps between the pieces, the same painted style and colours, and the same plain light-grey background.

Add only these Pongal festival touches, painted in the same style and light as the rest: the kolams on the three front steps filled with bright red, yellow, green and pink powder; the mango-leaf garland fresher; and, as one more separate piece at the end of the row, a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it, with two sugarcane stalks beside it.

Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric lights, fireworks or text.
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
