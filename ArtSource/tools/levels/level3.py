"""Level 3, "Up on the roofs": the lane's houses, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level3.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level3.py --report   # also writes docs/levels/level3.md

The last level of zone 1, at a small child's real pace (3.5 m/s against the rooster's 3.2, 290 m, a 7 m start: no
basket). The old design's timing is kept (its distances shrink by 3.5/6; its rows lose a house or two so they take
about as long to run), and the road between the rows holds only what lies in a village street. New, from the doc's
level table: houses, ladders and the first rooftop stretch.

  * Up: run into the bamboo ladder on a row's first house and she climbs it in 0.45 s. Or run into a rope cot pushed
    against the wall of a house with no ladder: she bounces off its near end, 2.4 m up, and pops onto the 2.35 m roof
    as she meets the wall (a double jump in the bounce makes it sure). Without either, a double jump, or a slow vault.
  * Across: gaps of 1.2 to 1.3 m between rows; a held jump clears them with 310 to 340 ms to spare.
  * On top: the black water tanks on their stands, jumped as on the road.
  * Down: off the end of a row, landing about 1.4 m on.

Between the rows the road keeps the zone's things: the dog asleep, cow dung, hens, a goat kid, the hand pump's
puddle, a heap of building sand, two neems with a low limb to slide under. No washing over the road and no pots: the
rooster's mischief is the hens' basket, knocked off a doorstep into the road. Feathers on the harder routes: above the
first gap, above a cot's bounce at the wall, above a tank on a roof.
"""
import math

from levelkit import KID_R, ROOF, Plan, run

IND, PINK, LIME = "house_indigo_veranda", "house_pink", "house_limewash"
COT = 1.9                    # Kit.Cot's length


def row(p, s, x, fronts, ladder=False, crows=None):
    end = p.roofs(s, x, ([""] if ladder else []) + list(fronts), ladder=ladder)
    if crows is not None:
        p.prop(s, "crows_on_ledge", crows, 1.3, h=0.45, y=ROOF + 0.15)    # on the back parapet
    return end


def roof_mangoes(p, s, x0, x1, avoid=()):
    x = x0
    while x < x1:
        if not any(abs(x - a) < 1.6 for a in avoid):
            p.mango(s, x, ROOF + 0.55)
        x += 0.7


def gap(p, s, end, nxt):
    """Across a gap between rows: the rooster's hop, and three mangoes on a held jump's arc over its middle."""
    p.hop_gap(s, end, nxt)
    c = (end + nxt) / 2
    p.arc(s, c - p.r.JUMP_LEN / 2, p.r.JUMP_LEN, p.r.T["jumpHeight"], 3, ROOF)


def cot_up(p, s, x):
    """A rope cot pushed against the wall of a row starting at its far end (x + 1.9), returned. Plan.cot(onto_roof)
    lays its mangoes and the rooster's bounce for the old 6 m/s, with the row about 1 m on: at 3.5 m/s her bounce off
    the cot's near end is back below the roof by then. Here: the cot, the rooster's bounce up onto the roof, and
    mangoes along her bounce until she meets the wall (her feet are still 2.1 m up there, so she steps onto the roof)."""
    n = len(s["items"])
    p.cot(s, x, onto_roof=True)
    del s["items"][n + 1:]                      # keep the cot the kit lays; drop its 6 m/s hop and mangoes
    p.hop(s, x - 0.3, 3.0, 1.3)
    r = p.r
    v = math.sqrt(2 * r.G * r.T["cotBounceHeight"])
    for t in (0.12, 0.26, 0.40):
        p.mango(s, x - KID_R + r.RUN * t, round(v * t - r.G * t * t / 2 + 0.55, 2))
    return x + COT


