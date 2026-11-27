"""Level 4, "The canal": the fields, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level4.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level4.py --report   # also writes docs/levels/level4.md

The first level of zone 2 (levelkit.py has the shared pieces and the audit). The kid is faster here (7 m/s against
the rooster's 6.4), the course is 600 m and the chase starts 12 m behind him (no basket). The new thing is the
irrigation canal across the bund path, in the doc's three widths:

  * 2.5 m: a held jump clears it comfortably (290 ms to take off); a tap lands in the water.
  * 3.5 m: a held jump is a gamble (under 150 ms), so it always has the plank bridge: run across. Later, without the
    plank, it is the double jump's.
  * 4.5 m: only a double jump clears it (405 ms); otherwise the kid wades across at 45% speed, about 5.5 m lost.

Falling in is never a fail: she wades out (the bed is 0.28 m down, a step up). The design:
  * Opening (-10 to 14 m): the bund between the paddies, a scarecrow, paddy and a cow.
  * Teach (to about 150 m, past the 131 m where a clean run catches him): the 2.5 m canal alone, the plank over the
    3.5 m one, cow dung (known from the lane), the small haystack (hop onto it or over it), the 4.5 m canal with a
    double-jump arc of mangoes and a feather at its top, a breather with a chilli, the bullock cart.
  * Practise (to 316 m): canals in rhythm with dung and haystacks, the plank then a jump, the cart into a canal, the
    wide canal again, three canals in a row.
  * Test (to 600 m): the rooster's mischief (he knocks the pots by the well into the lane, a canal right after),
    every combination, the wide canal twice more, then the bund opens out.
  * Every obstacle has the rooster's hop over it (the canals' flutters are Kit.Canal's own) and a mango line on the
    clean route; three feathers sit on the harder routes (the top of the double jump over the first wide canal, above
    the cart's bed, above the third small haystack).
"""
import math

from levelkit import Plan, run


def canal_jump(p, s, x, width):
    """A canal to jump, with the mangoes tracing a held jump (or, for the wide one, a double jump) across it (the zone's
    scenery has its own sluice gates in the fields)."""
    p.canal(s, x, width)
    if width <= 3.0:
        p.jump_arc(s, x + width / 2)
    else:
        # the double jump's line: up, the second push at the top, down beyond the far bank
        p.arc(s, x - 1.6, width + 3.2, 2.3, 7)


def plank(p, s, x, width=3.5):
    """The 3.5 m canal with its plank bridge: mangoes along the plank say walk across."""
    p.canal(s, x, width, bridge=True)
    p.mango_line(s, x + 0.1, 5, 0.75, 0.55)


