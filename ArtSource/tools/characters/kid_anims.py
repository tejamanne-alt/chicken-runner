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


ARM_MAX = 120.0                 # the most the upper arm turns from hanging (see out)
SHRUG = 0.3                     # the share of a raise past 70 degrees the shoulder takes (see out)


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


def shoulders(P):
    """A raise of the arm past 70 degrees is shared with the shoulder (it shrugs up, as a real shoulder does, so the
    puffed sleeve and the hair resting on it ride up with the arm instead of being crushed under it), and the upper arm
    never turns more than ARM_MAX from hanging: past that Meshy's sleeve folds into her neck."""
    for side, s in (("Left", 1), ("Right", -1)):
        fwd, twist, out_ = P[f"{side}UpperArm"]
        o = out_ * s
        raise_ = max(fwd, abs(o))
        if raise_ <= 70.0:
            continue
        shrug = SHRUG * (raise_ - 70.0)
        k = max(0.0, min(raise_, ARM_MAX) - shrug) / raise_
        P[f"{side}Shoulder"] = [P[f"{side}Shoulder"][0], P[f"{side}Shoulder"][1], P[f"{side}Shoulder"][2] + shrug * s]
        P[f"{side}UpperArm"] = [fwd * k if fwd > 0 else fwd, twist, o * k * s]


# the frock's measurements (meshy_kid sets them from the model): the waist's height, how far in front of (and behind)
# her middle the front and back skirt bones turn, how long they are from the waist to the hem and how far they lean out
SKIRT_FIT = {"waist": 0.667, "pivot": 0.077, "length": 0.435, "lean": 15.5}
DRESS_SPARE = 0.025             # metres the skirt clears a leg by (its gathers fold in 1-2 cm inside its line)


def dress(P):
    """The skirt clears her legs: each panel flares at least as far as the thigh, knee, shin and foot under it need,
    worked out in the hips' frame from the leg's angles. A leg sits to the side of her middle, where the round skirt is
    further back than at its front and its front panel moves it only by its share (cos^2 of the way round), so the
    flare is what brings the skirt's surface behind the limb's middle and at its outer edge in front of it, DRESS_SPARE
    metres to spare (the gathers fold in inside the skirt's line; the lining turned up inside the hem takes 3 cm more).
    Each side swings forward with its own leg's need in front (back with a heel behind), sharing the flare round the
    hem. The clip's own values stand where they are larger."""
    a, b, hz = LEGS["thigh"], LEGS["shank"], LEGS["hip"]
    W, pv, L, lean = SKIRT_FIT["waist"], SKIRT_FIT["pivot"], SKIRT_FIT["length"], SKIRT_FIT["lean"]
    tl = math.tan(math.radians(lean))
    need = {}
    for side in ("Left", "Right"):
        up = math.radians(P[f"{side}UpperLeg"][0]) + LEGS["thigh_rest"]
        lo = up + math.radians(P[f"{side}LowerLeg"][0]) + (LEGS["shank_rest"] - LEGS["thigh_rest"])
        kf, kz = a * math.sin(up), hz - a * math.cos(up)
        af, az = kf + b * math.sin(lo), kz - b * math.cos(lo)
        toe = lo + math.radians(90.0 + P[f"{side}Foot"][0])           # the foot, square to the shin at rest
        tf, tz = af + 0.09 * math.sin(toe), az - 0.09 * math.cos(toe)
        pts = [(a * 0.35 * math.sin(up), hz - a * 0.35 * math.cos(up), 0.075),
               (a * 0.7 * math.sin(up), hz - a * 0.7 * math.cos(up), 0.065), (kf, kz, 0.055),
               ((kf + af) / 2, (kz + az) / 2, 0.05), (af, az, 0.048), (tf, tz, 0.04)]
        nf = nb = 0.0
        for f, z, r in pts:
            depth = W - z
            if depth < 0.02 or math.hypot(abs(f) - pv, depth) > L + r:
                continue                       # above the waist, or past the hem's reach
            R = pv + depth * tl                # the skirt's radius at that height, at rest
            if depth > L * math.cos(math.radians(lean)) - 0.05:
                R -= 0.03                      # the lining turned up inside the hem
            n = 0.0
            for lat, ahead in ((0.0, 1.0), (0.8, 0.6)):        # behind the limb's middle, and at its outer edge
                xc = min(LEGS.get("x", 0.058) + lat * r, 0.95 * R)
                reach = math.sqrt(R * R - xc * xc)  # how far forward (or back) the skirt is there
                gap = abs(f) + ahead * r + DRESS_SPARE - reach
                if gap > 0:
                    share = (reach / R) ** 2 + 0.4 * (xc / R) ** 2
                    n = max(n, min(80.0, math.degrees(math.atan2(gap, depth)) / share))
            if n <= 0:
                continue
            if f >= 0:
                nf = max(nf, n)
            else:
                nb = max(nb, n)
        need[side] = (nf, nb)
    P["SkirtFront"] = [max(P["SkirtFront"][0], need["Left"][0], need["Right"][0]), 0.0, P["SkirtFront"][2]]
    P["SkirtBack"] = [max(P["SkirtBack"][0], need["Left"][1], need["Right"][1]), 0.0, P["SkirtBack"][2]]
    for side in ("Left", "Right"):
        k = f"Skirt{side}"
        swing = 0.4 * (need[side][0] - need[side][1])      # forward with a knee in front, back with a heel behind
        P[k] = [max(P[k][0], swing) if swing >= 0 else min(P[k][0], swing), 0.0, P[k][2]]


def out(P, hips=(0.0, 0.0, 0.0)):
    if not P.pop("_ik", None):
        shoulders(P)
    dress(P)
    return {k: tuple(v) for k, v in P.items()}, {"Hips": tuple(hips)}


