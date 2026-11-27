"""Level 2, "Washing day": the lane on washing day, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level2.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level2.py --report   # also writes docs/levels/level2.md

Zone 1 again (6 m/s against 5.5, 500 m, a 12 m start: no basket). Two new things, from the doc's level table:

  * The slide: clotheslines of sarees across the lane from 0.7 m down to 1.6 m up. Swipe down to slide under (the slide
    is 0.525 m tall and 3.6 m long at 6 m/s), or double jump over the top for a feather.
  * The rope cot: a trampoline. Run into it and she bounces 2.4 m up, landing about 5 m on, with mangoes along the
    bounce and a feather at its top for a double jump.

The design: teach the slide first, on its own, then two lines in rhythm; then the cot; then mixes of everything from
level 1 with both; the rooster's mischief by the water pots; a test of lines, cots and pots; the lane opens out.
"""
import math

from levelkit import Plan, run


def design():
    p = Plan(zone=1, seed=2)

    # ---- the opening: washing day in the lane
    s = p.section("WashingYard", -10.0, 24.0, "Washing day: sarees drying behind the lane, the rooster ahead; tap to chase.")
    p.prop(s, "clothesline", -6.5, 2.2, w=2.2)
    p.prop(s, "clothesline", 4.5, 2.6, w=2.2, mirror=True)
    p.prop(s, "woman_drawing_kolam", -2.5, 1.9, h=1.2)
    p.decal(s, "kolam_3", -2.0, 0.9, 1.0)
    p.prop(s, "water_pot_stand", 9.0, 1.7, h=1.1)
    p.prop(s, "hen_2", 11.5, 1.3, h=0.42)
    p.mango_line(s, 2.0, 5, 2.0, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstLine", 14.0, 18.0, "The first clothesline: swipe down and slide under; the low mangoes show the way.")
    p.clothesline(s, 24.0)
    p.litter(s, 2, avoid=(24.0,))

    s = p.section("Pots", 32.0, 16.0, "A pot stack: the jump again.")
    p.pots(s, 40.0)
    p.litter(s, 2, avoid=(40.0,))

    s = p.section("TwoLines", 48.0, 20.0, "Two clotheslines 8 m apart: slide, up, slide.")
    p.clothesline(s, 54.0)
    p.clothesline(s, 62.0)
    p.litter(s, 2, avoid=(54.0, 62.0))

    s = p.section("FirstCot", 68.0, 22.0, "The rope cot: run into it and bounce; a feather at the top for a double jump.")
    p.cot(s, 76.0)
    p.feather(s, 78.8, 4.3, 0)
    p.prop(s, "old_man_on_chair", 73.0, 2.2, h=1.25)
    p.litter(s, 2, avoid=(77.0,))

    s = p.section("Breather", 90.0, 16.0, "A breather: a wave of mangoes and the first chilli.")
    p.chilli(s, 91.0)
    for i in range(9):
        p.mango(s, 93.0 + i * 1.2, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 3)

    s = p.section("LinePots", 106.0, 20.0, "A clothesline, then a pot stack: slide, then jump.")
    p.clothesline(s, 111.0)
    p.pots(s, 119.0)
    p.litter(s, 2, avoid=(111.0, 119.0))

    s = p.section("Cart", 126.0, 20.0, "The bullock cart: onto its bed and off; a feather above it.")
    p.cart(s, 130.0)
    p.feather(s, 134.2, 3.4, 1)
    p.litter(s, 2, avoid=(130.0, 132.0))

    # ---- practise
    s = p.section("CotLine", 146.0, 22.0, "The cot, then a clothesline: bounce, land, slide.")
    p.cot(s, 149.0)
    p.clothesline(s, 162.0)
    p.litter(s, 2, avoid=(150.0, 162.0))

    s = p.section("DogLine", 168.0, 20.0, "The sleeping dog, then a clothesline.")
    p.dog(s, 172.5)
    p.clothesline(s, 182.0)
    p.litter(s, 2, avoid=(172.5, 182.0))

    s = p.section("LinePuddle", 188.0, 22.0, "A clothesline, then the hand-pump puddle.")
    p.clothesline(s, 192.0)
    p.puddle(s, 201.5)
    p.litter(s, 2, avoid=(192.0, 201.5))

    s = p.section("ChilliStraight", 210.0, 18.0, "A chilli and a long straight.")
    p.chilli(s, 211.0)
    p.mango_line(s, 213.5, 10, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("CotPots", 228.0, 20.0, "The cot, then a pot stack after the landing.")
    p.cot(s, 231.0)
    p.pots(s, 243.0)
    p.litter(s, 2, avoid=(232.0, 243.0))

    s = p.section("ThreeLines", 248.0, 26.0, "Three clotheslines in a row: slide, slide, slide. A feather over the middle one.")
    p.clothesline(s, 252.0)
    p.clothesline(s, 260.0)
    p.feather(s, 260.0, 2.9, 2)
    p.clothesline(s, 268.0)
    p.litter(s, 2, avoid=(252.0, 260.0, 268.0))

    s = p.section("DungPots", 274.0, 18.0, "Dung, then pots: tap, jump.")
    p.dung(s, 279.0)
    p.pots(s, 286.0)
    p.litter(s, 2, avoid=(279.0, 286.0))

    # ---- test
    s = p.section("Mischief", 292.0, 26.0, "The puddle; the rooster knocks the pots off their stand; a clothesline after.")
    p.puddle(s, 296.0)
    p.prop(s, "water_pot_stand", 306.3, 1.6, h=1.1)
    p.pots(s, 306.0, hidden=True, ident="knocked")
    p.mischief(s, 307.0, "knocked")
    p.jump_arc(s, 306.0)
    p.clothesline(s, 314.0)
    p.litter(s, 2, avoid=(296.0, 306.0, 314.0))

    s = p.section("CotLineCot", 318.0, 30.0, "Cot, clothesline, cot.")
    p.cot(s, 321.0)
    p.clothesline(s, 333.0)
    p.cot(s, 339.0)
    p.litter(s, 2, avoid=(322.0, 333.0, 340.0))

    s = p.section("ChilliLane", 348.0, 18.0, "A breather and a chilli.")
    p.chilli(s, 349.0)
    p.mango_line(s, 351.5, 9, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("LineDogLine", 366.0, 26.0, "Clothesline, dog, clothesline.")
    p.clothesline(s, 370.0)
    p.dog(s, 378.0)
    p.clothesline(s, 387.0)
    p.litter(s, 2, avoid=(370.0, 378.0, 387.0))

    s = p.section("LastCart", 392.0, 22.0, "The last cart, and pots after it.")
    p.cart(s, 396.0)
    p.pots(s, 406.0)
    p.litter(s, 2, avoid=(396.0, 398.0, 406.0))

    s = p.section("FinalChilli", 414.0, 18.0, "The last chilli.")
    p.chilli(s, 415.0)
    p.mango_line(s, 417.5, 9, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("LastTest", 432.0, 40.0, "Clothesline, pots, the cot, a clothesline, dung: everything once more.")
    p.clothesline(s, 436.0)
    p.pots(s, 443.0)
    p.cot(s, 449.0)
    p.clothesline(s, 461.0)
    p.dung(s, 468.0)
    p.litter(s, 2, avoid=(436.0, 443.0, 450.0, 461.0, 468.0))

    s = p.section("OpenLane", 472.0, 34.0, "The lane opens out: if he is still ahead, he gets away at 500 m.")
    p.mango_line(s, 474.0, 12, 1.4, 0.6)
    p.prop(s, "clothesline", 486.0, 2.4, w=2.2)
    p.litter(s, 4)
    return p


PROSE = [
    "## The opening: washing day",
    "",
    "No basket: the chase starts in the lane with the rooster 12 m ahead (the Ready screen; tap to chase). Sarees dry",
    "on lines behind the lane and a woman draws the morning kolam. A clean run catches him at about 110 m.",
    "",
    "## The new things",
    "",
    "* **Clotheslines** (the slide): sarees across the lane from 0.7 m down to 1.6 m up. Swipe down to slide under; the",
    "  low mangoes show the line. A double jump clears the top too (a feather sits over one).",
    "* **The rope cot** (the bounce): run into it for a 2.4 m bounce, landing about 5 m on, with mangoes along the arc",
    "  and a feather at its top.",
    "",
    "## The shape of it",
    "",
    "Teach (to 146 m): the slide alone, then in rhythm, the cot, a chilli, a line then pots, the cart. Practise (to",
    "292 m): the cot into a line, lines with the dog, the puddle and pots, three lines in a row. Test (to 500 m): the",
    "rooster's mischief, cot-line-cot, line-dog-line, the last cart, everything once more, then the lane opens out.",
]


def main():
    p = design()
    run(p, {"level": 2, "title": "Washing day", "subtitle": "Swipe down to slide. Bounce on the cot.", "prose": PROSE})


if __name__ == "__main__":
    main()
