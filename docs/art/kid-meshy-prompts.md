# The kid for Meshy: four view prompts

Four images of the kid in her pattu frock (front, left, right and back) for Meshy's multi-image to 3D. They follow
the kid's model sheet (`ArtSource/references/A0_kid_pattu_frock_sheet.png`), so she looks the same as in every other
image, and add what the model needs beyond it:

- **Gold jhumka earrings.**
- **Gold and glass bangles** on both wrists.
- **Maruthani** (mehandi, henna) on her hands and legs.

They are drawn the way Meshy and rigging need them:

- **The same scale and place in all four:** a square frame, her head and feet at the same heights in every view.
- **An A-pose:** arms held out from the body with space under them, palms turned forward so their henna shows, feet a
  little apart, so the arms, legs and skirt come out as separate shapes that can be rigged.
- **Flat and orthographic, evenly lit, with no shadows:** the texture is then her true colours. The game adds its own
  toon light and ink outline.
- **A plain light-grey background with nothing else in it.**

Written for Gemini, in the style of [the Gemini prompt sheet](prompt-sheet-gemini.md). They work in ChatGPT too.

## How to make them

1. In a new chat, make the **front** view first, uploading `A0_kid_pattu_frock_sheet.png`.
2. In the same chat, make the **left**, **right** and **back** views, one per message. Each time, upload the sheet and
   the front view you just made (`kid_meshy_front.png`): the front fixes her scale, pose, colours, jewellery and henna
   for the others.
3. Check every image before you go on:
   - the hem border, hairband, earrings, bangles, anklets and henna are the same in all four;
   - her arms are clear of her body;
   - she faces the right way: in the left view she faces the left edge, in the right view the right edge;
   - there is no shadow, no floor and no text.

   If a side view faces the wrong way, reply: *Flip this image left to right and keep everything else the same.*
   If something is missing, ask for just that: *Add the gold jhumka earrings and keep everything else the same.*
4. Save them as `kid_meshy_front.png`, `kid_meshy_left.png`, `kid_meshy_right.png` and `kid_meshy_back.png` in
   `ArtSource/references/`.

## In Meshy

1. **Image to 3D**, multi-image (several views of one object): upload the four views, as front, left, right and back
   where Meshy asks which is which.