# ------------------------------------------------------------------ run: Kick Off's gait, with the foot planted by IK
# Kick Off's kid (KidAnimator) runs at 4.2 m/s taking 1.9 x 4.2 / 4 = 2.0 strides a second, each step as long as the
# ground the body covers while that foot is down, so a planted foot stays put. Both games frame the kid at the same
# share of the screen, so its pace on screen is 4.2 x 1.08 / 1.3 = 3.5 m/s for her: the game's run speed, and this
# clip's (KidModelVisual plays it faster or slower with her speed). At 3.5 m/s and 2.0 strides a second a stride is
# 1.75 m. The planted foot is solved for exactly: while it is down it slides back under the hips at the run speed, flat
# on the ground, then the heel rises and the foot rolls over the front of its sole, which stays where it is, to push off
# on the toes (RUN_TOE_OFF; Meshy's toes are folded into the foot, so it rolls over their tips); the thigh and knee come
# from it (two-bone IK). Each foot is down for RUN_DUTY of the stride (0.14 s,
# twice the old sprint's share), so the flights between the steps are short and low: a kid's run, not a bound. Her
# hips sit as low as lets the leg reach the planted foot from touch-down (knee a little bent) to toe-off (nearly
# straight), dip a centimetre as the knee gives at mid-stance and rise a centimetre in each flight. In the swing the
# heel flicks up behind (Kick Off's knee fold, most early in the swing), the foot passes under her a hand above the
# ground with the knee forward, the leg reaches out and comes back a little to land (the foot nearly at rest on the
# ground as it touches). The arms swing against the legs (Kick Off's 34 degrees) with the elbows bent 70-95 degrees,
# bending more as the arm comes forward; the body leans 7 degrees and the head keeps the eyes level.
# LEGS is the kid model's (meshy_kid sets it from the model): thigh and shank lengths, the hip and ankle heights at rest,
# how far the ball of the foot and the front of the sole are ahead of the ankle, and the rest angles of thigh and shank
# from straight down (forward positive, radians).
LEGS = {"thigh": 0.282, "shank": 0.191, "hip": 0.54, "ankle": 0.067, "ball": 0.07, "toe": 0.12, "thigh_rest": 0.0,
        "shank_rest": 0.0}
RUN_SPEED = 3.5
RUN_T = 15 / 30                 # 2.0 strides a second (Kick Off's 1.9 x 4.2 / 4)
RUN_DUTY = 0.28                 # the part of a stride each foot is down
RUN_LEAN = 7.0                  # Kick Off's body lean
RUN_DIP = 0.010                 # the hips' dip at mid-stance (the knee giving)
RUN_RISE = 0.008                # and their rise in each flight
RUN_TOE_OFF = 32.0              # how far the heel has risen (degrees) when the toes leave the ground
RUN_ROLL = 0.45                 # the part of the stance the foot is flat; then the heel rises
RUN_REACH = (0.975, 0.985)      # the leg's length at touch-down and at toe-off, of its full length
ARM_SWING = 34.0                # Kick Off's maxArmSwing: each arm swings this far either side
# the swinging ankle's path: (part of the swing, metres forward of the hip, metres above the ground); the touch-down's
# forward reach is added to the last key (it comes from the stance)
RUN_SWING_KEYS = ((0.10, -0.28, 0.17),    # rising off the toes, still going back
                  (0.30, -0.28, 0.32),     # the heel flicked up behind, the thigh still back (Kick Off's knee fold)
                  (0.60, 0.00, 0.13),      # passing under her, the knee forward
                  (0.84, 0.035, 0.105))    # reaching out, a little ahead of where it lands
RUN_LAND = 0.6                  # the swinging foot comes back at this share of the run speed as it touches down


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


def hermite(keys, w):
    """A smooth path through keys [(w, value, slope or None)] at w: cubic Hermite, each slope left None taken from its
    neighbours (Catmull-Rom); values and slopes may be tuples (a path in the plane)."""
    n = len(keys)
    ws = [k[0] for k in keys]
    vals = [k[1] if isinstance(k[1], tuple) else (k[1],) for k in keys]
    slopes = []
    for i, k in enumerate(keys):
        if k[2] is not None:
            slopes.append(k[2] if isinstance(k[2], tuple) else (k[2],))
        else:
            j0, j1 = max(0, i - 1), min(n - 1, i + 1)
            slopes.append(tuple((vals[j1][c] - vals[j0][c]) / (ws[j1] - ws[j0]) for c in range(len(vals[i]))))
    i = 0
    while i < n - 2 and w > ws[i + 1]:
        i += 1
    dw = ws[i + 1] - ws[i]
    s = max(0.0, min(1.0, (w - ws[i]) / dw))
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s * s + 1, s ** 3 - 2 * s * s + s, -2 * s ** 3 + 3 * s * s, s ** 3 - s * s
    out_ = tuple(h00 * vals[i][c] + h10 * dw * slopes[i][c] + h01 * vals[i + 1][c] + h11 * dw * slopes[i + 1][c]
                 for c in range(len(vals[i])))
    return out_ if len(out_) > 1 else out_[0]


def gait(**over):
    """A gait's numbers: the run's (the RUN_ constants, read when called), with any of them changed (speed, T, duty,
    toe_off, roll, reach, dip, rise, keys, land, lean). Shorter strides (speed x T) scale the swing's path down."""
    G = {"speed": RUN_SPEED, "T": RUN_T, "duty": RUN_DUTY, "toe_off": RUN_TOE_OFF, "roll": RUN_ROLL,
         "reach": RUN_REACH, "dip": RUN_DIP, "rise": RUN_RISE, "keys": RUN_SWING_KEYS, "land": RUN_LAND,
         "lean": RUN_LEAN}
    G.update(over)
    return G


