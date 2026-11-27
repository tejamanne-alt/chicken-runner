# Chicken Runner — 3D view prompts (for Meshy)

One image per asset: the asset drawn four times in a 2 by 2 grid (front, left side, right side, back), from its painting, for building its 3D model in Meshy. The web version has each painting to save and attach, copy buttons, a checklist, and a tool that cuts a finished sheet into the four views Meshy wants.

## How to use it

1. Attach the asset's painting (`<name>.jpg`; the web version saves it) and paste its prompt.
2. Save the image as `<name>_views.png`. Regenerate it if a view is missing, mirrored wrongly (the left side view faces left, the right side view faces right), cropped, or has labels or a coloured background.
3. Cut it into `<name>_front.png`, `<name>_left.png`, `<name>_right.png` and `<name>_back.png` (the web version does this) and give the four to Meshy's multi-image to 3D, each in its slot.
4. Download the model as GLB, named `<name>.glb`, and put it in `ArtSource/models_meshy/<folder>/` (or upload it in the chat). `finish_models.py` fits it into the game at the painting's size and place.

## Which assets

Only the 36 worth a full model, in the order the levels meet them: the pieces the kid touches on the lane, and the pickups; plus the rooster, from his four existing views, and the kid, from four new views (ChatGPT and Gemini prompts for each). The game's camera watches the lane from the side, so everything else (the houses, trees, animals and people beside the lane and far off) is seen from the front, where its painting is already exactly right: it stays a painted card. Run `view_prompts.py --all` for a prompt for every asset.

## Pickups and the rooster

On screen all the time: the pickups spin as the kid collects them, and the rooster runs ahead of her in every level.

### The kid · `kid`

Four new images, one per view, made from her model sheet (A0) and given to Meshy as front, left, right and back. They change the sheet's leopard-print hairband for a simple plain one in peacock blue and add what the model needs beyond it: gold jhumka earrings, gold and glass bangles, and maruthani (henna) on her hands and legs. They are drawn the way Meshy and rigging need them: one square frame and scale for all four (head and feet at the same heights), standing as in the model sheet with the arms clear of the body, orthographic, evenly lit with no shadows, on plain light grey. A Meshy texture prompt adds what the views cannot show (her inner shorts, the henna on her palms).

Model: `ArtSource/models_meshy/characters/kid.glb`

