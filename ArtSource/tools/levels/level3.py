"""Level 3, "Up on the roofs": the lane's houses, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level3.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level3.py --report   # also writes docs/levels/level3.md

The last level of zone 1 (6 m/s against 5.5, 500 m, a 12 m start: no basket). New, from the doc's level table: houses,
ladders and the first rooftop stretch.

  * Up: run into the bamboo ladder on a row's first house and she climbs it in 0.45 s. Or bounce off a rope cot set just
    before a row (its 2.9 m bounce lands her on the 2.35 m roof). Without either, a double jump, or a slow vault.
  * Across: gaps of 1.8 to 2.2 m between rows; a held jump clears them with 290 to 360 ms to spare.
  * On top: pot stacks drying on the roofs, jumped as on the lane.
  * Down: off the end of a row, landing about 2.4 m on.

Between the rows the lane keeps the zone's things: clotheslines, pots, dung, the dog. Feathers on the harder routes:
above the first gap, at the top of a cot's bounce, above a pot stack on a roof.
"""
import math

from levelkit import Plan, ROOF, run

IND, PINK, LIME = "house_indigo_veranda", "house_pink", "house_limewash"


def row(p, s, x, fronts, ladder=False, crows=None):
    end = p.roofs(s, x, ([""] if ladder else []) + list(fronts), ladder=ladder)
    if crows is not None:
        p.prop(s, "crows_on_ledge", crows, 0.55, h=0.45, y=ROOF + 0.15)
    return end


def roof_mangoes(p, s, x0, x1, avoid=()):
    x = x0
    while x < x1:
        if not any(abs(x - a) < 2.0 for a in avoid):
            p.mango(s, x, ROOF + 0.55)
        x += 0.8


def gap(p, s, end, nxt):
    p.hop_gap(s, end, nxt)
    p.arc(s, end - 1.0, nxt - end + 2.0, 1.0, 3, ROOF)


