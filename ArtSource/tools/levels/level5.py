"""Level 5, "Mango trees": the fields' mango grove, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level5.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level5.py --report   # also writes docs/levels/level5.md

Zone 2 at a small child's real pace (3.5 m/s against the rooster's 3.15; 295 m; a 7 m start, no basket: a clean run
catches him at about 62 m). New, from the doc's level table: mango trees and their branch routes. A tree's branch
reaches over the bund road from 1 m to 5 m past its trunk, 2.3 m up: jump at it and she pulls herself up (a quick
climb), runs along it for its mangoes and drops off the end; or she runs on under it. From the road a double jump
gets her up from anywhere in the 2.9 m before the branch; a single jump only at two narrow spots. So most trees have
a step in front of them, something that really stands by a field road:

  * a small straw heap (1.05 m) 1.6 m short of the branch: hop onto it, jump again from its top (226 ms);
  * sacks of paddy waiting for the cart (0.8 m), the branch 2.2 m on from where they start: hop onto them, jump again
    from anywhere on them (217 ms). The rooster's one arc goes from in front of the sacks straight up onto the branch.

The orchard's trees stand 6 m apart, 2 m between branches: jump from one branch to the next (360 ms), the rooster
arcing branch to branch ahead of her. The canals (1.2 m to jump, 1.8 m with the plank, 2.6 m to double jump), the
haystacks, ducks and cow dung of level 4 come back between the trees, and the rooster knocks the water pots by the
well into the road. The old design's timing is kept at the new pace, so its distances are about half what they were;
things to jump stand about 4 m apart, and each chilli has 11 m or more of clear road after it.
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


def drop_hop(s, x):
    """Take out the plan's rooster hop that starts at x (one a kit helper added), where this level lays his route."""
    for i, it in enumerate(s["items"]):
        if it["kind"] == "hop" and abs(it["x"] - x) < 1e-6:
            del s["items"][i]
            return
    raise ValueError(f"no rooster hop at {x} in {s['name']}")


def tree(p, s, x, step=None):
    """A mango tree, its branch over the road from x+1 to x+5. With step "hay", a small haystack before it, its end 1.6 m
    short of the branch (the rooster's hop over the stack ends just where his flutter up onto the branch begins); with
    "sacks", sacks of paddy 2.2 m before the branch, the rooster's one arc from in front of them up onto it."""
    if step == "hay":
        hx = x - 1.8
        small(p, s, hx)
        p.mango(s, hx + 1.6, 2.5)                       # the jump from the stack's top up to the branch
    elif step == "sacks":
        sx = x - 1.2
        p.sacks(s, sx, rooster_hop=False)
        p.hop(s, sx - 0.7, 3.1, 0.9)                    # over the sacks and up onto the branch (Kit's flutter inside it)
        p.mango(s, sx + 1.6, 2.4)
    p.mango_tree(s, x)


def orchard(p, s, xs):
    """Trees in a row 6 m apart, 2 m between their branches: branch to branch. The rooster arcs from each branch to the
    next (in place of his flutter down off it, and taking in the Kit's flutter up onto the next)."""
    for a, b in zip(xs, xs[1:]):
        assert abs(b - a - 6.0) < 1e-6
    for i, x in enumerate(xs):
        p.mango_tree(s, x)
        if i + 1 < len(xs):
            drop_hop(s, x + 4.7)
            p.hop(s, x + 4.7, xs[i + 1] + 1.2 - (x + 4.7), 0.6)
            p.arc(s, x + 4.9, 2.2, 0.7, 3, 2.3)        # the jump across the gap


