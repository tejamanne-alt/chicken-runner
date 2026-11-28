"""Level 7, "Rooftop run": the terraces, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level7.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level7.py --report   # also writes docs/levels/level7.md

The first level of zone 3 (levelkit.py has the shared pieces and the audit), on the cement road of the market and
temple street. The kid runs at a small child's real pace, 3.5 m/s, against the rooster's 3.15; the course is 300 m
and the chase starts 7 m behind him (no basket), so a clean run catches him at about 62 m. The new thing is the long
rooftop run: rows of flat-roofed houses side by side, 2.35 m up, with the gaps between houses to jump and the black
water tanks on the roofs.

  * Up: every row that does not follow a gap has the bamboo ladder on its first house: run into it and she climbs in
    0.45 s. (Without the ladder a double jump reaches the roof, or she vaults it slowly.)
  * Across: the gaps between rows are 1.1 to 1.3 m (a real gap between two houses); a held jump clears them with
    310 to 370 ms to take off, a tap with 140 to 200 ms. Missing one drops her to the lane and the next house's wall is
    a slow vault.
  * On top: water tanks (jump them), chilli and papad mats drying (harmless), crows on the parapet.
  * Down: off the end of a row she drops to the lane, landing about 1.4 m on.
  * Between the rows, the street itself, with only what lies in a real one: a vendor's hens and their basket, a goat
    kid crossing, cow dung, the puddle round the hand pump, a dog asleep, sacks of paddy unloaded at the roadside for
    a shop (hop onto them), a heap of sand where a house is going up, and one roadside neem whose low limb she slides
    under. (The washing lines strung across the street and the pot stacks are gone.)

Every distance is the old design's timing at the new pace (about 4 m between things to jump, a second and a bit), with
the rows cut to fewer houses, since a house front keeps its size. The rooster flutters up onto each row ahead of her
(Kit.RoofRow's hop), across every gap and over every tank (this plan's hops), and down off each row's end. Three
feathers sit on the harder routes: above the first gap, at the top of a double jump over a tank, and over the neem's
limb (a double jump instead of the slide).
"""
from levelkit import Plan, ROOF, run

IND, PINK, LIME = "house_indigo_veranda", "house_pink", "house_limewash"


def row(p, s, x, fronts, ladder=False, mats=(), crows=None):
    """A roof row with `fronts` (after the ladder house when `ladder`); `mats` are x positions of drying mats on it."""
    end = p.roofs(s, x, ([""] if ladder else []) + list(fronts), ladder=ladder)
    for i, mx in enumerate(mats):
        p.prop(s, "chilli_mat" if i % 2 == 0 else "papad_mat", mx, 0.95, h=0.25, y=ROOF)    # behind her line
    if crows is not None:
        p.prop(s, "crows_on_ledge", crows, 1.3, h=0.45, y=ROOF + 0.15)    # on the back parapet
    return end


def roof_mangoes(p, s, x0, x1, avoid=()):
    """A line of mangoes along a roof, at chest height, stopping short of anything to jump on it."""
    x = x0
    while x < x1:
        if not any(abs(x - a) < 1.6 for a in avoid):
            p.mango(s, x, ROOF + 0.55)
        x += 0.7


def gap(p, s, end, width):
    """The gap between two rows: the rooster's hop across, and an arc of mangoes on the jump. Returns where the next
    row starts."""
    nxt = end + width
    p.hop_gap(s, end, nxt)
    p.arc(s, end - 0.6, width + 1.2, 0.9, 3, ROOF)
    return nxt


