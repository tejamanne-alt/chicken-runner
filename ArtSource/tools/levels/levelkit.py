"""The shared half of the level plans (level1.py, level4.py, level7.py): the game's rules read from its C#, the pieces
placed exactly as GameBuilder.Kit places them, the audit and the report.

A level script builds a Plan section by section and hands it to `run()`, which audits it, writes
Assets/ChickenRunner/Art/Levels/levelN.json and, with --report, docs/levels/levelN.md. Three things read the JSON:
  * GameBuilder.Plans (Unity) builds one chunk prefab per section, in order, with the same Kit calls the other levels use;
  * ArtSource/tools/levels/render_level.py draws it as the game camera sees it, from the resolved visuals;
  * the audit here, with the game's jump maths (JumpMath.cs), tuning (ChaseTuning.cs, zone by zone) and kid body
    (KidController.cs) read from the C#.

Coordinates are the course's, in metres: x along the lane from where the kid starts the chase (0), y up, z into the
picture (the lane is z = 0, the camera looks from z = -16; behind the lane is z > 0).
"""
import json
import math
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
LEVELS = ROOT / "Assets" / "ChickenRunner" / "Art" / "Levels"
DOCS = ROOT / "docs" / "levels"
MODELS = {m["name"]: m for m in json.loads((ROOT / "Assets/ChickenRunner/Art/Models/models.json").read_text())["models"]}
CUT = ROOT / "ArtSource" / "cutouts"
MANIFEST = json.loads((CUT / "lane" / "manifest.json").read_text())

SCRIPTS = ROOT / "Assets" / "ChickenRunner" / "Scripts"
_KID = (SCRIPTS / "Gameplay/Kid/KidController.cs").read_text()
_KIT = (SCRIPTS / "Editor/GameBuilder.Kit.cs").read_text()


def _const(src, name):
    return float(re.search(rf"\b{name}\s*=\s*([-\d.]+)f", src).group(1))


KID_R = _const(_KID, "radius")                      # KidController.radius
RAY_INSET = _const(_KID, "GroundRayInset")          # its ground rays sit this share of the radius either side
STEP = _const(_KID, "stepHeight")                   # ledges up to this are stepped onto
ROOF = _const(_KIT, "Roof")                         # GameBuilder.Roof: every roof row's top
CANAL_BED = _const(_KIT, "CanalBed")                # a canal's bed, below the banks
SLIDE_HEIGHT = _const(_KID, "slideHeight")


# ------------------------------------------------------------------ the game's numbers, read from its C#
def tuning(zone):
    """ChaseTuning's defaults with ChaseTuning.ForZone(zone)'s overrides, as the zone's TuningConfig asset starts."""
    src = (SCRIPTS / "Core/ChaseTuning.cs").read_text()
    t = {m.group(1): float(m.group(2)) for m in re.finditer(r"public float (\w+) = ([-\d.]+)f;", src)}
    t.update({m.group(1): int(m.group(2)) for m in re.finditer(r"public int (\w+) = (-?\d+);", src)})
    block = re.search(rf"case {zone}:(.*?)break;", src, re.S)
    if block:
        for m in re.finditer(r"t\.(\w+) = ([-\d.]+)f;", block.group(1)):
            t[m.group(1)] = float(m.group(2))
    return t


class Rules:
    """A zone's jump: gravity, launch speeds and the flight of the feet, as KidController flies it."""

    def __init__(self, zone):
        self.zone = zone
        T = self.T = tuning(zone)
        self.G = 8 * T["jumpHeight"] * T["jumpReferenceSpeed"] ** 2 / T["jumpLength"] ** 2       # JumpMath.Gravity
        self.V0 = math.sqrt(2 * self.G * T["jumpHeight"])                                         # JumpVelocity
        self.V2 = math.sqrt(2 * self.G * max(0.0, T["doubleJumpTotalHeight"] - T["jumpHeight"]))  # DoubleJumpVelocity
        self.LOW = max(1.0, T["jumpHeight"] / T["tapJumpHeight"])                                 # LowJumpGravityMultiplier
        self.RUN = T["kidRunSpeed"]
        self.JUMP_LEN = self.RUN * 2 * self.V0 / self.G                                           # JumpLengthAt
        self.HELD = self.flight(True)
        self.TAP = self.flight(False)
        self.DOUBLE = self.flight(True, double=True)
        self.BOOST = self.RUN * (1 + T["boostSpeedBonus"]) * T["boostDuration"]
        self.REACT = 0.3 * self.RUN

    def flight(self, held=True, double=False, dt=1 / 240, floor=0.0):
        """(t, height of the feet) through a jump from flat ground, held or tapped, with a double jump at the top if
        `double`, until the feet come back down to `floor`."""
        out, t, h, v, used = [], 0.0, 0.0, self.V0, False
        while True:
            g = self.G if (held or v <= 0) else self.G * self.LOW
            v -= g * dt
            if double and not used and v <= 0:
                v, used = self.V2, True
            h += v * dt
            t += dt
            if h <= floor and v < 0:
                out.append((t, floor))
                return out
            out.append((t, h))

    def length(self, path):
        return self.RUN * path[-1][0]

    def takeoff_window(self, span, top, path):
        """The take-off x (relative to the span's start) from which a jump on `path` keeps the feet above `top` over
        the whole span (widened by the kid's radius on both sides): (earliest, latest), or None."""
        a0, a1 = -KID_R, span + KID_R
        above = [self.RUN * t for t, h in path if h > top]
        if not above:
            return None
        lo, hi = above[0], above[-1]
        if hi - lo < a1 - a0:
            return None
        return a1 - hi, a0 - lo

    def onto_window(self, span, top, path, dt=1 / 240):
        """Take-off x (relative to the near face of a body `span` long and `top` high: the buffalo) from which a jump
        on `path` lands on its top, as KidController does it: her front must meet the face with the feet already above
        top - STEP (lower, the face is a wall), and her feet come down to `top` over the body, before its far end.
        Returns (earliest, latest), or None; the take-offs between them all work."""
        ok = []
        d = -4.0
        while d <= 0.0:
            # does her front reach the face while her feet are too low?
            blocked = False
            for t, h in path:
                front = d + self.RUN * t + KID_R
                if front >= 0.0:
                    blocked = h < top - STEP
                    break
            lands = None
            if not blocked:
                prev = path[0]
                for t, h in path[1:]:
                    if h < prev[1] and prev[1] >= top > h:          # coming down through the top
                        lands = d + self.RUN * t
                        break
                    prev = (t, h)
            if not blocked and lands is not None and 0.0 <= lands <= span:
                ok.append(d)
            d += 0.005
        if not ok:
            return None
        return ok[0], ok[-1]

    def gap_window(self, width, path):
        """Take-off x (relative to the near edge) that lands on the far side of a gap `width` wide: the kid stays up
        until her back ground ray leaves the near edge, and lands once her front ray is over the far one."""
        inset = KID_R * RAY_INSET
        latest = inset
        earliest = width - inset - self.length(path)
        return (earliest, latest) if earliest <= latest else None

    def fall_time(self, height):
        return math.sqrt(2 * height / self.G)

    def bounce_length(self, height, from_y=0.0):
        """How far she travels from a bounce `height` m high (JumpMath.BounceVelocity), launched `from_y` up, until she is
        back on the lane."""
        v = math.sqrt(2 * self.G * height)
        return self.RUN * (v / self.G + math.sqrt(2 * (from_y + height) / self.G))


