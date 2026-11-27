"""Level 5, "Mango trees": the fields' mango grove, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level5.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level5.py --report   # also writes docs/levels/level5.md

Zone 2 (7 m/s against 6.4, 600 m, a 12 m start: no basket). New, from the doc's level table: mango trees and their
branch routes. A tree's branch reaches over the bund road from 1 m to 5 m past its trunk, 2.3 m up: jump at it and
she pulls herself up (a quick climb), runs along it for its mangoes and drops off the end; or she runs on under it. A
small haystack just before a branch is a step up to it, and so is a cart's bed. The rooster flutters up onto every
branch and down off its end. The canals and haystacks of level 4 come back between the trees.
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


def plank(p, s, x, width=3.5):
    p.canal(s, x, width, bridge=True)
    p.mango_line(s, x + 0.1, 5, 0.75, 0.55)


def tree(p, s, x, step=False):
    """A mango tree, its branch over the road from x+1 to x+5; with `step`, a small haystack before it to hop onto."""
    if step:
        p.haystack(s, x - 2.8)
        p.mango_line(s, x - 2.65, 3, 0.45, 1.75)
    p.mango_tree(s, x)


def design():
    p = Plan(zone=2, seed=5)

    # ---- the opening: the grove's edge
    s = p.section("Grove", -10.0, 24.0, "The bund road into the mango grove: the rooster struts ahead; tap to chase.")
    p.prop(s, "tree_mango_1", -6.0, 5.0, h=5.6)
    p.prop(s, "palmyra_3", 2.0, 6.5, h=9.0)
    p.prop(s, "cow", 6.5, 2.8, h=1.45, mirror=True)
    p.prop(s, "goat_eating", -1.5, 2.2, h=0.9)
    p.mango_line(s, 2.0, 5, 2.0, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstTree", 14.0, 22.0, "The first mango tree, a haystack before it: hop onto the stack, jump at the branch.")
    tree(p, s, 21.0, step=True)
    p.litter(s, 2, avoid=(19.0, 23.0))

    s = p.section("Canal", 36.0, 16.0, "A 2.5 m canal: jump it.")
    canal_jump(p, s, 42.0, 2.5)
    p.litter(s, 2, avoid=(43.25,), holes=p.holes())

    s = p.section("Branch", 52.0, 22.0, "A branch with no step: jump straight up at it.")
    tree(p, s, 56.0)
    p.litter(s, 2, avoid=(58.0,))

    s = p.section("Dung", 74.0, 16.0, "Cow dung on the road.")
    p.dung(s, 82.0)
    p.litter(s, 2, avoid=(82.0,))

    s = p.section("Breather", 90.0, 16.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 91.0)
    for i in range(9):
        p.mango(s, 93.0 + i * 1.3, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 3)

    s = p.section("TreeFeather", 106.0, 22.0, "A tree with a feather above its branch: up, along, a double jump at the end.")
    tree(p, s, 112.0, step=True)
    p.feather(s, 116.3, 3.2, 0)
    p.litter(s, 2, avoid=(110.0, 114.0))

    s = p.section("Plank", 128.0, 18.0, "The plank over a 3.5 m canal.")
    plank(p, s, 134.0)
    p.litter(s, 2, avoid=(135.75,), holes=p.holes())

    # ---- practise
    s = p.section("CartTree", 146.0, 26.0, "The cart's bed as the step: off it and up onto the branch.")
    p.cart(s, 149.0)
    p.mango_tree(s, 154.0)
    p.litter(s, 2, avoid=(149.0, 151.0, 156.0))

    s = p.section("CanalDung", 172.0, 20.0, "A canal, then dung.")
    canal_jump(p, s, 176.0, 2.5)
    p.dung(s, 186.0)
    p.litter(s, 2, avoid=(177.25, 186.0), holes=p.holes())

    s = p.section("Haystacks", 192.0, 22.0, "Two small haystacks: hop, hop.")
    for x in (196.0, 204.0):
        p.haystack(s, x)
        p.mango_line(s, x + 0.15, 3, 0.45, 1.75)
    p.litter(s, 2, avoid=(196.6, 204.6))

    s = p.section("TreeCanal", 214.0, 26.0, "A tree, then a canal after its branch.")
    tree(p, s, 217.0)
    canal_jump(p, s, 231.5, 2.5)
    p.litter(s, 2, avoid=(219.0, 232.75), holes=p.holes())

    s = p.section("ChilliStraight", 240.0, 18.0, "A chilli and a long straight.")
    p.chilli(s, 241.0)
    p.mango_line(s, 243.5, 10, 1.3, 0.6)
    p.prop(s, "palmyra_1", 250.0, 6.0, h=9.0)
    p.litter(s, 3)

    s = p.section("Orchard", 258.0, 42.0, "Three trees in a row: branch to branch, a feather above the middle one.")
    for x in (262.0, 273.0, 284.0):
        p.mango_tree(s, x)
    p.feather(s, 277.3, 3.2, 1)
    p.litter(s, 2, avoid=(264.0, 275.0, 286.0))

    # ---- test
    s = p.section("Mischief", 300.0, 24.0, "Dung; the rooster knocks the pots by the well into the road; a canal after.")
    p.dung(s, 304.0)
    p.prop(s, "well", 312.4, 2.4, h=2.4)
    p.pots(s, 312.0, hidden=True, ident="knocked")
    p.mischief(s, 313.0, "knocked")
    p.jump_arc(s, 312.0)
    canal_jump(p, s, 318.5, 2.5)
    p.litter(s, 2, avoid=(304.0, 312.0, 319.75), holes=p.holes())

    s = p.section("WideTree", 324.0, 32.0, "The wide canal (double jump, a feather at its top), then a tree.")
    canal_jump(p, s, 327.0, 4.5)
    p.feather(s, 329.25, 3.4, 2)
    tree(p, s, 343.0, step=True)
    p.litter(s, 2, avoid=(329.25, 341.0, 345.0), holes=p.holes())

    s = p.section("ChilliRun", 356.0, 18.0, "A chilli and a run of mangoes.")
    p.chilli(s, 357.0)
    p.mango_line(s, 359.5, 10, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("CartCanal", 374.0, 24.0, "The cart, then a canal.")
    p.cart(s, 377.0)
    canal_jump(p, s, 388.0, 2.5)
    p.litter(s, 2, avoid=(377.0, 379.0, 389.25), holes=p.holes())

    s = p.section("TreesAndStacks", 398.0, 40.0, "A tree, a haystack, a tree.")
    p.mango_tree(s, 401.0)
    p.haystack(s, 415.0)
    p.mango_line(s, 415.15, 3, 0.45, 1.75)
    tree(p, s, 425.0, step=True)
    p.litter(s, 2, avoid=(403.0, 415.6, 427.0))

    s = p.section("FinalChilli", 438.0, 18.0, "The last chilli.")
    p.chilli(s, 439.0)
    p.mango_line(s, 441.5, 10, 1.2, 0.6)
    p.litter(s, 3)

    s = p.section("PlankDung", 456.0, 22.0, "The plank, then dung.")
    plank(p, s, 459.0)
    p.dung(s, 471.0)
    p.litter(s, 2, avoid=(460.75, 471.0), holes=p.holes())

    s = p.section("LastTrees", 478.0, 44.0, "The last two trees, a canal between them.")
    tree(p, s, 483.0, step=True)
    canal_jump(p, s, 497.5, 2.5)
    p.mango_tree(s, 506.0)
    p.litter(s, 2, avoid=(485.0, 498.75, 508.0), holes=p.holes())

    s = p.section("DungStack", 522.0, 22.0, "Dung, then a haystack.")
    p.dung(s, 526.0)
    p.haystack(s, 534.0)
    p.mango_line(s, 534.15, 3, 0.45, 1.75)
    p.litter(s, 2, avoid=(526.0, 534.6))

    s = p.section("LastWide", 544.0, 30.0, "The last wide canal.")
    canal_jump(p, s, 549.0, 4.5)
    p.prop(s, "field_shrine", 566.0, 4.0, h=4.2)
    p.litter(s, 3, avoid=(551.25,), holes=p.holes())

    s = p.section("OpenGrove", 574.0, 32.0, "The road opens out: if he is still ahead, he gets away at 600 m.")
    p.mango_line(s, 576.0, 12, 1.4, 0.6)
    p.prop(s, "tree_mango_1", 590.0, 5.0, h=5.6, mirror=True)
    p.litter(s, 4)
    return p


PROSE = [
    "## The opening: the grove",
    "",
    "No basket: the chase starts on the bund road into the mango grove with the rooster 12 m ahead (the Ready screen;",
    "tap to chase). A clean run catches him at about 131 m.",
    "",
    "## The branches",
    "",
    "* A mango tree's branch reaches over the road from 1 m to 5 m past its trunk, 2.3 m up, mangoes along it.",
    "* Jump at it and she pulls herself up (a quick climb), runs along it and drops off its end; or she runs on under.",
    "* A small haystack just before a branch is a step up to it, and so is a cart's bed.",
    "* The rooster flutters up onto every branch and down off its end.",
    "",
    "## The shape of it",
    "",
    "Teach (to 146 m): a tree with a haystack step, a canal, a branch with no step, dung, a chilli, a tree with a",
    "feather, the plank. Practise (to 300 m): the cart as a step, canals and dung, haystacks, a tree then a canal, an",
    "orchard of three trees. Test (to 600 m): the rooster's mischief by the well, the wide canal and a tree, trees and",
    "stacks, the last trees and canals, then the road opens out.",
]


def main():
    p = design()
    run(p, {"level": 5, "title": "Mango trees", "subtitle": "Jump at a branch to climb up for mangoes.", "prose": PROSE})


if __name__ == "__main__":
    main()
