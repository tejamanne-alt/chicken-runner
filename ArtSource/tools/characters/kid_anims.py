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


ARM_MAX = 180.0                 # the most the upper arm turns from hanging (see arm)
SHRUG = 0.0                     # the share of a big raise the shoulder takes (see arm)


def arm(P, side, forward=0.0, out=0.0, elbow=0.0, hand=0.0):
    """A raise past 70 degrees is shared with the shoulder (it shrugs up, as a real shoulder does, so the puffed sleeve
    and the hair resting on it ride up with the arm instead of being crushed under it); the upper arm never turns past
    ARM_MAX from hanging."""
    s = 1 if side == "Left" else -1
    raise_ = max(forward, abs(out))
    shrug = SHRUG * max(0.0, raise_ - 70.0)
    if raise_ > 0:
        k = min(1.0, max(0.0, (min(raise_, ARM_MAX) - shrug)) / raise_)
        forward, out = forward * k if forward > 0 else forward, out * k
    P[f"{side}Shoulder"] = [0.0, 0.0, shrug * s]
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


# ------------------------------------------------------------------ run: Kick Off's gait, with the foot planted by IK
# Each step is as long as the ground the body covers while that foot is down, so a planted foot stays put (Kick Off's
# KidAnimator.StrideSwing). Here the planted foot is solved for exactly: while it is down it slides back under the hips
# at the game's run speed (KidModelVisual plays this clip at 6 m/s, faster or slower with her speed), flat on the ground,
# and the thigh and knee angles come from it (two-bone IK); in the swing the heel flicks up behind and the knee drives
# through before the leg reaches out to land. Her leg can reach about 0.2 m either side of her hips, so at 6 m/s each
# foot is down for about 0.07 s of a 0.4 s stride: a bounding toddler's sprint with long flights between the steps.
# LEGS is the kid model's (meshy_kid sets it from the model): thigh and shank lengths, the hip and ankle heights at rest
# and the rest angles of thigh and shank from straight down (forward positive, radians).
LEGS = {"thigh": 0.282, "shank": 0.191, "hip": 0.54, "ankle": 0.067, "ball": 0.07, "thigh_rest": 0.0, "shank_rest": 0.0}
RUN_SPEED = 6.0
RUN_T = 12 / 30
RUN_DUTY = 0.18                 # the part of a stride each foot is down
SWING = 40.0                    # the arms swing in step with this (Kick Off's maxLegSwing)
RUN_LIFT = 0.20                 # how high the swinging foot rises (lower than Kick Off's 0.24, so the knee and heel stay
                                # under the skirt the model can flare without tearing it)


def two_bone(x, y, a, b, bend=1.0):
    """Absolute angles (from straight down, forward positive) of a two-bone limb from its root to a target x forward
    and y down; bend +1 puts the middle joint in front of the root-target line (a knee), -1 behind it (a bird's hock)."""
    d = min(max(math.hypot(x, y), abs(a - b) + 1e-4), a + b - 1e-4)
    line = math.atan2(x, y)
    off = math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d))))
    upper = line + bend * off
    kx, ky = a * math.sin(upper), a * math.cos(upper)
    lower = math.atan2(x - kx, y - ky)
    return upper, lower


def run_leg(u, T=None, speed=None):
    """The leg at stride phase u (0..1, contact at 0): thigh, knee and foot angles (degrees) and the ankle's height."""
    T = T or RUN_T
    speed = speed or RUN_SPEED
    a, b = LEGS["thigh"], LEGS["shank"]
    half = speed * RUN_DUTY * T / 2                 # the foot travels from +half to -half under the hips while down
    hip_ankle = math.sqrt(max(0.05, (0.985 * (a + b)) ** 2 - half * half))
    u = u % 1.0
    if u < RUN_DUTY:
        w = u / RUN_DUTY
        roll = 22 * smooth((w - 0.55) / 0.45)        # rolling onto the toes to push off: the heel rises, the toes stay
        x, lift = half - 2 * half * w, LEGS.get("ball", 0.07) * math.sin(math.radians(roll))
    else:
        w = (u - RUN_DUTY) / (1 - RUN_DUTY)
        # the heel flicks up behind, the knee drives through high, the leg reaches out and comes down to land
        x = -half * math.cos(math.pi * w) - 0.07 * math.sin(math.pi * w) * (1 - w) ** 1.5
        lift = RUN_LIFT * max(0.0, math.sin(math.pi * w)) ** 0.9 * (1 - 0.45 * w)
    upper, lower = two_bone(x, hip_ankle - lift, a, b, 1.0)
    thigh = math.degrees(upper - LEGS["thigh_rest"])
    knee = math.degrees((lower - upper) - (LEGS["shank_rest"] - LEGS["thigh_rest"]))
    flat = -math.degrees(lower - LEGS["shank_rest"])            # the sole level with the ground
    if u < RUN_DUTY:
        foot = flat - roll
    else:
        foot = flat * (1 - smooth(w / 0.3)) - 22 * (1 - smooth(w / 0.3)) + (-12 + 18 * smooth((w - 0.6) / 0.4)) * smooth(w / 0.3)
    return thigh, knee, foot, hip_ankle


