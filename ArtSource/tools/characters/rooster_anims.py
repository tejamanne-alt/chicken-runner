"""The rooster's animation clips, keyed onto rooster_model's rig.

Bone conventions (measured on the rig): Body +X tips his nose up; Neck1, Neck2 and Head +X bend forward and down and
+Y turns the head; Jaw -X opens the beak; Tail1 and Tail2 +X cock the tail forward and up; a wing +X lifts it (its tip
from hanging back along his flank to straight back, then up over his back), -Z on the left and +Z on the right swing it
out sideways (at 80 it stands straight out from his side), and Y twists it about its own length; UpperLeg (the
drumstick) and LowerLeg (the shank) +X swing forward, Foot (the toes) -X curls the toes down. The Body bone leans
forward-up, so its location is converted from (up, forward) metres by body_loc().
"""
import math

from kid_anims import g, hermite, keyed, mix, pose, smooth, two_bone  # noqa: F401


def body_loc(up=0.0, forward=0.0):
    return (0.0, 0.65 * up + 0.76 * forward, 0.76 * up - 0.65 * forward)


# meshy_rooster cuts his wings free of his body as flaps, so they can beat. FLAP_MAX caps how far a wing lifts or
# spreads (past it the hinge at his shoulder stretches too far).
FLAP_MAX = 85.0


def wings(P, lift=0.0, spread=0.0, twist=0.0, right=None):
    """Both wings: lift (+ up), spread (+ out from his side) and twist, degrees; right=(lift, spread, twist) gives the
    right wing its own (a panicking bird's wings do not beat as one)."""
    rl, rs, rt = right if right is not None else (lift, spread, twist)
    cap = lambda v: max(-FLAP_MAX, min(FLAP_MAX, v))  # noqa: E731
    P["LeftWing"] = [cap(lift), twist, -cap(spread)]
    P["RightWing"] = [cap(rl), -rt, cap(rs)]


def legs(P, side, thigh=0.0, shank=0.0, foot=0.0):
    P[f"{side}UpperLeg"] = [thigh, 0.0, 0.0]
    P[f"{side}LowerLeg"] = [shank, 0.0, 0.0]
    P[f"{side}Foot"] = [foot, 0.0, 0.0]


def out(P, up=0.0, forward=0.0):
    return {k: tuple(v) for k, v in P.items()}, {"Body": body_loc(up, forward)}


# ------------------------------------------------------------------ his legs, for the planted feet
# RIG is the rooster model's (meshy_rooster sets it from the model), in his side view: (forward, up) metres of the
# Body bone's pivot, his left knee (the top of the drumstick: the thigh above it is hidden in his feathers and moves
# with the body), the hock, the foot's joint (where the toes meet the shank) and the tip of his longest toe, at rest.
RIG = {"pivot": (0.011, 0.279), "knee": (0.114, 0.156), "hock": (0.061, 0.096), "ankle": (0.071, 0.029),
       "toe": (0.146, 0.011)}


def _rig():
    p, k, h, a, t = (RIG[n] for n in ("pivot", "knee", "hock", "ankle", "toe"))
    return {"drum": math.hypot(h[0] - k[0], h[1] - k[1]), "shank": math.hypot(a[0] - h[0], a[1] - h[1]),
            "up0": math.atan2(h[0] - k[0], k[1] - h[1]), "lo0": math.atan2(a[0] - h[0], h[1] - a[1]),
            "toe0": math.atan2(t[0] - a[0], a[1] - t[1]), "toe": (t[0] - a[0], t[1] - a[1]), "ankle_h": a[1]}


def rot_down(v, a):
    """(forward, up) turned nose-down by a radians."""
    return (v[0] * math.cos(a) + v[1] * math.sin(a), -v[0] * math.sin(a) + v[1] * math.cos(a))


def knee_at(pitch, up):
    """His knee (forward, up) with the body tipped pitch degrees nose-down about its pivot and raised up metres."""
    p, k = RIG["pivot"], RIG["knee"]
    r = rot_down((k[0] - p[0], k[1] - p[1]), math.radians(pitch))
    return (p[0] + r[0], p[1] + r[1] + up)


