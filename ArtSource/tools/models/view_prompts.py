"""Prompts for four-view model sheets of every asset, for building the 3D models in Meshy.

    python view_prompts.py [--site DIR]

Writes docs/art/prompt-sheet-3d.md. With --site, also writes the web version's data (data.json) and each asset's
reference picture (refs/<name>.jpg, the cut-out on plain light grey) into DIR.

Each prompt asks ChatGPT (or Gemini) for one image: the asset drawn four times in a 2 by 2 grid, front, left side,
right side and back, from its painting (attached), at one scale on a plain light-grey background. The sheet is cut
into the four views (the web version does it), Meshy builds the model from them, and the model comes back as
ArtSource/models_meshy/<folder>/<name>.glb for finish_models.py to fit into the game.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
CUT = ROOT / "ArtSource" / "cutouts"
REF = ROOT / "ArtSource" / "references"
ARGS = sys.argv[1:]
SITE = pathlib.Path(ARGS[ARGS.index("--site") + 1]) if "--site" in ARGS else None

# ------------------------------------------------------------------ the shared paragraphs (as in prompt-sheet.md)
SETTING = ("The setting is a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud "
           "and terracotta-tiled buildings; things made of brass, copper, clay, wood, cane, cotton, jute and palm leaf. "
           "Nothing modern: no plastic (no buckets, chairs, sheets or black water tanks), no concrete or half-built "
           "multi-storey buildings, no overhead water tanks, satellite dishes, motorbikes, tube lights, printed posters "
           "or packaged goods.")
SHADES = ("Market shades are plain faded cotton cloth (undyed, indigo, turmeric or madder red), woven palm-leaf mats, "
          "thatch or big black cloth umbrellas, never red-and-white or other striped awnings.")
STYLE = ("Art style: stylised, hand-painted 3D game art for a side-scrolling mobile game set in a South Indian village. "
         "Characters and props have clean dark outlines, flat saturated colour and soft two-tone cel shading, like a "
         "painted toy diorama. Palette: terracotta and red-earth ground, turmeric yellow, kumkum red, indigo and "
         "lime-washed walls, paddy green, warm golden light. No text, letters, numbers, logos, signatures, borders or "
         "watermarks.")
G_SETTING = ("It is set in a South Indian village in the 1970s and 1980s, like a vintage storybook: lime-washed, mud and "
             "terracotta-tiled buildings, and things made of brass, copper, clay, wood, cane, cotton, jute and palm "
             "leaf. Everything belongs to that time, so nothing plastic, concrete or modern appears: no plastic buckets, "
             "chairs, sheets or black water tanks, no overhead water tanks, satellite dishes, motorbikes, tube lights, "
             "printed posters or packaged goods. Market shades are plain faded cotton cloth (undyed, indigo, turmeric or "
             "madder red), woven palm-leaf mats, thatch or big black cloth umbrellas, never red-and-white or other "
             "striped awnings. Render it as stylised, hand-painted 3D game art for a side-scrolling mobile game, like a "
             "painted toy diorama, with clean dark outlines, flat saturated colours and soft two-tone cel shading. The "
             "image is clean artwork only: unlabeled, unsigned and borderless.")

# ------------------------------------------------------------------ every asset
# (name, kind, painted view, title, what it is, anything particular)
# view: "front", "right" (it faces right in the painting: its right side), "left", or None (no painting yet).
A = [
    # animals
    ("buffalo_mud", "animal", "right", "Buffalo in the mud", "a dark water buffalo lying in a patch of wet mud, with curved horns, a rope halter and a bell", "Show the patch of mud around it in every view."),
    ("bullocks", "animal", "right", "Pair of bullocks", "a pair of white bullocks standing side by side in step, with painted horns, striped cloth blankets on their backs and bells", "There are exactly two bullocks, side by side: in the side views the nearer one hides most of the other, and in the front and back views both are seen side by side."),
    ("calf", "animal", "right", "Calf", "a young brown calf standing", ""),
    ("cat_on_wall", "prop", "front", "Cat asleep on a wall", "a tabby cat curled up asleep on top of a short broken brick wall", "The wall is thin, about 25 cm deep, with plain old brickwork on its back face; the cat lies along its top."),
    ("cow", "animal", "right", "White cow", "a white humped village cow with red-and-white painted horns, a rope halter and a brass bell", ""),
    ("crows_on_ledge", "prop", "front", "Crows on a ledge", "three house crows perched in a row on a short weathered wooden ledge", "The ledge is a plain plank on two brackets, about as deep as a crow; the crows all face the same way in every view."),
    ("dog_barking", "animal", "right", "Barking dog", "a ginger-and-white village dog standing and barking, with a curled tail", ""),
    ("dog_sleeping", "animal", "right", "Sleeping dog", "a ginger-and-white village dog curled up asleep, chin on its paws", ""),
    ("duck_1", "animal", "right", "White duck", "a white duck standing upright", ""),
    ("duck_2", "animal", "left", "White duck, facing left", "a white duck standing upright", ""),
    ("goat_eating", "animal", "right", "Goat eating leaves", "a black-and-white goat standing and chewing a leafy twig", ""),
    ("goat_kid", "animal", "right", "Goat kid leaping", "a small black goat kid leaping for joy, all four legs off the ground", "It holds the same mid-leap pose in every view."),
    ("goat_on_wall", "animal", "right", "Goat on a wall", "a brown-and-white goat standing on top of a low brick wall", "The wall is low and about 40 cm deep, plain old brickwork all round."),
    ("hen_1", "animal", "right", "Brown hen pecking", "a rust-brown hen pecking at scattered grain", ""),
    ("hen_2", "animal", "right", "Buff hen pecking", "a pale buff hen pecking at scattered grain", ""),
    ("hen_3", "animal", "right", "Dark hen pecking", "a dark speckled brown hen pecking at scattered grain", ""),
    ("hen_with_chicks", "animal", "right", "Hen with chicks", "a brown hen with six fluffy chicks around her", "Keep the chicks where they are around her in every view."),
    ("parrots", "prop", "front", "Two parrots on a branch", "two green rose-ringed parakeets facing each other on a bare branch", "The branch runs from side to side; in the side views one parrot is in front of the other."),
    ("peacock", "animal", "right", "Peacock", "a peacock with its long train folded behind it", ""),
    ("squirrel", "animal", "left", "Palm squirrel on a rock", "a striped Indian palm squirrel sitting up on a small rock, nibbling a nut", ""),
    # fields
    ("bund_block", "prop", "front", "Field bund block", "a short block of raised earth bund between paddy fields: red earth with grass and small yellow flowers along its top", "It is a straight earth bank about 0.9 m deep, the same from the front and back, sloping down at both ends."),
    ("bund_strip", "prop", "front", "Field bund strip", "a long, low strip of earth bund with a grassy top", "It is a straight earth bank about 0.9 m deep, the same from the front and back."),
    ("canal_bank", "prop", "front", "Canal bank", "a short stretch of irrigation canal: earth banks sloping down to shallow water with reeds", "From the sides, both banks slope down to the water channel between them."),
    ("canal_bridge", "prop", "front", "Canal bridge", "a small bridge of stone slabs across a narrow stone-lined canal, with plants growing at its corners", ""),
    ("crop_strip_1", "crop", None, "Seedbed strip", "a long strip of paddy seedbed: dense bright-green rice seedlings a hand high in wet earth", ""),
    ("crop_strip_2", "crop", None, "Stubble strip", "a long strip of harvested field: short golden stubble in rows on dry earth, with a few small hay bundles", ""),
    ("crop_strip_3", "crop", None, "Sorghum strip", "a long strip of tall sorghum (jowar) plants with heavy reddish-brown grain heads", ""),
    ("crop_strip_4", "crop", None, "Groundnut strip", "a long strip of low, bushy green groundnut plants in red earth", ""),
    ("crop_strip_5", "crop", None, "Cotton strip", "a long strip of cotton plants with open white bolls", ""),
    ("crop_strip_6", "crop", None, "Banana strip", "a long row of young banana plants with broad green leaves", ""),
    ("field_bldg_1", "prop", "front", "Well with a bullock water lift", "a stone-lined well with a wooden frame and a leather bucket on a rope pulled by two white bullocks walking down a sloping earth ramp, clay pots beside the well", ""),
    ("field_bldg_2", "building", "front", "Watch hut on stilts", "a thatched field watch hut (machan) on tall bamboo stilts, with a bamboo ladder", ""),
    ("field_bldg_3", "building", "front", "Farm shed with a haystack", "a small open thatched farm shed beside a haystack, with a grinding stone and farm tools", ""),
    ("field_life_1", "person", "right", "Farmer ploughing", "a farmer in a white vest and dhoti guiding a wooden plough pulled by two white bullocks through muddy earth", ""),
    ("field_life_2", "person", "right", "Women transplanting paddy", "three women in saris bent over, planting rice seedlings in a muddy paddy patch", ""),
    ("field_life_3", "person", "front", "Boy herding goats", "a boy with a long stick herding four goats", ""),
    ("field_life_4", "animal", "right", "Buffalo with an egret", "a black water buffalo lying in mud with a white egret standing on its back", ""),
    ("field_life_5", "person", "right", "Old man herding ducks", "an old man in white with a long bamboo stick herding a line of white ducks", ""),
    ("field_life_6", "person", "front", "Man carrying a paddy sheaf", "a man in a vest and lungi carrying a big sheaf of harvested paddy on his head", ""),
    ("field_shrine", "building", "front", "Field shrine", "a small whitewashed roadside shrine with a deity in a niche and a saffron flag on top", ""),
    ("field_tree_1", "tree", "front", "Banyan tree", "a big banyan tree with hanging aerial roots", ""),
    ("field_tree_2", "tree", "front", "Gnarled field tree", "a gnarled, twisted tree with sparse feathery leaves", ""),
    ("field_tree_3", "tree", "front", "Bamboo clump", "a clump of tall green bamboo", ""),
    ("field_tree_4", "plant", "front", "Screw pine bush", "a big screw pine bush of long, spiky, sword-shaped leaves", ""),
    ("field_tree_5", "tree", "front", "Casuarina trees", "a few slender casuarina trees with feathery needles", ""),
    ("field_tree_6", "plant", "front", "Cactus and agave", "a dry patch of red earth with an agave, a prickly-pear cactus and small succulents", ""),
    ("granary", "building", "front", "Granary on stone legs", "a small square granary with a red-tiled hipped roof, standing on stone legs", ""),
    ("haystack", "round", "front", "Haystack", "a tall round haystack of golden straw, tied at the top", ""),
    ("haystack_small", "round", "front", "Small haystack", "a smaller round haystack with a pole sticking out of its top", ""),
    ("hut_with_pen", "building", "front", "Hut with a goat pen", "a small thatched mud hut with a bamboo pen fence beside it", ""),
    ("paddy_ripe", "crop", "front", "Ripe paddy row", "a long row of ripe golden paddy, the heads drooping", ""),
    ("paddy_tall", "crop", "front", "Green paddy row", "a long row of tall green paddy", ""),
    ("paddy_young", "crop", "front", "Young paddy in water", "a long strip of young paddy plants standing in shallow water", ""),
    ("palmyra_1", "tree", "front", "Palmyra palm", "a tall palmyra palm with a fan of stiff leaves on a straight dark trunk", ""),
    ("palmyra_2", "tree", "front", "Palmyra palm (2)", "a tall palmyra palm with a fan of stiff leaves on a straight dark trunk", ""),
    ("palmyra_3", "tree", "front", "Palmyra palm (3)", "a tall palmyra palm with a fan of stiff leaves on a straight dark trunk", ""),
    ("pump_house", "building", "front", "Pump house", "a small brick pump house with a wooden door and a pipe pouring water into a channel", ""),
    ("scarecrow", "prop", "front", "Scarecrow", "a scarecrow with a painted clay-pot head, a white shirt, a red scarf and straw hands on a wooden pole", ""),
    ("sluice_gate", "prop", "front", "Sluice gate", "a wooden canal sluice gate with an iron screw wheel between two stone pillars, water below", ""),
    ("sugarcane", "crop", "front", "Sugarcane row", "a long row of tall sugarcane", ""),
    ("well", "round", "front", "Village well", "a round stone-built well with a wooden crossbeam, a pulley, a coiled rope and a small bucket", ""),
    # ground details
    ("cart_rut", "flat", "front", "Cart rut", "tracks of cart wheels in the earth", ""),
    ("coconut", "small", "front", "Coconut", "a fallen brown coconut in its husk", ""),
    ("cracked_mud", "flat", "front", "Cracked mud", "a patch of dry, cracked mud", ""),
    ("footprints", "flat", "front", "Footprints", "a trail of small bare footprints", ""),
    ("hen_prints", "flat", "front", "Hen prints", "a trail of hen footprints", ""),
    ("hoof_prints", "flat", "front", "Hoof prints", "a trail of cattle hoof prints", ""),
    ("husk", "small", "front", "Coconut husk", "a broken, fibrous coconut husk lying on the ground", ""),
    ("leaf_1", "small", "front", "Dry leaf", "a single dry, gently curled brown leaf", ""),
    ("leaf_2", "small", "front", "Dry leaf (2)", "a single dry, gently curled brown leaf", ""),
    ("leaf_3", "small", "front", "Dry leaf (3)", "a single dry, gently curled brown leaf", ""),
    ("pebble_cluster", "small", "front", "Pebble cluster", "a small cluster of grey and brown pebbles", ""),
    ("pebbles", "small", "front", "Pebbles", "a few scattered stones of different sizes", ""),
    ("tuft_1", "plant", "front", "Grass tuft", "a tuft of green grass", ""),
    ("tuft_2", "plant", "front", "Grass tuft (2)", "a small tuft of green grass", ""),
    ("tuft_3", "plant", "front", "Grass tuft (3)", "a small tuft of green grass", ""),
    ("tuft_4", "plant", "front", "Grass tuft (4)", "a small tuft of green grass", ""),
    ("twigs", "small", "front", "Twigs", "a few dry twigs lying together", ""),
    ("weed_1", "plant", "front", "Yellow-flowered weed", "a small weed with yellow flowers", ""),
    ("weed_2", "plant", "front", "Yellow-flowered weed (2)", "a small weed with yellow flowers", ""),
    # the lane
    ("bicycle", "vehicle", "left", "Bicycle", "an old black roadster bicycle with a rear carrier and a stand", ""),
    ("brass_pots", "round", "front", "Brass pots", "two round brass water pots (kudam), one big and one small, on the ground", ""),
    ("bullock_cart", "vehicle", "right", "Bullock cart", "a wooden bullock cart with two big spoked wheels, painted side boards, hay in its bed and its yoke pole resting on a prop", ""),
    ("cattle_shed", "building", "front", "Cattle shed", "an open-fronted thatched cattle shed on wooden posts, its lime-washed back wall marked with handprints, a calf lying in the straw", "Its front is open between the posts."),
    ("chicken_basket", "round", "front", "Chicken basket", "a dome-shaped woven cane coop basket for hens", ""),
    ("clothesline", "prop", "front", "Clothesline", "a rope clothesline between two bamboo posts, with a magenta and a yellow cloth hanging on it", "It is thin: the posts and the hanging cloths are its whole depth."),
    ("doorway_garland", "building", "front", "Doorway with a garland", "a red-washed doorway with a carved wooden double door, a mango-leaf garland across the top and a kolam on the step", "It is a short piece of house wall about 40 cm thick; from behind, the same doorway seen from inside, plainly plastered."),
    ("dung", "small", "front", "Cow-dung cake", "a round, flat cow-dung cake drying on the ground", ""),
    ("hand_pump", "prop", "front", "Hand pump", "a green cast-iron village hand pump on a stone base, with a steel bucket and a small puddle", ""),
    ("house_being_built", "building", "front", "House being built", "a mud-brick house being built: unfinished walls, a roof frame of bare wooden poles, piles of bricks and earth", ""),
    ("house_hut_porch", "building", "front", "Thatched house with a porch", "a mud-walled house with a deep thatched porch on wooden posts, round dung cakes drying on its walls", ""),
    ("house_indigo_veranda", "building", "front", "Indigo house with a veranda", "a narrow indigo-blue lime-washed house with a red-tiled veranda roof on turned wooden pillars, a carved door with a garland, a window and kolam steps", ""),
    ("house_limewash", "building", "front", "Lime-washed house", "a narrow cream lime-washed flat-roofed house with a parapet, a teal-framed carved door with a garland, a bougainvillea vine and kolam steps", ""),
    ("house_mud_tin", "building", "front", "Mud house with a tin roof", "a plain mud-plastered house with a corrugated tin roof held down by an old tyre, a blue wooden door and a propped window shutter", ""),
    ("house_pink", "building", "front", "Pink house", "a narrow pink lime-washed flat-roofed house with a parapet, a teal-framed carved door with a garland, a jasmine vine, a potted hibiscus and kolam steps", ""),
    ("house_plank_sheet", "building", "front", "Plank and tin house", "a patched house of weathered planks and rusty tin sheets, with a sari curtain in the doorway and potted plants on the window sill", ""),
    ("house_potter", "building", "front", "Potter's house", "a potter's mud house with a thatched roof running out over an open work shed with a potter's wheel, rows of clay pots drying in front", ""),
    ("house_thatched_hut", "building", "front", "Thatched hut with a pumpkin vine", "a mud hut with a thick thatched roof covered in a pumpkin vine, a wooden door and a clay pot", ""),
    ("house_tiled_gate", "building", "front", "Tiled house behind a wall", "a lime-washed house with a red-tiled roof behind a compound wall with a wooden gate, and a tree inside the compound", ""),
    ("house_turmeric_ladder", "building", "front", "Turmeric house with a ladder", "a narrow turmeric-yellow flat-roofed house with a parapet, a carved door with a garland, a barred window, a clay pot, kolam steps and a bamboo ladder leaning up to the roof", ""),
    ("house_village_head", "building", "front", "Village head's house", "a big two-storey house with red-tiled roofs, a long veranda on carved pillars and lime-washed walls with a maroon band", ""),
    ("house_weaver", "building", "front", "Weaver's house", "a whitewashed house with a thatched roof and a loom window, a frame of coloured yarn drying beside it", ""),
    ("jute_sacks", "prop", "front", "Jute sacks", "three full jute sacks with purple stripes, two below and one on top", ""),
    ("kolam_1", "flat", "front", "Kolam 1", "a white rice-flour kolam with coloured petals", ""),
    ("kolam_2", "flat", "front", "Kolam 2", "a white rice-flour kolam with coloured petals", ""),
    ("kolam_3", "flat", "front", "Kolam 3", "a white rice-flour kolam with coloured petals", ""),
    ("kolam_4", "flat", "front", "Kolam 4", "a white rice-flour kolam with coloured petals", ""),
    ("kolam_5", "flat", "front", "Kolam 5", "a white rice-flour kolam with coloured petals", ""),
    ("kolam_6", "flat", "front", "Kolam 6", "a white rice-flour kolam with coloured petals", ""),
    ("lamp_pillar", "round", "front", "Lamp pillar", "a tall carved brass lamp pillar (deepa sthambam) with rows of little lamps, on a stepped stone base", ""),
    ("panchayat_office", "building", "front", "Panchayat office", "a plain cream single-storey village office with a flat roof, a door, two windows, a clock and a bench, a hand pump beside it", ""),
    ("peepal_platform", "tree", "front", "Peepal tree on a platform", "a big peepal tree growing out of a raised stone platform (katte) with steps, a sacred thread round its trunk", ""),
    ("pot_stack", "round", "front", "Stack of clay pots", "three red clay pots of decreasing size stacked one on another, painted with white and yellow triangles", ""),
    ("rope_cot", "prop", "front", "Rope cot", "a wooden rope cot (charpai) with turned legs and a woven jute top, a striped pillow at one end", "From the ends it is about 85 cm deep."),
    ("shop_provisions", "building", "front", "Provisions shop", "a small mud-walled provisions shop with a tin awning, shelves of glass jars and hanging bananas, and a signboard with no words", ""),
    ("shop_tailor_cycle", "building", "front", "Tailor and cycle shop", "a small wooden shop under a tin awning: shelves of cloth and a sewing machine on one side, bicycle tyres hanging on the other", ""),
    ("shop_tea_stall", "building", "front", "Tea stall", "a small dark-wood tea stall under a palm-thatch roof on poles, with a brass kettle on a clay stove, glasses, a jar of biscuits, a radio and a newspaper on a bench", ""),
    ("shrine_stone", "prop", "front", "Stone shrine", "an upright dark stone with painted marks, a marigold garland and a small oil lamp, on a stone base", ""),
    ("shrine_tree", "tree", "front", "Tree shrine", "a small whitewashed shrine at the foot of a big spreading tree", ""),
    ("tree_mango_1", "tree", "front", "Mango tree", "a mango tree with a twisted trunk, a dense rounded crown and ripe mangoes", ""),
    ("tree_mango_2", "tree", "front", "Mango tree (2)", "a mango tree with a twisted trunk, a dense rounded crown and ripe mangoes", ""),
    ("tulsi_planter", "prop", "front", "Tulsi planter", "a square painted tulsi planter (brindavan) with a red flower motif and a holy basil plant on top", "It is square, the same painted motif on all four sides."),
    ("water_pot_stand", "prop", "front", "Water pot on a stand", "a big red clay water pot with a brass tap, on a stone stand of two upright slabs and a top slab", ""),
    # the market
    ("black_tank", "round", "front", "Water tank", "a big round water storage tank on a stone stand", "Your style rules rule out black plastic tanks: make it a plastered terracotta tank, keeping its shape and stand."),
    ("brass_vessels", "round", "front", "Brass vessels", "a group of shiny brass pots and containers of different sizes", ""),
    ("bunting", "prop", "front", "Bunting", "a string of colourful triangular cloth flags", "It is a thin string of flags: from the sides, just the string and the flags edge-on."),
    ("chariot_shed", "building", "front", "Chariot shed", "a tall wooden shed with a sloping roof sheltering a carved wooden temple chariot, its front open", ""),
    ("chilli_mat", "prop", "front", "Chilli mat", "a woven palm-leaf mat with red chillies spread out to dry", "It lies nearly flat on the ground."),
    ("coconut_cart", "vehicle", "right", "Coconut cart", "a wooden cart heaped with green coconuts, pulled by two white bullocks", ""),
    ("flower_stall", "stall", "front", "Flower stall", "a small bamboo flower stall hung with marigold, jasmine and rose garlands, baskets of loose flowers on its counter", ""),
    ("hens_basket", "round", "front", "Hens in a basket", "two hens sitting in a shallow woven basket of straw", ""),
    ("kite", "prop", "front", "Kite", "a pink-and-yellow paper kite with a ribboned tail", "It is a flat paper kite: from the sides, edge-on."),
    ("lamp_step", "prop", "front", "Lamp steps", "temple steps of carved yellow stone with a pillar, and lit clay oil lamps on each step", ""),
    ("lantern", "round", "front", "Lantern", "a hurricane lantern with a glowing wick", ""),
    ("mandapam", "building", "front", "Mandapam", "a long, low stone temple pavilion (mandapam) with a row of carved pillars under a flat stone roof", ""),
    ("papad_mat", "prop", "front", "Papad mat", "a woven palm-leaf mat with round papads drying on it", "It lies nearly flat on the ground."),
    ("parapet_gap", "building", "front", "Roof parapet", "a section of lime-washed roof parapet wall with a dip in the middle and a painted red-and-white border", "It is a thin wall, about 30 cm thick, plain on its back."),
    ("roof_house_a_1", "building", "front", "House with a terrace stair", "a lime-washed house with a red-tiled roof and an outside stair up to a flat terrace with drying pots and dung cakes", ""),
    ("roof_house_a_2", "building", "front", "Mud house with a roof garden", "a mud house with a flat roof overgrown with a vine, and a small thatched lean-to", ""),
    ("roof_house_b_1", "building", "front", "Blue terrace house", "a pale-blue house with a red-tiled veranda roof, green shutters, a flat terrace with chillies and papads drying, and a ladder", ""),
    ("roof_house_b_2", "building", "front", "Old house with a roof hut", "an old cracked-plaster house with a small thatched hut and firewood on its roof", ""),
    ("stall_c_1", "stall", "front", "Spice stall", "a spice stall under a faded yellow cotton shade on bamboo poles: open jute sacks of red chillies, turmeric and grains", ""),
    ("stall_c_2", "stall", "front", "Vegetable seller under an umbrella", "an old woman in a white sari selling vegetables under a palm-leaf umbrella, with baskets of cabbages, greens and potatoes and a hand grinder", ""),
    ("stall_c_3", "stall", "front", "Cloth stall", "a cloth stall under a thatched shade: folded saris and cloth stacked on a low cot, more hanging from the front beam", ""),
    ("stall_d_1", "stall", "front", "Coconut and gourd stall", "a coconut and gourd stall under a coconut-frond shade, bunches hanging from the poles and more heaped on the ground", ""),
    ("stall_d_2", "stall", "front", "Pot stall", "a pot stall under a faded indigo cotton shade on bamboo poles: clay pots and jaggery blocks on a low bench", ""),
    ("stall_d_3", "stall", "front", "Basket stall", "a basket stall under a thatched shade, stacked with woven cane baskets and winnowing trays", ""),
    ("stall_e_1", "stall", "front", "Vegetable stall", "a vegetable stall under a faded madder-red cotton shade: tomatoes, aubergines, greens and bananas laid out on the ground", ""),
    ("stall_e_2", "stall", "front", "Snack fryer's stall", "a snack stall under a woven palm-leaf shade: a man frying in a big iron kadai over a clay stove", ""),
    ("stall_e_3", "stall", "front", "Parrot fortune teller", "a fortune teller sitting cross-legged under a big black cloth umbrella, with a caged parrot and cards spread on a mat", ""),
    ("stall_f_1", "stall", "front", "Sweets counter", "a sweets stall under an undyed cotton shade: a woman behind a wooden counter with glass jars of sweets", ""),
    ("stall_f_2", "stall", "front", "Sweets shelves", "a sweets stall under an undyed cotton shade: trays of jalebis and laddus on tiered shelves behind a wooden counter", ""),
    ("stall_f_3", "stall", "front", "Sugarcane juice stall", "a sugarcane juice stall: a man feeding cane into an iron roller press on a wooden table under a palm-leaf shade, glasses of juice", ""),
    ("stall_f_4", "stall", "front", "Broom and mat seller", "a broom and mat seller sitting under a thatched shade among rolled palm mats, brooms and coils of rope", ""),
    ("stall_flowers", "stall", "front", "Flower seller", "a flower seller woman sitting under a woven palm-leaf shade, garlands hanging and baskets of flowers around her", ""),
    ("stall_g_1", "stall", "front", "Dried fish stall", "a dried-fish stall under a thatched shade: baskets and rows of dried fish on a mat", ""),
    ("stall_g_2", "stall", "front", "Bangle stall", "a bangle stall under a faded indigo cotton shade: racks of coloured glass bangles, a mirror and bowls of kumkum powder", ""),
    ("stall_g_3", "stall", "front", "Banana stall", "a banana stall under a woven palm-leaf shade, bunches of green and yellow bananas hanging from it", ""),
    ("stall_h_1", "stall", "front", "Cobbler", "a cobbler sitting cross-legged under a big black cloth umbrella, sandals and tools spread on a mat", ""),
    ("stall_h_2", "stall", "front", "Barber's pitch", "a barber's pitch under a woven palm-leaf shade on bamboo poles: a wooden stool, a mirror hung on a pole and a brass bowl", ""),
    ("stall_h_3", "stall", "front", "Knife grinder", "a knife grinder's pitch under a coconut-frond shade: a treadle grinding wheel and knives laid out on a mat", ""),
    ("stall_high", "stall", "front", "Tall grain stall", "a tall bamboo stall with a counter of grain sacks and bowls of spice powders over a woven cloth", "Your style rules rule out striped awnings: make its shade plain faded madder-red cotton, keeping its shape."),
    ("stall_low", "stall", "front", "Low leaf stall", "a low bamboo stall with green banana leaves and a basket of coconuts on its counter", "Your style rules rule out striped awnings: make its shade plain faded turmeric cotton, keeping its shape."),
    ("stall_potter", "stall", "front", "Potter's pitch", "a potter sitting among clay pots and figurines under a big black umbrella and a woven palm-leaf shade", ""),
    ("stall_sweets", "stall", "front", "Sweet maker", "a sweet maker frying in a big iron kadai over a fire, plates of sweets around him", "Your style rules rule out striped awnings: make its shade plain undyed cotton, keeping its shape."),
    ("stall_veg", "stall", "front", "Vegetable heap stall", "a vegetable stall heaped with tomatoes, aubergines, chillies and greens in baskets", "Your style rules rule out striped awnings: make its shade plain faded indigo cotton, keeping its shape."),
    ("stall_vessels", "stall", "front", "Vessel stall", "a brass and copper vessel stall under a thatched shade: rows of shiny pots, lamps and tumblers", ""),
    ("tank_wall", "building", "front", "Temple tank wall", "a long, low stone wall of a temple tank with steps leading down and a small gateway in the middle", "It is a wall about 50 cm thick."),
    ("veg_basket", "round", "front", "Vegetable basket", "a woven cane basket heaped with aubergines, tomatoes and greens", ""),
    # people
    ("kids_rolling_tyre", "person", "right", "Kids rolling a tyre", "a boy and a girl running and rolling an old tyre with a stick", ""),
    ("milkman_on_bicycle", "person", "right", "Milkman on a bicycle", "a milkman in a checked shirt and dhoti riding an old bicycle with a big aluminium milk can on the back", ""),
    ("old_man_on_chair", "person", "right", "Old man in an easy chair", "a bald old man in a dhoti sitting in a wooden easy chair, holding a walking stick", ""),
    ("vegetable_seller", "person", "right", "Vegetable cart seller", "a vegetable seller in a dhoti pushing a wooden handcart of vegetables", ""),
    ("woman_carrying_pot", "person", "right", "Woman carrying a pot", "a woman in a rust-red sari walking with a brass pot balanced on her head", ""),
    ("woman_drawing_kolam", "person", "right", "Woman drawing a kolam", "a woman in a blue sari crouching to draw a white kolam on the ground from a small bowl of rice flour", ""),
    # trees and plants
    ("h1_1", "tree", "front", "Neem tree", "a big neem tree with a broad, dense crown and twisting roots", ""),
    ("h1_2", "tree", "front", "Young neem tree", "a slim young neem tree", ""),
    ("h1_3", "tree", "front", "Tree with a swing", "a leaning tree with a wooden plank swing hanging from a branch", ""),
    ("h2_1", "tree", "front", "Tamarind tree", "a tamarind tree with a gnarled trunk and hanging brown pods", ""),
    ("h2_2", "tree", "front", "Drumstick tree", "a slender drumstick (moringa) tree with long hanging pods", ""),
    ("h2_3", "tree", "front", "Young tamarind tree", "a young tamarind tree with brown pods", ""),
    ("h2_4", "tree", "front", "Young drumstick tree", "a thin young drumstick tree with long pods", ""),
    ("h3_1", "tree", "front", "Peepal on a low platform", "a big peepal tree on a low, square stone platform", ""),
    ("h4_1", "tree", "front", "Coconut palm", "a straight coconut palm with a cluster of coconuts", ""),
    ("h4_2", "tree", "front", "Curving coconut palm", "a tall, curving coconut palm", ""),
    ("h4_3", "tree", "front", "Twin coconut palms", "two coconut palms growing from one base, curving apart", ""),
    ("h4_4", "tree", "front", "Bottle palm", "a short palm with a swollen, bottle-shaped trunk and big arching fronds", ""),
    ("h4_5", "tree", "front", "Coconut palm with a climbing loop", "a coconut palm with coconuts and a climber's rope loop on its trunk", ""),
    ("h5_1", "plant", "front", "Banana plant", "a banana plant with broad leaves and a bunch of bananas", ""),
    ("h5_2", "plant", "front", "Banana plant (2)", "a banana plant with broad leaves and a small bunch of bananas", ""),
    ("h5_3", "plant", "front", "Papaya tree", "a papaya tree with a cluster of ripe and green papayas", ""),
    ("h5_4", "tree", "front", "Curry-leaf tree", "a bushy curry-leaf tree", ""),
    ("h5_5", "plant", "front", "Sugarcane clump", "a clump of sugarcane stalks", ""),
    ("h5_6", "plant", "front", "Pumpkin trellis", "a pumpkin vine climbing a bamboo trellis, with orange pumpkins", ""),
    ("h6_1", "plant", "front", "Hibiscus bush", "a round hibiscus bush with big red flowers", ""),
    ("h6_2", "plant", "front", "Bougainvillea on a wall", "magenta bougainvillea spilling over an old plastered brick wall", "The wall is thin, about 30 cm, with the bougainvillea hanging over both faces."),
    ("h6_3", "plant", "front", "Flower bed", "a low bed of pink and white flowers with croton leaves and a mossy stone", ""),
    ("h6_4", "plant", "front", "Jasmine trellis", "white jasmine climbing a bamboo trellis", ""),
    ("h6_5", "plant", "front", "Crotons in pots", "two croton plants with red and yellow leaves in clay pots", ""),
    ("h6_6", "plant", "front", "Oleander bush", "an oleander bush with pink flowers", ""),
    ("h6_7", "plant", "front", "Marigold bed", "a low bed of orange marigolds", ""),
    ("h7_1", "plant", "front", "Elephant-ear plant", "a big clump of dark green elephant-ear (taro) leaves", ""),
    ("h7_2", "plant", "front", "Tall wild grass", "a clump of tall wild grass with seed heads", ""),
    ("h7_3", "plant", "front", "Banana leaves", "a banana plant's big, tattered leaves", "The painting is cut off at its right edge: draw the whole plant."),
    ("h7_4", "prop", "front", "Broken wall pillar", "a broken old lime-plastered brick wall pillar with weeds at its foot", "It is about 30 cm thick, the same old plaster and brick on every face."),
    ("h7_5", "plant", "front", "Mossy boulder with ferns", "a mossy boulder surrounded by ferns", ""),
]

# The characters and pickups (no cut-out of their own in this list).
CHARACTERS = [
    ("kid", "The kid", ["A0_kid_pattu_frock_front.png", "A0_kid_pattu_frock_left.png",
                         "A0_kid_pattu_frock_right.png", "A0_kid_pattu_frock_back.png"],
     "No new images: her four views exist already. Use them in Meshy as front, left, right and back. (You are "
     "providing her model yourself.)"),
    ("rooster", "The rooster", ["B11_rooster_front.png", "B13_rooster_left.png", "B14_rooster_right.png",
                                 "B12_rooster_back.png"],
     "No new images: his four views exist already (B11 front, B13 left, B14 right, B12 back). Use them in Meshy."),
]
PICKUPS = [
    ("mango", "pickup", None, "Mango", "a ripe mango, golden yellow blushing to red, with a short stalk and one green leaf", ""),
    ("chilli", "pickup", None, "Chilli", "a single bright red chilli with a green cap and a gently curled tip", ""),
    ("feather", "pickup", None, "Golden tail feather", "a single long, curved golden rooster tail feather with a glossy sheen", ""),
]

GUIDE = {
    "building": "Its sides and back are the same building continued: the same walls, plinth, colours and roof all the "
                "way round, a plain back wall with a small window, and the roof's shape seen from the sides.",
    "stall": "From the sides you see its posts, shade, counter and goods in depth; from behind, the backs of the goods "
             "and of the seller, if there is one, under the same shade.",
    "tree": "A tree looks much the same from every side: the same trunk, branches and crown, the crown about as deep "
            "as it is wide.",
    "plant": "It looks much the same from every side and is about as deep as it is wide.",
    "animal": "The front view looks at it head-on and the back view from behind; both side views show the same animal "
              "with matching markings, in the same pose.",
    "person": "The same people, clothes and pose in every view: the front view facing us, the back view from behind, "
              "and both sides.",
    "vehicle": "The front view looks at it from its front end and the back view from behind; both side views show the "
               "same wheels and boards.",
    "prop": "Its sides and back are the same object continued, in the same materials and colours.",
    "round": "It is round, so its four views are much alike; keep every painted detail where it belongs as it turns.",
    "crop": "It is a long, narrow strip of crop about half a metre deep: the front and back views show its whole "
            "length, the side views its narrow ends.",
    "small": "It is a small thing lying on the ground: show it at ground level from the front, both sides and the back.",
    "pickup": "It is a single small object on its own: show the whole of it from every side.",
}
GROUPS = [("lane", "The lane", "Zone 1: houses, shops, the lane's props and obstacles."),
          ("fields", "The fields", "Zone 2: field buildings, crops, the canal and field life."),
          ("market", "The market", "Zone 3: stalls, terrace houses, temple pieces and market props."),
          ("animals", "Animals", "Every animal that stands or sits about in the three zones."),
          ("people", "People", "The villagers going about their day."),
          ("plants", "Trees and plants", "Trees, palms, bushes and the big foreground plants."),
          ("ground", "Ground details", "Small things on the ground. The prints, ruts and cracked mud need no model: "
                                       "they are painted on the ground as they are.")]


def folder_of(name):
    for folder in sorted(p.name for p in CUT.iterdir() if p.is_dir()):
        if (CUT / folder / f"{name}.png").exists():
            return folder
    return None


def shape(name, kind):
    """The sheet's shape: wide things on a landscape sheet, tall things on a portrait one."""
    if kind == "crop":
        return "Landscape 3:2", "16:9 landscape"
    png = CUT / (folder_of(name) or "") / f"{name}.png"
    if not png.exists():
        return "Square 1:1", "1:1 square"
    from PIL import Image
    im = Image.open(png).convert("RGBA")
    box = im.getchannel("A").point(lambda a: 255 if a > 110 else 0).getbbox() or (0, 0, *im.size)
    aspect = (box[2] - box[0]) / max(1, box[3] - box[1])
    if aspect >= 1.35:
        return "Landscape 3:2", "16:9 landscape"
    if aspect <= 0.75:
        return "Portrait 2:3", "9:16 portrait"
    return "Square 1:1", "1:1 square"