# ------------------------------------------------------------------ the pieces, placed as GameBuilder.Kit places them
def aspect(piece):
    m = MODELS.get(piece)
    if m:
        return m["width"] / m["height"]
    return card_aspect(piece)


def card_aspect(piece):
    """A cut-out's width over height as ArtAssets.SizeOf takes it: the manifest's pixels, else the picture's."""
    e = MANIFEST.get(piece)
    if isinstance(e, dict) and e.get("px"):
        return e["px"][0] / e["px"][1]
    from PIL import Image
    for p in CUT.rglob(piece + ".png"):
        w, h = Image.open(p).size
        return w / h
    return 1.0


def real_size(piece, fallback_height=1.0):
    """A cut-out's real (width, height) as ArtAssets.SizeOf takes it: pixels per metre, else its height or width in
    metres from the manifest, else `fallback_height`, keeping the picture's proportions."""
    e = MANIFEST.get(piece)
    a = card_aspect(piece)
    if isinstance(e, dict):
        if e.get("px_per_m") and e.get("px"):
            return e["px"][0] / e["px_per_m"], e["px"][1] / e["px_per_m"]
        if e.get("height_m"):
            return e["height_m"] * a, e["height_m"]
        if e.get("width_m"):
            return e["width_m"], e["width_m"] / a
    return fallback_height * a, fallback_height


def real_width(piece):
    """A piece's real width (m): its model's, else the manifest's."""
    m = MODELS.get(piece)
    if m:
        return m["width"]
    e = MANIFEST.get(piece)
    return e.get("width_m", 0.4) if isinstance(e, dict) else 0.4


def lies_flat(piece):
    """Whether Kit.Decal lays the piece face up (a slab model, or a card with no model) or stands it up (a volume
    model: a tuft, pebbles, a husk), as ArtModels.LiesFlat decides."""
    m = MODELS.get(piece)
    return m is None or m["kind"] == "slab"


def visual(piece, x, y=0.0, z=0.0, h=0.0, w=0.0, mirror=False, flat=False, turn=0.0, kind="art"):
    a = aspect(piece)
    if h:
        w = h * a
    elif w:
        h = w / a
    return {"piece": piece, "x": round(x, 3), "y": round(y, 3), "z": round(z, 3), "w": round(w, 3), "h": round(h, 3),
            "mirror": mirror, "flat": flat, "turn": round(turn, 1), "kind": kind}


def box(piece, x, y, z, w, h, d, color):
    """A solid drawn as a box (a roof's wall, a plank): x its centre, y its bottom."""
    return {"piece": piece, "x": round(x, 3), "y": round(y, 3), "z": round(z, 3), "w": round(w, 3), "h": round(h, 3),
            "d": round(d, 3), "color": [round(c, 3) for c in color], "mirror": False, "flat": False, "turn": 0,
            "kind": "box"}


WOOD = (0.6, 0.38, 0.2)
BAMBOO = (0.78, 0.66, 0.38)
WALLS = [(0.93, 0.86, 0.6), (0.45, 0.6, 0.85), (0.92, 0.65, 0.7), (0.95, 0.95, 0.9)]
LITTER = {
    1: ["leaf_1", "leaf_2", "twigs", "husk", "footprints", "hen_prints", "pebbles", "tuft_1", "tuft_2", "tuft_3"],
    2: ["tuft_1", "tuft_2", "tuft_3", "tuft_4", "weed_1", "weed_2", "hoof_prints", "pebbles", "husk", "leaf_3"],
    3: ["leaf_1", "leaf_2", "twigs", "husk", "footprints", "hen_prints", "pebbles", "pebble_cluster", "coconut"],
}


