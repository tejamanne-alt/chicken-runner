"""Level 1, "Pots and the sleeping dog": the lane, designed beat by beat, written as data and audited.

    python3 ArtSource/tools/levels/level1.py            # writes the plan and prints the audit (fails on a violation)
    python3 ArtSource/tools/levels/level1.py --report   # also writes docs/levels/level1.md

Writes Assets/ChickenRunner/Art/Levels/level1.json, which three things read:
  * GameBuilder.Plans (Unity) builds one chunk prefab per section, in order, with the same Kit calls the other levels use;
  * ArtSource/tools/levels/render_level.py draws it as the game camera sees it, from the resolved visuals;
  * this script's own audit, with the game's jump maths (JumpMath.cs) and tuning (ChaseTuning.cs) read from the C#.

Coordinates are the course's, in metres: x along the lane from where the kid starts the chase (0), y up, z into the
picture (the lane is z = 0, the camera looks from z = -16; behind the lane is z > 0).

The design (docs/levels/level1.md has the beat sheet):
  * Opening: the neighbour's yard. He naps on his rope cot; his hens peck about; the kid tiptoes to the bamboo basket
    the rooster sits under, and the player holds to lift it. A smooth lift starts the chase 10 m behind him, a clumsy
    one 14 m.
  * Teach (0 to 125 m), one new thing at a time, each first on its own with room around it, the rooster hopping it
    first to show the way and mangoes tracing the jump: a pot stack (tap or hold), two pots in rhythm, cow dung (low:
    a tap clears it), the sleeping dog (long: hold), a breather with the first chilli, the hand-pump puddle (wide: only
    a held jump clears it), the bullock cart (jump onto its bed and run off the end). A clean run catches the rooster
    at about 100 m, so a good player sees all of it once.
  * Practise (125 to 300 m): the same things in pairs and rhythms, spacing tightening from 7 m to 6.5 m, the cart as a
    step up, a long straight with a chilli to win back ground.
  * Test (300 to 500 m): the rooster's mischief (he knocks a pot stack into the lane behind him), trios, the dog and
    the dung together, the last cart, a final run of pots, then the lane opens out. Chillies come more often here,
    because a player who is still chasing has fallen behind.
  * Every obstacle has the rooster's hop over it and a mango arc on the held jump; three feathers sit on the harder
    routes (a double jump over the dog, a double jump off the cart's bed, the top of a double jump in the pot trio).
"""
import math

from levelkit import Plan, run, visual

