"""Level 7, "Rooftop run": the terraces, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level7.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level7.py --report   # also writes docs/levels/level7.md

The first level of zone 3 (levelkit.py has the shared pieces and the audit). The kid runs at 8 m/s against the
rooster's 7.4, the course is 700 m and the chase starts 12 m behind him (no basket). The new thing is the long rooftop
run: rows of flat-roofed houses side by side, 2.35 m up, with the gaps between houses to jump and the black water
tanks on the roofs.

  * Up: every row that does not follow a gap has the bamboo ladder on its first house: run into it and she climbs in
    0.45 s. (Without the ladder a double jump reaches the roof, or she vaults it slowly.)
  * Across: the gaps between rows are 1.8 to 2.2 m; a held jump clears them with 370 to 420 ms to spare, a tap too.
    Missing one drops her to the lane and the next house's wall is a slow vault.
  * On top: water tanks (jump them, as pot stacks), chilli and papad mats drying (harmless), crows on the parapet.
  * Down: off the end of the last row she drops to the lane, landing about 3.2 m on.
  * Between the rows, the lane: clotheslines (slide, learnt in level 2), pot stacks, the hens' basket.

The rooster flutters up onto each row ahead of her (Kit.RoofRow's hop), across every gap and over every tank (this
plan's hops), and down off each row's end. Three feathers sit on the harder routes: above the first gap, at the top of
a double jump over a tank, and over a clothesline (a double jump instead of the slide).
"""
from levelkit import Plan, ROOF, run

IND, PINK, LIME = "house_indigo_veranda", "house_pink", "house_limewash"


def row(p, s, x, fronts, ladder=False, mats=(), crows=None):
    """A roof row with mangoes along its top; `mats` are x positions of drying mats on it."""
    end = p.roofs(s, x, ([""] if ladder else []) + list(fronts), ladder=ladder)
    for i, mx in enumerate(mats):
        p.prop(s, "chilli_mat" if i % 2 == 0 else "papad_mat", mx, 0.3, h=0.25, y=ROOF)
    if crows is not None:
        p.prop(s, "crows_on_ledge", crows, 0.55, h=0.45, y=ROOF + 0.15)
    return end


def roof_mangoes(p, s, x0, x1, avoid=()):
    """A line of mangoes along a roof, at chest height, stopping short of anything to jump on it."""
    x = x0
    while x < x1:
        if not any(abs(x - a) < 2.4 for a in avoid):
            p.mango(s, x, ROOF + 0.55)
        x += 0.8


def gap(p, s, end, nxt):
    """The gap between two rows: the rooster's hop across, and an arc of mangoes on the jump."""
    p.hop_gap(s, end, nxt)
    p.arc(s, end - 1.2, nxt - end + 2.4, 1.1, 3, ROOF)


def tank(p, s, x):
    p.tank(s, x, ROOF)


