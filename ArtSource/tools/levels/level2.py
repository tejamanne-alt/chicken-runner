"""Level 2, "Washing day": the lane on washing day, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level2.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level2.py --report   # also writes docs/levels/level2.md

Zone 1 again, at a small child's real pace (3.5 m/s against the rooster's 3.2, 290 m, a 7 m start: no basket). The
old design's timing is kept (its distances shrink by 3.5/6), and the road holds only what lies in a village street
on washing day: the women wash at the hand pumps and the water spreads across the road in puddles; the sarees and
dhotis dry on lines inside the yards, behind the road, never across it. Two new things, from the doc's level table:

  * The slide: a roadside neem's low limb across the street, its leaves hanging from 1.6 m down to 0.75 m. Swipe down
    to slide under (the slide is 0.525 m tall and 2.1 m long at 3.5 m/s), or double jump over the top. Seven neems
    along the street, each one a tree, not a row of them.
  * The rope cot, carried out into the sun on washing day: a trampoline. Run into it and she bounces 2.4 m up, landing
    about 2.9 m on, with mangoes along the bounce and a feather above its top for a double jump.

The design: teach the slide first, on its own, then the hand pump's puddle, a neem then hens; then the cot; then
mixes of everything from level 1 with both; the rooster's mischief by the third pump (he knocks the water pots off
their stand into the road); a test of cots, neems and the pump; the lane opens out. Things to jump are about 4 m (a
second and a bit) apart, and every chilli has 11 m or more of clear road after it.
"""
import math

from levelkit import KID_R, Plan, run


def cot(p, s, x):
    """Plan.cot's rope cot, with the mangoes along her bounce and the rooster's own bounce sized for the real pace.
    (The kit still lays them for the old 6 m/s: a 4.8 m arc, where at 3.5 m/s she runs in, bounces off its near end
    2.4 m up and is back on the road 2.9 m on, so half the kit's mangoes hang out of her reach.)"""
    n = len(s["items"])
    p.cot(s, x)
    del s["items"][n + 1:]                      # keep the cot the kit lays; drop its 6 m/s hop and arc
    r, h = p.r, p.r.T["cotBounceHeight"]
    flight = r.RUN * 2 * math.sqrt(2 * r.G * h) / r.G
    p.hop(s, x - 0.4, 3.2, 2.0)                 # the rooster bounces off it too, clear of its frame
    p.arc(s, x - KID_R, flight, h, 5)


def pump_life(p, s, x, woman=None, line=None, pots_side=1.0):
    """Washing day round the hand pump Kit.Puddle stands at x - 0.27, z 1.35: the brass vessels set down beside it to
    be scrubbed, a woman bringing her pot, a line of sarees in the yard behind."""
    p.prop(s, "brass_pots", x + 1.15 * pots_side, 1.75, h=0.45)
    if woman is not None:
        p.prop(s, "woman_carrying_pot", x + woman, 2.0, h=1.95, mirror=woman > 0)
    if line is not None:
        p.prop(s, "clothesline", x + line, 2.7, w=2.4, mirror=line < 0)


