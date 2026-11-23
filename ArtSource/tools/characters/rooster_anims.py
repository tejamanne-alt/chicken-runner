"""The rooster's animation clips, keyed onto rooster_model's rig.

Bone conventions (measured on the rig): Body +X tips his nose up; Neck1, Neck2 and Head +X bend forward and down and
+Y turns the head; Jaw -X opens the beak; Tail1 and Tail2 +X cock the tail forward and up; a wing +X lifts it, and it
spreads outward with -Z on the left and +Z on the right; UpperLeg and LowerLeg +X swing forward, Foot -X curls the toes.
The Body bone leans forward-up, so its location is converted from (up, forward) metres by body_loc().
"""
import math

from kid_anims import g, keyed, mix, pose, smooth  # noqa: F401


def body_loc(up=0.0, forward=0.0):
    return (0.0, 0.65 * up + 0.76 * forward, 0.76 * up - 0.65 * forward)


def wings(P, lift=0.0, spread=0.0, fold=0.0):
    P["LeftWing"] = [lift, fold, -spread]
    P["RightWing"] = [lift, -fold, spread]


def legs(P, side, thigh=0.0, shank=0.0, foot=0.0):
    P[f"{side}UpperLeg"] = [thigh, 0.0, 0.0]
    P[f"{side}LowerLeg"] = [shank, 0.0, 0.0]
    P[f"{side}Foot"] = [foot, 0.0, 0.0]


def out(P, up=0.0, forward=0.0):
    return {k: tuple(v) for k, v in P.items()}, {"Body": body_loc(up, forward)}


# ------------------------------------------------------------------ run: quick little strides, head held steady
def run_cycle(t, T, lean, wing_lift, wing_flap, beak=0.0):
    P = pose()
    phi = 2 * math.pi * t / T
    for side, p in (("Left", phi), ("Right", phi + math.pi)):
        legs(P, side, thigh=26 * math.cos(p), shank=14 * math.cos(p - 0.3 * math.pi) - 42 * g(p, 1.3 * math.pi, 0.4 * math.pi),
             foot=10 * g(p, 0.0, 0.3 * math.pi) - 45 * g(p, 1.2 * math.pi, 0.45 * math.pi))
    bob = math.cos(2 * (phi - 0.6 * math.pi))
    P["Body"] = [-lean + 2 * bob, 3 * math.cos(phi), 0]
    # The head stays level and steady while the body pumps underneath: the neck takes up the bob.
    P["Neck1"] = [lean * 0.55 - 4 * bob, -2 * math.cos(phi), 0]
    P["Neck2"] = [lean * 0.25, 0, 0]
    P["Head"] = [-lean * 0.75 + 3 * bob, 0, 0]
    P["Jaw"] = [-beak, 0, 0]
    wings(P, lift=wing_lift + wing_flap * math.sin(2 * phi), spread=wing_lift * 0.8 + wing_flap * 0.5 * math.sin(2 * phi))
    P["Tail1"] = [-4 + 6 * math.sin(2 * phi - 1.0), 0, 2 * math.sin(phi)]
    P["Tail2"] = [5 * math.sin(2 * phi - 2.0), 0, 0]
    return P, 0.012 * bob - 0.01


def run(t):
    P, up = run_cycle(t, 10 / 30, lean=14, wing_lift=10, wing_flap=8)
    return out(P, up)


def panic(t):
    P, up = run_cycle(t, 8 / 30, lean=24, wing_lift=42, wing_flap=40, beak=18 + 10 * math.sin(2 * math.pi * t / 0.13))
    return out(P, up - 0.01)


# ------------------------------------------------------------------ flutter over hops and up onto roofs
def flutter(t):
    P = pose()
    q = 2 * math.pi * t / (8 / 30)
    wings(P, lift=35 + 70 * math.sin(q), spread=55 + 22 * math.sin(q))
    for side in ("Left", "Right"):
        legs(P, side, thigh=-38, shank=-58, foot=-50)
    P["Body"] = [16 + 3 * math.sin(q), 0, 0]
    P["Neck1"] = [-6, 0, 0]
    P["Head"] = [-10, 0, 0]
    P["Tail1"] = [8 - 6 * math.sin(q), 0, 0]
    P["Tail2"] = [-6 * math.sin(q + 0.6), 0, 0]
    return out(P, 0.02 * math.sin(q))