def leg_angles(knee, ankle, pitch, toe_abs):
    """Drumstick, shank and toe rotations (degrees) putting the foot's joint at ankle (forward, up) from the knee, the
    hock bending back, and the toes at toe_abs degrees from straight down (forward positive), with the body tipped
    pitch degrees nose-down."""
    R = _rig()
    upper, lower = two_bone(ankle[0] - knee[0], knee[1] - ankle[1], R["drum"], R["shank"], -1.0)
    thigh = math.degrees(upper - R["up0"]) + pitch
    shank = math.degrees((lower - upper) - (R["lo0"] - R["up0"]))
    foot = toe_abs - math.degrees(R["toe0"]) - math.degrees(lower - R["lo0"])
    return thigh, shank, foot


def toe_roll(tip, r):
    """The foot's joint, its toes rolled r degrees about their tip (the joint rising as the foot pushes off)."""
    tf, tu = _rig()["toe"]
    j = rot_down((-tf, -tu), math.radians(r))
    return (tip[0] + j[0], tip[1] + j[1])


# ------------------------------------------------------------------ run: a rooster's run, his feet planted
# He runs at 3.2 m/s (RoosterModelVisual plays Run at that, faster or slower with his speed, and Panic at 1.3 times it).
# A rooster running is a different bird from one standing: his body tipped forward toward level and carried level, low
# and steady, bobbing a little over each foot; his neck stretched forward and his head held still against the bob (the
# neck takes it up), jabbing forward a little with each step as a walking bird's head holds and thrusts; his wings held
# a little out from his sides for balance; his tail bouncing a beat behind the body. 4.3 strides a second (a chicken's
# at this pace), 0.75 m a stride. Each foot is planted: while it is down it moves back under him at the run speed, its
# toes flat, then rolls up onto their tips; then the toes curl as it leaves the ground, the hock folds the foot up under
# him and swings it forward, and the toes spread to land flat. His legs (0.15 m from knee to foot) reach far enough at
# this pace for each foot to be down a third of the stride, so his flights are short: a bird's quick, grounded run.
RUN_SPEED = 3.2
RUN_T = 6 / 30
PANIC_T = 5 / 30


def gait(**over):
    """The run's numbers, with any changed: speed, T (a stride, s), duty, pitch (the body tipped nose-down, degrees),
    roll (the toes' roll onto their tips at push-off, degrees), reach (the leg's length at touch-down and at push-off,
    of its full length), dip and rise (the body's bob, m), lift (how high the swinging foot is carried, m)."""
    G = {"speed": RUN_SPEED, "T": RUN_T, "duty": 0.30, "pitch": 18.0, "roll": 30.0, "reach": (0.95, 0.975),
         "dip": 0.006, "rise": 0.004, "lift": 0.075}
    G.update(over)
    return G


def gait_fit(G):
    """The body's height (m above rest) that lets the stance cover speed x duty x T of ground: the leg at reach[0] of
    its length as the foot lands and reach[1] as it pushes off. Returns (up, how far ahead of the knee the foot lands)."""
    R = _rig()
    L = R["drum"] + R["shank"]
    travel = G["speed"] * G["duty"] * G["T"]
    h = R["ankle_h"]
    lo, hi = -0.08, 0.04
    for _ in range(50):
        up = (lo + hi) / 2
        k = knee_at(G["pitch"], up)
        front = math.sqrt(max(0.0, (G["reach"][0] * L) ** 2 - (k[1] - h) ** 2))
        tip_td = k[0] + front + R["toe"][0]
        tip = (tip_td - travel, h + R["toe"][1])
        a = toe_roll(tip, G["roll"])
        if math.hypot(a[0] - k[0], a[1] - k[1]) > G["reach"][1] * L:
            hi = up
        else:
            lo = up
    k = knee_at(G["pitch"], lo)
    return lo, math.sqrt(max(0.0, (G["reach"][0] * L) ** 2 - (k[1] - h) ** 2))


def stance_foot(w, G, front, knee0):
    """The planted foot at stance phase w: its joint (forward, up) and the toes' angle from straight down."""
    R = _rig()
    h = R["ankle_h"]
    tip = (knee0[0] + front + R["toe"][0] - G["speed"] * G["duty"] * G["T"] * w, h + R["toe"][1])
    r = G["roll"] * max(0.0, (w - 0.5) / 0.5) ** 1.5
    return toe_roll(tip, r), math.degrees(R["toe0"]) - r