GRID = ("Show it four times in a 2 by 2 grid, at exactly the same scale and standing on the same level: top left, the "
        "front view; top right, the left side view (seen from its left, so it faces left); bottom left, the right side "
        "view (seen from its right, so it faces right); bottom right, the back view.")
LOOK = ("Each view is centred in its own quarter with clear space around it, nothing cropped. Orthographic, no "
        "perspective, seen straight on at its own height. Even, flat lighting with no cast shadows. Plain flat "
        "light-grey background everywhere, with no dividing lines, frames, ground plane or labels.")
G_LOOK = ("Centre each view in its own quarter with clear space around it, the whole of it showing. Draw them perfectly "
          "flat and orthographic, like an animation model sheet, seen straight on at their own height and lit evenly "
          "from the front so nothing casts a shadow, on one plain light-grey background. The sheet holds only the four "
          "drawings, unlabeled.")


def view_sentence(view):
    return {"front": "The painting is its front view.",
            "right": "The painting shows its right side (it faces right): that is the right side view, and the front "
                     "view looks at it head-on.",
            "left": "The painting shows its left side (it faces left): that is the left side view, and the front view "
                    "looks at it head-on."}.get(view, "")


def prompts(name, kind, view, what, extra):
    file = f"{name}.jpg"
    shape_c, shape_g = shape(name, kind)
    guide = GUIDE[kind] + (" " + extra if extra else "")
    if view:
        lead_c = (f"Model sheet for 3D modelling of {what}, drawn exactly like the attached painting ({file}): keep its "
                  f"shape, proportions, colours, materials and every painted detail as they are. {view_sentence(view)}")
        lead_g = (f"Model sheet for 3D modelling of {what}, drawn exactly like the painting I've uploaded: keep its "
                  f"shape, proportions, colours, materials and every painted detail as they are. {view_sentence(view)}")
        attach = f"{file} (its painting)"
        g_use = f"Use the image I've uploaded: {file}, the painting of it, to keep its design identical."
    else:
        lead_c = (f"Model sheet for 3D modelling of {what}, in the style of the attached A1 key art.")
        lead_g = (f"Model sheet for 3D modelling of {what}, in the style of the A1 key art I've uploaded.")
        attach = "A1_key_art.png"
        g_use = "Use the image I've uploaded: the A1 key art, as the style to match closely."
    chatgpt = f"{shape_c} image.\n\n{lead_c} {GRID} {guide} {LOOK}\n\n{SETTING}\n\n{SHADES}\n\n{STYLE}"
    gemini = f"Create a {shape_g} image.\n\n{g_use}\n\n{lead_g} {GRID} {guide} {G_LOOK}\n\n{G_SETTING}"
    return {"shape": shape_c, "gshape": shape_g, "attach": attach, "chatgpt": chatgpt, "gemini": gemini}


