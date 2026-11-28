"""Level 6, "Buffalo and haystacks": the fields at harvest, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level6.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level6.py --report   # also writes docs/levels/level6.md

The last level of zone 2, at a small child's real pace (3.5 m/s against the rooster's 3.15; 295 m; a 7 m start, no
basket: a clean run catches him at about 62 m). New, from the doc's level table:

  * The buffalo wallowing across the road in its mud: its back is 1.1 m up. Jump onto it (291 ms to take off) and it
    bounces her 2.6 m up, landing about 3.5 m on (mangoes trace the bounce; a feather sits above one for a double jump
    at its top); run into it and she climbs over it, slowly.
  * Haystack chains: small straw heaps (1.05 m: hop onto them or over) and big ones (1.85 m: a double jump onto the
    top, or a slow vault), small, big, small, big, 2.75 m between them.
  * The rooster's mischief by a farmer's hut: he knocks the hens' basket into the road behind him.

The canals (1.2 m to jump, 1.8 m with the plank, 2.6 m to double jump or wade), the sacks of paddy waiting for the
cart, cow dung, ducks, a goat kid and a mango branch come back between them: only what lies on a field road at harvest.
The old design's timing is kept at the new pace, so its distances are about half what they were; things to jump
stand about 4 m apart, and each chilli has 11 m or more of clear road after it.
"""
import math

from levelkit import Plan, run


def canal_jump(p, s, x, width):
    p.canal(s, x, width)
    if width < 2.0:
        p.jump_arc(s, x + width / 2)
    else:
        p.arc(s, x - 0.5, width + 1.0, 2.5, 7)


def plank(p, s, x, width=1.8):
    p.canal(s, x, width, bridge=True)
    p.mango_line(s, x + 0.15, 4, 0.5, 0.55)


def small(p, s, x):
    end = p.haystack(s, x)
    p.mango_line(s, x + 0.15, 3, 0.45, 1.75)
    return end


def big(p, s, x):
    """A big haystack, with the double jump's line of mangoes up onto it and along its top."""
    end = p.haystack(s, x, big=True)
    p.arc(s, x - 0.9, (end - x) + 1.8, 2.3, 5)
    return end


def buffalo(p, s, x):
    """A buffalo, the mangoes tracing the bounce off its back (she meets the back near the top of her jump, about
    0.45 m in, and the bounce peaks 1.5 m further on)."""
    end = p.buffalo(s, x)
    p.arc(s, x + 0.45, 2.95, 2.6, 5, 1.35)
    return end


