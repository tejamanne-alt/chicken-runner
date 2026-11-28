"""Draws a level plan in Blender as the game builds and frames it, and audits the placed scene.

    S=<scratchpad>; $S/blender/venv/bin/python ArtSource/tools/levels/render_level.py -- \\
        --plan Assets/ChickenRunner/Art/Levels/level1.json --out DIR \\
        [--every 8] [--from X --to X] [--gap 10] [--shots x1,x2,...] [--samples N] [--orbit] \\
        [--no-render] [--res 1280x720] [--threads 2] [--level N] [--sweep 1.0]

  --level N               plan Assets/ChickenRunner/Art/Levels/levelN.json (instead of --plan); without --out, writes
                          to $LEVEL_RENDER_DIR/levelN (default /tmp/level_render/levelN)
  --sweep M               the step of check i's sweep along the course (default 1 m)

Writes:
  DIR/shots/x+024.0.png   one 1280x720 frame per shot: the kid at that course x, the rooster `gap` metres ahead, framed
                          by the chase camera
  DIR/contact_sheet.jpg   every shot, four a row, labelled with x and section (and DIR/contact_NN.jpg, 16 a page)
  DIR/orbit/*.png         with --orbit: the yard (the level's opening) seen as a set from front-left, front-right and
                          above, plus the game's own opening frame (DIR/orbit_sheet.jpg)
  DIR/checks.json, .md    automated checks on the placed scene (see CHECKS below)
  DIR/shots.json          each shot's camera, kid and rooster

Shots at x <= 0 in a level with a basket item show the opening (the basket intro): the kid idle at x, the rooster under
the basket, the neighbour asleep, the camera framing the two. Shots at x > 0 are the chase: the kid running (on the
ground, or on a cart's bed when she is over one), the rooster at x + gap (on his authored hop when he is in one), the
basket flung aside, the neighbour awake, the mischief pots in the lane once the rooster has passed their spot.

Plan visual kinds: art (a model or card; y > 0 stands it on a roof), decal, pickup, water (Kit.Puddle's ellipse for a
puddle, a canal's flat water at its y otherwise), hidden (not drawn; the neighbour's awake card in the chase), box (a
solid grey-box slab, roof or plank: centre x, bottom y, z, w x h x d, `color`), hole (no ground from x to x+w: the slabs'
cut ends as earth walls down to the canal's bed at -0.28), ladder (the bamboo ladder model at its own size, foot at
x, y, z, leaning to `head` [x, y, z] or back toward the wall). Boxes, cart beds and canal beds are what the kid and
rooster stand on. Zone 2 draws its paddy water beyond the bund (GameBuilder.ZoneGround), and drops flat scenery on the
lane as ZoneArtBuilder does.

What it mirrors, file by file:
  * GameBuilder.Plans.cs: one chunk per section, laid end to end from the runway start; props through Kit.Art with the
    item's h (else w); decals through Kit.Decal with the item's own turn; pots with the plan's mirror; the basket
    hinged at `hinge` with the neighbour asleep (1.0 m) and awake (1.25 m) beside it.
  * GameBuilder.Kit.cs: Art (size from the cut-out's aspect, the manifest's when it has one; nothing at all when the
    cut-out PNG is missing, model or not), Decal (lies flat when its model is a slab or it has no model; a card decal
    0.004 m up), PotStack/Dung/Dog/Puddle/Cart (the puddle's water is the Unity cylinder: an ellipse width x 0.9 m with
    the water ground shader; the cart's bed is an invisible 0.95 m box over the first 62% of the cart), pickups (the
    character-folder models at their own size, tilted 12 / -30 / 0 degrees, spun about the vertical).
  * ArtModels.cs Place: size / (record width, height), depth by their mean, capped by roomBehind; set down by the
    record's lift clamped to 0..0.1; facing the camera, turned by `turn`; mirror flips x; flat models laid face up
    0.002 m over the ground; toon surface (shadow tint 0.86/0.8/0.86, edge -0.15, softness 0.25), ink 3-12 mm by size,
    none on flat pieces, leaf cards cut out at alpha 0.5 and two-sided; only Blender/TRELLIS models (an extruded-only
    model is its painted card, as with "Include Extruded Scenery Models" off). ArtAssets.Card for the rest.
  * ZoneArtBuilder.cs + BackdropStreamer.cs: the layout's wide cards (w >= 20 m) as strips per depth, the rest as one set
    cut to the near cards' stretch; standing cards between z -2 and 1.4, flat ones on the running line (|z| < 0.9; zone
    2: anywhere on the lane) and the Characters/Ground layers dropped; the side lanes (side_lane_mud.png, 8 m back from
    the road's back edge, in house gaps of 3 m or more, zones 1 and 3); each track repeated every period with exactly
    the copies the streamer keeps alive around the camera's x, the set's odd copies its mirrored arrangement
    (x' = 2 start + period - x, pictures unflipped); ArtModels.RoomBehind per track.
  * GameBuilder.cs ZoneGround/GroundMaterial + PaintedGround.shader: the red earth tiled 3.5 m in world space, the turned
    second sample, the slow drifts and the depth haze 6..40 m (zone 2: paddy beyond the bund, haze 10..55 m); the zone's
    road band (RoadFront..RoadBack read from GameBuilder.cs, wavy soft edges, its tile u = x / RoadTile, v front to
    back); ground only where the game has it (the chunks' slabs from x = -10, z -40..4.5, cut by canal holes; the
    streamer's plane z 4.4..95); the canals' light water tile and granite kerbs; the puddle card; the sky is the haze.
  * ChaseCamera.cs (Kick Off's framing): a 34 degree vertical lens pitched 4 degrees down; half-height
    max(2.7, minHalf / aspect) with minHalf = max(5.5, 1 s of the zone's run speed / (2 x 2/3)); the screen's centre on
    the lane plane, the kid on the left third, 1.75 m above the ground she stands on (not following jumps); a close
    rooster pulls the view back up to 1.25 (2.4 in the Ready state before the first tap; the basket intro stays close).
  * GameBuilder.Characters.cs PlaceModel: the kid and rooster turned by s_facing (115 degrees: run toward +x, 25
    degrees toward the camera), toon with 4 mm ink; RoosterBrain: his hops (sine arcs between the ground under their
    ends), the highest surface under him otherwise.
  * Toon.shader: two tones split by the fixed light (-0.45, 0.7, -0.55), backfaces culled, the inverted-hull outline
    (here a Solidify shell, the audit.py way), gloss on gold, mango and chilli.

CHECKS (checks.json / checks.md), each with course x, section, piece and what is wrong:
  a floating     a visual's lowest point (a model's mesh, a card's lowest painted row) off what it stands on
  b lane         a lane-side prop (not an obstacle, pickup or decal) whose footprint reaches |z| < 0.75
  c overlap      standing visuals overlapping in plan by more than 5 cm (a prop inside a house, pots inside a cart)
  d hidden       obstacles hidden from the camera: rays from the camera (kid 3, 6 and 10 m before it) to points on it,
                 blocked by scenery in front or covered by a pickup
  e missing      pieces with no model and no cut-out, which the game skips (or draws as grey boxes)
  f repeat       the same house within 20 m, the same figure or animal within 30 m, a plan prop beside the same piece
                 in the scenery
  g pickups      pickups inside or poking through solid geometry, or two on one spot
  i hidden       the kid or rooster hidden behind anything (scenery in front of the lane, a prop, the cart), swept
                 along the whole course every metre (--sweep) with the close camera, as x ranges
  h other        standing litter big enough to read as an obstacle, decals drawn far over their real size, plan sizes
                 that no longer match the art, the plan's flat flag against the game's rule, scenery decals on the
                 running line at an obstacle, pickups hidden behind things, the kid or rooster hidden in a shot, bare
                 sky where the game has no ground, extruded-only pieces drawn as flat cards
"""
import json
import math
import os
import pathlib
import re
import shutil
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
ART = ROOT / "Assets" / "ChickenRunner" / "Art"
SCRIPTS = ROOT / "Assets" / "ChickenRunner" / "Scripts"
CUTOUTS = ROOT / "ArtSource" / "cutouts"
SHADERS = ART / "Shaders"

ARGS = [a for a in sys.argv[1:] if a != "--"]


def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS and ARGS.index(name) + 1 < len(ARGS) else default


def flag(name):
    return name in ARGS


def log(*a):
    print("[render_level]", *a, flush=True)


# ====================================================================== the game's numbers, read from its C#
def cs_number(rel, name, default):
    """`name = <number or a/b>` from a C# file (the first match), else the default."""
    try:
        src = (SCRIPTS / rel).read_text()
    except OSError:
        return default
    m = re.search(r"\b" + re.escape(name) + r"\s*=\s*(-?[\d.]+f?(?:\s*[*/]\s*-?[\d.]+f?)*)\s*[;,)]", src)
    if not m:
        return default
    return float(eval(m.group(1).replace("f", ""), {"__builtins__": {}}, {}))


_CC = "Gameplay/View/ChaseCamera.cs"
CAMERA = {k: cs_number(_CC, k, d) for k, d in (
    ("kidHeight", 1.08), ("kidScreenHeight", 0.241), ("feetScreenY", 0.169), ("lookAheadSeconds", 0.75),
    ("kidScreenX", 0.4), ("pitch", 4.0), ("maxRoosterZoom", 1.25), ("roosterScreenX", 0.9),
    ("maxEstablishingZoom", 2.4))}
BUILDER_FOV = cs_number("Editor/GameBuilder.cs", "fieldOfView", 34.0)
# The Kick Off framing is made for a 34 degree lens (GameBuilder.BuildScene); --fov overrides.
CAMERA["fov"] = float(arg("--fov", "34"))
CAMERA["near"] = cs_number("Editor/GameBuilder.cs", "nearClipPlane", 0.3)
CAMERA["far"] = cs_number("Editor/GameBuilder.cs", "farClipPlane", 260.0)


def zone_run_speed(zone):
    """ChaseTuning.ForZone: the kid's run speed in a zone (the default, or its case's override)."""
    try:
        src = (SCRIPTS / "Core" / "ChaseTuning.cs").read_text()
    except OSError:
        return 6.0
    speed = cs_number("Core/ChaseTuning.cs", "kidRunSpeed", 6.0)
    m = re.search(r"case\s+%d\s*:(.*?)(?:break|return)" % zone, src, re.S)
    if m:
        k = re.search(r"kidRunSpeed\s*=\s*(-?[\d.]+)f?", m.group(1))
        if k:
            speed = float(k.group(1))
    return speed
ZAB = {k: cs_number("Editor/ZoneArtBuilder.cs", k, d) for k, d in (
    ("StripWidth", 20.0), ("LaneFront", -2.0), ("LaneBack", 1.4), ("NearDepth", 11.0), ("CameraDistance", 30.0),
    ("ViewSpread", 0.6), ("groundTo", 95.0))}
GROUND_FROM = cs_number("Gameplay/Config/ZoneArt.cs", "groundFrom", 4.4)
KIT_GROUND_FRONT = cs_number("Editor/GameBuilder.Kit.cs", "GroundFront", -40.0)
KIT_GROUND_BACK = cs_number("Editor/GameBuilder.Kit.cs", "GroundBack", 4.5)
RUNWAY_START = cs_number("Gameplay/Level/LevelStreamer.cs", "runwayStart", -10.0)
RUNOUT = cs_number("Gameplay/Level/LevelStreamer.cs", "runoutLength", 40.0)
ROOSTER_UNDER_BASKET = cs_number("Gameplay/Level/BasketIntro.cs", "roosterX", 0.7)
BASKET_MAX_ANGLE = cs_number("Gameplay/Level/BasketIntro.cs", "maxAngle", 40.0)
FACING = 115.0                     # GameBuilder.Characters.cs s_facing = Euler(0, 115, 0)
LIGHT = (-0.45, 0.7, -0.55)        # Toon.shader _LightDir, Unity axes
OUTLINE_COLOUR = (0.13, 0.07, 0.05)
SCENERY_TOON = {"shadow": (0.86, 0.8, 0.86), "threshold": -0.15, "softness": 0.25}   # ArtModels.Surface
CHAR_TOON = {"threshold": 0.05, "softness": 0.04}                                   # Toon.shader defaults
LANE_HALF = 0.75                   # the running lane, for check b
CUT_FOLDERS = ["lane", "market", "fields", "animals", "people", "plants", "ground", "kid", "rooster", "textures"]
PICKUP_TILT = {"Mango": 12.0, "Chilli": -30.0, "Feather": 0.0}                      # Kit.Mango/Chilli/Feather
KIT_OBSTACLE = {"pots": ("h", 0.68, "pot_stack"), "dung": ("w", 0.6, "dung"), "dog": ("w", 0.95, "dog_sleeping"),
                "cart": ("w", 3.6, "bullock_cart")}
OBSTACLES = ("pots", "dung", "dog", "puddle", "cart", "clothesline", "hens", "hens_basket", "tank", "cot", "haystack",
             "buffalo", "canal", "steps", "stall", "goats", "ducks", "sand", "lowbranch", "sacks")
NOT_OBSTACLES = ("prop", "decal", "mango", "chilli", "feather", "hop", "mischief", "basket", "neighbour", "ladder", "hole",
                 "roof", "box", "house", "houses", "bridge", "plank")
STARTS_AT_X = ("cart", "sacks", "cot", "haystack", "buffalo", "canal", "steps", "stall")     # Kit calls that start at x
CANAL_BED = cs_number("Editor/GameBuilder.Kit.cs", "CanalBed", -0.28)
ROAD = {"front": cs_number("Editor/GameBuilder.cs", "RoadFront", -1.25), "back": cs_number("Editor/GameBuilder.cs", "RoadBack", 2.05),
        "tile": cs_number("Editor/GameBuilder.cs", "RoadTile", 4.0), "soft": 0.32, "wave": 0.2,
        "tiles": ["road_mud_lane", "road_cart_track", "road_cement"]}
for _k in ("soft", "wave"):                    # ZoneGround: ground.SetFloat("_RoadSoft", 0.32f) and "_RoadWave"
    try:
        _m = re.search(r'"_Road%s"\s*,\s*([\d.]+)f' % _k.capitalize(), (SCRIPTS / "Editor" / "GameBuilder.cs").read_text())
        if _m:
            ROAD[_k] = float(_m.group(1))
    except OSError:
        pass
RUNNING_LINE = cs_number("Editor/ZoneArtBuilder.cs", "RunningLine", 0.9)
SIDE_LANE = {"image": "ArtSource/cutouts/ground/side_lane_mud.png", "length": 8.0}
# Kit boxes drawn only as colliders: always (the mango tree's branch), or where the piece's art was drawn over them
HIDDEN_BOXES = ("branch",)
STONE_BOXES = ("bank",)            # Kit.Canal's granite kerbs: looks only, the lane's ground ends at the same edges
COVERED_BOXES = ("wall", "haystack", "buffalo", "body", "bed", "stack")
LADDER_REST = 2.43                 # Kit.StandLadder: on the parapet's coping, Roof + 0.08
PLANK_BRIDGE_LENGTH = cs_number("Editor/GameBuilder.Kit.cs", "PlankBridgeLength", 3.9)
KID_RUN_FRAME = int(arg("--kid-frame", "4"))
ROOSTER_RUN_FRAME = int(arg("--rooster-frame", "3"))


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(rgb):
    return tuple(srgb_to_linear(c) for c in rgb) + (1.0,)


# ====================================================================== the art on disk
MODEL_INDEX = {}
for _e in json.loads((ART / "Models" / "models.json").read_text())["models"]:
    if _e.get("name") and _e.get("width", 0) > 0 and _e.get("height", 0) > 0:
        MODEL_INDEX[_e["name"]] = _e
try:
    MANIFEST = json.loads((CUTOUTS / "lane" / "manifest.json").read_text())
except (OSError, ValueError):
    MANIFEST = {}
INCLUDE_EXTRUDED = flag("--extruded")


def stem(path_or_name):
    return pathlib.Path(path_or_name).stem


def cutout(name):
    """ArtAssets.Cutout: the first ArtSource/cutouts/<folder>/<name>.png."""
    for f in CUT_FOLDERS:
        p = CUTOUTS / f / f"{name}.png"
        if p.exists():
            return p
    return None


def model_entry(piece, why=None):
    """ArtModels.Find + Model: the record of a piece's usable model, or None (none, extruded-only, FBX missing)."""
    e = MODEL_INDEX.get(stem(piece))
    if e is None:
        return None
    if (not e.get("source") or e["source"] == "extruded") and not INCLUDE_EXTRUDED:
        if why is not None:
            why.append("extruded")
        return None
    if not (ART / "Models" / e["folder"] / f"{e['name']}.fbx").exists():
        if why is not None:
            why.append("fbx missing")
        return None
    return e


_IMG = {}


class ImgInfo:
    """A picture's size, a small alpha map (for rays through cut-outs) and its transparent margin at the bottom."""

    def __init__(self, path):
        import numpy as np
        from PIL import Image
        im = Image.open(path)
        self.path = path
        self.size = im.size
        im = im.convert("RGBA")
        small = im.copy()
        small.thumbnail((768, 768))
        self.alpha = np.asarray(small)[..., 3].astype(np.float32) / 255.0
        a = np.asarray(im)[..., 3]
        rows = np.where(a.max(1) > 127)[0]
        cols = np.where(a.max(0) > 127)[0]
        h, w = a.shape
        self.bottom_margin = (h - 1 - rows.max()) / h if len(rows) else 0.0
        self.opaque = (cols.min() / w, 1 - (rows.max() + 1) / h, (cols.max() + 1) / w, 1 - rows.min() / h) \
            if len(rows) else (0, 0, 1, 1)       # u0, v0, u1, v1 (v up)

    def alpha_at(self, u, v):
        h, w = self.alpha.shape
        if not (0 <= u <= 1 and 0 <= v <= 1):
            return 0.0
        return float(self.alpha[min(h - 1, int((1 - v) * h)), min(w - 1, int(u * w))])


