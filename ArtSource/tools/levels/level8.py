"""Level 8, "Market day": the weekly market, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level8.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level8.py --report   # also writes docs/levels/level8.md

Zone 3 (8 m/s against 7.4, 700 m, a 12 m start: no basket), along the market's cement road. New, from the doc's level
table: the awnings, crowds of hens and the basket fake-out.

  * Rows of stalls stand at the road's edge, their awnings about 2.1 m up: run on under them, or jump into an awning
    and it bounces her 2 m up, from awning to awning, along a line of mangoes (a feather sits high over one row).
  * Flocks of two or three hens across the road: jump them like a pot stack, or scatter them (a stumble).
  * The hens' basket: jumped like pots; and the fake-out, the rooster knocking a basket into the road behind him.

Clotheslines and pot stacks from the lane come back between the rows. Everything is spaced for 8 m/s: 8 m between
things to jump, and after a row of awnings room for a bounce to come down.
"""
import math

from levelkit import Plan, run

ROWS = [
    ["stall_c_1", "stall_d_2", "stall_e_3"],
    ["stall_f_1", "stall_g_2", "stall_h_1", "stall_flowers"],
    ["stall_vessels", "stall_veg", "stall_c_2"],
    ["stall_sweets", "stall_potter", "stall_d_2"],
    ["stall_g_2", "stall_flowers", "stall_e_3", "stall_f_1"],
    ["stall_veg", "stall_h_1", "stall_c_1"],
]