class Plan:
    def __init__(self, zone=1, seed=1):
        self.r = Rules(zone)
        self.zone = zone
        self.sections = []
        self.rng = random.Random(seed)
        # the head starts a chase can begin with: levels without the basket start 12 m behind him
        self.start_gaps = [self.r.T["startGapNoBasket"]]

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

    # ---- obstacles, as Kit builds them (trigger sizes, card sizes and z); `y` is the surface they stand on
    def pots(self, s, x, hidden=False, ident="", y=0.0):
        mirror = self.rng.random() < 0.5
        kw = {"y": y} if y else {}
        self.add(s, "pots", x, [visual("pot_stack", x, y, z=0.05, h=0.68, mirror=mirror)], mirror=mirror, hidden=hidden,
                 id=ident, top=0.6, span=0.45, **kw)
        if not hidden:
            self.hop_over(s, x, 0.45, 0.6)
            self.jump_arc(s, x, y)

    def dung(self, s, x):
        self.add(s, "dung", x, [visual("dung", x, z=0.05, w=0.6)], top=0.2, span=0.55)
        self.hop_over(s, x, 0.55, 0.2)
        self.jump_arc(s, x)

    def dog(self, s, x):
        # its curled body (the painting's 0.95 m takes in the tail and paws): what a held jump must clear at 3.5 m/s
        self.add(s, "dog", x, [visual("dog_sleeping", x, z=0.05, w=0.95)], top=0.36, span=0.75)
        self.hop_over(s, x, 0.9, 0.36)
        self.jump_arc(s, x)

    def puddle(self, s, x, width=0.9):
        self.add(s, "puddle", x, [visual("puddle_water", x, 0.004, 0.0, w=width * 1.15, flat=True, kind="decal"),
                                  visual("hand_pump", x - width * 0.3, z=1.35, h=1.2)],
                 width=width, top=0.15, span=width)
        self.hop_over(s, x, width, 0.15)
        self.jump_arc(s, x)

    def cart(self, s, x):
        raise ValueError("no bullock carts parked across the road: a village street keeps its carts at the side "
                         "(use sacks() for something to hop onto)")

    def sacks(self, s, x, rooster_hop=True):
        """Kit.Sacks: sacks of paddy stacked at the roadside for the cart, 1.15 m long and 0.8 m high from x: a platform
        to hop onto (or over), as the cart's bed was. Without `rooster_hop` the level lays the rooster's own route over
        them (as the step to a mango branch, his flutter goes straight on up)."""
        self.add(s, "sacks", x, [visual("jute_sacks", x + 0.575, z=0.05, h=0.8)], bed=0.8, span=1.035)
        if rooster_hop:
            self.hop(s, x - 0.7, 2.6, 1.3)
        self.mango_line(s, x + 0.25, 2, 0.5, 1.35)     # on top of the sacks
        return x + 1.15

    def tank(self, s, x, y=ROOF):
        """Kit.Tank: the black water tank on its stand, on a roof at y: jump it."""
        self.add(s, "tank", x, [visual("black_tank", x, y, z=0.05, h=0.75)], y=y, top=0.65, span=0.45)
        self.hop_over(s, x, 0.55, 0.7)
        self.jump_arc(s, x, y)

    def hens_basket(self, s, x, hidden=False, ident=""):
        """Kit.HensBasket: the hens' basket on the lane, jumped like a pot stack (or knocked into the lane)."""
        self.add(s, "hensbasket", x, [visual("hens_basket", x, z=0.05, h=0.6)], hidden=hidden, id=ident, top=0.5,
                 span=0.6)
        if not hidden:
            self.hop_over(s, x, 0.6, 0.55)
            self.jump_arc(s, x)

    def clothesline(self, s, x, mirror=None):
        raise ValueError("no washing lines strung across the road: use low_branch() for something to slide under")

    def low_branch(self, s, x, mirror=None):
        """Kit.LowBranch: a roadside neem's limb across the street, its leaves hanging from 1.6 m down to 0.75 m over
        1.1 m of the lane (roadside_models.py): slide under, or double jump over. The trunk stands behind the road."""
        if mirror is None:
            mirror = self.rng.random() < 0.5
        self.add(s, "lowbranch", x, [{"piece": "low_branch", "x": round(x, 3), "y": 0.0, "z": 0.0, "w": 3.4,
                                      "h": 4.4, "mirror": mirror, "flat": False, "turn": 0, "kind": "model"}], mirror=mirror,
                 bottom=0.75, top=1.6, span=1.1)
        self.mango_line(s, x - 0.9, 3, 0.7, 0.3)      # low mangoes: the slide's line

    def goats(self, s, x, count=1):
        """Kit.Goats: one or two goat kids wandering across the street, 0.55 m high: jump them (or bump into them)."""
        spacing = 0.34
        width = 0.1 + count * spacing
        vis = [visual("goat_kid", x - width / 2 + 0.05 + spacing / 2 + i * spacing, 0.0, 0.05 + 0.08 * i, h=0.55)
               for i in range(count)]
        self.add(s, "goats", x, vis, count=count, top=0.45, span=round(width, 3))
        self.hop_over(s, x, width, 0.55)
        self.jump_arc(s, x)

    def ducks(self, s, x, count=2):
        """Kit.Ducks: ducks waddling across the bund road between the canals, 0.5 m high: jump them (or scatter them)."""
        spacing = 0.28
        width = 0.1 + count * spacing
        vis = [visual(f"duck_{1 + i % 2}", x - width / 2 + 0.05 + spacing / 2 + i * spacing, 0.0, 0.05 + 0.08 * i, h=0.5)
               for i in range(count)]
        self.add(s, "ducks", x, vis, count=count, top=0.4, span=round(width, 3))
        self.hop_over(s, x, width, 0.45)
        self.jump_arc(s, x)

    def sand(self, s, x):
        """Kit.SandHeap: a heap of river sand tipped at the road's edge for a house being built (roadside_models.py),
        1.24 m across and 0.45 m high: jump it (or flounder into it)."""
        self.add(s, "sand", x, [{"piece": "sand_heap", "x": round(x, 3), "y": 0.0, "z": 0.05, "w": 1.24, "h": 0.45,
                                 "mirror": False, "flat": False, "turn": 0, "kind": "model"}], top=0.4, span=0.7)
        self.hop_over(s, x, 1.0, 0.45)
        self.jump_arc(s, x)

    def canal(self, s, x, width, bridge=False):
        """Kit.Canal: a canal across the lane from x, `width` wide: jump it, wade it, or (with a bridge) cross the
        plank. Kit.Canal adds the rooster's flutter over it itself."""
        vis = [{"piece": "_hole", "x": round(x, 3), "y": 0.0, "z": 0.0, "w": width, "h": 0.0, "d": 0.0, "mirror": False,
                "flat": True, "turn": 0, "kind": "hole"},
               {"piece": "_water", "x": round(x + width / 2, 3), "y": -0.06, "z": -17.75, "w": width, "h": 0.0,
                "d": 44.5, "mirror": False, "flat": True, "turn": 0, "kind": "water"}]
        for edge in (x + 0.12, x + width - 0.12):              # Kit.Canal's stone-lined banks
            vis.append(box("bank", edge, -0.32, -17.75, 0.24, 0.34, 44.5, (0.6, 0.56, 0.52)))
        if bridge:
            vis.append(box("plank", x + width / 2, -0.1, 0.0, width + 0.4, 0.1, 0.9, WOOD))
            for z in (0.45,):                                    # the far handrail only (plank_model.py)
                vis.append(box("rail", x + width / 2, 0.525, z, width + 0.4, 0.05, 0.05, BAMBOO))
                for px in (x - 0.2, x + width + 0.2):
                    vis.append(box("post", px, -0.05, z, 0.06, 0.7, 0.06, BAMBOO))
        hop = (round(x - 0.6, 3), round(width + 1.2, 3), round(0.5 + width * 0.1, 3))
        self.add(s, "canal", x, vis, width=width, bridge=bridge, span=width, implicitHop=list(hop))

    def roofs(self, s, x, fronts, ladder=False):
        """Kit.RoofRow: house fronts side by side from x, their flat roofs one run ROOF up; the first front can carry
        the bamboo ladder. Returns where the row ends, from the same card sizes the Kit reads."""
        card_h = ROOF + 0.15
        widths, vis, cx = [], [], x
        for i, front in enumerate(fronts):
            with_ladder = ladder and i == 0
            piece = "house_turmeric_ladder" if with_ladder else front
            w = card_h * card_aspect(piece)
            widths.append(round(w, 4))
            v = visual(piece, cx + w / 2, 0.0, 0.4, h=card_h, mirror=with_ladder)
            v["w"] = round(w, 3)
            vis.append(v)
            vis.append(box("wall", cx + w / 2, 0.0, 0.0, w, ROOF, 1.2, WALLS[i % len(WALLS)]))
            if with_ladder:
                lean = 0.135 * w / (0.93 * card_h)
                foot = cx + 0.084 * w
                vis.append({"piece": "bamboo_ladder", "x": round(foot, 3), "y": 0.0, "z": -0.05, "w": 0.4,
                            "h": round(ROOF + 0.08, 3), "lean": round(lean, 4), "mirror": False, "flat": False,
                            "turn": 0, "kind": "ladder"})
            cx += w
        end = cx
        fronts_out = ["" if (ladder and i == 0) else f for i, f in enumerate(fronts)]
        self.add(s, "roofs", x, vis, fronts=fronts_out, ladder=ladder, widths=widths, end=round(end, 4),
                 implicitHop=[round(x - 1.6, 3), 2.0, 0.9])
        return end

    def haystack(self, s, x, big=False):
        """Kit.Haystack: a small stack (1.05 m) to hop onto or over, a big one (1.85 m) to double jump. Returns its
        end. The Kit picks its mirror at random; the plan lets it."""
        height = 2.0 if big else 1.25
        top = 1.85 if big else 1.05
        piece = "haystack" if big else "haystack_small"
        w = height * card_aspect(piece)
        length = w + 1.6
        edge = math.sin(math.pi * (0.8 + w * 0.1) / length)
        hop = (round(x - 0.8, 3), round(length, 3), round((top + 0.25) / max(0.3, edge), 3))   # as Kit.Haystack
        self.add(s, "haystack", x, [visual(piece, x + w / 2, 0.0, 0.15, h=height)], big=big, top=top,
                 span=round(w * 0.8, 4), width=round(w, 4), implicitHop=list(hop))
        return x + w

    def cot(self, s, x, onto_roof=False):
        """Kit.Cot: a rope cot 1.9 m long from x, a trampoline: run into it or land on it for a 2.4 m bounce. The
        rooster bounces off it too, and mangoes trace the bounce; with `onto_roof` (a roof row starting about 1 m after
        it), they rise onto the roof instead of coming back down into its wall."""
        self.add(s, "cot", x, [visual("rope_cot", x + 0.95, 0.0, 0.05, w=1.9)], span=1.9)
        self.hop(s, x, 4.8, 2.2)
        if onto_roof:
            for dx, y in ((0.5, 1.5), (1.3, 2.5), (2.1, 3.1)):
                self.mango(s, x + dx, y)
        else:
            self.arc(s, x - 0.1, 4.8, 2.4, 6)

    def mango_tree(self, s, x):
        """Kit.MangoTree: a mango tree behind the lane, its branch over it from x+1 to x+5, 2.3 m up: jump at it to
        pull up onto it, or run on underneath. The Kit lays the mangoes along the branch and the rooster's flutter up
        onto it; this plan adds his flutter down off its end."""
        vis = [visual("tree_mango_1", x + 3.0, 0.0, 0.9, h=5.2), box("branch", x + 3.0, 2.14, 0.0, 4.0, 0.16, 0.8, WOOD)]
        vis += [visual("Mango", x + 1.4 + i * 0.6, 2.85, kind="pickup", h=0.28) for i in range(6)]
        self.add(s, "mangotree", x, vis, branch=[round(x + 1.0, 3), round(x + 5.0, 3), 2.3],
                 implicitHop=[round(x + 0.2, 3), 1.0, 0.5])
        self.hop_down(s, x + 5.0)

    def buffalo(self, s, x):
        """Kit.Buffalo: a buffalo wallowing across the lane from x, its back 1.1 m up: jump onto it for a 2.6 m bounce,
        or climb over it slowly. Returns where it ends."""
        w = 1.5 * card_aspect("buffalo_mud")
        vis = [visual("buffalo_mud", x + w / 2, 0.0, 0.15, h=1.5),
               visual("cracked_mud", x + w / 2, 0.0, 0.0, w=1.8, flat=True, kind="decal")]
        self.add(s, "buffalo", x, vis, width=round(w, 4), top=1.1, span=round(w * 0.7, 4),
                 implicitHop=[round(x - 1.0, 3), round(w + 2.0, 3), 1.6])
        return x + w

    def stall(self, s, x, piece):
        """Kit.Stall: a market stall on the lane's far edge from x, at its real size: run under its awning, or jump into
        the awning (about 2.1 m up) for a 2 m bounce from roof to roof. Returns where it ends."""
        w, h = real_size(piece)
        self.add(s, "stall", x, [visual(piece, x + w / 2, 0.0, 0.55, h=h)], piece=piece, width=round(w, 4),
                 height=round(h, 4))
        return x + w

    def hens(self, s, x, count):
        """Kit.Hens: one or two hens pecking across the lane, jumped like a pot stack (or scattered: a stumble). Three
        abreast is more than a small child clears in one jump."""
        spacing = 0.3
        width = 0.1 + count * spacing
        vis = [visual(f"hen_{1 + i % 3}", x - width / 2 + 0.05 + spacing / 2 + i * spacing, 0.0, 0.05 + 0.08 * i, h=0.42)
               for i in range(count)]
        self.add(s, "hens", x, vis, count=count, top=0.4, span=round(width, 3))
        self.hop_over(s, x, width, 0.45)
        self.jump_arc(s, x)

    def steps(self, s, x, count, landing):
        """Kit.Steps: temple steps from x, `count` of them up (0.25 m each, low enough to walk up), a landing, the same
        steps down; the landing's lamps behind. Returns where they end."""
        rise, tread = 0.25, 0.7
        end = x + count * tread * 2 + landing
        vis = []
        for i in range(count):
            a, b = x + i * tread, end - i * tread
            vis.append(box("step", (a + b) / 2, i * rise, 0.6, b - a, rise, 1.8, (0.62, 0.58, 0.55)))
        top = count * rise
        for k in range(2):
            vis.append(visual("lamp_step", x + count * tread + landing * (0.25 + 0.5 * k), top, 1.2, h=1.9))
        vis.append(visual("lantern", x + count * tread + landing * 0.5, top, 0.9, h=0.45))
        self.add(s, "steps", x, vis, count=count, landing=landing, end=round(end, 4), top=top)
        return end

    # ---- the rooster's route
    def hop(self, s, x, length, height):
        self.add(s, "hop", x, length=length, height=height)

    def hop_over(self, s, centre, span, top, run_up=0.6):
        """The rooster's hop over an obstacle: from run_up before it to run_up after, its arc 0.25 m clear of the
        obstacle's top even at its edges (his hop's height is a sine over its length, on top of the surface)."""
        length = span + 2 * run_up
        height = (top + 0.25) / math.sin(math.pi * run_up / length)
        self.hop(s, centre - span / 2 - run_up, length, round(height, 2))

    def hop_gap(self, s, row_end, next_start, height=0.7):
        """Across the gap between two roof rows, roof to roof (his hop lerps from the roof he leaves to the one ahead)."""
        self.hop(s, row_end - 0.4, next_start - row_end + 0.8, height)

    def hop_down(self, s, row_end):
        """Off the end of a roof row, a flutter down to the lane."""
        self.hop(s, row_end - 0.3, 2.0, 0.45)

    def mischief(self, s, x, target):
        self.add(s, "mischief", x, target=target)

    # ---- pickups
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
        self.arc(s, centre - self.r.JUMP_LEN / 2, self.r.JUMP_LEN, self.r.T["jumpHeight"], 5, lift)

    def chilli(self, s, x, y=0.6):
        self.add(s, "chilli", x, [visual("Chilli", x, y, kind="pickup", h=0.3)], y=y)

    def feather(self, s, x, y, index):
        self.add(s, "feather", x, [visual("Feather", x, y, kind="pickup", h=0.35)], y=y, index=index)

    # ---- set dressing: a prop behind or in front of the lane, a mark on the ground
    def prop(self, s, piece, x, z, h=0.0, w=0.0, mirror=False, y=0.0):
        self.add(s, "prop", x, [visual(piece, x, y, z, h=h, w=w, mirror=mirror)], piece=piece, z=z, h=h, w=w, mirror=mirror,
                 y=y)

    def decal(self, s, piece, x, z, w):
        """A ground detail: a flat one at any turn, a standing one (a tuft, a husk) turned at most 20 degrees from
        facing the camera, so it never shows its back."""
        turn = self.rng.uniform(0, 360)
        flat = lies_flat(piece)
        if not flat:
            turn = turn % 40 - 20
        self.add(s, "decal", x, [visual(piece, x, 0.0, z, w=w, flat=flat, turn=turn, kind="decal")], piece=piece, z=z,
                 w=w, turn=round(turn, 1))

    def litter(self, s, count, avoid=(), holes=()):
        """Stray ground details along a section, never on the running line next to an obstacle (where a mark could
        be read as one) and never over a canal or under a roof row (`holes`: (from, to) spans)."""
        pieces = LITTER.get(self.zone, LITTER[1])
        x0, x1 = s["x"], s["x"] + s["length"]
        placed, tries = 0, 0
        while placed < count and tries < 500:
            tries += 1
            x = self.rng.uniform(x0 + 0.5, x1 - 0.5)
            z = self.rng.uniform(-1.6, 1.6)
            piece = self.rng.choice(pieces)
            # A standing piece (a tuft, a husk) reads as an obstacle on the running line: keep it off it.
            if not lies_flat(piece) and abs(z) < 0.9:
                continue
            if abs(z) < 0.7 and any(abs(x - a) < 1.6 for a in avoid):
                continue
            if any(a - 0.6 <= x <= b + 0.6 for a, b in holes):
                continue
            self.decal(s, piece, x, z, real_width(piece) * self.rng.uniform(0.85, 1.2))
            placed += 1

    # ---- what the plan makes of the ground
    def items(self, kind=None):
        for s in self.sections:
            for it in s["items"]:
                if kind is None or it["kind"] == kind:
                    yield s, it

    def surfaces(self):
        """Solid tops along the lane, (from, to, top): roof rows, cart beds, haystacks."""
        out = []
        for _, it in self.items():
            if it["kind"] == "roofs":
                out.append((it["x"], it["end"], ROOF))
            elif it["kind"] in ("cart", "sacks"):
                out.append((it["x"], it["x"] + it["span"], it["bed"]))
            elif it["kind"] == "haystack":
                c = it["x"] + it["width"] / 2
                out.append((c - it["span"] / 2, c + it["span"] / 2, it["top"]))
            elif it["kind"] == "mangotree":
                a, b, top = it["branch"]
                out.append((a, b, top))
            elif it["kind"] == "buffalo":
                c = it["x"] + it["width"] / 2
                out.append((c - it["span"] / 2, c + it["span"] / 2, it["top"]))
            elif it["kind"] == "steps":
                tread, rise = 0.7, 0.25
                for i in range(it["count"]):
                    out.append((it["x"] + i * tread, it["end"] - i * tread, (i + 1) * rise))
        return out

    def holes(self):
        return [(it["x"], it["x"] + it["width"]) for _, it in self.items("canal")]

    def ground_at(self, x):
        """What GroundAt finds under x: the highest solid top, a canal's bed, or the lane."""
        tops = [t for a, b, t in self.surfaces() if a <= x <= b]
        if tops:
            return max(tops)
        if any(a < x < b for a, b in self.holes()):
            return CANAL_BED
        return 0.0

    def hops(self):
        """Every rooster hop, authored and implied by a Kit piece: (start, end, height)."""
        out = []
        for _, it in self.items():
            if it["kind"] == "hop":
                out.append((it["x"], it["x"] + it["length"], it["height"]))
            elif "implicitHop" in it:
                a, n, h = it["implicitHop"]
                out.append((a, a + n, h))
        return sorted(out)

    def rooster_y(self, hop, x):
        """The rooster's height at x inside `hop`, as RoosterBrain.FollowRoute flies it."""
        a, b, h = hop
        k = (x - a) / (b - a)
        y0, y1 = self.ground_at(a), self.ground_at(b + 0.05)
        return y0 + (y1 - y0) * k + h * math.sin(math.pi * k)


