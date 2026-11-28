"""Level 8, "Market day": the weekly market, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level8.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level8.py --report   # also writes docs/levels/level8.md

Zone 3, along the market's cement road: the kid runs at a small child's real pace, 3.5 m/s, against the rooster's
3.15; the course is 300 m and the chase starts 7 m behind him (no basket), so a clean run catches him at about 62 m.
New, from the doc's level table: the awnings, the vendors' hens and the basket fake-out.

  * Rows of two or three stalls stand at the road's edge, their awnings about 2.1 m up: run on under them, or jump
    into an awning and it bounces her 2 m up, from awning to awning (a bounce carries her about 2.6 m, so she meets
    every stall), along a line of mangoes; feathers sit high over two rows.
  * The vendors' hens loose in the road, one or two at a time (three abreast is more than a small child clears): jump
    them, or scatter them (a stumble). Their baskets stand in the road too: jumped like a pot stack.
  * The fake-out: the rooster knocks a hens' basket into the road behind him.

Between the rows, only what really lies in a market street: a goat kid crossing, cow dung, the puddle round the hand
pump (and, once, two ducks waddling from it), sacks of grain unloaded for a shop (hop onto them and off), a heap of
building sand, a dog asleep, the potter's pots set out in front of his stall, and one tree at the market's edge whose
low limb she slides under. (The washing lines strung across the road and the other pot stacks are gone.) Distances
keep the old design's timing at the new pace: about 4 m between things to jump, and 4 to 5 m after a row of awnings
for a bounce to come down.
"""
import math

from levelkit import Plan, run

# Room between neighbouring stalls: each stands as far back as its own goods reach (Kit.FrontAt), so neighbours sit at
# different depths and their sides would overlap if they stood shoulder to shoulder.
STALL_GAP = 0.55

ROWS = [
    ["stall_c_2", "stall_e_3"],
    ["stall_f_1", "stall_h_1", "stall_flowers"],
    ["stall_vessels", "stall_veg"],
    ["stall_sweets", "stall_d_2", "stall_potter"],
    ["stall_g_2", "stall_flowers"],
    ["stall_veg", "stall_h_1", "stall_c_1"],
]