def design():
    p = Plan(zone=1, seed=3)

    # ---- the opening: the street of houses
    s = p.section("Street", -10.0, 18.0, "A street of flat-roofed houses: the rooster struts ahead; tap to chase.")
    p.prop(s, "kids_rolling_tyre", 4.6, 2.2, h=1.15)      # clear of the set's milkman at -4.4
    p.decal(s, "kolam_5", -1.0, 1.0, 1.0)
    p.mango_line(s, 1.0, 5, 1.2, 0.6)
    p.litter(s, 3)

    # ---- teach (to 88 m)
    s = p.section("FirstLadder", 8.0, 14.0, "The first ladder: run into it and she climbs; along the roofs, and off "
                                            "the end.")
    end = row(p, s, 11.0, [PINK, LIME], ladder=True, crows=13.6)
    roof_mangoes(p, s, 12.4, end - 0.4)
    p.hop_down(s, end)
    p.litter(s, 2, holes=[(11.0, end)])

    s = p.section("FirstGap", 22.0, 15.0, "Two rows with a 1.2 m gap: jump across. A feather above the gap.")
    end = row(p, s, 24.0, [IND], ladder=True)
    roof_mangoes(p, s, 25.4, end - 0.6)
    nxt = end + 1.2
    gap(p, s, end, nxt)
    p.feather(s, end + 0.6, ROOF + 2.8, 0)
    end2 = row(p, s, nxt, [PINK, IND])
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.4)
    p.hop_down(s, end2)
    p.litter(s, 2, holes=[(24.0, end2)])

    s = p.section("Neem", 37.0, 9.0, "Back on the road: a neem's low limb across it. Slide.")
    p.low_branch(s, 41.5)
    p.litter(s, 2, avoid=(41.5,))

    s = p.section("CotUp", 46.0, 14.0, "A rope cot pushed against a house with no ladder: run into it and bounce up "
                                       "onto its roof.")
    start = cot_up(p, s, 48.0)
    end = row(p, s, start, [IND, PINK, LIME])
    roof_mangoes(p, s, start + 0.5, end - 0.4)
    p.hop_down(s, end)
    p.litter(s, 2, avoid=(49.0,), holes=[(start, end)])

    s = p.section("Breather", 60.0, 10.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 60.6)
    for i in range(8):
        p.mango(s, 62.4 + i * 0.7, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 3)

    s = p.section("RoofTank", 70.0, 18.0, "A long row with a water tank on the roof: jump it up there. Dung after "
                                          "the drop.")
    end = row(p, s, 72.0, [IND, PINK, LIME], ladder=True, crows=78.4)
    p.tank(s, 76.0)
    roof_mangoes(p, s, 73.4, end - 0.4, avoid=(76.0,))
    p.hop_down(s, end)
    p.dung(s, 84.5)
    p.litter(s, 2, avoid=(84.5,), holes=[(72.0, end)])

    # ---- practise (to 160 m)
    s = p.section("GapGap", 88.0, 18.0, "Three rows, two gaps.")
    end = row(p, s, 89.0, [PINK], ladder=True)
    roof_mangoes(p, s, 90.4, end - 0.6)
    nxt = end + 1.2
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [LIME, IND])
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.6)
    nxt2 = end2 + 1.3
    gap(p, s, end2, nxt2)
    end3 = row(p, s, nxt2, [PINK, LIME])
    roof_mangoes(p, s, nxt2 + 1.0, end3 - 0.4)
    p.hop_down(s, end3)
    p.litter(s, 2, holes=[(89.0, end3)])

    s = p.section("SandHens", 106.0, 11.0, "A house going up: a heap of its sand in the road, then two hens.")
    p.sand(s, 109.0)
    p.hens(s, 113.5, 2)
    p.litter(s, 2, avoid=(109.0, 113.5))

    s = p.section("CotUpGap", 117.0, 20.0, "The cot up onto a roof (a feather above the wall), a gap, and a tank on "
                                           "the next roof.")
    start = cot_up(p, s, 119.0)
    p.feather(s, 120.7, 4.3, 1)
    end = row(p, s, start, [PINK, LIME, IND])
    roof_mangoes(p, s, start + 0.5, end - 0.6)
    nxt = end + 1.2
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [IND, PINK, LIME])
    p.tank(s, nxt + 3.5)
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.4, avoid=(nxt + 3.5,))
    p.hop_down(s, end2)
    p.litter(s, 2, avoid=(120.0,), holes=[(start, end2)])

    s = p.section("ChilliStraight", 137.0, 11.0, "A chilli and a long straight.")
    p.chilli(s, 137.6)
    p.mango_line(s, 139.6, 11, 0.7, 0.6)
    p.litter(s, 3)

    s = p.section("DogNeem", 148.0, 12.0, "The dog asleep in the dust, then a neem's low limb.")
    p.dog(s, 151.5)
    p.low_branch(s, 156.0)
    p.litter(s, 2, avoid=(151.5, 156.0))

    # ---- test (to 290 m)
    s = p.section("Mischief", 160.0, 12.0, "Dung; then the rooster knocks the hens' basket off a doorstep into the "
                                           "road.")
    p.dung(s, 162.5)
    p.prop(s, "hen_with_chicks", 168.6, 1.7, h=0.45)
    p.hens_basket(s, 167.0, hidden=True, ident="knocked")
    p.mischief(s, 167.6, "knocked")
    p.jump_arc(s, 167.0)
    p.litter(s, 2, avoid=(162.5, 167.0))

    s = p.section("RoofTrain", 172.0, 26.0, "Four rows in a train, a tank on the third: jump, jump, jump, and down.")
    end = row(p, s, 174.0, [PINK], ladder=True, crows=175.4)
    roof_mangoes(p, s, 175.4, end - 0.6)
    nxt = end + 1.2
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [LIME, IND])
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.6)
    nxt2 = end2 + 1.3
    gap(p, s, end2, nxt2)
    end3 = row(p, s, nxt2, [IND, LIME, PINK, IND])
    p.tank(s, nxt2 + 3.5)
    p.feather(s, nxt2 + 3.6, ROOF + 2.8, 2)
    roof_mangoes(p, s, nxt2 + 1.0, end3 - 0.6, avoid=(nxt2 + 3.5,))
    nxt3 = end3 + 1.2
    gap(p, s, end3, nxt3)
    end4 = row(p, s, nxt3, [PINK, LIME])
    p.hop_down(s, end4)
    p.litter(s, 2, holes=[(174.0, end4)])

    s = p.section("ChilliLane", 198.0, 12.0, "A breather and a chilli.")
    p.chilli(s, 198.6)
    p.mango_line(s, 200.6, 11, 0.7, 0.6)
    p.litter(s, 3)

    s = p.section("PumpGoatDog", 210.0, 14.0, "The hand pump's puddle, a goat kid, the dog.")
    p.puddle(s, 213.0)
    p.prop(s, "brass_pots", 214.15, 1.75, h=0.45)
    p.goats(s, 217.5, 1)
    p.dog(s, 222.0)
    p.litter(s, 2, avoid=(213.0, 217.5, 222.0))

    s = p.section("CotRoofs", 224.0, 22.0, "The cot up, a long row with a tank on it, a gap, and down.")
    start = cot_up(p, s, 226.0)
    end = row(p, s, start, [IND, PINK, LIME, IND])
    p.tank(s, start + 4.3)
    roof_mangoes(p, s, start + 0.5, end - 0.6, avoid=(start + 4.3,))
    nxt = end + 1.2
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [LIME, IND])
    p.hop_down(s, end2)
    p.litter(s, 2, avoid=(227.0,), holes=[(start, end2)])

    s = p.section("FinalChilli", 246.0, 10.0, "The last chilli.")
    p.chilli(s, 246.6)
    p.mango_line(s, 248.6, 9, 0.7, 0.6)
    p.litter(s, 3)

    s = p.section("LastRow", 256.0, 16.0, "The last ladder, a long row, and down onto the open road.")
    end = row(p, s, 258.0, [PINK, IND, LIME, PINK], ladder=True, crows=263.0)
    roof_mangoes(p, s, 259.4, end - 0.4)
    p.hop_down(s, end)
    p.litter(s, 2, holes=[(258.0, end)])

    s = p.section("OpenLane", 272.0, 24.0, "The lane opens out: if he is still ahead, he gets away at 290 m.")
    p.mango_line(s, 273.0, 12, 1.0, 0.6)
    p.litter(s, 3)
    return p