# ------------------------------------------------------------------ the audit
def challenges(p):
    """Everything the kid has to get past, in order: (x0, x1, base, kind, section, item)."""
    out = []
    for s, it in p.items():
        k = it["kind"]
        base = it.get("y", 0.0) if k in ("pots", "tank") else 0.0
        if k in ("pots", "dung", "dog", "puddle", "tank", "hensbasket", "clothesline", "hens", "goats", "ducks", "sand",
                 "lowbranch"):
            # a hidden one (the rooster's mischief) counts too: it can be there when the kid arrives
            out.append((it["x"] - it["span"] / 2, it["x"] + it["span"] / 2, base, k, s["name"], it))
        elif k in ("cart", "sacks"):
            out.append((it["x"], it["x"] + it["span"], 0.0, k, s["name"], it))
        elif k == "canal":
            out.append((it["x"], it["x"] + it["width"], 0.0, "bridge" if it["bridge"] else "canal", s["name"], it))
        elif k == "haystack":
            c = it["x"] + it["width"] / 2
            out.append((c - it["span"] / 2, c + it["span"] / 2, 0.0, k, s["name"], it))
        elif k == "roofs":
            out.append((it["x"], it["end"], ROOF, "roofs", s["name"], it))
        elif k == "cot":
            out.append((it["x"], it["x"] + it["span"], 0.0, "cot", s["name"], it))
        elif k == "buffalo":
            c = it["x"] + it["width"] / 2
            out.append((c - it["span"] / 2, c + it["span"] / 2, 0.0, "buffalo", s["name"], it))
        elif k == "mangotree":
            out.append((it["branch"][0], it["branch"][1], 0.0, "branch", s["name"], it))
        elif k == "steps":
            out.append((it["x"], it["end"], 0.0, "steps", s["name"], it))
    # a row of stalls side by side is one stretch of awnings
    stalls = sorted((it for _, it in p.items("stall")), key=lambda it: it["x"])
    run = []
    for it in stalls + [None]:
        if run and (it is None or it["x"] - (run[-1]["x"] + run[-1]["width"]) > 1.0):
            name = next(s["name"] for s, i2 in p.items("stall") if i2 is run[0])
            out.append((run[0]["x"], run[-1]["x"] + run[-1]["width"], 0.0, "awnings", name, {"stalls": run}))
            run = []
        if it is not None:
            run.append(it)
    return sorted(out, key=lambda c: c[0])


