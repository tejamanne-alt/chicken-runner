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
import json
import math
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "Assets" / "ChickenRunner" / "Art" / "Levels" / "level1.json"
MODELS = {m["name"]: m for m in json.loads((ROOT / "Assets/ChickenRunner/Art/Models/models.json").read_text())["models"]}
CUT = ROOT / "ArtSource" / "cutouts"


# ------------------------------------------------------------------ the game's numbers, read from its C#
def tuning():
    src = (ROOT / "Assets/ChickenRunner/Scripts/Core/ChaseTuning.cs").read_text()
    t = {m.group(1): float(m.group(2)) for m in re.finditer(r"public float (\w+) = ([-\d.]+)f;", src)}
    t.update({m.group(1): int(m.group(2)) for m in re.finditer(r"public int (\w+) = (-?\d+);", src)})
    return t


T = tuning()
G = 8 * T["jumpHeight"] * T["jumpReferenceSpeed"] ** 2 / T["jumpLength"] ** 2          # JumpMath.Gravity
V0 = math.sqrt(2 * G * T["jumpHeight"])                                                 # JumpMath.JumpVelocity
V2 = math.sqrt(2 * G * max(0.0, T["doubleJumpTotalHeight"] - T["jumpHeight"]))           # DoubleJumpVelocity
LOW = max(1.0, T["jumpHeight"] / T["tapJumpHeight"])                                    # LowJumpGravityMultiplier
RUN = T["kidRunSpeed"]
KID_R = 0.175                                                                           # KidController.radius
JUMP_LEN = RUN * 2 * V0 / G                                                             # JumpMath.JumpLengthAt


def flight(held=True, dt=1 / 240):
    """(t, height of the feet) through a jump from flat ground, held or tapped (KidController's gravity)."""
    out, t, h, v = [], 0.0, 0.0, V0
    while True:
        g = G if (held or v <= 0) else G * LOW
        v -= g * dt
        h += v * dt
        t += dt
        if h <= 0:
            out.append((t, 0.0))
            return out
        out.append((t, h))


HELD, TAP = flight(True), flight(False)


def takeoff_window(span, top, path):
    """The take-off x (relative to the span's start) from which a jump on `path` keeps the feet above `top` over the
    whole span (widened by the kid's radius on both sides): (earliest, latest), or None."""
    a0, a1 = -KID_R, span + KID_R
    above = [RUN * t for t, h in path if h > top]
    if not above:
        return None
    lo, hi = above[0], above[-1]           # the stretch of the jump with the feet above the top
    if hi - lo < a1 - a0:
        return None
    return a1 - hi, a0 - lo                # earliest: the span's end leaves the stretch's end; latest: its start


# ------------------------------------------------------------------ the pieces, placed as GameBuilder.Kit places them
def aspect(piece):
    m = MODELS.get(piece)
    if m:
        return m["width"] / m["height"]
    from PIL import Image
    for p in CUT.rglob(piece + ".png"):
        w, h = Image.open(p).size
        return w / h
    return 1.0


def visual(piece, x, y=0.0, z=0.0, h=0.0, w=0.0, mirror=False, flat=False, turn=0.0, kind="art"):
    a = aspect(piece)
    if h:
        w = h * a
    elif w:
        h = w / a
    return {"piece": piece, "x": round(x, 3), "y": round(y, 3), "z": round(z, 3), "w": round(w, 3), "h": round(h, 3),
            "mirror": mirror, "flat": flat, "turn": round(turn, 1), "kind": kind}


