"""The kid's animation clips, keyed onto kid_model's rig from functions of time.

Bone conventions (measured on the rig): +X swings an arm, leg, foot, hair or skirt bone forward (lifting the toes for a
foot); knees bend with -X and elbows with +X; for the spine, neck and head +X leans forward and +Y turns the front toward
the kid's left. Moving an arm, the hair or the skirt outward is +Z on the left side and -Z on the right. The Hips
location is (side, up, forward) in metres.

Each clip: (name, frames at 30 fps, loop, face, function of t in seconds -> (rotations, locations)).
"""
import math
from collections import defaultdict


def g(p, c, w):
    """A smooth bump in phase p (radians) centred on c, of width w, wrapping round the cycle."""
    d = (p - c + math.pi) % (2 * math.pi) - math.pi
    return math.exp(-(d / w) ** 2)


def smooth(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def pose():
    return defaultdict(lambda: [0.0, 0.0, 0.0])


def arm(P, side, forward=0.0, out=0.0, elbow=0.0, hand=0.0):
    s = 1 if side == "Left" else -1
    P[f"{side}UpperArm"] = [forward, 0.0, out * s]
    P[f"{side}LowerArm"] = [elbow, 0.0, 0.0]
    P[f"{side}Hand"] = [hand, 0.0, 0.0]


def leg(P, side, thigh=0.0, knee=0.0, foot=0.0, out=0.0):
    s = 1 if side == "Left" else -1
    P[f"{side}UpperLeg"] = [thigh, 0.0, out * s]
    P[f"{side}LowerLeg"] = [knee, 0.0, 0.0]
    P[f"{side}Foot"] = [foot, 0.0, 0.0]


def hair(P, back=0.0, sides=0.0, out=0.0):
    P["HairBack"] = [back, 0.0, 0.0]
    P["HairLeft"] = [sides, 0.0, out]
    P["HairRight"] = [sides, 0.0, -out]


def skirt(P, front=0.0, back=0.0, left=(0.0, 0.0), right=(0.0, 0.0)):
    """front/back: flare out; left/right: (forward swing, flare out)."""
    P["SkirtFront"] = [front, 0.0, 0.0]
    P["SkirtBack"] = [back, 0.0, 0.0]
    P["SkirtLeft"] = [left[0], 0.0, left[1]]
    P["SkirtRight"] = [right[0], 0.0, -right[1]]


def mix(a, b, k):
    out = pose()
    for key in set(a) | set(b):
        out[key] = [x + (y - x) * k for x, y in zip(a[key], b[key])]
    return out


def keyed(keys, t, fps=30):
    """Pose at time t from [(frame, pose, hips)] keys, eased between them."""
    f = t * fps
    for (f0, p0, h0), (f1, p1, h1) in zip(keys, keys[1:]):
        if f <= f1:
            k = smooth((f - f0) / (f1 - f0))
            return mix(p0, p1, k), [x + (y - x) * k for x, y in zip(h0, h1)]
    return keys[-1][1], keys[-1][2]


def out(P, hips=(0.0, 0.0, 0.0)):
    return {k: tuple(v) for k, v in P.items()}, {"Hips": tuple(hips)}


# ------------------------------------------------------------------ run: 16 frames, about 3.75 steps a second
RUN_T = 16 / 30


def run_pose(t, lean=12.0):
    P = pose()
    phi = 2 * math.pi * t / RUN_T
    thighs = {}
    for side, p in (("Left", phi), ("Right", phi + math.pi)):
        thigh = 10 + 36 * math.cos(p - 0.1 * math.pi)
        knee = -(12 + 14 * g(p, 0.25 * math.pi, 0.25 * math.pi) + 88 * g(p, 1.3 * math.pi, 0.42 * math.pi))
        foot = 12 * g(p, 0.0, 0.3 * math.pi) - 30 * g(p, 0.6 * math.pi, 0.25 * math.pi) + 10 * g(p, 1.3 * math.pi, 0.4 * math.pi)
        leg(P, side, thigh, knee, foot)
        thighs[side] = thigh
    for side, q in (("Left", phi + math.pi), ("Right", phi)):     # each arm swings with the opposite leg
        arm(P, side, forward=45 * math.cos(q) - 5, out=10, elbow=78 + 18 * math.cos(q), hand=-8)
    bob = math.cos(2 * (phi - 0.7 * math.pi))
    P["Hips"] = [3, -6 * math.cos(phi), 0]
    P["Spine"] = [lean * 0.6, 3 * math.cos(phi), 0]
    P["Chest"] = [lean * 0.4, 10 * math.cos(phi), 0]
    P["Neck"] = [-4, -6 * math.cos(phi), 0]
    P["Head"] = [-lean * 0.6 - 2 * bob, -2 * math.cos(phi), 0]
    lag = math.cos(2 * (phi - 0.95 * math.pi))
    hair(P, back=-24 - 8 * lag, sides=-14 - 5 * lag, out=6 + 3 * lag)
    skirt(P, front=6 + 0.55 * max(thighs["Left"], thighs["Right"], 0) + 3 * lag, back=14 + 6 * lag,
          left=(0.35 * thighs["Left"], 6 + 3 * lag), right=(0.35 * thighs["Right"], 6 + 3 * lag))
    return P, (0.006 * math.sin(phi), -0.025 + 0.02 * bob, 0.0)


def run(t):
    P, hips = run_pose(t)
    return out(P, hips)


# ------------------------------------------------------------------ idle: 2.4 s of breathing and fidgeting
def idle(t):
    P = pose()
    b = math.sin(2 * math.pi * t / 2.4)
    w = math.sin(2 * math.pi * t / 2.4 + 1.1)
    P["Spine"] = [2 + 0.8 * b, 0, 1.5 * w]
    P["Chest"] = [1.5 * b, 2 * w, 0]
    P["Head"] = [-2 + 1.5 * math.sin(2 * math.pi * t / 1.2), 6 * w, 3 * math.sin(2 * math.pi * t / 2.4 + 2)]
    for side, s in (("Left", 1), ("Right", -1)):
        arm(P, side, forward=4 + 2 * b * s, out=7 + 1.5 * b, elbow=14 + 3 * w * s)
        leg(P, side, thigh=2 * w * s, knee=-3 - 3 * max(0.0, w * s), foot=0)
    hair(P, back=-3 + 2 * w, sides=-2, out=2 + b)
    skirt(P, front=2, back=3 + w, left=(0, 3 + b), right=(0, 3 - b))
    return out(P, (0.006 * w, -0.004 * abs(w), 0.0))


# ------------------------------------------------------------------ air
def jump_pose():
    P = pose()
    leg(P, "Left", thigh=75, knee=-95, foot=-10)
    leg(P, "Right", thigh=-20, knee=-55, foot=-25)
    for side in ("Left", "Right"):
        arm(P, side, forward=150, out=25, elbow=28, hand=10)
    P["Spine"] = [-2, 0, 0]
    P["Head"] = [-14, 0, 0]
    hair(P, back=-6, sides=-4, out=2)
    skirt(P, front=40, back=-4, left=(25, 2), right=(-8, 2))
    return P


def jump_up(t):
    start, _ = run_pose(0.0)
    k = smooth(t / 0.24)
    P = mix(start, jump_pose(), k)
    wiggle = math.sin(2 * math.pi * t / 0.3) * (1 - k * 0.5)
    P["HairBack"][0] += 6 * wiggle
    return out(P, (0, 0.03 * k, 0))


def fall(t):
    P = pose()
    q = 2 * math.pi * t / 0.4
    for side, s in (("Left", 1), ("Right", -1)):
        arm(P, side, forward=25 + 14 * math.sin(q + (0 if s > 0 else math.pi)), out=70 + 8 * math.sin(q * 2),
            elbow=32, hand=10)
    leg(P, "Left", thigh=35 + 6 * math.sin(q), knee=-28 - 8 * math.sin(q), foot=-10)
    leg(P, "Right", thigh=4 - 6 * math.sin(q), knee=-62 + 8 * math.sin(q), foot=-20)
    P["Spine"] = [-6, 0, 0]
    P["Head"] = [-6, 0, 0]
    hair(P, back=-42 + 5 * math.sin(q * 2), sides=-10, out=26 + 4 * math.sin(q * 2))
    skirt(P, front=30 + 4 * math.sin(q), back=28 + 4 * math.sin(q + 1), left=(5, 26), right=(5, 26))
    return out(P, (0, 0, 0))


def land(t):
    impact = pose()
    for side in ("Left", "Right"):
        leg(impact, side, thigh=52, knee=-88, foot=18)
        arm(impact, side, forward=32, out=28, elbow=42)
    impact["Spine"] = [24, 0, 0]
    impact["Chest"] = [8, 0, 0]
    impact["Head"] = [-20, 0, 0]
    hair(impact, back=12, sides=8, out=10)
    skirt(impact, front=24, back=26, left=(0, 22), right=(0, 22))
    rest, rest_hips = run_pose(0.0)
    keys = [(0, impact, (0, -0.13, 0)), (2, impact, (0, -0.15, 0)), (7, rest, rest_hips)]
    P, hips = keyed(keys, t)
    return out(P, hips)


def double_jump(t):
    """A forward tuck somersault, 0.4 s."""
    k = smooth(t / 0.4)
    P = pose()
    for side in ("Left", "Right"):
        leg(P, side, thigh=100 * math.sin(math.pi * k) + 20, knee=-130 * math.sin(math.pi * k) - 20, foot=-20)
        arm(P, side, forward=60 + 40 * math.sin(math.pi * k), out=20, elbow=110 * math.sin(math.pi * k) + 20)
    P["Hips"] = [360 * k, 0, 0]
    P["Spine"] = [30 * math.sin(math.pi * k), 0, 0]
    P["Head"] = [25 * math.sin(math.pi * k), 0, 0]
    hair(P, back=-30 * math.sin(math.pi * k), sides=-10, out=12)
    skirt(P, front=40 * math.sin(math.pi * k), back=10, left=(20, 15), right=(20, 15))
    return out(P, (0, 0.04 * math.sin(math.pi * k), 0))


# ------------------------------------------------------------------ ground moves
def slide(t):
    P = pose()
    w = math.sin(2 * math.pi * t / (10 / 30))
    P["Spine"] = [-38 + 1.5 * w, 0, 0]
    P["Chest"] = [-6, 0, 0]
    P["Neck"] = [12, 0, 0]
    P["Head"] = [26, 0, 0]
    leg(P, "Left", thigh=86, knee=-4, foot=-18 + 2 * w)
    leg(P, "Right", thigh=22, knee=-112, foot=-30)
    for side in ("Left", "Right"):
        arm(P, side, forward=-48 + 2 * w, out=36, elbow=18, hand=-10)
    hair(P, back=-38, sides=-20, out=8)
    skirt(P, front=62, back=8, left=(34, 10), right=(6, 8))
    return out(P, (0, -0.31, 0.02))


def vault(t):
    reach = pose()
    reach["Spine"], reach["Head"] = [35, 0, 0], [-25, 0, 0]
    for side in ("Left", "Right"):
        arm(reach, side, forward=82, out=14, elbow=10)
    leg(reach, "Left", thigh=22, knee=-42)
    leg(reach, "Right", thigh=-12, knee=-32)
    hair(reach, back=-18)
    plant = pose()
    plant["Spine"], plant["Head"] = [46, 0, 0], [-30, 0, 0]
    for side in ("Left", "Right"):
        arm(plant, side, forward=40, out=16, elbow=0)
        leg(plant, side, thigh=96, knee=-126, foot=-10)
    hair(plant, back=-6, sides=-4, out=6)
    skirt(plant, front=50, back=10, left=(30, 10), right=(30, 10))
    over = pose()
    over["Spine"], over["Head"] = [20, 0, 0], [-14, 0, 0]
    for side in ("Left", "Right"):
        arm(over, side, forward=8, out=26, elbow=10)
        leg(over, side, thigh=62, knee=-58, foot=0)
    hair(over, back=-20, sides=-8, out=6)
    skirt(over, front=34, back=18, left=(18, 12), right=(18, 12))
    ready, ready_hips = run_pose(0.0)
    keys = [(0, reach, (0, 0, 0)), (5, plant, (0, 0.12, 0)), (10, over, (0, 0.06, 0)), (13, ready, ready_hips)]
    P, hips = keyed(keys, t)
    return out(P, hips)


def climb(t):
    P = pose()
    q = 2 * math.pi * t / 0.4
    for side, s in (("Left", 1), ("Right", -1)):
        arm(P, side, forward=145 + 28 * math.sin(q) * s, out=18, elbow=42 - 28 * math.sin(q) * s, hand=10)
        leg(P, side, thigh=55 - 32 * math.sin(q) * s, knee=-92 + 22 * math.sin(q) * s, foot=-10)
    P["Spine"] = [12, 0, 0]
    P["Head"] = [-22, 0, 0]
    hair(P, back=-4, sides=-2, out=3)
    skirt(P, front=30, back=4, left=(14, 6), right=(14, 6))
    return out(P, (0, 0.015 * math.sin(2 * q), 0))


def stumble(t):
    trip = pose()
    trip["Spine"], trip["Chest"], trip["Head"] = [46, 0, -6], [10, 6, 0], [-28, 0, 0]
    arm(trip, "Left", forward=120, out=40, elbow=20)
    arm(trip, "Right", forward=-30, out=52, elbow=24)
    leg(trip, "Left", thigh=52, knee=-30, foot=10)
    leg(trip, "Right", thigh=-46, knee=-22, foot=-30)
    hair(trip, back=10, sides=6, out=14)
    skirt(trip, front=30, back=30, left=(20, 16), right=(-15, 16))
    wind = pose()
    wind["Spine"], wind["Chest"], wind["Head"] = [32, 0, 6], [6, -8, 0], [-20, 0, 0]
    arm(wind, "Left", forward=-22, out=52, elbow=30)
    arm(wind, "Right", forward=112, out=40, elbow=24)
    leg(wind, "Left", thigh=-8, knee=-62, foot=-10)
    leg(wind, "Right", thigh=42, knee=-40, foot=8)
    hair(wind, back=-14, sides=-6, out=18)
    skirt(wind, front=24, back=24, left=(-4, 18), right=(16, 18))
    start, start_hips = run_pose(0.0)
    settle = pose()
    settle["Spine"], settle["Head"] = [20, 0, 0], [-14, 0, 0]
    for side in ("Left", "Right"):
        arm(settle, side, forward=20, out=26, elbow=50)
    leg(settle, "Left", thigh=30, knee=-36)
    leg(settle, "Right", thigh=-14, knee=-50)
    hair(settle, back=-16)
    keys = [(0, start, start_hips), (5, trip, (0, -0.06, 0.02)), (10, wind, (0, -0.04, 0)),
            (15, settle, (0, -0.02, 0)), (20, start, start_hips)]
    P, hips = keyed(keys, t)
    return out(P, hips)


def dive(t):
    crouch = pose()
    crouch["Spine"], crouch["Head"] = [30, 0, 0], [-20, 0, 0]
    for side in ("Left", "Right"):
        leg(crouch, side, thigh=34, knee=-54, foot=10)
        arm(crouch, side, forward=-42, out=16, elbow=20)
    fly = pose()
    fly["Hips"] = [72, 0, 0]
    fly["Spine"], fly["Chest"], fly["Neck"], fly["Head"] = [12, 0, 0], [4, 0, 0], [-20, 0, 0], [-48, 0, 0]
    for side in ("Left", "Right"):
        arm(fly, side, forward=168, out=10, elbow=6, hand=-6)
        leg(fly, side, thigh=-12, knee=-24, foot=-40)
    hair(fly, back=-48, sides=-30, out=10)
    skirt(fly, front=6, back=40, left=(-10, 12), right=(-10, 12))
    keys = [(0, crouch, (0, -0.06, 0)), (5, fly, (0, 0.02, 0.04)), (14, fly, (0, 0.02, 0.04))]
    P, hips = keyed(keys, t)
    return out(P, hips)


def wade(t):
    P = pose()
    T = 0.8
    phi = 2 * math.pi * t / T
    for side, p in (("Left", phi), ("Right", phi + math.pi)):
        lift = g(p, 1.25 * math.pi, 0.55 * math.pi)
        leg(P, side, thigh=-8 + 74 * lift + 10 * math.cos(p), knee=-14 - 96 * lift, foot=-18 * lift)
    for side, q in (("Left", phi + math.pi), ("Right", phi)):
        arm(P, side, forward=24 + 16 * math.cos(q), out=55, elbow=42, hand=10)
    P["Spine"] = [6, 0, 6 * math.sin(phi)]
    P["Head"] = [-6, 0, -4 * math.sin(phi)]
    hair(P, back=-6 + 4 * math.cos(2 * phi), sides=-3, out=4)
    skirt(P, front=14 + 10 * max(0.0, math.cos(phi)), back=6, left=(8, 10), right=(8, 10))
    return out(P, (0.02 * math.sin(phi), -0.03 + 0.02 * math.cos(2 * phi), 0))


CLIPS = [
    ("Idle", 72, True, "neutral", idle),
    ("Run", 16, True, "neutral", run),
    ("JumpUp", 9, False, "grin", jump_up),
    ("Fall", 12, True, "shocked", fall),
    ("Land", 8, False, "neutral", land),
    ("DoubleJump", 12, False, "grin", double_jump),
    ("Slide", 10, True, "grin", slide),
    ("Vault", 14, False, "straining", vault),
    ("Climb", 12, True, "straining", climb),
    ("Stumble", 21, False, "shocked", stumble),
    ("Dive", 15, False, "straining", dive),
    ("Wade", 24, True, "straining", wade),
]
