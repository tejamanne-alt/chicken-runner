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


# meshy_rooster cuts his wings free of his body as flaps, so they can beat. Tucked (Run, Crow, Idle) a wing only shifts a
# little against his side: TUCK scales the clip's wing values and caps them at TUCK_MAX. Beating (full=True: Flutter,
# Panic, Startled, Tumble) they open as far as FLAP_MAX.
TUCK = 0.3
TUCK_MAX = 20.0
FLAP_MAX = 80.0


def wings(P, lift=0.0, spread=0.0, fold=0.0, full=False):
    k, cap = (1.0, FLAP_MAX) if full else (TUCK, TUCK_MAX)
    lift = max(-cap, min(cap, lift * k))
    spread = max(-cap, min(cap, spread * k))
    P["LeftWing"] = [lift, fold, -spread]
    P["RightWing"] = [lift, -fold, spread]


def legs(P, side, thigh=0.0, shank=0.0, foot=0.0):
    P[f"{side}UpperLeg"] = [thigh, 0.0, 0.0]
    P[f"{side}LowerLeg"] = [shank, 0.0, 0.0]
    P[f"{side}Foot"] = [foot, 0.0, 0.0]


def out(P, up=0.0, forward=0.0):
    return {k: tuple(v) for k, v in P.items()}, {"Body": body_loc(up, forward)}


# ------------------------------------------------------------------ run: Kick Off's gait on a bird's legs
# His legs are 0.18 m long and he runs at 5.5 m/s (RoosterModelVisual plays Run at that, Panic at 1.3 times it): no foot
# that short can stay planted at that speed for more than a moment, so, like a real chicken flat out, he scuttles: a
# quick stride (6 a second) with long swings, each leg's drumstick and toes folding up early in its swing (Kick Off's
# knee fold) and reaching forward flat to strike, the body lowest as the legs pass and lifted between the steps, the
# head held steady by the neck while the body pumps, the wings half out for balance and the tail bouncing a beat late.
RUN_SPEED = 5.5
RUN_T = 6 / 30
PANIC_T = 5 / 30


def run_cycle(t, T, lean, wing_lift, wing_flap, beak=0.0, swing=42.0, full=False):
    P = pose()
    phi = 2 * math.pi * t / T
    for side, p in (("Left", phi), ("Right", phi + math.pi)):
        sp = math.sin(p)
        fold = max(0.0, math.cos(p + 0.9)) ** 2            # most early in the swing, none while the foot is down
        legs(P, side, thigh=swing * sp, shank=-8 - 56 * fold + 10 * g(p, math.pi, 0.25 * math.pi),
             foot=8 * g(p, 0.5 * math.pi, 0.35 * math.pi) - 50 * fold + 6 * g(p, math.pi, 0.25 * math.pi))
    spread = abs(math.sin(phi))
    lift = max(0.0, (spread - 0.5) / 0.5) ** 2           # between the steps
    pump = math.cos(2 * phi)                               # the body's pitch, twice a stride
    P["Body"] = [-lean + 2.5 * pump, 3 * math.cos(phi), 2 * math.sin(phi)]
    # The head stays level and steady while the body pumps underneath: the neck takes up the bob and the pitch.
    P["Neck1"] = [lean * 0.55 - 3 * pump, -2 * math.cos(phi), 0]
    P["Neck2"] = [lean * 0.25 - 1.5 * pump, 0, 0]
    P["Head"] = [-lean * 0.75 + 2 * pump - 6 * lift, 0, 0]
    P["Jaw"] = [-beak, 0, 0]
    wings(P, lift=wing_lift + wing_flap * math.sin(2 * phi), spread=wing_lift * 0.8 + wing_flap * 0.5 * math.sin(2 * phi),
          full=full)
    P["Tail1"] = [-4 + 7 * math.sin(2 * phi - 1.2), 0, 3 * math.sin(phi - 0.6)]
    P["Tail2"] = [6 * math.sin(2 * phi - 2.2), 0, 0]
    return P, 0.014 * lift - 0.006


def run(t):
    P, up = run_cycle(t, RUN_T, lean=16, wing_lift=12, wing_flap=10, swing=36.0)
    return out(P, up)


def panic(t):
    P, up = run_cycle(t, PANIC_T, lean=26, wing_lift=44, wing_flap=42, beak=18 + 10 * math.sin(2 * math.pi * t / 0.13),
                      swing=42.0, full=True)
    return out(P, up - 0.004)


