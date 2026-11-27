"""Section P: the Pongal repaint. One edit prompt per painting in the game: keep the painting exactly as it is (so the
cut-outs and the hand-built models traced from it still fit) and add the festival's touches in the same style."""

KEY = "P"
NAME = "Pongal: the festive repaint"
BLURB = ("The whole village is celebrating Pongal, the harvest festival. Each prompt below edits a painting you have "
         "already made: it keeps the picture exactly as it is, so its cut-outs and the Blender models traced from it "
         "still fit, and adds the festival in the same painted style: mango-leaf thoranams over the doors, marigold "
         "garlands, coloured Pongal kolams, tall sugarcane stalks, new clay Pongal pots boiling over on brick hearths "
         "with a turmeric plant tied round their necks, cattle with painted horns, bells and garlands, new festival "
         "clothes, bunting and kites. Gemini keeps the rest of a picture best: use it for these edits.")

HOWTO = [
    "Attach the painting named in the prompt, from <code>ArtSource/references/</code> (it is the image you made before).",
    "Paste the prompt. Gemini keeps everything else in place best; in ChatGPT, use its edit mode on the attached image.",
    "Check it against the old one (flip between the two): nothing may move, grow, shrink or disappear; only the "
    "festival touches are new. If something moved, reply: <i>Put the … back exactly where it is in the image I "
    "uploaded, and keep the decorations.</i>",
    "Save it under the <b>same file name</b>, replacing the old painting (the old one stays in the repo's history), "
    "and put it in <code>ArtSource/references/</code> or upload it here, in batches. Start with A1, then the lane (C, "
    "G, K), the fields (D), the market and temple (E), the people and animals (B) and the story (F).",
    "I then cut the pieces out again and add the new decorations to each Blender model as real parts: thoranams as "
    "hanging leaf strings, sugarcane, pots on hearths and garlands modelled, the kolams and painted horns as the "
    "painting itself.",
]

NOTHING_MODERN = ("Everything belongs to a Tamil village of the 1970s: no plastic, balloons, printed banners, electric "
                  "lights, fireworks or text.")
KEEP = {
    "scene": ("Keep everything in it exactly as it is: the same composition and framing, every building, object, "
              "person and animal in the same place, at the same size and in the same shape, and the same painted "
              "style, colours and light."),
    "sheet": ("Keep everything in it exactly as it is: every piece in the same place, at the same size and in the same "
              "shape, the same gaps between the pieces, the same painted style and colours, and the same plain "
              "light-grey background."),
    "layer": ("Keep everything in it exactly as it is: every shape in the same place, at the same size and in the same "
              "outline, the same painted style, colours and haze, and the same flat magenta background."),
    "dark": ("Keep the six designs exactly where they are, at the same size and with the same white outlines, on the "
             "same flat dark-grey background."),
    "people": ("Keep every figure exactly as it is: the same faces, bodies, poses, expressions and places on the "
               "sheet, the same painted style and the same plain light-grey background; change only what is "
               "described here."),
}
ADD = "Add only these Pongal festival touches, painted in the same style and light as the rest:"

# Things every house front gets.
DOOR = ("a string of fresh mango leaves (a thoranam) hung across the top of the door frame, a marigold garland swagged "
        "over the door, a bright Pongal kolam on the ground in front of the door, drawn in white rice flour and filled "
        "with red, yellow, green and pink powder, with a little Pongal pot and two sugarcane stalks in its middle, and "
        "a pair of tall sugarcane stalks with their leaves on, leaning against the wall beside the door")
POT = ("a new clay Pongal pot, painted with white lime stripes and red kumkum dots and with a turmeric plant tied round "
       "its neck, boiling over with white froth on a small hearth of three bricks with a few sticks burning under it")
STALL = ("a string of mango leaves along the front edge of every awning or shade, a marigold garland tied round each "
         "front pole, a few tall sugarcane stalks tied upright to the poles, and a small coloured Pongal kolam on the "
         "ground in front of each stall")
CATTLE = ("horns painted in bright bands of red, blue and green with shining brass tips, a marigold garland and a "
          "string of brass bells round the neck, and a red kumkum dot on the forehead")
KITES = "a few diamond-shaped paper kites with long tails high in the sky"
BUNTING = "strings of small triangular cloth bunting in red, yellow, green and blue strung across overhead"

