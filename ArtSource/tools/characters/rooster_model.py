"""The rooster as a 3D model, built to the B11-B14 turnaround (ArtSource/references/B1*_rooster_*.png).

About 0.62 m to the top of his comb: black-green breast and tail, chestnut back and wings, an orange-gold mane of
neck hackles, a big red comb and wattles, yellow beak and legs, and a heavy, smug brow. Faces -Y, left side at +X.
The M6-M8 plumage textures replace the flat colours here when they arrive in ArtSource/references.
"""
import math

from mathutils import Vector

import charkit as K
from kid_model import reference, srgb

BLACK = (34, 38, 36)
CHESTNUT = (152, 58, 26)
HACKLE = (236, 148, 40)
HEAD = (206, 112, 48)
RED = (206, 40, 38)
YELLOW = (236, 176, 58)
TAIL = (28, 40, 38)
EYE = (232, 170, 40)

BONES = [
    ("Body", (0, 0.03, 0.27), (0, -0.04, 0.33), None, (0, 0, 1)),
    ("Neck1", (0, -0.07, 0.36), (0, -0.105, 0.44), "Body", (0, -1, 0)),
    ("Neck2", (0, -0.105, 0.44), (0, -0.125, 0.5), "Neck1", (0, -1, 0)),
    ("Head", (0, -0.125, 0.5), (0, -0.14, 0.6), "Neck2", (0, -1, 0)),
    ("Jaw", (0, -0.165, 0.518), (0, -0.205, 0.508), "Head", (0, 0, 1)),
    ("Tail1", (0, 0.13, 0.36), (0, 0.2, 0.46), "Body", (0, 0, 1)),
    ("Tail2", (0, 0.2, 0.46), (0, 0.32, 0.5), "Tail1", (0, 0, 1)),
]
for side, sx in (("Left", 1), ("Right", -1)):
    BONES += [
        (f"{side}Wing", (0.07 * sx, -0.05, 0.35), (0.09 * sx, 0.12, 0.31), "Body", (0, 0, 1)),
        (f"{side}UpperLeg", (0.045 * sx, 0.03, 0.25), (0.046 * sx, 0.035, 0.17), "Body", (0, -1, 0)),
        (f"{side}LowerLeg", (0.046 * sx, 0.035, 0.17), (0.046 * sx, 0.005, 0.035), f"{side}UpperLeg", (0, -1, 0)),
        (f"{side}Foot", (0.046 * sx, 0.005, 0.035), (0.046 * sx, -0.06, 0.012), f"{side}LowerLeg", (0, 0, 1)),
    ]