def img_info(path):
    path = pathlib.Path(path)
    if path not in _IMG:
        _IMG[path] = ImgInfo(path) if path.exists() else None
    return _IMG[path]


def size_of(name, path, fallback=1.0):
    """ArtAssets.SizeOf: (width, height) in metres from the manifest, keeping the picture's proportions."""
    info = img_info(path) if path else None
    aspect = info.size[0] / info.size[1] if info else 1.0
    s = MANIFEST.get(name)
    if s:
        px = s.get("px")
        if px and px[1] > 0:
            aspect = px[0] / px[1]
        if s.get("px_per_m", 0) > 0 and px:
            return px[0] / s["px_per_m"], px[1] / s["px_per_m"], "manifest"
        if s.get("height_m", 0) > 0:
            return s["height_m"] * aspect, s["height_m"], "manifest"
        if s.get("width_m", 0) > 0:
            return s["width_m"], s["width_m"] / aspect, "manifest"
    return fallback * aspect, fallback, "picture"


def outline_for(w, h):
    """ArtModels.Place: 0.25% of the larger side, 3..12 mm, in 2 mm steps."""
    return round(min(0.012, max(0.003, 0.0025 * max(w, h))) * 500) / 500


# ====================================================================== the chase camera and who stands where
def frame_camera(kid_x, ground_y, gap, aspect=16 / 9, run=6.0, establishing=False):
    """ChaseCamera.Frame (snapped), framed as Kick Off's gameplay measures on a phone: the kid kidScreenHeight of the
    screen tall, her feet feetScreenY up it, kidScreenX across; wider only where the zone's run speed needs the lane
    ahead; the screen's centre on the lane plane over the ground she stands on (it does not follow jumps); a close
    rooster pulls the view back (up to 1.25, or 2.4 before the chase)."""
    c = CAMERA
    min_half = c["lookAheadSeconds"] * run / (2 * (1 - c["kidScreenX"]))
    base_h = max(0.5 * c["kidHeight"] / max(0.05, c["kidScreenHeight"]), min_half / aspect)
    zoom = 1.0
    if gap > 0:
        needed = (gap + 0.6) / (2 * max(0.05, c["roosterScreenX"] - c["kidScreenX"])) / max(0.1, base_h * aspect)
        if establishing:
            zoom = min(max(needed, 1.0), c["maxEstablishingZoom"])
        else:
            zoom = max(1.0, needed) if needed <= c["maxRoosterZoom"] else 1.0
    half_h = base_h * zoom
    half_w = half_h * aspect
    cy = max(ground_y + (1 - 2 * c["feetScreenY"]) * half_h, ground_y + 1.3 - half_h * 0.85)
    cy = min(cy, ground_y + half_h * 0.8)
    cx = kid_x + (0.5 - c["kidScreenX"]) * 2 * half_w
    dist = half_h / math.tan(math.radians(c["fov"]) / 2)
    pitch = math.radians(c["pitch"])
    return {"pos": (cx, cy + math.sin(pitch) * dist, -math.cos(pitch) * dist), "target": (cx, cy, 0.0),
            "width": 2 * half_w, "distance": dist, "zoom": zoom, "half_height": half_h}


def support(x, surf):
    """The highest solid surface under x on the running line (a cart's bed, a roof or plank, else the ground, or a
    canal's bed in a hole in it): KidController/RoosterBrain.GroundAt, a ray down at z = 0."""
    beds, holes = surf
    y = CANAL_BED if any(a <= x <= b for a, b in holes) else 0.0
    for a, b, top in beds:
        if a <= x <= b:
            y = max(y, top)
    return y


def in_hole(x, surf):
    return any(a <= x <= b for a, b in surf[1])


def is_obstacle(it):
    k = it["kind"]
    return k in OBSTACLES or (k not in NOT_OBSTACLES and ("span" in it or "top" in it))


def rooster_at(rx, hops, beds):
    """RoosterBrain.FollowRoute: on an authored hop he arcs between the ground under its ends, else he runs."""
    cur, end = None, -1e9
    for h in sorted(hops):
        if h[0] > rx:
            break
        if h[0] + 0.5 >= end:            # he can only enter a hop at its start, and only once out of the last one
            cur, end = h, h[1]
    if cur and cur[0] <= rx < cur[1]:
        p = (rx - cur[0]) / (cur[1] - cur[0])
        y0, y1 = support(cur[0], beds), support(cur[1] + 0.05, beds)
        return y0 + (y1 - y0) * p + cur[2] * math.sin(math.pi * p), "Flutter"
    return support(rx, beds), "Run"


# ====================================================================== the scene, as data
class Rec:
    """One placed visual: a model, a card, the water, a pickup."""

    def __init__(self, **kw):
        self.parts = []          # (PartLib, object, world matrix, inverse)
        self.objs = []
        self.aabb = None
        self.track = None
        self.state = "always"
        self.notes = []
        self.item = None
        self.item_id = None
        self.card = None
        self.haze = 0.0
        self.room = float("inf")
        self.entry = None
        self.image = None
        self.turn = 0.0
        self.mirror = False
        self.flat = False
        self.section = ""
        self.copy = None
        self.layer = ""
        self.__dict__.update(kw)


class Level:
    def __init__(self, plan_path):
        self.plan = json.loads(pathlib.Path(plan_path).read_text())
        self.sections = self.plan["sections"]
        self.start = self.sections[0]["x"]
        self.end = self.sections[-1]["x"] + self.sections[-1]["length"]
        self.course = float(self.plan.get("courseLength", self.end))
        self.recs = []
        self.obstacles = []      # dict(kind, x0, x1, top, section, recs, item)
        self.beds = []           # (x0, x1, top): cart beds, roofs, planks the kid and rooster run on
        self.holes = []          # (x0, x1): gaps in the ground (canals)
        self.solids = []         # boxes, drawn or not: what a prop can stand on
        self.surf = (self.beds, self.holes)
        self.rooster_beds = []
        self.rooster_surf = (self.beds + self.rooster_beds, self.holes)
        self.hops = []           # (x0, x1, height)
        self.pickups = []
        self.basket = None
        self.problems = []       # plan-level findings made while reading it
        self.read_plan()
        self.layout = json.loads((ART / "Layouts" / f"{self.layout_name()}.json").read_text())
        self.haze_srgb = tuple(self.layout.get("hazeColor", (0.98, 0.765, 0.545)))
        self.tracks = scenery_tracks(self.layout, self.zone)

    @property
    def zone(self):
        return int(self.plan.get("zone", 1))

    def layout_name(self):
        return {1: "lane_zone1", 2: "fields_zone2", 3: "market_zone3"}.get(self.zone, "lane_zone1")

    def section_at(self, x):
        for s in self.sections:
            if s["x"] <= x < s["x"] + s["length"]:
                return s["name"]
        return "before the course" if x < self.start else "after the course"

    # ------------------------------------------------------------------ the plan, as GameBuilder.Kit would build it
    def read_plan(self):
        mischief = {}
        for s in self.sections:
            for it in s["items"]:
                if it["kind"] == "mischief":
                    mischief[it.get("target")] = it["x"]
        for si, s in enumerate(self.sections):
            for ii, it in enumerate(s["items"]):
                k = it["kind"]
                if k == "hop":
                    self.hops.append((it["x"], it["x"] + it["length"], it["height"]))
                    continue
                if it.get("implicitHop"):          # the hop a Kit call adds by itself (Canal, RoofRow, Haystack)
                    hx, hl, hh = it["implicitHop"][:3]
                    self.hops.append((hx, hx + hl, hh))
                if k in ("cart", "sacks"):
                    self.beds.append((it["x"], it["x"] + it.get("span", 3.6 * 0.62), it.get("bed", 0.95)))
                if k == "haystack" and "span" in it:
                    # Kit.Haystack: an invisible solid over the middle 80% of the stack's width, `top` high
                    mid = it["x"] + it.get("width", it["span"] / 0.8) / 2
                    self.beds.append((mid - it["span"] / 2, mid + it["span"] / 2, it.get("top", 1.05)))
                    self.solids.append({"x0": mid - it["span"] / 2, "x1": mid + it["span"] / 2, "z0": -0.7, "z1": 0.7,
                                        "top": it.get("top", 1.05), "piece": "haystack (solid)"})
                item_id = f"{s['name']}#{ii}"
                recs = []
                for vi, v in enumerate(it.get("visuals", [])):
                    rec = self.plan_visual(s, it, item_id, vi, v)
                    if rec is None:
                        continue
                    if it.get("hidden"):
                        rec.state = ("after", mischief.get(it.get("id"), it["x"]))
                    recs.append(rec)
                    self.recs.append(rec)
                if k == "steps" and int(it.get("count", 0)) == 6 and abs(float(it.get("landing", 0)) - 6.0) < 0.01 \
                        and (ART / "Models" / "market" / "temple_steps.fbx").exists():
                    # Kit.Steps: the hand-built granite flight, stood (ArtModels.Stand, its own size, upright) at the
                    # flight's middle, z 0.4; the step boxes stay as colliders with their renderers off
                    steps = [r for r in recs if r.mode == "box" and r.piece == "step"]
                    for r in steps:
                        r.mode = "solid"
                    x0_ = min((r.x - r.w / 2 for r in steps), default=it["x"])
                    x1_ = max((r.x + r.w / 2 for r in steps), default=it.get("end", it["x"]))
                    mid = (x0_ + x1_) / 2
                    zs = steps[0].z if steps else 0.6           # Kit.Steps: the model at the colliders' depth (0.6)
                    stand = Rec(role="platform_art", mode="ladder", src="plan", section=s["name"], item=it, item_id=item_id,
                                item_kind=k, piece="temple_steps", name=f"{s['name']}/steps@{it['x']:.1f}/temple_steps",
                                x=mid, y=0.0, z=zs, w=x1_ - x0_, h=1.5, flat=False, outline=0.004, vis_kind="art",
                                entry={"name": "temple_steps", "folder": "market", "width": 1.0, "height": 1.0,
                                       "depth": 1.8, "kind": "volume"})
                    stand.head = (mid, 1.0, zs)
                    recs.append(stand)
                    self.recs.append(stand)
                if k == "canal" and it.get("bridge") and (ART / "Models" / "fields" / "plank_bridge.fbx").exists():
                    # Kit.Canal: the hand-built plank bridge stood on the walkway's top and stretched to width + 0.4; the
                    # plank box stays as a collider, the rails and posts are not made
                    for r in recs:
                        if r.mode == "box" and r.piece == "plank":
                            r.mode = "solid"
                        elif r.mode == "box" and r.piece in ("rail", "post"):
                            r.mode = "hole"            # not built at all
                    width = float(it.get("width", it.get("span", 3.5)))
                    mid = it["x"] + width / 2
                    bridge = Rec(role="platform_art", mode="ladder", src="plan", section=s["name"], item=it,
                                 item_id=item_id, item_kind=k, piece="plank_bridge",
                                 name=f"{s['name']}/canal@{it['x']:.1f}/plank_bridge", x=mid, y=0.0, z=0.0, w=width + 0.4,
                                 h=0.6, flat=False, outline=0.004, vis_kind="art",
                                 entry={"name": "plank_bridge", "folder": "fields", "width": 1.0, "height": 1.0,
                                        "depth": 1.0, "kind": "volume"})
                    bridge.head = (mid, 1.0, 0.0)
                    bridge.stand_scale_x = (width + 0.4) / PLANK_BRIDGE_LENGTH
                    recs.append(bridge)
                    self.recs.append(bridge)
                for r in recs:
                    # Kit.FrontAt: pushed back until the front of its renderers is at this depth (never forward)
                    if k == "stall" and r.vis_kind == "art":
                        r.front_at = 0.45
                    elif k == "mangotree" and r.piece == "tree_mango_1":
                        r.front_at = 0.45
                    elif (k == "cart" and r.piece == "bullock_cart") or (k == "sacks" and r.piece == "jute_sacks"):
                        r.front_at = -0.3
                    # Kit.RoofRow: its house fronts placed with roomBehind 1.0 (Place squashes their depth to fit)
                    if k == "roofs" and r.vis_kind == "art" and r.role == "platform_art":
                        r.room = 1.0
                if is_obstacle(it):
                    if k in ("cart", "sacks"):
                        x0, x1, top = it["x"], it["x"] + it.get("span", 3.6 * 0.62), it.get("bed", 0.95)
                    elif k == "haystack" and "span" in it:
                        mid = it["x"] + it.get("width", it["span"] / 0.8) / 2
                        x0, x1, top = mid - it["span"] / 2, mid + it["span"] / 2, it.get("top", 1.05)
                    elif "span" in it and k in STARTS_AT_X:
                        x0, x1, top = it["x"], it["x"] + it["span"], it.get("top", 0.3)
                    elif "span" in it:
                        x0, x1, top = it["x"] - it["span"] / 2, it["x"] + it["span"] / 2, it.get("top", 0.3)
                    else:
                        x0, x1, top = None, None, it.get("top", 0.3)      # from its visuals, once placed
                    self.obstacles.append({"kind": k, "x": it["x"], "x0": x0, "x1": x1, "top": top, "section": s["name"],
                                           "recs": [r for r in recs if r.role == "obstacle"], "item": it,
                                           "hidden": bool(it.get("hidden")),
                                           "after": mischief.get(it.get("id")) if it.get("hidden") else None})
                if k == "basket":
                    self.basket = it

    def plan_visual(self, s, it, item_id, vi, v):
        k, vk, piece = it["kind"], v.get("kind", "art"), v["piece"]
        common = dict(src="plan", section=s["name"], item=it, item_id=item_id, item_kind=k, piece=piece,
                      name=f"{s['name']}/{k}@{it['x']:.1f}/{piece}#{vi}", x=v["x"], y=v.get("y", 0.0), z=v.get("z", 0.0),
                      mirror=bool(v.get("mirror")), turn=float(v.get("turn", 0.0)), vis_kind=vk)
        if vk == "pickup":
            rec = Rec(role="pickup", mode="pickup", w=v.get("w", 0.3), h=v.get("h", 0.3), flat=False, **common)
            rec.spin = (v["x"] * 97.3 + 31) % 360
            rec.tilt = PICKUP_TILT.get(piece, 0.0)
            if not (ART / "Characters" / f"{piece}.fbx").exists():
                rec.mode = "missing"
                rec.notes.append(f"Characters/{piece}.fbx is missing: the game draws a grey-box shape")
            self.pickups.append(rec)
            return rec
        if vk == "water":
            # Kit.Puddle's water is a Unity cylinder (an ellipse); a canal's (Kit.Canal) a box across the whole ground
            return Rec(role="obstacle" if is_obstacle(it) else "water", mode="water", w=v["w"], h=0.008,
                       d=v.get("d", 0.9), flat=True, shape="ellipse" if k == "puddle" else "rect", **common)
        if vk == "hole":
            self.holes.append((v["x"], v["x"] + v["w"]))
            return Rec(role="hole", mode="hole", w=v["w"], h=0.0, flat=True, **common)
        if vk == "box":
            rec = Rec(role="platform", mode="box", w=v["w"], h=v["h"], d=v.get("d", 1.2), flat=False,
                      color=tuple(v.get("color") or (0.6, 0.6, 0.6)), **common)
            if abs(rec.z) <= rec.d / 2 + 0.05 and piece not in STONE_BOXES:
                bed = (rec.x - rec.w / 2, rec.x + rec.w / 2, rec.y + rec.h)
                # the kid runs under the mango tree's branch (she climbs it, she does not stand on it); the rooster, who
                # runs on whatever is highest under him, flutters up onto it
                (self.rooster_beds if piece in HIDDEN_BOXES else self.beds).append(bed)
            if piece not in STONE_BOXES:
                self.solids.append({"x0": rec.x - rec.w / 2, "x1": rec.x + rec.w / 2, "z0": rec.z - rec.d / 2,
                                "z1": rec.z + rec.d / 2, "top": rec.y + rec.h, "piece": piece})
            # Kit: a box is only a collider (its renderer off) where its piece's art was drawn over it (a house's wall in
            # RoofRow, a haystack's stack, the buffalo's body), and the mango tree's branch always
            fronts = [q for q in it.get("visuals", []) if q.get("kind", "art") == "art" and cutout(q["piece"])]
            if piece in HIDDEN_BOXES or (piece in COVERED_BOXES and any(abs(q["x"] - rec.x) < max(q["w"], rec.w) / 2
                                                                         for q in fronts)):
                rec.mode = "solid"
            return rec
        if vk == "model":
            # ArtModels.Stand at the visual's foot, upright, its own size (Kit.Clothesline's clothesline_line); mirrored,
            # the pivot's x scale is -1
            folder = next((f.name for f in (ART / "Models").iterdir() if (f / f"{piece}.fbx").exists()), None) \
                if (ART / "Models").exists() else None
            entry = {"name": piece, "folder": folder or "lane", "width": 1.0, "height": 1.0, "depth": 0.1, "kind": "volume"}
            role = "obstacle" if is_obstacle(it) else "prop"
            rec = Rec(role=role, mode="ladder" if folder else "missing", entry=entry, w=v.get("w", 1.0), h=v.get("h", 1.0),
                      flat=False, outline=0.004, **common)
            rec.head = (rec.x, rec.y + 1.0, rec.z)
            rec.stand_scale_x = -1.0 if rec.mirror else 1.0
            if not folder:
                rec.notes.append(f"Models/*/{piece}.fbx is missing")
            return rec
        if vk == "ladder":
            entry = {"name": piece if piece else "bamboo_ladder", "folder": v.get("folder", "lane"), "width": 1.0,
                     "height": 1.0, "depth": 0.1, "kind": "volume"}
            ok = (ART / "Models" / entry["folder"] / f"{entry['name']}.fbx").exists()
            rec = Rec(role="ladder", mode="ladder" if ok else "missing", entry=entry, w=0.45, h=v.get("h", 2.6),
                      flat=False, outline=0.004, **common)
            # Kit.StandLadder: foot 0.45 m before the house front, head on the parapet 0.05 m before it, leaning `lean`
            lean = v.get("lean", 0.163)
            rec.head = tuple(v["head"]) if v.get("head") else (rec.x + lean * rec.h, rec.y + rec.h, rec.z + 0.4)
            if not ok:
                rec.notes.append(f"Models/{entry['folder']}/{entry['name']}.fbx is missing: Kit draws grey-box rails")
            return rec
        # roles: the obstacle's own art; the other visuals of an obstacle (the hand pump) stand beside the lane; a
        # roof's or plank's house front or post is part of its platform
        platform_item = any(q.get("kind") == "box" for q in it.get("visuals", []))
        first_art = next((i for i, q in enumerate(it.get("visuals", []))
                          if q.get("kind", "art") in ("art", "water", "decal")), 0)
        if is_obstacle(it) and (vi == first_art or (vk == "art" and abs(v.get("z", 0.0)) < 0.3)):
            # the obstacle's own visual (Kit.Puddle's water is a flat puddle_water card, laid as a decal), and any other
            # art of it on the running line (Kit.Hens: a card per bird)
            role = "obstacle"
        elif vk == "decal":
            role = "decal"
        elif platform_item:
            role = "platform_art"
        elif is_obstacle(it):
            role = "lane"
        elif k == "basket":
            role = "basket"
        elif k == "neighbour":
            role = "figure"
        else:
            role = "prop"
        state = "always"
        if vk == "hidden":
            state = "chase" if k == "neighbour" else "never"
        elif k == "neighbour":
            state = "intro"
        tex = cutout(piece)
        why = []
        entry = model_entry(piece, why)
        rec = Rec(role=role, state=state, entry=entry, image=tex, flat=bool(v.get("flat")), w=v["w"], h=v["h"],
                  **common)
        if "extruded" in why:
            rec.extruded = True
        if tex is None:
            rec.mode = "missing"
            rec.notes.append("no cut-out PNG" + (" (its model is not used without one: Kit.Art returns null)" if entry else
                                                 " and no model") + ": the game skips it"
                             + (", or draws grey boxes" if role == "obstacle" else ""))
            return rec
        rw, rh, how = size_of(piece, tex)
        aspect = rw / rh
        # the size the Kit call makes: its fixed dimension (the plan's value), the other from the art's proportions
        if k in KIT_OBSTACLE and role == "obstacle":
            dim = KIT_OBSTACLE[k][0]
        elif k == "puddle":
            dim = "h"
        elif k == "prop":
            dim = "h" if it.get("h") else "w"
        elif vk == "decal" or k == "basket":
            dim = "w"
        else:
            dim = "h"
        if dim == "h":
            gw, gh = v["h"] * aspect, v["h"]
        else:
            gw, gh = v["w"], v["w"] / aspect
        if abs(gw - v["w"]) > 0.02 * max(v["w"], 0.1) or abs(gh - v["h"]) > 0.02 * max(v["h"], 0.1):
            rec.stale = (v["w"], v["h"], gw, gh)
        rec.w, rec.h = gw, gh
        rec.real = (rw, rh, how)
        if vk == "decal":
            # GameBuilder.Plans passes the item's own turn (0..360) to Kit.Decal, whatever the visual says
            if "turn" in it:
                rec.plan_turn = rec.turn
                rec.turn = float(it["turn"])
            # Kit.Decal: a model that lies flat (a slab) is laid face up, any other model stands; no model, a flat card
            game_flat = entry is None or entry.get("kind") == "slab"
            if game_flat != rec.flat:
                rec.flat_mismatch = (rec.flat, game_flat)
            rec.flat = game_flat
            if entry is None:
                rec.y = 0.004
        rec.mode = "model" if entry else "card"
        rec.outline = outline_for(rec.w, rec.h)
        return rec

    # ------------------------------------------------------------------ the zone's scenery, as the streamer repeats it
    def scenery_recs(self, x_from, x_to):
        """Every copy of every track that the streamer keeps alive for a camera anywhere in [x_from, x_to]."""
        out = []
        for ti, tr in enumerate(self.tracks):
            first = math.floor((x_from - tr["reach"] - tr["contentMax"]) / tr["period"])
            last = math.ceil((x_to + tr["reach"] - tr["contentMin"]) / tr["period"])
            for k in range(first, last + 1):
                for ci, c in enumerate(tr["cards"]):
                    out.append(self.scenery_card(ti, tr, k, ci, c))
        self.recs += out
        return out

    def scenery_card(self, ti, tr, k, ci, c):
        piece = stem(c["image"])
        why = []
        entry = model_entry(piece, why)
        path = ROOT / c["image"]
        cx = tr["axis"] - c["x"] if tr.get("axis") is not None and (k & 1) else c["x"]
        x = cx + k * tr["period"]
        rec = Rec(src="scenery", role="scenery", section=self.section_at(x), item_kind=c["layer"], layer=c["layer"],
                  piece=piece, name=f"{c['name']}@{k}" + (f"/t{ti}" if tr["kind"] == "strip" else ""), x=x, y=c["y"],
                  z=c["z"], w=c["w"], h=c["h"], mirror=bool(c["mirror"]), flat=bool(c["flat"]),
                  turn=float(c.get("turn", 0.0)), haze=float(c.get("haze", 0.0)), card=c, entry=entry, image=path,
                  track=(ti, k), copy=k, room=tr["room"][ci], vis_kind="scenery")
        if "extruded" in why:
            rec.extruded = True
        if entry:
            rec.mode = "model"
        elif path.exists():
            rec.mode = "card"
        else:
            rec.mode = "missing"
            rec.notes.append(f"{c['image']} is missing: the game skips it")
        rec.outline = outline_for(rec.w, rec.h)
        return rec