_RUN_FIT = {}


def run_fit(G=None):
    """How the stance fits her legs: the hips' height (at touch-down and toe-off) and how far ahead of them the foot
    lands, so that the leg is reach[0] of its length at touch-down and reach[1] at toe-off, the stance covering
    speed x duty x T of ground."""
    G = G or gait()
    key = (tuple(sorted(LEGS.items())), G["speed"], G["T"], G["duty"], G["toe_off"], G["reach"])
    if key in _RUN_FIT:
        return _RUN_FIT[key]
    a, b = LEGS["thigh"], LEGS["shank"]
    h, toe = LEGS["ankle"], LEGS.get("toe", 0.12)
    L = a + b
    p = math.radians(G["toe_off"])
    back = G["speed"] * G["duty"] * G["T"] - toe + toe * math.cos(p) - h * math.sin(p)  # touch-down to toe-off ankle
    y_off = toe * math.sin(p) + h * math.cos(p)                                       # the ankle's height at toe-off
    r_td, r_to = G["reach"][0] * L, G["reach"][1] * L
    lo, hi = h + 0.05, h + r_td
    for _ in range(60):
        y = (lo + hi) / 2
        front = math.sqrt(max(0.0, r_td ** 2 - (y - h) ** 2))
        if (front - back) ** 2 + (y - y_off) ** 2 > r_to ** 2:
            hi = y
        else:
            lo = y
    front = math.sqrt(max(0.0, r_td ** 2 - (lo - h) ** 2))
    _RUN_FIT[key] = {"hip": min(lo, LEGS["hip"] - 0.005), "front": front}
    return _RUN_FIT[key]


def run_hips(u, G=None):
    """The hips' height above the ground at stride phase u (left foot down at 0): each step a stance, the hips at their
    lowest at mid-stance, then a short flight."""
    G = G or gait()
    Y = run_fit(G)["hip"]
    h = (u % 0.5) / 0.5
    st = min(0.999, 2 * G["duty"])
    if h < st:
        return Y - G["dip"] * math.sin(math.pi * h / st)
    return Y + G["rise"] * math.sin(math.pi * (h - st) / (1 - st))


def stance_ankle(w, G=None):
    """The planted foot at stance phase w (0..1): the ankle's place (metres forward of the hip, metres above the
    ground) and how far the heel has risen (degrees)."""
    G = G or gait()
    fit = run_fit(G)
    h, toe = LEGS["ankle"], LEGS.get("toe", 0.12)
    tip = fit["front"] + toe - G["speed"] * G["duty"] * G["T"] * w      # the sole's front moves back at the speed
    k = max(0.0, (w - G["roll"]) / (1 - G["roll"]))
    roll = G["toe_off"] * k ** 1.6
    p = math.radians(roll)
    return tip - toe * math.cos(p) + h * math.sin(p), toe * math.sin(p) + h * math.cos(p), roll


def swing_ankle(w, G=None):
    """The swinging foot at swing phase w (0 at toe-off, 1 at touch-down): the ankle's place, as stance_ankle."""
    G = G or gait()
    fit = run_fit(G)
    D = G["duty"]
    sw = (1 - D) / D                                                       # stance slopes in swing units
    x0, y0, _ = stance_ankle(1.0, G)
    x1, y1, _ = stance_ankle(0.999, G)
    leave = ((x0 - x1) / 0.001 * sw, (y0 - y1) / 0.001 * sw)
    span = G["speed"] * (1 - D) * G["T"]                                   # metres per unit of swing at the speed
    land = (-G["land"] * span, -0.25 * (1 - D) * G["T"])
    scale = min(1.0, G["speed"] * G["T"] / (RUN_SPEED * RUN_T))            # a shorter stride, a smaller swing
    h = LEGS["ankle"]
    keys = [(0.0, (x0, y0), leave)]
    for i, (wk, xk, yk) in enumerate(G["keys"]):
        x = xk * scale + (fit["front"] if i == len(G["keys"]) - 1 else 0.0)
        keys.append((wk, (x, h + (yk - h) * (0.4 + 0.6 * scale)), None))
    keys.append((1.0, (fit["front"], h), land))
    return hermite(keys, w)


def leg_ik(x, hip_y, ankle_y):
    """Thigh and knee angles (degrees, from the rest pose) putting the ankle x forward of the hip and ankle_y above the
    ground with the hips at hip_y, and the foot angle that keeps the sole level."""
    a, b = LEGS["thigh"], LEGS["shank"]
    upper, lower = two_bone(x, hip_y - ankle_y, a, b, 1.0)
    thigh = math.degrees(upper - LEGS["thigh_rest"])
    knee = math.degrees((lower - upper) - (LEGS["shank_rest"] - LEGS["thigh_rest"]))
    flat = -math.degrees(lower - LEGS["shank_rest"])            # the sole level with the ground
    return thigh, knee, flat


def run_leg(u, hip_y=None, G=None):
    """The leg at its own stride phase u (0..1, touch-down at 0) with the hips at hip_y: thigh, knee and foot angles
    (degrees)."""
    G = G or gait()
    u = u % 1.0
    if hip_y is None:
        hip_y = run_fit(G)["hip"]
    D = G["duty"]
    if u < D:
        x, y, roll = stance_ankle(u / D, G)
        thigh, knee, flat = leg_ik(x, hip_y, y)
        return thigh, knee, flat - roll
    w = (u - D) / (1 - D)
    x, y = swing_ankle(w, G)
    thigh, knee, flat = leg_ik(x, hip_y, y)
    # the toes stay pointed as the foot leaves the ground, the foot hangs loose in the swing, and comes level (the toes
    # a touch up) to land flat
    k_out, k_in = smooth(w / 0.35), smooth((w - 0.55) / 0.4)
    foot = (flat - G["toe_off"]) * (1 - k_out) - 18 * k_out
    foot = foot * (1 - k_in) + (flat + 5 * (1 - smooth((w - 0.88) / 0.12))) * k_in
    return thigh, knee, foot