def design():
    p = Plan(zone=2, seed=4)

    # ---- the opening: the bund between the paddies
    s = p.section("Bund", -10.0, 24.0, "The bund path between the paddies: the rooster struts ahead; tap to chase.")
    p.prop(s, "scarecrow", -4.5, 2.4, h=2.1)
    p.prop(s, "paddy_ripe", -7.5, 1.6, h=1.0)
    p.prop(s, "paddy_ripe", 1.5, 1.7, h=1.0, mirror=True)
    p.prop(s, "paddy_tall", 6.0, 1.9, h=1.2)
    p.decal(s, "hoof_prints", -2.0, 0.8, 1.2)
    p.mango_line(s, 2.0, 5, 2.0, 0.6)
    p.litter(s, 4)

    # ---- teach
    s = p.section("FirstCanal", 14.0, 18.0, "The first canal, 2.5 m: a held jump clears it; the rooster flutters across first.")
    p.mango_line(s, 15.0, 3, 1.0, 0.6)
    canal_jump(p, s, 22.0, 2.5)
    p.litter(s, 3, avoid=(23.25,), holes=p.holes())

    s = p.section("Plank", 32.0, 18.0, "A 3.5 m canal, too wide for a sure jump: the plank bridge is the way across.")
    plank(p, s, 40.0)
    p.prop(s, "paddy_young", 36.0, 1.8, h=0.9)
    p.prop(s, "duck_1", 45.5, 1.6, h=0.55, mirror=True)
    p.litter(s, 3, avoid=(41.75,), holes=p.holes())

    s = p.section("Dung", 50.0, 16.0, "Cow dung on the bund, as in the lane: a tap clears it.")
    p.dung(s, 58.0)
    p.prop(s, "cow", 55.0, 2.6, h=1.45)
    p.decal(s, "hoof_prints", 61.0, 0.9, 1.2)
    p.litter(s, 2, avoid=(58.0,))

    s = p.section("Haystack", 66.0, 20.0, "A small haystack: hop onto it (mangoes along its top) or over it.")
    end = p.haystack(s, 74.0)
    p.mango_line(s, 74.15, 3, 0.45, 1.75)
    p.mango_line(s, end + 2.0, 3, 0.9, 0.6)
    p.litter(s, 2, avoid=(74.6,))

    s = p.section("WideCanal", 86.0, 22.0, "The widest canal, 4.5 m: double jump (the mangoes show where), or wade.")
    canal_jump(p, s, 95.0, 4.5)
    p.feather(s, 97.25, 3.4, 0)
    p.prop(s, "duck_2", 101.5, 1.5, h=0.55)
    p.litter(s, 2, avoid=(97.25,), holes=p.holes())

    s = p.section("Breather", 108.0, 16.0, "Room to breathe: a wave of mangoes and the first chilli.")
    p.chilli(s, 109.0)
    for i in range(10):
        p.mango(s, 110.5 + i * 1.2, 0.8 + 0.4 * math.sin(i * 0.8))
    p.prop(s, "palmyra_1", 116.0, 5.5, h=9.0)
    p.litter(s, 3)

    s = p.section("Cart", 124.0, 22.0, "The bullock cart on the bund: onto its bed; a feather above it for a double jump.")
    p.cart(s, 128.0)
    p.feather(s, 132.4, 3.4, 1)
    p.dung(s, 140.5)
    p.decal(s, "cart_rut", 126.0, 0.0, 2.2)
    p.litter(s, 2, avoid=(128.0, 130.0, 140.5))

    # ---- practise
    s = p.section("CanalDung", 146.0, 20.0, "A canal, then dung: jump, land, tap.")
    canal_jump(p, s, 151.0, 2.5)
    p.dung(s, 160.5)
    p.litter(s, 2, avoid=(152.25, 160.5), holes=p.holes())

    s = p.section("Haystacks", 166.0, 26.0, "Three small haystacks: hop, hop, hop; a feather above the last.")
    for x in (170.0, 177.5, 185.0):
        end = p.haystack(s, x)
        p.mango_line(s, x + 0.15, 3, 0.45, 1.75)
    p.feather(s, 185.6, 3.2, 2)
    p.prop(s, "granary", 180.0, 5.0, h=4.6)
    p.litter(s, 2, avoid=(170.6, 178.1, 185.6))

    s = p.section("PlankThenJump", 192.0, 22.0, "The plank, then a canal with no plank: walk, then jump.")
    plank(p, s, 195.0)
    canal_jump(p, s, 205.5, 2.5)
    p.litter(s, 2, avoid=(196.75, 206.75), holes=p.holes())

    s = p.section("ChilliStraight", 214.0, 18.0, "A long straight and a chilli to win back ground.")
    p.chilli(s, 215.0)
    p.mango_line(s, 217.5, 10, 1.2, 0.6)
    p.prop(s, "pump_house", 224.0, 4.5, h=2.9)
    p.litter(s, 3)

    s = p.section("CartCanal", 232.0, 22.0, "Off the cart's bed and straight on over a canal.")
    p.cart(s, 235.0)
    canal_jump(p, s, 245.0, 2.5)
    p.litter(s, 2, avoid=(235.0, 237.0, 246.25), holes=p.holes())

    s = p.section("WideAgain", 254.0, 20.0, "The wide canal again: double jump.")
    canal_jump(p, s, 261.0, 4.5)
    p.litter(s, 2, avoid=(263.25,), holes=p.holes())

    s = p.section("DungHaystack", 274.0, 18.0, "Dung, then a small haystack.")
    p.dung(s, 278.5)
    p.haystack(s, 285.5)
    p.mango_line(s, 285.65, 3, 0.45, 1.75)
    p.litter(s, 2, avoid=(278.5, 286.1))

    s = p.section("CanalTrio", 292.0, 26.0, "Three 2.5 m canals in a rhythm: jump, jump, jump.")
    for x in (295.0, 303.5, 312.0):
        canal_jump(p, s, x, 2.5)
    p.litter(s, 2, avoid=(296.25, 304.75, 313.25), holes=p.holes())

    # ---- test
    s = p.section("Mischief", 318.0, 24.0, "Dung; then the rooster knocks the pots by the well into the lane; a canal after.")
    p.dung(s, 322.0)
    p.pots(s, 330.0, hidden=True, ident="knocked")
    p.mischief(s, 331.0, "knocked")
    p.jump_arc(s, 330.0)
    canal_jump(p, s, 336.5, 2.5)
    p.litter(s, 2, avoid=(322.0, 330.0, 337.75), holes=p.holes())

    s = p.section("PlankHaystack", 342.0, 22.0, "The plank, then a haystack.")
    plank(p, s, 345.0)
    p.haystack(s, 356.0)
    p.mango_line(s, 356.15, 3, 0.45, 1.75)
    p.litter(s, 2, avoid=(346.75, 356.6), holes=p.holes())

    s = p.section("ChilliRun", 364.0, 18.0, "A chilli and a run of mangoes.")
    p.chilli(s, 365.0)
    p.mango_line(s, 367.5, 10, 1.2, 0.6)
    p.prop(s, "palmyra_2", 372.0, 6.0, h=9.0)
    p.litter(s, 3)

    s = p.section("CanalCartCanal", 382.0, 28.0, "Canal, cart, canal.")
    canal_jump(p, s, 385.0, 2.5)
    p.cart(s, 393.0)
    canal_jump(p, s, 403.0, 2.5)
    p.litter(s, 2, avoid=(386.25, 393.0, 395.0, 404.25), holes=p.holes())

    s = p.section("WideHaystack", 410.0, 22.0, "The wide canal, then a haystack straight after it.")
    canal_jump(p, s, 413.0, 4.5)
    p.haystack(s, 425.5)
    p.mango_line(s, 425.65, 3, 0.45, 1.75)
    p.litter(s, 2, avoid=(415.25, 426.1), holes=p.holes())

    s = p.section("DungPair", 432.0, 18.0, "Two cow pats: tap, tap.")
    p.dung(s, 436.5)
    p.dung(s, 444.0)
    p.prop(s, "calf", 440.0, 2.3, h=0.95)
    p.litter(s, 2, avoid=(436.5, 444.0))

    s = p.section("FinalChilli", 450.0, 18.0, "The last chilli.")
    p.chilli(s, 451.0)
    p.mango_line(s, 453.5, 10, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("ThreeWidths", 468.0, 32.0, "All three canals in a row: jump the 2.5 m, walk the plank, double jump the 4.5 m.")
    canal_jump(p, s, 471.0, 2.5)
    plank(p, s, 479.5)
    canal_jump(p, s, 489.5, 4.5)
    p.litter(s, 2, avoid=(472.25, 481.25, 491.75), holes=p.holes())

    s = p.section("HaystackDung", 500.0, 22.0, "Two haystacks and dung between them.")
    p.haystack(s, 503.5)
    p.mango_line(s, 503.65, 3, 0.45, 1.75)
    p.dung(s, 510.0)
    p.haystack(s, 517.5)
    p.mango_line(s, 517.65, 3, 0.45, 1.75)
    p.litter(s, 2, avoid=(504.1, 510.0, 518.1))

    s = p.section("Sugarcane", 522.0, 22.0, "Past the sugarcane: a canal, then dung.")
    p.prop(s, "sugarcane", 526.0, 2.6, h=2.8)
    canal_jump(p, s, 529.0, 2.5)
    p.dung(s, 538.5)
    p.litter(s, 2, avoid=(530.25, 538.5), holes=p.holes())

    s = p.section("LastWide", 544.0, 30.0, "The last wide canal, and a haystack after it.")
    canal_jump(p, s, 549.0, 4.5)
    p.haystack(s, 562.0)
    p.mango_line(s, 562.15, 3, 0.45, 1.75)
    p.prop(s, "field_shrine", 568.0, 4.0, h=4.2)
    p.litter(s, 3, avoid=(551.25, 562.6), holes=p.holes())

    s = p.section("OpenBund", 574.0, 32.0, "The bund opens out: if he is still ahead, he gets away at 600 m.")
    p.mango_line(s, 576.0, 12, 1.4, 0.6)
    p.prop(s, "hut_with_pen", 596.0, 5.5, h=3.8)
    p.litter(s, 4)
    return p


PROSE = [
    "## The opening: the bund",
    "",
    "No basket here: the chase starts on the bund between the paddies with the rooster 12 m ahead (the level's Ready",
    "screen; tap to chase). A clean run closes 0.6 m a second and catches him at about 131 m.",
    "",
    "## The canal",
    "",
    "* **2.5 m:** a held jump clears it (290 ms to take off); a tap lands in the water.",
    "* **3.5 m:** a held jump is a gamble (147 ms), so the 3.5 m canals all have the plank bridge: run across.",
    "* **4.5 m:** only a double jump clears it (405 ms); the mangoes trace the double jump's line.",
    "* **In the water:** never a fail. She wades at 45% speed (5.5 m lost on the widest) and steps out of the 0.28 m bed.",
    "",
    "## The shape of it",
    "",
    "Teach (to 150 m): one new thing at a time. Practise (to 316 m): canals in rhythm with dung and haystacks, the plank",
    "then a jump, the cart into a canal. Test (to 600 m): the rooster's mischief by the well, every combination, all",
    "three widths in a row, then the bund opens out.",
]


def main():
    p = design()
    run(p, {"level": 4, "title": "The canal", "subtitle": "Jump it, wade it, or take the plank.", "prose": PROSE})


if __name__ == "__main__":
    main()