# ------------------------------------------------------------------ the course
def design():
    p = Plan(zone=1, seed=1)
    p.start_gaps = [p.r.T["startGapSmoothLift"], p.r.T["startGapClumsyLift"]]

    # The neighbour's yard. The kid starts at 0 beside the basket; the runway behind her is the yard's back.
    s = p.section("Yard", -10.0, 24.0, "The neighbour naps on his cot; hens peck about; hold to lift the basket.")
    # the basket the rooster sits under (0.9 m across, so he fits): its near rim 0.1 m in front of her (within her reach
    # through the whole lift), its far rim, the hinge it lifts on, 1.0 m (kid_anims.BASKET_*); the kid tiptoes in from
    # -4.4 m toward the sleeping neighbour
    p.add(s, "basket", 0.55, [visual("chicken_basket", 0.55, z=0.0, w=0.9)], diameter=0.9, hinge=1.0, walkFrom=-4.4)
    # The neighbour asleep on his cot just past the basket, in front of his cattle shed (the zone set's, at 5.9): the kid
    # sneaks toward him, and the rooster bursts out right past him. Clear of the set's shop, old man and passing
    # milkman (-4.4 to -0.5), which stand behind the start; the set has its own chicken basket and tulsi planter.
    p.add(s, "neighbour", 2.6, [visual("neighbour_sleeping", 2.6, z=1.3, h=1.0),
                                visual("neighbour_awake", 2.6, z=1.3, h=1.25, kind="hidden")], z=1.3)
    p.prop(s, "hens_basket", -5.6, 1.2, h=0.55)
    p.prop(s, "water_pot_stand", -7.8, 1.7, h=1.1)
    for i, (hx, hz) in enumerate(((-1.4, 1.2), (4.7, 1.35), (6.5, 1.1))):
        p.prop(s, f"hen_{1 + i % 3}", hx, hz, h=0.42, mirror=i == 1)
    p.decal(s, "hen_prints", -0.8, 0.95, 0.9)
    p.decal(s, "kolam_2", -5.2, -1.2, 1.1)
    p.mango_line(s, 5.0, 6, 1.2, 0.6)
    p.litter(s, 3, avoid=(0.55,))

    # ---- teach
    s = p.section("FirstPot", 14.0, 18.0, "One pot stack alone: the rooster hops it, mangoes trace the jump.")
    p.mango_line(s, 15.0, 3, 0.9, 0.6)
    p.pots(s, 23.0)
    p.litter(s, 3, avoid=(23.0,))

    s = p.section("TwoPots", 32.0, 18.0, "Two pot stacks 7 m apart: jump, land, jump.")
    p.pots(s, 38.0)
    p.pots(s, 45.0)
    p.litter(s, 3, avoid=(38.0, 45.0))

    s = p.section("Dung", 50.0, 16.0, "Cow dung: low, a tap clears it; miss it and she slips.")
    p.dung(s, 57.0)
    p.mango_line(s, 60.0, 4, 0.8, 0.6)
    p.decal(s, "hoof_prints", 54.5, 0.9, 1.2)
    p.litter(s, 2, avoid=(57.0,))

    s = p.section("SleepingDog", 66.0, 20.0, "The sleeping dog: long, so hold the jump. A feather above for a double jump.")
    p.dog(s, 74.0)
    p.feather(s, 74.1, 2.8, 0)
    p.mango_line(s, 78.5, 3, 0.8, 0.6)
    p.litter(s, 3, avoid=(74.0,))

    s = p.section("Breather", 86.0, 16.0, "Room to breathe: a wave of mangoes and the first chilli.")
    for i in range(8):
        p.mango(s, 87.0 + i * 0.9, 0.8 + 0.4 * math.sin(i * 0.8))
    p.chilli(s, 95.0)
    p.litter(s, 3)

    s = p.section("HandPump", 102.0, 20.0, "The hand-pump puddle: wide and low, only a held jump clears it.")
    p.puddle(s, 114.0)
    p.litter(s, 2, avoid=(114.0,))

    s = p.section("Cart", 122.0, 20.0, "The bullock cart: jump onto its bed, run off the end. A feather for a double jump.")
    p.cart(s, 127.0)
    p.feather(s, 131.2, 3.4, 1)
    p.litter(s, 2, avoid=(127.0, 129.0))

    # ---- practise
    s = p.section("PotsDungPots", 142.0, 22.0, "Pots, dung, pots: 6.5 m apart, the first rhythm.")
    p.pots(s, 148.0)
    p.dung(s, 154.5)
    p.pots(s, 161.0)
    p.litter(s, 2, avoid=(148.0, 154.5, 161.0))

    s = p.section("DogPots", 164.0, 20.0, "The dog, then a pot stack.")
    p.dog(s, 170.5)
    p.pots(s, 177.5)
    p.litter(s, 2, avoid=(170.5, 177.5))

    s = p.section("Lane", 184.0, 14.0, "A short run of mangoes.")
    p.mango_line(s, 185.5, 8, 1.1, 0.6)
    p.litter(s, 3)

    s = p.section("PotTrio", 198.0, 22.0, "Three pot stacks in rhythm; a feather at the top of a double jump over the middle.")
    p.pots(s, 204.0)
    p.pots(s, 210.5)
    p.feather(s, 210.6, 2.8, 2)
    p.pots(s, 217.0)
    p.litter(s, 2, avoid=(204.0, 210.5, 217.0))

    s = p.section("PuddleDog", 220.0, 20.0, "The puddle, then the dog.")
    p.puddle(s, 226.5)
    p.dog(s, 234.5)
    p.litter(s, 2, avoid=(226.5, 234.5))

    s = p.section("CartPots", 240.0, 22.0, "The cart as a step: off its bed straight into a jump over pots.")
    p.cart(s, 244.0)
    p.pots(s, 253.0)
    p.litter(s, 2, avoid=(244.0, 246.0, 253.0))

    s = p.section("ChilliStraight", 262.0, 18.0, "A long straight and a chilli to win back ground.")
    p.chilli(s, 263.5)
    p.mango_line(s, 266.0, 10, 1.1, 0.6)
    p.litter(s, 3)

    s = p.section("DungPair", 280.0, 18.0, "Two cow pats: tap, tap.")
    p.dung(s, 286.0)
    p.dung(s, 292.0)
    p.litter(s, 2, avoid=(286.0, 292.0))

    # ---- test
    s = p.section("Mischief", 298.0, 22.0, "The puddle; then the rooster knocks a pot stack off its stand into the lane.")
    p.puddle(s, 303.5)
    p.prop(s, "water_pot_stand", 313.3, 1.6, h=1.1)
    p.pots(s, 313.0, hidden=True, ident="knocked")
    p.mischief(s, 314.0, "knocked")
    p.jump_arc(s, 313.0)
    p.litter(s, 2, avoid=(303.5, 313.0))

    s = p.section("DogDung", 320.0, 20.0, "The dog and the dung.")
    p.dog(s, 326.5)
    p.dung(s, 333.5)
    p.litter(s, 2, avoid=(326.5, 333.5))

    s = p.section("ChilliLane", 340.0, 20.0, "A breather and a chilli.")
    p.chilli(s, 341.5)
    p.mango_line(s, 344.0, 9, 1.1, 0.6)
    p.litter(s, 3)

    s = p.section("PotQuartet", 360.0, 26.0, "Four pot stacks, 6.5 m apart.")
    for x in (364.0, 370.5, 377.0, 383.5):
        p.pots(s, x)
    p.litter(s, 2, avoid=(364.0, 370.5, 377.0, 383.5))

    s = p.section("LastCart", 386.0, 22.0, "The last cart, and pots after it.")
    p.cart(s, 390.0)
    p.pots(s, 399.0)
    p.litter(s, 2, avoid=(390.0, 392.0, 399.0))

    s = p.section("DogDungPots", 408.0, 24.0, "Dog, dung, pots.")
    p.dog(s, 413.5)
    p.dung(s, 420.5)
    p.pots(s, 427.0)
    p.litter(s, 2, avoid=(413.5, 420.5, 427.0))

    s = p.section("FinalChilli", 432.0, 18.0, "The last chilli.")
    p.chilli(s, 433.5)
    p.mango_line(s, 436.0, 9, 1.1, 0.6)
    p.litter(s, 3)

    s = p.section("PuddlePots", 450.0, 22.0, "The puddle and two pots: the last test.")
    p.puddle(s, 456.0)
    p.pots(s, 463.5)
    p.pots(s, 470.0)
    p.litter(s, 2, avoid=(456.0, 463.5, 470.0))

    s = p.section("OpenLane", 472.0, 34.0, "The lane opens out: if he is still ahead, he gets away at 500 m.")
    p.mango_line(s, 474.0, 12, 1.4, 0.6)
    p.litter(s, 4)
    return p