# The left foot touches down at run_left() of the stride, the right half a stride later; the clip starts (u = 0) with
# the right foot at mid-stance and the left leg passing under her, the pose the take-off and the stumble blend from and
# the landing and the stumble end in.
def run_left(G=None):
    return 0.5 - (G or gait())["duty"] / 2


def run_pose(t, lean=None, G=None, crouch=0.0):
    """Legs from run_leg; each arm swings against its own leg (Kick Off's 34 degrees), the elbow bending more on its
    forward swing (70 to 95 degrees); the hips turn with the forward leg and the shoulders against them; the body leans
    in, the head turns back against most of the lean (eyes level) and nods a touch as each foot takes the weight; the
    hips dip at mid-stance and rise in each flight, and sway over the planted foot. crouch lowers the hips that many
    metres (the feet stay where they are, the knees bend)."""
    G = G or gait()
    lean = G["lean"] if lean is None else lean
    P = pose()
    u = (t / G["T"]) % 1.0
    ul = run_left(G)
    hip_y = run_hips(u - ul, G) - crouch
    for side, uu in (("Left", u - ul), ("Right", u - ul - 0.5)):
        thigh, knee, foot = run_leg(uu, hip_y, G)
        leg(P, side, thigh, knee, foot)
    # phi: 0 as the left leg reaches furthest forward (just before it lands), pi as the right one does
    swing = min(1.0, G["speed"] * G["T"] / (RUN_SPEED * RUN_T))
    phi = 2 * math.pi * (u - ul + 0.04)
    for side, p in (("Left", phi), ("Right", phi + math.pi)):
        c = math.cos(p)                       # its own leg forward (c = 1): this arm back
        arm(P, side, forward=-ARM_SWING * swing * c - 6, out=9, elbow=70 + 25 * max(0.0, -c), hand=-6)
    P["Hips"] = [0, -7 * swing * math.cos(phi), 0]               # the hips turn with the forward leg
    P["Spine"] = [lean * 0.6, 3 * swing * math.cos(phi), 0]
    P["Chest"] = [lean * 0.4, 9 * swing * math.cos(phi), 0]       # the shoulders turn against the hips
    P["Neck"] = [-0.3 * lean, -6 * swing * math.cos(phi), 0]
    strike = 2 * math.pi * (u - ul)            # each foot strike at a multiple of pi
    nod = 2.5 * math.cos(2 * strike - 2 * math.pi * G["duty"])     # a dip of the head at each mid-stance
    P["Head"] = [-0.45 * lean + 2 + nod, -3 * swing * math.cos(phi), 0]
    lag = math.cos(2 * strike - 0.95 * math.pi)
    hair(P, back=-8 - 3 * lag, sides=-4 - 1.5 * lag, out=2 + lag)
    # the skirt's sway; dress() (in out) flares it as far as the knee coming through and the heel flicking up behind need
    skirt(P, front=3 + 2 * lag, back=5 + 2 * lag, left=(0.0, 4 + 2 * lag), right=(0.0, 4 + 2 * lag))
    sway = 0.006 * math.cos(2 * math.pi * (u - ul - G["duty"] / 2))  # over the planted foot (+: her left)
    return P, (sway, hip_y - LEGS["hip"], 0.0)


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
    skirt(P, front=lerp(8, 10, rise), back=lerp(8, 0, rise), left=(lerp(2, 8, rise), lerp(8, 3, rise)),
          right=(lerp(0, -3, rise), lerp(8, 3, rise)))
    return P


# The held jump: 1.4 m high, 0.62 s in the air (ChaseTuning: gravity about 29.4 m/s^2, so she leaves the ground at
# 9.1 m/s). KidModelVisual plays JumpUp while she rises and Fall from the top.
JUMP_V, JUMP_G = 9.1, 29.4


def jump_up(t):
    """The take-off and the rise (Kick Off's jump): from the stride into the rising pose in 0.12 s, the lead knee driven
    up off the other foot, then easing out of it as the rise slows (KidAnimator's rising = vertical speed / 6), so the
    clip ends near the top-of-the-jump pose Fall takes over from."""
    start, start_hips = run_pose(0.0)
    rise = max(0.0, min(1.0, (JUMP_V - JUMP_G * t) / 6.0))
    k = smooth(t / 0.12)
    P = mix(start, rising_pose(rise), k)
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


LAND_T = 0.25                   # KidModelVisual shows Land this long, then Run from its first frame


def land(t):
    """Kick Off's landing: the stride runs on underneath (the planted foot keeps pace with the ground) while she sinks
    through the knees, 7 cm at the touch-down and back up in 0.22 s, leaning in, the elbows bending and the arms out for
    balance. It starts LAND_T before the end of a stride, so it ends where Run starts."""
    k = max(0.0, 1.0 - t / 0.22)
    P, hips = run_pose(RUN_T - LAND_T + t, crouch=0.07 * k)
    for side, s_ in (("Left", 1), ("Right", -1)):
        P[f"{side}LowerArm"][0] += 20 * k
        P[f"{side}UpperArm"][0] += 10 * k
        P[f"{side}UpperArm"][2] += 16 * k * s_
    P["Spine"][0] += 6 * k
    P["Chest"][0] += 4 * k
    P["Head"][0] -= 6 * k
    P["HairBack"][0] += 14 * k
    P["SkirtFront"][0] += 4 * k
    P["SkirtBack"][0] += 6 * k
    return out(P, hips)


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
    skirt(P, front=8 + 6 * push + 6 * gather, back=4 * gather, left=(6 * gather + 6 * push, 6), right=(6 * gather, 6))
    return out(P, (0, 0.02 * push - 0.02 * gather, 0))