# (original id, how to keep it, what to add)
EDITS = [
    ("A1", "scene", f"on every house {DOOR}; in front of one house, {POT}; {BUNTING} the lane; {KITES}. Keep the "
                    "toddler and the rooster exactly as they are."),
    ("A2", "scene", "in the lane panels, mango-leaf thoranams over the doors, coloured kolams and bunting across the "
                    "lane; in a yard, a Pongal pot boiling over on a brick hearth beside sugarcane stalks; in the "
                    "field panels, cattle with brightly painted horns and garlands and sheaves of harvested paddy; "
                    "over the rooftops, paper kites; at the market and the temple, more marigold garlands, sugarcane "
                    "bundles and oil lamps."),
    ("B5", "people", "dress him for Pongal: a crisp new white veshti with a thin gold border instead of the checked "
                     "lungi, a new white cotton shirt over the vest, a white sandal-paste stripe and a red kumkum dot "
                     "on his forehead, and a small marigold garland round his neck in the standing views."),
    ("B6", "people", "dress her for Pongal: a new silk saree in turmeric yellow with a broad magenta and gold border "
                     "instead of the cotton one, a thicker string of jasmine round her bun, small gold earrings, a few "
                     "more glass bangles, and a red kumkum dot with a little turmeric on her forehead."),
    ("B7", "people", f"the pair of white bullocks dressed for Mattu Pongal: {CATTLE}; the water buffalo with its horns "
                     "painted red and a marigold garland round its neck. Leave the dog and the hens as they are."),
    ("B8", "people", f"the white cow dressed for Mattu Pongal: {CATTLE}; the calf with a small marigold garland and one "
                     "brass bell; the standing buffalo with its horns painted red and a garland round its neck. Leave "
                     "the goats as they are."),
    ("B10", "people", "everyone in new, brighter Pongal clothes (new cotton and silk saris, crisp white veshtis); the "
                      "woman drawing a kolam now draws a big coloured Pongal kolam with red, yellow and green powder; "
                      "the woman with the water pot carries a new clay Pongal pot with a turmeric plant tied round its "
                      "neck; the vegetable seller's cart is heaped with sugarcane stalks, turmeric plants and bananas; "
                      "the milkman has two sugarcane stalks tied along his bicycle."),
    ("C1", "scene", f"on every house {DOOR}; in front of one house, {POT}; {BUNTING} the lane; {KITES}."),
    ("C2", "scene", f"{KITES}, and a long string of bunting hanging from the distant temple tower."),
    ("C3", "layer", "strings of small triangular cloth bunting between the roofs, mango-leaf thoranams under the eaves "
                    "where a doorway shows, and two paper kites flying just above the roofs, inside the cut-out."),
    ("C4", "sheet", f"on each of the four houses {DOOR}; in front of the lime-white house's door, {POT}."),
    ("C5", "sheet", "the top pot of the clay pot stack decorated as a Pongal pot, painted with white lime stripes and "
                    "red kumkum dots, with a turmeric plant tied round its neck; a marigold garland hung on the hand "
                    "pump; two sugarcane stalks tied along the bicycle's carrier; a marigold garland and a sprig of "
                    "mango leaves on the tulsi planter, with a small coloured kolam on its pedestal; a turmeric smear "
                    "and red kumkum dots on the necks of the brass water pots. Leave the dung and the cot as they are."),
    ("C6", "sheet", "the bullock cart's wheels and frame painted with turmeric-yellow and kumkum-red stripes, with two "
                    "sugarcane stalks and a bunch of mango leaves tied to it; new bright silk sarees on the clothesline; "
                    "two sugarcane stalks and a turmeric plant leaning on the jute sacks; the doorway's mango-leaf "
                    "garland fresher, with a marigold garland too and a coloured kolam at its step; fresh turmeric and "
                    "kumkum on the shrine stone with a lit clay lamp before it; a turmeric plant tied round the neck "
                    "of the pot on the stand. Leave the chicken basket as it is."),
    ("C7", "dark", "make all six into Pongal kolams: fill the white line designs with bright coloured powder (red, "
                   "yellow, green, pink and orange), and work a small Pongal pot with sugarcane stalks, or a rising "
                   "sun, into the middle of three of them."),
    ("C8", "layer", "strings of small triangular cloth bunting between the roofs, mango-leaf thoranams under the eaves "
                    "where a doorway shows, and a thin wisp of smoke from a Pongal hearth behind one house."),
    ("C9", "layer", "a string of bunting and a marigold garland on the tiny white shrine, mango-leaf thoranams under "
                    "the thatched eaves, and two paper kites caught high in the tamarind tree."),
    ("D1", "scene", f"sheaves of harvested paddy stacked along the bund; the scarecrow wearing a marigold garland and a "
                    f"new bright towel round its neck; a pair of grazing bullocks by the well with {CATTLE}; beside the "
                    f"farmhouse, {POT} and two sugarcane stalks; a mango-leaf thoranam and a marigold garland on the "
                    f"well's pulley frame; {KITES}."),
    ("D2", "scene", f"{KITES}."),
    ("D3", "sheet", "a small marigold garland round the top of the haystack; a mango-leaf thoranam and a marigold "
                    "garland on the well's pulley frame, with turmeric and kumkum dots on the well's stone rim; the "
                    "scarecrow wearing a marigold garland and a new bright towel round its neck; a mango-leaf "
                    "thoranam across the sluice gate's frame; a small coloured kolam on the bund path. Leave the canal "
                    "and plank bridge as they are."),
    ("D5", "sheet", f"a mango-leaf thoranam over the pump house door, with turmeric and kumkum dots on its wall; at the "
                    f"farmer's hut {DOOR}, and beside its cattle pen {POT}; a marigold garland and turmeric and kumkum "
                    f"dots on the granary's posts; the shrine with fresh marigold garlands, a lit clay lamp and a new "
                    f"red flag."),
    ("D7", "layer", "mango-leaf thoranams on the farmhouse doors, a thin wisp of smoke from a Pongal hearth in each "
                    "farmhouse yard, and a few cut paddy sheaves stacked on the bund."),
    ("D8", "sheet", f"the kavalai's bullocks with {CATTLE}; a mango-leaf thoranam across the well's pulley frame; a "
                    f"thoranam on the watch hut's ladder; at the threshing floor, a coloured kolam beside the paddy "
                    f"heaps and {POT}, with two sugarcane stalks beside it."),
    ("D9", "sheet", "a marigold garland and a turmeric and kumkum mark on the picottah's post; a turmeric plant tied "
                    "round the neck of the brass pot on the washing steps; a mango-leaf thoranam across the sluice "
                    "gate's frame. Leave the slab bridge as it is."),
    ("D10", "people", f"the ploughing bullocks and the kavalai bullocks with {CATTLE}; the three women in new bright "
                      "saris; small marigold garlands on the herd boy's goats; the wallowing buffalo with its horns "
                      "painted red; the farmer carrying a bundle of cut paddy with two sugarcane stalks."),
    ("D13", "layer", "the grazing cattle with brightly painted horns, mango-leaf thoranams on the hut doors, thin wisps "
                     "of smoke from Pongal hearths in the hamlet, and two paper kites just above the palms."),
    ("E1", "scene", f"more paper kites in the sunset sky; on one terrace, {POT}, with two sugarcane stalks; mango-leaf "
                    "thoranams over the doors up to the roofs; coloured kolams on the terraces."),
    ("E2", "scene", f"tall bundles of sugarcane standing upright at the stalls; turmeric plants and new clay Pongal "
                    f"pots for sale; more marigold garlands; {STALL}; {BUNTING} the market."),
    ("E3", "scene", f"a big coloured Pongal kolam on the bottom step; tall sugarcane stalks tied either side of the "
                    f"temple gateway, with mango-leaf thoranams across it; beside the steps, {POT}; more marigold "
                    f"garlands on the bells."),
    ("E4", "sheet", "the big clay water pot painted with white lime stripes and red kumkum dots, with a turmeric plant "
                    "tied round its neck; more colours in the bunting. Leave the parapet, the mats and the kite as "
                    "they are."),
    ("E5", "sheet", f"on both stalls under the indigo awning and on the flower stall, {STALL}; a coloured kolam and a "
                    f"marigold garland on the temple step segment. Leave the baskets, vessels and lantern as they are."),
    ("E6", "sheet", f"on both houses {DOOR}; in front of the first house, {POT}; strings of small triangular cloth "
                    f"bunting along the roof parapets."),
    ("E7", "sheet", f"on both houses {DOOR}; on the first house's terrace, beside the drying mats, {POT}; strings of "
                    f"small triangular cloth bunting along the roof parapets."),
    ("E8", "sheet", f"{STALL}; bunches of turmeric plants and ginger among the vegetables; more marigold and jasmine "
                    f"garlands at the flower seller's."),
    ("E9", "sheet", f"{STALL}; the coconut cart's bullocks with {CATTLE}; the potter's new pots painted with white lime "
                    f"stripes and red kumkum dots, some with turmeric plants tied round their necks, for Pongal."),
    ("E10", "sheet", "mango-leaf thoranams strung between the mandapam's pillars and marigold garlands round them, "
                     "with lit clay lamps on the plinth; a thoranam across the chariot shed's front and sugarcane "
                     "stalks tied either side; lit lamps and a coloured kolam on the temple tank's steps."),
    ("E11", "sheet", f"{STALL}; bunches of turmeric plants for sale beside the spice seller's heaps."),
    ("E12", "sheet", f"{STALL}; a few sugarcane pieces and bananas beside the jaggery blocks."),
    ("E13", "sheet", f"{STALL}; bunches of turmeric plants and sugarcane stalks among the vegetables."),
    ("E14", "sheet", f"{STALL}; a taller bundle of sugarcane at the juice seller's, and a tray of sweet Pongal in a "
                     f"brass dish among the sweets."),
    ("E15", "sheet", f"{STALL}; more garlands and bowls of turmeric and kumkum at the bangle seller's."),
    ("E16", "sheet", f"{STALL}."),
    ("E17", "sheet", f"{STALL}; the cattle-fair seller's horn caps in brighter colours, with strings of brass bells "
                     f"and coloured tassels for Mattu Pongal."),
    ("E18", "sheet", f"{STALL}; a few banana leaves of sweet Pongal beside the idlis."),
    ("F1", "scene", "a coloured Pongal kolam on the ground instead of the white one, a mango-leaf thoranam over the "
                    "yard's gate, sugarcane stalks leaning on the low wall, and in the background a Pongal pot "
                    "boiling over on a brick hearth."),
    ("F2", "scene", "a coloured Pongal kolam on the doorstep, a mango-leaf thoranam over the door, two sugarcane "
                    "stalks leaning beside it, and a mango-leaf thoranam over the neighbour's kitchen window."),
    ("F3", "scene", "a coloured Pongal kolam in the yard, a mango-leaf thoranam over the yard's gate, sugarcane stalks "
                    "leaning on the wall, and a marigold garland on the tree's trunk."),
    ("F4", "scene", "the edge of a coloured Pongal kolam on the ground and a few marigold petals scattered there."),
    ("F5", "scene", "the coloured Pongal kolam in the yard scattered by the rooster in puffs of coloured powder, and a "
                    "sugarcane stalk toppling against the wall."),
    ("F6", "scene", "a puff of coloured kolam powder rising where the toddler lands, and a few marigold petals in "
                    "the air."),
    ("F7", "scene", "strings of triangular cloth bunting along the parapet and paper kites in the sunset sky."),
    ("F8", "scene", "a Pongal feast: a brass pot of sweet Pongal on the stove, pieces of sugarcane and bananas on "
                    "banana leaves on the floor, a mango-leaf thoranam over the kitchen door and a coloured kolam by "
                    "the stove."),
    ("G1", "sheet", f"{DOOR}; beside the door, {POT}."),
    ("G2", "sheet", f"{DOOR}; marigold garlands round the porch posts; beside the porch, {POT}."),
    ("G3", "sheet", f"{DOOR}."),
    ("G4", "sheet", f"{DOOR}; a new bright saree as the door curtain."),
    ("G5", "sheet", f"{DOOR}, with more thoranams strung between the veranda pillars and marigold garlands round every "
                    f"pillar; the brass lamp by the door lit; in front of the steps, {POT}, in brass, larger than "
                    f"the others."),
    ("G6", "sheet", f"over the courtyard gate and at it, {DOOR.replace('the door frame', 'the gate').replace('over the door', 'over the gate').replace('in front of the door', 'in front of the gate').replace('beside the door', 'beside the gate')}."),
    ("G7", "sheet", "a string of mango leaves along the awning's edge, a marigold garland on the signboard, bundles of "
                    "sugarcane for sale leaning against the bench, bunches of turmeric plants hanging with the snacks, "
                    "and a coloured kolam in front."),
    ("G8", "sheet", "a string of mango leaves along the thatch's edge, a marigold garland on the kettle's shelf, two "
                    "sugarcane stalks leaning beside the bench, and a coloured kolam in front."),
    ("G9", "sheet", "a string of mango leaves along the awning's edge, new bright festival blouses and a silk saree "
                    "hung up at the tailor's, a marigold garland on the sewing machine and on the cycle pump, and a "
                    "coloured kolam in front of each shop."),
    ("G10", "sheet", f"{DOOR}; at the front, rows of new Pongal pots painted with white lime stripes and red kumkum "
                     f"dots, some with turmeric plants tied round their necks; a mango-leaf thoranam along the work "
                     f"shed's eave."),
    ("G11", "sheet", f"{DOOR}; a finished magenta silk saree hung up beside the door."),
    ("G12", "sheet", "a mango-leaf thoranam and a marigold garland on the standing door frame, and a small coloured "
                     "kolam on the ground before it (the blessing for a new house)."),
    ("G13", "sheet", f"for Mattu Pongal, the calf with its small horns painted red and green, a marigold garland and a "
                     f"brass bell; a mango-leaf thoranam along the shed's eave; turmeric and kumkum dots on the posts; "
                     f"two sugarcane stalks tied to the front posts; a coloured kolam in front."),
    ("G14", "sheet", "mango-leaf thoranams along the veranda, marigold garlands round the pillars, two sugarcane "
                     "stalks either side of the steps, a coloured kolam in front, and a string of triangular cloth "
                     "bunting along the roof."),
    ("G15", "sheet", f"more marigold garlands, every oil lamp lit, two sugarcane stalks tied either side of the "
                     f"entrance, a coloured kolam in front, and beside it {POT}."),
    ("G16", "sheet", "a small flame lit on every lamp ledge, more marigold garlands at its foot, two sugarcane stalks "
                     "tied either side of the base, and a coloured kolam round the base."),
    ("H3", "sheet", "fresh marigold garlands on the stone idols, the clay lamps lit, two sugarcane stalks leaning on "
                    "the platform, and a coloured kolam on the ground in front of it."),
    ("K1", "sheet", "a string of fresh mango leaves across the top of every door, and marigold garlands on the carved "
                    "double door and the blue plank door."),
    ("K3", "sheet", f"the kolams on the three front steps filled with bright red, yellow, green and pink powder; the "
                    f"mango-leaf garland fresher; and, as one more separate piece at the end of the row, {POT}, with "
                    f"two sugarcane stalks beside it."),
]
UNCHANGED = ("Left as they are: A0 and the kid sheets, the rooster (B1-B4, B11-B14), B9's small animals, the far "
             "trees and plants (D4, D6, D11, D12, H1, H2, H4-H7), the ground details (C10), K2's roof edges, the "
             "textures (T) and the 3D textures (M): there is nothing on them to celebrate, or they are not seen in the "
             "festival's scenes.")


def entries(prompts):
    """The P section's entries, in the page's prompt format, from the original prompts (by id)."""
    by_id = {p["id"]: p for p in prompts}
    out = []
    for i, (orig, kind, adds) in enumerate(EDITS, 1):
        p = by_id[orig]
        keep = KEEP[kind]
        c = (f"{p['aspect']} image, the same shape as the attached one.\n\nEdit the attached image ({p['file']}) so it "
             f"shows the village on Pongal, the harvest festival. {keep}\n\n{ADD} {adds}\n\n{NOTHING_MODERN}")
        g = (f"Edit the image I've uploaded ({p['file']}) so it shows the village on Pongal, the harvest festival. "
             f"{keep}\n\n{ADD} {adds}\n\n{NOTHING_MODERN} Keep the image's shape and size.")
        out.append({"id": f"P{i}", "orig": orig, "title": f"{orig} · {p['title']}", "file": p["file"],
                    "aspect": p["aspect"], "gshape": "same shape as the uploaded image", "batch": 1,
                    "attach": p["file"], "use": f"Replaces {orig} ({p['title']}): {p['use']}",
                    "prompt": adds, "text": c, "gtext": g, "block": "style"})
    return out