# ------------------------------------------------------------------ the beat sheet's own words
PROSE = [
    "## The opening: the neighbour's yard",
    "",
    "The neighbour naps on his rope cot behind the lane, just past the basket; his hens peck about. The kid tiptoes in",
    "from -4.4 m to the bamboo basket the rooster is sitting under (a tap hurries her). The player holds to lift it by its near rim; it turns",
    "up on its far rim over 1.6 s of holding. Letting go part way drops it back with a clunk, and the neighbour stirs.",
    "Fully up, the rooster bursts out and sprints off, the kid flings the basket aside, and the neighbour wakes shouting.",
    "",
    "* A lift with no drop gives the rooster a **10 m** head start; any drop gives him **14 m**.",
    "* A retry skips the opening and keeps the head start it earned; loading the level again plays it again.",
    "* The rules are `Core/BasketLift.cs` (tested in `BasketLiftTests`); the flow is `GameFlow`'s Intro state; the",
    "  basket, its hinge and the neighbour's two cut-outs are `BasketIntro`.",
    "",
    "## The shape of it",
    "",
    "Teach (to about 140 m): one new thing at a time, each first on its own with room around it, the rooster hopping",
    "it first to show the way and mangoes tracing the jump. Practise (to 300 m): the same things in pairs and rhythms.",
    "Test (to 500 m): the rooster's mischief, trios, the last cart, then the lane opens out.",
]


def main():
    p = design()
    T = p.r.T
    run(p, {"level": 1, "title": "Pots and the sleeping dog", "subtitle": "Tap to jump. Hold for higher.",
            "extra": {"startGapSmooth": T["startGapSmoothLift"], "startGapClumsy": T["startGapClumsyLift"]},
            "prose": PROSE})


if __name__ == "__main__":
    main()