# ------------------------------------------------------------------ flutter over hops and up onto roofs
def flutter(t):
    P = pose()
    q = 2 * math.pi * t / (8 / 30)
    wings(P, lift=35 + 45 * math.sin(q), spread=55 + 22 * math.sin(q), full=True)
    for side in ("Left", "Right"):
        legs(P, side, thigh=-18, shank=-36, foot=-40)        # tucked, clear of his wings
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
    open_["Jaw"] = [-30, 0, 0]
    open_["Neck2"] = [-14, 0, 0]
    open_["Head"] = [-20, 0, 0]
    keys = [(0, stand, (0, 0, 0)), (8, puff, (0, 0.02, 0)), (11, open_, (0, 0.025, 0)), (28, open_, (0, 0.025, 0)),
            (35, stand, (0, 0, 0))]
    P, loc = keyed(keys, t)
    if 11 <= t * 30 <= 28:   # the crow warbles
        P["Jaw"][0] += 5 * math.sin(2 * math.pi * t / 0.11)
        P["Neck1"][0] += 2 * math.sin(2 * math.pi * t / 0.2)
    return out(P, loc[1])


# ------------------------------------------------------------------ startled: a leap with wings up, beak open
def startled(t):
    rest, up = run_cycle(0.0, RUN_T, 16, 12, 10)
    leap = pose()
    wings(leap, lift=55, spread=72, full=True)          # thrown open sideways, clear of his tail
    for side in ("Left", "Right"):
        legs(leap, side, thigh=-14, shank=-40, foot=-40)
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
    wings(P, lift=30 + 35 * math.sin(q), spread=66 + 14 * math.sin(q * 0.7), full=True)
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
    look["Neck1"], look["Neck2"], look["Head"] = [2, 10, 0], [0, 10, 0], [0, 18, 0]
    wings(look, lift=2)
    look2 = pose()
    look2["Neck1"], look2["Neck2"], look2["Head"] = [2, -9, 0], [0, -9, 0], [0, -16, 0]
    peck = pose()
    # a peck bends him down through his body, both neck joints and his head, not at one joint
    peck["Body"], peck["Neck1"], peck["Neck2"], peck["Head"] = [-28, 0, 0], [34, 0, 0], [26, 0, 0], [10, 0, 0]
    peck["Tail1"] = [10, 0, 0]
    up = pose()
    keys = [(0, up, (0, 0, 0)), (8, look, (0, 0, 0)), (18, look, (0, 0, 0)), (24, look2, (0, 0, 0)), (31, up, (0, 0, 0)),
            (35, peck, (0, -0.02, 0)), (38, up, (0, 0, 0)), (42, peck, (0, -0.02, 0)), (46, up, (0, 0, 0)), (54, up, (0, 0, 0))]
    P, loc = keyed(keys, t)
    P["Tail1"][0] += 3 * math.sin(2 * math.pi * t / 1.8)
    return out(P, loc[1])


# flags judged natural by eye in the check renders (meshy_rooster prints them marked): (clip or *, kind, region, why)
NATURAL_FLAGS = [
    ("Idle", "cross", "beak x neck", "his wattles pressing into his neck feathers at the bottom of the peck"),
    ("Idle", "cross", "head x neck", "his wattles pressing into his neck feathers at the bottom of the peck"),
    ("*", "squash", "Neck", "the neck feathers bunching on the inside of the bend"),
    ("*", "fold", "Neck", "the neck feathers bunching on the inside of the bend"),
    ("*", "squash", "LowerLeg", "the inside of the bent hock"),
    ("*", "fold", "Wing", "the skin of the wing's hinge at his shoulder folding as the wing beats up (like an armpit)"),
    ("*", "fold", "body/Body", "the skin of the wing's hinge at his shoulder folding as the wing beats up"),
    ("Idle", "cross", "x body", "the wing's underside and his flank under it, hidden inside the folded wing"),
    ("Crow", "cross", "x body", "the wing's underside and his flank under it, hidden inside the folded wing"),
]

CLIPS = [
    ("Idle", 54, True, "", idle),
    ("Run", round(RUN_T * 30), True, "", run),
    ("Panic", round(PANIC_T * 30), True, "", panic),
    ("Flutter", 8, True, "", flutter),
    ("Crow", 36, False, "", crow),
    ("Startled", 10, False, "", startled),
    ("Tumble", 18, True, "", tumble),
]
