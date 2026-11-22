"""Renders every kind of built house in a row, to check the house kit at a glance.

Run from the repo root with Blender's Python (bpy):
    python ArtSource/tools/build_house_catalog.py [--samples 32] [--seed 3]
Writes ArtSource/blender/renders/house_catalog_seed<N>.png. Each seed builds a different set.
"""
import math
import pathlib
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from village_kit import Kit  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEX = ROOT / "ArtSource" / "cutouts" / "textures"
RENDERS = ROOT / "ArtSource" / "blender" / "renders"
ARGS = sys.argv[1:]
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 32
SEED = int(ARGS[ARGS.index("--seed") + 1]) if "--seed" in ARGS else 3
ORDER = ["hut", "mud_tin", "shop", "head", "tiled", "parapet", "hut", "mud_tin"]

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 4
scene.render.resolution_x, scene.render.resolution_y = 2400, 900
scene.view_settings.view_transform = "Standard"
col = bpy.data.collections.new("BuiltHouses")
scene.collection.children.link(col)


def load_image(path):
    return bpy.data.images.load(str(path), check_existing=True)


kit = Kit(TEX, col, load_image, random.Random(SEED))

# Ground: the mud tile in the lane's earth colour.
ground_col = bpy.data.collections.new("Ground")
scene.collection.children.link(ground_col)
kit.col = ground_col
kit.box("ground", -10, -40, -0.1, 70, 60, 0, kit.painted("mud_floor", (0.86, 0.48, 0.28), 0.25))
kit.col = col

x, prev = 0.0, []
for kind in ORDER:
    w, door_x, rgb = kit.build(kind, x, 4.0 + (0.8 if kind == "head" else 0.0), avoid_colours=tuple(prev[-2:]))
    prev.append(rgb)
    x += w + 0.9
width = x

# Outlines on the houses, as in the lane scene.
scene.render.use_freestyle = True
scene.render.line_thickness_mode = "ABSOLUTE"
vl = scene.view_layers[0]
vl.use_freestyle = True
fs = vl.freestyle_settings
fs.crease_angle = math.radians(140)
ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("Outlines")
ls.select_by_collection = True
ls.collection = col
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new("Ink")
ls.linestyle.color = (0.16, 0.09, 0.06)
ls.linestyle.thickness = 1.4

world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.85, 0.62, 0.42, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55
sun_data = bpy.data.lights.new("Sun", "SUN")
sun_data.energy = 4.2
sun_data.color = (1.0, 0.84, 0.62)
sun = bpy.data.objects.new("Sun", sun_data)
sun.rotation_euler = Vector((-0.55, 0.6, -0.7)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(sun)

cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = width + 1.0
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = (width / 2 - 0.5, -30, 9.5)  # close to the game's low, side-on view: 10° down
cam.rotation_euler = (math.radians(80), 0, 0)

RENDERS.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(RENDERS / f"house_catalog_seed{SEED}.png")
bpy.ops.render.render(write_still=True)
print("rendered", scene.render.filepath)