def build(collection=None):
    arm = K.armature("RoosterRig", BONES, collection)
    meshes = []

    def tex(name):
        im = reference(name)
        return K.image_from_pil(name, im) if im is not None else None
    m_black = K.materials("RoosterBlack", srgb(*BLACK), shadow=(0.6, 0.65, 0.75))
    m_chest = K.materials("RoosterChestnut", srgb(*CHESTNUT), image=tex("M6_rooster_body.png"))
    m_hackle = K.materials("RoosterHackle", srgb(*HACKLE), image=tex("M7_rooster_hackles.png"), shadow=(0.78, 0.62, 0.6))
    m_head = K.materials("RoosterHead", srgb(*HEAD))
    m_red = K.materials("RoosterRed", srgb(*RED), shadow=(0.7, 0.55, 0.65), gloss=0.25)
    m_yellow = K.materials("RoosterYellow", srgb(*YELLOW), shadow=(0.78, 0.62, 0.55))
    m_tail = K.materials("RoosterTail", srgb(*TAIL), image=tex("M8_rooster_tail.png"), shadow=(0.6, 0.7, 0.8), gloss=0.18)
    m_eye = K.materials("RoosterEye", srgb(*EYE))
    m_pupil = K.materials("RoosterPupil", srgb(15, 10, 8))

    def add(name, data, mats, weights, subsurf=1):
        if isinstance(weights, dict):
            weights = [weights] * len(data[0])
        elif callable(weights):
            weights = [weights(*co) for co in data[0]]
        ob = K.mesh_object(name, data, subsurf=subsurf, collection=collection)
        K.assign(ob, mats)
        K.bind(ob, arm, weights)
        meshes.append(ob)
        return ob

    def body_w(x, y, z):
        """The body, with the neck end following the neck and the rump following the tail a little."""
        w = {"Body": 1.0}
        if y < -0.08 and z > 0.33:
            w = {"Body": 0.6, "Neck1": 0.4}
        if y > 0.13:
            w = {"Body": 0.7, "Tail1": 0.3}
        return w

    # ---- body: an egg tipped breast-up, black below, chestnut saddle and wings on top
    def egg(t, a):
        breast = 0.12 * max(0.0, math.cos(a)) * math.exp(-((t - 0.45) / 0.25) ** 2)
        return breast
    v, f, uv, r = K.ellipsoid(Vector((0, 0.02, 0.3)), 0.092, 0.155, 0.108, rings=12, n=20, squash=egg)
    tilt = math.radians(-18)
    rv = []
    for x, y, z in v:   # tip the breast up
        dy, dz = y - 0.02, z - 0.3
        rv.append((x, 0.02 + dy * math.cos(tilt) - dz * math.sin(tilt), 0.3 + dy * math.sin(tilt) + dz * math.cos(tilt)))
    add("RoosterBody", (rv, f, uv, r), m_black, body_w, subsurf=2)
    add("RoosterSaddle", K.ellipsoid(Vector((0, 0.06, 0.375)), 0.082, 0.115, 0.05, rings=8, n=16), m_chest,
        lambda x, y, z: {"Body": 1.0})
    for side, sx in (("Left", 1), ("Right", -1)):
        def wing_shape(t, a):
            return -0.25 * max(0.0, math.cos(a)) * t     # tapering toward the front
        wing = add(f"RoosterWing{side[0]}", K.ellipsoid(Vector((0.088 * sx, 0.045, 0.315)), 0.024, 0.11, 0.065,
                                                       rings=8, n=14, squash=wing_shape), m_chest, {f"{side}Wing": 1.0})
        # dark flight feathers along the wing's back edge
        add(f"RoosterPrimaries{side[0]}", K.ellipsoid(Vector((0.09 * sx, 0.13, 0.285)), 0.018, 0.07, 0.03, rings=6, n=12),
            m_tail, {f"{side}Wing": 1.0})
        add(f"RoosterThigh{side[0]}", K.ellipsoid(Vector((0.052 * sx, 0.035, 0.205)), 0.046, 0.058, 0.068, rings=8, n=12),
            m_black, {f"{side}UpperLeg": 0.7, "Body": 0.3})

    # ---- neck and the orange-gold mane of hackles, flaring over the shoulders
    rings = []
    spine = [(0.53, -0.13, 0.034, 0.036), (0.49, -0.12, 0.046, 0.05), (0.45, -0.105, 0.058, 0.064),
             (0.41, -0.085, 0.072, 0.08), (0.375, -0.06, 0.088, 0.095), (0.35, -0.03, 0.098, 0.105),
             (0.335, 0.0, 0.1, 0.1)]
    for z, cy, rx, ry in spine:
        def points(a, z=z):
            return 0.06 * math.sin(9 * a) * max(0.0, (0.47 - z) / 0.13)   # pointed feather tips at the bottom
        rings.append(K.ring(Vector((0, cy + 0.012, z)), rx, ry, 28, wobble=points))
    data = K.loft(rings, cap_start=True)

    def mane_w(x, y, z):
        if z > 0.47:
            return {"Head": 0.5, "Neck2": 0.5}
        if z > 0.42:
            return {"Neck2": 0.6, "Neck1": 0.4}
        if z > 0.37:
            return {"Neck1": 0.7, "Body": 0.3}
        return {"Body": 1.0}
    add("RoosterMane", data, m_hackle, mane_w)

    # ---- head, beak, eyes and the smug brow, comb and wattles
    add("RoosterHead", K.ellipsoid(Vector((0, -0.14, 0.535)), 0.038, 0.052, 0.042, rings=8, n=14), m_head, {"Head": 1.0})
    beak_up = [(0, -0.172, 0.53), (0, -0.19, 0.527), (0, -0.207, 0.521), (0, -0.219, 0.512)]
    add("RoosterBeak", K.tube(beak_up, [0.016, 0.012, 0.007, 0.002], n=8, flatten=0.8, cap_end=False), m_yellow,
        {"Head": 1.0})
    beak_lo = [(0, -0.17, 0.515), (0, -0.188, 0.512), (0, -0.203, 0.509)]
    add("RoosterJaw", K.tube(beak_lo, [0.011, 0.008, 0.003], n=8, flatten=0.8, cap_end=False), m_yellow, {"Jaw": 1.0})
    for sx in (1, -1):
        add(f"RoosterEye{'L' if sx > 0 else 'R'}", K.ellipsoid(Vector((0.03 * sx, -0.16, 0.545)), 0.009, 0.011, 0.011,
                                                             rings=6, n=10), m_eye, {"Head": 1.0})
        add(f"RoosterPupil{'L' if sx > 0 else 'R'}", K.ellipsoid(Vector((0.037 * sx, -0.162, 0.545)), 0.004, 0.006, 0.006,
                                                               rings=5, n=8), m_pupil, {"Head": 1.0}, subsurf=0)
        brow = [(0.03 * sx, -0.145, 0.562), (0.033 * sx, -0.158, 0.561), (0.032 * sx, -0.172, 0.553)]
        add(f"RoosterBrow{'L' if sx > 0 else 'R'}", K.tube(brow, [0.006, 0.007, 0.004], n=6), m_pupil, {"Head": 1.0})
    for i, (y, z, rz) in enumerate([(-0.172, 0.585, 0.03), (-0.152, 0.608, 0.038), (-0.128, 0.616, 0.04),
                                    (-0.104, 0.606, 0.034), (-0.084, 0.588, 0.026)]):
        add(f"RoosterComb{i}", K.ellipsoid(Vector((0, y, z)), 0.009, 0.016, rz, rings=6, n=10), m_red, {"Head": 1.0})
    add("RoosterCombBase", K.ellipsoid(Vector((0, -0.13, 0.572)), 0.01, 0.055, 0.02, rings=6, n=10), m_red, {"Head": 1.0})
    for sx in (1, -1):
        add(f"RoosterWattle{'L' if sx > 0 else 'R'}", K.ellipsoid(Vector((0.009 * sx, -0.172, 0.49)), 0.012, 0.014, 0.03,
                                                                rings=6, n=10), m_red,
            lambda x, y, z: {"Jaw": 0.6, "Head": 0.4})

    # ---- tail: arching black-green sickle feathers fanned across the back
    add("RoosterCoverts", K.ellipsoid(Vector((0, 0.15, 0.36)), 0.06, 0.07, 0.07, rings=8, n=14), m_tail,
        lambda x, y, z: {"Tail1": 0.6, "Body": 0.4})
    fan = []
    for row, (lift, length, w, count, spread) in enumerate([(0.1, 1.1, 0.04, 5, 0.06), (0.03, 0.98, 0.038, 6, 0.075),
                                                          (-0.05, 0.86, 0.034, 5, 0.085), (-0.12, 0.72, 0.03, 4, 0.08)]):
        for k in range(count):
            fx = spread * (k / (count - 1) * 2 - 1) if count > 1 else 0.0
            fan.append((fx, lift + 0.02 * math.cos(k * 1.7), length * (1 - 0.06 * abs(k - (count - 1) / 2)), w))
    for i, (fx, lift, length, w) in enumerate(fan):
        path = []
        for k in range(8):
            s = k / 7
            y = 0.13 + 0.32 * s * length
            z = 0.36 + (0.2 + lift) * math.sin(math.pi * s * 0.85) * length - 0.06 * s * s
            path.append((fx * (0.6 + 0.3 * s), y, z))
        radii = [w * (1 - 0.75 * k / 7) for k in range(8)]
        data = K.tube(path, radii, n=6, flatten=0.22, up=Vector((1, 0, 0)))
        ts = [r / 7 for r in data[3]]
        add(f"RoosterTail{i}", data, m_tail, [K.chain(t, [("Tail1", 0.35), ("Tail2", 1.0)]) for t in ts])

    # ---- legs: yellow scaled shanks, three toes forward and one back, a spur
    for side, sx in (("Left", 1), ("Right", -1)):
        shank = [(0.046 * sx, 0.035, 0.17), (0.046 * sx, 0.02, 0.1), (0.046 * sx, 0.005, 0.035)]
        add(f"RoosterShank{side[0]}", K.tube(shank, [0.018, 0.016, 0.014], n=8), m_yellow, {f"{side}LowerLeg": 1.0})
        for toe, (dx, dy, ln) in enumerate([(-0.02, -1.0, 0.06), (0.0, -1.0, 0.07), (0.02, -1.0, 0.06), (0.0, 1.0, 0.035)]):
            ang = math.atan2(dx * 3, -1) if dy < 0 else 0
            end = (0.046 * sx + dx * sx * 1.6 + math.sin(ang) * 0.0, 0.005 + dy * ln, 0.006)
            path = [(0.046 * sx, 0.005, 0.03), ((0.046 * sx + end[0]) / 2, (0.005 + end[1]) / 2, 0.014), end]
            add(f"RoosterToe{side[0]}{toe}", K.tube(path, [0.01, 0.009, 0.005], n=6), m_yellow,
                {f"{side}Foot": 1.0} if dy < 0 else {f"{side}LowerLeg": 1.0}, subsurf=0)
        add(f"RoosterSpur{side[0]}", K.tube([(0.046 * sx, 0.012, 0.075), (0.046 * sx, 0.03, 0.07)], [0.005, 0.001], n=6),
            m_yellow, {f"{side}LowerLeg": 1.0}, subsurf=0)
    return arm, meshes
