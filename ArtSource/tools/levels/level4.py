"""Level 4, "The canal": the fields, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level4.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level4.py --report   # also writes docs/levels/level4.md

The first level of zone 2 (levelkit.py has the shared pieces and the audit). The kid runs at a small child's real pace,
3.5 m/s, against the rooster's 3.15; the course is 295 m and the chase starts 7 m behind him (no basket), so a clean
run catches him at about 62 m. Everything on the bund road is what lies on one: irrigation canals cut across it, ducks
waddling up from them, cow dung, straw heaps at the roadside, sacks of paddy waiting for the cart, the water pots by
the well. The new thing is the canal, in three real widths:

  * 1.2 m: a held jump clears it (340 ms to take off); a tap lands in the water.
  * 1.8 m: a full held jump only just clears it (168 ms), so where it is first met it has a plank bridge: run across.
    Later, without the plank, it is a held jump or (safer) a double jump.
  * 2.6 m: only a double jump clears it (340 ms); otherwise the kid wades across at 45% speed, about 3.2 m lost.

Falling in is never a fail: she wades out (the bed is 0.28 m down, a step up). The design keeps the old level's timing
(seconds between things) at the new pace, so its distances are about half what they were:
  * Opening (-10 to 8 m): the bund between the paddies, a scarecrow and a cow.
  * Teach (to about 75 m, past the 62 m where a clean run catches him): the 1.2 m canal alone, the plank over the 1.8 m
    one, a pair of ducks crossing, a small haystack (hop onto it or over it), the 2.6 m canal with a double-jump arc of
    mangoes and a feather at its top, a breather with a chilli, the sacks of paddy (hop onto them) and cow dung.
  * Practise (to 162 m): canals in rhythm with dung, ducks and haystacks, the plank then a jump, off the sacks over a
    canal, the wide canal again, three canals in a row.
  * Test (to 295 m): the rooster's mischief (he knocks the water pots by the well into the road, a canal right after),
    every combination, all three widths in a row, a 1.8 m canal with no plank, the wide canal twice more, then the bund
    opens out.
  * Things to jump stand about 4 m apart (a second and a bit); every chilli has 11 m or more clear after it (the boost).
  * Every obstacle has the rooster's hop over it (the canals' flutters are Kit.Canal's own) and a mango line on the
    clean route; three feathers sit on the harder routes (the top of the double jump over the first wide canal, above
    the first sacks for a double jump off them, above the third small haystack).
"""
import math

from levelkit import Plan, run


def canal_jump(p, s, x, width):
    """A canal to jump, with the mangoes tracing a held jump (or, for the wide one, a double jump) across it (the zone's
    scenery has its own sluice gates in the fields)."""
    p.canal(s, x, width)
    if width < 2.0:
        p.jump_arc(s, x + width / 2)
    else:
        # the double jump's line: up, the second push at the top, down beyond the far bank
        p.arc(s, x - 0.5, width + 1.0, 2.5, 7)


def plank(p, s, x, width=1.8):
    """The 1.8 m canal with its plank bridge: mangoes along the plank say walk across."""
    p.canal(s, x, width, bridge=True)
    p.mango_line(s, x + 0.15, 4, 0.5, 0.55)


def small(p, s, x):
    """A small haystack, mangoes along its top."""
    end = p.haystack(s, x)
    p.mango_line(s, x + 0.15, 3, 0.45, 1.75)
    return end