def design():
    p = Plan(zone=1, seed=2)

    # ---- the opening: washing day in the lane
    s = p.section("WashingDay", -10.0, 18.0, "Washing day: sarees drying in the yards, the rooster ahead; tap to chase.")
    p.prop(s, "clothesline", -7.0, 2.6, w=2.4)
    p.prop(s, "woman_drawing_kolam", 1.8, 1.9, h=1.0)
    p.decal(s, "kolam_3", 2.3, 0.95, 1.0)
    p.prop(s, "clothesline", 5.6, 2.9, w=2.4, mirror=True)
    p.prop(s, "hen_2", 7.2, 1.4, h=0.42)
    p.mango_line(s, 1.0, 5, 1.2, 0.6)
    p.litter(s, 3)

    # ---- teach (to 82 m): one new thing at a time
    s = p.section("FirstNeem", 8.0, 11.0, "A neem by the road, its low limb across the street: swipe down and slide "
                                          "under; the low mangoes show the way.")
    p.low_branch(s, 14.0)
    p.litter(s, 2, avoid=(14.0,))

    s = p.section("HandPump", 19.0, 9.0, "The hand pump: women wash the clothes there and the water spreads across "
                                         "the road. Hold the jump.")
    p.puddle(s, 23.5)
    pump_life(p, s, 23.5, woman=-2.4, line=3.1)
    p.litter(s, 2, avoid=(23.5,))

    s = p.section("NeemHens", 28.0, 12.0, "Another neem, then two hens pecking in the road: slide, then jump.")
    p.low_branch(s, 31.5)
    p.hens(s, 36.0, 2)
    p.litter(s, 2, avoid=(31.5, 36.0))

    s = p.section("FirstCot", 40.0, 11.0, "A rope cot carried out into the sun: run into it and bounce; a feather "
                                          "above its top for a double jump.")
    cot(p, s, 44.0)
    p.feather(s, 46.1, 4.2, 0)
    p.prop(s, "old_man_on_chair", 41.6, 2.2, h=1.35)
    p.litter(s, 2, avoid=(45.0,))

    s = p.section("Breather", 51.0, 11.0, "A breather: a wave of mangoes and the first chilli.")
    p.chilli(s, 52.0)
    for i in range(8):
        p.mango(s, 53.8 + i * 0.7, 0.8 + 0.4 * math.sin(i * 0.8))
    p.prop(s, "clothesline", 57.5, 2.8, w=2.4)
    p.litter(s, 2)

    s = p.section("NeemGoat", 62.0, 10.0, "A neem's low branch, then a goat kid wandering across.")
    p.low_branch(s, 64.5)
    p.goats(s, 69.0, 1)
    p.prop(s, "goat_eating", 71.2, 2.3, h=0.95)        # its mother, grazing at the road's edge
    p.litter(s, 2, avoid=(64.5, 69.0))

    s = p.section("Sacks", 72.0, 10.0, "Sacks of paddy waiting for the cart: hop onto them and run off the end; "
                                       "a feather above them.")
    p.sacks(s, 75.8)
    p.feather(s, 76.8, 3.4, 1)
    p.litter(s, 2, avoid=(75.8, 77.0))

    # ---- practise (to 168 m): the same things in pairs, about 4 m apart
    s = p.section("CotNeem", 82.0, 13.0, "The cot, then a neem: bounce, land, slide.")
    cot(p, s, 85.5)
    p.low_branch(s, 92.0)
    p.litter(s, 2, avoid=(86.5, 92.0))

    s = p.section("DogDung", 95.0, 11.0, "The dog asleep in the dust, then cow dung.")
    p.dog(s, 99.5)
    p.dung(s, 104.0)
    p.litter(s, 2, avoid=(99.5, 104.0))

    s = p.section("HensPump", 106.0, 14.0, "Two hens, then the second hand pump's puddle.")
    p.hens(s, 111.0, 2)
    p.puddle(s, 116.5)
    pump_life(p, s, 116.5, line=-3.3, pots_side=1.0)
    p.litter(s, 2, avoid=(111.0, 116.5))

    s = p.section("ChilliStraight", 120.0, 13.0, "A chilli and a long straight.")
    p.chilli(s, 121.0)
    p.mango_line(s, 123.0, 12, 0.7, 0.6)
    p.prop(s, "clothesline", 128.5, 2.6, w=2.4, mirror=True)
    p.litter(s, 3)

    s = p.section("CotSand", 133.0, 11.0, "A house going up: the cot, then a heap of building sand after the landing.")
    cot(p, s, 134.0)
    p.sand(s, 141.0)
    p.litter(s, 2, avoid=(135.0, 141.0))

    s = p.section("NeemDung", 144.0, 12.0, "A neem, then dung: slide, tap. A feather over the neem for a double jump.")
    p.low_branch(s, 148.0)
    p.feather(s, 148.0, 3.0, 2)
    p.dung(s, 152.5)
    p.litter(s, 2, avoid=(148.0, 152.5))

    s = p.section("GoatHen", 156.0, 12.0, "A goat kid, then a hen.")
    p.goats(s, 160.0, 1)
    p.hens(s, 164.5, 1)
    p.prop(s, "hen_with_chicks", 166.5, 1.8, h=0.45)
    p.litter(s, 2, avoid=(160.0, 164.5))

    # ---- test (to 290 m)
    s = p.section("Mischief", 168.0, 13.0, "The third pump's puddle; then the rooster knocks the water pots off their "
                                           "stand by the pump into the road.")
    p.puddle(s, 172.5)
    pump_life(p, s, 172.5, woman=-2.6, pots_side=-1.6)
    p.prop(s, "water_pot_stand", 178.3, 1.6, h=1.1)
    p.pots(s, 178.0, hidden=True, ident="knocked")
    p.mischief(s, 178.6, "knocked")
    p.jump_arc(s, 178.0)
    p.litter(s, 2, avoid=(172.5, 178.0))

    s = p.section("CotDogCot", 181.0, 16.0, "Two cots out in the sun with the dog asleep between them: bounce, jump, "
                                            "bounce.")
    cot(p, s, 183.0)
    p.dog(s, 189.5)
    cot(p, s, 193.5)
    p.prop(s, "clothesline", 191.5, 2.9, w=2.4)
    p.litter(s, 2, avoid=(184.0, 189.5, 194.5))

    s = p.section("ChilliLane", 197.0, 15.0, "A breather and a chilli.")
    p.chilli(s, 197.6)
    p.mango_line(s, 199.6, 12, 0.7, 0.6)
    p.litter(s, 3)

    s = p.section("NeemGoatDog", 212.0, 16.0, "A neem, a goat kid, the dog.")
    p.low_branch(s, 215.5)
    p.goats(s, 220.0, 1)
    p.dog(s, 225.0)
    p.litter(s, 2, avoid=(215.5, 220.0, 225.0))

    s = p.section("LastSacks", 228.0, 12.0, "The last sacks, then two hens.")
    p.sacks(s, 231.0)
    p.hens(s, 236.5, 2)
    p.litter(s, 2, avoid=(231.0, 232.2, 236.5))

    s = p.section("FinalChilli", 240.0, 12.0, "The last chilli.")
    p.chilli(s, 240.6)
    p.mango_line(s, 242.6, 12, 0.7, 0.6)
    p.prop(s, "clothesline", 247.0, 2.7, w=2.4, mirror=True)
    p.litter(s, 3)

    s = p.section("LastTest", 252.0, 22.0, "The last pump's puddle, a cot, a neem, dung: everything once more.")
    p.puddle(s, 254.5)
    pump_life(p, s, 254.5, woman=-2.0, line=3.3)
    cot(p, s, 258.5)
    p.low_branch(s, 265.5)
    p.dung(s, 270.0)
    p.litter(s, 2, avoid=(254.5, 259.5, 265.5, 270.0))

    s = p.section("OpenLane", 274.0, 22.0, "The lane opens out: if he is still ahead, he gets away at 290 m.")
    p.mango_line(s, 275.0, 12, 1.0, 0.6)
    p.prop(s, "clothesline", 283.0, 2.8, w=2.4)
    p.litter(s, 3)
    return p