# ------------------------------------------------------------------ ground moves
SLIDE_LEAN = 58.0               # Kick Off's slideLean: how far the body leans back from upright


def slide(t):
    """Kick Off's feet-first slide, held while she skids: the whole body leaning far back (from the hips, so the frock
    lies along her thighs), the near leg stretched out just off the ground, the far leg tucked with its knee up and its
    foot planted ahead of it, the far hand planted on the ground by the hip and the near arm reaching forward toward the
    feet for balance, chin down so the eyes look on ahead. Each limb is (its direction in the world from straight
    down, forward positive) minus the lean, as in KidAnimator.SlidePose; held still (a scuff that moved the legs read as
    a vibrating leg in Kick Off), only the hair stirring."""
    lean = SLIDE_LEAN
    w = math.sin(2 * math.pi * t / (10 / 30))
    P = pose()
    P["Hips"] = [-lean, 0, 0]
    P["Spine"] = [4, 0, 0]
    P["Chest"] = [2, 0, 0]
    P["Neck"] = [16, 0, 0]
    P["Head"] = [26, 0, 0]
    leg(P, "Left", thigh=82 - lean, knee=-6, foot=-12)                  # nearly level, the heel skimming the ground
    # the far leg: the thigh 45 degrees above level, the shin slanting forward down to the foot, flat on the ground
    leg(P, "Right", thigh=135 - lean, knee=-80, foot=-(135 - 80 - math.degrees(LEGS["shank_rest"])))
    arm(P, "Right", forward=24 - lean, out=22, elbow=10, hand=20)       # down by her side to the hand on the ground
    arm(P, "Left", forward=95 - lean, out=14, elbow=30, hand=-6)        # reaching forward toward her feet
    hair(P, back=-30 + 2 * w, sides=-16, out=8)
    skirt(P, front=6, back=14, left=(4, 8), right=(10, 8))
    return out(P, (0, -0.40, 0.0))


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
    skirt(plant, front=12, back=4, left=(8, 6), right=(8, 6))
    over = pose()
    over["Spine"], over["Head"] = [20, 0, 0], [-14, 0, 0]
    for side in ("Left", "Right"):
        arm(over, side, forward=8, out=26, elbow=10)
        leg(over, side, thigh=62, knee=-58, foot=0)
    hair(over, back=-20, sides=-8, out=6)
    skirt(over, front=10, back=6, left=(6, 6), right=(6, 6))
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
    skirt(P, front=8, back=2, left=(4, 5), right=(4, 5))
    return out(P, (0, 0.015 * math.sin(2 * q), 0))


# Stumbling (0.7 s): the game slows her to 0.45 of her run speed (ChaseTuning.stumbleSpeedFactor), so her feet go to
# short, quick catch-up steps at that speed (two strides in the clip, planted as in the run), with Kick Off's wobble
# on top: a jolt forward as the foot catches, then the head, the body and the arms (one up, the other back) swinging
# back and forth twice, dying away.
STUMBLE_T = 0.7
STUMBLE_SPEED = 0.45


def stumble(t):
    G = gait(speed=RUN_SPEED * STUMBLE_SPEED, T=STUMBLE_T / 2, duty=0.4, toe_off=24.0, lean=10.0)
    P, hips = run_pose(t, G=G)
    jolt = math.sin(math.pi * min(1.0, t / 0.3)) if t < 0.3 else 0.0
    st = min(1.0, t / 0.6)
    wob = math.sin(st * math.pi * 4) * (1 - st)
    P["Spine"][0] += 14 * jolt - 6 * wob
    P["Chest"][0] += 6 * jolt - 2 * wob
    P["Head"][0] += -10 * jolt - 12 * wob
    P["Chest"][1] += 8 * wob
    for side, s_ in (("Left", 1), ("Right", -1)):
        P[f"{side}UpperArm"][0] += 45 * jolt + 40 * wob * s_
        P[f"{side}UpperArm"][2] += (28 * jolt + 10 * abs(wob)) * s_
        P[f"{side}LowerArm"][0] -= 30 * jolt
    P["HairBack"][0] += 16 * jolt + 6 * wob
    P["SkirtFront"][0] += 6 * jolt
    blend = smooth((t - (STUMBLE_T - 0.12)) / 0.12)                     # back to Run's first frame at the end
    if blend > 0:
        R, rh = run_pose(0.0)
        P = mix(P, R, blend)
        hips = tuple(a + (b - a) * blend for a, b in zip(hips, rh))
    return out(P, hips)


def dive(t):
    crouch = pose()
    crouch["Spine"], crouch["Head"] = [30, 0, 0], [-20, 0, 0]
    for side in ("Left", "Right"):
        leg(crouch, side, thigh=34, knee=-54, foot=10)
        arm(crouch, side, forward=-42, out=16, elbow=20)
    fly = pose()
    fly["Hips"] = [72, 0, 0]
    # prone, she looks ahead under her arms (a head thrown further back pushes her bob into her shoulders)
    fly["Spine"], fly["Chest"], fly["Neck"], fly["Head"] = [12, 0, 0], [4, 0, 0], [-14, 0, 0], [-30, 0, 0]
    for side in ("Left", "Right"):
        arm(fly, side, forward=168, out=10, elbow=6, hand=-6)
        leg(fly, side, thigh=-12, knee=-24, foot=-40)
    hair(fly, back=-48, sides=-30, out=10)
    skirt(fly, front=4, back=15, left=(-4, 6), right=(-4, 6))
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
    skirt(P, front=6 + 4 * max(0.0, math.cos(phi)), back=4, left=(3, 6), right=(3, 6))
    return out(P, (0.02 * math.sin(phi), -0.03 + 0.02 * math.cos(2 * phi), 0))


