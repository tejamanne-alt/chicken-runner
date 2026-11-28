"""Level 9, "The temple steps": the finale, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level9.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level9.py --report   # also writes docs/levels/level9.md

The last level (zone 3): the kid runs at a small child's real pace, 3.5 m/s, against the rooster's 3.15; the course is
340 m, the longest (this level's meta sets it), and the chase starts 7 m behind him (no basket), so a clean run catches
him at about 62 m. From the doc's level table: everything, and the catch that sticks.

The temple street at festival time, on its cement road. Five flights of temple steps (six steps of 0.25 m, walked up,
a landing 1.5 m up with its lamps, six steps down: 14.4 m, the hand-built granite flight), new clay pots stacked on
two landings for the festival's pongal (jump them up there), and on the way the whole game once more: two rooftop
stretches with a ladder, a tank and a 1.2 m gap, rows of flower and brass-vessel stalls to bounce along, and only
what lies in a real temple street: the vendors' hens and their baskets, a goat kid, cow dung, the puddle round the
hand pump, a dog asleep, sacks of paddy unloaded for a shop, a heap of building sand, two neems by the temple whose
low limbs she slides under, and the rooster's mischief. (The washing lines across the street and the pot stacks in
it are gone.) Distances keep the old design's timing at the new pace: about 4 m between things to jump.
"""
import math

from levelkit import Plan, ROOF, run

# Room between neighbouring stalls: each stands as far back as its own goods reach (Kit.FrontAt), so neighbours sit at
# different depths and their sides would overlap if they stood shoulder to shoulder.
STALL_GAP = 0.55

IND, PINK, LIME = "house_indigo_veranda", "house_pink", "house_limewash"