def swing_foot(w, G, front, knee0):
    """The swinging foot at swing phase w (0 as the toes leave the ground, 1 as they land): its joint and the toes'
    angle. The toes curl as the foot lifts, hang curled as the hock folds it up and forward, and spread to land."""
    R = _rig()
    h, D = R["ankle_h"], G["duty"]
    (x0, y0), t0 = stance_foot(1.0, G, front, knee0)
    (x1, y1), _ = stance_foot(0.999, G, front, knee0)
    sw = (1 - D) / D
    leave = ((x0 - x1) / 0.001 * sw, (y0 - y1) / 0.001 * sw)
    span = G["speed"] * (1 - D) * G["T"]
    kx, lift = knee0[0], G["lift"]
    keys = [(0.0, (x0, y0), (leave[0], max(leave[1], 0.3 * span))),
            (0.16, (x0 + 0.008, h + 0.85 * lift), None),             # snatched up off the ground, the toes curling
            (0.5, (kx - 0.03, h + lift), None),                      # folded up under him
            (0.8, (kx + front + 0.025, h + 0.6 * lift), None),       # reaching out, the toes spreading
            (1.0, (kx + front, h), (-0.95 * span, -0.6 * span))]     # down onto the ground, at rest on it
    x, y = hermite(keys, w)
    toe0 = math.degrees(R["toe0"])
    curl = toe0 - 38.0                                               # curled: the toes pointing down and back
    k_out, k_in = smooth((w - 0.06) / 0.3), smooth((w - 0.55) / 0.33)
    toe = t0 + (curl - t0) * k_out
    toe = toe + (toe0 + 26.0 * (1 - smooth((w - 0.9) / 0.1)) - toe) * k_in
    return (x, y), toe


def gait_legs(P, u, G, up, front, pitch):
    """Both legs at stride phase u (the left foot landing at 0), the body tipped pitch and raised up."""
    knee = knee_at(pitch, up)
    knee0 = knee_at(G["pitch"], 0.0)                 # the feet's paths are laid out from the knee at its mean place
    D = G["duty"]
    for side, uu in (("Left", u), ("Right", u + 0.5)):
        uu %= 1.0
        if uu < D:
            ankle, toe = stance_foot(uu / D, G, front, knee0)
        else:
            ankle, toe = swing_foot((uu - D) / (1 - D), G, front, knee0)
        legs(P, side, *leg_angles(knee, ankle, pitch, toe))


def gait_pose(t, G, neck=20.0, head=8.0, wing=(6.0, 16.0), wing_beat=(0.0, 0.0), beak=0.0, tail=(-6.0, 5.0, 7.0),
              jab=0.012):
    """A running stride at time t: the legs from gait_legs; the body low and level, dipping over each planted foot and
    rising a little between; the neck stretched forward (neck degrees) holding the head steady against the bob, the
    head (head degrees beak-down) jabbing forward with each step (jab metres, about); the wings held out (lift, spread)
    and beating (amplitude of lift and spread, at the steps); the tail (rest, bounce of Tail1, of Tail2) a beat behind
    the body. Returns the pose and the body's height (m above rest)."""
    P = pose()
    u = (t / G["T"]) % 1.0
    up0, front = gait_fit(G)
    h = (u % 0.5) / 0.5                               # the step: a foot lands at 0
    st = 2 * G["duty"]
    bob = -G["dip"] * math.sin(math.pi * h / st) if h < st else G["rise"] * math.sin(math.pi * (h - st) / (1 - st))
    step = 2 * math.pi * h
    pitch = G["pitch"] + 1.2 * math.sin(step - 1.0)    # the body rocks a little over each foot
    up = up0 + bob
    gait_legs(P, u, G, up, front, pitch)
    P["Body"] = [-pitch, 2.5 * math.cos(2 * math.pi * u), 1.5 * math.sin(2 * math.pi * u)]
    # the head: holds back through each stance (the body runs on under it) and jabs forward as the next foot reaches
    # out; the neck also takes up the body's bob so the head stays level
    hold = h / st if h < st else 1 - (h - st) / (1 - st)
    jab_k = (1 - 2 * smooth(hold)) * jab / 0.012
    level = bob / 0.006
    P["Neck1"] = [neck + 5 * jab_k + 3 * level, -2.5 * math.cos(2 * math.pi * u), 0]
    P["Neck2"] = [0.25 * neck - 3 * jab_k - 2 * level, 0, 0]
    P["Head"] = [head - pitch - 1.25 * neck - 2 * jab_k - level, 1.5 * math.cos(2 * math.pi * u), 0]
    P["Jaw"] = [-beak, 0, 0]
    beat = math.sin(step - 0.6)
    wings(P, lift=wing[0] + wing_beat[0] * beat, spread=wing[1] + wing_beat[1] * beat)
    P["Tail1"] = [tail[0] + tail[1] * math.sin(step - 1.9), 0, 3 * math.sin(2 * math.pi * u - 0.8)]
    P["Tail2"] = [tail[2] * math.sin(step - 2.7), 0, 2 * math.sin(2 * math.pi * u - 1.4)]
    return P, up