def design():
    p = Plan(zone=2, seed=4)

    # ---- the opening: the bund between the paddies
    s = p.section("Bund", -10.0, 18.0, "The bund road between the paddies: the rooster struts ahead; tap to chase.")
    p.prop(s, "scarecrow", -4.5, 2.4, h=2.1)
    p.prop(s, "cow", 5.0, 2.8, h=1.45)
    p.decal(s, "hoof_prints", -2.0, 0.8, 1.2)
    p.mango_line(s, 2.0, 4, 1.2, 0.6)
    p.litter(s, 4)

    # ---- teach: one new thing at a time, each alone with room around it, the rooster showing the way
    s = p.section("FirstCanal", 8.0, 9.0, "The first canal, 1.2 m: a held jump clears it; the rooster flutters across first.")
    p.mango_line(s, 8.5, 3, 0.6, 0.6)
    canal_jump(p, s, 12.0, 1.2)
    p.litter(s, 2, avoid=(12.6,), holes=p.holes())

    s = p.section("Plank", 17.0, 10.0, "A 1.8 m canal, too wide for a sure jump: the plank bridge is the way across.")
    plank(p, s, 21.0)
    p.prop(s, "duck_1", 24.6, 1.6, h=0.55, mirror=True)      # the ducks' canal: they swim and waddle off the road
    p.litter(s, 2, avoid=(21.9,), holes=p.holes())

    s = p.section("Ducks", 27.0, 8.0, "Two ducks waddling up from the canal across the bund: jump them.")
    p.ducks(s, 31.0, 2)
    p.decal(s, "hoof_prints", 33.4, 1.0, 1.1)
    p.litter(s, 2, avoid=(31.0,))

    s = p.section("Haystack", 35.0, 10.0, "A small haystack at the roadside: hop onto it (mangoes along its top) or over it.")
    end = small(p, s, 38.5)
    p.mango_line(s, end + 1.0, 3, 0.6, 0.6)
    p.litter(s, 2, avoid=(39.1,))

    s = p.section("WideCanal", 45.0, 11.0, "The widest canal, 2.6 m: double jump (the mangoes show where), or wade.")
    canal_jump(p, s, 48.5, 2.6)
    p.feather(s, 49.9, 3.4, 0)
    p.prop(s, "duck_2", 53.6, 1.5, h=0.55)
    p.litter(s, 2, avoid=(49.8,), holes=p.holes())

    s = p.section("Breather", 56.0, 8.0, "Room to breathe: a wave of mangoes and the first chilli.")
    p.chilli(s, 56.5)
    for i in range(8):
        p.mango(s, 57.6 + i * 0.75, 0.8 + 0.4 * math.sin(i * 0.8))
    p.prop(s, "palmyra_1", 60.0, 5.5, h=9.0)
    p.litter(s, 2)

    s = p.section("Sacks", 64.0, 11.0, "Sacks of paddy waiting for the cart: hop onto them; a feather above for a double "
                                      "jump. Then dung.")
    p.sacks(s, 68.0)
    p.feather(s, 68.9, 3.4, 1)
    p.dung(s, 72.5)
    p.decal(s, "cart_rut", 66.0, 0.0, 2.2)
    p.litter(s, 2, avoid=(68.0, 69.0, 72.5))

    # ---- practise: the same things in pairs and rhythms, about 4 m apart
    s = p.section("CanalDung", 75.0, 10.0, "A canal, then dung: jump, land, tap.")
    canal_jump(p, s, 77.0, 1.2)
    p.dung(s, 82.0)
    p.litter(s, 2, avoid=(77.6, 82.0), holes=p.holes())

    s = p.section("Haystacks", 85.0, 13.0, "Three small haystacks: hop, hop, hop; a feather above the last.")
    for x in (86.5, 90.5, 94.5):
        small(p, s, x)
    p.feather(s, 95.1, 3.3, 2)
    p.prop(s, "granary", 91.0, 5.0, h=4.6)
    p.litter(s, 2, avoid=(87.1, 91.1, 95.1))

    s = p.section("PlankThenJump", 98.0, 11.0, "The plank, then a canal with no plank: walk, then jump.")
    plank(p, s, 100.0)
    canal_jump(p, s, 104.5, 1.2)
    p.litter(s, 2, avoid=(100.9, 105.1), holes=p.holes())

    s = p.section("ChilliStraight", 109.0, 9.0, "A long straight and a chilli to win back ground.")
    p.chilli(s, 109.5)
    p.mango_line(s, 110.8, 8, 0.9, 0.6)
    p.prop(s, "pump_house", 112.5, 4.5, h=2.9)
    p.litter(s, 2)

    s = p.section("SacksCanal", 118.0, 11.0, "Onto the sacks and off their end straight over a canal.")
    p.sacks(s, 121.0)
    canal_jump(p, s, 125.0, 1.2)
    p.litter(s, 2, avoid=(121.0, 122.0, 125.6), holes=p.holes())

    s = p.section("WideAgain", 129.0, 10.0, "The wide canal again: double jump.")
    canal_jump(p, s, 131.5, 2.6)
    p.prop(s, "duck_1", 136.8, 1.7, h=0.55)
    p.litter(s, 2, avoid=(132.8,), holes=p.holes())

    s = p.section("DucksHaystack", 139.0, 9.0, "Ducks crossing, then a small haystack.")
    p.ducks(s, 141.5, 2)
    small(p, s, 145.0)
    p.litter(s, 2, avoid=(141.5, 145.6))

    s = p.section("CanalTrio", 148.0, 14.0, "Three 1.2 m canals in a rhythm: jump, jump, jump.")
    for x in (150.0, 154.25, 158.5):
        canal_jump(p, s, x, 1.2)
    p.litter(s, 2, avoid=(150.6, 154.85, 159.1), holes=p.holes())

    # ---- test
    s = p.section("Mischief", 162.0, 13.0, "Dung; then the rooster knocks the water pots off their stand by the well "
                                         "into the road; a canal after.")
    p.dung(s, 164.0)
    p.prop(s, "water_pot_stand", 169.5, 1.7, h=1.1)     # by the well (the fields' own, behind)
    p.pots(s, 168.5, hidden=True, ident="knocked")
    p.mischief(s, 169.0, "knocked")
    p.jump_arc(s, 168.5)
    canal_jump(p, s, 171.8, 1.2)
    p.litter(s, 2, avoid=(164.0, 168.5, 172.4), holes=p.holes())

    s = p.section("PlankHaystack", 175.0, 10.0, "The plank, then a haystack.")
    plank(p, s, 176.5)
    small(p, s, 181.5)
    p.litter(s, 2, avoid=(177.4, 182.1), holes=p.holes())

    s = p.section("ChilliRun", 185.0, 9.0, "A chilli and a run of mangoes.")
    p.chilli(s, 185.5)
    p.mango_line(s, 186.8, 8, 0.9, 0.6)
    p.prop(s, "palmyra_2", 190.0, 6.0, h=9.0)
    p.litter(s, 2)

    s = p.section("CanalSacksCanal", 194.0, 15.0, "Canal, sacks, canal.")
    canal_jump(p, s, 197.0, 1.2)
    p.sacks(s, 201.5)
    canal_jump(p, s, 205.5, 1.2)
    p.litter(s, 2, avoid=(197.6, 201.5, 202.5, 206.1), holes=p.holes())

    s = p.section("WideHaystack", 209.0, 11.0, "The wide canal, then a haystack straight after it.")
    canal_jump(p, s, 210.5, 2.6)
    small(p, s, 216.5)
    p.litter(s, 2, avoid=(211.8, 217.1), holes=p.holes())

    s = p.section("DungDucks", 220.0, 9.0, "Dung, then ducks: tap, jump.")
    p.dung(s, 221.5)
    p.ducks(s, 226.0, 2)
    p.prop(s, "calf", 224.0, 2.3, h=0.95)
    p.litter(s, 2, avoid=(221.5, 226.0))

    s = p.section("FinalChilli", 229.0, 9.0, "The last chilli.")
    p.chilli(s, 229.5)
    p.mango_line(s, 230.8, 8, 0.9, 0.6)
    p.litter(s, 2)

    s = p.section("ThreeWidths", 238.0, 16.0, "All three canals in a row: jump the 1.2 m, walk the plank over the 1.8 m, "
                                            "double jump the 2.6 m.")
    canal_jump(p, s, 241.0, 1.2)
    plank(p, s, 245.0)
    canal_jump(p, s, 249.5, 2.6)
    p.litter(s, 2, avoid=(241.6, 245.9, 250.8), holes=p.holes())

    s = p.section("HaystackDung", 254.0, 12.0, "Two haystacks and dung between them.")
    small(p, s, 255.5)
    p.dung(s, 260.5)
    small(p, s, 264.0)
    p.litter(s, 2, avoid=(256.1, 260.5, 264.6))

    s = p.section("Sugarcane", 266.0, 10.0, "Past the sugarcane: a 1.8 m canal with no plank (a full jump, or a double), "
                                          "then ducks.")
    p.prop(s, "sugarcane", 267.0, 2.6, h=2.8)
    canal_jump(p, s, 268.5, 1.8)
    p.ducks(s, 273.5, 2)
    p.litter(s, 2, avoid=(269.4, 273.5), holes=p.holes())

    s = p.section("LastWide", 276.0, 12.0, "The last wide canal, and a haystack after it.")
    canal_jump(p, s, 278.0, 2.6)
    small(p, s, 284.0)
    p.prop(s, "field_shrine", 286.5, 4.0, h=4.2)
    p.litter(s, 2, avoid=(279.3, 284.6), holes=p.holes())

    s = p.section("OpenBund", 288.0, 17.0, "The bund opens out: if he is still ahead, he gets away at 295 m.")
    p.mango_line(s, 289.0, 10, 1.0, 0.6)
    p.prop(s, "hut_with_pen", 300.0, 5.5, h=3.8)
    p.litter(s, 3)
    return p