def run_pose(t, lean=8.0):
    """Legs from run_leg (left on the stride's first half, right on its second); each arm swings against its own leg,
    as far as the legs swing, the elbow bending more on its forward swing; the body leans in, the head turns back against
    most of the lean (eyes level) and nods a touch under each foot strike; the hips sit low enough for the planted leg to
    reach and rise a little in each flight."""
    P = pose()
    u = (t / RUN_T) % 1.0
    thighs, shins = {}, {}
    hip_ankle = None
    for side, uu in (("Left", u), ("Right", u + 0.5)):
        thigh, knee, foot, hip_ankle = run_leg(uu)
        leg(P, side, thigh, knee, foot)
        thighs[side] = thigh
        shins[side] = -(thigh + knee)         # how far back the shin points (the heel flicked up behind)
    phi = 2 * math.pi * u                     # left foot strikes at phi = 0, right at phi = pi
    arm_swing = 32.0 * SWING / 42.0
    for side, p in (("Left", phi), ("Right", phi + math.pi)):
        c = math.cos(p)                       # its own leg forward at the strike (c = 1): this arm back
        arm(P, side, forward=-arm_swing * c - 6, out=9, elbow=70 + 25 * max(0.0, c), hand=-6)
    P["Hips"] = [0, -7 * math.cos(phi), 0]                       # the hips turn with the forward leg
    P["Spine"] = [lean * 0.6, 3 * math.cos(phi), 0]
    P["Chest"] = [lean * 0.4, 9 * math.cos(phi), 0]               # the shoulders turn against the hips
    P["Neck"] = [-0.3 * lean, -6 * math.cos(phi), 0]
    nod = 2.5 * math.cos(2 * phi - 0.7)
    P["Head"] = [-0.45 * lean + 2 + nod, -3 * math.cos(phi), 0]
    lag = math.cos(2 * phi - 0.95 * math.pi)
    hair(P, back=-10 - 4 * lag, sides=-5 - 2 * lag, out=2 + lag)
    # The skirt flares only as far as the legs need: its front clears the knee driving up, its back the heel flicking
    # up behind, and each side swings forward with its own thigh (never back, which would tear it from the front).
    fwd = max(thighs["Left"], thighs["Right"], 0.0)
    heel = max(0.0, max(shins.values()) - 55.0)
    skirt(P, front=3 + 0.45 * fwd + 2 * lag, back=8 + 0.3 * heel + 2 * lag,
          left=(0.25 * max(thighs["Left"], 0.0), 5 + 2 * lag), right=(0.25 * max(thighs["Right"], 0.0), 5 + 2 * lag))
    # each half stride: a stance (both hips at the planted leg's height), then a flight that rises and falls
    h = (u % 0.5) / 0.5
    flight = 0.0 if h < 2 * RUN_DUTY else math.sin(math.pi * (h - 2 * RUN_DUTY) / (1 - 2 * RUN_DUTY))
    drop = (LEGS["hip"] - LEGS["ankle"]) - hip_ankle
    return P, (0.005 * math.cos(phi), -drop + 0.02 * flight, 0.0)


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


# ------------------------------------------------------------------ air: Kick Off's jump, fall, landing and double jump
def rising_pose(rise=1.0, fall_=0.0):
    """In the air (KidAnimator): rising, the lead knee driven up high and the take-off leg left long behind, the arms
    driving against the legs; falling, the legs reach down for the ground and the arms come forward and out to balance."""
    P = pose()
    lerp = lambda a, b, k: a + (b - a) * k  # noqa: E731
    leg(P, "Left", thigh=lerp(18, 52, rise), knee=lerp(-25, -82, rise), foot=lerp(4, -6, rise))
    leg(P, "Right", thigh=lerp(-12, -30, rise), knee=lerp(-35, -42, rise), foot=lerp(-6, -24, rise))
    arm(P, "Left", forward=lerp(lerp(60, 80, fall_), -35, rise), out=lerp(30, 12, rise), elbow=lerp(30, 85, rise))
    arm(P, "Right", forward=lerp(lerp(-40, 70, fall_), 55, rise), out=lerp(30, 12, rise), elbow=lerp(25, 60, rise))
    lean = lerp(2, 8, rise)
    P["Spine"] = [lean * 0.6, 0, 0]
    P["Chest"] = [lean * 0.4, 0, 0]
    P["Head"] = [-0.6 * lean, 0, 0]
    hair(P, back=lerp(-30, -6, rise), sides=lerp(-8, -4, rise), out=lerp(18, 2, rise))
    skirt(P, front=lerp(26, 38, rise), back=lerp(24, -2, rise), left=(lerp(6, 22, rise), lerp(20, 3, rise)),
          right=(lerp(-4, -10, rise), lerp(20, 3, rise)))
    return P