def audit(p, course_length, require_feathers=True):
    r, T = p.r, p.r.T
    problems, notes = [], []
    secs = p.sections
    for a, b in zip(secs, secs[1:]):
        if abs(a["x"] + a["length"] - b["x"]) > 1e-6:
            problems.append(f"sections {a['name']} and {b['name']} do not meet")
    end = secs[-1]["x"] + secs[-1]["length"]
    if end < course_length:
        problems.append(f"the course ends at {end} m, before its length {course_length} m")

    for s, it in p.items():
        x0, x1 = s["x"], s["x"] + s["length"]
        if not (x0 <= it["x"] < x1):
            problems.append(f"{it['kind']} at {it['x']} lies outside its section {s['name']} [{x0}, {x1})")
    for x0, x1, base, kind, name, it in challenges(p):
        s = next(s for s in secs if s["name"] == name)
        if x0 < s["x"] - 1e-6 or x1 > s["x"] + s["length"] + 1e-6:
            problems.append(f"{kind} at {x0:.1f} crosses the edge of section {name}")

    # ---- each challenge: how it is cleared, its window, where the kid is settled after it at the latest
    rows = []
    for x0, x1, base, kind, name, it in challenges(p):
        span, info, latest, land = x1 - x0, "", x0, x1
        if kind in ("pots", "dung", "dog", "puddle", "tank", "hensbasket", "hens", "goats", "ducks", "sand"):
            held = r.takeoff_window(span, it["top"], r.HELD)
            tap = r.takeoff_window(span, it["top"], r.TAP)
            if held is None or (held[1] - held[0]) / r.RUN < 0.2:
                problems.append(f"{kind} at {x0:.1f} ({name}): a held jump has under 0.2 s to clear it")
                held = held or (0.0, 0.0)
            info = (f"held window {(held[1] - held[0]) / r.RUN * 1000:.0f} ms"
                    + (f", tap {(tap[1] - tap[0]) / r.RUN * 1000:.0f} ms" if tap else ", a tap cannot clear it"))
            latest, land = x0 + held[1], x0 + held[1] + r.JUMP_LEN
        elif kind in ("clothesline", "lowbranch"):
            if SLIDE_HEIGHT >= it["bottom"] - 0.05:
                problems.append(f"{kind} at {x0:.1f}: the slide ({SLIDE_HEIGHT} m) does not fit under it")
            dbl = r.takeoff_window(span, it["top"], r.DOUBLE)
            slide_len = r.RUN * T["slideDuration"]
            if slide_len < span + 2 * KID_R + 0.6 * r.RUN / 6.0:
                problems.append(f"{kind} at {x0:.1f}: a slide ({slide_len:.1f} m) barely spans it")
            info = (f"slide window {(slide_len - span - 2 * KID_R) / r.RUN * 1000:.0f} ms"
                    + (f", double jump over {(dbl[1] - dbl[0]) / r.RUN * 1000:.0f} ms" if dbl else ", no double jump over"))
            latest, land = x0 - KID_R, x1 + KID_R
        elif kind in ("canal", "bridge"):
            w = it["width"]
            held = r.gap_window(w, r.HELD)
            dbl = r.gap_window(w, r.DOUBLE)
            wade = w * (1 / T["wadeSpeedFactor"] - 1)
            if kind == "bridge":
                info = f"a {w:g} m canal with the plank: run across (a held jump {'clears it' if held else 'falls short'})"
                latest, land = x1, x1
            else:
                if held is None and dbl is None:
                    problems.append(f"canal at {x0:.1f} ({w} m): not even a double jump clears it")
                hw = (held[1] - held[0]) / r.RUN * 1000 if held else 0
                dw = (dbl[1] - dbl[0]) / r.RUN * 1000 if dbl else 0
                if held is None and dw < 250:
                    problems.append(f"canal at {x0:.1f} ({w} m): a double jump has only {dw:.0f} ms")
                if held is not None and hw < 150:
                    notes.append(f"canal at {x0:.1f} ({w} m): a held jump is a gamble ({hw:.0f} ms); the double jump is the way")
                info = (f"{w:g} m: held jump {hw:.0f} ms" if held else f"{w:g} m: needs a double jump")
                info += f", double jump {dw:.0f} ms; wading loses {wade:.1f} m"
                best = held if held and hw >= 150 else dbl
                latest = x0 + best[1]
                path = r.HELD if best is held else r.DOUBLE
                land = latest + r.length(path)
        elif kind in ("cart", "sacks"):
            info = "hop onto the sacks and run off the end" if kind == "sacks" else "jump onto the bed and run off the end"
            land = x1
        elif kind == "haystack":
            reach = T["jumpHeight"] if not it["big"] else T["doubleJumpTotalHeight"]
            if reach < it["top"] + 0.15:
                problems.append(f"haystack at {x0:.1f}: a {'double ' if it['big'] else ''}jump only reaches {reach} m")
            over = r.takeoff_window(span, it["top"], r.DOUBLE if it["big"] else r.HELD)
            info = (f"{'big' if it['big'] else 'small'}: hop onto it or over it"
                    + (f" (over: {(over[1] - over[0]) / r.RUN * 1000:.0f} ms)" if over else ""))
            land = x1 + 0.5
        elif kind == "cot":
            land = x0 + 0.95 + r.bounce_length(T["cotBounceHeight"], 0.5)
            info = f"a trampoline: run into it (no input) for a {T['cotBounceHeight']:g} m bounce, landing about {land - x0:.1f} m on"
        elif kind == "buffalo":
            # onto its back: take-offs whose feet clear its face (above top - step) and come down over the back
            win = r.onto_window(span, it["top"], r.HELD)
            if win is None or (win[1] - win[0]) / r.RUN < 0.2:
                problems.append(f"buffalo at {x0:.1f}: a held jump has under 0.2 s to get onto its back")
                win = win or (0.0, 0.0)
            latest = x0 + win[1]
            land = x0 + 0.3 + r.bounce_length(2.6, it["top"] + 0.1)
            info = (f"jump onto its back ({(win[1] - win[0]) / r.RUN * 1000:.0f} ms) for a 2.6 m bounce, landing about "
                    f"{land - x0:.1f} m on; or a slow climb over")
        elif kind == "branch":
            latest, land = x1, x1 + r.RUN * r.fall_time(it["branch"][2])
            info = "optional: jump at the branch to pull up onto it (mangoes along it), or run on under it"
        elif kind == "awnings":
            latest, land = x1, x1 + r.RUN * r.fall_time(2.1 + 2.0)
            info = f"{len(it['stalls'])} stalls: run under, or jump into an awning and bounce along them (optional)"
        elif kind == "steps":
            latest, land = x0, x0
            info = f"{it['count']} steps up (walked), a {it['landing']:g} m landing {it['top']:g} m up, and down"
        elif kind == "roofs":
            continue                          # a roof row is its events below: getting up, then a gap or a drop
        rows.append([x0, x1, base, kind, name, it, latest, land, info])

    # ---- roof rows: up onto each (the ladder, or the jump across from the row before), then a gap or the drop
    roofs = sorted((it for _, it in p.items("roofs")), key=lambda it: it["x"])
    if roofs and T["doubleJumpTotalHeight"] < ROOF + 0.15:
        problems.append(f"a double jump ({T['doubleJumpTotalHeight']} m) cannot reach the roofs ({ROOF} m)")
    hops = p.hops()
    for i, it in enumerate(roofs):
        x0, x1 = it["x"], it["end"]
        name = next(s["name"] for s, i2 in p.items("roofs") if i2 is it)
        prev = roofs[i - 1] if i > 0 else None
        nxt = roofs[i + 1] if i + 1 < len(roofs) else None
        from_gap = prev is not None and x0 - prev["end"] < 6.0
        # or bounced up onto from a rope cot just before it (the bounce tops 2.9 m)
        from_gap = from_gap or any(x0 - 6.0 <= c["x"] + c["span"] <= x0 for _, c in p.items("cot"))
        if it["ladder"]:
            w = it["widths"][0]
            head = x0 + 0.084 * w + 0.135 * w / (0.93 * (ROOF + 0.15)) * (ROOF + 0.08) + 0.3
            rows.append([x0, x0, 0.0, "ladder", name, it, x0, head,
                         f"up the ladder (no input: she climbs in {T['ladderClimbDuration']:g} s), onto the roof at {head:.1f}"])
        elif not from_gap:
            problems.append(f"roofs at {x0:.1f}: no ladder and no row before it to jump across from")
        for o in rows:
            if o[3] in ("tank", "pots") and o[2] == ROOF and x0 <= o[0] <= x1:
                if o[0] - x0 < (3.0 if it["ladder"] else 2.5) or x1 - o[1] < 1.5:
                    problems.append(f"{o[3]} at {o[0]:.1f}: too near the end of its roof row [{x0:.1f}, {x1:.1f}]")
        if nxt is not None and nxt["x"] - x1 < 6.0:
            gap = nxt["x"] - x1
            held = r.gap_window(gap, r.HELD)
            tap = r.gap_window(gap, r.TAP)
            if held is None or (held[1] - held[0]) / r.RUN < 0.2:
                problems.append(f"roof gap at {x1:.1f} ({gap:.1f} m): a held jump has under 0.2 s")
                held = held or (0.0, 0.0)
            latest = x1 + held[1]
            rows.append([x1, nxt["x"], ROOF, "roofgap", name, it, latest, max(nxt["x"] + 0.3, latest + r.JUMP_LEN),
                         f"a {gap:.1f} m gap between roofs: held {(held[1] - held[0]) / r.RUN * 1000:.0f} ms"
                         + (f", tap {(tap[1] - tap[0]) / r.RUN * 1000:.0f} ms" if tap else ", a tap falls short")])
            if not any(a <= x1 - 0.2 and b >= nxt["x"] + 0.2 for a, b, h in hops):
                problems.append(f"roof gap at {x1:.1f}: no rooster hop across it")
        else:
            drop = x1 + r.RUN * r.fall_time(ROOF)
            rows.append([x1, x1, ROOF, "drop", name, it, x1, drop,
                         f"off the end of the roofs (no input), landing about {drop - x1:.1f} m on"])
            if not any(a <= x1 - 0.1 and b >= x1 + 0.5 for a, b, h in hops):
                problems.append(f"roofs ending at {x1:.1f}: no rooster hop down")
        if not any(a <= x0 - 0.3 and b >= x0 + 0.1 for a, b, h in hops):
            problems.append(f"roofs at {x0:.1f}: no rooster hop up")
        else:
            h = next(hp for hp in hops if hp[0] <= x0 - 0.3 and hp[1] >= x0 + 0.1)
            if p.rooster_y(h, x0) < ROOF:
                problems.append(f"roofs at {x0:.1f}: the rooster's hop up meets the wall at {p.rooster_y(h, x0):.2f} m")
    for o in rows:
        if o[3] == "tank" and not any(it["x"] <= o[0] <= it["end"] for it in roofs):
            problems.append(f"tank at {o[0]:.1f} is not on a roof")
    rows.sort(key=lambda row: (row[0], row[1]))

    # ---- consecutive challenges: after one at the latest moment, room to react and still clear the next
    no_input = ("ladder", "drop", "cart", "sacks", "bridge", "cot", "branch", "awnings", "steps")
    # things close together: under 0.7 s of running apart (4.5 m at the old 6 m/s)
    close = 0.7 * r.RUN
    for a, b in zip(rows, rows[1:]):
        slack = b[6] - a[7] - (0.0 if b[3] in no_input else r.REACT)
        if slack < 0.5:
            problems.append(f"{a[3]} at {a[0]:.1f} then {b[3]} at {b[0]:.1f}: {slack:.2f} m to react after the landing")
        # (a step onto a branch, the awnings or the steps is meant to be close: they are routes, not obstacles)
        if (b[0] - a[1] < close and a[3] not in ("ladder", "drop", "roofgap", "branch", "awnings", "steps", "cot")
                and b[3] not in ("cart", "sacks", "ladder", "drop", "roofgap", "branch", "awnings", "steps", "cot")
                and a[2] == b[2]):
            problems.append(f"{a[3]} at {a[0]:.1f} and {b[3]} at {b[0]:.1f} only {b[0] - a[1]:.1f} m apart")

    # ---- the rooster's route: a hop over everything in the lane, high enough, starting before it
    for x0, x1, base, kind, name, it, *_ in rows:
        if (kind in ("bridge", "ladder", "roofgap", "drop", "clothesline", "lowbranch", "cot", "branch", "awnings", "steps")
                or it.get("hidden")):
            continue                          # he runs under a low branch; a knocked-in obstacle lands behind him
        need = base + (it.get("top", 0.0) if kind not in ("canal",) else 0.0)
        margin = {"cart": -0.2, "sacks": -0.2, "canal": 0.2, "haystack": 0.1}.get(kind, 0.15)
        h = next((hp for hp in hops if hp[0] <= x0 - 0.2 and hp[1] >= x1 + 0.1), None)
        if h is None:
            problems.append(f"{kind} at {x0:.1f}: no rooster hop over it")
            continue
        lowest = min(p.rooster_y(h, x) for x in (x0, (x0 + x1) / 2, x1))
        if kind in ("cart", "sacks"):
            need = it["bed"]
        if lowest < need + margin:
            problems.append(f"{kind} at {x0:.1f}: the rooster's hop is only {lowest:.2f} m up over it (needs {need + margin:.2f})")

    # ---- chillies: no challenge inside the boost
    for s, it in p.items("chilli"):
        nxt = [row for row in rows if row[0] > it["x"] and row[3] not in ("bridge", "ladder", "drop", "branch", "awnings", "steps")]
        if nxt and nxt[0][0] - it["x"] < r.BOOST * 0.8:
            problems.append(f"chilli at {it['x']}: {nxt[0][3]} {nxt[0][0] - it['x']:.1f} m after it, inside the boost")

    # ---- feathers: one of each, reachable with a double jump from the surface they sit over
    feathers = [it for _, it in p.items("feather")]
    if require_feathers and sorted(f["index"] for f in feathers) != [0, 1, 2]:
        problems.append("the three feathers (0, 1, 2) are not all there once")
    reach = T["doubleJumpTotalHeight"] + 0.55 + 0.3
    for f in feathers:
        # the double jump's top is about 4 m on from its take-off: the surface it can start from, or a bounce
        under = max(p.ground_at(f["x"] + d) for d in (-4.0, -3.0, -2.0, -1.0, 0.0, 1.0))
        top = under + reach
        extra = T["doubleJumpTotalHeight"] - T["jumpHeight"] + 0.85
        for row in rows:
            if row[0] - 5.0 <= f["x"] <= row[1] + 2.0:
                if row[3] == "cot":
                    top = max(top, 0.5 + T["cotBounceHeight"] + extra)
                elif row[3] == "buffalo":
                    top = max(top, 1.1 + 2.6 + extra)
                elif row[3] == "awnings":
                    top = max(top, 2.1 + 2.0 + extra)
        if f["y"] > top:
            problems.append(f"feather {f['index']} at {f['x']}: {f['y']} m is above a double jump's reach")

    # ---- mischief: its target is hidden, in the same section
    for s, it in p.items("mischief"):
        target = next((t for t in s["items"] if t.get("id") == it["target"]), None)
        if target is None or not target.get("hidden"):
            problems.append(f"mischief at {it['x']}: its target is missing or not hidden")

    # ---- mangoes: none inside a wall or a roof, none under a canal's water
    for s, it in p.items("mango"):
        g = p.ground_at(it["x"])
        if it["y"] < g + 0.2:
            problems.append(f"mango at {it['x']}, {it['y']} m: inside what stands there (top {g} m)")

    # ---- the chase: when a clean run catches him
    closing = r.RUN - T["roosterRunSpeed"]
    for gap in sorted(set(p.start_gaps)):
        t = (gap - T["grabDistance"]) / closing
        notes.append(f"a clean run from a {gap:.0f} m start catches him after about {t:.0f} s, at about {r.RUN * t:.0f} m "
                     f"(without chillies)")
    first = {}
    for row in rows:
        first.setdefault(row[3], row[0])
    notes.append("first of each: " + ", ".join(f"{k} {v:.0f} m" for k, v in first.items()))
    return problems, notes, rows


