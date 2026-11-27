"""Level 6, "Buffalo and haystacks": the fields at harvest, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level6.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level6.py --report   # also writes docs/levels/level6.md

The last level of zone 2 (7 m/s against 6.4, 600 m, a 12 m start: no basket). New, from the doc's level table:

  * The buffalo wallowing across the road in its mud: its back is 1.1 m up. Jump onto it and it bounces her 2.6 m up,
    landing about 7 m on (a feather sits up there); run into it and she climbs over it, slowly.
  * Haystack chains: small stacks (1.05 m: hop onto them or over) and big ones (1.85 m: a double jump, or a slow vault),
    small, big, small, big.
  * The rooster's mischief by the well: he knocks its pots into the road behind him.

The canals, the cart and the mango branch of levels 4 and 5 come back between them.
"""
import math

from levelkit import Plan, run


def canal_jump(p, s, x, width):
    p.canal(s, x, width)
    if width <= 3.0:
        p.jump_arc(s, x + width / 2)
    else:
        p.arc(s, x - 1.6, width + 3.2, 2.3, 7)
    p.prop(s, "sluice_gate", x + width / 2, 2.6, h=1.7)


def small(p, s, x):
    end = p.haystack(s, x)
    p.mango_line(s, x + 0.15, 3, 0.45, 1.75)
    return end


def big(p, s, x):
    """A big haystack, with the double jump's line of mangoes over it."""
    end = p.haystack(s, x, big=True)
    p.arc(s, x - 1.5, (end - x) + 3.0, 2.4, 5)
    return end


def buffalo(p, s, x):
    end = p.buffalo(s, x)
    p.arc(s, x + 0.5, 7.0, 2.8, 6, 1.1)       # the bounce's line, from its back
    return end