1. Make the front view first, attaching `A0_kid_pattu_frock_sheet.png`. In the same chat, make the left, right and back views, one per message, attaching the sheet and the front view you made (`kid_meshy_front.png`): the front fixes her scale, pose, colours, jewellery and henna for the others.
2. Check each image: her arms hang relaxed a little away from her sides, palms towards her thighs, as in the model sheet, with a gap of background between each arm and the skirt; each hand has a thumb and four separate fingers with only their tips hennaed; the two jhumkas are an identical pair; the hem border, plain hairband, bangles, anklets and henna (dyed fingertips and toe tips, one leaf vine on the back of each hand, on the top of each foot and up each shin, dot rings round the ankles, dyed sole edges) are the same in all four; in the left view she faces the left edge, in the right view the right edge; no shadow, floor or text.
3. Fix a view by asking for just the change, in the same chat. Facing the wrong way: *Flip this image left to right and keep everything else the same.* Hands wrong: *Make her arms hang relaxed a little away from her sides with her palms towards her thighs, exactly as in the model sheet, each hand with a thumb and four separate fingers, and keep everything else the same.* Earrings: *Make both earrings the same small gold jhumka and keep everything else the same.* Henna: *Make the henna exactly the design in the front view and keep everything else the same.* Hairband: *Make the hairband a plain peacock-blue band with no pattern and keep everything else the same.* A back view with front details (palms, toes, henna on the backs of the legs): *Using the image you just made, show her hands and feet from behind: the backs of her hands, her heels with her toes hidden, and the backs of her legs plain skin. Keep everything else the same.*
4. Save them as `kid_meshy_front.png`, `kid_meshy_left.png`, `kid_meshy_right.png` and `kid_meshy_back.png` in `ArtSource/references/`.
5. In Meshy, **Image to 3D** with several images: upload the four as front, left, right and back. Turn **symmetry on**: it makes the two earrings, hands and feet match. Choose the newest model, texture on, and if it asks for a pose, the A-pose (her relaxed stance is close to one). Paste the **Meshy texture prompt** below where Meshy takes a texture prompt. Keep the triangle count low: a target of about 30,000, or **Remesh** to about 30,000 triangles after (the first try came out at 1.5 million; the game's budget for the kid is 15,000, and I reduce it from 30,000).
6. If the texture still has a mismatched earring, blotchy fingers or bare thighs under the skirt, run Meshy's **Retexture** on the model with the same texture prompt (and `kid_meshy_front.png` as its reference image).
7. Download it as GLB with the texture inside and save it as `ArtSource/models_meshy/characters/kid.glb` (or upload it in the chat). I then fit it to the game (1.05 m tall), check it all round, put right what is left (the same jhumka on both ears, the inner shorts as real cloth if they are only painted, the triangle budget), and rig it for Unity's Humanoid, with the hand socket for the rooster.

#### Front · `kid_meshy_front.png`

Square 1:1 · Attach: `A0_kid_pattu_frock_sheet.png`

ChatGPT:

```text
Square 1:1 image.

Full-length front view, for 3D modelling, of the toddler hero from the attached model sheet (A0_kid_pattu_frock_sheet.png). Match her face, skin tone, hair, frock, anklets, proportions and painted style exactly; replace the leopard-print hairband with the plain one described below, and add the earrings, bangles and henna described below. She is a South Indian girl of about three, with chubby toddler proportions (a big head about a quarter of her height, short arms and legs), warm brown skin, a round face with big dark eyes, a small red bindi and a gentle closed-mouth smile, and shoulder-length wavy black hair held back by a simple plain hairband: a smooth, narrow band in solid peacock blue, the colour of her frock, with no pattern, print or bow. She wears a knee-length peacock-blue silk pattu frock: a fitted bodice with a gold zari neckline with a short slit at the front, short puffed sleeves edged in gold, a blue sash at the waist, and a gathered, flared skirt with a wide magenta and gold border at the hem woven with small temple towers. Bare feet with silver anklets with tiny bells.

Her jewellery: a matching pair of small gold jhumka earrings, identical in size and shape, one bell-shaped gold drop hanging from each earlobe, both ears showing through her hair; and on each wrist the same set of a few thin gold bangles with red and green glass bangles between them, sitting loosely at the wrist.

Her maruthani (henna) is one fixed design, the same in every view, identical on both hands (mirror images) and on both legs, in one flat deep orange-red with no other colour: the tip of every finger dyed up to the first knuckle, the rest of each finger skin-coloured, so the fingers stay slender and separate; on the back of each hand, one vine of small paired leaves running from the base of the middle finger to the wrist, ending in a row of small dots just below the bangles; the tip of every toe dyed; a thin dyed band round the edge of each sole; on the top of each foot, one vine of small paired leaves from the big toe to the ankle; a ring of small dots round each ankle, just below the anklet; and on the front of each shin, one vine of small paired leaves rising halfway to the knee, ending in a small dot. Nothing else is hennaed: not her arms above the wrists, not her legs above that dot. From the front we see the backs of her hands, turned a little towards us, with their leaf vines and the dots below the bangles, the dyed fingertips, the dyed toe tips, the leaf vines on the tops of both feet, the rings of dots round the ankles and the leaf vines up the fronts of the shins.

She faces the viewer squarely and stands exactly as in the model sheet: upright and symmetrical, her weight on both feet, her feet flat, toes forward and a hand's width apart; her arms hanging relaxed and straight, held a little away from her sides (about 20 degrees), so a clear gap of background shows between each arm and her body and skirt; her hands relaxed beside her skirt, palms facing in towards her thighs, the backs of her hands turned a little towards us, each hand with a thumb and four separate, slender toddler fingers, gently curled; her head level, looking straight ahead; her hair resting on her shoulders, clear of her arms and earrings. A calm, pleasant face with the mouth closed.

Only her: one full-length figure, centred, from the top of her hair to the soles of her feet, filling about 85% of the image height, clear space all round, nothing cropped. Orthographic, no perspective, seen straight on at her chest height. Even, soft front lighting so her colours read true: no cast shadows, no strong highlights. Plain flat light-grey background: no floor, no shadow on the ground, no text, labels, frames or other objects.
```

Gemini:

```text
Create a 1:1 square image.

Use the image I've uploaded: the kid's model sheet, for her face, skin tone, hair, frock, anklets, proportions and painted style. Match it exactly, but replace the leopard-print hairband with the plain one described below, and add the earrings, bangles and henna described below.

A full-length front view of the toddler hero from the model sheet, for building a 3D model: a South Indian girl of about three, with chubby toddler proportions (a big head about a quarter of her height, short arms and legs), warm brown skin, a round face with big dark eyes, a small red bindi and a gentle closed-mouth smile, and shoulder-length wavy black hair held back by a simple plain hairband: a smooth, narrow band in solid peacock blue, the colour of her frock, with no pattern, print or bow. She wears a knee-length peacock-blue silk pattu frock: a fitted bodice with a gold zari neckline with a short slit at the front, short puffed sleeves edged in gold, a blue sash at the waist, and a gathered, flared skirt with a wide magenta and gold border at the hem woven with small temple towers. Bare feet with silver anklets with tiny bells.

Her jewellery: a matching pair of small gold jhumka earrings, identical in size and shape, one bell-shaped gold drop hanging from each earlobe, both ears showing through her hair; and on each wrist the same set of a few thin gold bangles with red and green glass bangles between them, sitting loosely at the wrist.

Her maruthani (henna) is one fixed design, the same in every view, identical on both hands (mirror images) and on both legs, in one flat deep orange-red with no other colour: the tip of every finger dyed up to the first knuckle, the rest of each finger skin-coloured, so the fingers stay slender and separate; on the back of each hand, one vine of small paired leaves running from the base of the middle finger to the wrist, ending in a row of small dots just below the bangles; the tip of every toe dyed; a thin dyed band round the edge of each sole; on the top of each foot, one vine of small paired leaves from the big toe to the ankle; a ring of small dots round each ankle, just below the anklet; and on the front of each shin, one vine of small paired leaves rising halfway to the knee, ending in a small dot. Nothing else is hennaed: not her arms above the wrists, not her legs above that dot. From the front we see the backs of her hands, turned a little towards us, with their leaf vines and the dots below the bangles, the dyed fingertips, the dyed toe tips, the leaf vines on the tops of both feet, the rings of dots round the ankles and the leaf vines up the fronts of the shins.

She faces the viewer squarely and stands exactly as in the model sheet: upright and symmetrical, her weight on both feet, her feet flat, toes forward and a hand's width apart; her arms hanging relaxed and straight, held a little away from her sides (about 20 degrees), so a clear gap of background shows between each arm and her body and skirt; her hands relaxed beside her skirt, palms facing in towards her thighs, the backs of her hands turned a little towards us, each hand with a thumb and four separate, slender toddler fingers, gently curled; her head level, looking straight ahead; her hair resting on her shoulders, clear of her arms and earrings. A calm, pleasant face with the mouth closed.

Show only her: one full-length figure, centred, from the top of her hair to the soles of her feet, filling about 85 percent of the image height, with clear space all round and nothing cropped. Draw her orthographic and straight on at her own chest height, with no perspective. Light her evenly and softly from the front, so her colours read true, with no cast shadows and no strong highlights. A plain, flat light-grey background, with no floor, no shadow on the ground, and no text, labels, frames or other objects.
```

#### Left · `kid_meshy_left.png`

Square 1:1 · Attach: `A0_kid_pattu_frock_sheet.png`, `kid_meshy_front.png`

ChatGPT:

```text
Square 1:1 image.

Left side view, for 3D modelling, of the same toddler as in the attached images: the model sheet (A0_kid_pattu_frock_sheet.png) for her face, hair, frock, anklets and painted style, and the front view (kid_meshy_front.png) for her exact size, position in the frame, pose, colours, plain hairband (not the sheet's leopard-print one), earrings, bangles and henna (the same design in the same places). Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from her left side: a true 90-degree profile, so we see her left side and she faces the left edge of the image. She stands in the same pose as in the front view, seen from the side: her arms hanging relaxed a little away from her sides, her near hand beside her skirt with its palm towards her thigh, a thumb and four separate fingers gently curled, and her feet a hand's width apart. Show her profile clearly: the round cheek, the small nose and the closed-mouth smile, her ear with its small gold jhumka hanging below it, the plain peacock-blue hairband over the top of her head, her wavy hair falling to her shoulder at the back, the puffed sleeve with its gold edge, the gold and glass bangles on her wrist, the sash at the waist with the end of the bow at the back, the flared skirt with the magenta and gold temple-tower border running round it, and her bare feet with the silver anklets.

Her maruthani (henna) is one fixed design, the same in every view, identical on both hands (mirror images) and on both legs, in one flat deep orange-red with no other colour: the tip of every finger dyed up to the first knuckle, the rest of each finger skin-coloured, so the fingers stay slender and separate; on the back of each hand, one vine of small paired leaves running from the base of the middle finger to the wrist, ending in a row of small dots just below the bangles; the tip of every toe dyed; a thin dyed band round the edge of each sole; on the top of each foot, one vine of small paired leaves from the big toe to the ankle; a ring of small dots round each ankle, just below the anklet; and on the front of each shin, one vine of small paired leaves rising halfway to the knee, ending in a small dot. Nothing else is hennaed: not her arms above the wrists, not her legs above that dot. From the side we see, on her near hand and leg, exactly the design of the front view: the back of the hand with its leaf vine and the row of dots below the bangles, the dyed fingertips, the dyed toe tips, the dyed band along the edge of the sole, the leaf vine on the top of the foot from the side, the ring of dots round the ankle and the leaf vine up the front of the shin.

The same size and place in the frame as the attached front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85% of the image height, clear space all round, nothing cropped. Orthographic, no perspective, seen straight on at her chest height. Even, soft lighting: no cast shadows, no strong highlights. Plain flat light-grey background: no floor, no shadow on the ground, no text, labels, frames or other objects.
```

Gemini:

```text
Create a 1:1 square image.

Use the images I've uploaded: the kid's model sheet, for her face, hair, frock, anklets and painted style; and the front view, for her exact size, position in the frame, pose, colours, plain hairband (not the sheet's leopard-print one), earrings, bangles and henna (the same design in the same places). Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from her left side: a true 90-degree profile, so we see her left side and she faces the left edge of the image. She stands in the same pose as in the front view, seen from the side: her arms hanging relaxed a little away from her sides, her near hand beside her skirt with its palm towards her thigh, a thumb and four separate fingers gently curled, and her feet a hand's width apart. Show her profile clearly: the round cheek, the small nose and the closed-mouth smile, her ear with its small gold jhumka hanging below it, the plain peacock-blue hairband over the top of her head, her wavy hair falling to her shoulder at the back, the puffed sleeve with its gold edge, the gold and glass bangles on her wrist, the sash at the waist with the end of the bow at the back, the flared skirt with the magenta and gold temple-tower border running round it, and her bare feet with the silver anklets.

Her maruthani (henna) is one fixed design, the same in every view, identical on both hands (mirror images) and on both legs, in one flat deep orange-red with no other colour: the tip of every finger dyed up to the first knuckle, the rest of each finger skin-coloured, so the fingers stay slender and separate; on the back of each hand, one vine of small paired leaves running from the base of the middle finger to the wrist, ending in a row of small dots just below the bangles; the tip of every toe dyed; a thin dyed band round the edge of each sole; on the top of each foot, one vine of small paired leaves from the big toe to the ankle; a ring of small dots round each ankle, just below the anklet; and on the front of each shin, one vine of small paired leaves rising halfway to the knee, ending in a small dot. Nothing else is hennaed: not her arms above the wrists, not her legs above that dot. From the side we see, on her near hand and leg, exactly the design of the front view: the back of the hand with its leaf vine and the row of dots below the bangles, the dyed fingertips, the dyed toe tips, the dyed band along the edge of the sole, the leaf vine on the top of the foot from the side, the ring of dots round the ankle and the leaf vine up the front of the shin.

Keep her the same size and in the same place as in the front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85 percent of the image height, with clear space all round and nothing cropped. Draw her orthographic and straight on at her own chest height, with no perspective. Light her evenly and softly, with no cast shadows and no strong highlights. A plain, flat light-grey background, with no floor, no shadow on the ground, and no text, labels, frames or other objects.
```

#### Right · `kid_meshy_right.png`

Square 1:1 · Attach: `A0_kid_pattu_frock_sheet.png`, `kid_meshy_front.png`

ChatGPT:

```text
Square 1:1 image.

Right side view, for 3D modelling, of the same toddler as in the attached images: the model sheet (A0_kid_pattu_frock_sheet.png) for her face, hair, frock, anklets and painted style, and the front view (kid_meshy_front.png) for her exact size, position in the frame, pose, colours, plain hairband (not the sheet's leopard-print one), earrings, bangles and henna (the same design in the same places). Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from her right side: a true 90-degree profile, so we see her right side and she faces the right edge of the image. She stands in the same pose as in the front view, seen from the side: her arms hanging relaxed a little away from her sides, her near hand beside her skirt with its palm towards her thigh, a thumb and four separate fingers gently curled, and her feet a hand's width apart. Show her profile clearly: the round cheek, the small nose and the closed-mouth smile, her ear with its small gold jhumka hanging below it, the plain peacock-blue hairband over the top of her head, her wavy hair falling to her shoulder at the back, the puffed sleeve with its gold edge, the gold and glass bangles on her wrist, the sash at the waist with the end of the bow at the back, the flared skirt with the magenta and gold temple-tower border running round it, and her bare feet with the silver anklets.

Her maruthani (henna) is one fixed design, the same in every view, identical on both hands (mirror images) and on both legs, in one flat deep orange-red with no other colour: the tip of every finger dyed up to the first knuckle, the rest of each finger skin-coloured, so the fingers stay slender and separate; on the back of each hand, one vine of small paired leaves running from the base of the middle finger to the wrist, ending in a row of small dots just below the bangles; the tip of every toe dyed; a thin dyed band round the edge of each sole; on the top of each foot, one vine of small paired leaves from the big toe to the ankle; a ring of small dots round each ankle, just below the anklet; and on the front of each shin, one vine of small paired leaves rising halfway to the knee, ending in a small dot. Nothing else is hennaed: not her arms above the wrists, not her legs above that dot. From the side we see, on her near hand and leg, exactly the design of the front view: the back of the hand with its leaf vine and the row of dots below the bangles, the dyed fingertips, the dyed toe tips, the dyed band along the edge of the sole, the leaf vine on the top of the foot from the side, the ring of dots round the ankle and the leaf vine up the front of the shin.

The same size and place in the frame as the attached front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85% of the image height, clear space all round, nothing cropped. Orthographic, no perspective, seen straight on at her chest height. Even, soft lighting: no cast shadows, no strong highlights. Plain flat light-grey background: no floor, no shadow on the ground, no text, labels, frames or other objects.
```

Gemini:

```text
Create a 1:1 square image.

Use the images I've uploaded: the kid's model sheet, for her face, hair, frock, anklets and painted style; and the front view, for her exact size, position in the frame, pose, colours, plain hairband (not the sheet's leopard-print one), earrings, bangles and henna (the same design in the same places). Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from her right side: a true 90-degree profile, so we see her right side and she faces the right edge of the image. She stands in the same pose as in the front view, seen from the side: her arms hanging relaxed a little away from her sides, her near hand beside her skirt with its palm towards her thigh, a thumb and four separate fingers gently curled, and her feet a hand's width apart. Show her profile clearly: the round cheek, the small nose and the closed-mouth smile, her ear with its small gold jhumka hanging below it, the plain peacock-blue hairband over the top of her head, her wavy hair falling to her shoulder at the back, the puffed sleeve with its gold edge, the gold and glass bangles on her wrist, the sash at the waist with the end of the bow at the back, the flared skirt with the magenta and gold temple-tower border running round it, and her bare feet with the silver anklets.

Her maruthani (henna) is one fixed design, the same in every view, identical on both hands (mirror images) and on both legs, in one flat deep orange-red with no other colour: the tip of every finger dyed up to the first knuckle, the rest of each finger skin-coloured, so the fingers stay slender and separate; on the back of each hand, one vine of small paired leaves running from the base of the middle finger to the wrist, ending in a row of small dots just below the bangles; the tip of every toe dyed; a thin dyed band round the edge of each sole; on the top of each foot, one vine of small paired leaves from the big toe to the ankle; a ring of small dots round each ankle, just below the anklet; and on the front of each shin, one vine of small paired leaves rising halfway to the knee, ending in a small dot. Nothing else is hennaed: not her arms above the wrists, not her legs above that dot. From the side we see, on her near hand and leg, exactly the design of the front view: the back of the hand with its leaf vine and the row of dots below the bangles, the dyed fingertips, the dyed toe tips, the dyed band along the edge of the sole, the leaf vine on the top of the foot from the side, the ring of dots round the ankle and the leaf vine up the front of the shin.

Keep her the same size and in the same place as in the front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85 percent of the image height, with clear space all round and nothing cropped. Draw her orthographic and straight on at her own chest height, with no perspective. Light her evenly and softly, with no cast shadows and no strong highlights. A plain, flat light-grey background, with no floor, no shadow on the ground, and no text, labels, frames or other objects.
```

#### Back · `kid_meshy_back.png`

Square 1:1 · Attach: `A0_kid_pattu_frock_sheet.png`, `kid_meshy_front.png`

ChatGPT:

```text
Square 1:1 image.

Back view, for 3D modelling, of the same toddler as in the attached images: the model sheet (A0_kid_pattu_frock_sheet.png) for her hair, frock, anklets and painted style, and the front view (kid_meshy_front.png) for her exact size, position in the frame, pose, colours, plain hairband (not the sheet's leopard-print one), earrings, bangles and henna design, seen here from behind. Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from behind: we look at her back, and she faces away from us, into the picture, so her face and the fronts of her legs are turned away. She stands in the same pose as in the front view, seen from the back: her arms hanging relaxed a little away from her sides (about 20 degrees), with a clear gap between each arm and her body and skirt, and her feet flat and a hand's width apart.

Show her back clearly: the back of her head, all shoulder-length wavy black hair; a thin arc of the plain peacock-blue hairband showing across the top of her head; the gold jhumka earrings just peeping out below her hair on each side; the plain back of the bodice with a fine seam down the middle; the puffed sleeves with their gold edges; the blue sash tied in a neat bow at the back of the waist; the gathered skirt with the magenta and gold temple-tower border continuing all the way round; the backs of her knees and calves, plain bare skin; the silver anklets; and her two round heels, the soles' edges just showing beneath them.

Her hands hang beside her skirt with their palms towards her thighs, so from behind we see the outer edges and backs of her hands, fingers gently curled, the gold and glass bangles at the wrists. Her feet point away from us, so we see her heels and the backs of her ankles, with her toes hidden in front of her feet.

Her maruthani (henna) from the front view, as it looks from behind, is only this, in the same flat deep orange-red: on the back of each hand, one vine of small paired leaves from the base of the middle finger to the wrist, ending in a row of small dots just below the bangles; the dyed fingertips showing as orange-red tips round the fingernails; a ring of small dots round the back of each ankle, just below the anklet; and a thin orange-red rim round each heel, where the dyed edge of the sole shows. The backs of her legs are plain bare skin.

The same size and place in the frame as the attached front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85% of the image height, clear space all round, nothing cropped. Orthographic, no perspective, seen straight on at her chest height. Even, soft lighting: no cast shadows, no strong highlights. Plain flat light-grey background: no floor, no shadow on the ground, no text, labels, frames or other objects.
```

Gemini:

```text
Create a 1:1 square image.

Use the images I've uploaded: the kid's model sheet, for her hair, frock, anklets and painted style; and the front view, for her exact size, position in the frame, pose, colours, plain hairband (not the sheet's leopard-print one), earrings, bangles and henna design, seen here from behind. Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from behind: we look at her back, and she faces away from us, into the picture, so her face and the fronts of her legs are turned away. She stands in the same pose as in the front view, seen from the back: her arms hanging relaxed a little away from her sides (about 20 degrees), with a clear gap between each arm and her body and skirt, and her feet flat and a hand's width apart.

Show her back clearly: the back of her head, all shoulder-length wavy black hair; a thin arc of the plain peacock-blue hairband showing across the top of her head; the gold jhumka earrings just peeping out below her hair on each side; the plain back of the bodice with a fine seam down the middle; the puffed sleeves with their gold edges; the blue sash tied in a neat bow at the back of the waist; the gathered skirt with the magenta and gold temple-tower border continuing all the way round; the backs of her knees and calves, plain bare skin; the silver anklets; and her two round heels, the soles' edges just showing beneath them.

Her hands hang beside her skirt with their palms towards her thighs, so from behind we see the outer edges and backs of her hands, fingers gently curled, the gold and glass bangles at the wrists. Her feet point away from us, so we see her heels and the backs of her ankles, with her toes hidden in front of her feet.

Her maruthani (henna) from the front view, as it looks from behind, is only this, in the same flat deep orange-red: on the back of each hand, one vine of small paired leaves from the base of the middle finger to the wrist, ending in a row of small dots just below the bangles; the dyed fingertips showing as orange-red tips round the fingernails; a ring of small dots round the back of each ankle, just below the anklet; and a thin orange-red rim round each heel, where the dyed edge of the sole shows. The backs of her legs are plain bare skin.

Keep her the same size and in the same place as in the front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85 percent of the image height, with clear space all round and nothing cropped. Draw her orthographic and straight on at her own chest height, with no perspective. Light her evenly and softly, with no cast shadows and no strong highlights. A plain, flat light-grey background, with no floor, no shadow on the ground, and no text, labels, frames or other objects.
```

#### Meshy texture prompt

For Meshy's texture prompt in Image to 3D, or for Retexture on the finished model:

```text
South Indian toddler girl, hand-painted storybook style, even light, no baked shadows. Peacock-blue silk pattu frock, gold zari neckline and sleeve edges, magenta and gold temple-tower hem border; short peacock-blue cotton bloomers on her upper thighs under the skirt. Plain peacock-blue hairband. Identical pair of small gold jhumka earrings. Gold and red-green glass bangles, silver anklets. Skin-toned hands, five separate fingers, only fingertips dyed orange-red henna; henna dot ring on each palm; henna leaf vine on the back of each hand, top of each foot and each shin; dyed toe tips.
```

### 1. Mango · `mango`

**On the lane** · Save as `mango_views.png` · Square 1:1 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/pickups/mango.glb`

Note: No painting of it yet: the prompt describes it.

```text
Square 1:1 image.

Model sheet for 3D modelling of a ripe mango, golden yellow blushing to red, with a short stalk and one green leaf, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a single small object on its own: show the whole of it from every side. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 2. Chilli · `chilli`

**On the lane** · Save as `chilli_views.png` · Square 1:1 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/pickups/chilli.glb`

Note: No painting of it yet: the prompt describes it.

```text
Square 1:1 image.

Model sheet for 3D modelling of a single bright red chilli with a green cap and a gently curled tip, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a single small object on its own: show the whole of it from every side. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 3. Golden tail feather · `feather`

**On the lane** · Save as `feather_views.png` · Square 1:1 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/pickups/feather.glb`

Note: No painting of it yet: the prompt describes it.

```text
Square 1:1 image.

Model sheet for 3D modelling of a single long, curved golden rooster tail feather with a glossy sheen, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a single small object on its own: show the whole of it from every side. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 4. The rooster · `rooster`

No new images: his four views exist already (B11 front, B13 left, B14 right, B12 back). Use them in Meshy.

Images: `B11_rooster_front.png`, `B13_rooster_left.png`, `B14_rooster_right.png`, `B12_rooster_back.png`

## Levels 1–3: the lane

Pots and the sleeping dog, washing day, and up on the roofs.

### 5. Stack of clay pots · `pot_stack`

**On the lane** · Save as `pot_stack_views.png` · Portrait 2:3 · Attach: pot_stack.jpg (its painting) · Model: `ArtSource/models_meshy/lane/pot_stack.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of three red clay pots of decreasing size stacked one on another, painted with white and yellow triangles, drawn exactly like the attached painting (pot_stack.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 6. Sleeping dog · `dog_sleeping`

**On the lane** · Save as `dog_sleeping_views.png` · Landscape 3:2 · Attach: dog_sleeping.jpg (its painting) · Model: `ArtSource/models_meshy/animals/dog_sleeping.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a ginger-and-white village dog curled up asleep, chin on its paws, drawn exactly like the attached painting (dog_sleeping.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 7. Hand pump · `hand_pump`

**On the lane** · Save as `hand_pump_views.png` · Square 1:1 · Attach: hand_pump.jpg (its painting) · Model: `ArtSource/models_meshy/lane/hand_pump.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a green cast-iron village hand pump on a stone base, with a steel bucket and a small puddle, drawn exactly like the attached painting (hand_pump.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 8. Clothesline · `clothesline`

**On the lane** · Save as `clothesline_views.png` · Landscape 3:2 · Attach: clothesline.jpg (its painting) · Model: `ArtSource/models_meshy/lane/clothesline.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a rope clothesline between two bamboo posts, with a magenta and a yellow cloth hanging on it, drawn exactly like the attached painting (clothesline.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It is thin: the posts and the hanging cloths are its whole depth. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 9. Rope cot · `rope_cot`

**On the lane** · Save as `rope_cot_views.png` · Landscape 3:2 · Attach: rope_cot.jpg (its painting) · Model: `ArtSource/models_meshy/lane/rope_cot.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a wooden rope cot (charpai) with turned legs and a woven jute top, a striped pillow at one end, drawn exactly like the attached painting (rope_cot.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. From the ends it is about 85 cm deep. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 10. Bullock cart · `bullock_cart`

**On the lane** · Save as `bullock_cart_views.png` · Landscape 3:2 · Attach: bullock_cart.jpg (its painting) · Model: `ArtSource/models_meshy/lane/bullock_cart.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a wooden bullock cart with two big spoked wheels, painted side boards, hay in its bed and its yoke pole resting on a prop, drawn exactly like the attached painting (bullock_cart.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it from its front end and the back view from behind; both side views show the same wheels and boards. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 11. Water pot on a stand · `water_pot_stand`

**On the lane** · Save as `water_pot_stand_views.png` · Square 1:1 · Attach: water_pot_stand.jpg (its painting) · Model: `ArtSource/models_meshy/lane/water_pot_stand.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a big red clay water pot with a brass tap, on a stone stand of two upright slabs and a top slab, drawn exactly like the attached painting (water_pot_stand.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 12. Brass pots · `brass_pots`

**On the lane** · Save as `brass_pots_views.png` · Landscape 3:2 · Attach: brass_pots.jpg (its painting) · Model: `ArtSource/models_meshy/lane/brass_pots.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of two round brass water pots (kudam), one big and one small, on the ground, drawn exactly like the attached painting (brass_pots.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 13. Indigo house with a veranda · `house_indigo_veranda`

**On the lane** · Save as `house_indigo_veranda_views.png` · Square 1:1 · Attach: house_indigo_veranda.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_indigo_veranda.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a narrow indigo-blue lime-washed house with a red-tiled veranda roof on turned wooden pillars, a carved door with a garland, a window and kolam steps, drawn exactly like the attached painting (house_indigo_veranda.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 14. Lime-washed house · `house_limewash`

**On the lane** · Save as `house_limewash_views.png` · Portrait 2:3 · Attach: house_limewash.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_limewash.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a narrow cream lime-washed flat-roofed house with a parapet, a teal-framed carved door with a garland, a bougainvillea vine and kolam steps, drawn exactly like the attached painting (house_limewash.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 15. Pink house · `house_pink`

**On the lane** · Save as `house_pink_views.png` · Portrait 2:3 · Attach: house_pink.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_pink.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a narrow pink lime-washed flat-roofed house with a parapet, a teal-framed carved door with a garland, a jasmine vine, a potted hibiscus and kolam steps, drawn exactly like the attached painting (house_pink.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 16. Turmeric house (the ladder is separate) · `house_turmeric_ladder`

**On the lane** · Save as `house_turmeric_ladder_views.png` · Square 1:1 · Attach: house_turmeric_ladder.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_turmeric_ladder.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a narrow turmeric-yellow flat-roofed house with a parapet, a carved door with a garland, a barred window, a clay pot and kolam steps, drawn exactly like the attached painting (house_turmeric_ladder.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Leave out any ladder: the bamboo ladder the kid climbs is a separate model that the game stands against this house, so its wall at the right end, where the painting once had a ladder, is plain. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## Levels 4–6: the fields

The canal, the mango trees, and the buffalo and haystacks.

### 17. Mango tree · `tree_mango_1`

**On the lane** · Save as `tree_mango_1_views.png` · Square 1:1 · Attach: tree_mango_1.jpg (its painting) · Model: `ArtSource/models_meshy/lane/tree_mango_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a mango tree with a twisted trunk, a dense rounded crown and ripe mangoes, drawn exactly like the attached painting (tree_mango_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 18. Haystack · `haystack`

**On the lane** · Save as `haystack_views.png` · Square 1:1 · Attach: haystack.jpg (its painting) · Model: `ArtSource/models_meshy/fields/haystack.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a tall round haystack of golden straw, tied at the top, drawn exactly like the attached painting (haystack.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 19. Small haystack · `haystack_small`

**On the lane** · Save as `haystack_small_views.png` · Square 1:1 · Attach: haystack_small.jpg (its painting) · Model: `ArtSource/models_meshy/fields/haystack_small.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a smaller round haystack with a pole sticking out of its top, drawn exactly like the attached painting (haystack_small.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 20. Buffalo in the mud · `buffalo_mud`

**On the lane** · Save as `buffalo_mud_views.png` · Landscape 3:2 · Attach: buffalo_mud.jpg (its painting) · Model: `ArtSource/models_meshy/animals/buffalo_mud.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a dark water buffalo lying in a patch of wet mud, with curved horns, a rope halter and a bell, drawn exactly like the attached painting (buffalo_mud.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Show the patch of mud around it in every view. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 21. Village well · `well`

**On the lane** · Save as `well_views.png` · Square 1:1 · Attach: well.jpg (its painting) · Model: `ArtSource/models_meshy/fields/well.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a round stone-built well with a wooden crossbeam, a pulley, a coiled rope and a small bucket, drawn exactly like the attached painting (well.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## Levels 7–9: roofs, market and temple

The rooftop run, market day and the temple steps.

### 22. Water tank · `black_tank`

**On the lane** · Save as `black_tank_views.png` · Square 1:1 · Attach: black_tank.jpg (its painting) · Model: `ArtSource/models_meshy/market/black_tank.glb`

Note: Your style rules rule out black plastic tanks: make it a plastered terracotta tank, keeping its shape and stand.

```text
Square 1:1 image.

Model sheet for 3D modelling of a big round water storage tank on a stone stand, drawn exactly like the attached painting (black_tank.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Your style rules rule out black plastic tanks: make it a plastered terracotta tank, keeping its shape and stand. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 23. Spice stall · `stall_c_1`

**On the lane** · Save as `stall_c_1_views.png` · Landscape 3:2 · Attach: stall_c_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_c_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a spice stall under a faded yellow cotton shade on bamboo poles: open jute sacks of red chillies, turmeric and grains, drawn exactly like the attached painting (stall_c_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 24. Pot stall · `stall_d_2`

**On the lane** · Save as `stall_d_2_views.png` · Square 1:1 · Attach: stall_d_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_d_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a pot stall under a faded indigo cotton shade on bamboo poles: clay pots and jaggery blocks on a low bench, drawn exactly like the attached painting (stall_d_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 25. Parrot fortune teller · `stall_e_3`

**On the lane** · Save as `stall_e_3_views.png` · Square 1:1 · Attach: stall_e_3.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_e_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a fortune teller sitting cross-legged under a big black cloth umbrella, with a caged parrot and cards spread on a mat, drawn exactly like the attached painting (stall_e_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 26. Sweets counter · `stall_f_1`

**On the lane** · Save as `stall_f_1_views.png` · Square 1:1 · Attach: stall_f_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_f_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a sweets stall under an undyed cotton shade: a woman behind a wooden counter with glass jars of sweets, drawn exactly like the attached painting (stall_f_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 27. Flower seller · `stall_flowers`

**On the lane** · Save as `stall_flowers_views.png` · Square 1:1 · Attach: stall_flowers.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_flowers.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a flower seller woman sitting under a woven palm-leaf shade, garlands hanging and baskets of flowers around her, drawn exactly like the attached painting (stall_flowers.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 28. Bangle stall · `stall_g_2`

**On the lane** · Save as `stall_g_2_views.png` · Square 1:1 · Attach: stall_g_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_g_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a bangle stall under a faded indigo cotton shade: racks of coloured glass bangles, a mirror and bowls of kumkum powder, drawn exactly like the attached painting (stall_g_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 29. Cobbler · `stall_h_1`

**On the lane** · Save as `stall_h_1_views.png` · Square 1:1 · Attach: stall_h_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_h_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a cobbler sitting cross-legged under a big black cloth umbrella, sandals and tools spread on a mat, drawn exactly like the attached painting (stall_h_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 30. Vessel stall · `stall_vessels`

**On the lane** · Save as `stall_vessels_views.png` · Landscape 3:2 · Attach: stall_vessels.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_vessels.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a brass and copper vessel stall under a thatched shade: rows of shiny pots, lamps and tumblers, drawn exactly like the attached painting (stall_vessels.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 31. Brown hen pecking · `hen_1`

**On the lane** · Save as `hen_1_views.png` · Square 1:1 · Attach: hen_1.jpg (its painting) · Model: `ArtSource/models_meshy/animals/hen_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a rust-brown hen pecking at scattered grain, drawn exactly like the attached painting (hen_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 32. Buff hen pecking · `hen_2`

**On the lane** · Save as `hen_2_views.png` · Square 1:1 · Attach: hen_2.jpg (its painting) · Model: `ArtSource/models_meshy/animals/hen_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a pale buff hen pecking at scattered grain, drawn exactly like the attached painting (hen_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 33. Dark hen pecking · `hen_3`

**On the lane** · Save as `hen_3_views.png` · Square 1:1 · Attach: hen_3.jpg (its painting) · Model: `ArtSource/models_meshy/animals/hen_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a dark speckled brown hen pecking at scattered grain, drawn exactly like the attached painting (hen_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 34. Hens in a basket · `hens_basket`

**On the lane** · Save as `hens_basket_views.png` · Square 1:1 · Attach: hens_basket.jpg (its painting) · Model: `ArtSource/models_meshy/market/hens_basket.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of two hens sitting in a shallow woven basket of straw, drawn exactly like the attached painting (hens_basket.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 35. Mandapam · `mandapam`

**On the lane** · Save as `mandapam_views.png` · Landscape 3:2 · Attach: mandapam.jpg (its painting) · Model: `ArtSource/models_meshy/market/mandapam.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long, low stone temple pavilion (mandapam) with a row of carved pillars under a flat stone roof, drawn exactly like the attached painting (mandapam.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 36. Lamp steps · `lamp_step`

**On the lane** · Save as `lamp_step_views.png` · Square 1:1 · Attach: lamp_step.jpg (its painting) · Model: `ArtSource/models_meshy/market/lamp_step.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of temple steps of carved yellow stone with a pillar, and lit clay oil lamps on each step, drawn exactly like the attached painting (lamp_step.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### 37. Lantern · `lantern`

**On the lane** · Save as `lantern_views.png` · Portrait 2:3 · Attach: lantern.jpg (its painting) · Model: `ArtSource/models_meshy/market/lantern.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a hurricane lantern with a glowing wick, drawn exactly like the attached painting (lantern.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```