# ------------------------------------------------------------------ writing it out
NAMES = {"pots": "pot stack", "dung": "cow dung", "dog": "sleeping dog", "puddle": "hand-pump puddle",
         "cart": "bullock cart", "tank": "water tank", "hensbasket": "hens' basket", "clothesline": "clothesline",
         "sacks": "sacks of paddy", "sand": "heap of building sand", "lowbranch": "low neem branch"}


def describe(s):
    out, mangoes = [], 0
    for it in s["items"]:
        k = it["kind"]
        if k == "mango":
            mangoes += 1
        elif k in NAMES:
            out.append(f"{NAMES[k]} {it['x']:g}" + (" (knocked in by the rooster)" if it.get("hidden") else "")
                       + (" on the roof" if it.get("y") else ""))
        elif k == "canal":
            out.append(f"{it['width']:g} m canal {it['x']:g}" + (" with the plank" if it["bridge"] else ""))
        elif k == "roofs":
            out.append(f"roofs {it['x']:g} to {it['end']:.1f}" + (" (ladder)" if it["ladder"] else ""))
        elif k == "haystack":
            out.append(f"{'big' if it['big'] else 'small'} haystack {it['x']:g}")
        elif k == "cot":
            out.append(f"rope cot {it['x']:g}")
        elif k == "buffalo":
            out.append(f"buffalo {it['x']:g}")
        elif k == "mangotree":
            out.append(f"mango tree and branch {it['x']:g}")
        elif k == "stall":
            out.append(f"stall {it['x']:g}")
        elif k == "hens":
            out.append(f"{it['count']} hens {it['x']:g}")
        elif k == "goats":
            out.append(f"{it['count']} goat kid{'s' if it['count'] > 1 else ''} {it['x']:g}")
        elif k == "ducks":
            out.append(f"{it['count']} ducks {it['x']:g}")
        elif k == "steps":
            out.append(f"temple steps {it['x']:g} to {it['end']:.1f}")
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