def design():
    p = Plan(zone=2, seed=6)

    # ---- the opening: by the pond
    s = p.section("Pond", -10.0, 17.0, "The road by the buffalo pond, haystacks drying: the rooster struts ahead; tap "
                                     "to chase.")
    p.prop(s, "buffalo_mud", -5.5, 3.4, h=1.5)
    p.prop(s, "haystack", 3.0, 4.2, h=2.6)
    p.prop(s, "calf", -1.5, 2.4, h=0.95)
    p.prop(s, "scarecrow", 6.0, 3.0, h=2.1)
    p.decal(s, "cracked_mud", -4.5, 1.4, 1.6)
    p.mango_line(s, 1.5, 4, 1.3, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstBuffalo", 7.0, 9.0, "The first buffalo: jump onto its back and it bounces you high.")
    buffalo(p, s, 11.0)
    p.litter(s, 2, avoid=(12.3,))

    s = p.section("SmallStacks", 16.0, 10.0, "Two small haystacks: hop, hop.")
    small(p, s, 17.5)
    small(p, s, 21.5)
    p.litter(s, 2, avoid=(18.1, 22.1))

    s = p.section("BigStack", 26.0, 10.0, "A big haystack: a double jump onto it (the mangoes show it). A feather above it.")
    end = big(p, s, 28.0)
    p.feather(s, end - 0.8, 3.7, 0)
    p.litter(s, 2, avoid=(29.1,))

    s = p.section("Breather", 36.0, 8.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 36.5)
    for i in range(8):
        p.mango(s, 37.6 + i * 0.75, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 2)

    s = p.section("Chain", 44.0, 19.0, "A haystack chain: small, big, small, big.")
    x = 47.5
    for kind in (small, big, small, big):
        x = kind(p, s, x) + 2.75
    p.prop(s, "haystack", 55.0, 4.6, h=2.6, mirror=True)        # the harvest's stacks behind the road
    p.litter(s, 2, avoid=(48.1, 52.5, 57.0, 61.4))

    s = p.section("Canal", 63.0, 7.0, "A 1.2 m canal.")
    canal_jump(p, s, 66.0, 1.2)
    p.litter(s, 2, avoid=(66.6,), holes=p.holes())

    # ---- practise
    s = p.section("BuffaloFeather", 70.0, 9.0, "A buffalo, a feather above its bounce for a double jump at the top.")
    buffalo(p, s, 72.5)
    p.feather(s, 75.0, 5.2, 1)
    p.litter(s, 2, avoid=(73.8,))

    s = p.section("DungStack", 79.0, 10.0, "Dung, then a small haystack.")
    p.dung(s, 80.0)
    small(p, s, 84.0)
    p.litter(s, 2, avoid=(80.0, 84.6))

    s = p.section("WideCanal", 89.0, 7.0, "The wide canal: double jump, or wade.")
    canal_jump(p, s, 89.5, 2.6)
    p.prop(s, "duck_1", 93.8, 1.7, h=0.55)
    p.litter(s, 2, avoid=(90.8,), holes=p.holes())

    s = p.section("ChilliStraight", 96.0, 11.0, "A chilli and a long straight.")
    p.chilli(s, 96.5)
    p.mango_line(s, 97.8, 9, 0.9, 0.6)
    p.prop(s, "palmyra_2", 102.0, 6.0, h=9.0)
    p.litter(s, 2)

    s = p.section("BuffaloStacks", 107.0, 14.0, "A buffalo, then a small and a big haystack.")
    buffalo(p, s, 108.5)
    small(p, s, 114.0)
    big(p, s, 117.5)
    p.litter(s, 2, avoid=(109.8, 114.6, 118.6))

    s = p.section("Branch", 121.0, 12.0, "A mango tree, a haystack as the step up to its branch.")
    small(p, s, 122.5)
    p.mango(s, 124.1, 2.5)
    p.mango_tree(s, 124.3)
    p.litter(s, 2, avoid=(123.1, 125.3))

    # ---- test
    s = p.section("Mischief", 133.0, 13.0, "Dung; the rooster knocks the hens' basket by the farmer's hut into the road; "
                                         "a canal after.")
    p.dung(s, 134.0)
    p.prop(s, "hut_with_pen", 139.0, 4.2, h=3.8)
    p.prop(s, "hen_2", 137.2, 1.9, h=0.42)
    p.hens_basket(s, 138.5, hidden=True, ident="knocked")
    p.mischief(s, 139.0, "knocked")
    p.jump_arc(s, 138.5)
    canal_jump(p, s, 142.0, 1.2)
    p.litter(s, 2, avoid=(134.0, 138.5, 142.6), holes=p.holes())

    s = p.section("TwoBuffaloes", 146.0, 11.0, "Two buffaloes: bounce, land, bounce.")
    buffalo(p, s, 146.3)
    buffalo(p, s, 152.0)
    p.litter(s, 2, avoid=(147.6, 153.3))

    s = p.section("BigChain", 157.0, 14.0, "Big, small, big: a feather above the last.")
    end = big(p, s, 158.5)
    end = small(p, s, end + 2.75)
    end = big(p, s, end + 2.75)
    p.feather(s, end - 0.8, 3.7, 2)
    p.litter(s, 2, avoid=(159.6, 164.0, 168.5))

    s = p.section("ChilliLane", 171.0, 9.0, "A chilli to win back ground.")
    p.chilli(s, 171.5)
    p.mango_line(s, 172.8, 7, 0.9, 0.6)
    p.litter(s, 2)

    s = p.section("SacksCanal", 180.0, 11.0, "The harvest's sacks of paddy waiting for the cart: onto them, then a canal.")
    p.sacks(s, 182.5)
    canal_jump(p, s, 186.5, 1.2)
    p.decal(s, "cart_rut", 180.8, 0.0, 2.2)
    p.litter(s, 2, avoid=(182.5, 183.5, 187.1), holes=p.holes())

    s = p.section("BuffaloWide", 191.0, 12.0, "A buffalo, then the wide canal.")
    buffalo(p, s, 192.0)
    canal_jump(p, s, 198.0, 2.6)
    p.litter(s, 2, avoid=(193.3, 199.3), holes=p.holes())

    s = p.section("StacksDung", 203.0, 13.0, "Small, dung, big.")
    small(p, s, 204.0)
    p.dung(s, 208.5)
    big(p, s, 212.5)
    p.litter(s, 2, avoid=(204.6, 208.5, 213.6))

    s = p.section("PlankGoat", 216.0, 10.0, "The plank over a 1.8 m canal, then a goat kid wandering across.")
    plank(p, s, 218.0)
    p.goats(s, 223.0, 1)
    p.prop(s, "goat_eating", 225.0, 2.4, h=0.9)                  # its mother, grazing at the road's edge
    p.litter(s, 2, avoid=(218.9, 223.0), holes=p.holes())

    s = p.section("FinalChilli", 226.0, 9.0, "The last chilli.")
    p.chilli(s, 226.5)
    p.mango_line(s, 227.8, 7, 0.9, 0.6)
    p.litter(s, 2)

    s = p.section("LastTest", 235.0, 27.0, "A buffalo, a small and a big stack, a canal, ducks: everything once more.")
    buffalo(p, s, 238.0)
    x = 243.5
    for kind in (small, big):
        x = kind(p, s, x) + 2.75
    canal_jump(p, s, 252.0, 1.2)
    p.ducks(s, 257.0, 2)
    p.litter(s, 2, avoid=(239.3, 244.1, 248.5, 252.6, 257.0), holes=p.holes())

    s = p.section("LastBuffalo", 262.0, 12.0, "Dung, and the last buffalo to bounce off.")
    p.dung(s, 264.0)
    buffalo(p, s, 268.0)
    p.litter(s, 2, avoid=(264.0, 269.3))

    s = p.section("OpenFields", 274.0, 31.0, "The fields open out: if he is still ahead, he gets away at 295 m.")
    p.mango_line(s, 275.5, 14, 1.2, 0.6)
    p.prop(s, "buffalo_mud", 293.0, 3.6, h=1.5, mirror=True)
    p.litter(s, 4)
    return p


PROSE = [
    "## The opening: the pond",
    "",
    "No basket: the chase starts on the road by the buffalo pond with the rooster 7 m ahead (the Ready screen; tap to",
    "chase). The kid runs at a small child's real pace, 3.5 m/s, against his 3.15: a clean run catches him at about",
    "62 m, some 18 s in.",
    "",
    "## The new things",
    "",
    "* **The buffalo:** its back is 1.1 m up. Jump onto it (291 ms to take off) for a 2.6 m bounce, landing about",
    "  3.5 m on (mangoes trace it; a feather sits above one for a double jump at the top of the bounce); run into it",
    "  and she climbs over, slowly.",
    "* **Haystack chains:** small straw heaps (1.05 m: hop onto or over) and big ones (1.85 m: a double jump onto the",
    "  top, or a slow vault), 2.75 m apart.",
    "* **The rooster's mischief** by a farmer's hut: he knocks the hens' basket into the road behind him.",
    "",
    "## What is on the road",
    "",
    "Only what lies on a field road at harvest: the buffaloes in their mud, the straw heaps, the canals (1.2 m to jump,",
    "1.8 m with the plank, 2.6 m to double jump or wade), sacks of paddy waiting for the cart, cow dung, ducks, a goat",
    "kid and a mango branch over the road. Things to jump are about 4 m apart, and each chilli has 11 m or more clear",
    "after it.",
    "",
    "## The shape of it",
    "",
    "Teach (to 70 m): the buffalo, small stacks, a big stack, a chilli, a chain, a canal. Practise (to 133 m): the",
    "buffalo with a feather, dung and stacks, the wide canal, a buffalo into stacks, a branch. Test (to 295 m): the",
    "mischief, two buffaloes, a big chain, the sacks and canals, the plank and a goat kid, everything once more, the",
    "last buffalo, then the fields open out.",
]


def main():
    p = design()
    run(p, {"level": 6, "title": "Buffalo and haystacks", "subtitle": "Bounce off a buffalo's back.", "prose": PROSE})


if __name__ == "__main__":
    main()