# ------------------------------------------------------------------ level 1 intro: the sneak to the basket, and the lift
# Tiptoe: a slow, exaggerated sneak at 1.1 m/s, 1.2 s a stride (both steps). Each foot is planted on its toes by IK
# (as run_leg plants it) and slides back under her at the walking speed while it is down; she is lowered and leaning in,
# so a leg on tiptoe reaches about 0.28 m either side of her hips, and each foot is down 42 % of the stride (a light,
# floating sneak: both feet are off the ground for a moment between the steps). In the swing the knee lifts high and the
# toes stay pointed; the elbows are bent with the hands up by her chest; the head is forward and turns slowly, watching.
TIPTOE_SPEED = 1.1
TIPTOE_T = 1.2
TIPTOE_DROP = 0.05              # how far her hips are lowered
TIPTOE_POINT = 42.0             # degrees the foot points down: she stands on the balls of her feet
TIPTOE_LIFT = 0.12              # how high the foot is carried (the knee lifts high; higher, the skirt would tear)


def tiptoe_leg(u, bob=0.0):
    """The leg at stride phase u (0..1, toes down at 0): thigh, knee and foot angles (degrees)."""
    a, b = LEGS["thigh"], LEGS["shank"]
    ball = LEGS.get("ball", 0.07)
    ankle_h = LEGS["ankle"] + ball * math.sin(math.radians(TIPTOE_POINT))      # the ankle up, the ball on the ground
    hip_ankle = LEGS["hip"] - TIPTOE_DROP + bob - ankle_h
    reach = math.sqrt(max(0.0, (0.97 * (a + b)) ** 2 - hip_ankle ** 2))
    duty = min(0.46, 2 * reach / (TIPTOE_SPEED * TIPTOE_T))
    half = TIPTOE_SPEED * duty * TIPTOE_T / 2                 # the planted ball travels from +half to -half
    u = u % 1.0
    if u < duty:
        w = u / duty
        x, lift, point = half - 2 * half * w, 0.0, TIPTOE_POINT
    else:
        w = (u - duty) / (1 - duty)
        # the knee lifts high and the foot is carried forward, toes pointed, and set down gently on the toes
        x = -half * math.cos(math.pi * w)
        lift = TIPTOE_LIFT * math.sin(math.pi * w) ** 1.2
        point = TIPTOE_POINT + 12 * math.sin(math.pi * w)
    # the ball is planted; the ankle sits behind and above it by the pitched foot
    ax = x - ball * math.cos(math.radians(point)) + ball
    upper, lower = two_bone(ax, hip_ankle - lift, a, b, 1.0)
    thigh = math.degrees(upper - LEGS["thigh_rest"])
    knee = math.degrees((lower - upper) - (LEGS["shank_rest"] - LEGS["thigh_rest"]))
    foot = -math.degrees(lower - LEGS["shank_rest"]) - point
    return thigh, knee, foot


def tiptoe(t):
    P = pose()
    u = (t / TIPTOE_T) % 1.0
    phi = 2 * math.pi * u
    bob = 0.008 * math.cos(2 * phi)            # a little lift through each step
    for side, uu in (("Left", u), ("Right", u + 0.5)):
        thigh, knee, foot = tiptoe_leg(uu, bob)
        leg(P, side, thigh, knee, foot)
    for side, p in (("Left", phi), ("Right", phi + math.pi)):
        c = math.cos(p)
        # elbows bent, hands up near the chest, held loose, swinging a touch against the legs
        arm(P, side, forward=24 - 8 * c, out=12, elbow=108 + 6 * c, hand=-18)
    P["Hips"] = [0, -4 * math.cos(phi), 0]
    P["Spine"] = [9, 2 * math.cos(phi), 0]
    P["Chest"] = [7, 4 * math.cos(phi), 0]
    P["Neck"] = [6, 0, 0]
    look = 9 * math.sin(phi * 0.5 + 0.4)      # the head turns slowly, once a stride, watching the sleeping neighbour
    P["Head"] = [-8 + 1.5 * math.cos(2 * phi), look - 4 * math.cos(phi), 0]
    hair(P, back=-2, sides=-1, out=1)
    skirt(P, front=4, back=4, left=(0.0, 4), right=(0.0, 4))
    return out(P, (0.006 * math.cos(phi), -TIPTOE_DROP + bob, 0.0))


# BasketLift: she lifts an upturned dome basket by its near rim, hinging it up on its far rim. The game scrubs the clip
# from its first frame to its last as the player holds, so frame k of N - 1 is the lift's progress p = k / (N - 1). The
# basket, in her own frame (she faces forward): BASKET_DIAMETER across, its far rim (the hinge) on the ground
# BASKET_HINGE_FORWARD in front of her root; the game turns it about the far rim by theta(p) = BASKET_MAX_ANGLE x
# smoothstep(p), so the near rim's middle is at forward HINGE - DIAMETER cos(theta), height DIAMETER sin(theta) (+ the
# rim's thickness). Her hands grip the near rim BASKET_GRIP either side of her middle (solved by IK each frame). At p = 0
# she squats with her heels down and her hands on the rim at the ground (ArtSource/references/F4_story_basket.png); as
# it rises she rises, leaning back, and shuffles her hips forward; at p = 1 she is half standing, the basket propped
# open at chest height, and she peers under it.
BASKET_DIAMETER = 0.90
BASKET_HINGE_FORWARD = 1.00
BASKET_MAX_ANGLE = 40.0
BASKET_RIM = 0.03               # the rim's thickness: its middle is this far above where it rests
BASKET_GRIP = 0.20              # her hands, either side of her middle along the near rim
BASKET_FRAMES = 30
BASKET_KNEES = 12.0             # her knees' spread in the squat: she folds in between them, her hands outside them
BASKET_FRONT = 75.0             # the skirt's front, lying up over her knees in the squat
BASKET_SIDE_SWING = -35.0       # the skirt's sides swing back in the squat, clear of the ground and of her hands
BASKET_SIDE_OUT = 16.0          # and flare out over her spread knees
BASKET_WRIST = 25.0             # her wrists bent back at the start, so her fingers lie over the rim