def design():
    p = Plan(zone=3, seed=7)

    # ---- the opening: the street below the terraces
    s = p.section("Street", -10.0, 16.0, "The street under the terraces: the rooster struts ahead; tap to chase.")
    p.prop(s, "brass_vessels", -6.5, 1.5, h=0.9)
    p.prop(s, "veg_basket", -3.0, 1.3, h=0.6)
    p.prop(s, "hen_2", 3.5, 1.4, h=0.42)
    p.decal(s, "kolam_4", -1.5, -1.3, 1.2)
    p.mango_line(s, 1.0, 4, 1.0, 0.6)
    p.litter(s, 3)

    # ---- teach: one new thing at a time
    s = p.section("FirstRoofs", 6.0, 13.0, "Up the ladder onto the roofs, a run along them, and off the end.")
    end = row(p, s, 8.0, [IND, PINK], ladder=True, mats=(11.5,), crows=13.0)
    roof_mangoes(p, s, 9.6, end - 0.4)
    p.hop_down(s, end)
    p.litter(s, 2, holes=[(8.0, end)])

    s = p.section("FirstGap", 19.0, 14.0, "Two rows with a 1.2 m gap between: jump it. A feather above the gap.")
    end = row(p, s, 20.6, [LIME], ladder=True)
    nxt = gap(p, s, end, 1.2)
    p.feather(s, end + 0.6, ROOF + 1.9, 0)
    end2 = row(p, s, nxt, [PINK, IND], mats=(nxt + 2.4,))
    roof_mangoes(p, s, nxt + 1.0, end2 - 0.4)
    p.hop_down(s, end2)
    p.litter(s, 2, holes=[(20.6, end2)])

    s = p.section("FirstTank", 33.0, 16.0,
                  "A water tank on the roofs: jump it. Down, and a vendor's hen in the street.")
    end = row(p, s, 35.7, [IND, PINK], ladder=True, crows=37.2)
    p.tank(s, 39.1, ROOF)
    roof_mangoes(p, s, 37.3, end - 0.4, avoid=(39.1,))
    p.hop_down(s, end)
    p.hens(s, 47.0, 1)
    p.prop(s, "hens_basket", 48.1, 1.5, h=0.55)        # the hen's own basket at the road's edge
    p.litter(s, 2, avoid=(47.0,), holes=[(35.7, end)])

    s = p.section("Neem", 49.0, 8.0, "A roadside neem's low limb across the street: slide under. A feather above it.")
    p.low_branch(s, 53.0)
    p.feather(s, 53.0, 2.9, 2)
    p.litter(s, 2, avoid=(53.0,))

    s = p.section("Breather", 57.0, 9.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 57.5)
    p.mango_line(s, 59.0, 9, 0.75, 0.6)
    p.prop(s, "kite", 62.0, 2.0, h=0.9, y=4.2)
    p.litter(s, 2)

    s = p.section("LongRun", 66.0, 21.0, "The long run: five houses and two tanks, a gap, three more houses.")
    end = row(p, s, 67.5, [IND, PINK, LIME, IND], ladder=True, mats=(73.0,), crows=76.5)
    p.tank(s, 71.0, ROOF)
    p.tank(s, 75.0, ROOF)
    roof_mangoes(p, s, 69.1, end - 0.4, avoid=(71.0, 75.0))
    nxt = gap(p, s, end, 1.3)
    end2 = row(p, s, nxt, [PINK, LIME, IND])
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4)
    p.hop_down(s, end2)
    p.litter(s, 2, holes=[(67.5, end2)])

    # ---- practise
    s = p.section("GoatBasket", 87.0, 11.0, "A goat kid crossing, then the hens' basket.")
    p.goats(s, 90.5, 1)
    p.prop(s, "goat_eating", 88.4, 2.0, h=0.95)        # its mother, nosing at the roadside
    p.hens_basket(s, 94.5)
    p.prop(s, "hen_1", 95.6, 1.3, h=0.42)
    p.litter(s, 2, avoid=(90.5, 94.5))

    s = p.section("GapTanks", 98.0, 25.0, "Three rows, two gaps, a tank on the first two.")
    end = row(p, s, 99.5, [PINK, IND], ladder=True)
    p.tank(s, 103.0, ROOF)
    roof_mangoes(p, s, 101.1, end - 0.4, avoid=(103.0,))
    nxt = gap(p, s, end, 1.2)
    end2 = row(p, s, nxt, [IND, LIME, PINK, IND], mats=(nxt + 2.0, nxt + 6.5))
    p.tank(s, nxt + 4.2, ROOF)
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4, avoid=(nxt + 4.2,))
    nxt2 = gap(p, s, end2, 1.1)
    end3 = row(p, s, nxt2, [PINK, LIME])
    roof_mangoes(p, s, nxt2 + 0.7, end3 - 0.4)
    p.hop_down(s, end3)
    p.litter(s, 2, holes=[(99.5, end3)])

    s = p.section("ShopSacks", 123.0, 13.0,
                  "Sacks of paddy unloaded at the roadside for a shop: hop on and off. A dog asleep.")
    p.sacks(s, 126.0)
    p.dog(s, 132.0)
    p.litter(s, 2, avoid=(126.0, 127.2, 132.0))

    s = p.section("ChilliLane", 136.0, 9.0, "A chilli to win back ground.")
    p.chilli(s, 136.5)
    p.mango_line(s, 138.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("RoofTrain", 145.0, 29.0, "Four rows in a train: jump, jump, jump; a feather above the tank.")
    end = row(p, s, 146.0, [IND], ladder=True, crows=148.0)
    roof_mangoes(p, s, 147.6, end - 0.4)
    nxt = gap(p, s, end, 1.2)
    end2 = row(p, s, nxt, [LIME, IND, PINK])
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4)
    nxt2 = gap(p, s, end2, 1.3)
    end3 = row(p, s, nxt2, [IND, LIME, PINK, IND], mats=(nxt2 + 6.0,))
    p.tank(s, nxt2 + 4.0, ROOF)
    p.feather(s, nxt2 + 4.1, ROOF + 2.9, 1)
    roof_mangoes(p, s, nxt2 + 0.8, end3 - 0.4, avoid=(nxt2 + 4.0,))
    nxt3 = gap(p, s, end3, 1.1)
    end4 = row(p, s, nxt3, [PINK, LIME])
    p.hop_down(s, end4)
    p.litter(s, 2, holes=[(146.0, end4)])

    s = p.section("DungHens", 174.0, 9.0, "Cow dung, then two hens pecking in the street.")
    p.dung(s, 177.0)
    p.hens(s, 181.0, 2)
    p.litter(s, 2, avoid=(177.0, 181.0))

    # ---- test
    s = p.section("Mischief", 183.0, 13.0,
                  "The hand-pump puddle; the rooster knocks the hens' basket into the street; a goat kid.")
    p.puddle(s, 186.5)
    p.prop(s, "hens_basket", 190.9, 1.4, h=0.55)
    p.hens_basket(s, 190.5, hidden=True, ident="knocked")
    p.mischief(s, 191.0, "knocked")
    p.jump_arc(s, 190.5)
    p.goats(s, 194.5, 1)
    p.litter(s, 2, avoid=(186.5, 190.5, 194.5))

    s = p.section("LongTanks", 196.0, 26.0, "The long run again: three tanks and a gap, then down.")
    end = row(p, s, 197.5, [IND, PINK, LIME, IND], ladder=True, mats=(203.0,), crows=206.5)
    p.tank(s, 201.0, ROOF)
    p.tank(s, 205.0, ROOF)
    roof_mangoes(p, s, 199.1, end - 0.4, avoid=(201.0, 205.0))
    nxt = gap(p, s, end, 1.2)
    end2 = row(p, s, nxt, [PINK, IND, LIME, PINK])
    p.tank(s, nxt + 3.8, ROOF)
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4, avoid=(nxt + 3.8,))
    p.hop_down(s, end2)
    p.litter(s, 2, holes=[(197.5, end2)])

    s = p.section("SandDogBasket", 222.0, 13.0, "A house going up (its sand heap), the dog, the hens' basket.")
    p.sand(s, 225.0)
    p.dog(s, 229.0)
    p.hens_basket(s, 233.0)
    p.litter(s, 2, avoid=(225.0, 229.0, 233.0))

    s = p.section("FinalChilli", 235.0, 9.0, "The last chilli.")
    p.chilli(s, 235.5)
    p.mango_line(s, 237.0, 9, 0.75, 0.6)
    p.litter(s, 2)

    s = p.section("LastRoofs", 244.0, 33.0, "The last long run: two tanks, a gap, a tank, a gap; down.")
    end = row(p, s, 245.5, [IND, PINK, LIME, IND], ladder=True, mats=(251.0,), crows=254.5)
    p.tank(s, 249.0, ROOF)
    p.tank(s, 253.0, ROOF)
    roof_mangoes(p, s, 247.1, end - 0.4, avoid=(249.0, 253.0))
    nxt = gap(p, s, end, 1.2)
    end2 = row(p, s, nxt, [IND, PINK, LIME, IND])
    p.tank(s, nxt + 4.2, ROOF)
    roof_mangoes(p, s, nxt + 0.8, end2 - 0.4, avoid=(nxt + 4.2,))
    nxt2 = gap(p, s, end2, 1.3)
    end3 = row(p, s, nxt2, [PINK, LIME, IND])
    roof_mangoes(p, s, nxt2 + 0.7, end3 - 0.4)
    p.hop_down(s, end3)
    p.litter(s, 2, holes=[(245.5, end3)])

    s = p.section("LastTest", 277.0, 13.0, "The hens' basket, a goat kid, cow dung: the last test.")
    p.hens_basket(s, 280.0)
    p.goats(s, 284.0, 1)
    p.dung(s, 288.0)
    p.litter(s, 2, avoid=(280.0, 284.0, 288.0))

    s = p.section("OpenStreet", 290.0, 18.0, "The street opens out: if he is still ahead, he gets away at 300 m.")
    p.mango_line(s, 291.0, 10, 1.0, 0.6)
    p.prop(s, "brass_vessels", 299.0, 1.6, h=0.9)
    p.prop(s, "veg_basket", 301.0, 1.3, h=0.6, mirror=True)
    p.litter(s, 3)
    return p