def design():
    p = Plan(zone=2, seed=6)

    # ---- the opening: by the pond
    s = p.section("Pond", -10.0, 24.0, "The road by the buffalo pond, haystacks drying: the rooster struts ahead; tap to chase.")
    p.prop(s, "buffalo_mud", -5.0, 3.4, h=1.5)
    p.prop(s, "haystack", 3.5, 4.2, h=2.6)
    p.prop(s, "calf", 8.5, 2.4, h=0.95)
    p.prop(s, "scarecrow", 11.5, 3.0, h=2.1)
    p.decal(s, "cracked_mud", -4.0, 1.4, 1.6)
    p.mango_line(s, 2.0, 5, 2.0, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstBuffalo", 14.0, 24.0, "The first buffalo: jump onto its back and it bounces you high.")
    buffalo(p, s, 22.0)
    p.litter(s, 2, avoid=(23.3,))

    s = p.section("SmallStacks", 38.0, 18.0, "Two small haystacks: hop, hop.")
    small(p, s, 42.0)
    small(p, s, 50.0)
    p.litter(s, 2, avoid=(42.6, 50.6))

    s = p.section("BigStack", 56.0, 22.0, "A big haystack: a double jump (the mangoes show it). A feather above it.")
    end = big(p, s, 63.0)
    p.feather(s, end - 0.8, 3.7, 0)
    p.litter(s, 2, avoid=(64.1,))

    s = p.section("Breather", 78.0, 16.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 79.0)
    for i in range(9):
        p.mango(s, 81.0 + i * 1.3, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 3)

    s = p.section("Chain", 94.0, 34.0, "A haystack chain: small, big, small, big.")
    x = 97.0
    for kind in (small, big, small, big):
        end = kind(p, s, x)
        x = end + 5.5
    p.litter(s, 2, avoid=(97.6, 104.0, 111.0, 117.0))

    s = p.section("Canal", 128.0, 16.0, "A 2.5 m canal.")
    canal_jump(p, s, 134.0, 2.5)
    p.litter(s, 2, avoid=(135.25,), holes=p.holes())

    # ---- practise
    s = p.section("BuffaloFeather", 144.0, 22.0, "A buffalo with a feather at the top of its bounce.")
    end = buffalo(p, s, 148.0)
    p.feather(s, end + 1.6, 4.4, 1)
    p.litter(s, 2, avoid=(149.3,))

    s = p.section("DungStack", 166.0, 20.0, "Dung, then a small haystack.")
    p.dung(s, 170.0)
    small(p, s, 178.0)
    p.litter(s, 2, avoid=(170.0, 178.6))

    s = p.section("WideCanal", 186.0, 22.0, "The wide canal: double jump, or wade.")
    canal_jump(p, s, 192.0, 4.5)
    p.litter(s, 2, avoid=(194.25,), holes=p.holes())

    s = p.section("ChilliStraight", 208.0, 18.0, "A chilli and a long straight.")
    p.chilli(s, 209.0)
    p.mango_line(s, 211.5, 10, 1.3, 0.6)
    p.litter(s, 3)

    s = p.section("BuffaloStacks", 226.0, 32.0, "A buffalo, then a small and a big haystack.")
    buffalo(p, s, 229.0)
    small(p, s, 241.0)
    big(p, s, 249.0)
    p.litter(s, 2, avoid=(230.3, 241.6, 250.1))

    s = p.section("Branch", 258.0, 22.0, "A mango tree, a haystack as the step up to its branch.")
    p.haystack(s, 261.2)
    p.mango_line(s, 261.35, 3, 0.45, 1.75)
    p.mango_tree(s, 264.0)
    p.litter(s, 2, avoid=(262.0, 266.0))

    # ---- test
    s = p.section("Mischief", 280.0, 24.0, "Dung; the rooster knocks the pots by the well into the road; a canal after.")
    p.dung(s, 284.0)
    p.prop(s, "well", 292.4, 2.4, h=2.4)
    p.pots(s, 292.0, hidden=True, ident="knocked")
    p.mischief(s, 293.0, "knocked")
    p.jump_arc(s, 292.0)
    canal_jump(p, s, 298.5, 2.5)
    p.litter(s, 2, avoid=(284.0, 292.0, 299.75), holes=p.holes())

    s = p.section("TwoBuffaloes", 304.0, 30.0, "Two buffaloes: bounce, land, bounce.")
    buffalo(p, s, 307.0)
    buffalo(p, s, 320.0)
    p.litter(s, 2, avoid=(308.3, 321.3))

    s = p.section("BigChain", 334.0, 36.0, "Big, small, big: a feather above the last.")
    end = big(p, s, 337.0)
    end = small(p, s, end + 5.5)
    end = big(p, s, end + 5.5)
    p.feather(s, end - 0.8, 3.7, 2)
    p.litter(s, 2, avoid=(338.1, 345.0, 352.0))

    s = p.section("ChilliLane", 370.0, 18.0, "A chilli to win back ground.")
    p.chilli(s, 371.0)
    p.mango_line(s, 373.5, 10, 1.2, 0.6)
    p.prop(s, "haystack", 380.0, 4.5, h=2.6, mirror=True)
    p.litter(s, 3)

    s = p.section("CartCanal", 388.0, 24.0, "The cart, then a canal.")
    p.cart(s, 391.0)
    canal_jump(p, s, 402.0, 2.5)
    p.litter(s, 2, avoid=(391.0, 393.0, 403.25), holes=p.holes())

    s = p.section("BuffaloWide", 412.0, 34.0, "A buffalo, then the wide canal.")
    buffalo(p, s, 415.0)
    canal_jump(p, s, 429.0, 4.5)
    p.litter(s, 2, avoid=(416.3, 431.25), holes=p.holes())

    s = p.section("StacksDung", 446.0, 28.0, "Small, dung, big.")
    small(p, s, 449.0)
    p.dung(s, 457.5)
    big(p, s, 465.0)
    p.litter(s, 2, avoid=(449.6, 457.5, 466.1))

    s = p.section("FinalChilli", 474.0, 18.0, "The last chilli.")
    p.chilli(s, 475.0)
    p.mango_line(s, 477.5, 10, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("LastTest", 492.0, 50.0, "A buffalo, a chain, a canal: everything once more.")
    buffalo(p, s, 495.0)
    x = 507.0
    for kind in (small, big):
        x = kind(p, s, x) + 5.5
    canal_jump(p, s, x + 3.0, 2.5)
    p.litter(s, 2, avoid=(496.3, 507.6, 514.0), holes=p.holes())

    s = p.section("OpenFields", 542.0, 64.0, "The fields open out: if he is still ahead, he gets away at 600 m.")
    p.mango_line(s, 544.0, 14, 1.4, 0.6)
    p.prop(s, "haystack", 560.0, 4.2, h=2.6)
    p.prop(s, "buffalo_mud", 578.0, 3.6, h=1.5, mirror=True)
    p.litter(s, 5)
    return p


PROSE = [
    "## The opening: the pond",
    "",
    "No basket: the chase starts on the road by the buffalo pond with the rooster 12 m ahead (the Ready screen; tap to",
    "chase). A clean run catches him at about 131 m.",
    "",
    "## The new things",
    "",
    "* **The buffalo:** its back is 1.1 m up. Jump onto it for a 2.6 m bounce, landing about 7 m on (mangoes trace it,",
    "  a feather sits at the top of one); run into it and she climbs over, slowly.",
    "* **Haystack chains:** small stacks (1.05 m: hop onto or over) and big ones (1.85 m: a double jump).",
    "* **The rooster's mischief** by the well.",
    "",
    "## The shape of it",
    "",
    "Teach (to 144 m): the buffalo, small stacks, a big stack, a chilli, a chain, a canal. Practise (to 280 m): the",
    "buffalo with a feather, dung and stacks, the wide canal, a buffalo into stacks, a branch. Test (to 600 m): the",
    "mischief, two buffaloes, a big chain, the cart and canals, everything once more, then the fields open out.",
]


def main():
    p = design()
    run(p, {"level": 6, "title": "Buffalo and haystacks", "subtitle": "Bounce off a buffalo's back.", "prose": PROSE})


if __name__ == "__main__":
    main()