def design():
    p = Plan(zone=3, seed=7)

    # ---- the opening: the street below the terraces
    s = p.section("Street", -10.0, 24.0, "The street under the terraces: the rooster struts ahead; tap to chase.")
    p.prop(s, "brass_vessels", -6.5, 1.5, h=0.9)
    p.prop(s, "veg_basket", -3.0, 1.3, h=0.6)
    p.prop(s, "coconut_cart", 4.0, 2.8, h=2.7)
    p.prop(s, "bunting", 9.0, 1.6, h=0.7, y=2.4)
    p.prop(s, "hen_2", 11.0, 1.4, h=0.42)
    p.decal(s, "kolam_4", -1.5, -1.3, 1.2)
    p.mango_line(s, 2.0, 5, 2.0, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstRoofs", 14.0, 26.0, "Up the ladder onto the roofs, a run along them, and off the end.")
    end = row(p, s, 20.0, [IND, PINK, LIME, IND, PINK], ladder=True, mats=(27.0,), crows=30.5)
    roof_mangoes(p, s, 23.0, end - 0.5)
    p.hop_down(s, end)
    p.litter(s, 2, holes=[(20.0, end)])

    s = p.section("FirstGap", 40.0, 26.0, "Two rows with a 2 m gap between: jump it. A feather above the gap.")
    end = row(p, s, 42.0, [IND, LIME], ladder=True)
    nxt = end + 2.0
    gap(p, s, end, nxt)
    p.feather(s, end + 1.0, ROOF + 1.9, 0)
    end2 = row(p, s, nxt, [PINK, IND, LIME, PINK], mats=(nxt + 3.0,))
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.5)
    p.hop_down(s, end2)
    p.litter(s, 2, holes=[(42.0, end2)])

    s = p.section("FirstTank", 66.0, 28.0, "A water tank on the roofs: jump it like a pot stack.")
    end = row(p, s, 68.0, [IND, PINK, IND, LIME], ladder=True, crows=69.5)
    tank(p, s, 74.0)
    roof_mangoes(p, s, 71.0, end - 0.5, avoid=(74.0,))
    p.hop_down(s, end)
    p.pots(s, 88.5)
    p.litter(s, 2, avoid=(88.5,), holes=[(68.0, end)])

    s = p.section("Clothesline", 94.0, 18.0, "Back on the lane: a clothesline across it. Slide under.")
    p.clothesline(s, 102.0)
    p.prop(s, "brass_vessels", 106.5, 1.6, h=0.9)
    p.litter(s, 2, avoid=(102.0,))

    s = p.section("Breather", 112.0, 18.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 113.0)
    p.mango_line(s, 115.5, 10, 1.3, 0.6)
    p.prop(s, "kite", 122.0, 2.0, h=0.9, y=4.2)
    p.litter(s, 3)

    s = p.section("LongRun", 130.0, 40.0, "The long run: eleven houses and two tanks, a gap, four more houses.")
    end = row(p, s, 133.0, [IND, PINK, LIME, IND, PINK, LIME, IND, PINK, LIME, IND], ladder=True, mats=(143.0, 151.0),
              crows=144.0)
    tank(p, s, 138.5)
    tank(p, s, 146.5)
    roof_mangoes(p, s, 136.0, end - 0.5, avoid=(138.5, 146.5))
    nxt = end + 2.2
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [PINK, IND, LIME, PINK])
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.5)
    p.hop_down(s, end2)
    p.litter(s, 2, holes=[(133.0, end2)])

    # ---- practise
    s = p.section("PotsHens", 170.0, 20.0, "A pot stack, then the hens' basket.")
    p.pots(s, 175.5)
    p.hens_basket(s, 184.0)
    p.prop(s, "hen_1", 185.5, 1.3, h=0.42)
    p.litter(s, 2, avoid=(175.5, 184.0))

    s = p.section("GapTanks", 190.0, 48.0, "Three rows, two gaps, a tank on the first two.")
    end = row(p, s, 193.0, [PINK, IND, LIME, IND, PINK], ladder=True)
    tank(p, s, 198.0)
    roof_mangoes(p, s, 196.0, end - 0.5, avoid=(198.0,))
    nxt = end + 1.8
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [IND, PINK, LIME, IND, PINK, LIME, IND, PINK], mats=(nxt + 3.0, nxt + 12.0))
    tank(p, s, nxt + 7.5)
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.5, avoid=(nxt + 7.5,))
    nxt2 = end2 + 2.0
    gap(p, s, end2, nxt2)
    end3 = row(p, s, nxt2, [PINK, LIME, IND])
    roof_mangoes(p, s, nxt2 + 0.8, end3 - 0.5)
    p.hop_down(s, end3)
    p.litter(s, 2, holes=[(193.0, end3)])

    s = p.section("Clotheslines", 238.0, 24.0, "Two clotheslines: slide, slide. A feather over the second.")
    p.clothesline(s, 243.0)
    p.clothesline(s, 252.0)
    p.feather(s, 252.0, 2.9, 2)
    p.litter(s, 2, avoid=(243.0, 252.0))

    s = p.section("ChilliLane", 262.0, 18.0, "A chilli to win back ground.")
    p.chilli(s, 263.0)
    p.mango_line(s, 265.5, 10, 1.3, 0.6)
    p.prop(s, "stall_veg", 272.0, 3.2)
    p.litter(s, 3)

    s = p.section("RoofTrain", 280.0, 52.0, "Four rows in a train: jump, jump, jump; a feather above the tank.")
    end = row(p, s, 284.0, [IND, PINK], ladder=True, crows=286.0)
    roof_mangoes(p, s, 287.0, end - 0.5)
    nxt = end + 2.0
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [LIME, IND, PINK, LIME])
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.5)
    nxt2 = end2 + 2.2
    gap(p, s, end2, nxt2)
    end3 = row(p, s, nxt2, [IND, LIME, PINK, IND, LIME, PINK, IND, LIME], mats=(nxt2 + 3.0,))
    tank(p, s, nxt2 + 7.1)
    p.feather(s, nxt2 + 7.2, ROOF + 2.9, 1)
    roof_mangoes(p, s, nxt2 + 1.0, end3 - 0.5, avoid=(nxt2 + 7.1,))
    nxt3 = end3 + 1.8
    gap(p, s, end3, nxt3)
    end4 = row(p, s, nxt3, [PINK, LIME, IND])
    p.hop_down(s, end4)
    p.litter(s, 2, holes=[(284.0, end4)])

    s = p.section("PotsPair", 332.0, 20.0, "Two pot stacks.")
    p.pots(s, 336.0)
    p.pots(s, 344.0)
    p.litter(s, 2, avoid=(336.0, 344.0))

    # ---- test
    s = p.section("Mischief", 352.0, 26.0, "A pot stack; the rooster knocks the hens' basket into the lane; a clothesline.")
    p.pots(s, 357.0)
    p.prop(s, "hens_basket", 365.4, 1.4, h=0.55)
    p.hens_basket(s, 365.0, hidden=True, ident="knocked")
    p.mischief(s, 366.0, "knocked")
    p.jump_arc(s, 365.0)
    p.clothesline(s, 374.0)
    p.litter(s, 2, avoid=(357.0, 365.0, 374.0))

    s = p.section("LongTanks", 378.0, 54.0, "The long run again, three tanks, a gap; down, and pots.")
    end = row(p, s, 382.0, [IND, PINK, LIME, IND, PINK, LIME, IND, PINK, LIME, IND], ladder=True, mats=(391.5, 399.5),
              crows=392.5)
    tank(p, s, 387.5)
    tank(p, s, 395.5)
    roof_mangoes(p, s, 385.0, end - 0.5, avoid=(387.5, 395.5))
    nxt = end + 2.2
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [IND, PINK, LIME, IND, PINK, LIME, IND])
    tank(p, s, nxt + 7.1)
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.5, avoid=(nxt + 7.1,))
    p.hop_down(s, end2)
    p.pots(s, 428.0)
    p.litter(s, 2, avoid=(428.0,), holes=[(382.0, end2)])

    s = p.section("ChilliStraight", 432.0, 20.0, "A chilli and a long straight.")
    p.chilli(s, 433.0)
    p.mango_line(s, 435.5, 10, 1.3, 0.6)
    p.prop(s, "coconut_cart", 442.0, 3.0, h=2.7, mirror=True)
    p.litter(s, 3)

    s = p.section("ClothesPotsHens", 452.0, 28.0, "Clothesline, pots, the hens' basket.")
    p.clothesline(s, 456.0)
    p.pots(s, 462.5)
    p.hens_basket(s, 471.0)
    p.litter(s, 2, avoid=(456.0, 462.5, 471.0))

    s = p.section("GapRun", 480.0, 50.0, "Four rows, three gaps, a tank in the third row.")
    end = row(p, s, 482.0, [PINK, IND, LIME], ladder=True)
    roof_mangoes(p, s, 485.0, end - 0.5)
    nxt = end + 2.0
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [IND, LIME, PINK, LIME])
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.5)
    nxt2 = end2 + 2.2
    gap(p, s, end2, nxt2)
    end3 = row(p, s, nxt2, [PINK, IND, LIME, IND, PINK, LIME, IND, PINK], crows=nxt2 + 11.0)
    tank(p, s, nxt2 + 7.2)
    roof_mangoes(p, s, nxt2 + 1.0, end3 - 0.5, avoid=(nxt2 + 7.2,))
    nxt3 = end3 + 1.8
    gap(p, s, end3, nxt3)
    end4 = row(p, s, nxt3, [LIME, PINK, IND])
    p.hop_down(s, end4)
    p.litter(s, 2, holes=[(482.0, end4)])

    s = p.section("HensPots", 530.0, 22.0, "The hens' basket, then pots.")
    p.hens_basket(s, 535.0)
    p.pots(s, 543.5)
    p.litter(s, 2, avoid=(535.0, 543.5))

    s = p.section("FinalChilli", 552.0, 20.0, "The last chilli.")
    p.chilli(s, 553.0)
    p.mango_line(s, 555.5, 10, 1.3, 0.6)
    p.prop(s, "bunting", 562.0, 1.6, h=0.7, y=2.4)
    p.litter(s, 3)

    s = p.section("LastRoofs", 572.0, 64.0, "The last long run: two tanks, a gap, a tank, a gap; down, a clothesline.")
    end = row(p, s, 575.0, [IND, PINK, LIME, IND, PINK, LIME, IND, PINK, LIME, IND], ladder=True, mats=(584.5,),
              crows=592.0)
    tank(p, s, 580.5)
    tank(p, s, 588.5)
    roof_mangoes(p, s, 578.0, end - 0.5, avoid=(580.5, 588.5))
    nxt = end + 2.0
    gap(p, s, end, nxt)
    end2 = row(p, s, nxt, [IND, PINK, LIME, IND, PINK, LIME, IND, PINK])
    tank(p, s, nxt + 7.3)
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.5, avoid=(nxt + 7.3,))
    nxt2 = end2 + 2.2
    gap(p, s, end2, nxt2)
    end3 = row(p, s, nxt2, [PINK, IND, LIME])
    roof_mangoes(p, s, nxt2 + 0.8, end3 - 0.5)
    p.hop_down(s, end3)
    p.clothesline(s, 631.0)
    p.litter(s, 2, avoid=(631.0,), holes=[(575.0, end3)])

    s = p.section("LastTest", 636.0, 32.0, "Pots, a clothesline, the hens' basket, pots.")
    p.pots(s, 639.0)
    p.clothesline(s, 648.0)
    p.hens_basket(s, 654.0)
    p.pots(s, 662.0)
    p.mango_line(s, 665.0, 2, 1.3, 0.6)
    p.litter(s, 3, avoid=(639.0, 648.0, 654.0, 662.0))

    s = p.section("OpenStreet", 668.0, 38.0, "The street opens out: if he is still ahead, he gets away at 700 m.")
    p.mango_line(s, 670.0, 14, 1.4, 0.6)
    p.prop(s, "brass_vessels", 690.0, 1.6, h=0.9)
    p.prop(s, "veg_basket", 692.0, 1.3, h=0.6, mirror=True)
    p.prop(s, "stall_sweets", 699.0, 3.2)
    p.litter(s, 4)
    return p