def run(t):
    P, up = gait_pose(t, gait())
    return out(P, up)


# ------------------------------------------------------------------ panic: a frantic scramble, wings flapping
# At 1.3 times the run's speed (4.2 m/s): quicker, scrambling strides (6 a second), the body tipped further forward and
# lower, the neck thrust out low, the beak open squawking, the wings half open and flapping (twice a stride, the two
# not quite together) and the tail jerking. Two strides a loop, the second a little different from the first.
def panic(t):
    G = gait(speed=RUN_SPEED * 1.3, T=PANIC_T, duty=0.30, pitch=24.0, roll=34.0, lift=0.075, dip=0.008, rise=0.006)
    P, up = gait_pose(t, G, neck=30.0, head=4.0, beak=0.0, tail=(-2.0, 9.0, 12.0), jab=0.006)
    stride = int(t / PANIC_T) % 2
    q = 2 * math.pi * t / PANIC_T                    # one wingbeat a stride
    lw = math.sin(q + 0.3)
    rw = math.sin(q + 0.3 + 0.5 + 0.3 * stride)      # the right wing a little behind, and more so on the second stride
    wings(P, lift=28 + 36 * lw, spread=46 + 14 * lw, twist=8 * math.cos(q),
          right=(26 + 34 * rw, 44 + 14 * rw, 8 * math.cos(q + 0.5)))
    P["Jaw"] = [-(20 + 10 * math.sin(2 * math.pi * t / 0.11)), 0, 0]
    P["Head"][1] += 6 * math.sin(2 * math.pi * t / (2 * PANIC_T) + 0.5)     # glancing back over a shoulder
    P["Body"][2] += 3 * (1 if stride else -1) * math.sin(q)
    return out(P, up - 0.006)


# ------------------------------------------------------------------ flutter over hops and up onto roofs
# A chicken's wingbeat: a hard downstroke with the wings spread wide (tips sweeping from up over his back to below his
# belly, a little forward), then a quicker upstroke with them half folded and twisted edge-on; 7.5 beats a second. The
# body is tipped up into the climb and bobs with each downstroke, the head is held steady, the legs hang folded with the
# toes curled, the tail spread down as a brake and rudder.
FLAP_T = 4 / 30


def flap(q, up=82.0, down=-42.0, spread=(78.0, 46.0)):
    """A wingbeat at phase q (0..1, the downstroke first): (lift, spread, twist)."""
    if q < 0.55:
        k = smooth(q / 0.55)
        return up + (down - up) * k, spread[0], 10.0
    k = smooth((q - 0.55) / 0.45)
    lift = down + (up - down) * k
    return lift, spread[0] - (spread[0] - spread[1]) * math.sin(math.pi * k), 10.0 - 34.0 * math.sin(math.pi * k)


def flutter(t):
    P = pose()
    q = (t / FLAP_T) % 1.0
    lift, spread, twist = flap(q)
    wings(P, lift=lift, spread=spread, twist=twist)
    down = math.sin(2 * math.pi * q)                 # + through the downstroke
    for side in ("Left", "Right"):
        legs(P, side, thigh=-20, shank=-40, foot=-45)  # folded, the toes curled
    P["Body"] = [30 + 3 * down, 0, 0]
    P["Neck1"] = [-4 - 3 * down, 0, 0]
    P["Neck2"] = [-4, 0, 0]
    P["Head"] = [-14 - 0 * down, 0, 0]
    P["Jaw"] = [-6, 0, 0]
    P["Tail1"] = [-12 - 5 * down, 0, 0]
    P["Tail2"] = [-8 * math.sin(2 * math.pi * q - 1.2), 0, 0]
    return out(P, 0.02 + 0.012 * down)


