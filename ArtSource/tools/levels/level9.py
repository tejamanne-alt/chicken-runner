"""Level 9, "The temple steps": the finale, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level9.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level9.py --report   # also writes docs/levels/level9.md

The last level (zone 3, 8 m/s against 7.4, 800 m: the longest course, a 12 m start). From the doc's level table:
everything, and the catch that sticks. The temple street: its cement road, flights of temple steps (six steps of
0.25 m, walked up, a landing 1.5 m up with lamps, six steps down; pot stacks wait on one landing), and on the way
there the whole game once more: a rooftop stretch with a ladder, a gap and a tank, rows of stalls to bounce along,
flocks of hens, clotheslines, pots, the rooster's mischief.
"""
import math

from levelkit import Plan, ROOF, run

IND, PINK, LIME = "house_indigo_veranda", "house_pink", "house_limewash"


def stalls(p, s, x, pieces, feather=None):
    start = x
    for piece in pieces:
        x = p.stall(s, x, piece) + 0.25
    end = x - 0.25
    p.mango_line(s, start + 0.6, int((end - start - 1.0) // 1.1), 1.1, 3.4)
    if feather is not None:
        p.feather(s, (start + end) / 2, 4.7, feather)
    return end


def steps(p, s, x, feather=None, pots=False):
    """A flight of temple steps with mangoes along its landing; optionally pots on the landing."""
    end = p.steps(s, x, 6, 6.0)
    top = 6 * 0.25
    land0 = x + 6 * 0.7
    if pots:
        p.pots(s, land0 + 3.0, y=top)
        p.mango_line(s, land0 + 0.4, 2, 0.75, top + 0.55)
    else:
        p.mango_line(s, land0 + 0.4, 7, 0.75, top + 0.55)
    if feather is not None:
        p.feather(s, land0 + 3.0, top + 2.1, feather)
    p.prop(s, "mandapam", land0 + 3.0, 3.2, h=2.9)
    return end


def roofs(p, s, x):
    """A ladder up onto a row, a tank on it, a gap, a second row, and down: the terraces once more."""
    end = p.roofs(s, x, ["", IND, PINK, LIME, IND, PINK, LIME], ladder=True)
    p.tank(s, x + 6.0, ROOF)
    x_m = x + 3.0
    while x_m < end - 0.5:
        if abs(x_m - (x + 6.0)) > 2.4:
            p.mango(s, x_m, ROOF + 0.55)
        x_m += 0.8
    nxt = end + 2.0
    p.hop_gap(s, end, nxt)
    p.arc(s, end - 1.2, 4.4, 1.1, 3, ROOF)
    end2 = p.roofs(s, nxt, [IND, PINK, LIME, IND])
    p.hop_down(s, end2)
    return end2


def design():
    p = Plan(zone=3, seed=9)

    # ---- the opening: the temple street
    s = p.section("TempleStreet", -10.0, 24.0, "The temple street at festival time: the rooster struts ahead; tap to chase.")
    p.prop(s, "lamp_step", -6.0, 2.2, h=1.9)
    p.prop(s, "brass_vessels", -2.0, 1.6, h=0.9)
    p.prop(s, "flower_stall", 4.5, 3.2)
    p.decal(s, "kolam_6", -3.5, -1.2, 1.2)
    p.mango_line(s, 2.0, 5, 2.0, 0.6)
    p.litter(s, 3)

    # ---- the way to the temple: everything once more
    s = p.section("FirstSteps", 14.0, 32.0, "The first temple steps: up (walked), along the landing, and down.")
    steps(p, s, 20.0, feather=0)
    p.litter(s, 2, holes=[(20.0, 34.4)])

    s = p.section("HensPots", 46.0, 20.0, "Hens, then pots.")
    p.hens(s, 50.0, 3)
    p.pots(s, 59.0)
    p.litter(s, 2, avoid=(50.0, 59.0))

    s = p.section("Rooftops", 66.0, 40.0, "Up a ladder onto the terraces, a tank, a gap, and down.")
    roofs(p, s, 68.0)
    p.litter(s, 2, holes=[(68.0, 100.0)])

    s = p.section("Clothesline", 106.0, 16.0, "A clothesline: slide.")
    p.clothesline(s, 113.0)
    p.litter(s, 2, avoid=(113.0,))

    s = p.section("Breather", 122.0, 18.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 123.0)
    for i in range(10):
        p.mango(s, 125.5 + i * 1.3, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 3)

    s = p.section("Awnings", 140.0, 30.0, "A row of stalls: bounce along the awnings.")
    stalls(p, s, 143.0, ["stall_flowers", "stall_vessels", "stall_e_3"], feather=1)
    p.litter(s, 2)

    s = p.section("Mischief", 170.0, 28.0, "Pots; the rooster knocks a hens' basket into the road; a clothesline.")
    p.pots(s, 174.0)
    p.prop(s, "hens_basket", 182.9, 1.4, h=0.55)
    p.hens_basket(s, 182.5, hidden=True, ident="knocked")
    p.mischief(s, 183.5, "knocked")
    p.jump_arc(s, 182.5)
    p.clothesline(s, 192.0)
    p.litter(s, 2, avoid=(174.0, 182.5, 192.0))

    s = p.section("StepsWithPots", 198.0, 32.0, "Temple steps with a pot stack on the landing: jump it up there.")
    steps(p, s, 203.0, pots=True)
    p.litter(s, 2, holes=[(203.0, 217.4)])

    s = p.section("ChilliLane", 230.0, 18.0, "A chilli to win back ground.")
    p.chilli(s, 231.0)
    p.mango_line(s, 233.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("Flocks", 248.0, 26.0, "Two flocks and a basket.")
    p.hens(s, 252.0, 2)
    p.hens(s, 260.5, 3)
    p.hens_basket(s, 269.0)
    p.feather(s, 269.0, 2.9, 2)
    p.litter(s, 2, avoid=(252.0, 260.5, 269.0))

    s = p.section("RoofsAgain", 274.0, 40.0, "The terraces again.")
    roofs(p, s, 277.0)
    p.litter(s, 2, holes=[(277.0, 309.0)])

    s = p.section("LinesPots", 314.0, 26.0, "Clothesline, pots, clothesline.")
    p.clothesline(s, 318.0)
    p.pots(s, 324.5)
    p.clothesline(s, 334.0)
    p.litter(s, 2, avoid=(318.0, 324.5, 334.0))

    s = p.section("ChilliStraight", 340.0, 18.0, "A chilli and a long straight.")
    p.chilli(s, 341.0)
    p.mango_line(s, 343.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("StepsAwnings", 358.0, 44.0, "Temple steps, then a row of stalls.")
    end = steps(p, s, 361.0)
    stalls(p, s, end + 4.0, ["stall_g_1", "stall_h_1", "stall_c_3"])
    p.litter(s, 2, holes=[(361.0, 375.4)])

    s = p.section("CrowdedStreet", 402.0, 36.0, "Hens, the basket, pots, a clothesline.")
    p.hens(s, 410.0, 3)
    p.hens_basket(s, 418.0)
    p.pots(s, 426.0)
    p.clothesline(s, 435.0)
    p.litter(s, 2, avoid=(410.0, 418.0, 426.0, 435.0))

    s = p.section("FinalChilli", 438.0, 20.0, "A chilli.")
    p.chilli(s, 441.0)
    p.mango_line(s, 443.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("LastRoofs", 458.0, 42.0, "The last rooftops.")
    roofs(p, s, 461.0)
    p.litter(s, 2, holes=[(461.0, 493.0)])

    s = p.section("StepsTwice", 500.0, 44.0, "Two flights of steps, pots on the second landing.")
    end = steps(p, s, 503.0)
    steps(p, s, end + 4.0, pots=True)
    p.litter(s, 2, holes=[(503.0, 540.0)])

    s = p.section("LastAwnings", 544.0, 34.0, "The last row of stalls.")
    stalls(p, s, 547.0, ["stall_sweets", "stall_potter", "stall_flowers"])
    p.litter(s, 2)

    s = p.section("ChilliLane2", 578.0, 18.0, "One more chilli.")
    p.chilli(s, 579.0)
    p.mango_line(s, 581.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("LastTest", 596.0, 50.0, "Everything once more: hens, pots, a clothesline, the basket, hens.")
    p.hens(s, 600.0, 3)
    p.pots(s, 608.0)
    p.clothesline(s, 617.0)
    p.hens_basket(s, 623.0)
    p.hens(s, 632.0, 2)
    p.mango_line(s, 636.0, 6, 1.3, 0.6)
    p.litter(s, 2, avoid=(600.0, 608.0, 617.0, 623.0, 632.0))

    s = p.section("TempleApproach", 646.0, 40.0, "The temple's own steps, the last flight.")
    steps(p, s, 652.0)
    p.prop(s, "lamp_step", 676.0, 2.0, h=1.9)
    p.litter(s, 2, holes=[(652.0, 666.4)])

    s = p.section("TempleCourt", 686.0, 120.0, "The temple court: if he is still ahead, he gets away at 800 m.")
    p.mango_line(s, 688.0, 20, 1.4, 0.6)
    p.prop(s, "lamp_step", 712.0, 2.0, h=1.9)
    p.prop(s, "brass_vessels", 740.0, 1.6, h=0.9)
    p.prop(s, "lamp_step", 772.0, 2.0, h=1.9, mirror=True)
    p.litter(s, 8)
    return p


PROSE = [
    "## The opening: the temple street",
    "",
    "No basket: the chase starts in the temple street at festival time with the rooster 12 m ahead (the Ready screen;",
    "tap to chase). A clean run catches him at about 149 m; the course runs 800 m, the longest.",
    "",
    "## The temple steps",
    "",
    "* Six steps of 0.25 m (low enough to walk up), a landing 1.5 m up with its lamps, six steps down: 14.4 m in all.",
    "* Mangoes along the landing; on two flights a pot stack waits up there to jump; a feather above the first.",
    "",
    "## The shape of it",
    "",
    "The whole game once more on the way to the temple: steps, hens and pots, a rooftop stretch (ladder, tank, gap),",
    "a clothesline, the awnings, the mischief, steps with pots, flocks, the roofs again, lines and pots, steps then",
    "stalls, a crowded street, the last rooftops, two flights of steps, the last awnings, everything once more, the",
    "temple's own steps, and the temple court.",
]


def main():
    p = design()
    run(p, {"level": 9, "title": "The temple steps", "subtitle": "Everything at once. Catch him for good!",
            "courseLength": 800.0, "prose": PROSE})


if __name__ == "__main__":
    main()