def design():
    p = Plan(zone=2, seed=5)

    # ---- the opening: the grove's edge
    s = p.section("Grove", -10.0, 18.0, "The bund road into the mango grove: the rooster struts ahead; tap to chase.")
    p.prop(s, "tree_mango_2", -7.5, 5.0, h=5.6)
    p.prop(s, "palmyra_3", -2.3, 6.5, h=9.0)
    p.prop(s, "cow", 5.5, 2.8, h=1.45, mirror=True)
    p.prop(s, "goat_eating", -1.5, 2.2, h=0.9)
    p.mango_line(s, 1.5, 4, 1.4, 0.6)
    p.litter(s, 3)

    # ---- teach
    s = p.section("FirstTree", 8.0, 12.0, "The first mango tree, a haystack before it: hop onto the stack, jump at the "
                                        "branch, run along it for the mangoes.")
    tree(p, s, 13.5, step="hay")
    p.litter(s, 2, avoid=(12.3, 15.0))

    s = p.section("Canal", 20.0, 9.0, "A 1.2 m canal: jump it.")
    canal_jump(p, s, 23.5, 1.2)
    p.prop(s, "duck_1", 26.6, 1.7, h=0.55, mirror=True)
    p.litter(s, 2, avoid=(24.1,), holes=p.holes())

    s = p.section("Branch", 29.0, 12.0, "A branch with no step: a double jump gets her up (or a well-timed jump).")
    tree(p, s, 31.0)
    p.litter(s, 2, avoid=(32.0,))

    s = p.section("Dung", 41.0, 8.0, "Cow dung on the road.")
    p.dung(s, 44.5)
    p.decal(s, "hoof_prints", 46.8, 0.9, 1.2)
    p.litter(s, 2, avoid=(44.5,))

    s = p.section("Breather", 49.0, 8.0, "A breather: mangoes and a chilli.")
    p.chilli(s, 49.5)
    for i in range(8):
        p.mango(s, 50.6 + i * 0.75, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 2)

    s = p.section("TreeFeather", 57.0, 12.0, "A tree with a haystack step and a feather above its branch: up, along, a "
                                           "double jump at the end.")
    tree(p, s, 62.5, step="hay")
    p.feather(s, 66.8, 3.2, 0)
    p.litter(s, 2, avoid=(61.3, 64.0))

    s = p.section("Plank", 69.0, 9.0, "The plank over a 1.8 m canal.")
    plank(p, s, 71.5)
    p.litter(s, 2, avoid=(72.4,), holes=p.holes())

    # ---- practise
    s = p.section("SacksTree", 78.0, 12.0, "Sacks of paddy waiting for the cart as the step: onto them, and up onto the "
                                         "branch.")
    tree(p, s, 81.2, step="sacks")
    p.decal(s, "cart_rut", 79.0, 0.0, 2.2)
    p.litter(s, 2, avoid=(80.0, 81.0, 83.0))

    s = p.section("CanalDung", 90.0, 9.0, "A canal, then dung.")
    canal_jump(p, s, 90.5, 1.2)
    p.dung(s, 95.0)
    p.litter(s, 2, avoid=(91.1, 95.0), holes=p.holes())

    s = p.section("Haystacks", 99.0, 9.0, "Two small haystacks: hop, hop.")
    small(p, s, 100.0)
    small(p, s, 104.0)
    p.litter(s, 2, avoid=(100.6, 104.6))

    s = p.section("TreeCanal", 108.0, 14.0, "A tree, then a canal after its branch.")
    tree(p, s, 110.0)
    canal_jump(p, s, 118.5, 1.2)
    p.litter(s, 2, avoid=(111.0, 119.1), holes=p.holes())

    s = p.section("ChilliStraight", 122.0, 9.0, "A chilli and a long straight.")
    p.chilli(s, 122.5)
    p.mango_line(s, 123.8, 7, 0.9, 0.6)
    p.prop(s, "palmyra_1", 127.0, 6.0, h=9.0)
    p.litter(s, 2)

    s = p.section("Orchard", 131.0, 22.0, "Three trees in a row, 2 m between their branches: branch to branch, a feather "
                                        "above the middle one.")
    orchard(p, s, (133.0, 139.0, 145.0))
    p.feather(s, 143.3, 3.2, 1)
    p.litter(s, 2, avoid=(134.0, 140.0, 146.0))

    # ---- test
    s = p.section("Mischief", 153.0, 13.0, "Dung; the rooster knocks the water pots off their stand by the well into "
                                         "the road; a canal after.")
    p.dung(s, 156.0)
    p.prop(s, "water_pot_stand", 161.5, 1.7, h=1.1)     # by the well (the fields' own, behind)
    p.pots(s, 160.5, hidden=True, ident="knocked")
    p.mischief(s, 161.0, "knocked")
    p.jump_arc(s, 160.5)
    canal_jump(p, s, 164.0, 1.2)
    p.litter(s, 2, avoid=(156.0, 160.5, 164.6), holes=p.holes())

    s = p.section("WideTree", 166.0, 17.0, "The wide canal (double jump, a feather at its top), then a tree with a "
                                         "haystack step.")
    canal_jump(p, s, 168.0, 2.6)
    p.feather(s, 169.4, 3.4, 2)
    tree(p, s, 175.8, step="hay")
    p.litter(s, 2, avoid=(169.3, 174.6, 177.0), holes=p.holes())

    s = p.section("ChilliRun", 183.0, 9.0, "A chilli and a run of mangoes.")
    p.chilli(s, 183.5)
    p.mango_line(s, 184.8, 7, 0.9, 0.6)
    p.litter(s, 2)

    s = p.section("DucksCanal", 192.0, 12.0, "Ducks waddling up from the canal: jump them, then the canal.")
    p.ducks(s, 195.0, 2)
    canal_jump(p, s, 198.5, 1.2)
    p.prop(s, "duck_2", 201.5, 1.6, h=0.55)
    p.litter(s, 2, avoid=(195.0, 199.1), holes=p.holes())

    s = p.section("TreesAndStacks", 204.0, 22.0, "A tree, a haystack, then sacks as the step up to another tree.")
    tree(p, s, 205.0)
    small(p, s, 213.5)
    tree(p, s, 218.7, step="sacks")
    p.litter(s, 2, avoid=(206.0, 214.1, 217.5, 219.7))

    s = p.section("FinalChilli", 226.0, 9.0, "The last chilli.")
    p.chilli(s, 226.5)
    p.mango_line(s, 227.8, 7, 0.9, 0.6)
    p.litter(s, 2)

    s = p.section("PlankDung", 235.0, 11.0, "The plank, then dung.")
    plank(p, s, 238.0)
    p.dung(s, 243.0)
    p.litter(s, 2, avoid=(238.9, 243.0), holes=p.holes())

    s = p.section("LastTrees", 246.0, 22.0, "The last two trees (a haystack before the first), a canal between them.")
    tree(p, s, 250.0, step="hay")
    canal_jump(p, s, 258.0, 1.2)
    tree(p, s, 261.0)
    p.litter(s, 2, avoid=(248.8, 251.0, 258.6, 262.0), holes=p.holes())

    s = p.section("DungStack", 268.0, 10.0, "Dung, then a haystack.")
    p.dung(s, 270.5)
    small(p, s, 274.0)
    p.litter(s, 2, avoid=(270.5, 274.6))

    s = p.section("LastWide", 278.0, 12.0, "The last wide canal.")
    canal_jump(p, s, 280.0, 2.6)
    p.prop(s, "field_shrine", 286.0, 4.0, h=4.2)
    p.litter(s, 2, avoid=(281.3,), holes=p.holes())

    s = p.section("OpenGrove", 290.0, 15.0, "The road opens out: if he is still ahead, he gets away at 295 m.")
    p.mango_line(s, 291.0, 9, 1.1, 0.6)
    p.prop(s, "tree_mango_1", 297.5, 5.0, h=5.6, mirror=True)
    p.litter(s, 3)
    return p