# ------------------------------------------------------------------ the taunt: wings clapped, chest out, a long crow
# A rooster about to crow stands tall and beats his wings hard two or three times, then stretches his neck up and
# forward, throws his head back a little and opens his beak wide, his throat working through the call, then settles.
def crow(t):
    f = t * 30
    stand = pose()
    wings(stand, lift=4, spread=6)
    stand["Body"] = [6, 0, 0]
    tall = pose()
    tall["Body"], tall["Neck1"], tall["Neck2"], tall["Head"] = [16, 0, 0], [-10, 0, 0], [-4, 0, 0], [-6, 0, 0]
    tall["Tail1"] = [10, 0, 0]
    wings(tall, lift=6, spread=12)
    call = mix(tall, pose(), 0)
    call["Body"], call["Neck1"], call["Neck2"], call["Head"] = [20, 0, 0], [-20, 0, 0], [16, 0, 0], [-30, 0, 0]
    call["Jaw"] = [-32, 0, 0]
    call["Tail1"] = [14, 0, 0]
    wings(call, lift=-2, spread=10)
    keys = [(0, stand, (0, 0, 0)), (3, tall, (0, 0.015, 0)), (12, tall, (0, 0.02, 0)), (16, call, (0, 0.03, 0)),
            (29, call, (0, 0.03, 0)), (35, stand, (0, 0, 0))]
    P, loc = keyed(keys, t)
    if 2 <= f <= 13:                                 # three hard wingbeats before the call
        q = ((f - 2) / 4.0) % 1.0
        k = smooth((f - 2) / 1.5) * (1 - smooth((f - 11) / 2.0))
        lift, spread, twist = flap(q, up=78.0, down=-8.0, spread=(70.0, 40.0))
        P["LeftWing"] = [P["LeftWing"][0] + (lift - P["LeftWing"][0]) * k, twist * k,
                         P["LeftWing"][2] + (-spread - P["LeftWing"][2]) * k]
        P["RightWing"] = [P["RightWing"][0] + (lift - P["RightWing"][0]) * k, -twist * k,
                          P["RightWing"][2] + (spread - P["RightWing"][2]) * k]
        P["Body"][0] += 3 * k * math.sin(2 * math.pi * q)
    if 16 <= f <= 29:                                # the call warbles in his throat
        P["Jaw"][0] += 5 * math.sin(2 * math.pi * t / 0.11)
        P["Neck2"][0] += 2 * math.sin(2 * math.pi * t / 0.2)
    return out(P, loc[1])


# ------------------------------------------------------------------ startled: a leap with a wingbeat, beak open
def startled(t):
    rest, up = gait_pose(0.0, gait())
    crouch = mix(rest, pose(), 0)
    crouch["Body"] = [rest["Body"][0] - 6, 0, 0]
    crouch["Neck1"] = [-14, 0, 0]
    crouch["Head"] = [-6, 0, 0]
    for side in ("Left", "Right"):
        legs(crouch, side, thigh=16, shank=-30, foot=0)
    leap = pose()
    wings(leap, lift=80, spread=74, twist=-10)         # thrown up and open
    for side in ("Left", "Right"):
        legs(leap, side, thigh=-18, shank=-44, foot=-45)
    leap["Body"], leap["Neck1"], leap["Neck2"], leap["Head"], leap["Jaw"] = [14, 0, 0], [-12, 0, 0], [-6, 0, 0], \
        [-14, 0, 0], [-34, 0, 0]
    leap["Tail1"], leap["Tail2"] = [22, 0, 0], [10, 0, 0]
    beat = mix(leap, pose(), 0)
    wings(beat, lift=-18, spread=72, twist=10)        # the downstroke that carries him
    beat["Body"] = [6, 0, 0]
    beat["Tail1"] = [6, 0, 0]
    land, land_up = gait_pose(0.0, gait(speed=RUN_SPEED * 1.3, T=PANIC_T, duty=0.30, pitch=24.0, roll=34.0,
                                        lift=0.075), neck=30.0, head=4.0)
    wings(land, lift=40, spread=50)
    keys = [(0, rest, (0, up, 0)), (2, crouch, (0, up - 0.015, 0)), (4, leap, (0, 0.10, 0)), (6, beat, (0, 0.09, 0)),
            (9, land, (0, land_up - 0.006, 0))]
    P, loc = keyed(keys, t)
    return out(P, loc[1])