class Plan:
    def __init__(self):
        self.sections = []
        self.rng = random.Random(1)

    def section(self, name, x, length, note):
        s = {"name": name, "x": x, "length": length, "note": note, "items": []}
        self.sections.append(s)
        return s

    def add(self, s, kind, x, visuals=(), **kw):
        item = {"kind": kind, "x": round(x, 3)}
        item.update({k: (round(v, 3) if isinstance(v, float) else v) for k, v in kw.items()})
        item["visuals"] = list(visuals)
        s["items"].append(item)
        return item

    # obstacles, as Kit builds them (trigger sizes, card sizes and z)
    def pots(self, s, x, hidden=False, ident=""):
        mirror = self.rng.random() < 0.5
        self.add(s, "pots", x, [visual("pot_stack", x, z=0.05, h=0.68, mirror=mirror)], mirror=mirror, hidden=hidden,
                 id=ident, top=0.6, span=0.45)
        if not hidden:
            self.hop_over(s, x, 0.45, 0.6)
            self.jump_arc(s, x)

    def dung(self, s, x):
        self.add(s, "dung", x, [visual("dung", x, z=0.05, w=0.6)], top=0.2, span=0.55)
        self.hop_over(s, x, 0.55, 0.2)
        self.jump_arc(s, x)

    def dog(self, s, x):
        self.add(s, "dog", x, [visual("dog_sleeping", x, z=0.05, w=0.95)], top=0.36, span=0.9)
        self.hop_over(s, x, 0.9, 0.36)
        self.jump_arc(s, x)

    def puddle(self, s, x, width=1.6):
        self.add(s, "puddle", x, [{"piece": "_water", "x": x, "y": 0.004, "z": 0.0, "w": width, "h": 0.0, "d": 0.9,
                                   "mirror": False, "flat": True, "turn": 0, "kind": "water"},
                                  visual("hand_pump", x - width * 0.3, z=0.9, h=1.2)],
                 width=width, top=0.15, span=width)
        self.hop_over(s, x, width, 0.15)
        self.jump_arc(s, x)

    def cart(self, s, x):
        self.add(s, "cart", x, [visual("bullock_cart", x + 1.8, z=0.05, w=3.6)], bed=0.95, span=3.6 * 0.62)
        self.hop(s, x - 0.8, 4.0, 1.6)
        self.mango_line(s, x + 0.4, 4, 0.5, 1.5)
        self.mango_line(s, x + 0.8, 3, 0.7, 2.9)

    def hop(self, s, x, length, height):
        self.add(s, "hop", x, length=length, height=height)

    def hop_over(self, s, centre, span, top, run_up=0.6):
        """The rooster's hop over an obstacle: from run_up before it to run_up after, its arc 0.25 m clear of the
        obstacle's top even at its edges (his hop's height is a sine over its length)."""
        length = span + 2 * run_up
        height = (top + 0.25) / math.sin(math.pi * run_up / length)
        self.hop(s, centre - span / 2 - run_up, length, round(height, 2))

    def mischief(self, s, x, target):
        self.add(s, "mischief", x, target=target)

    # pickups
    def mango(self, s, x, y):
        self.add(s, "mango", x, [visual("Mango", x, y, kind="pickup", h=0.28)], y=y)

    def mango_line(self, s, x, count, spacing, y):
        for i in range(count):
            self.mango(s, x + i * spacing, y)

    def arc(self, s, start, length, peak, count, lift=0.0):
        for i in range(count):
            k = (i + 1) / (count + 1)
            self.mango(s, start + k * length, lift + 0.55 + 4 * peak * k * (1 - k))

    def jump_arc(self, s, centre, lift=0.0):
        self.arc(s, centre - JUMP_LEN / 2, JUMP_LEN, T["jumpHeight"], 5, lift)

    def chilli(self, s, x, y=0.6):
        self.add(s, "chilli", x, [visual("Chilli", x, y, kind="pickup", h=0.3)], y=y)

    def feather(self, s, x, y, index):
        self.add(s, "feather", x, [visual("Feather", x, y, kind="pickup", h=0.35)], y=y, index=index)

    # set dressing: a prop behind or in front of the lane, a mark on the ground
    def prop(self, s, piece, x, z, h=0.0, w=0.0, mirror=False, y=0.0):
        self.add(s, "prop", x, [visual(piece, x, y, z, h=h, w=w, mirror=mirror)], piece=piece, z=z, h=h, w=w, mirror=mirror,
                 y=y)

    def decal(self, s, piece, x, z, w):
        turn = self.rng.uniform(0, 360)
        flat = piece in ("leaf_1", "leaf_2", "leaf_3", "twigs", "footprints", "hen_prints", "hoof_prints", "cart_rut",
                         "cracked_mud", "kolam_1", "kolam_2", "kolam_3", "kolam_4", "kolam_5", "kolam_6")
        self.add(s, "decal", x, [visual(piece, x, 0.0, z, w=w, flat=flat, turn=turn if flat else turn % 40 - 20,
                                        kind="decal")], piece=piece, z=z, w=w, turn=turn)

    def litter(self, s, count, avoid=()):
        pieces = ["leaf_1", "leaf_2", "twigs", "husk", "footprints", "hen_prints", "pebbles", "tuft_1", "tuft_2", "tuft_3"]
        x0, x1 = s["x"], s["x"] + s["length"]
        placed = 0
        while placed < count:
            x = self.rng.uniform(x0 + 0.5, x1 - 0.5)
            z = self.rng.uniform(-1.3, 1.3)
            # never on the running line next to an obstacle, where a mark could be read as one
            if abs(z) < 0.7 and any(abs(x - a) < 1.6 for a in avoid):
                continue
            self.decal(s, self.rng.choice(pieces), x, z, self.rng.uniform(0.4, 0.8))
            placed += 1