def report(p, meta, notes, problems, rows):
    n = meta["level"]
    lines = [
        f"# Level {n}: {meta['title']}",
        "",
        f"The beat sheet for level {n} (zone {p.zone}). It is written by `ArtSource/tools/levels/level{n}.py --report` from",
        f"the same plan the game is built from (`Assets/ChickenRunner/Art/Levels/level{n}.json`), so it cannot drift from",
        "it. Edit the plan script, not this page, and run it again; it audits the course with the game's own jump maths",
        "and tuning, and fails on a violation. `GameBuilder` (Chicken Runner > Build Game) then lays one chunk per section.",
        "",
        f"Zone {p.zone}: the kid runs at {p.r.RUN:g} m/s, the rooster at {p.r.T['roosterRunSpeed']:g} m/s; a held jump is "
        f"{p.r.JUMP_LEN:.2f} m long and {p.r.T['jumpHeight']:g} m high; the course is {p.r.T['courseLength']:g} m.",
        "",
    ]
    lines += meta["prose"]
    lines += ["", "## The course", "", "| From | To | Section | What is there | Why |", "|---:|---:|---|---|---|"]
    for s in p.sections:
        lines.append(f"| {s['x']:g} | {s['x'] + s['length']:g} | {s['name']} | {describe(s)} | {s['note']} |")
    lines += ["", "## The audit", ""]
    lines += [f"* {x}" for x in notes]
    lines += ["", "How each challenge is cleared, and the take-off windows (how long the player has to start the move):", ""]
    lines += ["```"] + [f"{row[3]:11s} {row[0]:6.1f} m ({row[4]}): {row[8]}" for row in rows] + ["```", ""]
    lines.append("Problems: " + ("none." if not problems else ""))
    lines += [f"* {pr}" for pr in problems]
    out = DOCS / f"level{n}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")