def stalls(p, s, x, pieces, feather=None):
    """A row of stalls 0.25 m apart from x, mangoes along their awnings; returns where the row ends."""
    start = x
    for piece in pieces:
        x = p.stall(s, x, piece) + 0.25
    end = x - 0.25
    n = int((end - start - 1.0) // 1.1)
    p.mango_line(s, start + 0.6, n, 1.1, 3.4)
    if feather is not None:
        p.feather(s, (start + end) / 2, 4.7, feather)
    return end


def design():
    p = Plan(zone=3, seed=8)

    # ---- the opening: the market gate
    s = p.section("MarketGate", -10.0, 24.0, "The weekly market's cement road: the rooster struts ahead; tap to chase.")
    p.prop(s, "coconut_cart", -5.0, 3.0, h=2.7)
    p.prop(s, "brass_vessels", 1.0, 1.6, h=0.9)
    p.prop(s, "veg_basket", 2.2, 1.4, h=0.6)
    p.prop(s, "bunting", 5.5, 1.6, h=0.7, y=2.4)
    p.prop(s, "hen_with_chicks", 9.5, 1.5, h=0.5)
    p.mango_line(s, 2.0, 5, 2.0, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstStalls", 14.0, 26.0, "The first row of stalls: run under, or jump into an awning and bounce along.")
    stalls(p, s, 18.0, ROWS[0])
    p.litter(s, 2)

    s = p.section("Hens", 40.0, 16.0, "A flock of hens across the road: jump them.")
    p.hens(s, 48.0, 3)
    p.litter(s, 2, avoid=(48.0,))

    s = p.section("Basket", 56.0, 16.0, "The hens' basket: jump it.")
    p.hens_basket(s, 64.0)
    p.litter(s, 2, avoid=(64.0,))

    s = p.section("HighAwnings", 72.0, 30.0, "Four stalls: a feather high over their awnings for a bounce and a double jump.")
    stalls(p, s, 75.0, ROWS[1], feather=0)
    p.litter(s, 2)

    s = p.section("Breather", 102.0, 18.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 103.0)
    for i in range(10):
        p.mango(s, 105.5 + i * 1.3, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 3)

    s = p.section("Clothesline", 120.0, 16.0, "A clothesline across the road: slide.")
    p.clothesline(s, 126.0)
    p.litter(s, 2, avoid=(126.0,))

    s = p.section("PotsBasket", 136.0, 18.0, "Pots, then the hens' basket.")
    p.pots(s, 139.0)
    p.hens_basket(s, 148.0)
    p.litter(s, 2, avoid=(139.0, 148.0))

    # ---- practise
    s = p.section("Flocks", 154.0, 22.0, "Two flocks of hens.")
    p.hens(s, 158.0, 2)
    p.hens(s, 167.0, 3)
    p.feather(s, 167.0, 2.9, 2)
    p.litter(s, 2, avoid=(158.0, 167.0))

    s = p.section("StallsHens", 176.0, 32.0, "A row of stalls, then hens after it.")
    end = stalls(p, s, 179.0, ROWS[2])
    p.hens(s, end + 9.0, 2)
    p.litter(s, 2, avoid=(end + 9.0,))

    s = p.section("ChilliLane", 208.0, 18.0, "A chilli to win back ground.")
    p.chilli(s, 209.0)
    p.mango_line(s, 211.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("ClothesBasketPots", 226.0, 26.0, "Clothesline, the hens' basket, pots.")
    p.clothesline(s, 230.0)
    p.hens_basket(s, 236.0)
    p.pots(s, 245.0)
    p.litter(s, 2, avoid=(230.0, 236.0, 245.0))

    s = p.section("LongAwnings", 252.0, 32.0, "A long row of stalls: bounce along all of them, a feather at the top.")
    stalls(p, s, 255.0, ROWS[3], feather=1)
    p.litter(s, 2)

    # ---- test
    s = p.section("FakeOut", 284.0, 28.0, "Pots; the rooster knocks a hens' basket into the road; a clothesline.")
    p.pots(s, 288.0)
    p.prop(s, "hens_basket", 296.9, 1.4, h=0.55)
    p.hens_basket(s, 296.5, hidden=True, ident="knocked")
    p.mischief(s, 297.5, "knocked")
    p.jump_arc(s, 296.5)
    p.clothesline(s, 306.0)
    p.litter(s, 2, avoid=(288.0, 296.5, 306.0))

    s = p.section("FlocksAwnings", 312.0, 40.0, "Hens, a row of stalls, hens.")
    p.hens(s, 316.0, 3)
    end = stalls(p, s, 321.0, ROWS[4])
    p.hens(s, end + 9.0, 2)
    p.litter(s, 2, avoid=(316.0, end + 9.0))

    s = p.section("ChilliStraight", 352.0, 18.0, "A chilli and a long straight.")
    p.chilli(s, 353.0)
    p.mango_line(s, 355.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("CrowdedRoad", 370.0, 36.0, "Hens, pots, a clothesline, the hens' basket.")
    p.hens(s, 374.0, 2)
    p.pots(s, 382.0)
    p.clothesline(s, 391.0)
    p.hens_basket(s, 397.0)
    p.litter(s, 2, avoid=(374.0, 382.0, 391.0, 397.0))

    s = p.section("LastAwnings", 406.0, 34.0, "The last row of stalls.")
    stalls(p, s, 409.0, ROWS[5])
    p.litter(s, 2)

    s = p.section("FinalChilli", 440.0, 18.0, "The last chilli.")
    p.chilli(s, 441.0)
    p.mango_line(s, 443.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("LastTest", 458.0, 44.0, "Hens, a clothesline, pots, the hens' basket, hens: everything once more.")
    p.hens(s, 462.0, 3)
    p.clothesline(s, 471.0)
    p.pots(s, 477.0)
    p.hens_basket(s, 485.0)
    p.hens(s, 494.0, 2)
    p.litter(s, 2, avoid=(462.0, 471.0, 477.0, 485.0, 494.0))

    s = p.section("StallsAgain", 502.0, 36.0, "Stalls, then a flock after them.")
    end = stalls(p, s, 505.0, ROWS[1])
    p.hens(s, end + 9.0, 3)
    p.litter(s, 2, avoid=(end + 9.0,))

    s = p.section("ChilliLane2", 538.0, 18.0, "A chilli.")
    p.chilli(s, 539.0)
    p.mango_line(s, 541.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("BasketsPots", 556.0, 34.0, "Two hens' baskets, pots, a clothesline.")
    p.hens_basket(s, 560.0)
    p.hens_basket(s, 568.0)
    p.pots(s, 576.0)
    p.clothesline(s, 585.0)
    p.litter(s, 2, avoid=(560.0, 568.0, 576.0, 585.0))

    s = p.section("LastRow", 590.0, 36.0, "One more row of stalls.")
    stalls(p, s, 593.0, ROWS[2])
    p.litter(s, 2)

    s = p.section("MarketEnd", 626.0, 80.0, "The market thins out: if he is still ahead, he gets away at 700 m.")
    p.hens(s, 634.0, 2)
    p.mango_line(s, 640.0, 16, 1.4, 0.6)
    p.prop(s, "coconut_cart", 668.0, 3.0, h=2.7, mirror=True)
    p.prop(s, "brass_vessels", 684.0, 1.6, h=0.9)
    p.litter(s, 6, avoid=(634.0,))
    return p


PROSE = [
    "## The opening: the market gate",
    "",
    "No basket: the chase starts on the market's cement road with the rooster 12 m ahead (the Ready screen; tap to",
    "chase). A clean run catches him at about 149 m.",
    "",
    "## The new things",
    "",
    "* **Awnings:** rows of stalls at the road's edge, awnings about 2.1 m up. Run under them, or jump into one for a",
    "  2 m bounce, from awning to awning along a line of mangoes (feathers sit high over two rows).",
    "* **Flocks of hens** across the road: jump them, or scatter them (a stumble).",
    "* **The hens' basket**, jumped like pots, and the fake-out: the rooster knocks one into the road behind him.",
    "",
    "## The shape of it",
    "",
    "Teach (to 154 m): stalls, hens, the basket, stalls with a feather, a chilli, a clothesline, pots and a basket.",
    "Practise (to 284 m): flocks, stalls then hens, the basket among pots, a long row of awnings. Test (to 700 m): the",
    "fake-out, flocks and awnings, a crowded road, the last rows, everything once more, then the market thins out.",
]


def main():
    p = design()
    run(p, {"level": 8, "title": "Market day", "subtitle": "Bounce across the awnings.", "prose": PROSE})


if __name__ == "__main__":
    main()