def scenery_tracks(layout, zone=1):
    """ZoneArtBuilder.Build: the strips (cards 20 m wide or more, one per depth) and the set (all the rest)."""
    def keep(c):
        if c["layer"] in ("Characters", "Ground"):
            return False
        if c["flat"]:
            # nothing lies on the running line itself, where a husk reads as an obstacle (the plans lay their own)
            return (zone != 2 or c["z"] < ZAB["LaneFront"] or c["z"] > ZAB["LaneBack"]) and abs(c["z"]) >= RUNNING_LINE
        return c["z"] <= ZAB["LaneFront"] or c["z"] >= ZAB["LaneBack"]

    cards = [c for c in layout["cards"] if keep(c)]
    if zone != 2:
        cards += side_lanes(cards)
    wide = [c for c in cards if not c["flat"] and c["w"] >= ZAB["StripWidth"]]
    rest = [c for c in cards if not (not c["flat"] and c["w"] >= ZAB["StripWidth"])]
    tracks = []
    groups = {}
    for c in wide:
        groups.setdefault(round(c["z"]), []).append(c)
    for key in sorted(groups, reverse=True):
        g = sorted(groups[key], key=lambda c: c["x"])
        if len(g) > 1 and g[0]["image"] == g[-1]["image"] and g[0]["mirror"] == g[-1]["mirror"]:
            g = g[:-1]
        step = (g[-1]["x"] - g[0]["x"]) / (len(g) - 1) if len(g) > 1 else g[0]["w"]
        tracks.append(save_track(g, g[-1]["x"] - g[0]["x"] + step, "strip"))
    near = [c for c in rest if c["z"] < ZAB["NearDepth"]]
    if near:
        start = min(c["x"] for c in near) - 2
        period = max(c["x"] for c in near) - start + 2
        inside = [c for c in rest if start <= c["x"] < start + period]
        tracks.append(save_track(inside, period, "set"))
        # ZoneArtBuilder.Set's alternate: the same set mirrored about the middle of its stretch (positions only), which
        # BackdropStreamer lays for the odd copies
        tracks[-1]["axis"] = start * 2 + period
    return tracks


def side_lanes(cards):
    """ZoneArtBuilder.SideLanes: a mud lane running back from the road wherever the set leaves a gap of 3 m or more
    between buildings with nobody standing in it, at most one every 20 m."""
    if not (ROOT / SIDE_LANE["image"]).exists():
        return []
    blocks = sorted((c["x"] - c["w"] / 2, c["x"] + c["w"] / 2) for c in cards
                    if not c["flat"] and ZAB["LaneBack"] < c["z"] < ZAB["NearDepth"]
                    and (c["layer"] == "Houses" or (c["w"] >= 2.5 and c["h"] >= 2 and c["layer"] not in ("Backdrop", "Plants"))))
    figures = [c for c in cards if not c["flat"] and c["layer"] != "Houses" and c["w"] < 2.5 and ZAB["LaneBack"] < c["z"] < 6
               and c["h"] > 0.5]
    out, last = [], float("-inf")
    for i in range(len(blocks) - 1):
        frm = max(b[1] for b in blocks[:i + 1])
        to = blocks[i + 1][0]
        if to - frm < 3:
            continue
        cx = (frm + to) / 2
        if cx - last < 20 or any(abs(f["x"] - cx) < 1.2 + f["w"] / 2 for f in figures):
            continue
        last = cx
        out.append({"name": f"side_lane_{len(out)}", "image": SIDE_LANE["image"], "layer": "Ground", "x": cx, "y": 0.0,
                    "z": ROAD["back"] - 0.3 + SIDE_LANE["length"] / 2, "w": min(2.6, to - frm - 0.6),
                    "h": SIDE_LANE["length"], "flat": True, "mirror": False, "turn": 0.0, "haze": 0.0,
                    "fade_bottom": 0.0, "fade_sides": 0.0})
    return out


def save_track(cards, period, kind):
    deepest = max(c["z"] for c in cards)
    return {"kind": kind, "cards": cards, "period": max(1.0, period),
            "contentMin": min(c["x"] - c["w"] / 2 for c in cards), "contentMax": max(c["x"] + c["w"] / 2 for c in cards),
            "reach": max(10.0, (ZAB["CameraDistance"] + deepest) * ZAB["ViewSpread"] + 5),
            "room": [room_behind(c, cards) for c in cards]}


def room_behind(card, cards):
    """ArtModels.RoomBehind."""
    room = float("inf")
    if card["flat"]:
        return room
    for o in cards:
        if o is card or o["flat"] or o["z"] <= card["z"] + 0.05:
            continue
        if abs(o["x"] - card["x"]) >= (o["w"] + card["w"]) * 0.5 * 0.8:
            continue
        if o["y"] > card["y"] + card["h"] or o["y"] + o["h"] < card["y"]:
            continue
        room = min(room, o["z"] - card["z"])
    return room


def live_copies(track, cam_x):
    """BackdropStreamer.Refresh: the copies alive for a camera at cam_x."""
    first = math.floor((cam_x - track["reach"] - track["contentMax"]) / track["period"])
    last = math.ceil((cam_x + track["reach"] - track["contentMin"]) / track["period"])
    return first, last


