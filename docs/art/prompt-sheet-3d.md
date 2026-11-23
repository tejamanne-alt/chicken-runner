# Chicken Runner — 3D view prompts (for Meshy)

One image per asset: the asset drawn four times in a 2 by 2 grid (front, left side, right side, back), from its painting, for building its 3D model in Meshy. The web version has each painting to save and attach, copy buttons, a checklist, and a tool that cuts a finished sheet into the four views Meshy wants.

## How to use it

1. Attach the asset's painting (`<name>.jpg`; the web version saves it) and paste its prompt.
2. Save the image as `<name>_views.png`. Regenerate it if a view is missing, mirrored wrongly (the left side view faces left, the right side view faces right), cropped, or has labels or a coloured background.
3. Cut it into `<name>_front.png`, `<name>_left.png`, `<name>_right.png` and `<name>_back.png` (the web version does this) and give the four to Meshy's multi-image to 3D, each in its slot.
4. Download the model as GLB, named `<name>.glb`, and put it in `ArtSource/models_meshy/<folder>/` (or upload it in the chat). `finish_models.py` fits it into the game at the painting's size and place.

Prints, ruts, cracked mud and kolams need no model: they lie flat on the ground as painted.

## Characters and pickups

The kid and the rooster have their four views already; the pickups have no painting, so their prompts describe them.

### Mango · `mango`

Save as `mango_views.png` · Square 1:1 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/pickups/mango.glb`

Note: No painting of it yet: the prompt describes it.

```text
Square 1:1 image.

Model sheet for 3D modelling of a ripe mango, golden yellow blushing to red, with a short stalk and one green leaf, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a single small object on its own: show the whole of it from every side. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Chilli · `chilli`

Save as `chilli_views.png` · Square 1:1 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/pickups/chilli.glb`

Note: No painting of it yet: the prompt describes it.

```text
Square 1:1 image.

Model sheet for 3D modelling of a single bright red chilli with a green cap and a gently curled tip, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a single small object on its own: show the whole of it from every side. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Golden tail feather · `feather`

Save as `feather_views.png` · Square 1:1 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/pickups/feather.glb`

Note: No painting of it yet: the prompt describes it.

```text
Square 1:1 image.

Model sheet for 3D modelling of a single long, curved golden rooster tail feather with a glossy sheen, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a single small object on its own: show the whole of it from every side. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### The kid · `kid`

No new images: her four views exist already. Use them in Meshy as front, left, right and back. (You are providing her model yourself.)

Images: `A0_kid_pattu_frock_front.png`, `A0_kid_pattu_frock_left.png`, `A0_kid_pattu_frock_right.png`, `A0_kid_pattu_frock_back.png`

### The rooster · `rooster`

No new images: his four views exist already (B11 front, B13 left, B14 right, B12 back). Use them in Meshy.

Images: `B11_rooster_front.png`, `B13_rooster_left.png`, `B14_rooster_right.png`, `B12_rooster_back.png`

## The lane

Zone 1: houses, shops, the lane's props and obstacles.

### Bicycle · `bicycle`