PROSE = [
    "## The opening: the street",
    "",
    "No basket here: the chase starts in the street under the terraces with the rooster 7 m ahead (the level's Ready",
    "screen; tap to chase). The kid runs 3.5 m/s, a small child's real pace, and the rooster 3.15: a clean run closes",
    "0.35 m a second and catches him at about 62 m. The course is 300 m, about a minute and a half.",
    "",
    "## The roofs",
    "",
    "* **Up:** every row that does not follow a gap has the bamboo ladder on its first house: run into it and she",
    "  climbs in 0.45 s. Without one, a double jump reaches the 2.35 m roof, or she vaults it slowly.",
    "* **Across:** the gaps are 1.1 to 1.3 m, a real gap between two houses; a held jump clears them with 310 to 370 ms",
    "  to take off, a tap with 140 to 200 ms. Missing one drops her to the lane, and the next house's wall is a slow vault.",
    "* **On top:** black water tanks to jump; chilli and papad mats drying, crows on the parapets.",
    "* **Down:** off a row's end she drops to the lane, about 1.4 m on.",
    "* **Rows:** two to five houses (a house front keeps its size, so the rows are shorter than at the old pace, and",
    "  take about as long to run).",
    "",
    "## The street between the rows",
    "",
    "Only what lies in a real street, spaced about 4 m (a second and a bit) apart: a vendor's hens and their basket, a",
    "goat kid crossing, cow dung, the puddle round the hand pump, a dog asleep, sacks of paddy unloaded at the roadside",
    "for a shop (hop onto them and off), a heap of sand where a house is going up, and one roadside neem whose low",
    "limb she slides under. The washing lines strung across the street are gone, and so are the pot stacks.",
    "",
    "## The shape of it",
    "",
    "Teach (to 87 m): the ladder and one row, one gap, one tank, the neem back on the lane, a chilli, then the long run.",
    "Practise (to 183 m): a goat and the basket, gaps and tanks together, the sacks and the dog, a train of four rows.",
    "Test (to 300 m): the rooster's mischief with the hens' basket, the long run with three tanks, the sand heap and the",
    "dog, the last long run, the last three things in the street, and the street opens out.",
]


def main():
    p = design()
    run(p, {"level": 7, "title": "Rooftop run", "subtitle": "Mind the gaps and the water tanks.", "prose": PROSE})


if __name__ == "__main__":
    main()