# ====================================================================== Blender
def blender_main():
    import bpy
    import numpy as np
    from mathutils import Matrix, Vector
    from mathutils.bvhtree import BVHTree

    level_no = arg("--level")
    plan_path = pathlib.Path(arg("--plan", f"Assets/ChickenRunner/Art/Levels/level{level_no or 1}.json"))
    if not plan_path.is_absolute():
        plan_path = ROOT / plan_path
    default_out = pathlib.Path(os.environ.get("LEVEL_RENDER_DIR", "/tmp/level_render")) / plan_path.stem
    out = pathlib.Path(arg("--out", str(default_out)))
    out.mkdir(parents=True, exist_ok=True)
    res = tuple(int(v) for v in arg("--res", "1280x720").split("x"))
    aspect = res[0] / res[1]
    samples = int(arg("--samples", "8"))
    threads = int(arg("--threads", os.environ.get("KIT_THREADS", "2") or "2"))
    gap = float(arg("--gap", "10"))
    t_start = time.time()

    L = Level(plan_path)
    log(f"plan {plan_path.name}: {len(L.sections)} sections, {L.start:.0f}..{L.end:.0f} m, "
        f"{sum(len(s['items']) for s in L.sections)} items")
    if arg("--shots"):
        xs = [float(v) for v in arg("--shots").split(",") if v.strip()]
    else:
        x0 = float(arg("--from", "0"))
        x1 = float(arg("--to", str(L.course)))
        every = float(arg("--every", "8"))
        xs = []
        x = x0
        while x <= x1 + 1e-6:
            xs.append(round(x, 3))
            x += every
    intro_level = L.basket is not None
    if intro_level and not arg("--shots") and xs and xs[0] >= 0:
        # the opening is what the player sees first: the tiptoe in from walkFrom, half way, and the lift at 0
        walk = float(L.basket.get("walkFrom") or -4.4)
        xs = [round(walk, 2), round(walk / 2, 2)] + xs

    run_speed = zone_run_speed(L.zone)

    def shot_state(x):
        """Who stands where for a shot with the kid at x: the basket intro (close framing) at x <= 0 in a level that
        opens with one; the Ready state (kid idle, the view pulled back to show the rooster) at x = 0 in any other;
        else the chase."""
        intro = intro_level and x <= 1e-6
        ready = not intro_level and abs(x) < 1e-6
        if intro:
            kid_y, clip, frame = 0.0, "Idle", 1
            rx = L.basket["x"] if L.basket else ROOSTER_UNDER_BASKET
            ry, rclip, rframe = 0.0, "Idle", 1
        else:
            kid_y, clip, frame = support(x, L.surf), ("Idle" if ready else "Run"), (1 if ready else KID_RUN_FRAME)
            if in_hole(x, L.surf) and kid_y < 0:
                clip = "Wade"            # KidModelVisual: on the canal's bed, in its water
            rx = x + gap
            L.rooster_surf = (L.beds + L.rooster_beds, L.holes)
            ry, rclip = rooster_at(rx, L.hops, L.rooster_surf)
            rframe = ROOSTER_RUN_FRAME
        cam = frame_camera(x, kid_y, rx - x, aspect, run_speed, establishing=ready)
        return {"x": x, "intro": intro, "ready": ready, "kid": (x, kid_y, clip, frame),
                "rooster": (rx, ry, rclip, rframe), "cam": cam, "rooster_x": rx}

    # scenery for every camera the game could have on this course (so the checks see all of it)
    cams = [frame_camera(x, 0, gap, aspect, run_speed)["pos"][0] for x in (L.start, L.end)]
    cams += [shot_state(x)["cam"]["pos"][0] for x in xs]
    L.scenery_recs(min(cams) - 2, max(cams) + 2)
    log(f"{len(L.recs)} visuals ({sum(1 for r in L.recs if r.src == 'scenery')} scenery copies)")

    # ------------------------------------------------------------------ scene and render settings
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 8
    for k in ("diffuse_bounces", "glossy_bounces", "transmission_bounces", "volume_bounces"):
        setattr(scene.cycles, k, 0)
    scene.cycles.transparent_max_bounces = 64
    scene.render.threads_mode = "FIXED"
    scene.render.threads = threads
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.use_persistent_data = True
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    haze_lin = lin(L.haze_srgb)
    world = bpy.data.worlds.new("sky")
    scene.world = world
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = haze_lin
    bg.inputs["Strength"].default_value = 1.0
    coll = bpy.data.collections.new("level")
    scene.collection.children.link(coll)
    lib_coll = bpy.data.collections.new("lib")
    scene.collection.children.link(lib_coll)
    bpy.context.view_layer.layer_collection.children["lib"].exclude = True

    # ------------------------------------------------------------------ materials
    class Nodes:
        def __init__(self, mat):
            self.nt = mat.node_tree
            for n in list(self.nt.nodes):
                self.nt.nodes.remove(n)
            self.out = self.new("ShaderNodeOutputMaterial")

        def new(self, kind, **props):
            n = self.nt.nodes.new(kind)
            for k, v in props.items():
                setattr(n, k, v)
            return n

        def feed(self, sock, v):
            if isinstance(v, bpy.types.NodeSocket):
                self.nt.links.new(v, sock)
            else:
                sock.default_value = v

        def math(self, op, a, b=0.0, c=None, clamp=False):
            n = self.new("ShaderNodeMath", operation=op, use_clamp=clamp)
            self.feed(n.inputs[0], a)
            self.feed(n.inputs[1], b)
            if c is not None:
                self.feed(n.inputs[2], c)
            return n.outputs[0]

        def vmath(self, op, a, b=None, scale=None):
            n = self.new("ShaderNodeVectorMath", operation=op)
            self.feed(n.inputs[0], a)
            if b is not None:
                self.feed(n.inputs[1], b)
            if scale is not None:
                self.feed(n.inputs["Scale"], scale)
            return n

        def smooth(self, v, lo, hi):
            n = self.new("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP", clamp=True)
            self.feed(n.inputs["Value"], v)
            self.feed(n.inputs["From Min"], lo)
            self.feed(n.inputs["From Max"], hi)
            return n.outputs["Result"]

        def mix(self, fac, a, b, blend="MIX"):
            n = self.new("ShaderNodeMix", data_type="RGBA", blend_type=blend)
            self.feed(n.inputs["Factor"], fac)
            self.feed(n.inputs["A"], a)
            self.feed(n.inputs["B"], b)
            return n.outputs["Result"]

        def mix_shader(self, fac, a, b):
            n = self.new("ShaderNodeMixShader")
            self.feed(n.inputs[0], fac)
            self.feed(n.inputs[1], a)
            self.feed(n.inputs[2], b)
            return n.outputs[0]

        def emit(self, colour):
            n = self.new("ShaderNodeEmission")
            self.feed(n.inputs["Color"], colour)
            n.inputs["Strength"].default_value = 1.0
            return n.outputs[0]

        def transparent(self):
            return self.new("ShaderNodeBsdfTransparent").outputs[0]

        def finish(self, shader):
            self.nt.links.new(shader, self.out.inputs["Surface"])

    LIGHT_B = Vector((LIGHT[0], LIGHT[2], LIGHT[1])).normalized()
    MATS = {}
    IMAGES = {}

    def image(path):
        path = pathlib.Path(path)
        if path not in IMAGES:
            IMAGES[path] = bpy.data.images.load(str(path), check_existing=True) if path.exists() else None
        return IMAGES[path]

    def toon(key, img, colour, shadow, threshold, softness, gloss=0.0, haze=0.0, cutout=False, cull=True,
             extension="REPEAT"):
        """ChickenRunner/Toon: the painting in two tones split by the fixed light, culled backfaces, haze."""
        key = f"toon|{key}|h{haze:.2f}"
        if key in MATS:
            return MATS[key]
        m = bpy.data.materials.new(key)
        N = Nodes(m)
        geo = N.new("ShaderNodeNewGeometry")
        alpha = None
        if img is not None:
            tex = N.new("ShaderNodeTexImage", extension=extension, interpolation="Linear")
            tex.image = img
            base, alpha = tex.outputs["Color"], tex.outputs["Alpha"]
        else:
            rgb = N.new("ShaderNodeRGB")
            rgb.outputs[0].default_value = colour
            base = rgb.outputs[0]
        # Cycles turns a backface's normal toward the camera; the game lights both sides of a card with its own normal
        sign = N.math("MULTIPLY_ADD", geo.outputs["Backfacing"], -2.0, 1.0)
        n = N.vmath("SCALE", geo.outputs["Normal"], scale=sign).outputs["Vector"]
        d = N.vmath("DOT_PRODUCT", n, tuple(LIGHT_B)).outputs["Value"]
        lit = N.smooth(d, threshold - softness, threshold + softness)
        shaded = N.mix(1.0, base, tuple(shadow) + (1.0,), "MULTIPLY")
        c = N.mix(lit, shaded, base)
        if gloss > 0:
            half = N.vmath("NORMALIZE", N.vmath("ADD", tuple(LIGHT_B), geo.outputs["Incoming"]).outputs["Vector"])
            spec = N.smooth(N.vmath("DOT_PRODUCT", n, half.outputs["Vector"]).outputs["Value"], 0.93, 0.96)
            c = N.mix(N.math("MULTIPLY", spec, gloss * 0.9), c, (1, 1, 1, 1))
        if haze > 0:
            c = N.mix(haze, c, haze_lin)
        sh = N.emit(c)
        if cull:
            sh = N.mix_shader(geo.outputs["Backfacing"], sh, N.transparent())
        if cutout and alpha is not None:
            sh = N.mix_shader(N.math("GREATER_THAN", alpha, 0.5), N.transparent(), sh)
        N.finish(sh)
        MATS[key] = m
        return m

    def ink(haze=0.0):
        """The outline pass: the shell's far side, past the silhouette, in the outline colour (hazed)."""
        key = f"ink|h{haze:.2f}"
        if key in MATS:
            return MATS[key]
        m = bpy.data.materials.new(key)
        N = Nodes(m)
        geo = N.new("ShaderNodeNewGeometry")
        col = tuple(a + (b - a) * haze for a, b in zip(lin(OUTLINE_COLOUR), haze_lin))
        N.finish(N.mix_shader(geo.outputs["Backfacing"], N.emit(col), N.transparent()))
        MATS[key] = m
        return m

    def card_material(path, haze=0.0, fade_bottom=0.0, fade_sides=0.0):
        """ChickenRunner/PaintedCard: the art unlit, alpha-blended, hazed, optionally faded at its foot and sides."""
        haze = round(haze * 20) / 20
        key = f"card|{path}|h{haze:.2f}|b{fade_bottom:.2f}|s{fade_sides:.2f}"
        if key in MATS:
            return MATS[key]
        m = bpy.data.materials.new(key)
        N = Nodes(m)
        uv = N.new("ShaderNodeTexCoord").outputs["UV"]
        tex = N.new("ShaderNodeTexImage", extension="EXTEND", interpolation="Linear")
        tex.image = image(path)
        N.feed(tex.inputs[0], uv)
        alpha = tex.outputs["Alpha"]
        if fade_bottom > 0 or fade_sides > 0:
            sep = N.new("ShaderNodeSeparateXYZ")
            N.feed(sep.inputs[0], uv)
            if fade_bottom > 0:
                alpha = N.math("MULTIPLY", alpha, N.smooth(sep.outputs["Y"], 0.0, fade_bottom))
            if fade_sides > 0:
                edge = N.math("MINIMUM", sep.outputs["X"], N.math("SUBTRACT", 1.0, sep.outputs["X"]))
                alpha = N.math("MULTIPLY", alpha, N.smooth(edge, 0.0, fade_sides))
        c = N.mix(haze, tex.outputs["Color"], haze_lin) if haze > 0 else tex.outputs["Color"]
        N.finish(N.mix_shader(alpha, N.transparent(), N.emit(c)))
        MATS[key] = m
        return m

    def ground_material(name, path, tile, tint, drift, haze_from, haze_to, far=None, far_tile=6.0, band_front=-40.0,
                        band_back=1.8, band_soft=0.5, road=None):
        """ChickenRunner/PaintedGround, node for node (with zone 2's field texture away from the lane band)."""
        m = bpy.data.materials.new(name)
        N = Nodes(m)
        pos = N.new("ShaderNodeSeparateXYZ")
        N.feed(pos.inputs[0], N.new("ShaderNodeNewGeometry").outputs["Position"])
        px, pz = pos.outputs["X"], pos.outputs["Y"]          # Unity's world x and z

        def sample(uu, vv, pth):
            vec = N.new("ShaderNodeCombineXYZ")
            N.feed(vec.inputs[0], uu)
            N.feed(vec.inputs[1], vv)
            tex = N.new("ShaderNodeTexImage", extension="REPEAT", interpolation="Linear")
            tex.image = image(pth)
            N.feed(tex.inputs[0], vec.outputs[0])
            return tex.outputs["Color"]

        w1 = N.math("SINE", N.math("ADD", N.math("MULTIPLY", px, 0.21),
                                    N.math("MULTIPLY", N.math("SINE", N.math("MULTIPLY", pz, 0.17)), 2.3)))
        w2 = N.math("SINE", N.math("ADD", N.math("MULTIPLY", pz, 0.13), N.math("MULTIPLY", px, 0.05)))
        mixer = N.smooth(N.math("MULTIPLY_ADD", N.math("MULTIPLY", w1, w2), 0.5, 0.5), 0.25, 0.75)

        def tiled(pth, t):
            uu, vv = N.math("DIVIDE", px, t), N.math("DIVIDE", pz, t)
            a_ = sample(uu, vv, pth)
            tu = N.math("MULTIPLY_ADD", N.math("SUBTRACT", N.math("MULTIPLY", uu, 0.8), N.math("MULTIPLY", vv, 0.6)), 0.63, 0.37)
            tv = N.math("MULTIPLY_ADD", N.math("ADD", N.math("MULTIPLY", uu, 0.6), N.math("MULTIPLY", vv, 0.8)), 0.63, 0.37)
            return N.mix(mixer, a_, sample(tu, tv, pth))
        c = tiled(path, tile)
        d1 = N.math("SINE", N.math("ADD", N.math("MULTIPLY", px, 0.09), N.math("MULTIPLY", pz, 0.05)))
        d2 = N.math("SINE", N.math("ADD", N.math("SUBTRACT", N.math("MULTIPLY", px, 0.031), N.math("MULTIPLY", pz, 0.11)), 1.7))
        dd = N.math("MULTIPLY", d1, d2)
        k = N.math("MULTIPLY_ADD", dd, drift, 1.0)
        mul = N.new("ShaderNodeVectorMath", operation="SCALE")
        N.feed(mul.inputs[0], c)
        N.feed(mul.inputs["Scale"], k)
        c = mul.outputs["Vector"]
        if far is not None:
            band = N.math("MULTIPLY", N.smooth(pz, band_front - band_soft, band_front),
                          N.math("SUBTRACT", 1.0, N.smooth(pz, band_back, band_back + band_soft)))
            c = N.mix(band, tiled(far, far_tile), c)
        if road is not None:
            # GameBuilder.ZoneGround's road: its own tile across its width, its edges wandering and fading into the earth
            def wave(a, b, c_, d_):
                return N.math("MULTIPLY_ADD", N.math("ADD", N.math("MULTIPLY", N.math("SINE", N.math("MULTIPLY_ADD", px, a, b)), 0.6),
                                                     N.math("MULTIPLY", N.math("SINE", N.math("MULTIPLY_ADD", px, c_, d_)), 0.4)),
                              ROAD["wave"], 0.0)
            front = N.math("ADD", wave(1.3, 0.0, 0.47, 1.1), ROAD["front"])
            back = N.math("ADD", wave(1.1, 2.0, 0.53, 0.3), ROAD["back"])
            soft = ROAD["soft"]
            mask = N.math("MULTIPLY", N.smooth(pz, N.math("SUBTRACT", front, soft), N.math("ADD", front, soft)),
                          N.math("SUBTRACT", 1.0, N.smooth(pz, N.math("SUBTRACT", back, soft), N.math("ADD", back, soft))))
            rv = N.math("DIVIDE", N.math("SUBTRACT", pz, ROAD["front"]), max(0.01, ROAD["back"] - ROAD["front"]), clamp=True)
            r = sample(N.math("DIVIDE", px, ROAD["tile"]), rv, road)
            rk = N.new("ShaderNodeVectorMath", operation="SCALE")
            N.feed(rk.inputs[0], r)
            N.feed(rk.inputs["Scale"], N.math("MULTIPLY_ADD", dd, 0.5 * drift, 1.0))
            c = N.mix(mask, c, rk.outputs["Vector"])
        c = N.mix(1.0, c, lin(tint), "MULTIPLY")
        hz = N.math("POWER", N.math("DIVIDE", N.math("SUBTRACT", pz, haze_from), max(0.01, haze_to - haze_from),
                                    clamp=True), 0.85)
        c = N.mix(hz, c, haze_lin)
        N.finish(N.emit(c))
        return m

    # ------------------------------------------------------------------ the art, imported once
    class PartLib:
        def __init__(self, mesh, base, leaves, src_mats, ink_slot, img=None):
            self.mesh, self.base, self.leaves, self.src_mats, self.ink_slot = mesh, base, leaves, src_mats, ink_slot
            self.img = img               # leaves: the cut-out texture's alpha, for rays
            co = np.empty(len(mesh.vertices) * 3)
            mesh.vertices.foreach_get("co", co)
            self.co = co.reshape(-1, 3)
            self.lo, self.hi = (self.co.min(0), self.co.max(0)) if len(self.co) else (np.zeros(3), np.zeros(3))
            self._bvh = None
            self._uv = None

        def bvh(self):
            if self._bvh is None:
                self._bvh = BVHTree.FromPolygons([tuple(c) for c in self.co], [tuple(p.vertices) for p in self.mesh.polygons])
            return self._bvh

        def uv_at(self, poly, p):
            """The texture coordinate at local point p on polygon `poly` (a triangle fan, barycentric)."""
            if self._uv is None:
                uvl = self.mesh.uv_layers.active
                self._uv = [([self.mesh.loops[i].vertex_index for i in pl.loop_indices],
                             [tuple(uvl.data[i].uv) for i in pl.loop_indices]) for pl in self.mesh.polygons] if uvl else []
            if not self._uv:
                return None
            vs, uvs = self._uv[poly]
            P = [Vector(self.co[i]) for i in vs]
            for t in range(1, len(P) - 1):
                a, b, c = P[0], P[t], P[t + 1]
                v0, v1, v2 = b - a, c - a, p - a
                d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
                d20, d21 = v2.dot(v0), v2.dot(v1)
                den = d00 * d11 - d01 * d01
                if abs(den) < 1e-14:
                    continue
                bv = (d11 * d20 - d01 * d21) / den
                bw = (d00 * d21 - d01 * d20) / den
                if bv >= -1e-3 and bw >= -1e-3 and bv + bw <= 1 + 1e-3:
                    ua, ub, uc = uvs[0], uvs[t], uvs[t + 1]
                    bu = 1 - bv - bw
                    return (bu * ua[0] + bv * ub[0] + bw * uc[0], bu * ua[1] + bv * ub[1] + bw * uc[1])
            return None

    LIB = {}
    INK_PLACEHOLDER = bpy.data.materials.new("ink_placeholder")

    def closed_share(mesh):
        """The share of edges with exactly two faces (1.0: a closed surface, where in and out mean something)."""
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        n = len(bm.edges)
        share = sum(1 for e in bm.edges if e.is_manifold) / n if n else 0.0
        bm.free()
        return share

    def inside_out(volume, lo, hi, closed=1.0):
        """Closed, of some size, and a clearly negative volume for it (an ellipsoid fills about half its box)."""
        box = float(np.prod(np.asarray(hi) - np.asarray(lo)))
        return closed > 0.9 and box > 1e-7 and volume < -0.1 * box

    def signed_volume(mesh):
        """Positive when the faces wind outward. Negative: the normals point in, and the game's back-face culling shows
        the inside of the far half while the outline shell (pushed along the normals, drawn on its back faces) covers it."""
        mesh.calc_loop_triangles()
        n = len(mesh.loop_triangles)
        if not n:
            return 0.0
        tri = np.empty(n * 3, dtype=np.int64)
        mesh.loop_triangles.foreach_get("vertices", tri)
        co = np.empty(len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        t = co[tri.reshape(-1, 3)]
        return float(np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6)

    def import_fbx(path):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(path))
        new = [o for o in bpy.data.objects if o not in before]
        bpy.context.view_layer.update()
        return new

    def tex_of(mat):
        if mat is None or mat.node_tree is None:
            return None
        for n in mat.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image is not None:
                return n.image
        return None

    def base_colour(mat):
        if mat is None or mat.node_tree is None:
            return (0.8, 0.8, 0.8, 1)
        p = mat.node_tree.nodes.get("Principled BSDF")
        return tuple(p.inputs["Base Color"].default_value) if p else (0.8, 0.8, 0.8, 1)

    def library(entry):
        name = entry["name"]
        if name in LIB:
            return LIB[name]
        folder = ART / "Models" / entry["folder"]
        new = import_fbx(folder / f"{name}.fbx")
        parts = []
        for o in new:
            if o.type != "MESH":
                continue
            me = o.data
            me.use_fake_user = True
            mats = [s.material for s in o.material_slots]
            leaves = o.name.endswith("_leaves") or any(m is not None and m.name.endswith("_Leaves") for m in mats)
            src = []
            for m in mats:
                img = tex_of(m)
                if img is None:
                    for p in ([folder / f"{name}_leaves.png"] if leaves else [folder / f"{name}.jpg", folder / f"{name}.png"]):
                        if p.exists():
                            img = image(p)
                            break
                src.append((m.name if m else "none", img, base_colour(m)))
            ink_slot = None
            if not leaves:
                ink_slot = len(me.materials)
                for _ in range(max(1, len(me.materials))):
                    me.materials.append(INK_PLACEHOLDER)
            info = img_info(folder / f"{name}_leaves.png") if leaves else None
            parts.append(PartLib(me, o.matrix_world.copy(), leaves, src, ink_slot, info))
            parts[-1].volume = 0.0 if leaves else signed_volume(me) * (1 if o.matrix_world.determinant() > 0 else -1)
            parts[-1].closed = 0.0 if leaves else closed_share(me)
        for o in new:
            bpy.data.objects.remove(o)
        LIB[name] = parts
        return parts

    def matrix_np(M):
        return np.array([list(r) for r in M])

    def aabb_of(parts_world):
        pts = []
        for part, Mw in parts_world:
            lo, hi = part.lo, part.hi
            c = np.array([[x, y, z, 1] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
            pts.append((c @ matrix_np(Mw).T)[:, :3])
        P = np.vstack(pts)
        return np.array([P.min(0), P.max(0)])

    def mscale(M):
        return float(np.mean([Vector(M.col[i][:3]).length for i in range(3)]))

    # ------------------------------------------------------------------ placing: ArtModels.Place / ArtAssets.Card
    def model_matrix(e, x, y, z, w, h, mirror, flat, turn, room):
        sx, sy = w / e["width"], h / e["height"]
        sz = (sx + sy) * 0.5
        building = e.get("kind") == "building"
        reach = e["depth"] * sz * (1.0 if building or (e.get("oblique") or 0) > 0 else 0.5)
        if not flat and reach > room - 0.1:
            sz *= max(0.15, (room - 0.1) / reach)
        S = Matrix.Diagonal((-sx if mirror else sx, sz, sy, 1.0))
        R = Matrix.Rotation(math.radians(turn), 4, "Z")
        if flat:
            up = Matrix.Rotation(math.radians(turn), 3, "Z") @ Vector((0, 1, 0))
            T = Matrix.Translation((x, z, y + 0.002 + e["depth"] * sz * 0.5)) @ Matrix.Translation(-up * h * 0.5)
            return T @ R @ Matrix.Rotation(math.radians(-90), 4, "X") @ S
        lift = min(max(e.get("lift") or 0.0, 0.0), 0.1)
        return Matrix.Translation((x, z, y - lift * sy)) @ R @ S

    def card_matrix(x, y, z, w, h, mirror, flat, turn):
        S = Matrix.Diagonal((-w if mirror else w, 1.0, h, 1.0))
        R = Matrix.Rotation(math.radians(turn), 4, "Z")
        if flat:
            return Matrix.Translation((x, z, y + 0.002)) @ R @ Matrix.Rotation(math.radians(-90), 4, "X") @ S
        return Matrix.Translation((x, z, y + h * 0.5)) @ R @ S

    quad = bpy.data.meshes.new("card_quad")
    quad.from_pydata([(-0.5, 0, -0.5), (0.5, 0, -0.5), (0.5, 0, 0.5), (-0.5, 0, 0.5)], [], [(0, 1, 2, 3)])
    uvl = quad.uv_layers.new(name="UV")
    for i, uv in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uvl.data[i].uv = uv
    quad.use_fake_user = True
    disc = bpy.data.meshes.new("water_disc")
    n_seg = 40
    disc.from_pydata([(0.5 * math.cos(2 * math.pi * i / n_seg), 0.5 * math.sin(2 * math.pi * i / n_seg), 0.0)
                      for i in range(n_seg)], [], [tuple(range(n_seg))])
    disc.use_fake_user = True
    flat_quad = bpy.data.meshes.new("water_rect")
    flat_quad.from_pydata([(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)], [], [(0, 1, 2, 3)])
    flat_quad.use_fake_user = True
    cube = bpy.data.meshes.new("box")
    cube.from_pydata([(x, y, z) for x in (-0.5, 0.5) for y in (-0.5, 0.5) for z in (-0.5, 0.5)], [],
                     [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)])
    cube.materials.append(None)
    cube.use_fake_user = True
    _sun = Matrix.Rotation(math.radians(-35), 3, "Y") @ Matrix.Rotation(math.radians(38), 3, "X") @ Vector((0, 0, 1))
    SUN_B = Vector((-_sun.x, -_sun.z, -_sun.y)).normalized()      # toward the sun, Blender axes

    def new_object(name, mesh):
        ob = bpy.data.objects.new(name, mesh)
        coll.objects.link(ob)
        ob.hide_viewport = True
        ob.hide_render = True
        return ob

    def build_model(rec, M):
        world = []
        for part in library(rec.entry):
            Mw = M @ part.base
            ob = new_object(rec.name, part.mesh)
            ob.matrix_world = Mw
            for i, (mname, img, col) in enumerate(part.src_mats):
                slot = ob.material_slots[i]
                slot.link = "OBJECT"
                cards = part.leaves or mname.endswith("_Leaves")
                slot.material = toon(f"{rec.entry['name']}|{mname}", img, col, SCENERY_TOON["shadow"],
                                     SCENERY_TOON["threshold"], SCENERY_TOON["softness"], haze=round(rec.haze * 20) / 20,
                                     cutout=cards, cull=not cards, extension="EXTEND" if cards else "REPEAT")
            world.append((part, Mw))
            rec.parts.append((part, ob, Mw, Mw.inverted_safe()))
            rec.objs.append(ob)
        rec.aabb = aabb_of(world)
        tiny_all = False
        for part, ob, Mw, _ in rec.parts:
            if part.ink_slot is None or rec.flat:
                continue
            lo_hi = aabb_of([(part, Mw)])
            tiny = bool(np.all(lo_hi[1] - lo_hi[0] < 0.02))
            tiny_all = tiny_all or tiny
            if tiny:
                continue
            mod = ob.modifiers.new("ink", "SOLIDIFY")
            mod.thickness = rec.outline / max(1e-4, mscale(Mw))
            mod.offset = 1.0
            mod.use_flip_normals = True
            mod.material_offset = part.ink_slot
            mod.material_offset_rim = part.ink_slot
            for i in range(part.ink_slot, len(ob.material_slots)):
                ob.material_slots[i].link = "OBJECT"
                ob.material_slots[i].material = ink(round(rec.haze * 20) / 20)

    def build_card(rec, M):
        ob = new_object(rec.name, quad)
        ob.matrix_world = M
        c = rec.card or {}
        mat = card_material(rec.image, rec.haze, c.get("fade_bottom", 0.0) or 0.0, c.get("fade_sides", 0.0) or 0.0)
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = mat
        rec.parts.append((None, ob, M, M.inverted_safe()))
        rec.objs.append(ob)
        corners = np.array([[(M @ Vector((sx, 0, sz)))[i] for i in range(3)] for sx in (-0.5, 0.5) for sz in (-0.5, 0.5)])
        rec.aabb = np.array([corners.min(0), corners.max(0)])
        rec.info = img_info(rec.image)

    quad.materials.append(None)

    # pickups and characters: GameBuilder.Characters
    PICK = {}

    def pickup_parts(name):
        if name in PICK:
            return PICK[name]
        new = import_fbx(ART / "Characters" / f"{name}.fbx")
        meshes = [o for o in new if o.type == "MESH"]
        import bmesh
        bm = bmesh.new()
        mats, src = [], []
        for o in meshes:
            tmp = bmesh.new()
            tmp.from_mesh(o.data)
            tmp.transform(o.matrix_world)
            offset = len(mats)
            for s in o.material_slots:
                mats.append(s.material)
                src.append((s.material.name if s.material else "none", tex_of(s.material), base_colour(s.material)))
            for f in tmp.faces:
                f.material_index += offset
            me_tmp = bpy.data.meshes.new("tmp")
            tmp.to_mesh(me_tmp)
            bm.from_mesh(me_tmp)
            bpy.data.meshes.remove(me_tmp)
            tmp.free()
        me = bpy.data.meshes.new(f"pickup_{name}")
        bm.to_mesh(me)
        bm.free()
        for m in mats:
            me.materials.append(m)
        n = len(mats)
        for _ in range(n):
            me.materials.append(INK_PLACEHOLDER)
        me.use_fake_user = True
        def _box(o):
            co = np.array([tuple(o.matrix_world @ v.co) for v in o.data.vertices]) if len(o.data.vertices) else np.zeros((1, 3))
            return co.min(0), co.max(0)
        volumes = [(o.name, signed_volume(o.data) * (1 if o.matrix_world.determinant() > 0 else -1), *_box(o),
                    closed_share(o.data)) for o in meshes]
        for o in new:
            bpy.data.objects.remove(o)
        part = PartLib(me, Matrix.Identity(4), False, src, n)
        part.volumes = volumes
        PICK[name] = part
        return part

    def char_toon(src_name, img, col, outline_kind):
        n = src_name
        gloss = 0.5 if ("Gold" in n or "Silver" in n) else 0.6 if ("Chilli" in n or "Mango" in n) else \
            0.2 if ("Red" in n or "Tail" in n) else 0.0
        shadow = (0.78, 0.66, 0.7) if ("Skin" in n or "Face" in n) else (0.68, 0.62, 0.78)
        return toon(f"char|{n}", img, col if img is None else (1, 1, 1, 1), shadow, CHAR_TOON["threshold"],
                    CHAR_TOON["softness"], gloss=gloss)

    def add_ink(ob, slot, width, scale=1.0):
        mod = ob.modifiers.new("ink", "SOLIDIFY")
        mod.thickness = width / scale
        mod.offset = 1.0
        mod.use_flip_normals = True
        mod.material_offset = slot
        mod.material_offset_rim = slot
        for i in range(slot, len(ob.material_slots)):
            ob.material_slots[i].link = "OBJECT"
            ob.material_slots[i].material = ink(0.0)

    def build_pickup(rec):
        part = pickup_parts(rec.piece)
        M = (Matrix.Translation((rec.x, rec.z, rec.y)) @ Matrix.Rotation(math.radians(-rec.spin), 4, "Z")
             @ Matrix.Rotation(math.radians(-rec.tilt), 4, "Y") @ Matrix.Rotation(math.pi, 4, "Z"))
        ob = new_object(rec.name, part.mesh)
        ob.matrix_world = M
        for i, (mname, img, col) in enumerate(part.src_mats):
            ob.material_slots[i].link = "OBJECT"
            ob.material_slots[i].material = char_toon(mname, img, col, "pickup")
        add_ink(ob, part.ink_slot, 0.003)
        rec.parts.append((part, ob, M, M.inverted_safe()))
        rec.objs.append(ob)
        rec.aabb = aabb_of([(part, M)])

    def build_water(rec):
        top = 0.008 if rec.shape == "ellipse" else rec.y
        M = Matrix.Translation((rec.x, rec.z, top)) @ Matrix.Diagonal((rec.w, rec.d, 1.0, 1.0))
        ob = new_object(rec.name, disc if rec.shape == "ellipse" else flat_quad)
        ob.matrix_world = M
        rec.parts.append((None, ob, M, M.inverted_safe()))
        rec.objs.append(ob)
        rec.top = top
        rec.aabb = np.array([[rec.x - rec.w / 2, rec.z - rec.d / 2, top - 0.008], [rec.x + rec.w / 2, rec.z + rec.d / 2, top]])

    PRIMS = {}

    def prim_material(colour):
        """The grey-box material (Standard, lit by the scene's sun at Euler(38, -35, 0) and the flat ambient)."""
        key = tuple(round(c, 3) for c in colour)
        if key in PRIMS:
            return PRIMS[key]
        m = bpy.data.materials.new(f"prim{key}")
        N = Nodes(m)
        geo = N.new("ShaderNodeNewGeometry")
        d = N.vmath("DOT_PRODUCT", geo.outputs["Normal"], tuple(SUN_B)).outputs["Value"]
        lam = N.math("MAXIMUM", d, 0.0)
        amb = lin((0.66, 0.6, 0.54))
        sun = lin((1.0, 0.9, 0.75))
        light = N.new("ShaderNodeVectorMath", operation="MULTIPLY_ADD")
        N.feed(light.inputs[0], tuple(c * 1.1 for c in sun[:3]))
        N.feed(light.inputs[1], N.new("ShaderNodeCombineXYZ").outputs[0])
        comb = light.inputs[1].links[0].from_node
        for i in range(3):
            N.feed(comb.inputs[i], lam)
        N.feed(light.inputs[2], tuple(amb[:3]))
        c = N.mix(1.0, lin(colour), light.outputs["Vector"], "MULTIPLY")
        N.finish(N.emit(c))
        PRIMS[key] = m
        return m

    def build_box(rec):
        M = Matrix.Translation((rec.x, rec.z, rec.y + rec.h / 2)) @ Matrix.Diagonal((rec.w, rec.d, rec.h, 1.0))
        ob = new_object(rec.name, cube)
        ob.matrix_world = M
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = STONE_MAT if (rec.piece in STONE_BOXES and STONE_MAT) else prim_material(rec.color)
        rec.parts.append((None, ob, M, M.inverted_safe()))
        rec.objs.append(ob)
        rec.aabb = np.array([[rec.x - rec.w / 2, rec.z - rec.d / 2, rec.y], [rec.x + rec.w / 2, rec.z + rec.d / 2, rec.y + rec.h]])

    def build_ladder(rec):
        """ArtModels.Stand: the model at its own size, its foot at the visual, leaning along the line to its head."""
        foot = Vector((rec.x, rec.z, rec.y))
        head = Vector((rec.head[0], rec.head[2], rec.head[1]))
        R = Vector((0, 0, 1)).rotation_difference(head - foot).to_matrix().to_4x4()
        M = Matrix.Translation(foot) @ R @ Matrix.Diagonal((getattr(rec, "stand_scale_x", 1.0), 1.0, 1.0, 1.0))
        rec.M = M
        build_model(rec, M)

    earth = cutout("plain_red_earth") or cutout("ground_earth_lane")
    road_tex = cutout(ROAD["tiles"][min(max(L.zone, 1), 3) - 1])
    if L.zone == 2 and cutout("paddy_water"):
        # GameBuilder.ZoneGround: the bund's earth along the lane, paddy water beyond it, a longer haze; the zone's road
        GROUND_MAT = ground_material("ground", earth, 3.5, (1, 1, 1), 0.14, 10.0, 55.0, far=cutout("paddy_water"),
                                     band_back=ROAD["back"] + 0.15, road=road_tex)
    else:
        GROUND_MAT = ground_material("ground", earth, 3.5, (1, 1, 1), 0.14, 6.0, 40.0, road=road_tex)
    water_tex = cutout("canal_water")
    # GameBuilder: the canals' water is the light painted tile (white tint), else the old dark one tinted lighter
    light_water = cutout("canal_water_light")
    WATER_MAT = (ground_material("water", light_water or water_tex, 2.5, (1.0, 1.0, 1.0) if light_water else (0.82, 0.92, 1.0),
                                 0.05, 6.0, 40.0) if (light_water or water_tex) else GROUND_MAT)
    # ... and their granite kerbs (Kit.Canal's "Bank" boxes), the granite tile through the ground shader
    STONE_MAT = ground_material("stone", cutout("granite"), 1.2, (1.0, 0.97, 0.92), 0.05, 6.0, 40.0) if cutout("granite") else None
    # GameBuilder: the hand pump's puddle is the same water, lighter and bluer, in a smaller tile
    PUDDLE_MAT = ground_material("puddle", water_tex, 1.2, (0.95, 1.05, 1.25), 0.03, 6.0, 40.0) if water_tex else GROUND_MAT
    disc.materials.append(PUDDLE_MAT)
    flat_quad.materials.append(WATER_MAT)

    # ------------------------------------------------------------------ build every visual
    t0 = time.time()
    basket_recs = []
    for rec in list(L.recs):
        if rec.mode in ("missing", "hole", "solid"):
            continue
        if rec.mode == "pickup":
            build_pickup(rec)
        elif rec.mode == "water":
            build_water(rec)
        elif rec.mode == "box":
            build_box(rec)
        elif rec.mode == "ladder":
            build_ladder(rec)
        elif rec.mode == "model":
            M = model_matrix(rec.entry, rec.x, rec.y, rec.z, rec.w, rec.h, rec.mirror, rec.flat, rec.turn, rec.room)
            rec.M = M
            build_model(rec, M)
        else:
            M = card_matrix(rec.x, rec.y, rec.z, rec.w, rec.h, rec.mirror, rec.flat, rec.turn)
            rec.M = M
            build_card(rec, M)
        if getattr(rec, "front_at", None) is not None and rec.aabb is not None:
            shift = rec.front_at - float(rec.aabb[0][1])
            if shift > 0:
                T = Matrix.Translation((0.0, shift, 0.0))
                rec.parts = [(pt, ob, T @ Mw, (T @ Mw).inverted_safe()) for pt, ob, Mw, _ in rec.parts]
                for pt, ob, Mw, _ in rec.parts:
                    ob.matrix_world = Mw
                rec.M = T @ rec.M
                rec.aabb = rec.aabb + np.array([0.0, shift, 0.0])
                rec.z += shift
        if rec.role == "basket":
            basket_recs.append(rec)
    # obstacles whose extent the plan does not give: from their placed visuals
    for ob in L.obstacles:
        rs = [r for r in ob["recs"] if r.aabb is not None]
        if not rs:
            rs = [r for r in L.recs if r.item is ob["item"] and r.aabb is not None and r.role not in ("pickup", "decal")]
            ob["recs"] = rs
        if ob["x0"] is None:
            ob["x0"] = min((float(r.aabb[0][0]) for r in rs), default=ob["x"])
            ob["x1"] = max((float(r.aabb[1][0]) for r in rs), default=ob["x"])
    # BasketIntro: down over the rooster in the opening; flung aside for the chase (its far rim the hinge, turned 105
    # degrees about the lane's depth axis, moved 0.35 m on and 1.5 m back)
    for rec in basket_recs:
        rec.state = "intro"
        it = rec.item
        hinge = Vector((it.get("hinge", rec.x + rec.w / 2), 0.0, 0.0))
        T = (Matrix.Translation(hinge + Vector((0.35, 1.5, 0.0))) @ Matrix.Rotation(math.radians(105), 4, "Y")
             @ Matrix.Translation(-hinge))
        tossed = Rec(**{k: v for k, v in rec.__dict__.items() if k not in ("parts", "objs", "aabb", "notes")})
        tossed.parts, tossed.objs, tossed.notes = [], [], []
        tossed.name = rec.name + "/tossed"
        tossed.state = "chase"
        tossed.role = "basket_tossed"
        for part, ob, Mw, _ in rec.parts:
            ob2 = ob.copy()
            coll.objects.link(ob2)
            ob2.matrix_world = T @ Mw
            tossed.parts.append((part, ob2, T @ Mw, (T @ Mw).inverted_safe()))
            tossed.objs.append(ob2)
        pts = [(p, Mw) for p, _, Mw, _ in tossed.parts if p is not None]
        tossed.aabb = aabb_of(pts) if pts else rec.aabb
        L.recs.append(tossed)

    # ground: the chunks' slabs (x from the runway start, z -40..4.5) and the streamer's plane (z 4.4..95)
    def ground_plane(name, x0, x1, z0, z1):
        me = bpy.data.meshes.new(name)
        me.from_pydata([(x0, z0, 0), (x1, z0, 0), (x1, z1, 0), (x0, z1, 0)], [], [(0, 1, 2, 3)])
        me.materials.append(GROUND_MAT)
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
        return ob
    chunk_end = L.end + RUNOUT + 30
    gx = RUNWAY_START
    for h0, h1 in sorted(L.holes) + [(chunk_end, chunk_end)]:
        if h0 > gx:
            ground_plane(f"ground_chunks_{gx:.0f}", gx, h0, KIT_GROUND_FRONT, KIT_GROUND_BACK)
        gx = max(gx, h1)
    for h0, h1 in L.holes:
        # Kit.Canal: no slab over the canal; the slabs' cut ends show as earth walls down to the canal's bed
        me = bpy.data.meshes.new("canal")
        z0, z1, b = KIT_GROUND_FRONT, KIT_GROUND_BACK, CANAL_BED
        me.from_pydata([(h0, z0, 0), (h0, z1, 0), (h0, z1, b), (h0, z0, b), (h1, z0, 0), (h1, z1, 0), (h1, z1, b), (h1, z0, b)],
                       [], [(0, 1, 2, 3), (4, 7, 6, 5), (3, 2, 6, 7)])
        me.materials.append(GROUND_MAT)
        coll.objects.link(bpy.data.objects.new("canal", me))
    ground_plane("ground_backdrop", min(cams) - 260, max(cams) + 260, GROUND_FROM, ZAB["groundTo"])
    GROUND_REGIONS = [(RUNWAY_START, chunk_end, KIT_GROUND_FRONT, KIT_GROUND_BACK),
                      (min(cams) - 260, max(cams) + 260, GROUND_FROM, ZAB["groundTo"])]
    log(f"built {sum(len(r.objs) for r in L.recs)} objects from {len(LIB)} models in {time.time() - t0:.0f} s")

    # ------------------------------------------------------------------ the kid and the rooster
    def stable_copy(src, tmp):
        """A copy of a file another process may be rewriting: wait until it has not changed for a few seconds."""
        for _ in range(60):
            try:
                a = src.stat()
                time.sleep(1.5)
                b = src.stat()
            except OSError:
                time.sleep(5)
                continue
            if a.st_size == b.st_size and a.st_mtime == b.st_mtime and time.time() - b.st_mtime > 3:
                dst = pathlib.Path(tmp) / src.name
                shutil.copy2(src, dst)
                if dst.stat().st_size == b.st_size:
                    return dst
            time.sleep(5)
        raise RuntimeError(f"{src} kept changing")

    def import_character(name):
        src = ART / "Characters" / f"{name}.fbx"
        for attempt in range(10):
            tmp = tempfile.mkdtemp(prefix=f"rl_{name}_")
            new = []
            try:
                fbx = stable_copy(src, tmp)
                painted = src.with_name(f"{name}_painted.png")
                if painted.exists():
                    shutil.copy2(painted, pathlib.Path(tmp) / painted.name)
                before_actions = set(bpy.data.actions)
                new = import_fbx(fbx)
                arm = next((o for o in new if o.type == "ARMATURE"), None)
                body = [o for o in new if o.type == "MESH"]
                acts = {a.name.split("|")[-1]: a for a in bpy.data.actions if a not in before_actions}
                if arm is None or not body or "Run" not in acts:
                    raise RuntimeError(f"incomplete import: armature {arm}, meshes {len(body)}, clips {sorted(acts)}")
                for o in new:
                    for c in list(o.users_collection):
                        c.objects.unlink(o)
                    coll.objects.link(o)
                for ob in body:
                    src_mats = [(s.material.name if s.material else "none", tex_of(s.material), base_colour(s.material))
                                for s in ob.material_slots]
                    n = len(src_mats)
                    for i, (mname, img, col) in enumerate(src_mats):
                        ob.material_slots[i].link = "OBJECT"
                        ob.material_slots[i].material = char_toon(mname, img, col, "char")
                    for _ in range(n):
                        ob.data.materials.append(INK_PLACEHOLDER)
                    add_ink(ob, n, 0.004)
                # PlaceModel's holder: s_facing turns the model (front +Z in Unity, -Y here) to run along +x, 25 degrees
                # toward the camera. It goes on a parent, as in the game: the clips key the rig object's own transform.
                root = bpy.data.objects.new(f"{name}_holder", None)
                coll.objects.link(root)
                for o in new:
                    if o.parent is None:
                        o.parent = root
                        o.matrix_parent_inverse = Matrix.Identity(4)
                log(f"{name}: imported ({len(body)} meshes, clips {', '.join(sorted(acts))})")
                return {"root": root, "arm": arm, "body": body, "acts": acts, "objs": new,
                        "volumes": [(o.name, signed_volume(o.data)) for o in body]}
            except Exception as e:      # noqa: BLE001  (a file half-written by the other exporter)
                log(f"{name}: import failed ({e!r}); retrying in 20 s")
                for o in new:
                    try:
                        bpy.data.objects.remove(o)
                    except ReferenceError:
                        pass
                time.sleep(20)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        log(f"{name}: could not be imported; shots go without it")
        return None

    KID = import_character("Kid")
    ROOSTER = import_character("Rooster")

    def pose(ch, x, y, clip, frame):
        if ch is None:
            return
        ch["root"].matrix_world = Matrix.Translation((x, 0.0, y)) @ Matrix.Rotation(math.radians(180 - FACING), 4, "Z")
        act = ch["acts"].get(clip) or ch["acts"].get("Run")
        ad = ch["arm"].animation_data or ch["arm"].animation_data_create()
        ad.action = act
        if getattr(ad, "action_slot", None) is None and getattr(act, "slots", None):
            ad.action_slot = act.slots[0]
        lo, hi = act.frame_range
        scene.frame_set(int(min(max(frame, lo), hi)))
        ad.action = None            # the pose stays as evaluated, so the other character can be posed on its own frame
        bpy.context.view_layer.update()

    def char_aabb(ch):
        if ch is None:
            return None
        dg = bpy.context.evaluated_depsgraph_get()
        pts = []
        for ob in ch["body"]:
            ev = ob.evaluated_get(dg)
            me = ev.to_mesh()
            co = np.empty(len(me.vertices) * 3)
            me.vertices.foreach_get("co", co)
            co = co.reshape(-1, 3)
            M = matrix_np(ob.matrix_world)
            pts.append(np.c_[co, np.ones(len(co))] @ M.T)
            ev.to_mesh_clear()
        P = np.vstack(pts)[:, :3]
        return np.array([P.min(0), P.max(0)])

    # ------------------------------------------------------------------ cameras and what each one sees
    cam_ob = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    scene.collection.objects.link(cam_ob)
    scene.camera = cam_ob
    cam_ob.data.sensor_fit = "VERTICAL"
    cam_ob.data.angle_y = math.radians(CAMERA["fov"])
    cam_ob.data.clip_start = CAMERA["near"]
    cam_ob.data.clip_end = CAMERA["far"]

    def to_b(p):
        return Vector((p[0], p[2], p[1]))

    def aim(pos_b, target_b):
        cam_ob.location = pos_b
        cam_ob.rotation_euler = (target_b - pos_b).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()

    RECS = [r for r in L.recs if r.objs]
    AABB = np.array([r.aabb for r in RECS])

    def state_mask(st):
        """The game's visibility for a state: the plan's states, the streamer's live copies around the camera."""
        cam_x = st["cam_x"]
        live = [live_copies(tr, cam_x) for tr in L.tracks]
        mask = np.zeros(len(RECS), bool)
        for i, r in enumerate(RECS):
            s = r.state
            if r.track is not None:
                f, l_ = live[r.track[0]]
                ok = f <= r.track[1] <= l_
            elif s == "always":
                ok = True
            elif s == "never":
                ok = False
            elif s == "intro":
                ok = st["intro"]
            elif s == "chase":
                ok = not st["intro"]
            else:
                ok = (not st["intro"]) and st["rooster_x"] >= s[1]
            mask[i] = ok
        return mask

    def frustum_mask(pos_b, rot, vfov, aspect_, margin=1.08):
        R = np.array(rot.to_matrix())
        C = np.array(pos_b)
        lo, hi = AABB[:, 0], AABB[:, 1]
        corners = np.stack([np.stack([np.where(b & 1, hi[:, 0], lo[:, 0]), np.where(b & 2, hi[:, 1], lo[:, 1]),
                                      np.where(b & 4, hi[:, 2], lo[:, 2])], -1) for b in range(8)], 1)
        local = (corners - C) @ R
        depth = -local[..., 2]
        tv = math.tan(vfov / 2) * margin
        th = math.tan(vfov / 2) * aspect_ * margin
        out = (np.all(depth < CAMERA["near"], 1) | np.all(depth > CAMERA["far"], 1)
               | np.all(local[..., 0] > depth * th, 1) | np.all(local[..., 0] < -depth * th, 1)
               | np.all(local[..., 1] > depth * tv, 1) | np.all(local[..., 1] < -depth * tv, 1))
        return ~out

    SHOWN = np.zeros(len(RECS), bool)

    def show(mask):
        changed = np.nonzero(mask != SHOWN)[0]
        for i in changed:
            for ob in RECS[i].objs:
                ob.hide_render = not mask[i]
        SHOWN[:] = mask

    def place_characters(st, visible=True):
        for ch, (x, y, clip, frame) in ((KID, st["kid"]), (ROOSTER, st["rooster"])):
            if ch is None:
                continue
            pose(ch, x, y, clip, frame)
            for o in ch["objs"]:
                o.hide_render = not visible

    def render_to(path):
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)

    # ====================================================================== rays through the placed scene
    def ray_rec(rec, o, d, tmax):
        """The nearest opaque hit of the ray o + t d (world, d unit) on rec, as the game draws it: (t, part) or None."""
        best = None
        for part, ob, Mw, Mi in rec.parts:
            ol = Mi @ o
            dl = (Mi.to_3x3() @ d)
            scale = dl.length
            if scale < 1e-12:
                continue
            dl.normalize()
            if part is None:
                if rec.mode == "card":
                    if abs(dl.y) < 1e-9:
                        continue
                    tl = -ol.y / dl.y
                    if tl <= 1e-6:
                        continue
                    p = ol + dl * tl
                    if abs(p.x) > 0.5 or abs(p.z) > 0.5:
                        continue
                    if rec.info is not None and rec.info.alpha_at(p.x + 0.5, p.z + 0.5) < 0.5:
                        continue
                    t = tl / scale
                elif rec.mode == "water":
                    if abs(dl.z) < 1e-9:
                        continue
                    tl = -ol.z / dl.z
                    p = ol + dl * tl
                    if tl <= 0 or (p.x * p.x + p.y * p.y > 0.25 if rec.shape == "ellipse" else
                                   (abs(p.x) > 0.5 or abs(p.y) > 0.5)):
                        continue
                    t = tl / scale
                elif rec.mode == "box":
                    tn_, tf_ = -1e9, 1e9
                    for a in range(3):
                        if abs(dl[a]) < 1e-12:
                            if abs(ol[a]) > 0.5:
                                tn_ = 1e9
                            continue
                        ta, tb = (-0.5 - ol[a]) / dl[a], (0.5 - ol[a]) / dl[a]
                        tn_, tf_ = max(tn_, min(ta, tb)), min(tf_, max(ta, tb))
                    if tn_ > tf_ or tf_ < 0:
                        continue
                    t = max(tn_, 0.0) / scale
                else:
                    continue
                if t < tmax and (best is None or t < best[0]):
                    best = (t, part)
                continue
            bvh = part.bvh()
            start = ol.copy()
            travelled = 0.0
            for _ in range(32):
                hit = bvh.ray_cast(start, dl)
                if hit[0] is None:
                    break
                loc, nrm, idx, dist = hit
                travelled += dist
                t = travelled / scale
                if t >= tmax or (best is not None and t >= best[0]):
                    break
                opaque = True
                if part.leaves:
                    uv = part.uv_at(idx, loc)
                    opaque = part.img is not None and uv is not None and \
                        part.img.alpha_at(min(max(uv[0], 0.0), 1.0), min(max(uv[1], 0.0), 1.0)) >= 0.5
                elif nrm.dot(dl) > 0:              # the game culls back faces
                    opaque = False
                if opaque:
                    best = (t, part)
                    break
                start = loc + dl * 1e-4
                travelled += 1e-4
        return best

    def ground_hit(o, d):
        if d.z >= -1e-9:
            return None
        t = -o.z / d.z
        p = o + d * t
        if KIT_GROUND_FRONT <= p.y <= KIT_GROUND_BACK and in_hole(p.x, L.surf):
            return (CANAL_BED - o.z) / d.z         # down to the canal's bed
        for x0, x1, z0, z1 in GROUND_REGIONS:
            if x0 <= p.x <= x1 and z0 <= p.y <= z1:
                return t
        return None

    def cast(o, d, cand, tmax=1e9, skip=()):
        """First opaque hit among candidate recs (indices into RECS): (t, rec) or (t, 'ground') or (None, None)."""
        o, d = Vector(o), Vector(d).normalized()
        lo, hi = AABB[cand, 0], AABB[cand, 1]
        with np.errstate(divide="ignore", invalid="ignore"):
            inv = 1.0 / np.array(d)
            t1 = (lo - np.array(o)) * inv
            t2 = (hi - np.array(o)) * inv
        tn = np.nanmax(np.minimum(t1, t2), 1)
        tf = np.nanmin(np.maximum(t1, t2), 1)
        ok = (tf >= np.maximum(tn, 0)) & (tn < tmax)
        order = np.argsort(tn)
        best_t, best = ground_hit(o, d), "ground"
        if best_t is None or best_t > tmax:
            best_t, best = None, None
        for j in order:
            if not ok[j]:
                continue
            if best_t is not None and tn[j] > best_t:
                break
            rec = RECS[cand[j]]
            if rec in skip:
                continue
            h = ray_rec(rec, o, d, best_t if best_t is not None else tmax)
            if h is not None:
                best_t, best = h[0], rec
        return best_t, best

    # ====================================================================== renders
    shots_dir = out / "shots"
    shots_meta = []
    render = not flag("--no-render")
    if render:
        shots_dir.mkdir(exist_ok=True)

    def state_for_shot(x):
        st = shot_state(x)
        st["cam_x"] = st["cam"]["pos"][0]
        return st

    def name_for(x):
        return f"x{x:+07.1f}"

    for i, x in enumerate(xs):
        st = state_for_shot(x)
        pos_b, tgt_b = to_b(st["cam"]["pos"]), to_b(st["cam"]["target"])
        aim(pos_b, tgt_b)
        mask = state_mask(st) & frustum_mask(pos_b, cam_ob.rotation_euler.to_quaternion(), math.radians(CAMERA["fov"]), aspect)
        show(mask)
        place_characters(st)
        meta = {"x": x, "name": name_for(x), "section": L.section_at(x), "intro": st["intro"], "ready": st["ready"],
                "kid": st["kid"], "rooster": st["rooster"], "camera": st["cam"], "visible_objects": int(mask.sum())}
        # who can see the kid and the rooster (things between them and the camera)
        meta["blocked"] = {}
        cand = np.nonzero(mask)[0]
        for who, ch in (("kid", KID), ("rooster", ROOSTER)):
            box = char_aabb(ch)
            if box is None or (who == "rooster" and st["intro"]):     # under the basket, as the opening has him
                continue
            hits, blockers = 0, {}
            pts = [(box[0][0] + (box[1][0] - box[0][0]) * fx, (box[0][1] + box[1][1]) / 2,
                    box[0][2] + (box[1][2] - box[0][2]) * fz) for fx in (0.3, 0.5, 0.7) for fz in (0.25, 0.5, 0.75)]
            for p in pts:
                p = Vector(p)
                dvec = p - pos_b
                t_target = dvec.length
                tb, rb = cast(pos_b, dvec, cand, tmax=t_target - 0.3)
                if rb is not None and rb != "ground":
                    hits += 1
                    blockers[rb.piece] = blockers.get(rb.piece, 0) + 1
            meta["blocked"][who] = {"share": hits / len(pts), "by": blockers}
        if render:
            t1 = time.time()
            render_to(shots_dir / f"{name_for(x)}.png")
            meta["seconds"] = round(time.time() - t1, 1)
            log(f"shot {i + 1}/{len(xs)} x={x:.1f} {meta['section']} ({meta['visible_objects']} objects, "
                f"{meta['seconds']} s)")
        shots_meta.append(meta)
    (out / "shots.json").write_text(json.dumps(shots_meta, indent=1))

    # the yard as a set: front-left, front-right, from above, and the game's own opening frame
    if flag("--orbit"):
        odir = out / "orbit"
        odir.mkdir(exist_ok=True)
        yard = next((s for s in L.sections if any(it["kind"] == "basket" for it in s["items"])), L.sections[0])
        st = state_for_shot(0.0 if intro_level else yard["x"] + 4)
        cx = yard["x"] + yard["length"] * 0.45
        target = Vector((cx, 1.0, 0.6))
        views = [("game_opening", None), ("front_left", (-38, 10, 19)), ("front_right", (38, 10, 19)),
                 ("front_left_high", (-30, 32, 22)), ("front_right_high", (30, 32, 22)),
                 ("front_left_low", (-55, 4, 12)), ("front_right_low", (55, 4, 12))]
        for label, view in views:
            if view is None:
                pos_b, tgt_b = to_b(st["cam"]["pos"]), to_b(st["cam"]["target"])
            else:
                yaw, pitch, dist = view
                a, b = math.radians(yaw), math.radians(pitch)
                pos_b = target + Vector((dist * math.sin(a) * math.cos(b), -dist * math.cos(a) * math.cos(b),
                                         dist * math.sin(b)))
                tgt_b = target
            aim(pos_b, tgt_b)
            mask = state_mask(st) & frustum_mask(pos_b, cam_ob.rotation_euler.to_quaternion(),
                                                  math.radians(CAMERA["fov"]), aspect)
            show(mask)
            place_characters(st)
            if render:
                render_to(odir / f"{label}.png")
                log(f"orbit {label}")
        if render:
            sheet([odir / f"{lab}.png" for lab, _ in views], [lab.replace("_", " ") for lab, _ in views],
                  out / "orbit_sheet.jpg", cols=4, thumb=(640, 360))

    # ====================================================================== checks
    log("checks ...")
    findings = []
    shots_x = [(m["x"], m["camera"]["pos"][0], m["camera"]["width"], m["name"]) for m in shots_meta]

    def shots_showing(x0, x1=None):
        x1 = x0 if x1 is None else x1
        res_ = []
        for sx, cx, w, nm in shots_x:
            if cx - w / 2 <= x1 and x0 <= cx + w / 2:
                res_.append(nm)
        return res_

    def add(check, severity, x, piece, what, rec=None, section=None, x1=None, **extra):
        f = {"check": check, "severity": severity, "x": round(float(x), 2), "section": section or L.section_at(x),
             "piece": piece, "what": what, "shots": shots_showing(x, x1)}
        if rec is not None:
            f["source"] = rec.src
            f["name"] = rec.name
        f.update(extra)
        findings.append(f)

    in_course = [r for r in RECS if L.start - 2 <= r.x <= L.end + 2]
    COVER = ("crop", "paddy", "grass", "reed", "weed", "tuft", "bank", "sugarcane", "hedge", "bush", "fern", "flower",
             "lotus", "bund")

    def ground_cover(r):
        """Crops, grasses and banks the layouts tile edge to edge: not things that read as a copy or a clash."""
        folder = r.image.parent.name if r.image else ""
        return (r.layer in ("Plants", "Ground", "Decals") or folder in ("plants", "ground")
                or any(k in r.piece for k in COVER))
    plan_recs = [r for r in L.recs if r.src == "plan"]
    near_scenery = [r for r in in_course if r.src == "scenery" and r.z < ZAB["NearDepth"] and not r.flat]

    # (e) missing art
    for r in L.recs:
        if r.mode == "missing" and r.src == "plan":
            add("e", "high", r.x, r.piece, "; ".join(r.notes) or "no model and no cut-out", r)
    seen = set()
    for r in L.recs:
        if r.mode == "missing" and r.src == "scenery" and r.card["name"] not in seen:
            seen.add(r.card["name"])
            add("e", "high", r.x, r.piece, "; ".join(r.notes), r)
    for nm, ch in (("Kid", KID), ("Rooster", ROOSTER)):
        if ch is None:
            add("e", "high", 0, nm, f"{nm}.fbx could not be imported: the shots have no {nm.lower()}")
    seen = set()
    for r in L.recs:
        if getattr(r, "extruded", False) and r.mode == "card":
            key = (r.piece, r.src)
            if key in seen:
                continue
            seen.add(key)
            xs_ = sorted({round(q.x, 1) for q in L.recs if q.piece == r.piece and q.src == r.src
                          and L.start <= q.x <= L.end})
            add("h", "low" if r.role != "obstacle" else "medium", xs_[0] if xs_ else r.x, r.piece,
                f"only an extruded model exists, so the game draws the flat painted card"
                + (" (an obstacle: a flat card in a lane of 3D models)" if r.role == "obstacle" else "")
                + (f"; at x {', '.join(str(v) for v in xs_[:12])}" if xs_ else ""), r)

    # models drawn inside out (inward normals)
    for name, part in PICK.items():
        bad = [(n, v) for n, v, lo, hi, cl in part.volumes if inside_out(v, lo, hi, cl)]
        if bad:
            where = sorted(r.x for r in L.recs if r.role == "pickup" and r.piece == name)
            add("h", "high", where[0] if where else 0, name,
                f"Characters/{name}.fbx is inside out: its parts ({', '.join(n for n, _ in bad)}) have their normals "
                f"pointing in (signed volume {sum(v for _, v in bad) * 1e6:.0f} cm3). The Toon shader culls back faces "
                f"and pushes its outline shell along the normals, so the game draws every {name.lower()} as a dark "
                f"blob ({len(where)} of them in this level). Flip the normals in pickups.py (recalc outward) and "
                f"re-export", section="(every pickup)")
    for nm, ch in (("Kid", KID), ("Rooster", ROOSTER)):
        if ch and any(v < 0 for _, v in ch["volumes"]):    # the bodies are open meshes: any clear sign counts
            add("h", "high", 0, nm, f"{nm}.fbx's body has its normals pointing in: the game draws it inside out")
    for name, parts in LIB.items():
        mains = [pt for pt in parts if not pt.leaves]
        vol = sum(getattr(pt, "volume", 0.0) for pt in mains)
        if mains and inside_out(vol, np.min([pt.lo for pt in mains], 0), np.max([pt.hi for pt in mains], 0),
                                min(getattr(pt, "closed", 0.0) for pt in mains)):
            where = sorted({round(r.x, 1) for r in L.recs if r.entry and r.entry["name"] == name and L.start <= r.x <= L.end})
            add("h", "high", where[0] if where else 0, name,
                f"Models/{MODEL_INDEX[name]['folder']}/{name}.fbx has its normals pointing in (signed volume "
                f"{vol:.3f} m3): the game culls its outside and the outline shell covers it", section="(model)")

    # (a) floating or sunk
    seen = set()
    for r in plan_recs + near_scenery:
        if r.mode not in ("model", "card") or r.flat or r.state == "never" or r.role == "basket_tossed":
            continue
        if r.src == "scenery":
            if r.card["name"] in seen or r.layer not in ("Props", "Houses"):
                continue
        base = r.y if r.src == "plan" else 0.0
        if r.mode == "model":
            lowest = float(r.aabb[0][2])
            gap_ = lowest - base
            lift = r.entry.get("lift") or 0.0
            why = f" (its record's lift {lift:.2f} m is over the 0.1 m the game sets it down)" if lift > 0.1 else ""
        else:
            info = r.info
            gap_ = r.y + (info.bottom_margin * r.h if info else 0.0) - base
            why = f" (its cut-out has {info.bottom_margin * 100:.1f}% clear rows under the painting)" if info else ""
        if gap_ > 0.03:
            if r.src == "scenery":
                seen.add(r.card["name"])
            add("a", "medium" if gap_ > 0.06 else "low", r.x, r.piece,
                f"its bottom floats {gap_ * 100:.0f} cm above the ground{why}", r, gap=round(gap_, 3))
        elif r.mode == "model" and gap_ < -0.12 and r.src == "plan":
            add("a", "low", r.x, r.piece, f"sinks {-gap_ * 100:.0f} cm into the ground", r, gap=round(gap_, 3))
        on_solid = any(sd["x0"] - 0.05 <= r.x <= sd["x1"] + 0.05 and sd["z0"] - 0.05 <= r.z <= sd["z1"] + 0.05
                       and abs(sd["top"] - r.y) < 0.07 for sd in L.solids)
        if r.src == "plan" and r.y > 0.01 and not on_solid:
            o = Vector((r.x, r.z, r.y + 0.02))
            cand = np.nonzero([q is not r and q.src == "plan" for q in RECS])[0]
            t, hit = cast(o, (0, 0, -1), cand, tmax=2.0)
            if t is None or t > 0.07:
                add("a", "medium", r.x, r.piece, f"stands {r.y:.2f} m up with nothing under it", r)

    # (b) lane-side props reaching into the lane
    seen = {}
    for r in plan_recs + near_scenery:
        if r.mode not in ("model", "card") or r.flat or r.role in ("obstacle", "pickup", "decal", "basket", "basket_tossed",
                                                                     "platform", "platform_art", "ladder") \
                or r.state == "never":
            continue
        if r.mode == "card":
            z0 = z1 = r.z
        else:
            z0, z1 = float(r.aabb[0][1]), float(r.aabb[1][1])
        if z0 < LANE_HALF and z1 > -LANE_HALF:
            edge = z0 if r.z >= 0 else z1
            what = (f"its footprint (z {z0:.2f}..{z1:.2f}) reaches z = {edge:+.2f}, into the running lane (|z| < "
                    f"{LANE_HALF}): it would look like an obstacle the kid runs through")
            if r.src == "scenery":
                seen.setdefault(r.card["name"], []).append(r)
                continue
            add("b", "high", r.x, r.piece, what, r, x1=float(r.aabb[1][0]), reach=round(edge, 2))
    for nm, rs in seen.items():
        r = rs[0]
        add("b", "medium", r.x, r.piece, f"(scenery card {nm}, every {L.tracks[r.track[0]]['period']:.1f} m, at x "
            f"{', '.join(f'{q.x:.1f}' for q in rs[:8])}) footprint z {r.aabb[0][1]:.2f}..{r.aabb[1][1]:.2f} reaches "
            "into the running lane", r)

    # (c) overlaps in plan
    cands = []
    for r in plan_recs + near_scenery:
        if r.mode not in ("model", "card", "box") or r.flat or r.role in ("pickup", "decal", "basket_tossed") or not r.objs:
            continue
        if r.src == "scenery" and ground_cover(r):
            continue
        if r.state == "never" or max(r.w, r.h) < 0.5 and r.src == "scenery":
            continue
        lo, hi = r.aabb[0].copy(), r.aabb[1].copy()
        if r.mode == "card":
            lo[1], hi[1] = r.z - 0.01, r.z + 0.01
        cands.append((float(lo[0]), r, lo, hi))
    cands.sort(key=lambda c: c[0])
    layout_pairs = {}
    for i, (x0, r, lo, hi) in enumerate(cands):
        for j in range(i + 1, len(cands)):
            x0b, q, lo2, hi2 = cands[j]
            if x0b > hi[0]:
                break
            if r.item_id and r.item_id == q.item_id:
                continue
            if (r.state == "intro" and q.state == "chase") or (r.state == "chase" and q.state == "intro"):
                continue
            ox = min(hi[0], hi2[0]) - max(lo[0], lo2[0])
            oz = min(hi[1], hi2[1]) - max(lo[1], lo2[1])
            oy = min(hi[2], hi2[2]) - max(lo[2], lo2[2])
            if ox <= 0.05 or oz <= 0.0 or oy <= (0.2 if max(r.y, q.y) > 0.5 else 0.05):
                continue
            if r.mode == "card" or q.mode == "card":
                if oz < 0.0:
                    continue
            elif oz <= 0.05:
                continue
            if r.src == "scenery" and q.src == "scenery":
                if r.copy == q.copy:
                    key = tuple(sorted((r.card["name"], q.card["name"])))
                    layout_pairs.setdefault(key, (r, q, ox, oz))
                continue
            a, b = (r, q) if r.src == "plan" else (q, r)
            add("c", "high" if b.src == "plan" or b.layer == "Houses" else "medium", (a.x + b.x) / 2, a.piece,
                f"overlaps {b.piece}" + (" (scenery)" if b.src == "scenery" else "")
                + f" by {ox:.2f} m along the lane and {max(oz, 0):.2f} m in depth (x {a.x:.2f} z {a.z:.2f} vs x {b.x:.2f} "
                f"z {b.z:.2f})", a, other=b.name)
    for (n1, n2), (r, q, ox, oz) in layout_pairs.items():
        if r.mode == "card" and q.mode == "card":
            continue
        add("c", "low", (r.x + q.x) / 2, r.piece, f"(scenery layout) {n1} and {n2} overlap by {ox:.2f} m x {max(oz, 0):.2f} m "
            "in plan, in every copy of the set", r, other=q.name)

    # (d) obstacles hidden from the camera
    for ob in L.obstacles:
        if not ob["recs"]:
            continue
        target_recs = ob["recs"]
        worst = None
        for dist in (3.0, 6.0, 10.0):
            kx = ob["x0"] - dist
            st = state_for_shot(kx)
            if st["intro"]:
                continue
            if ob["after"] is not None and st["rooster_x"] < ob["after"]:
                st["rooster_x"] = ob["after"] + 0.1
            pos_b = to_b(st["cam"]["pos"])
            aim(pos_b, to_b(st["cam"]["target"]))
            mask = state_mask(st)
            cand = np.nonzero(mask)[0]
            pts = []
            for tr in target_recs:
                lo, hi = tr.aabb
                if tr.mode == "card" and tr.info is not None:
                    u0, v0, u1, v1 = tr.info.opaque
                    for fu, fv in ((0.5, 0.5), (0.5, 0.88), (0.25, 0.6), (0.75, 0.6), (0.5, 0.2)):
                        u, v = u0 + (u1 - u0) * fu, v0 + (v1 - v0) * fv
                        if tr.info.alpha_at(u, v) >= 0.5:
                            pts.append(tr.M @ Vector((u - 0.5, 0, v - 0.5)))
                elif tr.mode == "water":
                    pts += [Vector((tr.x + fx * tr.w / 2, tr.z, 0.008)) for fx in (-0.6, 0.0, 0.6)]
                else:
                    cx_, cz_ = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
                    hgt = hi[2] - lo[2]
                    for fx, fz in ((0.5, 0.5), (0.5, 0.88), (0.25, 0.65), (0.75, 0.65), (0.5, 0.2)):
                        pts.append(Vector((lo[0] + (hi[0] - lo[0]) * fx, cz_, lo[2] + hgt * fz)))
            vis = blk = cov = 0
            by = {}
            for p in pts:
                dvec = p - pos_b
                tt = dvec.length
                t, hit = cast(pos_b, dvec, cand, tmax=tt + 2.0)
                if hit is None or hit == "ground":
                    continue
                if hit in target_recs:
                    vis += 1
                elif hit.role == "pickup":
                    cov += 1
                    by[hit.piece] = by.get(hit.piece, 0) + 1
                elif t < tt - 0.05:
                    blk += 1
                    by[f"{hit.piece}" + (" (scenery)" if hit.src == "scenery" else "")] = by.get(hit.piece, 0) + 1
            n = vis + blk + cov
            if n and (blk + cov) and (worst is None or (blk + cov) / n > worst[0]):
                worst = ((blk + cov) / n, dist, blk, cov, by, n)
        if worst:
            share, dist, blk, cov, by, n = worst
            parts_ = []
            if blk:
                parts_.append(f"{blk} of {n} rays blocked")
            if cov:
                parts_.append(f"{cov} of {n} covered by pickups")
            add("d", "high" if share >= 0.4 else "medium", ob["x"], ob["kind"],
                f"hidden from the camera with the kid {dist:.0f} m before it: {', '.join(parts_)} "
                f"(by {', '.join(f'{k} x{v}' for k, v in by.items())})", ob["recs"][0], share=round(share, 2))

    # (f) repeated scenery
    standing = [r for r in in_course if r.src in ("scenery", "plan") and r.mode in ("model", "card") and not r.flat
                and r.role not in ("pickup", "decal", "obstacle", "basket_tossed", "platform_art")
                and r.state != "never" and not ground_cover(r)]
    by_piece = {}
    for r in standing:
        by_piece.setdefault(r.piece, []).append(r)
    for piece, rs in by_piece.items():
        rs.sort(key=lambda r: r.x)
        folder = rs[0].image.parent.name if rs[0].image else ""
        for a, b in zip(rs, rs[1:]):
            dx = b.x - a.x
            big = max(a.h, b.h) >= 2.5 and min(a.z, b.z) < 20 and (
                a.layer in ("Houses", "Backdrop") or (a.entry or {}).get("kind") == "building")
            figure = folder in ("people", "animals") or piece in ("bicycle", "bullock_cart", "hand_pump", "tulsi_planter",
                                                                   "chicken_basket", "hens_basket", "water_pot_stand")
            mixed = a.src != b.src
            limit = 12.0 if mixed else 20.0 if big else 30.0 if figure else 0.0
            if limit > dx > 0.5:
                sev = "medium" if (mixed or (big and a.z < 12)) else "low"
                add("f", sev, a.x, piece, f"the same {piece} again {dx:.1f} m on (x {a.x:.1f} z {a.z:.1f}"
                    f"{' mirrored' if a.mirror else ''} and x {b.x:.1f} z {b.z:.1f}{' mirrored' if b.mirror else ''})"
                    + (": a plan prop beside the scenery's own" if mixed else ""), a, x1=b.x)
    fronts = sorted((r for r in plan_recs if r.role == "platform_art" and r.mode in ("model", "card")), key=lambda r: r.x)
    if fronts:
        count = {}
        for r in fronts:
            count[r.piece] = count.get(r.piece, 0) + 1
        twins = [(a_.x, b_.x) for a_, b_ in zip(fronts, fronts[1:]) if a_.piece == b_.piece and b_.x - a_.x < 4.0]
        add("f", "medium" if twins else "low", fronts[0].x, "house fronts",
            f"{len(fronts)} house fronts from {len(count)} paintings ("
            + ", ".join(f"{k} x{v}" for k, v in sorted(count.items(), key=lambda kv: -kv[1])) + ")"
            + (f"; the same front twice side by side {len(twins)} times (at x "
               + ", ".join(f"{u:.1f}" for u, _ in twins[:10]) + ")" if twins else ""), section="(roof rows)")
    for tr in L.tracks:
        if tr["kind"] == "set":
            houses = sorted({stem(c["image"]) for c in tr["cards"] if c["layer"] == "Houses"})
            add("f", "low", L.start, "zone set", f"the whole near set repeats every {tr['period']:.1f} m: over the "
                f"{L.end - L.start:.0f} m course a player passes the same {len(houses)} houses in the same order about "
                f"{(L.end - L.start) / tr['period']:.1f} times", section="(whole course)")

    # (g) pickups inside solid geometry, and doubled
    pick = [r for r in RECS if r.role == "pickup"]
    solids = [i for i, r in enumerate(RECS) if r.role != "pickup" and r.mode in ("model", "card", "box") and not r.flat]
    SOL_AABB = AABB[solids]
    for p in pick:
        c = np.array([p.x, p.z, p.y])
        rad = 0.12
        near_ = np.nonzero(np.all(SOL_AABB[:, 0] - rad <= c, 1) & np.all(SOL_AABB[:, 1] + rad >= c, 1))[0]
        for j in near_:
            r = RECS[solids[j]]
            if r.state in ("never",) or r.role == "basket_tossed":
                continue
            msg = None
            for part, ob, Mw, Mi in r.parts:
                if part is None and r.mode == "box":
                    pl = Mi @ Vector(c)
                    if max(abs(pl.x), abs(pl.y), abs(pl.z)) < 0.5:
                        msg = f"inside the {r.piece} box"
                    continue
                if part is None:
                    pl = Mi @ Vector(c)
                    if abs(pl.y) * mscale(Mw) < rad and abs(pl.x) <= 0.5 and abs(pl.z) <= 0.5 and r.info and \
                            r.info.alpha_at(pl.x + 0.5, pl.z + 0.5) >= 0.5:
                        msg = f"pokes through the {r.piece} card"
                    continue
                if part.leaves:
                    continue
                pl = Mi @ Vector(c)
                loc, nrm, idx, dl = part.bvh().find_nearest(pl)
                if loc is None:
                    continue
                dw = (Mw @ loc - Vector(c)).length
                inside = (pl - loc).dot(nrm) < 0
                if inside:
                    msg = f"inside the {r.piece}" + (" (scenery)" if r.src == "scenery" else "")
                    break
                if dw < rad * 0.8:
                    msg = msg or f"cuts into the {r.piece} ({dw * 100:.0f} cm from its surface)"
            if msg:
                add("g", "high" if "inside" in msg else "medium", p.x, p.piece, f"at y {p.y:.2f}: {msg}", p, other=r.name)
    ps = sorted(pick, key=lambda r: r.x)
    for a, b in zip(ps, ps[1:]):
        if abs(b.x - a.x) < 0.25 and abs(b.y - a.y) < 0.25:
            add("g", "medium", a.x, a.piece, f"two pickups on one spot ({a.piece} x {a.x:.2f} y {a.y:.2f}, "
                f"{b.piece} x {b.x:.2f} y {b.y:.2f})", a)

    # (h) the rest
    for r in plan_recs:
        if r.vis_kind == "decal" and r.mode in ("model", "card"):
            rw = r.real[0] if getattr(r, "real", None) else None
            on_line = abs(r.z) < LANE_HALF
            in_front = -1.3 < r.z <= -LANE_HALF and r.h >= 0.35     # between the camera and her feet
            if not r.flat and r.h >= 0.25 and (on_line or in_front):
                add("h", "high" if on_line else "medium", r.x, r.piece,
                    f"litter standing {r.h:.2f} m tall ({r.w:.2f} m wide) at z {r.z:+.2f}, "
                    + ("on the running line: it reads as an obstacle that is not one" if on_line else
                       "just in front of the running line: it covers her feet as she passes"), r)
            if rw and r.real[2] == "manifest" and r.w / rw > 1.75:
                add("h", "medium", r.x, r.piece, f"drawn {r.w:.2f} m wide, {r.w / rw:.1f} times its real size "
                    f"({rw:.2f} m in the cut-out manifest)", r)
        if getattr(r, "stale", None):
            pw, ph, gw, gh = r.stale
            add("h", "medium", r.x, r.piece, f"the plan's resolved size {pw:.2f} x {ph:.2f} m no longer matches its art: "
                f"the game makes it {gw:.2f} x {gh:.2f} m (re-run level1.py)", r)
        if getattr(r, "flat_mismatch", None):
            pf, gf = r.flat_mismatch
            add("h", "low", r.x, r.piece, f"the plan says flat={pf} but Kit.Decal {'lays it flat' if gf else 'stands it up'} "
                f"(its model is {'a slab' if r.entry and r.entry.get('kind') == 'slab' else 'not a slab' if r.entry else 'missing'})",
                r)
        if r.role == "obstacle" and r.item_kind in KIT_OBSTACLE:
            dim, val, piece = KIT_OBSTACLE[r.item_kind]
            pv = r.item["visuals"][0][dim]
            if abs(pv - val) > 0.01 or r.piece != piece or abs(r.z - 0.05) > 0.01:
                add("h", "low", r.x, r.piece, f"the plan's {r.item_kind} ({r.piece} {dim}={pv} z={r.z}) differs from "
                    f"Kit's ({piece} {dim}={val} z=0.05)", r)
    # overhead obstacles (a clothesline: slide under it): does the painting hang below the gap the trigger leaves?
    hem_cache, hems = {}, {}
    for ob in L.obstacles:
        bottom = float(ob["item"].get("bottom", 0) or 0)
        for r in ob["recs"]:
            if bottom <= 0 or r.image is None or r.mode not in ("model", "card"):
                continue
            if r.image not in hem_cache:
                import numpy as np_
                from PIL import Image as Im
                a_ = np_.asarray(Im.open(r.image).convert("RGBA"))[..., 3] > 127
                hh_, ww_ = a_.shape
                low = []
                for col in range(int(0.15 * ww_), int(0.85 * ww_)):
                    rows_ = np_.where(a_[:, col])[0]
                    if not len(rows_):
                        continue
                    y_ = rows_.min()
                    while y_ < hh_ and a_[y_, col]:
                        y_ += 1                      # the first opaque run down from the top: the line and its cloth
                    low.append((hh_ - y_) / hh_)
                hem_cache[r.image] = min(low) if low else 1.0
            hem = r.y + hem_cache[r.image] * r.h
            if hem < bottom - 0.1:
                hems.setdefault(r.piece, []).append((ob["x"], hem, bottom))
    for piece, lst in hems.items():
        add("h", "high", lst[0][0], piece, f"the painting hangs down to {min(h_ for _, h_, _ in lst):.2f} m but the "
            f"obstacle's gap is {lst[0][2]:.2f} m high: the kid slides through the cloth, and pickups on the slide route "
            f"sit at its hem ({len(lst)} of them, at x " + ", ".join(f"{x_:.0f}" for x_, _, _ in lst[:10]) + ")",
            section="(every " + piece + ")")

    # standing decals the game turns away from the camera (Plans passes the item's 0..360 turn)
    for r in plan_recs:
        if r.vis_kind == "decal" and not r.flat and r.mode == "model":
            a = (r.turn + 180) % 360 - 180
            if abs(a) > 60:
                add("h", "medium" if abs(a) > 110 else "low", r.x, r.piece,
                    f"stands turned {a:+.0f} degrees (Plans passes the item's turn {r.turn:.0f}; the plan's visual says "
                    f"{getattr(r, 'plan_turn', r.turn):+.0f}): the camera sees its {'back' if abs(a) > 110 else 'side'}, "
                    "which the painting never showed", r)
    # the streamer lays the sections end to end from the runway's start, whatever their x says
    run = RUNWAY_START
    for sct in L.sections:
        if abs(sct["x"] - run) > 1e-3:
            add("h", "high", sct["x"], sct["name"], f"section starts at x {sct['x']:g} but the game lays it at {run:g} "
                "(LevelStreamer places chunks end to end from runwayStart): everything in it shifts by "
                f"{run - sct['x']:+.2f} m", section=sct["name"])
        run += sct["length"]
        for it in sct["items"]:
            if it["kind"] not in ("hop", "mischief") and not (sct["x"] - 1e-3 <= it["x"] < sct["x"] + sct["length"] + 1e-3):
                add("h", "medium", it["x"], it["kind"], f"lies outside its section {sct['name']} "
                    f"[{sct['x']:g}, {sct['x'] + sct['length']:g}): its chunk carries it there anyway", section=sct["name"])

    # scenery decals on the running line at an obstacle
    flats = [r for r in in_course if r.src == "scenery" and r.flat and abs(r.z) < LANE_HALF]
    for r in flats:
        for ob in L.obstacles:
            if ob["x0"] - 1.0 <= r.x <= ob["x1"] + 1.0:
                lump = (r.aabb[1][2] if r.aabb is not None else 0)
                add("h", "medium" if lump > 0.06 else "low", r.x, r.piece,
                    f"a scenery decal ({r.card['name']}, {r.w:.2f} m, {lump * 100:.0f} cm high) lies on the running line "
                    f"at the {ob['kind']} at {ob['x']:.1f}: it can read as part of the obstacle", r)
    # pickups hidden behind things
    for p in pick:
        st = state_for_shot(p.x - 6.0)
        if st["intro"]:
            continue
        pos_b = to_b(st["cam"]["pos"])
        mask = state_mask(st)
        cand = np.nonzero(mask & np.array([r.role != "pickup" for r in RECS]))[0]
        c = Vector((p.x, p.z, p.y))
        dvec = c - pos_b
        t, hit = cast(pos_b, dvec, cand, tmax=dvec.length - 0.13)
        if hit is not None and hit != "ground":
            add("h", "medium", p.x, p.piece, f"at y {p.y:.2f} is hidden behind the {hit.piece}"
                + (" (scenery)" if hit.src == "scenery" else ""), p, other=hit.name)
        elif hit == "ground":
            add("h", "medium", p.x, p.piece, f"at y {p.y:.2f} is below the ground line from the camera", p)
    # (i) the kid or rooster hidden behind something, swept along the course every metre with the close camera
    t_i = time.time()
    no_pick = np.array([r.role != "pickup" for r in RECS])
    sweep_from = (L.basket.get("walkFrom", -4.4) if L.basket else 0.0) if intro_level else 0.0
    runs = {}
    for kx in np.arange(sweep_from, L.end - 2.0, float(arg("--sweep", "1.0"))):
        st = state_for_shot(float(kx))
        pos_b = to_b(st["cam"]["pos"])
        cand = np.nonzero(state_mask(st) & no_pick)[0]
        for who, (x, y, clip, _f) in (("kid", st["kid"]), ("rooster", st["rooster"])):
            if who == "rooster" and st["intro"]:
                continue                     # under the basket, as the opening has him
            hw, hh = (0.18, 1.05) if who == "kid" else (0.25, 0.6)
            hit_by = {}
            n = 0
            for fx in (-0.6, 0.0, 0.6):
                for fy in (0.2, 0.5, 0.85):
                    p_ = Vector((x + fx * hw, -0.1, y + fy * hh))
                    dvec = p_ - pos_b
                    n += 1
                    t, hit = cast(pos_b, dvec, cand, tmax=dvec.length - 0.05)
                    if hit is not None and hit != "ground":
                        hit_by[hit.name] = hit
            share = 0.0
            if hit_by:
                # the share of rays any one thing blocks, for each blocker
                for nm, rec in hit_by.items():
                    blocked = 0
                    for fx in (-0.6, 0.0, 0.6):
                        for fy in (0.2, 0.5, 0.85):
                            p_ = Vector((x + fx * hw, -0.1, y + fy * hh))
                            dvec = p_ - pos_b
                            if ray_rec(rec, pos_b, dvec.normalized(), dvec.length - 0.05) is not None:
                                blocked += 1
                    share = blocked / n
                    if share >= 0.3:
                        key = (who, nm)
                        r_ = runs.setdefault(key, {"rec": rec, "xs": [], "worst": 0.0})
                        r_["xs"].append(float(kx))
                        r_["worst"] = max(r_["worst"], share)
    for (who, nm), r_ in runs.items():
        rec = r_["rec"]
        xs_r = r_["xs"]
        spans, a0 = [], xs_r[0]
        for u, v in zip(xs_r, xs_r[1:] + [None]):
            if v is None or v - u > 1.5:
                spans.append((a0, u))
                if v is not None:
                    a0 = v
        for a0, a1 in spans:
            fg = rec.src == "scenery" and rec.z < -0.5
            add("i", "high" if r_["worst"] >= 0.6 and (fg or a1 - a0 >= 2) else "medium", a0, who,
                f"the {who} is up to {r_['worst'] * 100:.0f}% hidden behind the {rec.piece}"
                + (f" (scenery card {rec.card['name']}, z {rec.z:.1f})" if rec.src == "scenery" else f" (z {rec.z:.2f})")
                + f" with the kid at x {a0:.0f}" + (f"..{a1:.0f}" if a1 > a0 else ""), rec, x1=a1 + 4)
    log(f"sweep for hidden characters: {time.time() - t_i:.0f} s")
    if abs(BUILDER_FOV - CAMERA["fov"]) > 0.01:
        add("h", "high", 0, "camera", f"GameBuilder.BuildScene sets camera.fieldOfView = {BUILDER_FOV:g}, but the Kick Off "
            f"framing (ChaseCamera) is made for {CAMERA['fov']:g}: these renders use {CAMERA['fov']:g}; the game would "
            f"show {math.tan(math.radians(BUILDER_FOV) / 2) / math.tan(math.radians(CAMERA['fov']) / 2):.2f} of the "
            "height and width, its kid bigger", section="(camera)")
    # bare sky where the game has no ground (in front of the runway start)
    for m in shots_meta:
        pos_b = to_b(m["camera"]["pos"])
        aim(pos_b, to_b(m["camera"]["target"]))
        bare = 0
        for fx in np.linspace(0, 1, 9):
            for fy in (0.0, 0.08, 0.16):
                d = cam_dir(cam_ob, fx, fy, aspect)
                if d.z < 0:
                    t = -pos_b.z / d.z
                    p = pos_b + d * t
                    if t < CAMERA["far"] and not any(x0 <= p.x <= x1 and z0 <= p.y <= z1 for x0, x1, z0, z1 in GROUND_REGIONS):
                        bare += 1
        if bare:
            add("h", "medium", m["x"], "ground", f"shot {m['name']}: the bottom of the frame shows sky where the game has no "
                f"ground ({bare} of 27 sample rays; the chunks' ground starts at x = {RUNWAY_START:.0f})",
                section=m["section"])

    order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["check"], f["x"]))
    (out / "checks.json").write_text(json.dumps(findings, indent=1))
    write_md(out / "checks.md", findings, L, plan_path, shots_meta, xs)
    log(f"{len(findings)} findings -> {out / 'checks.md'}")

    if render and shots_meta:
        paths = [shots_dir / f"{m['name']}.png" for m in shots_meta]
        labels = [f"x={m['x']:g}  {m['section']}" + ("  (opening)" if m["intro"] else "  (ready)" if m.get("ready")
                                                     else "") for m in shots_meta]
        sheet(paths, labels, out / "contact_sheet.jpg", cols=4, thumb=(480, 270))
        for page in range(0, len(paths), 16):
            sheet(paths[page:page + 16], labels[page:page + 16], out / f"contact_{page // 16 + 1:02d}.jpg", cols=4,
                  thumb=(640, 360))
    log(f"done in {time.time() - t_start:.0f} s")


