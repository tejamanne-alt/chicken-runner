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
  * At the real pace of a small child running hard (3.5 m/s, Kick Off's), with only what really lies in a village
    street: the potter's pots drying by the road, a dog asleep in the dust, cow dung, the puddle round the hand pump,
    hens and a goat kid crossing, sacks of paddy waiting for the cart, a heap of sand where a house is being built.
  * Opening: the neighbour's yard. He naps on his rope cot; his hens peck about; the kid tiptoes to the bamboo basket
    the rooster sits under, and the player holds to lift it. A smooth lift starts the chase 6 m behind him, a clumsy
    one 8 m.
  * Teach (to about 90 m), one new thing at a time, each first on its own with room around it, the rooster hopping it
    first to show the way and mangoes tracing the jump: a pot stack (tap or hold), two pots in rhythm, cow dung (low:
    a tap clears it), the sleeping dog (long: hold), a breather with the first chilli, the hand-pump puddle (hold), a
    goat kid, the sacks of paddy (hop onto them and run off the end). A clean run catches the rooster at about 75 m.
  * Practise (to 177 m): the same things in pairs and rhythms about 4 m apart (a second and a bit), the sand heap, a
    long straight with a chilli to win back ground.
  * Test (to 290 m): the rooster's mischief (he knocks a pot stack into the lane behind him), the potter's four stacks,
    the dog and the dung together, the last sacks, then the lane opens out.
  * Every obstacle has the rooster's hop over it and a mango arc on the held jump; three feathers sit on the harder
    routes (a double jump over the dog, a double jump off the sacks, the top of a double jump in the pot trio).
"""
import math

from levelkit import Plan, run, visual

# ------------------------------------------------------------------ the course
def design():
    p = Plan(zone=1, seed=1)
    p.start_gaps = [p.r.T["startGapSmoothLift"], p.r.T["startGapClumsyLift"]]

    # The neighbour's yard. The kid starts at 0 beside the basket; the runway behind her is the yard's back.
    s = p.section("Yard", -10.0, 20.0, "The neighbour naps on his cot; hens peck about; hold to lift the basket.")
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
    p.mango_line(s, 5.0, 4, 1.0, 0.6)
    p.litter(s, 3, avoid=(0.55,))

    # ---- teach: one new thing at a time, each alone with room around it, the rooster hopping it first
    s = p.section("FirstPot", 10.0, 10.0, "The potter's pots drying by the road: one stack alone, the rooster hops it.")
    p.mango_line(s, 11.0, 3, 0.6, 0.6)
    p.pots(s, 15.5)
    p.prop(s, "pot_stack", 17.8, 2.1, h=0.62)          # more of his pots drying at the road's edge
    p.litter(s, 2, avoid=(15.5,))

    s = p.section("TwoPots", 20.0, 10.0, "Two pot stacks 4 m apart: jump, land, jump.")
    p.pots(s, 23.0)
    p.pots(s, 27.0)
    p.litter(s, 2, avoid=(23.0, 27.0))

    s = p.section("Dung", 30.0, 9.0, "Cow dung: low, a tap clears it; miss it and she slips.")
    p.dung(s, 34.0)
    p.mango_line(s, 35.6, 3, 0.6, 0.6)
    p.decal(s, "hoof_prints", 32.0, 0.9, 1.2)
    p.litter(s, 2, avoid=(34.0,))

    s = p.section("SleepingDog", 39.0, 11.0, "The dog asleep in the dust: long, so hold the jump. A feather above it.")
    p.dog(s, 44.0)
    p.feather(s, 44.1, 2.8, 0)
    p.mango_line(s, 46.8, 3, 0.6, 0.6)
    p.litter(s, 2, avoid=(44.0,))

    s = p.section("Breather", 50.0, 9.0, "Room to breathe: a wave of mangoes and the first chilli.")
    p.chilli(s, 50.6)
    for i in range(7):
        p.mango(s, 52.4 + i * 0.6, 0.8 + 0.4 * math.sin(i * 0.8))
    p.litter(s, 2)

    s = p.section("HandPump", 59.0, 10.0, "The puddle round the hand pump: wide and low, hold the jump.")
    p.puddle(s, 64.5)
    p.litter(s, 2, avoid=(64.5,))

    s = p.section("GoatKid", 69.0, 9.0, "A goat kid wandering across the street: jump it.")
    p.goats(s, 73.5, 1)
    p.prop(s, "goat_eating", 76.2, 2.3, h=0.95)        # its mother, grazing at the road's edge
    p.litter(s, 2, avoid=(73.5,))

    s = p.section("Sacks", 78.0, 11.0, "Sacks of paddy waiting for the cart: hop onto them, run off the end. A feather.")
    p.sacks(s, 82.0)
    p.feather(s, 82.9, 3.2, 1)
    p.litter(s, 2, avoid=(82.0, 83.2))

    # ---- practise: the same things in pairs and rhythms, about 4 m apart
    s = p.section("PotsDungPots", 89.0, 13.0, "Pots, dung, pots: the first rhythm.")
    p.pots(s, 92.0)
    p.dung(s, 96.0)
    p.pots(s, 100.0)
    p.litter(s, 2, avoid=(92.0, 96.0, 100.0))

    s = p.section("DogHens", 102.0, 11.0, "The dog, then two hens pecking in the road.")
    p.dog(s, 105.0)
    p.hens(s, 109.5, 2)
    p.litter(s, 2, avoid=(105.0, 109.5))

    s = p.section("Lane", 113.0, 7.0, "A short run of mangoes.")
    p.mango_line(s, 113.8, 6, 0.8, 0.6)
    p.litter(s, 2)

    s = p.section("PotTrio", 120.0, 14.0, "Three pot stacks in rhythm; a feather at the top of a double jump over the middle.")
    p.pots(s, 123.0)
    p.pots(s, 127.0)
    p.feather(s, 127.1, 2.8, 2)
    p.pots(s, 131.0)
    p.litter(s, 2, avoid=(123.0, 127.0, 131.0))

    s = p.section("PuddleDog", 134.0, 11.0, "The puddle, then the dog.")
    p.puddle(s, 137.5)
    p.dog(s, 141.8)
    p.litter(s, 2, avoid=(137.5, 141.8))

    s = p.section("SandHeap", 145.0, 12.0, "A house being built: a heap of sand at the road's edge, then the sacks.")
    p.sand(s, 148.5)
    p.sacks(s, 152.5)
    p.litter(s, 2, avoid=(148.5, 152.5, 153.7))

    s = p.section("ChilliStraight", 157.0, 10.0, "A long straight and a chilli to win back ground.")
    p.chilli(s, 157.8)
    p.mango_line(s, 159.8, 7, 0.8, 0.6)
    p.litter(s, 2)

    s = p.section("DungPair", 167.0, 10.0, "Two cow pats: tap, tap.")
    p.dung(s, 170.0)
    p.dung(s, 174.0)
    p.litter(s, 2, avoid=(170.0, 174.0))

    # ---- test
    s = p.section("Mischief", 177.0, 13.0, "The puddle; then the rooster knocks a pot stack off its stand into the lane.")
    p.puddle(s, 180.0)
    p.prop(s, "water_pot_stand", 186.3, 1.6, h=1.1)
    p.pots(s, 186.0, hidden=True, ident="knocked")
    p.mischief(s, 186.6, "knocked")
    p.jump_arc(s, 186.0)
    p.litter(s, 2, avoid=(180.0, 186.0))

    s = p.section("DogDung", 190.0, 11.0, "The dog and the dung.")
    p.dog(s, 193.5)
    p.dung(s, 197.5)
    p.litter(s, 2, avoid=(193.5, 197.5))

    s = p.section("ChilliLane", 201.0, 10.0, "A breather and a chilli.")
    p.chilli(s, 201.8)
    p.mango_line(s, 203.8, 6, 0.8, 0.6)
    p.litter(s, 2)

    s = p.section("PotQuartet", 211.0, 18.0, "Four of the potter's stacks, 4 m apart.")
    for x in (214.0, 218.0, 222.0, 226.0):
        p.pots(s, x)
    p.prop(s, "pot_stack", 220.0, 2.2, h=0.62, mirror=True)
    p.litter(s, 2, avoid=(214.0, 218.0, 222.0, 226.0))

    s = p.section("GoatSacks", 229.0, 13.0, "A goat kid, then the last sacks.")
    p.goats(s, 232.5, 1)
    p.sacks(s, 236.5)
    p.litter(s, 2, avoid=(232.5, 236.5, 237.7))

    s = p.section("DogDungPots", 242.0, 14.0, "Dog, dung, pots.")
    p.dog(s, 245.0)
    p.dung(s, 249.0)
    p.pots(s, 253.0)
    p.litter(s, 2, avoid=(245.0, 249.0, 253.0))

    s = p.section("FinalChilli", 256.0, 10.0, "The last chilli.")
    p.chilli(s, 256.8)
    p.mango_line(s, 258.8, 6, 0.8, 0.6)
    p.litter(s, 2)

    s = p.section("PuddlePots", 266.0, 13.0, "The puddle and two pots: the last test.")
    p.puddle(s, 269.5)
    p.pots(s, 273.8)
    p.pots(s, 277.8)
    p.litter(s, 2, avoid=(269.5, 273.8, 277.8))

    s = p.section("OpenLane", 279.0, 21.0, "The lane opens out: if he is still ahead, he gets away at 290 m.")
    p.mango_line(s, 280.0, 10, 1.0, 0.6)
    p.litter(s, 3)
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
    "* A lift with no drop gives the rooster a **6 m** head start; any drop gives him **8 m**.",
    "* A retry skips the opening and keeps the head start it earned; loading the level again plays it again.",
    "* The rules are `Core/BasketLift.cs` (tested in `BasketLiftTests`); the flow is `GameFlow`'s Intro state; the",
    "  basket, its hinge and the neighbour's two cut-outs are `BasketIntro`.",
    "",
    "## The shape of it",
    "",
    "Everything runs at a small child's real pace (3.5 m/s, as Kick Off's kid) and everything in the road is what lies",
    "in a village street: the potter's pots drying, a dog asleep in the dust, cow dung, the hand pump's puddle, hens and",
    "a goat kid crossing, sacks of paddy waiting for the cart, a heap of sand where a house is going up.",
    "",
    "Teach (to about 90 m): one new thing at a time, each first on its own with room around it, the rooster hopping",
    "it first to show the way and mangoes tracing the jump. Practise (to 177 m): the same things in pairs and rhythms,",
    "about 4 m (a second and a bit) apart. Test (to 290 m): the rooster's mischief, the potter's four stacks, the last",
    "sacks, then the lane opens out.",
]


def main():
    p = design()
    T = p.r.T
    run(p, {"level": 1, "title": "Pots and the sleeping dog", "subtitle": "Tap to jump. Hold for higher.",
            "extra": {"startGapSmooth": T["startGapSmoothLift"], "startGapClumsy": T["startGapClumsyLift"]},
            "prose": PROSE})


if __name__ == "__main__":
    main()