def design():
    p = Plan(zone=1, seed=3)

    # ---- the opening: the street of houses
    s = p.section("Street", -10.0, 24.0, "A street of flat-roofed houses: the rooster struts ahead; tap to chase.")
    p.prop(s, "kids_rolling_tyre", -5.5, 2.3, h=1.2)
    p.prop(s, "tulsi_planter", 1.5, 1.8, h=1.1)
    p.prop(s, "woman_carrying_pot", 7.5, 2.1, h=1.5, mirror=True)
    p.decal(s, "kolam_5", -1.0, 1.0, 1.0)
    p.mango_line(s, 2.0, 5, 2.0, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstLadder", 14.0, 24.0, "The first ladder: run into it and she climbs; along the roofs, and off the end.")
    end = row(p, s, 20.0, [PINK, LIME, IND], ladder=True, crows=24.5)
    roof_mangoes(p, s, 22.5, end - 0.4)
    p.hop_down(s, end)
    p.litter(s, 2, holes=[(20.0, end)])

    s = p.section("FirstGap", 38.0, 24.0, "Two rows with a 1.8 m gap: jump across. A feather above the gap.")
    end = row(p, s, 41.0, [IND], ladder=True)
    nxt = end + 1.8
    gap(p, s, end, nxt)
    p.feather(s, end + 0.9, ROOF + 1.9, 0)
    end2 = row(p, s, nxt, [PINK, LIME, IND])
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4)
    p.hop_down(s, end2)
    p.litter(s, 2, holes=[(41.0, end2)])

    s = p.section("Clothesline", 62.0, 16.0, "Back on the lane: a clothesline. Slide.")
    p.clothesline(s, 70.0)
    p.litter(s, 2, avoid=(70.0,))

    s = p.section("CotUp", 78.0, 24.0, "A rope cot before a house with no ladder: bounce up onto its roof.")
    p.cot(s, 82.0, onto_roof=True)
    end = row(p, s, 84.9, [IND, PINK, LIME, IND])
    roof_mangoes(p, s, 86.5, end - 0.4)
    p.hop_down(s, end)
    p.litter(s, 2, avoid=(83.0,), holes=[(84.9, end)])

    s = p.section("Breather", 102.0, 16.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 103.0)
    for i in range(9):
        p.mango(s, 105.0 + i * 1.2, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 3)

    s = p.section("RoofPots", 118.0, 30.0, "A long row with a pot stack drying on the roof: jump it up there.")
    end = row(p, s, 121.0, [IND, PINK, LIME, IND, PINK], ladder=True, crows=131.5)
    p.pots(s, 127.0, y=ROOF)
    roof_mangoes(p, s, 123.5, end - 0.4, avoid=(127.0,))
    p.hop_down(s, end)
    p.dung(s, 142.5)
    p.litter(s, 2, avoid=(142.5,), holes=[(121.0, end)])

    # ---- practise
    s = p.section("GapGap", 148.0, 34.0, "Three rows, two gaps.")
    end = row(p, s, 151.0, [PINK, IND], ladder=True)
    roof_mangoes(p, s, 153.5, end - 0.4)
    nxt = end + 2.0
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [LIME, IND, PINK])
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4)
    nxt2 = end2 + 2.2
    gap(p, s, end2, nxt2)
    end3 = row(p, s, nxt2, [IND, LIME])
    p.hop_down(s, end3)
    p.litter(s, 2, holes=[(151.0, end3)])

    s = p.section("LinePots", 182.0, 18.0, "A clothesline, then pots.")
    p.clothesline(s, 186.0)
    p.pots(s, 194.0)
    p.litter(s, 2, avoid=(186.0, 194.0))

    s = p.section("CotUpGap", 200.0, 34.0, "The cot up onto a roof, a gap, and a pot stack on the next roof.")
    p.cot(s, 203.0, onto_roof=True)
    p.feather(s, 205.6, 4.4, 1)
    end = row(p, s, 205.9, [PINK, LIME, IND])
    roof_mangoes(p, s, 207.5, end - 0.4)
    nxt = end + 1.8
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [IND, PINK, LIME, IND, PINK])
    p.pots(s, nxt + 5.6, y=ROOF)
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4, avoid=(nxt + 5.6,))
    p.hop_down(s, end2)
    p.litter(s, 2, avoid=(204.0,), holes=[(205.9, end2)])

    s = p.section("ChilliStraight", 234.0, 18.0, "A chilli and a long straight.")
    p.chilli(s, 235.0)
    p.mango_line(s, 237.5, 10, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("DogLine", 252.0, 20.0, "The dog, then a clothesline.")
    p.dog(s, 256.5)
    p.clothesline(s, 266.0)
    p.litter(s, 2, avoid=(256.5, 266.0))

    # ---- test
    s = p.section("Mischief", 272.0, 26.0, "Dung; the rooster knocks the pots off their stand; then a ladder.")
    p.dung(s, 276.0)
    p.prop(s, "water_pot_stand", 284.3, 1.6, h=1.1)
    p.pots(s, 284.0, hidden=True, ident="knocked")
    p.mischief(s, 285.0, "knocked")
    p.jump_arc(s, 284.0)
    p.litter(s, 2, avoid=(276.0, 284.0))

    s = p.section("RoofTrain", 298.0, 46.0, "Four rows in a train, a pot stack on the third: jump, jump, jump, and down.")
    end = row(p, s, 300.0, [IND, PINK], ladder=True, crows=302.0)
    roof_mangoes(p, s, 302.5, end - 0.4)
    nxt = end + 2.0
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [LIME, IND, PINK])
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4)
    nxt2 = end2 + 2.2
    gap(p, s, end2, nxt2)
    end3 = row(p, s, nxt2, [IND, LIME, PINK, IND, LIME, PINK])
    p.pots(s, nxt2 + 5.4, y=ROOF)
    p.feather(s, nxt2 + 5.5, ROOF + 2.9, 2)
    roof_mangoes(p, s, nxt2 + 0.8, end3 - 0.4, avoid=(nxt2 + 5.4,))
    nxt3 = end3 + 1.8
    gap(p, s, end3, nxt3)
    end4 = row(p, s, nxt3, [PINK, IND])
    p.hop_down(s, end4)
    p.litter(s, 2, holes=[(300.0, end4)])

    s = p.section("ChilliLane", 344.0, 18.0, "A breather and a chilli.")
    p.chilli(s, 345.0)
    p.mango_line(s, 347.5, 9, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("LinePotsDog", 362.0, 28.0, "Clothesline, pots, the dog.")
    p.clothesline(s, 366.0)
    p.pots(s, 373.5)
    p.dog(s, 381.5)
    p.litter(s, 2, avoid=(366.0, 373.5, 381.5))

    s = p.section("CotRoofs", 390.0, 40.0, "The cot up, a long row with pots on it, a gap, and down.")
    p.cot(s, 393.0, onto_roof=True)
    end = row(p, s, 395.9, [IND, PINK, LIME, IND, PINK, LIME, IND])
    p.pots(s, 403.5, y=ROOF)
    roof_mangoes(p, s, 397.5, end - 0.4, avoid=(403.5,))
    nxt = end + 2.0
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [LIME, IND, PINK])
    p.hop_down(s, end2)
    p.litter(s, 2, avoid=(394.0,), holes=[(395.9, end2)])

    s = p.section("FinalChilli", 430.0, 16.0, "The last chilli.")
    p.chilli(s, 431.0)
    p.mango_line(s, 433.5, 8, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("LastRow", 446.0, 28.0, "The last ladder, a long row, and down onto the open lane.")
    end = row(p, s, 449.0, [PINK, IND, LIME, IND, PINK, LIME], ladder=True, crows=455.0)
    roof_mangoes(p, s, 451.5, end - 0.4)
    p.hop_down(s, end)
    p.litter(s, 2, holes=[(449.0, end)])

    s = p.section("OpenLane", 474.0, 32.0, "The lane opens out: if he is still ahead, he gets away at 500 m.")
    p.mango_line(s, 476.0, 12, 1.4, 0.6)
    p.litter(s, 4)
    return p


PROSE = [
    "## The opening: the street",
    "",
    "No basket: the chase starts in a street of flat-roofed houses with the rooster 12 m ahead (the Ready screen; tap",
    "to chase). A clean run catches him at about 110 m.",
    "",
    "## The roofs",
    "",
    "* **Up:** the bamboo ladder on a row's first house (run into it: a 0.45 s climb), or a rope cot set just before a",
    "  row with no ladder (its 2.9 m bounce lands her on the 2.35 m roof).",
    "* **Across:** gaps of 1.8 to 2.2 m between rows: a held jump.",
    "* **On top:** pot stacks drying on the roofs: jump them as on the lane.",
    "* **Down:** off the end of a row, landing about 2.4 m on.",
    "",
    "## The shape of it",
    "",
    "Teach (to 148 m): the ladder and a row, the first gap, a clothesline, the cot up onto a roof, pots on a roof.",
    "Practise (to 272 m): two gaps, the cot then a gap, the dog and a line. Test (to 500 m): the rooster's mischief, a",
    "train of four rows, the cot onto a long row, the last ladder, then the lane opens out.",
]


def main():
    p = design()
    run(p, {"level": 3, "title": "Up on the roofs", "subtitle": "Ladders, roofs and the jump between them.", "prose": PROSE})


if __name__ == "__main__":
    main()