def cam_dir(cam_ob, fx, fy, aspect):
    """The world direction through the frame at (fx, fy), 0..1 from the bottom left."""
    from mathutils import Vector
    tv = math.tan(cam_ob.data.angle_y / 2)
    th = tv * aspect
    d = Vector(((fx * 2 - 1) * th, (fy * 2 - 1) * tv, -1.0))
    return (cam_ob.matrix_world.to_3x3() @ d).normalized()


# ====================================================================== outputs
def sheet(paths, labels, out, cols=4, thumb=(480, 270)):
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18 if thumb[0] >= 600 else 15)
    except OSError:
        font = ImageFont.load_default()
    pad, lab = 6, 26
    rows = max(1, math.ceil(len(paths) / cols))
    im = Image.new("RGB", (pad + cols * (thumb[0] + pad), pad + rows * (thumb[1] + lab + pad)), (32, 30, 28))
    d = ImageDraw.Draw(im)
    for i, (p, t) in enumerate(zip(paths, labels)):
        x = pad + (i % cols) * (thumb[0] + pad)
        y = pad + (i // cols) * (thumb[1] + lab + pad)
        if pathlib.Path(p).exists():
            s = Image.open(p).convert("RGB").resize(thumb, Image.LANCZOS)
            im.paste(s, (x, y + lab))
        d.text((x + 2, y + 4), t, fill=(250, 235, 200), font=font)
    im.save(out, quality=88)


def write_md(path, findings, L, plan_path, shots_meta, xs):
    names = {"a": "Floating or sunk", "b": "Props reaching into the running lane", "c": "Overlaps in plan",
             "d": "Obstacles hidden from the camera", "e": "Missing art", "f": "Repeated scenery",
             "g": "Pickups in solid geometry", "h": "Other", "i": "Kid or rooster hidden (close camera)"}
    lines = [f"# Level render checks: {L.plan.get('title', plan_path.stem)}", "",
             f"Plan `{plan_path.relative_to(ROOT) if plan_path.is_relative_to(ROOT) else plan_path}`, "
             f"{len(L.sections)} sections, {L.start:.0f}..{L.end:.0f} m; {len(shots_meta)} shots "
             f"({', '.join(f'{x:g}' for x in xs[:6])}{'...' if len(xs) > 6 else ''}).", "",
             "Each finding: course x, section, piece, what is wrong, and the shots that show that x. "
             "Sorted by severity (high, medium, low), then check, then x.", ""]
    counts = {}
    for f in findings:
        counts[(f["check"], f["severity"])] = counts.get((f["check"], f["severity"]), 0) + 1
    lines += ["| Check | High | Medium | Low |", "| --- | --- | --- | --- |"]
    for c in "abcdefghi":
        lines.append(f"| {c}: {names[c]} | {counts.get((c, 'high'), 0)} | {counts.get((c, 'medium'), 0)} | "
                     f"{counts.get((c, 'low'), 0)} |")
    for sev in ("high", "medium", "low"):
        fs = [f for f in findings if f["severity"] == sev]
        if not fs:
            continue
        lines += ["", f"## {sev.capitalize()}", ""]
        for c in "abcdefghi":
            sub = [f for f in fs if f["check"] == c]
            if not sub:
                continue
            lines += [f"### {c}: {names[c]} ({len(sub)})", ""]
            for f in sub:
                shots = ", ".join(f["shots"][:4]) + ("..." if len(f["shots"]) > 4 else "")
                lines.append(f"- **x {f['x']:g}** ({f['section']}) `{f['piece']}`: {f['what']}"
                             + (f" [shots: {shots}]" if shots else ""))
            lines.append("")
    path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    blender_main()