# ------------------------------------------------------------------ the course
def design():
    p = Plan()

    # The neighbour's yard. The kid starts at 0 beside the basket; the runway behind her is the yard's back.
    s = p.section("Yard", -10.0, 24.0, "The neighbour naps on his cot; hens peck about; hold to lift the basket.")
    # the basket the rooster sits under (0.9 m across, so he fits): its near rim 0.25 m in front of her, its far rim,
    # the hinge it lifts on, 1.15 m (kid_anims.BASKET_*); the kid tiptoes in from -4.4 m past the sleeping neighbour
    p.add(s, "basket", 0.7, [visual("chicken_basket", 0.7, z=0.0, w=0.9)], diameter=0.9, hinge=1.15, walkFrom=-4.4)
    p.add(s, "neighbour", -2.4, [visual("neighbour_sleeping", -2.4, z=1.3, h=1.0),
                                 visual("neighbour_awake", -2.4, z=1.3, h=1.25, kind="hidden")], z=1.3)
    p.prop(s, "hens_basket", -5.6, 1.2, h=0.55)
    p.prop(s, "chicken_basket", 2.6, 1.6, h=0.6, mirror=True)
    p.prop(s, "water_pot_stand", -7.8, 1.7, h=1.1)
    p.prop(s, "tulsi_planter", 4.6, 1.7, h=1.1)
    for i, (hx, hz) in enumerate(((1.6, 1.15), (3.4, 1.35), (6.2, 1.1))):
        p.prop(s, f"hen_{1 + i % 3}", hx, hz, h=0.42, mirror=i == 1)
    p.decal(s, "hen_prints", 2.4, 0.85, 0.7)
    p.decal(s, "kolam_2", -5.2, -1.2, 1.1)
    p.mango_line(s, 5.0, 6, 1.2, 0.6)
    p.litter(s, 3, avoid=(0.7,))

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
        p.mango(s, 87.0 + i * 0.9, 0.6 + 0.45 * math.sin(i * 0.8))
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