PROSE = [
    "## The opening: the bund",
    "",
    "No basket here: the chase starts on the bund between the paddies with the rooster 7 m ahead (the level's Ready",
    "screen; tap to chase). The kid runs at a small child's real pace, 3.5 m/s, and closes on him at 0.35 m a second:",
    "a clean run catches him at about 62 m, some 18 s in. A level still takes about a minute and a half.",
    "",
    "## The canal",
    "",
    "Irrigation channels cut across the bund road at the widths they really are:",
    "",
    "* **1.2 m:** a held jump clears it (340 ms to take off); a tap lands in the water.",
    "* **1.8 m:** a full held jump only just clears it (168 ms), so where it is first met it has the plank bridge: run",
    "  across. Near the end one has no plank: a full jump, or a double jump to be sure (570 ms).",
    "* **2.6 m:** only a double jump clears it (340 ms); the mangoes trace the double jump's line.",
    "* **In the water:** never a fail. She wades at 45% speed (3.2 m lost on the widest) and steps out of the 0.28 m bed.",
    "",
    "## What is on the road",
    "",
    "Only what lies on a bund road between the paddies: the canals, ducks waddling up from them (at most two), cow dung,",
    "small straw heaps at the roadside (hop onto or over), sacks of paddy waiting for the cart (a 0.8 m platform to hop",
    "onto), and the water pots by the well, which the rooster knocks into the road. No carts stand across it any more.",
    "Things to jump are about 4 m (a second and a bit) apart, and each chilli has 11 m or more of clear road after it.",
    "",
    "## The shape of it",
    "",
    "Teach (to 75 m): one new thing at a time. Practise (to 162 m): canals in rhythm with dung, ducks and haystacks, the",
    "plank then a jump, off the sacks over a canal, three canals in a row. Test (to 295 m): the rooster's mischief by",
    "the well, every combination, all three widths in a row, a 1.8 m canal without its plank, then the bund opens out.",
]


def main():
    p = design()
    run(p, {"level": 4, "title": "The canal", "subtitle": "Jump it, wade it, or take the plank.", "prose": PROSE})


if __name__ == "__main__":
    main()