# ------------------------------------------------------------------ the taunt: chest out, neck up, a long crow
def crow(t):
    stand = pose()
    wings(stand, lift=4)
    puff = pose()
    puff["Body"], puff["Neck1"], puff["Neck2"], puff["Head"] = [14, 0, 0], [-12, 0, 0], [-6, 0, 0], [-16, 0, 0]
    wings(puff, lift=-6, spread=22)
    puff["Tail1"] = [14, 0, 0]
    open_ = mix(puff, pose(), 0)
    open_["Jaw"] = [-38, 0, 0]
    open_["Head"] = [-34, 0, 0]
    keys = [(0, stand, (0, 0, 0)), (8, puff, (0, 0.02, 0)), (11, open_, (0, 0.025, 0)), (28, open_, (0, 0.025, 0)),
            (35, stand, (0, 0, 0))]
    P, loc = keyed(keys, t)
    if 11 <= t * 30 <= 28:   # the crow warbles
        P["Jaw"][0] += 5 * math.sin(2 * math.pi * t / 0.11)
        P["Neck1"][0] += 2 * math.sin(2 * math.pi * t / 0.2)
    return out(P, loc[1])


# ------------------------------------------------------------------ startled: a leap with wings up, beak open
def startled(t):
    rest, up = run_cycle(0.0, 10 / 30, 14, 10, 8)
    leap = pose()
    wings(leap, lift=72, spread=52)
    for side in ("Left", "Right"):
        legs(leap, side, thigh=-20, shank=-50, foot=-45)
    leap["Body"], leap["Neck1"], leap["Head"], leap["Jaw"] = [12, 0, 0], [-8, 0, 0], [-16, 0, 0], [-34, 0, 0]
    leap["Tail1"] = [20, 0, 0]
    keys = [(0, rest, (0, up, 0)), (4, leap, (0, 0.09, 0)), (9, rest, (0, up, 0))]
    P, loc = keyed(keys, t)
    return out(P, loc[1])


# ------------------------------------------------------------------ tumble: out of the kid's hands, head over heels
def tumble(t):
    P = pose()
    k = t / 0.6
    q = 2 * math.pi * t / 0.2
    P["Body"] = [-360 * k, 0, 10 * math.sin(q)]
    wings(P, lift=40 + 50 * math.sin(q), spread=60 + 20 * math.sin(q * 0.7))
    for side, s in (("Left", 1), ("Right", -1)):
        legs(P, side, thigh=30 * math.sin(q + s), shank=-30 + 30 * math.sin(q * 1.3 + s), foot=-40)
    P["Neck1"] = [-20 + 25 * math.sin(q * 0.9), 0, 0]
    P["Head"] = [-10, 15 * math.sin(q), 0]
    P["Jaw"] = [-30, 0, 0]
    P["Tail1"] = [15 * math.sin(q + 1), 0, 0]
    return out(P, 0.0)


# ------------------------------------------------------------------ idle: looks about, pecks twice
def idle(t):
    look = pose()
    look["Neck1"], look["Head"] = [2, 18, 0], [0, 22, 0]
    wings(look, lift=2)
    look2 = pose()
    look2["Neck1"], look2["Head"] = [2, -16, 0], [0, -20, 0]
    peck = pose()
    peck["Body"], peck["Neck1"], peck["Neck2"], peck["Head"] = [-16, 0, 0], [56, 0, 0], [12, 0, 0], [26, 0, 0]
    peck["Tail1"] = [10, 0, 0]
    up = pose()
    keys = [(0, up, (0, 0, 0)), (8, look, (0, 0, 0)), (18, look, (0, 0, 0)), (24, look2, (0, 0, 0)), (31, up, (0, 0, 0)),
            (35, peck, (0, -0.02, 0)), (38, up, (0, 0, 0)), (42, peck, (0, -0.02, 0)), (46, up, (0, 0, 0)), (54, up, (0, 0, 0))]
    P, loc = keyed(keys, t)
    P["Tail1"][0] += 3 * math.sin(2 * math.pi * t / 1.8)
    return out(P, loc[1])


CLIPS = [
    ("Idle", 54, True, "", idle),
    ("Run", 10, True, "", run),
    ("Panic", 8, True, "", panic),
    ("Flutter", 8, True, "", flutter),
    ("Crow", 36, False, "", crow),
    ("Startled", 10, False, "", startled),
    ("Tumble", 18, True, "", tumble),
]