Save as `bicycle_views.png` · Landscape 3:2 · Attach: bicycle.jpg (its painting) · Model: `ArtSource/models_meshy/lane/bicycle.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of an old black roadster bicycle with a rear carrier and a stand, drawn exactly like the attached painting (bicycle.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its left side (it faces left): that is the left side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it from its front end and the back view from behind; both side views show the same wheels and boards. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Brass pots · `brass_pots`

Save as `brass_pots_views.png` · Landscape 3:2 · Attach: brass_pots.jpg (its painting) · Model: `ArtSource/models_meshy/lane/brass_pots.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of two round brass water pots (kudam), one big and one small, on the ground, drawn exactly like the attached painting (brass_pots.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Bullock cart · `bullock_cart`

Save as `bullock_cart_views.png` · Landscape 3:2 · Attach: bullock_cart.jpg (its painting) · Model: `ArtSource/models_meshy/lane/bullock_cart.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a wooden bullock cart with two big spoked wheels, painted side boards, hay in its bed and its yoke pole resting on a prop, drawn exactly like the attached painting (bullock_cart.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it from its front end and the back view from behind; both side views show the same wheels and boards. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Cattle shed · `cattle_shed`

Save as `cattle_shed_views.png` · Landscape 3:2 · Attach: cattle_shed.jpg (its painting) · Model: `ArtSource/models_meshy/lane/cattle_shed.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of an open-fronted thatched cattle shed on wooden posts, its lime-washed back wall marked with handprints, a calf lying in the straw, drawn exactly like the attached painting (cattle_shed.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Its front is open between the posts. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Chicken basket · `chicken_basket`

Save as `chicken_basket_views.png` · Square 1:1 · Attach: chicken_basket.jpg (its painting) · Model: `ArtSource/models_meshy/lane/chicken_basket.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a dome-shaped woven cane coop basket for hens, drawn exactly like the attached painting (chicken_basket.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Clothesline · `clothesline`

Save as `clothesline_views.png` · Landscape 3:2 · Attach: clothesline.jpg (its painting) · Model: `ArtSource/models_meshy/lane/clothesline.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a rope clothesline between two bamboo posts, with a magenta and a yellow cloth hanging on it, drawn exactly like the attached painting (clothesline.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It is thin: the posts and the hanging cloths are its whole depth. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Doorway with a garland · `doorway_garland`

Save as `doorway_garland_views.png` · Square 1:1 · Attach: doorway_garland.jpg (its painting) · Model: `ArtSource/models_meshy/lane/doorway_garland.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a red-washed doorway with a carved wooden double door, a mango-leaf garland across the top and a kolam on the step, drawn exactly like the attached painting (doorway_garland.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. It is a short piece of house wall about 40 cm thick; from behind, the same doorway seen from inside, plainly plastered. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Cow-dung cake · `dung`

Save as `dung_views.png` · Landscape 3:2 · Attach: dung.jpg (its painting) · Model: `ArtSource/models_meshy/lane/dung.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a round, flat cow-dung cake drying on the ground, drawn exactly like the attached painting (dung.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Hand pump · `hand_pump`

Save as `hand_pump_views.png` · Square 1:1 · Attach: hand_pump.jpg (its painting) · Model: `ArtSource/models_meshy/lane/hand_pump.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a green cast-iron village hand pump on a stone base, with a steel bucket and a small puddle, drawn exactly like the attached painting (hand_pump.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### House being built · `house_being_built`

Save as `house_being_built_views.png` · Landscape 3:2 · Attach: house_being_built.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_being_built.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a mud-brick house being built: unfinished walls, a roof frame of bare wooden poles, piles of bricks and earth, drawn exactly like the attached painting (house_being_built.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Thatched house with a porch · `house_hut_porch`

Save as `house_hut_porch_views.png` · Landscape 3:2 · Attach: house_hut_porch.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_hut_porch.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a mud-walled house with a deep thatched porch on wooden posts, round dung cakes drying on its walls, drawn exactly like the attached painting (house_hut_porch.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Indigo house with a veranda · `house_indigo_veranda`

Save as `house_indigo_veranda_views.png` · Square 1:1 · Attach: house_indigo_veranda.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_indigo_veranda.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a narrow indigo-blue lime-washed house with a red-tiled veranda roof on turned wooden pillars, a carved door with a garland, a window and kolam steps, drawn exactly like the attached painting (house_indigo_veranda.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Lime-washed house · `house_limewash`

Save as `house_limewash_views.png` · Portrait 2:3 · Attach: house_limewash.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_limewash.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a narrow cream lime-washed flat-roofed house with a parapet, a teal-framed carved door with a garland, a bougainvillea vine and kolam steps, drawn exactly like the attached painting (house_limewash.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Mud house with a tin roof · `house_mud_tin`

Save as `house_mud_tin_views.png` · Square 1:1 · Attach: house_mud_tin.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_mud_tin.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a plain mud-plastered house with a corrugated tin roof held down by an old tyre, a blue wooden door and a propped window shutter, drawn exactly like the attached painting (house_mud_tin.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Pink house · `house_pink`

Save as `house_pink_views.png` · Portrait 2:3 · Attach: house_pink.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_pink.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a narrow pink lime-washed flat-roofed house with a parapet, a teal-framed carved door with a garland, a jasmine vine, a potted hibiscus and kolam steps, drawn exactly like the attached painting (house_pink.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Plank and tin house · `house_plank_sheet`

Save as `house_plank_sheet_views.png` · Landscape 3:2 · Attach: house_plank_sheet.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_plank_sheet.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a patched house of weathered planks and rusty tin sheets, with a sari curtain in the doorway and potted plants on the window sill, drawn exactly like the attached painting (house_plank_sheet.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Potter's house · `house_potter`

Save as `house_potter_views.png` · Landscape 3:2 · Attach: house_potter.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_potter.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a potter's mud house with a thatched roof running out over an open work shed with a potter's wheel, rows of clay pots drying in front, drawn exactly like the attached painting (house_potter.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Thatched hut with a pumpkin vine · `house_thatched_hut`

Save as `house_thatched_hut_views.png` · Square 1:1 · Attach: house_thatched_hut.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_thatched_hut.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a mud hut with a thick thatched roof covered in a pumpkin vine, a wooden door and a clay pot, drawn exactly like the attached painting (house_thatched_hut.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tiled house behind a wall · `house_tiled_gate`

Save as `house_tiled_gate_views.png` · Landscape 3:2 · Attach: house_tiled_gate.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_tiled_gate.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a lime-washed house with a red-tiled roof behind a compound wall with a wooden gate, and a tree inside the compound, drawn exactly like the attached painting (house_tiled_gate.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Turmeric house with a ladder · `house_turmeric_ladder`

Save as `house_turmeric_ladder_views.png` · Square 1:1 · Attach: house_turmeric_ladder.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_turmeric_ladder.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a narrow turmeric-yellow flat-roofed house with a parapet, a carved door with a garland, a barred window, a clay pot, kolam steps and a bamboo ladder leaning up to the roof, drawn exactly like the attached painting (house_turmeric_ladder.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Village head's house · `house_village_head`

Save as `house_village_head_views.png` · Landscape 3:2 · Attach: house_village_head.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_village_head.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a big two-storey house with red-tiled roofs, a long veranda on carved pillars and lime-washed walls with a maroon band, drawn exactly like the attached painting (house_village_head.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Weaver's house · `house_weaver`

Save as `house_weaver_views.png` · Landscape 3:2 · Attach: house_weaver.jpg (its painting) · Model: `ArtSource/models_meshy/lane/house_weaver.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a whitewashed house with a thatched roof and a loom window, a frame of coloured yarn drying beside it, drawn exactly like the attached painting (house_weaver.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Jute sacks · `jute_sacks`

Save as `jute_sacks_views.png` · Landscape 3:2 · Attach: jute_sacks.jpg (its painting) · Model: `ArtSource/models_meshy/lane/jute_sacks.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of three full jute sacks with purple stripes, two below and one on top, drawn exactly like the attached painting (jute_sacks.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Kolam 1 · `kolam_1`

No model needed: it lies flat and is painted on the ground as it is.

### Kolam 2 · `kolam_2`

No model needed: it lies flat and is painted on the ground as it is.

### Kolam 3 · `kolam_3`

No model needed: it lies flat and is painted on the ground as it is.

### Kolam 4 · `kolam_4`

No model needed: it lies flat and is painted on the ground as it is.

### Kolam 5 · `kolam_5`

No model needed: it lies flat and is painted on the ground as it is.

### Kolam 6 · `kolam_6`

No model needed: it lies flat and is painted on the ground as it is.

### Lamp pillar · `lamp_pillar`

Save as `lamp_pillar_views.png` · Portrait 2:3 · Attach: lamp_pillar.jpg (its painting) · Model: `ArtSource/models_meshy/lane/lamp_pillar.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a tall carved brass lamp pillar (deepa sthambam) with rows of little lamps, on a stepped stone base, drawn exactly like the attached painting (lamp_pillar.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Panchayat office · `panchayat_office`

Save as `panchayat_office_views.png` · Landscape 3:2 · Attach: panchayat_office.jpg (its painting) · Model: `ArtSource/models_meshy/lane/panchayat_office.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a plain cream single-storey village office with a flat roof, a door, two windows, a clock and a bench, a hand pump beside it, drawn exactly like the attached painting (panchayat_office.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Peepal tree on a platform · `peepal_platform`

Save as `peepal_platform_views.png` · Square 1:1 · Attach: peepal_platform.jpg (its painting) · Model: `ArtSource/models_meshy/lane/peepal_platform.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a big peepal tree growing out of a raised stone platform (katte) with steps, a sacred thread round its trunk, drawn exactly like the attached painting (peepal_platform.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Stack of clay pots · `pot_stack`

Save as `pot_stack_views.png` · Portrait 2:3 · Attach: pot_stack.jpg (its painting) · Model: `ArtSource/models_meshy/lane/pot_stack.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of three red clay pots of decreasing size stacked one on another, painted with white and yellow triangles, drawn exactly like the attached painting (pot_stack.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Rope cot · `rope_cot`

Save as `rope_cot_views.png` · Landscape 3:2 · Attach: rope_cot.jpg (its painting) · Model: `ArtSource/models_meshy/lane/rope_cot.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a wooden rope cot (charpai) with turned legs and a woven jute top, a striped pillow at one end, drawn exactly like the attached painting (rope_cot.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. From the ends it is about 85 cm deep. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Provisions shop · `shop_provisions`

Save as `shop_provisions_views.png` · Square 1:1 · Attach: shop_provisions.jpg (its painting) · Model: `ArtSource/models_meshy/lane/shop_provisions.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small mud-walled provisions shop with a tin awning, shelves of glass jars and hanging bananas, and a signboard with no words, drawn exactly like the attached painting (shop_provisions.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tailor and cycle shop · `shop_tailor_cycle`

Save as `shop_tailor_cycle_views.png` · Square 1:1 · Attach: shop_tailor_cycle.jpg (its painting) · Model: `ArtSource/models_meshy/lane/shop_tailor_cycle.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small wooden shop under a tin awning: shelves of cloth and a sewing machine on one side, bicycle tyres hanging on the other, drawn exactly like the attached painting (shop_tailor_cycle.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tea stall · `shop_tea_stall`

Save as `shop_tea_stall_views.png` · Square 1:1 · Attach: shop_tea_stall.jpg (its painting) · Model: `ArtSource/models_meshy/lane/shop_tea_stall.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small dark-wood tea stall under a palm-thatch roof on poles, with a brass kettle on a clay stove, glasses, a jar of biscuits, a radio and a newspaper on a bench, drawn exactly like the attached painting (shop_tea_stall.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Stone shrine · `shrine_stone`

Save as `shrine_stone_views.png` · Square 1:1 · Attach: shrine_stone.jpg (its painting) · Model: `ArtSource/models_meshy/lane/shrine_stone.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of an upright dark stone with painted marks, a marigold garland and a small oil lamp, on a stone base, drawn exactly like the attached painting (shrine_stone.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tree shrine · `shrine_tree`

Save as `shrine_tree_views.png` · Square 1:1 · Attach: shrine_tree.jpg (its painting) · Model: `ArtSource/models_meshy/lane/shrine_tree.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small whitewashed shrine at the foot of a big spreading tree, drawn exactly like the attached painting (shrine_tree.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Mango tree · `tree_mango_1`

Save as `tree_mango_1_views.png` · Square 1:1 · Attach: tree_mango_1.jpg (its painting) · Model: `ArtSource/models_meshy/lane/tree_mango_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a mango tree with a twisted trunk, a dense rounded crown and ripe mangoes, drawn exactly like the attached painting (tree_mango_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Mango tree (2) · `tree_mango_2`

Save as `tree_mango_2_views.png` · Square 1:1 · Attach: tree_mango_2.jpg (its painting) · Model: `ArtSource/models_meshy/lane/tree_mango_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a mango tree with a twisted trunk, a dense rounded crown and ripe mangoes, drawn exactly like the attached painting (tree_mango_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tulsi planter · `tulsi_planter`

Save as `tulsi_planter_views.png` · Portrait 2:3 · Attach: tulsi_planter.jpg (its painting) · Model: `ArtSource/models_meshy/lane/tulsi_planter.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a square painted tulsi planter (brindavan) with a red flower motif and a holy basil plant on top, drawn exactly like the attached painting (tulsi_planter.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It is square, the same painted motif on all four sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Water pot on a stand · `water_pot_stand`

Save as `water_pot_stand_views.png` · Square 1:1 · Attach: water_pot_stand.jpg (its painting) · Model: `ArtSource/models_meshy/lane/water_pot_stand.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a big red clay water pot with a brass tap, on a stone stand of two upright slabs and a top slab, drawn exactly like the attached painting (water_pot_stand.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## The fields

Zone 2: field buildings, crops, the canal and field life.

### Field bund block · `bund_block`

Save as `bund_block_views.png` · Landscape 3:2 · Attach: bund_block.jpg (its painting) · Model: `ArtSource/models_meshy/fields/bund_block.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a short block of raised earth bund between paddy fields: red earth with grass and small yellow flowers along its top, drawn exactly like the attached painting (bund_block.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It is a straight earth bank about 0.9 m deep, the same from the front and back, sloping down at both ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Field bund strip · `bund_strip`

Save as `bund_strip_views.png` · Landscape 3:2 · Attach: bund_strip.jpg (its painting) · Model: `ArtSource/models_meshy/fields/bund_strip.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long, low strip of earth bund with a grassy top, drawn exactly like the attached painting (bund_strip.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It is a straight earth bank about 0.9 m deep, the same from the front and back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Canal bank · `canal_bank`

Save as `canal_bank_views.png` · Landscape 3:2 · Attach: canal_bank.jpg (its painting) · Model: `ArtSource/models_meshy/fields/canal_bank.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a short stretch of irrigation canal: earth banks sloping down to shallow water with reeds, drawn exactly like the attached painting (canal_bank.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. From the sides, both banks slope down to the water channel between them. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Canal bridge · `canal_bridge`

Save as `canal_bridge_views.png` · Landscape 3:2 · Attach: canal_bridge.jpg (its painting) · Model: `ArtSource/models_meshy/fields/canal_bridge.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a small bridge of stone slabs across a narrow stone-lined canal, with plants growing at its corners, drawn exactly like the attached painting (canal_bridge.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Seedbed strip · `crop_strip_1`

Save as `crop_strip_1_views.png` · Landscape 3:2 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/fields/crop_strip_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long strip of paddy seedbed: dense bright-green rice seedlings a hand high in wet earth, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Stubble strip · `crop_strip_2`

Save as `crop_strip_2_views.png` · Landscape 3:2 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/fields/crop_strip_2.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long strip of harvested field: short golden stubble in rows on dry earth, with a few small hay bundles, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sorghum strip · `crop_strip_3`

Save as `crop_strip_3_views.png` · Landscape 3:2 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/fields/crop_strip_3.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long strip of tall sorghum (jowar) plants with heavy reddish-brown grain heads, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Groundnut strip · `crop_strip_4`

Save as `crop_strip_4_views.png` · Landscape 3:2 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/fields/crop_strip_4.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long strip of low, bushy green groundnut plants in red earth, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Cotton strip · `crop_strip_5`

Save as `crop_strip_5_views.png` · Landscape 3:2 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/fields/crop_strip_5.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long strip of cotton plants with open white bolls, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Banana strip · `crop_strip_6`

Save as `crop_strip_6_views.png` · Landscape 3:2 · Attach: A1_key_art.png · Model: `ArtSource/models_meshy/fields/crop_strip_6.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long row of young banana plants with broad green leaves, in the style of the attached A1 key art. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Well with a bullock water lift · `field_bldg_1`

Save as `field_bldg_1_views.png` · Landscape 3:2 · Attach: field_bldg_1.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_bldg_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a stone-lined well with a wooden frame and a leather bucket on a rope pulled by two white bullocks walking down a sloping earth ramp, clay pots beside the well, drawn exactly like the attached painting (field_bldg_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Watch hut on stilts · `field_bldg_2`

Save as `field_bldg_2_views.png` · Square 1:1 · Attach: field_bldg_2.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_bldg_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a thatched field watch hut (machan) on tall bamboo stilts, with a bamboo ladder, drawn exactly like the attached painting (field_bldg_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Farm shed with a haystack · `field_bldg_3`

Save as `field_bldg_3_views.png` · Landscape 3:2 · Attach: field_bldg_3.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_bldg_3.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a small open thatched farm shed beside a haystack, with a grinding stone and farm tools, drawn exactly like the attached painting (field_bldg_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Farmer ploughing · `field_life_1`

Save as `field_life_1_views.png` · Landscape 3:2 · Attach: field_life_1.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_life_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a farmer in a white vest and dhoti guiding a wooden plough pulled by two white bullocks through muddy earth, drawn exactly like the attached painting (field_life_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Women transplanting paddy · `field_life_2`

Save as `field_life_2_views.png` · Landscape 3:2 · Attach: field_life_2.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_life_2.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of three women in saris bent over, planting rice seedlings in a muddy paddy patch, drawn exactly like the attached painting (field_life_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Boy herding goats · `field_life_3`

Save as `field_life_3_views.png` · Landscape 3:2 · Attach: field_life_3.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_life_3.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a boy with a long stick herding four goats, drawn exactly like the attached painting (field_life_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Buffalo with an egret · `field_life_4`

Save as `field_life_4_views.png` · Landscape 3:2 · Attach: field_life_4.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_life_4.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a black water buffalo lying in mud with a white egret standing on its back, drawn exactly like the attached painting (field_life_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Old man herding ducks · `field_life_5`

Save as `field_life_5_views.png` · Landscape 3:2 · Attach: field_life_5.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_life_5.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of an old man in white with a long bamboo stick herding a line of white ducks, drawn exactly like the attached painting (field_life_5.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Man carrying a paddy sheaf · `field_life_6`

Save as `field_life_6_views.png` · Portrait 2:3 · Attach: field_life_6.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_life_6.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a man in a vest and lungi carrying a big sheaf of harvested paddy on his head, drawn exactly like the attached painting (field_life_6.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Field shrine · `field_shrine`

Save as `field_shrine_views.png` · Portrait 2:3 · Attach: field_shrine.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_shrine.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a small whitewashed roadside shrine with a deity in a niche and a saffron flag on top, drawn exactly like the attached painting (field_shrine.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Banyan tree · `field_tree_1`

Save as `field_tree_1_views.png` · Square 1:1 · Attach: field_tree_1.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_tree_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a big banyan tree with hanging aerial roots, drawn exactly like the attached painting (field_tree_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Gnarled field tree · `field_tree_2`

Save as `field_tree_2_views.png` · Square 1:1 · Attach: field_tree_2.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_tree_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a gnarled, twisted tree with sparse feathery leaves, drawn exactly like the attached painting (field_tree_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Bamboo clump · `field_tree_3`

Save as `field_tree_3_views.png` · Portrait 2:3 · Attach: field_tree_3.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_tree_3.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a clump of tall green bamboo, drawn exactly like the attached painting (field_tree_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Screw pine bush · `field_tree_4`

Save as `field_tree_4_views.png` · Square 1:1 · Attach: field_tree_4.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_tree_4.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a big screw pine bush of long, spiky, sword-shaped leaves, drawn exactly like the attached painting (field_tree_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Casuarina trees · `field_tree_5`

Save as `field_tree_5_views.png` · Portrait 2:3 · Attach: field_tree_5.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_tree_5.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a few slender casuarina trees with feathery needles, drawn exactly like the attached painting (field_tree_5.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Cactus and agave · `field_tree_6`

Save as `field_tree_6_views.png` · Landscape 3:2 · Attach: field_tree_6.jpg (its painting) · Model: `ArtSource/models_meshy/fields/field_tree_6.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a dry patch of red earth with an agave, a prickly-pear cactus and small succulents, drawn exactly like the attached painting (field_tree_6.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Granary on stone legs · `granary`

Save as `granary_views.png` · Square 1:1 · Attach: granary.jpg (its painting) · Model: `ArtSource/models_meshy/fields/granary.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small square granary with a red-tiled hipped roof, standing on stone legs, drawn exactly like the attached painting (granary.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Haystack · `haystack`

Save as `haystack_views.png` · Square 1:1 · Attach: haystack.jpg (its painting) · Model: `ArtSource/models_meshy/fields/haystack.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a tall round haystack of golden straw, tied at the top, drawn exactly like the attached painting (haystack.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Small haystack · `haystack_small`

Save as `haystack_small_views.png` · Square 1:1 · Attach: haystack_small.jpg (its painting) · Model: `ArtSource/models_meshy/fields/haystack_small.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a smaller round haystack with a pole sticking out of its top, drawn exactly like the attached painting (haystack_small.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Hut with a goat pen · `hut_with_pen`

Save as `hut_with_pen_views.png` · Landscape 3:2 · Attach: hut_with_pen.jpg (its painting) · Model: `ArtSource/models_meshy/fields/hut_with_pen.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a small thatched mud hut with a bamboo pen fence beside it, drawn exactly like the attached painting (hut_with_pen.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Ripe paddy row · `paddy_ripe`

Save as `paddy_ripe_views.png` · Landscape 3:2 · Attach: paddy_ripe.jpg (its painting) · Model: `ArtSource/models_meshy/fields/paddy_ripe.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long row of ripe golden paddy, the heads drooping, drawn exactly like the attached painting (paddy_ripe.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Green paddy row · `paddy_tall`

Save as `paddy_tall_views.png` · Landscape 3:2 · Attach: paddy_tall.jpg (its painting) · Model: `ArtSource/models_meshy/fields/paddy_tall.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long row of tall green paddy, drawn exactly like the attached painting (paddy_tall.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Young paddy in water · `paddy_young`

Save as `paddy_young_views.png` · Landscape 3:2 · Attach: paddy_young.jpg (its painting) · Model: `ArtSource/models_meshy/fields/paddy_young.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long strip of young paddy plants standing in shallow water, drawn exactly like the attached painting (paddy_young.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Palmyra palm · `palmyra_1`

Save as `palmyra_1_views.png` · Portrait 2:3 · Attach: palmyra_1.jpg (its painting) · Model: `ArtSource/models_meshy/fields/palmyra_1.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a tall palmyra palm with a fan of stiff leaves on a straight dark trunk, drawn exactly like the attached painting (palmyra_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Palmyra palm (2) · `palmyra_2`

Save as `palmyra_2_views.png` · Portrait 2:3 · Attach: palmyra_2.jpg (its painting) · Model: `ArtSource/models_meshy/fields/palmyra_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a tall palmyra palm with a fan of stiff leaves on a straight dark trunk, drawn exactly like the attached painting (palmyra_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Palmyra palm (3) · `palmyra_3`

Save as `palmyra_3_views.png` · Portrait 2:3 · Attach: palmyra_3.jpg (its painting) · Model: `ArtSource/models_meshy/fields/palmyra_3.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a tall palmyra palm with a fan of stiff leaves on a straight dark trunk, drawn exactly like the attached painting (palmyra_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Pump house · `pump_house`

Save as `pump_house_views.png` · Square 1:1 · Attach: pump_house.jpg (its painting) · Model: `ArtSource/models_meshy/fields/pump_house.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small brick pump house with a wooden door and a pipe pouring water into a channel, drawn exactly like the attached painting (pump_house.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Scarecrow · `scarecrow`

Save as `scarecrow_views.png` · Square 1:1 · Attach: scarecrow.jpg (its painting) · Model: `ArtSource/models_meshy/fields/scarecrow.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a scarecrow with a painted clay-pot head, a white shirt, a red scarf and straw hands on a wooden pole, drawn exactly like the attached painting (scarecrow.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sluice gate · `sluice_gate`

Save as `sluice_gate_views.png` · Square 1:1 · Attach: sluice_gate.jpg (its painting) · Model: `ArtSource/models_meshy/fields/sluice_gate.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a wooden canal sluice gate with an iron screw wheel between two stone pillars, water below, drawn exactly like the attached painting (sluice_gate.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sugarcane row · `sugarcane`

Save as `sugarcane_views.png` · Landscape 3:2 · Attach: sugarcane.jpg (its painting) · Model: `ArtSource/models_meshy/fields/sugarcane.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long row of tall sugarcane, drawn exactly like the attached painting (sugarcane.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole length, the side views its narrow ends. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Village well · `well`

Save as `well_views.png` · Square 1:1 · Attach: well.jpg (its painting) · Model: `ArtSource/models_meshy/fields/well.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a round stone-built well with a wooden crossbeam, a pulley, a coiled rope and a small bucket, drawn exactly like the attached painting (well.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## The market

Zone 3: stalls, terrace houses, temple pieces and market props.

### Water tank · `black_tank`

Save as `black_tank_views.png` · Square 1:1 · Attach: black_tank.jpg (its painting) · Model: `ArtSource/models_meshy/market/black_tank.glb`

Note: Your style rules rule out black plastic tanks: make it a plastered terracotta tank, keeping its shape and stand.

```text
Square 1:1 image.

Model sheet for 3D modelling of a big round water storage tank on a stone stand, drawn exactly like the attached painting (black_tank.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Your style rules rule out black plastic tanks: make it a plastered terracotta tank, keeping its shape and stand. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Brass vessels · `brass_vessels`

Save as `brass_vessels_views.png` · Square 1:1 · Attach: brass_vessels.jpg (its painting) · Model: `ArtSource/models_meshy/market/brass_vessels.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a group of shiny brass pots and containers of different sizes, drawn exactly like the attached painting (brass_vessels.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Bunting · `bunting`

Save as `bunting_views.png` · Landscape 3:2 · Attach: bunting.jpg (its painting) · Model: `ArtSource/models_meshy/market/bunting.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a string of colourful triangular cloth flags, drawn exactly like the attached painting (bunting.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It is a thin string of flags: from the sides, just the string and the flags edge-on. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Chariot shed · `chariot_shed`

Save as `chariot_shed_views.png` · Landscape 3:2 · Attach: chariot_shed.jpg (its painting) · Model: `ArtSource/models_meshy/market/chariot_shed.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a tall wooden shed with a sloping roof sheltering a carved wooden temple chariot, its front open, drawn exactly like the attached painting (chariot_shed.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Chilli mat · `chilli_mat`

Save as `chilli_mat_views.png` · Landscape 3:2 · Attach: chilli_mat.jpg (its painting) · Model: `ArtSource/models_meshy/market/chilli_mat.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a woven palm-leaf mat with red chillies spread out to dry, drawn exactly like the attached painting (chilli_mat.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It lies nearly flat on the ground. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Coconut cart · `coconut_cart`

Save as `coconut_cart_views.png` · Landscape 3:2 · Attach: coconut_cart.jpg (its painting) · Model: `ArtSource/models_meshy/market/coconut_cart.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a wooden cart heaped with green coconuts, pulled by two white bullocks, drawn exactly like the attached painting (coconut_cart.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it from its front end and the back view from behind; both side views show the same wheels and boards. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Flower stall · `flower_stall`

Save as `flower_stall_views.png` · Square 1:1 · Attach: flower_stall.jpg (its painting) · Model: `ArtSource/models_meshy/market/flower_stall.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small bamboo flower stall hung with marigold, jasmine and rose garlands, baskets of loose flowers on its counter, drawn exactly like the attached painting (flower_stall.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Hens in a basket · `hens_basket`

Save as `hens_basket_views.png` · Square 1:1 · Attach: hens_basket.jpg (its painting) · Model: `ArtSource/models_meshy/market/hens_basket.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of two hens sitting in a shallow woven basket of straw, drawn exactly like the attached painting (hens_basket.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Kite · `kite`

Save as `kite_views.png` · Portrait 2:3 · Attach: kite.jpg (its painting) · Model: `ArtSource/models_meshy/market/kite.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a pink-and-yellow paper kite with a ribboned tail, drawn exactly like the attached painting (kite.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It is a flat paper kite: from the sides, edge-on. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Lamp steps · `lamp_step`

Save as `lamp_step_views.png` · Square 1:1 · Attach: lamp_step.jpg (its painting) · Model: `ArtSource/models_meshy/market/lamp_step.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of temple steps of carved yellow stone with a pillar, and lit clay oil lamps on each step, drawn exactly like the attached painting (lamp_step.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Lantern · `lantern`

Save as `lantern_views.png` · Portrait 2:3 · Attach: lantern.jpg (its painting) · Model: `ArtSource/models_meshy/market/lantern.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a hurricane lantern with a glowing wick, drawn exactly like the attached painting (lantern.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Mandapam · `mandapam`

Save as `mandapam_views.png` · Landscape 3:2 · Attach: mandapam.jpg (its painting) · Model: `ArtSource/models_meshy/market/mandapam.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long, low stone temple pavilion (mandapam) with a row of carved pillars under a flat stone roof, drawn exactly like the attached painting (mandapam.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Papad mat · `papad_mat`

Save as `papad_mat_views.png` · Landscape 3:2 · Attach: papad_mat.jpg (its painting) · Model: `ArtSource/models_meshy/market/papad_mat.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a woven palm-leaf mat with round papads drying on it, drawn exactly like the attached painting (papad_mat.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It lies nearly flat on the ground. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Roof parapet · `parapet_gap`

Save as `parapet_gap_views.png` · Landscape 3:2 · Attach: parapet_gap.jpg (its painting) · Model: `ArtSource/models_meshy/market/parapet_gap.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a section of lime-washed roof parapet wall with a dip in the middle and a painted red-and-white border, drawn exactly like the attached painting (parapet_gap.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. It is a thin wall, about 30 cm thick, plain on its back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### House with a terrace stair · `roof_house_a_1`

Save as `roof_house_a_1_views.png` · Landscape 3:2 · Attach: roof_house_a_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/roof_house_a_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a lime-washed house with a red-tiled roof and an outside stair up to a flat terrace with drying pots and dung cakes, drawn exactly like the attached painting (roof_house_a_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Mud house with a roof garden · `roof_house_a_2`

Save as `roof_house_a_2_views.png` · Landscape 3:2 · Attach: roof_house_a_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/roof_house_a_2.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a mud house with a flat roof overgrown with a vine, and a small thatched lean-to, drawn exactly like the attached painting (roof_house_a_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Blue terrace house · `roof_house_b_1`

Save as `roof_house_b_1_views.png` · Landscape 3:2 · Attach: roof_house_b_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/roof_house_b_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a pale-blue house with a red-tiled veranda roof, green shutters, a flat terrace with chillies and papads drying, and a ladder, drawn exactly like the attached painting (roof_house_b_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Old house with a roof hut · `roof_house_b_2`

Save as `roof_house_b_2_views.png` · Landscape 3:2 · Attach: roof_house_b_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/roof_house_b_2.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of an old cracked-plaster house with a small thatched hut and firewood on its roof, drawn exactly like the attached painting (roof_house_b_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Spice stall · `stall_c_1`

Save as `stall_c_1_views.png` · Landscape 3:2 · Attach: stall_c_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_c_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a spice stall under a faded yellow cotton shade on bamboo poles: open jute sacks of red chillies, turmeric and grains, drawn exactly like the attached painting (stall_c_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Vegetable seller under an umbrella · `stall_c_2`

Save as `stall_c_2_views.png` · Square 1:1 · Attach: stall_c_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_c_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of an old woman in a white sari selling vegetables under a palm-leaf umbrella, with baskets of cabbages, greens and potatoes and a hand grinder, drawn exactly like the attached painting (stall_c_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Cloth stall · `stall_c_3`

Save as `stall_c_3_views.png` · Landscape 3:2 · Attach: stall_c_3.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_c_3.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a cloth stall under a thatched shade: folded saris and cloth stacked on a low cot, more hanging from the front beam, drawn exactly like the attached painting (stall_c_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Coconut and gourd stall · `stall_d_1`

Save as `stall_d_1_views.png` · Landscape 3:2 · Attach: stall_d_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_d_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a coconut and gourd stall under a coconut-frond shade, bunches hanging from the poles and more heaped on the ground, drawn exactly like the attached painting (stall_d_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Pot stall · `stall_d_2`

Save as `stall_d_2_views.png` · Square 1:1 · Attach: stall_d_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_d_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a pot stall under a faded indigo cotton shade on bamboo poles: clay pots and jaggery blocks on a low bench, drawn exactly like the attached painting (stall_d_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Basket stall · `stall_d_3`

Save as `stall_d_3_views.png` · Landscape 3:2 · Attach: stall_d_3.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_d_3.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a basket stall under a thatched shade, stacked with woven cane baskets and winnowing trays, drawn exactly like the attached painting (stall_d_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Vegetable stall · `stall_e_1`

Save as `stall_e_1_views.png` · Landscape 3:2 · Attach: stall_e_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_e_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a vegetable stall under a faded madder-red cotton shade: tomatoes, aubergines, greens and bananas laid out on the ground, drawn exactly like the attached painting (stall_e_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Snack fryer's stall · `stall_e_2`

Save as `stall_e_2_views.png` · Square 1:1 · Attach: stall_e_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_e_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a snack stall under a woven palm-leaf shade: a man frying in a big iron kadai over a clay stove, drawn exactly like the attached painting (stall_e_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Parrot fortune teller · `stall_e_3`

Save as `stall_e_3_views.png` · Square 1:1 · Attach: stall_e_3.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_e_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a fortune teller sitting cross-legged under a big black cloth umbrella, with a caged parrot and cards spread on a mat, drawn exactly like the attached painting (stall_e_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sweets counter · `stall_f_1`

Save as `stall_f_1_views.png` · Square 1:1 · Attach: stall_f_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_f_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a sweets stall under an undyed cotton shade: a woman behind a wooden counter with glass jars of sweets, drawn exactly like the attached painting (stall_f_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sweets shelves · `stall_f_2`

Save as `stall_f_2_views.png` · Square 1:1 · Attach: stall_f_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_f_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a sweets stall under an undyed cotton shade: trays of jalebis and laddus on tiered shelves behind a wooden counter, drawn exactly like the attached painting (stall_f_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sugarcane juice stall · `stall_f_3`

Save as `stall_f_3_views.png` · Square 1:1 · Attach: stall_f_3.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_f_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a sugarcane juice stall: a man feeding cane into an iron roller press on a wooden table under a palm-leaf shade, glasses of juice, drawn exactly like the attached painting (stall_f_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Broom and mat seller · `stall_f_4`

Save as `stall_f_4_views.png` · Square 1:1 · Attach: stall_f_4.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_f_4.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a broom and mat seller sitting under a thatched shade among rolled palm mats, brooms and coils of rope, drawn exactly like the attached painting (stall_f_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Flower seller · `stall_flowers`

Save as `stall_flowers_views.png` · Square 1:1 · Attach: stall_flowers.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_flowers.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a flower seller woman sitting under a woven palm-leaf shade, garlands hanging and baskets of flowers around her, drawn exactly like the attached painting (stall_flowers.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Dried fish stall · `stall_g_1`

Save as `stall_g_1_views.png` · Landscape 3:2 · Attach: stall_g_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_g_1.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a dried-fish stall under a thatched shade: baskets and rows of dried fish on a mat, drawn exactly like the attached painting (stall_g_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Bangle stall · `stall_g_2`

Save as `stall_g_2_views.png` · Square 1:1 · Attach: stall_g_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_g_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a bangle stall under a faded indigo cotton shade: racks of coloured glass bangles, a mirror and bowls of kumkum powder, drawn exactly like the attached painting (stall_g_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Banana stall · `stall_g_3`

Save as `stall_g_3_views.png` · Landscape 3:2 · Attach: stall_g_3.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_g_3.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a banana stall under a woven palm-leaf shade, bunches of green and yellow bananas hanging from it, drawn exactly like the attached painting (stall_g_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Cobbler · `stall_h_1`

Save as `stall_h_1_views.png` · Square 1:1 · Attach: stall_h_1.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_h_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a cobbler sitting cross-legged under a big black cloth umbrella, sandals and tools spread on a mat, drawn exactly like the attached painting (stall_h_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Barber's pitch · `stall_h_2`

Save as `stall_h_2_views.png` · Square 1:1 · Attach: stall_h_2.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_h_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a barber's pitch under a woven palm-leaf shade on bamboo poles: a wooden stool, a mirror hung on a pole and a brass bowl, drawn exactly like the attached painting (stall_h_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Knife grinder · `stall_h_3`

Save as `stall_h_3_views.png` · Square 1:1 · Attach: stall_h_3.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_h_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a knife grinder's pitch under a coconut-frond shade: a treadle grinding wheel and knives laid out on a mat, drawn exactly like the attached painting (stall_h_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tall grain stall · `stall_high`

Save as `stall_high_views.png` · Square 1:1 · Attach: stall_high.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_high.glb`

Note: Your style rules rule out striped awnings: make its shade plain faded madder-red cotton, keeping its shape.

```text
Square 1:1 image.

Model sheet for 3D modelling of a tall bamboo stall with a counter of grain sacks and bowls of spice powders over a woven cloth, drawn exactly like the attached painting (stall_high.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Your style rules rule out striped awnings: make its shade plain faded madder-red cotton, keeping its shape. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Low leaf stall · `stall_low`

Save as `stall_low_views.png` · Square 1:1 · Attach: stall_low.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_low.glb`

Note: Your style rules rule out striped awnings: make its shade plain faded turmeric cotton, keeping its shape.

```text
Square 1:1 image.

Model sheet for 3D modelling of a low bamboo stall with green banana leaves and a basket of coconuts on its counter, drawn exactly like the attached painting (stall_low.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Your style rules rule out striped awnings: make its shade plain faded turmeric cotton, keeping its shape. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Potter's pitch · `stall_potter`

Save as `stall_potter_views.png` · Landscape 3:2 · Attach: stall_potter.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_potter.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a potter sitting among clay pots and figurines under a big black umbrella and a woven palm-leaf shade, drawn exactly like the attached painting (stall_potter.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sweet maker · `stall_sweets`

Save as `stall_sweets_views.png` · Landscape 3:2 · Attach: stall_sweets.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_sweets.glb`

Note: Your style rules rule out striped awnings: make its shade plain undyed cotton, keeping its shape.

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a sweet maker frying in a big iron kadai over a fire, plates of sweets around him, drawn exactly like the attached painting (stall_sweets.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Your style rules rule out striped awnings: make its shade plain undyed cotton, keeping its shape. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Vegetable heap stall · `stall_veg`

Save as `stall_veg_views.png` · Landscape 3:2 · Attach: stall_veg.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_veg.glb`

Note: Your style rules rule out striped awnings: make its shade plain faded indigo cotton, keeping its shape.

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a vegetable stall heaped with tomatoes, aubergines, chillies and greens in baskets, drawn exactly like the attached painting (stall_veg.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Your style rules rule out striped awnings: make its shade plain faded indigo cotton, keeping its shape. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Vessel stall · `stall_vessels`

Save as `stall_vessels_views.png` · Landscape 3:2 · Attach: stall_vessels.jpg (its painting) · Model: `ArtSource/models_meshy/market/stall_vessels.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a brass and copper vessel stall under a thatched shade: rows of shiny pots, lamps and tumblers, drawn exactly like the attached painting (stall_vessels.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods and of the seller, if there is one, under the same shade. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Temple tank wall · `tank_wall`

Save as `tank_wall_views.png` · Landscape 3:2 · Attach: tank_wall.jpg (its painting) · Model: `ArtSource/models_meshy/market/tank_wall.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a long, low stone wall of a temple tank with steps leading down and a small gateway in the middle, drawn exactly like the attached painting (tank_wall.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same building continued: the same walls, plinth, colours and roof all the way round, a plain back wall with a small window, and the roof's shape seen from the sides. It is a wall about 50 cm thick. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Vegetable basket · `veg_basket`

Save as `veg_basket_views.png` · Square 1:1 · Attach: veg_basket.jpg (its painting) · Model: `ArtSource/models_meshy/market/veg_basket.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a woven cane basket heaped with aubergines, tomatoes and greens, drawn exactly like the attached painting (veg_basket.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is round, so its four views are much alike; keep every painted detail where it belongs as it turns. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## Animals

Every animal that stands or sits about in the three zones.

### Buffalo in the mud · `buffalo_mud`

Save as `buffalo_mud_views.png` · Landscape 3:2 · Attach: buffalo_mud.jpg (its painting) · Model: `ArtSource/models_meshy/animals/buffalo_mud.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a dark water buffalo lying in a patch of wet mud, with curved horns, a rope halter and a bell, drawn exactly like the attached painting (buffalo_mud.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Show the patch of mud around it in every view. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Pair of bullocks · `bullocks`

Save as `bullocks_views.png` · Landscape 3:2 · Attach: bullocks.jpg (its painting) · Model: `ArtSource/models_meshy/animals/bullocks.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a pair of white bullocks standing side by side in step, with painted horns, striped cloth blankets on their backs and bells, drawn exactly like the attached painting (bullocks.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. There are exactly two bullocks, side by side: in the side views the nearer one hides most of the other, and in the front and back views both are seen side by side. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Calf · `calf`

Save as `calf_views.png` · Square 1:1 · Attach: calf.jpg (its painting) · Model: `ArtSource/models_meshy/animals/calf.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a young brown calf standing, drawn exactly like the attached painting (calf.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Cat asleep on a wall · `cat_on_wall`

Save as `cat_on_wall_views.png` · Landscape 3:2 · Attach: cat_on_wall.jpg (its painting) · Model: `ArtSource/models_meshy/animals/cat_on_wall.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a tabby cat curled up asleep on top of a short broken brick wall, drawn exactly like the attached painting (cat_on_wall.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. The wall is thin, about 25 cm deep, with plain old brickwork on its back face; the cat lies along its top. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### White cow · `cow`

Save as `cow_views.png` · Square 1:1 · Attach: cow.jpg (its painting) · Model: `ArtSource/models_meshy/animals/cow.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a white humped village cow with red-and-white painted horns, a rope halter and a brass bell, drawn exactly like the attached painting (cow.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Crows on a ledge · `crows_on_ledge`

Save as `crows_on_ledge_views.png` · Landscape 3:2 · Attach: crows_on_ledge.jpg (its painting) · Model: `ArtSource/models_meshy/animals/crows_on_ledge.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of three house crows perched in a row on a short weathered wooden ledge, drawn exactly like the attached painting (crows_on_ledge.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. The ledge is a plain plank on two brackets, about as deep as a crow; the crows all face the same way in every view. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Barking dog · `dog_barking`

Save as `dog_barking_views.png` · Square 1:1 · Attach: dog_barking.jpg (its painting) · Model: `ArtSource/models_meshy/animals/dog_barking.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a ginger-and-white village dog standing and barking, with a curled tail, drawn exactly like the attached painting (dog_barking.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sleeping dog · `dog_sleeping`

Save as `dog_sleeping_views.png` · Landscape 3:2 · Attach: dog_sleeping.jpg (its painting) · Model: `ArtSource/models_meshy/animals/dog_sleeping.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a ginger-and-white village dog curled up asleep, chin on its paws, drawn exactly like the attached painting (dog_sleeping.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### White duck · `duck_1`

Save as `duck_1_views.png` · Portrait 2:3 · Attach: duck_1.jpg (its painting) · Model: `ArtSource/models_meshy/animals/duck_1.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a white duck standing upright, drawn exactly like the attached painting (duck_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### White duck, facing left · `duck_2`

Save as `duck_2_views.png` · Portrait 2:3 · Attach: duck_2.jpg (its painting) · Model: `ArtSource/models_meshy/animals/duck_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a white duck standing upright, drawn exactly like the attached painting (duck_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its left side (it faces left): that is the left side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Goat eating leaves · `goat_eating`

Save as `goat_eating_views.png` · Square 1:1 · Attach: goat_eating.jpg (its painting) · Model: `ArtSource/models_meshy/animals/goat_eating.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a black-and-white goat standing and chewing a leafy twig, drawn exactly like the attached painting (goat_eating.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Goat kid leaping · `goat_kid`

Save as `goat_kid_views.png` · Square 1:1 · Attach: goat_kid.jpg (its painting) · Model: `ArtSource/models_meshy/animals/goat_kid.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small black goat kid leaping for joy, all four legs off the ground, drawn exactly like the attached painting (goat_kid.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. It holds the same mid-leap pose in every view. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Goat on a wall · `goat_on_wall`

Save as `goat_on_wall_views.png` · Square 1:1 · Attach: goat_on_wall.jpg (its painting) · Model: `ArtSource/models_meshy/animals/goat_on_wall.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a brown-and-white goat standing on top of a low brick wall, drawn exactly like the attached painting (goat_on_wall.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. The wall is low and about 40 cm deep, plain old brickwork all round. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Brown hen pecking · `hen_1`

Save as `hen_1_views.png` · Square 1:1 · Attach: hen_1.jpg (its painting) · Model: `ArtSource/models_meshy/animals/hen_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a rust-brown hen pecking at scattered grain, drawn exactly like the attached painting (hen_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Buff hen pecking · `hen_2`

Save as `hen_2_views.png` · Square 1:1 · Attach: hen_2.jpg (its painting) · Model: `ArtSource/models_meshy/animals/hen_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a pale buff hen pecking at scattered grain, drawn exactly like the attached painting (hen_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Dark hen pecking · `hen_3`

Save as `hen_3_views.png` · Square 1:1 · Attach: hen_3.jpg (its painting) · Model: `ArtSource/models_meshy/animals/hen_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a dark speckled brown hen pecking at scattered grain, drawn exactly like the attached painting (hen_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Hen with chicks · `hen_with_chicks`

Save as `hen_with_chicks_views.png` · Landscape 3:2 · Attach: hen_with_chicks.jpg (its painting) · Model: `ArtSource/models_meshy/animals/hen_with_chicks.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a brown hen with six fluffy chicks around her, drawn exactly like the attached painting (hen_with_chicks.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Keep the chicks where they are around her in every view. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Two parrots on a branch · `parrots`

Save as `parrots_views.png` · Square 1:1 · Attach: parrots.jpg (its painting) · Model: `ArtSource/models_meshy/animals/parrots.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of two green rose-ringed parakeets facing each other on a bare branch, drawn exactly like the attached painting (parrots.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. The branch runs from side to side; in the side views one parrot is in front of the other. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Peacock · `peacock`

Save as `peacock_views.png` · Landscape 3:2 · Attach: peacock.jpg (its painting) · Model: `ArtSource/models_meshy/animals/peacock.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a peacock with its long train folded behind it, drawn exactly like the attached painting (peacock.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Palm squirrel on a rock · `squirrel`

Save as `squirrel_views.png` · Landscape 3:2 · Attach: squirrel.jpg (its painting) · Model: `ArtSource/models_meshy/animals/squirrel.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a striped Indian palm squirrel sitting up on a small rock, nibbling a nut, drawn exactly like the attached painting (squirrel.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its left side (it faces left): that is the left side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The front view looks at it head-on and the back view from behind; both side views show the same animal with matching markings, in the same pose. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## People

The villagers going about their day.

### Kids rolling a tyre · `kids_rolling_tyre`

Save as `kids_rolling_tyre_views.png` · Landscape 3:2 · Attach: kids_rolling_tyre.jpg (its painting) · Model: `ArtSource/models_meshy/people/kids_rolling_tyre.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a boy and a girl running and rolling an old tyre with a stick, drawn exactly like the attached painting (kids_rolling_tyre.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Milkman on a bicycle · `milkman_on_bicycle`

Save as `milkman_on_bicycle_views.png` · Square 1:1 · Attach: milkman_on_bicycle.jpg (its painting) · Model: `ArtSource/models_meshy/people/milkman_on_bicycle.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a milkman in a checked shirt and dhoti riding an old bicycle with a big aluminium milk can on the back, drawn exactly like the attached painting (milkman_on_bicycle.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Old man in an easy chair · `old_man_on_chair`

Save as `old_man_on_chair_views.png` · Square 1:1 · Attach: old_man_on_chair.jpg (its painting) · Model: `ArtSource/models_meshy/people/old_man_on_chair.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a bald old man in a dhoti sitting in a wooden easy chair, holding a walking stick, drawn exactly like the attached painting (old_man_on_chair.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Vegetable cart seller · `vegetable_seller`

Save as `vegetable_seller_views.png` · Square 1:1 · Attach: vegetable_seller.jpg (its painting) · Model: `ArtSource/models_meshy/people/vegetable_seller.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a vegetable seller in a dhoti pushing a wooden handcart of vegetables, drawn exactly like the attached painting (vegetable_seller.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Woman carrying a pot · `woman_carrying_pot`

Save as `woman_carrying_pot_views.png` · Portrait 2:3 · Attach: woman_carrying_pot.jpg (its painting) · Model: `ArtSource/models_meshy/people/woman_carrying_pot.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a woman in a rust-red sari walking with a brass pot balanced on her head, drawn exactly like the attached painting (woman_carrying_pot.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Woman drawing a kolam · `woman_drawing_kolam`

Save as `woman_drawing_kolam_views.png` · Square 1:1 · Attach: woman_drawing_kolam.jpg (its painting) · Model: `ArtSource/models_meshy/people/woman_drawing_kolam.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a woman in a blue sari crouching to draw a white kolam on the ground from a small bowl of rice flour, drawn exactly like the attached painting (woman_drawing_kolam.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting shows its right side (it faces right): that is the right side view, and the front view looks at it head-on. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. The same people, clothes and pose in every view: the front view facing us, the back view from behind, and both sides. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## Trees and plants

Trees, palms, bushes and the big foreground plants.

### Neem tree · `h1_1`

Save as `h1_1_views.png` · Square 1:1 · Attach: h1_1.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h1_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a big neem tree with a broad, dense crown and twisting roots, drawn exactly like the attached painting (h1_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Young neem tree · `h1_2`

Save as `h1_2_views.png` · Portrait 2:3 · Attach: h1_2.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h1_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a slim young neem tree, drawn exactly like the attached painting (h1_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tree with a swing · `h1_3`

Save as `h1_3_views.png` · Square 1:1 · Attach: h1_3.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h1_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a leaning tree with a wooden plank swing hanging from a branch, drawn exactly like the attached painting (h1_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tamarind tree · `h2_1`

Save as `h2_1_views.png` · Square 1:1 · Attach: h2_1.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h2_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a tamarind tree with a gnarled trunk and hanging brown pods, drawn exactly like the attached painting (h2_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Drumstick tree · `h2_2`

Save as `h2_2_views.png` · Portrait 2:3 · Attach: h2_2.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h2_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a slender drumstick (moringa) tree with long hanging pods, drawn exactly like the attached painting (h2_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Young tamarind tree · `h2_3`

Save as `h2_3_views.png` · Square 1:1 · Attach: h2_3.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h2_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a young tamarind tree with brown pods, drawn exactly like the attached painting (h2_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Young drumstick tree · `h2_4`

Save as `h2_4_views.png` · Portrait 2:3 · Attach: h2_4.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h2_4.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a thin young drumstick tree with long pods, drawn exactly like the attached painting (h2_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Peepal on a low platform · `h3_1`

Save as `h3_1_views.png` · Square 1:1 · Attach: h3_1.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h3_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a big peepal tree on a low, square stone platform, drawn exactly like the attached painting (h3_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Coconut palm · `h4_1`

Save as `h4_1_views.png` · Portrait 2:3 · Attach: h4_1.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h4_1.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a straight coconut palm with a cluster of coconuts, drawn exactly like the attached painting (h4_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Curving coconut palm · `h4_2`

Save as `h4_2_views.png` · Portrait 2:3 · Attach: h4_2.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h4_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a tall, curving coconut palm, drawn exactly like the attached painting (h4_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Twin coconut palms · `h4_3`

Save as `h4_3_views.png` · Portrait 2:3 · Attach: h4_3.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h4_3.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of two coconut palms growing from one base, curving apart, drawn exactly like the attached painting (h4_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Bottle palm · `h4_4`

Save as `h4_4_views.png` · Square 1:1 · Attach: h4_4.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h4_4.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a short palm with a swollen, bottle-shaped trunk and big arching fronds, drawn exactly like the attached painting (h4_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Coconut palm with a climbing loop · `h4_5`

Save as `h4_5_views.png` · Portrait 2:3 · Attach: h4_5.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h4_5.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a coconut palm with coconuts and a climber's rope loop on its trunk, drawn exactly like the attached painting (h4_5.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Banana plant · `h5_1`

Save as `h5_1_views.png` · Portrait 2:3 · Attach: h5_1.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h5_1.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a banana plant with broad leaves and a bunch of bananas, drawn exactly like the attached painting (h5_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Banana plant (2) · `h5_2`

Save as `h5_2_views.png` · Portrait 2:3 · Attach: h5_2.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h5_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a banana plant with broad leaves and a small bunch of bananas, drawn exactly like the attached painting (h5_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Papaya tree · `h5_3`

Save as `h5_3_views.png` · Portrait 2:3 · Attach: h5_3.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h5_3.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a papaya tree with a cluster of ripe and green papayas, drawn exactly like the attached painting (h5_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Curry-leaf tree · `h5_4`

Save as `h5_4_views.png` · Square 1:1 · Attach: h5_4.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h5_4.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a bushy curry-leaf tree, drawn exactly like the attached painting (h5_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Sugarcane clump · `h5_5`

Save as `h5_5_views.png` · Portrait 2:3 · Attach: h5_5.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h5_5.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a clump of sugarcane stalks, drawn exactly like the attached painting (h5_5.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Pumpkin trellis · `h5_6`

Save as `h5_6_views.png` · Square 1:1 · Attach: h5_6.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h5_6.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a pumpkin vine climbing a bamboo trellis, with orange pumpkins, drawn exactly like the attached painting (h5_6.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Hibiscus bush · `h6_1`

Save as `h6_1_views.png` · Square 1:1 · Attach: h6_1.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h6_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a round hibiscus bush with big red flowers, drawn exactly like the attached painting (h6_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Bougainvillea on a wall · `h6_2`

Save as `h6_2_views.png` · Square 1:1 · Attach: h6_2.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h6_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of magenta bougainvillea spilling over an old plastered brick wall, drawn exactly like the attached painting (h6_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. The wall is thin, about 30 cm, with the bougainvillea hanging over both faces. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Flower bed · `h6_3`

Save as `h6_3_views.png` · Landscape 3:2 · Attach: h6_3.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h6_3.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a low bed of pink and white flowers with croton leaves and a mossy stone, drawn exactly like the attached painting (h6_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Jasmine trellis · `h6_4`

Save as `h6_4_views.png` · Square 1:1 · Attach: h6_4.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h6_4.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of white jasmine climbing a bamboo trellis, drawn exactly like the attached painting (h6_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Crotons in pots · `h6_5`

Save as `h6_5_views.png` · Square 1:1 · Attach: h6_5.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h6_5.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of two croton plants with red and yellow leaves in clay pots, drawn exactly like the attached painting (h6_5.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Oleander bush · `h6_6`

Save as `h6_6_views.png` · Square 1:1 · Attach: h6_6.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h6_6.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of an oleander bush with pink flowers, drawn exactly like the attached painting (h6_6.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Marigold bed · `h6_7`

Save as `h6_7_views.png` · Landscape 3:2 · Attach: h6_7.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h6_7.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a low bed of orange marigolds, drawn exactly like the attached painting (h6_7.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Elephant-ear plant · `h7_1`

Save as `h7_1_views.png` · Square 1:1 · Attach: h7_1.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h7_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a big clump of dark green elephant-ear (taro) leaves, drawn exactly like the attached painting (h7_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Tall wild grass · `h7_2`

Save as `h7_2_views.png` · Portrait 2:3 · Attach: h7_2.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h7_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a clump of tall wild grass with seed heads, drawn exactly like the attached painting (h7_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Banana leaves · `h7_3`

Save as `h7_3_views.png` · Portrait 2:3 · Attach: h7_3.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h7_3.glb`

Note: The painting is cut off at its right edge: draw the whole plant.

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a banana plant's big, tattered leaves, drawn exactly like the attached painting (h7_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. The painting is cut off at its right edge: draw the whole plant. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Broken wall pillar · `h7_4`

Save as `h7_4_views.png` · Portrait 2:3 · Attach: h7_4.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h7_4.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a broken old lime-plastered brick wall pillar with weeds at its foot, drawn exactly like the attached painting (h7_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. Its sides and back are the same object continued, in the same materials and colours. It is about 30 cm thick, the same old plaster and brick on every face. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Mossy boulder with ferns · `h7_5`

Save as `h7_5_views.png` · Landscape 3:2 · Attach: h7_5.jpg (its painting) · Model: `ArtSource/models_meshy/plants/h7_5.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a mossy boulder surrounded by ferns, drawn exactly like the attached painting (h7_5.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

## Ground details

Small things on the ground. The prints, ruts and cracked mud need no model: they are painted on the ground as they are.

### Cart rut · `cart_rut`

No model needed: it lies flat and is painted on the ground as it is.

### Coconut · `coconut`

Save as `coconut_views.png` · Square 1:1 · Attach: coconut.jpg (its painting) · Model: `ArtSource/models_meshy/ground/coconut.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a fallen brown coconut in its husk, drawn exactly like the attached painting (coconut.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Cracked mud · `cracked_mud`

No model needed: it lies flat and is painted on the ground as it is.

### Footprints · `footprints`

No model needed: it lies flat and is painted on the ground as it is.

### Hen prints · `hen_prints`

No model needed: it lies flat and is painted on the ground as it is.

### Hoof prints · `hoof_prints`

No model needed: it lies flat and is painted on the ground as it is.

### Coconut husk · `husk`

Save as `husk_views.png` · Landscape 3:2 · Attach: husk.jpg (its painting) · Model: `ArtSource/models_meshy/ground/husk.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a broken, fibrous coconut husk lying on the ground, drawn exactly like the attached painting (husk.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Dry leaf · `leaf_1`

Save as `leaf_1_views.png` · Portrait 2:3 · Attach: leaf_1.jpg (its painting) · Model: `ArtSource/models_meshy/ground/leaf_1.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a single dry, gently curled brown leaf, drawn exactly like the attached painting (leaf_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Dry leaf (2) · `leaf_2`

Save as `leaf_2_views.png` · Portrait 2:3 · Attach: leaf_2.jpg (its painting) · Model: `ArtSource/models_meshy/ground/leaf_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a single dry, gently curled brown leaf, drawn exactly like the attached painting (leaf_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Dry leaf (3) · `leaf_3`

Save as `leaf_3_views.png` · Portrait 2:3 · Attach: leaf_3.jpg (its painting) · Model: `ArtSource/models_meshy/ground/leaf_3.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a single dry, gently curled brown leaf, drawn exactly like the attached painting (leaf_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Pebble cluster · `pebble_cluster`

Save as `pebble_cluster_views.png` · Landscape 3:2 · Attach: pebble_cluster.jpg (its painting) · Model: `ArtSource/models_meshy/ground/pebble_cluster.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a small cluster of grey and brown pebbles, drawn exactly like the attached painting (pebble_cluster.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Pebbles · `pebbles`

Save as `pebbles_views.png` · Landscape 3:2 · Attach: pebbles.jpg (its painting) · Model: `ArtSource/models_meshy/ground/pebbles.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a few scattered stones of different sizes, drawn exactly like the attached painting (pebbles.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Grass tuft · `tuft_1`

Save as `tuft_1_views.png` · Square 1:1 · Attach: tuft_1.jpg (its painting) · Model: `ArtSource/models_meshy/ground/tuft_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a tuft of green grass, drawn exactly like the attached painting (tuft_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Grass tuft (2) · `tuft_2`

Save as `tuft_2_views.png` · Square 1:1 · Attach: tuft_2.jpg (its painting) · Model: `ArtSource/models_meshy/ground/tuft_2.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small tuft of green grass, drawn exactly like the attached painting (tuft_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Grass tuft (3) · `tuft_3`

Save as `tuft_3_views.png` · Square 1:1 · Attach: tuft_3.jpg (its painting) · Model: `ArtSource/models_meshy/ground/tuft_3.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small tuft of green grass, drawn exactly like the attached painting (tuft_3.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Grass tuft (4) · `tuft_4`

Save as `tuft_4_views.png` · Square 1:1 · Attach: tuft_4.jpg (its painting) · Model: `ArtSource/models_meshy/ground/tuft_4.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small tuft of green grass, drawn exactly like the attached painting (tuft_4.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Twigs · `twigs`

Save as `twigs_views.png` · Landscape 3:2 · Attach: twigs.jpg (its painting) · Model: `ArtSource/models_meshy/ground/twigs.glb`

```text
Landscape 3:2 image.

Model sheet for 3D modelling of a few dry twigs lying together, drawn exactly like the attached painting (twigs.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It is a small thing lying on the ground: show it at ground level from the front, both sides and the back. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Yellow-flowered weed · `weed_1`

Save as `weed_1_views.png` · Square 1:1 · Attach: weed_1.jpg (its painting) · Model: `ArtSource/models_meshy/ground/weed_1.glb`

```text
Square 1:1 image.

Model sheet for 3D modelling of a small weed with yellow flowers, drawn exactly like the attached painting (weed_1.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```

### Yellow-flowered weed (2) · `weed_2`

Save as `weed_2_views.png` · Portrait 2:3 · Attach: weed_2.jpg (its painting) · Model: `ArtSource/models_meshy/ground/weed_2.glb`

```text
Portrait 2:3 image.

Model sheet for 3D modelling of a small weed with yellow flowers, drawn exactly like the attached painting (weed_2.jpg): keep its shape, proportions, colours, materials and every painted detail as they are. The painting is its front view. Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side view (seen from its right, so it faces right); bottom right, the back view. It looks much the same from every side and is about as deep as it is wide. Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat light-grey background everywhere, with no dividing lines, frames, ground plane or labels.

The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters or packaged goods.

Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other striped awnings.

Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or watermarks.
```