PROSE = [
    "## The opening: the street",
    "",
    "No basket here: the chase starts in the street under the terraces with the rooster 12 m ahead (the level's Ready",
    "screen; tap to chase). A clean run closes 0.6 m a second and catches him at about 149 m.",
    "",
    "## The roofs",
    "",
    "* **Up:** every row that does not follow a gap has the bamboo ladder on its first house: run into it and she",
    "  climbs in 0.45 s. Without one, a double jump reaches the 2.35 m roof, or she vaults it slowly.",
    "* **Across:** the gaps are 1.8 to 2.2 m; a held jump clears them with 370 to 420 ms to take off, a tap too. Missing",
    "  one drops her to the lane, and the next house's wall is a slow vault.",
    "* **On top:** black water tanks to jump like pot stacks; chilli and papad mats drying, crows on the parapets.",
    "* **Down:** off the last row's end she drops to the lane, about 3.2 m on.",
    "* **Between the rows:** clotheslines to slide under (learnt in level 2), pot stacks, the hens' basket.",
    "",
    "## The shape of it",
    "",
    "Teach (to 170 m): the ladder and one row, one gap, one tank, a clothesline back on the lane, then the long run.",
    "Practise (to 328 m): gaps and tanks together, two clotheslines, a train of four rows. Test (to 700 m): the",
    "rooster's mischief with the hens' basket, the long run with three tanks, rows of gaps, the last ladder.",
]


def main():
    p = design()
    run(p, {"level": 7, "title": "Rooftop run", "subtitle": "Mind the gaps and the water tanks.", "prose": PROSE})


if __name__ == "__main__":
    main()