PROSE = [
    "## The opening: the grove",
    "",
    "No basket: the chase starts on the bund road into the mango grove with the rooster 7 m ahead (the Ready screen;",
    "tap to chase). The kid runs at a small child's real pace, 3.5 m/s, against his 3.15: a clean run catches him at",
    "about 62 m, some 18 s in.",
    "",
    "## The branches",
    "",
    "* A mango tree's branch reaches over the road from 1 m to 5 m past its trunk, 2.3 m up, mangoes along it.",
    "* Jump at it and she pulls herself up (a quick climb), runs along it and drops off its end; or she runs on under.",
    "* From the road, a double jump gets her up from anywhere in the 2.9 m before the branch; a single jump only from",
    "  two narrow spots. So most trees have a step before them, as a field road really has:",
    "  * a **small haystack**, its end 1.6 m short of the branch: hop onto it and jump again from its top (226 ms);",
    "  * **sacks of paddy** waiting for the cart (0.8 m), the branch 2.2 m on from where they start: hop onto them and",
    "    jump again from anywhere on them (217 ms).",
    "* In the orchard the trees stand 6 m apart, 2 m between branches: jump from one branch to the next (360 ms).",
    "* The rooster flutters up onto every branch and down off its end (in the orchard, branch to branch; at the sacks,",
    "  one arc over them and up).",
    "",
    "## What is on the road",
    "",
    "Only what lies on a field road: the canals (1.2 m to jump, 1.8 m with the plank, 2.6 m to double jump or wade),",
    "ducks waddling up from them, cow dung, small straw heaps, the sacks of paddy, and the water pots by the well, which",
    "the rooster knocks into the road. Things to jump are about 4 m apart, and each chilli has 11 m or more clear after it.",
    "",
    "## The shape of it",
    "",
    "Teach (to 78 m): a tree with a haystack step, a canal, a branch with no step, dung, a chilli, a tree with a",
    "feather, the plank. Practise (to 153 m): the sacks as a step, canals and dung, haystacks, a tree then a canal, an",
    "orchard of three trees, branch to branch. Test (to 295 m): the rooster's mischief by the well, the wide canal and a",
    "tree, ducks and a canal, trees and steps, the last trees and canals, then the road opens out.",
]


def main():
    p = design()
    run(p, {"level": 5, "title": "Mango trees", "subtitle": "Jump at a branch to climb up for mangoes.", "prose": PROSE})


if __name__ == "__main__":
    main()