2. If Meshy offers these options, choose:
   - the newest model;
   - symmetry on;
   - an **A-pose** (or T-pose) for a character;
   - texture on;
   - a target of **about 15,000 triangles** (the game's budget for the kid).
3. Download it as **GLB**, with the texture inside. Save it as `ArtSource/models_meshy/characters/kid.glb`, or upload it
   here. It is then fitted to the game: 1.05 m tall, rigged for Unity's Humanoid, with the hand socket for the rooster.

## 1. Front · `kid_meshy_front.png`

Upload: `A0_kid_pattu_frock_sheet.png`

```text
Create a 1:1 square image.

Use the image I've uploaded: the kid's model sheet, for her face, skin tone, hair, hairband, frock, anklets, proportions and painted style. Match it exactly, and add the earrings, bangles and henna described below.

A full-length front view of the toddler hero from the model sheet, for building a 3D model: a South Indian girl of about three, with chubby toddler proportions (a big head about a quarter of her height, short arms and legs), warm brown skin, a round face with big dark eyes, a small red bindi and a gentle closed-mouth smile, and shoulder-length wavy black hair held back by a leopard-print hairband. She wears a knee-length peacock-blue silk pattu frock: a fitted bodice with a gold zari neckline with a short slit at the front, short puffed sleeves edged in gold, a blue sash at the waist, and a gathered, flared skirt with a wide magenta and gold border at the hem woven with small temple towers. Bare feet with silver anklets with tiny bells.

Her jewellery: small gold jhumka earrings, little bell-shaped gold drops hanging from her earlobes, her ears showing through her hair; and on each wrist a few thin gold bangles with red and green glass bangles between them, sitting loosely at the wrist. Fresh maruthani (henna) in a deep orange-red on her hands and legs: on each palm a large round dot ringed with small dots, every fingertip dyed, and a fine vine of leaves and dots over the backs of her hands and fingers up to the bangles; on her feet the toes and the edges of the soles dyed, and a vine of leaves and dots over the tops of her feet, round her ankles under the anklets and a little way up her shins. The same pattern on both hands and both legs.

She faces the viewer squarely and stands in a neutral A-pose for rigging: upright and symmetrical, her weight on both feet, her feet flat, toes forward and a hand's width apart; her arms straight and held out about 45 degrees from her sides, with clear space between her arms, her body and her skirt; her hands open and relaxed, fingers together, palms turned forward so the henna on them shows; her head level, looking straight ahead; her hair resting on her shoulders, clear of her arms and earrings. A calm, pleasant face with the mouth closed.

Show only her: one full-length figure, centred, from the top of her hair to the soles of her feet, filling about 85 percent of the image height, with clear space all round and nothing cropped. Draw her orthographic and straight on at her own chest height, with no perspective. Light her evenly and softly from the front, so her colours read true, with no cast shadows and no strong highlights. A plain, flat light-grey background, with no floor, no shadow on the ground, and no text, labels, frames or other objects.
```

## 2. Left side · `kid_meshy_left.png`

Upload: `A0_kid_pattu_frock_sheet.png`, `kid_meshy_front.png`

```text
Create a 1:1 square image.

Use the images I've uploaded: the kid's model sheet, for her face, hair, hairband, frock, anklets and painted style; and the front view, for her exact size, position in the frame, pose, colours, earrings, bangles and henna. Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from her left side: a true 90-degree profile, so we see her left side and she faces the left edge of the image. She stands in the same A-pose as in the front view, her arms held out from her sides at the same angle, palms forward, and her feet a hand's width apart, seen from the side. Show her profile clearly: the round cheek, the small nose and the closed-mouth smile, her ear with the gold jhumka earring hanging below it, the leopard-print hairband over the top of her head, her wavy hair falling to her shoulder at the back, the puffed sleeve with its gold edge, the gold and glass bangles on her wrist, the orange-red henna on her hand and fingers, the sash at the waist with the end of the bow at the back, the flared skirt with the magenta and gold temple-tower border running round it, and her bare feet with the silver anklets, the henna on the tops of her feet, round her ankles and up her shins, and the dyed edges of her soles.

Keep her the same size and in the same place as in the front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85 percent of the image height, with clear space all round and nothing cropped. Draw her orthographic and straight on at her own chest height, with no perspective. Light her evenly and softly, with no cast shadows and no strong highlights. A plain, flat light-grey background, with no floor, no shadow on the ground, and no text, labels, frames or other objects.
```

## 3. Right side · `kid_meshy_right.png`

Upload: `A0_kid_pattu_frock_sheet.png`, `kid_meshy_front.png`

```text
Create a 1:1 square image.

Use the images I've uploaded: the kid's model sheet, for her face, hair, hairband, frock, anklets and painted style; and the front view, for her exact size, position in the frame, pose, colours, earrings, bangles and henna. Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from her right side: a true 90-degree profile, so we see her right side and she faces the right edge of the image. She stands in the same A-pose as in the front view, her arms held out from her sides at the same angle, palms forward, and her feet a hand's width apart, seen from the side. Show her profile clearly: the round cheek, the small nose and the closed-mouth smile, her ear with the gold jhumka earring hanging below it, the leopard-print hairband over the top of her head, her wavy hair falling to her shoulder at the back, the puffed sleeve with its gold edge, the gold and glass bangles on her wrist, the orange-red henna on her hand and fingers, the sash at the waist with the end of the bow at the back, the flared skirt with the magenta and gold temple-tower border running round it, and her bare feet with the silver anklets, the henna on the tops of her feet, round her ankles and up her shins, and the dyed edges of her soles.

Keep her the same size and in the same place as in the front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85 percent of the image height, with clear space all round and nothing cropped. Draw her orthographic and straight on at her own chest height, with no perspective. Light her evenly and softly, with no cast shadows and no strong highlights. A plain, flat light-grey background, with no floor, no shadow on the ground, and no text, labels, frames or other objects.
```

## 4. Back · `kid_meshy_back.png`

Upload: `A0_kid_pattu_frock_sheet.png`, `kid_meshy_front.png`

```text
Create a 1:1 square image.

Use the images I've uploaded: the kid's model sheet, for her hair, hairband, frock, anklets and painted style; and the front view, for her exact size, position in the frame, pose, colours, earrings, bangles and henna. Match them exactly.

The same toddler in the same peacock-blue pattu frock, seen exactly from behind, so her face is hidden. She stands in the same A-pose as in the front view, mirrored as seen from the back: her arms straight and held out about 45 degrees from her sides, with clear space between her arms, her body and her skirt, her hands open with the palms forward, so we see the backs of her hands, and her feet flat and a hand's width apart. Show her back clearly: the back of her head with the shoulder-length wavy black hair, the gold jhumka earrings just showing below her hair on each side, the back of the leopard-print hairband, the plain back of the bodice with a fine seam down the middle, the puffed sleeves with their gold edges, the gold and glass bangles on both wrists, the orange-red henna vines on the backs of her hands and fingers, the blue sash tied in a neat bow at the back of the waist, the gathered skirt with the magenta and gold temple-tower border continuing all the way round, the backs of her lower legs with the henna round her ankles under the silver anklets, and her bare heels with the dyed edges of her soles.

Keep her the same size and in the same place as in the front view: the top of her head and the soles of her feet at the same heights, centred, filling about 85 percent of the image height, with clear space all round and nothing cropped. Draw her orthographic and straight on at her own chest height, with no perspective. Light her evenly and softly, with no cast shadows and no strong highlights. A plain, flat light-grey background, with no floor, no shadow on the ground, and no text, labels, frames or other objects.
```