def records():
    out = []
    names = {a[0] for a in A}
    for folder in sorted(p.name for p in CUT.iterdir() if p.is_dir()):
        if folder in ("kid", "rooster", "textures"):
            continue
        for png in sorted((CUT / folder).glob("*.png")):
            if png.stem.startswith(("mid_", "far_", "ground_earth", "paddy_water", "canal_water")):
                continue
            assert png.stem in names, f"no prompt written for {folder}/{png.stem}"
    for name, kind, view, title, what, extra in A:
        folder = folder_of(name)
        assert folder, name
        group = folder if folder in ("lane", "fields", "market", "animals", "people", "plants", "ground") else "lane"
        rec = {"name": name, "folder": folder, "group": group, "kind": kind, "title": title, "what": what,
               "view": view, "views": f"{name}_views.png", "model": f"{name}.glb"}
        if kind == "flat":
            rec["note"] = "No model needed: it lies flat and is painted on the ground as it is."
        else:
            rec.update(prompts(name, kind, view, what, extra))
            if extra and ("style rules" in extra or "cut off" in extra):
                rec["note"] = extra
        if view:      # the crop strips' pictures are placeholders, not paintings to attach
            rec["ref"] = f"refs/{name}.jpg"
        out.append(rec)
    for name, kind, view, title, what, extra in PICKUPS:
        rec = {"name": name, "folder": "pickups", "group": "characters", "kind": kind, "title": title, "what": what,
               "view": None, "views": f"{name}_views.png", "model": f"{name}.glb"}
        rec.update(prompts(name, kind, view, what, extra))
        rec["note"] = "No painting of it yet: the prompt describes it."
        out.append(rec)
    for name, title, files, note in CHARACTERS:
        out.append({"name": name, "folder": "characters", "group": "characters", "kind": "character", "title": title,
                    "existing": files, "model": f"{name}.glb", "note": note,
                    "ref": f"refs/{files[0].replace('.png', '.jpg')}",
                    "existing_refs": [f"refs/{f.replace('.png', '.jpg')}" for f in files]})
    return out