def jump_up(t):
    """The take-off: from the stride into the rising pose in 0.12 s, a little stretched (Kick Off's jump)."""
    start, start_hips = run_pose(0.0)
    k = smooth(t / 0.12)
    P = mix(start, rising_pose(1.0), k)
    return out(P, (0, start_hips[1] * (1 - k) + 0.02 * k, 0))


def fall(t):
    """Falling: legs reaching down, arms forward and out for balance, a slow paddle of the arms."""
    q = 2 * math.pi * t / 0.4
    P = rising_pose(0.0, 1.0)
    for side, s_ in (("Left", 1), ("Right", -1)):
        P[f"{side}UpperArm"][0] += 6 * math.sin(q + (0 if s_ > 0 else math.pi))
    P["LeftUpperLeg"][0] += 4 * math.sin(q)
    P["RightUpperLeg"][0] -= 4 * math.sin(q)
    P["HairBack"][0] += 4 * math.sin(2 * q)
    return out(P, (0, 0, 0))


def land(t):
    """A quick crouch through the knees that springs back into the stride in 0.22 s (Kick Off's landing)."""
    rest, rest_hips = run_pose(0.0)
    k = max(0.0, 1.0 - t / 0.22)
    k = k * k * (3 - 2 * k)
    P = mix(rest, rest, 0)
    for side in ("Left", "Right"):
        P[f"{side}UpperLeg"][0] += 30 * k
        P[f"{side}LowerLeg"][0] -= 60 * k
        P[f"{side}Foot"][0] += 14 * k
        P[f"{side}LowerArm"][0] += 20 * k
        P[f"{side}UpperArm"][2] += 14 * k * (1 if side == "Left" else -1)
    P["Spine"][0] += 10 * k
    P["Head"][0] -= 8 * k
    P["HairBack"][0] += 14 * k
    P["SkirtFront"][0] += 12 * k
    P["SkirtBack"][0] += 16 * k
    return out(P, (0, rest_hips[1] - 0.047 * k, 0))


DOUBLE_T = 0.46


def double_jump(t):
    """A second push in the air, as if off an invisible step (KidAnimator): the lead knee drives up to the chest while
    the other leg stamps down straight behind, both arms swing up hard past the face and the chest lifts; then both
    knees come up together, the arms drop out for balance; then the legs open down toward the ground. No spin."""
    ft = t / DOUBLE_T
    ss = lambda a, b, x: smooth((x - a) / (b - a))  # noqa: E731
    push = ss(0, 0.12, ft) * (1 - ss(0.3, 0.5, ft))
    gather = ss(0.3, 0.52, ft) * (1 - ss(0.72, 1.0, ft))
    P = rising_pose(max(0.0, 1.0 - ft), max(0.0, ft - 0.4))

    def to(bone, axis, value, k):
        P[bone][axis] += (value - P[bone][axis]) * k

    for k, pose_ in ((push, {"LeftUpperLeg": 82, "LeftLowerLeg": -108, "RightUpperLeg": -24, "RightLowerLeg": -8,
                             "LeftUpperArm": 150, "LeftLowerArm": 28, "RightUpperArm": 120, "RightLowerArm": 40,
                             "Spine": -2.4, "Chest": -1.6, "Head": -8}),
                     (gather, {"LeftUpperLeg": 70, "LeftLowerLeg": -100, "RightUpperLeg": 58, "RightLowerLeg": -96,
                               "LeftUpperArm": 70, "LeftLowerArm": 35, "RightUpperArm": -30, "RightLowerArm": 30,
                               "Spine": 7.2, "Chest": 4.8, "Head": 6})):
        for bone, value in pose_.items():
            to(bone, 0, value, k)
    hair(P, back=-30 * push + 6 * gather - 20 * max(0.0, ft - 0.7), sides=-8, out=6 + 12 * max(0.0, ft - 0.6))
    skirt(P, front=30 + 20 * push + 26 * gather, back=10 * gather - 6 * push, left=(18 * gather + 20 * push, 10),
          right=(18 * gather - 8 * push, 10))
    return out(P, (0, 0.02 * push - 0.02 * gather, 0))


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
        # Hand over hand up the ladder's rails: each hand reaches up beside the head (about 1 m up, 0.19 m out, where
        # the rails are), then pulls down to the shoulder; the game turns her back to the camera on a ladder, and the
        # hands show either side of her hair. (On this rig a negative out swings the arm away from the body.)
        arm(P, side, forward=140 + 28 * math.sin(q) * s, out=-40, elbow=30 - 25 * math.sin(q) * s, hand=10)
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
    ("Run", round(RUN_T * 30), True, "neutral", run),
    ("JumpUp", 9, False, "grin", jump_up),
    ("Fall", 12, True, "shocked", fall),
    ("Land", 8, False, "neutral", land),
    ("DoubleJump", round(DOUBLE_T * 30), False, "grin", double_jump),
    ("Slide", 10, True, "grin", slide),
    ("Vault", 14, False, "straining", vault),
    ("Climb", 12, True, "straining", climb),
    ("Stumble", 21, False, "shocked", stumble),
    ("Dive", 15, False, "straining", dive),
    ("Wade", 24, True, "straining", wade),
]