# ------------------------------------------------------------------ the audit
def audit(p, course_length):
    problems, notes = [], []
    secs = p.sections
    for a, b in zip(secs, secs[1:]):
        if abs(a["x"] + a["length"] - b["x"]) > 1e-6:
            problems.append(f"sections {a['name']} and {b['name']} do not meet")
    end = secs[-1]["x"] + secs[-1]["length"]
    if end < course_length:
        problems.append(f"the course ends at {end} m, before its length {course_length} m")

    obstacles = []
    for s in secs:
        x0, x1 = s["x"], s["x"] + s["length"]
        for it in s["items"]:
            if not (x0 <= it["x"] < x1):
                problems.append(f"{it['kind']} at {it['x']} lies outside its section {s['name']} [{x0}, {x1})")
            if it["kind"] in ("pots", "dung", "dog", "puddle") and not it.get("hidden"):
                obstacles.append((it["x"] - it["span"] / 2, it["x"] + it["span"] / 2, it["top"], it["kind"], s["name"]))
            if it["kind"] == "cart":
                obstacles.append((it["x"], it["x"] + it["span"], it["bed"], "cart", s["name"]))
            if it["kind"] in ("pots", "dung", "dog", "puddle", "cart"):
                ext = it["span"] / 2 if it["kind"] != "cart" else it["span"]
                if it["x"] - (ext if it["kind"] != "cart" else 0) < x0 or it["x"] + ext > x1:
                    problems.append(f"{it['kind']} at {it['x']} crosses the edge of section {s['name']}")
    obstacles.sort()

    # every obstacle: a held jump must clear it with a comfortable window; report the tap's
    windows = []
    for a0, a1, top, kind, name in obstacles:
        if kind == "cart":
            windows.append((a0, a1, kind, name, None, None))
            continue
        held = takeoff_window(a1 - a0, top, HELD)
        tap = takeoff_window(a1 - a0, top, TAP)
        if held is None or (held[1] - held[0]) / RUN < 0.2:
            problems.append(f"{kind} at {a0:.1f} ({name}): a held jump has under 0.2 s to clear it")
        windows.append((a0, a1, kind, name, held, tap))

    # consecutive obstacles: after clearing one at the latest moment, room to react and still clear the next
    react = 0.3 * RUN
    for (a0, a1, ka, na, ha, _), (b0, b1, kb, nb, hb, _) in zip(windows, windows[1:]):
        if ka == "cart":
            land = a1                                  # running off the bed
        else:
            land = a0 + ha[1] + JUMP_LEN               # the latest take-off over A, landed
        latest_b = b0 + (hb[1] if hb else 0.0)
        slack = latest_b - land - react
        if slack < 0.5:
            problems.append(f"{ka} at {a0:.1f} then {kb} at {b0:.1f}: {slack:.2f} m to react after the landing")
        if b0 - a1 < 4.5 and kb != "cart":
            problems.append(f"{ka} at {a0:.1f} and {kb} at {b0:.1f} only {b0 - a1:.1f} m apart")

    # the rooster hops every obstacle, high enough, starting before it
    hops = [(it["x"], it["x"] + it["length"], it["height"]) for s in secs for it in s["items"] if it["kind"] == "hop"]
    for a0, a1, top, kind, name in obstacles:
        h = next((hp for hp in hops if hp[0] <= a0 - 0.2 and hp[1] >= a1 + 0.1), None)
        if h is None:
            problems.append(f"{kind} at {a0:.1f}: no rooster hop over it")
            continue
        k0 = (a0 - h[0]) / (h[1] - h[0])
        k1 = (a1 - h[0]) / (h[1] - h[0])
        lowest = h[2] * min(math.sin(math.pi * k0), math.sin(math.pi * k1))
        if lowest < top + (0.15 if kind != "cart" else -0.2):
            problems.append(f"{kind} at {a0:.1f}: the rooster's hop is only {lowest:.2f} m up over it")

    # chillies: no obstacle within the boost's reach
    boost = RUN * (1 + T["boostSpeedBonus"]) * T["boostDuration"]
    for s in secs:
        for it in s["items"]:
            if it["kind"] != "chilli":
                continue
            nxt = [o for o in obstacles if o[0] > it["x"]]
            if nxt and nxt[0][0] - it["x"] < boost:
                problems.append(f"chilli at {it['x']}: {nxt[0][3]} {nxt[0][0] - it['x']:.1f} m after it, inside the boost")

    # feathers: one of each, reachable with a double jump from where they sit over
    feathers = [it for s in secs for it in s["items"] if it["kind"] == "feather"]
    if sorted(f["index"] for f in feathers) != [0, 1, 2]:
        problems.append("the three feathers (0, 1, 2) are not all there once")
    reach = T["doubleJumpTotalHeight"] + 0.55 + 0.3
    for f in feathers:
        base = 0.95 if any(o[3] == "cart" and o[0] - 1 <= f["x"] <= o[1] + 3 for o in obstacles) else 0.0
        if f["y"] > base + reach:
            problems.append(f"feather {f['index']} at {f['x']}: {f['y']} m is above a double jump's reach")

    # mischief: its pots are hidden and the spot is after them
    for s in secs:
        for it in s["items"]:
            if it["kind"] == "mischief":
                target = next((t for t in s["items"] if t.get("id") == it["target"]), None)
                if target is None or not target.get("hidden"):
                    problems.append(f"mischief at {it['x']}: its target is missing or not hidden")

    # the chase: when a clean run catches him, from a smooth and a clumsy lift
    closing = RUN - T["roosterRunSpeed"]
    for gap in (T["startGapSmoothLift"], T["startGapClumsyLift"]):
        t = (gap - T["grabDistance"]) / closing
        notes.append(f"a clean run from a {gap:.0f} m start catches him after about {t:.0f} s, at about {RUN * t:.0f} m "
                     f"(without chillies)")
    taught = {"pots": None, "dung": None, "dog": None, "puddle": None, "cart": None}
    for a0, a1, top, kind, name in obstacles:
        if taught[kind] is None:
            taught[kind] = a0
    notes.append("first of each: " + ", ".join(f"{k} {v:.0f} m" for k, v in taught.items()))
    for a0, a1, kind, name, held, tap in windows:
        if held:
            notes.append(f"{kind:6s} {a0:6.1f} m ({name}): held window {(held[1] - held[0]) / RUN * 1000:.0f} ms"
                         + (f", tap {(tap[1] - tap[0]) / RUN * 1000:.0f} ms" if tap else ", a tap cannot clear it"))
    return problems, notes, obstacles


REPORT = ROOT / "docs" / "levels" / "level1.md"


