"""Review sheets for the kit's models: the painting next to the model seen from the front at the same size, then the
model from the front-left, front-right, the side, the back and from above, in the game's toon look (flat colour, a
two-tone light from the front-left-top, an ink outline). A model is right when its front is the painting and every
other view looks like the same thing painted by the same hand.
"""
import math
import pathlib

import bpy
import numpy as np
from mathutils import Vector
from PIL import Image, ImageDraw

LIGHT = Vector((-0.45, -0.55, 0.7)).normalized()      # towards the light: front-left-top, as Toon.shader
SHADOW = (0.86, 0.8, 0.86)


def _toon(mat_src, name, cutout=False):
    """A Cycles stand-in for ChickenRunner/Toon: the texture, darkened by SHADOW where the surface turns from LIGHT."""
    tex_img = None
    for n in mat_src.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image is not None:
            tex_img = n.image
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = tex_img
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = tuple(LIGHT)
    nt.links.new(geo.outputs["Normal"], dot.inputs[0])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = -0.3
    ramp.inputs["From Max"].default_value = -0.1
    nt.links.new(dot.outputs["Value"], ramp.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    shade = nt.nodes.new("ShaderNodeMix")
    shade.data_type = "RGBA"
    shade.blend_type = "MULTIPLY"
    shade.inputs["Factor"].default_value = 1.0
    shade.inputs["B"].default_value = SHADOW + (1,)
    nt.links.new(tex.outputs["Color"], shade.inputs["A"])
    nt.links.new(ramp.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(shade.outputs["Result"], mix.inputs["A"])
    nt.links.new(tex.outputs["Color"], mix.inputs["B"])
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mix.outputs["Result"], emit.inputs["Color"])
    if cutout:
        gt = nt.nodes.new("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 0.5
        nt.links.new(tex.outputs["Alpha"], gt.inputs[0])
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        ms = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(gt.outputs[0], ms.inputs[0])
        nt.links.new(tr.outputs[0], ms.inputs[1])
        nt.links.new(emit.outputs[0], ms.inputs[2])
        nt.links.new(ms.outputs[0], out.inputs["Surface"])
    else:
        nt.links.new(emit.outputs[0], out.inputs["Surface"])
    return m


def _ink(width):
    m = bpy.data.materials.new("ink")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.03, 0.015, 0.01, 1)
    ms = nt.nodes.new("ShaderNodeMixShader")
    # the shell's near faces (turned away from the camera) are see-through; its far faces, showing past the edge, ink
    nt.links.new(geo.outputs["Backfacing"], ms.inputs[0])
    nt.links.new(em.outputs[0], ms.inputs[1])
    nt.links.new(tr.outputs[0], ms.inputs[2])
    nt.links.new(ms.outputs[0], out.inputs["Surface"])
    return m


def render_sheet(rec, ob, leaves, painting, out_path, res=420):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 12
    scene.cycles.device = "CPU"
    scene.cycles.transparent_max_bounces = 128     # a crown is many cut-out cards deep (the game draws them cut out)
    import kitlib
    kitlib.threads(scene)
    scene.cycles.max_bounces = 128
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    world = scene.world or bpy.data.worlds.new("w")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    for o in list(scene.objects):
        if o not in (ob, leaves):
            bpy.data.objects.remove(o)
    ob.data.materials[0] = _toon(ob.data.materials[0], "toon_main")
    W, H = rec["width"], rec["height"]
    size = max(W, H, rec["depth"])
    ink = ob.modifiers.new("ink", "SOLIDIFY")
    ink.thickness = max(0.003, 0.006 * size)
    ink.offset = 1.0
    ink.use_flip_normals = True
    ink.material_offset = 1
    ob.data.materials.append(_ink(ink.thickness))
    if leaves is not None:
        leaves.data.materials[0] = _toon(leaves.data.materials[0], "toon_leaves", cutout=True)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    centre = Vector((0, rec["depth"] * 0.25 if rec["kind"] == "building" else 0, H / 2))
    tiles = []

    def shot(label, loc, ortho=None, aspect=(1, 1)):
        if ortho:
            cam.data.type = "ORTHO"
            cam.data.ortho_scale = ortho
        else:
            cam.data.type = "PERSP"
            cam.data.lens = 50
        cam.location = loc
        d = (centre - Vector(loc)).normalized()
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        scene.render.resolution_x = int(res * aspect[0])
        scene.render.resolution_y = int(res * aspect[1])
        p = pathlib.Path(out_path).with_name(f"_{rec['name']}_{len(tiles)}.png")
        scene.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        tiles.append((label, Image.open(p).convert("RGBA")))
        p.unlink()

    # the front, framed exactly as the painting (ortho, the painting's own frame)
    aspect = (W / max(W, H), H / max(W, H))
    centre_front = Vector((0, 0, H / 2))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(W, H)
    cam.location = (0, -30, H / 2)
    cam.rotation_euler = (math.radians(90), 0, 0)
    scene.render.resolution_x = int(res * aspect[0])
    scene.render.resolution_y = int(res * aspect[1])
    p = pathlib.Path(out_path).with_name(f"_{rec['name']}_front.png")
    scene.render.filepath = str(p)
    bpy.ops.render.render(write_still=True)
    front = Image.open(p).convert("RGBA")
    p.unlink()
    dist = size * 2.6
    for label, yaw, pitch in (("front-left", -35, 12), ("front-right", 35, 12), ("side", 90, 8), ("back", 180, 12),
                              ("above", -25, 50)):
        a, b = math.radians(yaw), math.radians(pitch)
        loc = (centre.x + dist * math.sin(a) * math.cos(b), centre.y - dist * math.cos(a) * math.cos(b), centre.z + dist * math.sin(b))
        shot(label, loc)
    # compose: painting | model front, then the five views
    paint = painting.copy()
    paint.thumbnail((res, res))
    pad = 10
    row1 = [("painting", paint), ("model, front", front)]
    cell = res
    sheet = Image.new("RGB", (pad + 4 * (cell + pad), 2 * (cell + 28) + pad), (205, 198, 186))
    d = ImageDraw.Draw(sheet)
    items = row1 + tiles
    for i, (label, im) in enumerate(items):
        col, row = (i % 4), (i // 4)
        x, y = pad + col * (cell + pad), pad + row * (cell + 28)
        bg = Image.new("RGBA", (cell, cell), (226, 221, 210, 255))
        bg.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
        sheet.paste(bg.convert("RGB"), (x, y))
        d.text((x + 4, y + cell + 6), f"{rec['name']}: {label}", fill=(40, 30, 20))
    sheet.save(out_path, quality=90)
    return out_path