def run(p, meta):
    """Audit the plan, write its JSON (and with --report its beat sheet); exit non-zero on a problem."""
    T = p.r.T
    course = meta.get("courseLength", T["courseLength"])
    problems, notes, rows = audit(p, course)
    n = meta["level"]
    data = {"level": n, "zone": p.zone, "title": meta["title"], "subtitle": meta["subtitle"], "courseLength": course}
    data.update(meta.get("extra", {}))
    data["jumpLength"] = round(p.r.JUMP_LEN, 3)
    data["sections"] = p.sections
    out = LEVELS / f"level{n}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1))
    counts = {}
    for _, it in p.items():
        counts[it["kind"]] = counts.get(it["kind"], 0) + 1
    end = p.sections[-1]["x"] + p.sections[-1]["length"]
    print(f"wrote {out.relative_to(ROOT)}: {len(p.sections)} sections, {end:.0f} m,",
          ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    print(f"zone {p.zone}: run {p.r.RUN:g} m/s; jump {p.r.JUMP_LEN:.2f} m held, {p.r.length(p.r.TAP):.2f} m tapped, "
          f"{p.r.length(p.r.DOUBLE):.2f} m with a double jump; gravity {p.r.G:.1f}")
    for x in notes:
        print("  " + x)
    for row in rows:
        print(f"  {row[3]:11s} {row[0]:6.1f} m ({row[4]}): {row[8]}")
    if "--report" in sys.argv:
        report(p, meta, notes, problems, rows)
    if problems:
        print("PROBLEMS:")
        for pr in problems:
            print("  - " + pr)
        sys.exit(1)
    print("audit: no problems")
    return problems