def report(p, notes, problems):
    """The beat sheet: docs/levels/level1.md, written from the same plan the game is built from."""
    def what(s):
        out, mangoes = [], 0
        for it in s["items"]:
            k = it["kind"]
            if k == "mango":
                mangoes += 1
            elif k in ("pots", "dung", "dog", "puddle", "cart"):
                name = {"pots": "pot stack", "dung": "cow dung", "dog": "sleeping dog", "puddle": "hand-pump puddle",
                        "cart": "bullock cart"}[k]
                out.append(f"{name} {it['x']:g}" + (" (knocked in by the rooster)" if it.get("hidden") else ""))
            elif k == "chilli":
                out.append(f"chilli {it['x']:g}")
            elif k == "feather":
                out.append(f"feather {it['index'] + 1} at {it['x']:g}, {it['y']:g} m up")
            elif k == "mischief":
                out.append(f"mischief {it['x']:g}")
            elif k == "basket":
                out.append(f"the basket {it['x']:g}")
            elif k == "neighbour":
                out.append(f"the neighbour {it['x']:g}")
        if mangoes:
            out.append(f"{mangoes} mangoes")
        return "; ".join(out)

    lines = [
        "# Level 1: Pots and the sleeping dog",
        "",
        "The beat sheet for zone 1's first level. It is written by `ArtSource/tools/levels/level1.py --report` from the",
        "same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level1.json`), so it cannot drift from it.",
        "Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths and",
        "tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.",
        "",
        "## The opening: the neighbour's yard",
        "",
        "The neighbour naps on his rope cot behind the lane; his hens peck about. The kid tiptoes in from "
        f"{p.sections[0]['items'][0]['walkFrom']:g} m to the bamboo basket the rooster is sitting under (a tap hurries her). "
        "The player holds to lift it by its near rim; it turns up on its far rim over 1.6 s of holding. Letting go part "
        "way drops it back with a clunk, and the neighbour stirs. Fully up, the rooster bursts out and sprints off, the kid "
        "flings the basket aside, and the neighbour wakes shouting.",
        "",
        f"* A lift with no drop gives the rooster a **{T['startGapSmoothLift']:g} m** head start; any drop gives him "
        f"**{T['startGapClumsyLift']:g} m**.",
        "* A retry skips the opening and keeps the head start it earned; loading the level again plays it again.",
        "* The rules are `Core/BasketLift.cs` (tested in `BasketLiftTests`); the flow is `GameFlow`'s Intro state; the "
        "basket, its hinge and the neighbour's two cut-outs are `BasketIntro`.",
        "",
        "## The course",
        "",
        "Teach (to about 140 m): one new thing at a time, each first on its own with room around it, the rooster hopping",
        "it first to show the way and mangoes tracing the jump. Practise (to 300 m): the same things in pairs and rhythms.",
        "Test (to 500 m): the rooster's mischief, trios, the last cart, then the lane opens out.",
        "",
        "| From | To | Section | What is there | Why |",
        "|---:|---:|---|---|---|",
    ]
    for s in p.sections:
        lines.append(f"| {s['x']:g} | {s['x'] + s['length']:g} | {s['name']} | {what(s)} | {s['note']} |")
    lines += ["", "## The audit", ""]
    lines += [f"* {n}" for n in notes if not n.startswith(("pots ", "dung ", "dog ", "puddle"))]
    lines += ["", "Take-off windows (how long the player has to start a jump that clears each obstacle):", ""]
    lines += ["```"] + [n for n in notes if n.startswith(("pots ", "dung ", "dog ", "puddle"))] + ["```", ""]
    lines.append("Problems: " + ("none." if not problems else ""))
    lines += [f"* {pr}" for pr in problems]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT.relative_to(ROOT)}")


def main():
    p = design()
    course = T["courseLength"]
    problems, notes, obstacles = audit(p, course)
    data = {
        "level": 1, "zone": 1, "title": "Pots and the sleeping dog", "subtitle": "Tap to jump. Hold for higher.",
        "courseLength": course, "startGapSmooth": T["startGapSmoothLift"], "startGapClumsy": T["startGapClumsyLift"],
        "jumpLength": round(JUMP_LEN, 3),
        "sections": p.sections,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    counts = {}
    for s in p.sections:
        for it in s["items"]:
            counts[it["kind"]] = counts.get(it["kind"], 0) + 1
    print(f"wrote {OUT.relative_to(ROOT)}: {len(p.sections)} sections, {data['sections'][-1]['x'] + data['sections'][-1]['length']:.0f} m,",
          ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    print(f"jump: {JUMP_LEN:.2f} m held, {RUN * TAP[-1][0]:.2f} m tapped; gravity {G:.1f}")
    for n in notes:
        print("  " + n)
    if "--report" in sys.argv:
        report(p, notes, problems)
    if problems:
        print("PROBLEMS:")
        for pr in problems:
            print("  - " + pr)
        sys.exit(1)
    print("audit: no problems")
    return p, notes


if __name__ == "__main__":
    main()