PROSE = [
    "## The opening: the street",
    "",
    "No basket: the chase starts in a street of flat-roofed houses with the rooster 7 m ahead (the Ready screen; tap",
    "to chase). A clean run catches him at about 72 m.",
    "",
    "## The roofs",
    "",
    "* **Up:** the bamboo ladder on a row's first house (run into it: a 0.45 s climb), or a rope cot pushed against",
    "  the wall of a house with no ladder: she bounces off its near end 2.4 m up and steps onto the 2.35 m roof as she",
    "  meets the wall (a double jump in the bounce makes it sure; without one a late bounce is a slow vault).",
    "* **Across:** gaps of 1.2 to 1.3 m between rows: a held jump (310 to 340 ms to take off), or even a tap.",
    "* **On top:** the black water tanks on their stands: jump them as on the road.",
    "* **Down:** off the end of a row, landing about 1.4 m on.",
    "",
    "## The road between",
    "",
    "Only what lies in a village street: the dog asleep in the dust, cow dung, hens and a goat kid crossing, the hand",
    "pump's puddle, a heap of sand where a house is going up, and two neems with a low limb across the road to slide",
    "under (level 2's lesson). Nothing hangs across the road and there are no pots: the rooster's mischief is the",
    "hens' basket, knocked off a doorstep into the road behind him.",
    "",
    "## The shape of it",
    "",
    "Everything runs at a small child's real pace (3.5 m/s); things to jump are about 4 m (a second and a bit) apart.",
    "Teach (to 88 m): the ladder and a row, the first gap, a neem, the cot up onto a roof, a tank on a roof. Practise",
    "(to 160 m): two gaps, the sand heap and hens, the cot then a gap, the dog and a neem. Test (to 290 m): the",
    "rooster's mischief, a train of four rows, the pump, a goat kid and the dog, the cot onto a long row, the last",
    "ladder, then the lane opens out.",
]


def main():
    p = design()
    run(p, {"level": 3, "title": "Up on the roofs", "subtitle": "Ladders, roofs and the jump between them.", "prose": PROSE})


if __name__ == "__main__":
    main()