def stalls(p, s, x, pieces, feather=None):
    """A row of stalls STALL_GAP apart from x, mangoes along their awnings; returns where the row ends."""
    start = x
    for piece in pieces:
        x = p.stall(s, x, piece) + STALL_GAP
    end = x - STALL_GAP
    n = int((end - start - 1.0) // 1.1)
    p.mango_line(s, start + 0.6, n, 1.1, 3.4)
    if feather is not None:
        p.feather(s, (start + end) / 2, 4.7, feather)
    return end


def design():
    p = Plan(zone=3, seed=8)

    # ---- the opening: the market gate
    s = p.section("MarketGate", -10.0, 16.0, "The weekly market's cement road: the rooster struts ahead; tap to chase.")
    p.prop(s, "brass_vessels", -6.0, 1.6, h=0.9)
    p.prop(s, "veg_basket", -2.0, 1.4, h=0.6)
    p.prop(s, "hen_with_chicks", 2.5, 1.5, h=0.45)
    p.mango_line(s, 1.0, 4, 1.0, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstStalls", 6.0, 13.0, "The first row of stalls: run under, or jump into an awning and bounce along.")
    stalls(p, s, 8.0, ROWS[0])
    p.litter(s, 2)

    s = p.section("Hens", 19.0, 7.0, "Two of a vendor's hens loose in the road: jump them.")
    p.hens(s, 23.0, 2)
    p.litter(s, 2, avoid=(23.0,))

    s = p.section("Basket", 26.0, 7.0, "Their basket, left in the road: jump it.")
    p.hens_basket(s, 29.5)
    p.prop(s, "hen_1", 31.0, 1.4, h=0.42)
    p.litter(s, 2, avoid=(29.5,))

    s = p.section("HighAwnings", 33.0, 14.0, "Three stalls: a feather high over their awnings for a bounce and a double jump.")
    stalls(p, s, 35.0, ROWS[1], feather=0)
    p.litter(s, 2)

    s = p.section("Breather", 47.0, 9.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 47.5)
    for i in range(10):
        p.mango(s, 49.0 + i * 0.7, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 2)

    s = p.section("EdgeTree", 56.0, 8.0, "A tree at the market's edge, its low limb across the road: slide.")
    p.low_branch(s, 60.0)
    p.litter(s, 2, avoid=(60.0,))

    s = p.section("DungBasket", 64.0, 9.0, "Cow dung, then a hens' basket.")
    p.dung(s, 67.5)
    p.hens_basket(s, 71.5)
    p.litter(s, 2, avoid=(67.5, 71.5))

    # ---- practise
    s = p.section("Flocks", 73.0, 10.0, "Two pairs of hens. A feather over the second, for a double jump.")
    p.hens(s, 76.0, 2)
    p.hens(s, 80.0, 2)
    p.feather(s, 80.0, 2.9, 2)
    p.litter(s, 2, avoid=(76.0, 80.0))

    s = p.section("StallsHens", 83.0, 16.0, "A row of stalls, then a hen after it.")
    end = stalls(p, s, 84.5, ROWS[2])
    p.hens(s, end + 4.5, 1)
    p.litter(s, 2, avoid=(end + 4.5,))

    s = p.section("ChilliLane", 99.0, 9.0, "A chilli to win back ground.")
    p.chilli(s, 99.5)
    p.mango_line(s, 101.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("PumpSacks", 108.0, 14.0, "The hand-pump puddle, two ducks waddling from it, sacks of grain unloaded for a shop.")
    p.puddle(s, 111.5)
    p.prop(s, "woman_carrying_pot", 112.6, 2.0, h=1.95)   # filling her pot at the pump
    p.ducks(s, 115.5, 2)
    p.sacks(s, 119.0)
    p.litter(s, 2, avoid=(111.5, 115.5, 119.0, 120.2))

    s = p.section("LongAwnings", 122.0, 18.0, "A long row of stalls, the potter's last: bounce along, a feather at the top.")
    stalls(p, s, 123.5, ROWS[3], feather=1)
    p.litter(s, 2)

    # ---- test
    s = p.section("FakeOut", 140.0, 12.0, "The potter's pots set out in the road by his stall; the rooster knocks a hens' basket in; a goat kid.")
    p.pots(s, 142.5)
    p.prop(s, "pot_stack", 140.6, 2.3, h=0.62, mirror=True)   # more of his pots, at the road's edge
    p.prop(s, "hens_basket", 146.9, 1.4, h=0.55)
    p.hens_basket(s, 146.5, hidden=True, ident="knocked")
    p.mischief(s, 147.0, "knocked")
    p.jump_arc(s, 146.5)
    p.goats(s, 150.5, 1)
    p.litter(s, 2, avoid=(142.5, 146.5, 150.5))

    s = p.section("FlocksAwnings", 152.0, 20.0, "Hens, a row of stalls, cow dung.")
    p.hens(s, 154.5, 2)
    end = stalls(p, s, 157.5, ROWS[4])
    p.dung(s, end + 4.5)
    p.litter(s, 2, avoid=(154.5, end + 4.5))

    s = p.section("ChilliStraight", 172.0, 9.0, "A chilli and a straight.")
    p.chilli(s, 172.5)
    p.mango_line(s, 174.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("CrowdedRoad", 181.0, 17.0, "Hens, a heap of building sand, a dog asleep, the hens' basket.")
    p.hens(s, 184.0, 2)
    p.sand(s, 188.0)
    p.dog(s, 192.0)
    p.hens_basket(s, 196.0)
    p.litter(s, 2, avoid=(184.0, 188.0, 192.0, 196.0))

    s = p.section("LastAwnings", 198.0, 16.0, "The last long row of stalls.")
    stalls(p, s, 199.5, ROWS[5])
    p.litter(s, 2)

    s = p.section("FinalChilli", 214.0, 9.0, "A chilli.")
    p.chilli(s, 214.5)
    p.mango_line(s, 216.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("LastTest", 223.0, 21.0, "Hens, a goat kid, the puddle, sacks, hens: everything once more.")
    p.hens(s, 226.0, 2)
    p.goats(s, 230.0, 1)
    p.puddle(s, 234.0)
    p.sacks(s, 237.5)
    p.hens(s, 242.5, 2)
    p.litter(s, 2, avoid=(226.0, 230.0, 234.0, 237.5, 238.7, 242.5))

    s = p.section("StallsAgain", 244.0, 18.0, "Stalls, then hens after them.")
    end = stalls(p, s, 245.5, ROWS[1])
    p.hens(s, end + 4.5, 2)
    p.litter(s, 2, avoid=(end + 4.5,))

    s = p.section("ChilliLane2", 262.0, 9.0, "One more chilli.")
    p.chilli(s, 262.5)
    p.mango_line(s, 264.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("LastRow", 271.0, 14.0, "One more row of stalls.")
    stalls(p, s, 272.5, ROWS[2])
    p.litter(s, 2)

    s = p.section("MarketEnd", 285.0, 21.0, "The market thins out: a last hens' basket; if he is still ahead, he gets away at 300 m.")
    p.hens_basket(s, 288.0)
    p.mango_line(s, 290.5, 10, 1.0, 0.6)
    p.prop(s, "brass_vessels", 299.0, 1.6, h=0.9)
    p.litter(s, 3, avoid=(288.0,))
    return p


PROSE = [
    "## The opening: the market gate",
    "",
    "No basket: the chase starts on the market's cement road with the rooster 7 m ahead (the Ready screen; tap to",
    "chase). The kid runs 3.5 m/s, a small child's real pace, and the rooster 3.15: a clean run catches him at about",
    "62 m. The course is 300 m, about a minute and a half.",
    "",
    "## The new things",
    "",
    "* **Awnings:** rows of two or three stalls at the road's edge, awnings about 2.1 m up. Run under them, or jump into",
    "  one for a 2 m bounce, from awning to awning (a bounce carries her about 2.6 m, so she meets every stall) along a",
    "  line of mangoes; feathers sit high over two rows. After a row, 4 to 5 m for a bounce to come down.",
    "* **The vendors' hens**, loose in the road one or two at a time: jump them, or scatter them (a stumble). Their",
    "  baskets stand in the road too, jumped like a pot stack.",
    "* **The fake-out:** the rooster knocks a hens' basket into the road behind him.",
    "",
    "## The market street",
    "",
    "Only what lies in a real one, about 4 m (a second and a bit) apart: a goat kid crossing, cow dung (a cow wanders by),",
    "the hand pump's puddle with two ducks waddling from it, sacks of grain unloaded for a shop (hop onto them and off),",
    "a heap of building sand, a dog asleep, the potter's pots set out in front of his stall, and one tree at the market's",
    "edge whose low limb she slides under. The washing lines strung across the road are gone, and so are the other pots.",
    "",
    "## The shape of it",
    "",
    "Teach (to 73 m): stalls, hens, their basket, stalls with a feather, a chilli, the tree's limb, dung and a basket.",
    "Practise (to 140 m): two pairs of hens, stalls then a hen, a chilli, the pump, the ducks and the sacks, the long row",
    "of awnings. Test (to 300 m): the fake-out by the potter's, hens and awnings, a crowded road, the last long row,",
    "everything once more, the last rows, then the market thins out.",
]


def main():
    p = design()
    run(p, {"level": 8, "title": "Market day", "subtitle": "Bounce across the awnings.", "prose": PROSE})


if __name__ == "__main__":
    main()