def markdown(recs):
    lines = ["# Chicken Runner — 3D view prompts (for Meshy)", "",
             "One image per asset: the asset drawn four times in a 2 by 2 grid (front, left side, right side, back), "
             "from its painting, for building its 3D model in Meshy. The web version has each painting to save and "
             "attach, copy buttons, a checklist, and a tool that cuts a finished sheet into the four views Meshy wants.",
             "", "## How to use it", "",
             "1. Attach the asset's painting (`<name>.jpg`; the web version saves it) and paste its prompt.",
             "2. Save the image as `<name>_views.png`. Regenerate it if a view is missing, mirrored wrongly (the left "
             "side view faces left, the right side view faces right), cropped, or has labels or a coloured background.",
             "3. Cut it into `<name>_front.png`, `<name>_left.png`, `<name>_right.png` and `<name>_back.png` (the web "
             "version does this) and give the four to Meshy's multi-image to 3D, each in its slot.",
             "4. Download the model as GLB, named `<name>.glb`, and put it in `ArtSource/models_meshy/<folder>/` "
             "(or upload it in the chat). `finish_models.py` fits it into the game at the painting's size and place.",
             "", "Prints, ruts, cracked mud and kolams need no model: they lie flat on the ground as painted.", ""]
    order = ["characters"] + [g[0] for g in GROUPS]
    names = {"characters": ("Characters and pickups", "The kid and the rooster have their four views already; the "
                                                       "pickups have no painting, so their prompts describe them.")}
    names.update({g[0]: (g[1], g[2]) for g in GROUPS})
    for group in order:
        title, blurb = names[group]
        lines += [f"## {title}", "", blurb, ""]
        for r in [r for r in recs if r["group"] == group]:
            lines += [f"### {r['title']} · `{r['name']}`", ""]
            if r["kind"] == "character":
                lines += [r["note"], "", "Images: " + ", ".join(f"`{f}`" for f in r["existing"]), ""]
                continue
            if r["kind"] == "flat":
                lines += [r["note"], ""]
                continue
            lines += [f"Save as `{r['views']}` · {r['shape']} · Attach: {r['attach']} · Model: "
                      f"`ArtSource/models_meshy/{r['folder']}/{r['model']}`", ""]
            if r.get("note"):
                lines += [f"Note: {r['note']}", ""]
            lines += ["```text", r["chatgpt"], "```", ""]
    return "\n".join(lines)


def main():
    recs = records()
    doc = ROOT / "docs" / "art" / "prompt-sheet-3d.md"
    doc.write_text(markdown(recs))
    print(f"{len(recs)} assets, {sum(1 for r in recs if 'chatgpt' in r)} prompts -> {doc}")
    if SITE:
        from PIL import Image
        (SITE / "refs").mkdir(parents=True, exist_ok=True)
        grey = (217, 219, 222)
        for r in recs:
            sources = []
            if r["kind"] == "character":
                sources = [(REF / f, SITE / ref) for f, ref in zip(r["existing"], r["existing_refs"])]
            elif "ref" in r:
                sources = [(CUT / r["folder"] / f"{r['name']}.png", SITE / r["ref"])]
            for src, dst in sources:
                im = Image.open(src).convert("RGBA")
                im.thumbnail((1024, 1024), Image.LANCZOS)
                bg = Image.new("RGB", im.size, grey)
                bg.paste(im, (0, 0), im)
                bg.save(dst, quality=88)
        (SITE / "data.json").write_text(json.dumps(recs, ensure_ascii=False))
        print("site data written to", SITE)


if __name__ == "__main__":
    main()