# ------------------------------------------------------------------ tumble: out of the kid's hands, head over heels
def tumble(t):
    P = pose()
    k = t / 0.6
    q = (t / FLAP_T) % 1.0
    P["Body"] = [-360 * k, 0, 10 * math.sin(2 * math.pi * t / 0.2)]
    lift, spread, twist = flap(q, up=75.0, down=-15.0, spread=(72.0, 50.0))
    wings(P, lift=lift, spread=spread, twist=twist,
          right=flap((q + 0.15) % 1.0, up=70.0, down=-10.0, spread=(70.0, 48.0)))
    s2 = 2 * math.pi * t / 0.2
    for side, s in (("Left", 1), ("Right", -1)):
        legs(P, side, thigh=30 * math.sin(s2 + s), shank=-30 + 30 * math.sin(s2 * 1.5 + s), foot=-30 - 20 * math.sin(s2 + s))
    P["Neck1"] = [-20 + 25 * math.sin(s2 * 0.5), 0, 0]
    P["Head"] = [-10, 15 * math.sin(s2), 0]
    P["Jaw"] = [-30 + 6 * math.sin(2 * math.pi * t / 0.1), 0, 0]
    P["Tail1"] = [15 * math.sin(s2 + 1), 0, 0]
    return out(P, 0.0)


# ------------------------------------------------------------------ idle: looking about, pecking
# A chicken standing looks about in jerks: his head holds still, then snaps to a new place, often turned to look with
# one eye; then he spots something, cocks his head at it, pecks at it twice and looks up again. His body is still but
# for breathing, a shift of weight and a flick of the tail.
def idle(t):
    look_l = pose()
    look_l["Neck1"], look_l["Neck2"], look_l["Head"] = [2, 8, 0], [0, 8, 0], [0, 22, 8]
    wings(look_l, lift=2, spread=3)
    look_r = pose()
    look_r["Neck1"], look_r["Neck2"], look_r["Head"] = [4, -8, 0], [2, -8, 0], [-4, -26, -10]
    wings(look_r, lift=2, spread=3)
    ahead = pose()
    ahead["Neck1"], ahead["Neck2"], ahead["Head"] = [-4, 0, 0], [-2, 0, 0], [4, 4, 0]
    wings(ahead, lift=2, spread=3)
    spot = pose()                                     # cocking his head at something on the ground
    spot["Body"], spot["Neck1"], spot["Neck2"], spot["Head"] = [-8, 0, 0], [14, 0, 0], [8, 0, 0], [16, -18, -14]
    wings(spot, lift=2, spread=3)
    peck = pose()
    # a peck bends him down through his body, both neck joints and his head, not at one joint
    peck["Body"], peck["Neck1"], peck["Neck2"], peck["Head"] = [-28, 0, 0], [34, 0, 0], [26, 0, 0], [10, 0, 0]
    peck["Tail1"] = [10, 0, 0]
    wings(peck, lift=4, spread=3)
    keys = [(0, look_l, (0, 0, 0)), (9, look_l, (0, 0, 0)), (11, look_r, (0, 0, 0)), (20, look_r, (0, 0, 0)),
            (22, ahead, (0, 0, 0)), (27, ahead, (0, 0, 0)), (29, spot, (0, -0.008, 0)), (33, spot, (0, -0.008, 0)),
            (36, peck, (0, -0.02, 0)), (38, spot, (0, -0.008, 0)), (40, peck, (0, -0.02, 0)), (43, spot, (0, -0.008, 0)),
            (47, ahead, (0, 0, 0)), (52, look_l, (0, 0, 0)), (54, look_l, (0, 0, 0))]
    P, loc = keyed(keys, t)
    breath = math.sin(2 * math.pi * t / 0.9)
    P["Body"][0] += 0.8 * breath
    P["Tail1"][0] += 2 * math.sin(2 * math.pi * t / 1.8)
    if 14 <= t * 30 <= 19:                            # a flick of the tail
        P["Tail1"][2] += 6 * math.sin(math.pi * (t * 30 - 14) / 5)
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
    ("Panic", round(2 * PANIC_T * 30), True, "", panic),
    ("Flutter", round(2 * FLAP_T * 30), True, "", flutter),
    ("Crow", 36, False, "", crow),
    ("Startled", 10, False, "", startled),
    ("Tumble", 18, True, "", tumble),
]