PROSE = [
    "## The opening: washing day",
    "",
    "No basket: the chase starts in the lane with the rooster 7 m ahead (the Ready screen; tap to chase). Sarees and",
    "dhotis dry on lines inside the yards behind the road and a woman draws the morning kolam. A clean run catches him",
    "at about 72 m.",
    "",
    "## Washing day, as it really is",
    "",
    "Nothing hangs across the road. The women wash at the hand pumps, and the water spreads across the road in a",
    "puddle at each of the four pumps (hold the jump); their brass vessels wait beside the pump and the washing dries",
    "on lines in the yards behind. The rope cots are carried out into the sun. The rest is what lies in any village",
    "street: the dog asleep in the dust, cow dung, hens and a goat kid crossing, sacks of paddy waiting for the cart,",
    "a heap of sand where a house is going up. The rooster's mischief is the water pots by the third pump: he knocks",
    "them off their stand into the road.",
    "",
    "## The new things",
    "",
    "* **The neem's low branch** (the slide): seven neems along the street, each with a limb across it, its leaves",
    "  hanging from 1.6 m down to 0.75 m. Swipe down to slide under (2.1 m of slide at 3.5 m/s); the low mangoes show",
    "  the line. A double jump clears the top too (a feather sits over one).",
    "* **The rope cot** (the bounce): run into it for a 2.4 m bounce off its near end, back on the road about 2.9 m on,",
    "  with mangoes along the arc and a feather above its top for a double jump.",
    "",
    "## The shape of it",
    "",
    "Everything runs at a small child's real pace (3.5 m/s); things to jump are about 4 m (a second and a bit) apart.",
    "Teach (to 82 m): a neem alone, the first pump, a neem then hens, the cot, a chilli, a neem then a goat kid, the",
    "sacks. Practise (to 168 m): the cot into a neem, the dog and dung, hens and the second pump, the cot then the sand",
    "heap, a neem then dung, a goat kid and a hen. Test (to 290 m): the rooster's mischief at the third pump,",
    "cot-dog-cot, neem-goat-dog, the last sacks, everything once more at the last pump, then the lane opens out.",
]


def main():
    p = design()
    run(p, {"level": 2, "title": "Washing day", "subtitle": "Swipe down to slide. Bounce on the cot.", "prose": PROSE})


if __name__ == "__main__":
    main()