# the rig at rest, for solving her arms: {bone: (parent, rest matrix 4x4 as rows, length)} (meshy_kid fills it)
RIG = {}


def basket_theta(p):
    return math.radians(BASKET_MAX_ANGLE * smooth(p))


def basket_grip(p, side):
    """Where a hand holds the near rim at progress p: (x to her left, forward, up) in metres, in her root's frame."""
    th = basket_theta(p)
    r = BASKET_DIAMETER / 2
    s = 1 if side == "Left" else -1
    d = r + math.sqrt(max(0.0, r * r - BASKET_GRIP ** 2))     # from the hinge line toward her, along the basket
    return (s * BASKET_GRIP, BASKET_HINGE_FORWARD - d * math.cos(th), d * math.sin(th) + BASKET_RIM)


def _mat_mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _inv_rigid(M):
    R = [[M[j][i] for j in range(3)] for i in range(3)]
    t = [-sum(R[i][k] * M[k][3] for k in range(3)) for i in range(3)]
    return [R[0] + [t[0]], R[1] + [t[1]], R[2] + [t[2]], [0, 0, 0, 1]]


def _basis(rot, loc=(0.0, 0.0, 0.0)):
    """Blender's pose basis: translation, then Euler XYZ (applied X first)."""
    x, y, z = (math.radians(v) for v in rot)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    Rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    R = [[sum(Ry[i][k] * Rx[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    R = [[sum(Rz[i][k] * R[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return [R[0] + [loc[0]], R[1] + [loc[1]], R[2] + [loc[2]], [0, 0, 0, 1]]


def _pose_matrix(P, hips, bone, cache):
    if bone in cache:
        return cache[bone]
    parent, rest, _ = RIG[bone]
    basis = _basis(P[bone] if bone in P else (0, 0, 0), hips if parent is None else (0, 0, 0))
    if parent is None:
        M = _mat_mul(rest, basis)
    else:
        M = _mat_mul(_mat_mul(_pose_matrix(P, hips, parent, cache), _mat_mul(_inv_rigid(RIG[parent][1]), rest)), basis)
    cache[bone] = M
    return M


def wrist_at(P, hips, side):
    """Where her wrist is (armature space, Blender axes) in pose P with the Hips moved by `hips`."""
    M = _pose_matrix(P, hips, f"{side}LowerArm", {})
    ln = RIG[f"{side}LowerArm"][2]
    return [M[i][1] * ln + M[i][3] for i in range(3)]


def reach(P, hips, side, target, guess=(60.0, 0.0, 20.0), prefer=(70.0, 0.0, 15.0), pull=0.002, out_=8.0):
    """Solves her arm so the wrist meets target (armature space): the upper arm's forward swing (X) and its sweep
    across (Y: with the arm raised forward, Blender's XYZ order makes Y the sideways sweep and Z a twist), and the
    elbow, by damped Newton with numeric derivatives, gently pulled toward a natural forward reach (`prefer`), the elbow
    kept bending the right way. Out of reach, the arm points straight at the target."""
    s = 1 if side == "Left" else -1
    q = list(guess)

    def put(q_):
        P[f"{side}UpperArm"] = [q_[0], q_[1], out_ * s]
        P[f"{side}LowerArm"] = [q_[2], 0.0, 0.0]

    for _ in range(80):
        put(q)
        w = wrist_at(P, hips, side)
        err = [(target[i] - w[i]) * 100.0 for i in range(3)]          # in centimetres, so the solve is well scaled
        if math.sqrt(sum(e * e for e in err)) < 1e-2 and _ > 5:
            break
        Jc = []
        for k in range(3):
            dq = list(q)
            dq[k] += 0.5
            put(dq)
            w2 = wrist_at(P, hips, side)
            Jc.append([(w2[i] - w[i]) * 100.0 / 0.5 for i in range(3)])
        # solve (J^T J + l I) d = J^T err
        JtJ = [[sum(Jc[a][i] * Jc[b][i] for i in range(3)) + (pull if a == b else 0) for b in range(3)] for a in range(3)]
        Jte = [sum(Jc[a][i] * err[i] for i in range(3)) + pull * (prefer[a] - q[a]) for a in range(3)]
        d = _solve3(JtJ, Jte)
        step = max(abs(x) for x in d) or 1.0
        d = [x * min(1.0, 15.0 / step) for x in d]
        q = [q[0] + d[0], max(-60.0, min(60.0, q[1] + d[1])), max(0.0, min(140.0, q[2] + d[2]))]
    put(q)
    return q


def _solve3(A, b):
    det = (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1]) - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
           + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))
    if abs(det) < 1e-12:
        return [0.0, 0.0, 0.0]
    out = []
    for c in range(3):
        M = [row[:] for row in A]
        for r in range(3):
            M[r][c] = b[r]
        out.append((M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                    + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0])) / det)
    return out


def basket_lift(t):
    p = min(1.0, max(0.0, t * 30 / (BASKET_FRAMES - 1)))
    e = smooth(p)
    P = pose()
    lerp = lambda a_, b_, k: a_ + (b_ - a_) * k  # noqa: E731
    # The rim starts on the ground 0.15 m ahead of her (where her hands grip it) and ends 0.35 m ahead at chest height;
    # her arms reach 0.27 m to the wrist. So she starts in a full toddler squat, bottom behind her heels and her body
    # folded over her knees, and rises to half standing, shuffling her hips 8 cm forward, her arms holding the rim.
    fwd = lerp(-0.07, 0.01, smooth(p * 1.6))       # her bottom behind her heels in the squat, shuffling 8 cm forward
    hip_h = lerp(0.17, 0.46, e)                    # the hip joints: a full squat, heels down, up to half standing
    tilt = lerp(26.0, 18.0, e)                     # the pelvis tipped forward
    drop_head = LEGS.get("pelvis", 0.074)          # the hip joints sit this far below the Hips bone's head
    up = hip_h + drop_head * math.cos(math.radians(tilt)) - (LEGS["hip"] + drop_head)
    hips = (0.0, up, fwd)
    P["Hips"] = [tilt, 0, 0]
    a, b = LEGS["thigh"], LEGS["shank"]
    hip_fwd = LEGS.get("hip_fwd", 0.0) + fwd - drop_head * math.sin(math.radians(tilt))
    for side in ("Left", "Right"):
        x = LEGS.get("ankle_fwd", -0.02) - hip_fwd       # feet flat where they stand
        upper, lower = two_bone(x, hip_h - LEGS["ankle"], a, b, 1.0)
        thigh = math.degrees(upper - LEGS["thigh_rest"]) + tilt
        knee = math.degrees((lower - upper) - (LEGS["shank_rest"] - LEGS["thigh_rest"]))
        foot = -math.degrees(lower - LEGS["shank_rest"])        # the sole flat on the ground: heels down
        leg(P, side, thigh, knee, foot, out=lerp(BASKET_KNEES, 6, e))   # knees together: her hands go round them
    P["Spine"] = [lerp(42, 30, e), 0, 0]
    P["Chest"] = [lerp(26, 16, e), 0, 0]
    for side in ("Left", "Right"):
        P[f"{side}Shoulder"] = [lerp(25.0, 20.0, e), 0.0, 0.0]           # shoulders reaching forward
    P["Neck"] = [lerp(-24, -14, e), 0, 0]
    # her head up to watch the rim, then tipped to one side to peer in under the basket as it opens
    P["Head"] = [lerp(-26, -16, e), lerp(0, 10, e), lerp(0, 8, e)]
    hair(P, back=lerp(4, -2, e), sides=lerp(2, -1, e), out=1)
    # squatting, her skirt spreads out round her so its hem stays off the ground
    # squatting, her skirt's front lies up over her knees, its sides swing back clear of the ground and her hands
    skirt(P, front=lerp(BASKET_FRONT, 4, e), back=lerp(34, 6, e), left=(lerp(BASKET_SIDE_SWING, 0, e), lerp(8, 4, e)),
          right=(lerp(BASKET_SIDE_SWING, 0, e), lerp(8, 4, e)))
    # her hands on the near rim: the wrist 5.5 cm short of the grip, toward her shoulder
    for side in ("Left", "Right"):
        if not RIG:
            arm(P, side, forward=lerp(60, 75, e), out=10, elbow=lerp(10, 20, e), hand=-20)
            continue
        gx, gf, gz = basket_grip(p, side)
        grip = [gx, -gf, gz]                                 # Blender: forward is -Y
        sh = _pose_matrix(P, hips, f"{side}UpperArm", {})
        shp = [sh[i][3] for i in range(3)]
        dv = [shp[i] - grip[i] for i in range(3)]
        dl = math.sqrt(sum(v * v for v in dv)) or 1.0
        target = [grip[i] + 0.055 * dv[i] / dl for i in range(3)]
        reach(P, hips, side, target)
        P[f"{side}Hand"] = [lerp(BASKET_WRIST, -10, e), 0.0, 0.0]      # fingers over the rim, not into the ground
    P["_ik"] = [1, 0, 0]
    rot, loc = out(P, hips)
    # her skirt's sides keep this clip's swing back (dress() would swing them forward after the front)
    sw, fl = lerp(BASKET_SIDE_SWING, 0, e), lerp(BASKET_SIDE_OUT, 4, e)
    rot["SkirtLeft"], rot["SkirtRight"] = (sw, 0.0, fl), (sw, 0.0, -fl)
    return rot, loc


# flags judged natural by eye in the check renders (meshy_kid prints them marked): (clip or *, kind, region, why)
NATURAL_FLAGS = [
    ("*", "squash", "LowerLeg", "the back of a deeply bent knee folding in (run heel flick, squats, landings)"),
    ("*", "squash", "UpperLeg", "the back of a deeply bent knee folding in"),
    ("*", "fold", "LowerLeg", "the crease behind a deeply bent knee"),
    ("*", "fold", "UpperLeg", "the crease behind a deeply bent knee"),
    ("*", "squash", "LowerArm", "the inside of a bent elbow"),
    ("*", "fold", "LowerArm", "the crease inside a bent elbow"),
    ("*", "squash", "Foot", "the front of the ankle folding as the toes point"),
]

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
    ("Stumble", round(STUMBLE_T * 30), False, "shocked", stumble),
    ("Dive", 15, False, "straining", dive),
    ("Wade", 24, True, "straining", wade),
    ("Tiptoe", round(TIPTOE_T * 30), True, "grin", tiptoe),
    ("BasketLift", BASKET_FRAMES, False, "straining", basket_lift),
]