def stalls(p, s, x, pieces, feather=None):
    start = x
    for piece in pieces:
        x = p.stall(s, x, piece) + STALL_GAP
    end = x - STALL_GAP
    p.mango_line(s, start + 0.6, int((end - start - 1.0) // 1.1), 1.1, 3.4)
    if feather is not None:
        p.feather(s, (start + end) / 2, 4.7, feather)
    return end


def steps(p, s, x, feather=None, pots=False):
    """A flight of temple steps (six up, a 6 m landing, six down: the hand-built granite flight) with mangoes along its
    landing; optionally the festival's new clay pots stacked on the landing, to jump up there."""
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
    """A ladder up onto a row, a tank on it, a 1.2 m gap, a second row, and down: the terraces once more."""
    end = p.roofs(s, x, ["", IND, PINK], ladder=True)
    p.tank(s, x + 3.3, ROOF)
    x_m = x + 1.6
    while x_m < end - 0.4:
        if abs(x_m - (x + 3.3)) > 1.6:
            p.mango(s, x_m, ROOF + 0.55)
        x_m += 0.7
    nxt = end + 1.2
    p.hop_gap(s, end, nxt)
    p.arc(s, end - 0.6, 2.4, 0.9, 3, ROOF)
    end2 = p.roofs(s, nxt, [IND, LIME, PINK])
    x_m = nxt + 0.8
    while x_m < end2 - 0.4:
        p.mango(s, x_m, ROOF + 0.55)
        x_m += 0.7
    p.hop_down(s, end2)
    return end2


def design():
    p = Plan(zone=3, seed=9)

    # ---- the opening: the temple street
    s = p.section("TempleStreet", -10.0, 16.0, "The temple street at festival time: the rooster struts ahead; tap to chase.")
    p.prop(s, "lamp_step", -6.0, 2.2, h=1.9)
    p.prop(s, "brass_vessels", -2.0, 1.6, h=0.9)
    p.decal(s, "kolam_6", -3.5, -1.2, 1.2)
    p.mango_line(s, 1.0, 4, 1.0, 0.6)
    p.litter(s, 3)

    # ---- the way to the temple: everything once more
    s = p.section("FirstSteps", 6.0, 20.0, "The first temple steps: up (walked), along the landing, and down. A feather.")
    end = steps(p, s, 9.0, feather=0)
    p.litter(s, 2, holes=[(9.0, end)])

    s = p.section("HensDog", 26.0, 9.0, "Two of a vendor's hens, then a dog asleep in the street.")
    p.hens(s, 28.5, 2)
    p.dog(s, 32.5)
    p.litter(s, 2, avoid=(28.5, 32.5))

    s = p.section("Rooftops", 35.0, 18.0, "Up a ladder onto the terraces, a tank, a gap, and down.")
    end = roofs(p, s, 36.5)
    p.litter(s, 2, holes=[(36.5, end)])

    s = p.section("Neem", 53.0, 8.0, "A neem by the temple, its low limb across the street: slide.")
    p.low_branch(s, 57.0)
    p.litter(s, 2, avoid=(57.0,))

    s = p.section("Breather", 61.0, 9.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 61.5)
    for i in range(10):
        p.mango(s, 63.0 + i * 0.7, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 2)

    s = p.section("Awnings", 70.0, 13.0, "The flower and brass-vessel stalls: bounce along the awnings. A feather.")
    stalls(p, s, 71.5, ["stall_flowers", "stall_vessels"], feather=1)
    p.litter(s, 2)

    s = p.section("Mischief", 83.0, 14.0, "The hand-pump puddle; the rooster knocks a hens' basket into the road; a goat kid.")
    p.puddle(s, 87.5)
    p.prop(s, "hens_basket", 91.9, 1.4, h=0.55)
    p.hens_basket(s, 91.5, hidden=True, ident="knocked")
    p.mischief(s, 92.0, "knocked")
    p.jump_arc(s, 91.5)
    p.goats(s, 95.5, 1)
    p.litter(s, 2, avoid=(87.5, 91.5, 95.5))

    s = p.section("StepsWithPots", 97.0, 19.0, "Temple steps with the festival's new pots stacked on the landing: jump them up there.")
    end = steps(p, s, 99.0, pots=True)
    p.litter(s, 2, holes=[(99.0, end)])

    s = p.section("ChilliLane", 116.0, 9.0, "A chilli to win back ground.")
    p.chilli(s, 116.5)
    p.mango_line(s, 118.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("Flocks", 125.0, 13.0, "Two hens, a goat kid, the hens' basket; a feather over the basket.")
    p.hens(s, 128.5, 2)
    p.goats(s, 132.5, 1)
    p.hens_basket(s, 136.5)
    p.feather(s, 136.5, 2.9, 2)
    p.litter(s, 2, avoid=(128.5, 132.5, 136.5))

    s = p.section("RoofsAgain", 138.0, 18.0, "The terraces again.")
    end = roofs(p, s, 139.5)
    p.litter(s, 2, holes=[(139.5, end)])

    s = p.section("SacksDungNeem", 156.0, 14.0, "Sacks of paddy unloaded for a shop, cow dung, the second neem's low limb.")
    p.sacks(s, 158.5)
    p.dung(s, 163.5)
    p.low_branch(s, 168.0)
    p.litter(s, 2, avoid=(158.5, 159.7, 163.5, 168.0))

    s = p.section("ChilliStraight", 170.0, 9.0, "A chilli and a straight.")
    p.chilli(s, 170.5)
    p.mango_line(s, 172.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("StepsAwnings", 179.0, 29.0, "Temple steps, then a row of stalls.")
    end = steps(p, s, 180.0)
    stalls(p, s, end + 2.5, ["stall_g_1", "stall_h_1"])
    p.litter(s, 2, holes=[(180.0, end)])

    s = p.section("CrowdedStreet", 208.0, 17.0, "Hens, their basket, a heap of building sand, a dog asleep.")
    p.hens(s, 211.0, 2)
    p.hens_basket(s, 215.0)
    p.sand(s, 219.0)
    p.dog(s, 223.0)
    p.litter(s, 2, avoid=(211.0, 215.0, 219.0, 223.0))

    s = p.section("FinalChilli", 225.0, 9.0, "A chilli.")
    p.chilli(s, 225.5)
    p.mango_line(s, 227.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("LastRoofs", 234.0, 18.0, "The last rooftops.")
    end = roofs(p, s, 235.0)
    p.litter(s, 2, holes=[(235.0, end)])

    s = p.section("StepsAgain", 252.0, 18.0, "Another flight, the festival's pots on its landing.")
    end = steps(p, s, 253.0, pots=True)
    p.litter(s, 2, holes=[(253.0, end)])

    s = p.section("LastAwnings", 270.0, 12.0, "The last row of stalls.")
    stalls(p, s, 271.0, ["stall_sweets", "stall_flowers"])
    p.litter(s, 2)

    s = p.section("LastTest", 282.0, 21.0, "Everything once more: hens, a goat kid, the puddle, the basket, a hen.")
    p.hens(s, 285.0, 2)
    p.goats(s, 289.0, 1)
    p.puddle(s, 293.0)
    p.hens_basket(s, 297.0)
    p.hens(s, 301.0, 1)
    p.litter(s, 2, avoid=(285.0, 289.0, 293.0, 297.0, 301.0))

    s = p.section("TempleApproach", 303.0, 20.0, "The temple's own steps, the last flight.")
    end = steps(p, s, 305.0)
    p.prop(s, "lamp_step", end + 1.5, 2.0, h=1.9)
    p.litter(s, 2, holes=[(305.0, end)])

    s = p.section("TempleCourt", 323.0, 22.0, "The temple court: if he is still ahead, he gets away at 340 m.")
    p.mango_line(s, 324.0, 12, 1.0, 0.6)
    p.prop(s, "brass_vessels", 333.0, 1.6, h=0.9)
    p.prop(s, "lamp_step", 338.0, 2.0, h=1.9, mirror=True)
    p.litter(s, 3)
    return p


PROSE = [
    "## The opening: the temple street",
    "",
    "No basket: the chase starts in the temple street at festival time with the rooster 7 m ahead (the Ready screen;",
    "tap to chase). The kid runs 3.5 m/s, a small child's real pace, and the rooster 3.15: a clean run catches him at",
    "about 62 m. The course runs 340 m, the longest, about a minute and a half and a bit.",
    "",
    "## The temple steps",
    "",
    "* Five flights. Six steps of 0.25 m (low enough to walk up), a landing 1.5 m up with its lamps, six steps down:",
    "  14.4 m in all, about four seconds of running.",
    "* Mangoes along the landing; on two flights the festival's new clay pots are stacked up there, to jump; a feather",
    "  above the first.",
    "",
    "## The rest of the street",
    "",
    "Three rooftop stretches (a ladder, a water tank, a 1.2 m gap, a second row, the drop), three rows of stalls to",
    "bounce along, and only what lies in a real temple street, about 4 m (a second and a bit) apart: the vendors' hens",
    "and their baskets, a goat kid, cow dung, the puddle round the hand pump, a dog asleep, sacks of paddy unloaded for",
    "a shop, a heap of building sand, two neems by the temple whose low limbs she slides under, and the rooster's",
    "mischief with a hens' basket. The washing lines across the street and the pot stacks in it are gone.",
    "",
    "## The shape of it",
    "",
    "The whole game once more on the way to the temple: steps, hens and a dog, a rooftop stretch, a neem, the awnings,",
    "the mischief, steps with pots, hens, a goat and a basket, the roofs again, sacks, dung and a neem, steps then",
    "stalls, a crowded street, the last rooftops, steps with pots again, the last awnings, everything once more, the",
    "temple's own steps, and the temple court.",
]


def main():
    p = design()
    run(p, {"level": 9, "title": "The temple steps", "subtitle": "Everything at once. Catch him for good!",
            "courseLength": 340.0, "prose": PROSE})


if __name__ == "__main__":
    main()
