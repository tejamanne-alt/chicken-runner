"""Procedural village houses for the Blender scenes. Every call builds a different house.

Six kinds, each with its own ranges for size, colour, roof and details:
    hut        mud walls with a lime band and palm thatch: a round hut with a cone roof, or a square one
               with a hipped roof
    mud_tin    orange mud walls under corrugated sheets (shed or gable, silver, faded blue or green) held down
               with stones and a tyre; often a plank lean-to on one side
    tiled      painted walls, a terracotta-tiled gable roof, sometimes a pillared veranda
    parapet    painted walls, a flat roof behind a crenellated parapet, steps up to the door
    shop       a petty shop: open front, counter with sweet jars, shelves, sachet strips, a banana bunch,
               a striped or tin awning on poles, a blank signboard, sometimes a bench
    head       the village head's house: wide and two storeys, a raised pillared veranda (thinnai) under
               tiles, a big carved door with a mango-leaf garland, steps up from the street
Compound walls (compound) fill the breaks between houses: coping, a coloured dado, end pillars, sometimes
a row of decorative openings.

Houses face the camera: the front wall sits at y = y0 and the house runs back along +Y. Walls take their
colour from a palette and their grain from the hand-painted texture tiles in ArtSource/cutouts/textures.
"""
import math

import bmesh
import bpy

WALLS = [  # (texture tile for the grain, sRGB colour)
    ("limewash_wall", (0.95, 0.93, 0.87)),
    ("indigo_wall", (0.38, 0.45, 0.78)),
    ("turmeric_wall", (0.96, 0.76, 0.32)),
    ("pink_wall", (0.94, 0.72, 0.70)),
    ("seagreen_wall", (0.56, 0.80, 0.70)),
    ("limewash_wall", (0.62, 0.80, 0.92)),  # sky blue
    ("seagreen_wall", (0.76, 0.90, 0.72)),  # mint
    ("pink_wall", (0.86, 0.56, 0.62)),      # rose
]
MUD = [  # orange, laterite red, ochre, brown: far enough apart to tell neighbours apart
    ("mud_floor", (0.92, 0.58, 0.30)),
    ("mud_floor", (0.80, 0.40, 0.25)),
    ("mud_floor", (0.90, 0.72, 0.44)),
    ("mud_floor", (0.68, 0.46, 0.33)),
]
TINS = [(0.66, 0.68, 0.70), (0.50, 0.63, 0.76), (0.55, 0.70, 0.58), (0.76, 0.74, 0.68)]  # silver, faded blue/green, asbestos
BRIGHT = [(0.90, 0.20, 0.20), (0.98, 0.78, 0.15), (0.20, 0.55, 0.90), (0.20, 0.70, 0.35), (0.95, 0.45, 0.70),
          (0.98, 0.55, 0.10), (0.55, 0.30, 0.75), (0.95, 0.95, 0.92)]
AWNINGS = [((0.90, 0.25, 0.20), (0.97, 0.93, 0.85)), ((0.15, 0.45, 0.75), (0.97, 0.93, 0.85)),
           ((0.20, 0.60, 0.35), (0.98, 0.80, 0.20)), ((0.95, 0.55, 0.10), (0.97, 0.93, 0.85))]
DOORS = [(1.0, 1.0, 1.0), (0.45, 0.62, 0.92), (0.50, 0.80, 0.55), (0.62, 0.24, 0.22), (0.95, 0.80, 0.55)]
FRAMES = [(0.20, 0.62, 0.62), (0.95, 0.93, 0.87), (0.30, 0.55, 0.30), (0.75, 0.25, 0.20)]
PLINTHS = [(0.70, 0.25, 0.18), (0.95, 0.93, 0.87), (0.32, 0.30, 0.30)]
KINDS = ["hut", "mud_tin", "tiled", "parapet", "shop", "head"]


def srgb_to_linear(rgb):
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)


class Kit:
    def __init__(self, tex_dir, collection, load_image, rng):
        self.tex_dir = tex_dir
        self.col = collection
        self.load_image = load_image
        self.rng = rng
        self.count = 0
        self.doorstep_y = 0.0  # where the last house's doorstep kolam goes
        self.kind_colours = {}  # wall colours each kind has used, so the same kind comes back in a new colour

    # ------------------------------------------------------------------ materials
    def _material(self, name, emission=0.12):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = 1.0
        bsdf.inputs["Specular IOR Level"].default_value = 0.0
        bsdf.inputs["Emission Strength"].default_value = emission
        return mat, nt, bsdf

    def _texture(self, nt, tile, scale):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = self.load_image(self.tex_dir / f"{tile}.png")
        tex.projection = "BOX"
        tex.projection_blend = 0.3
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (scale, scale, scale)
        mapping.inputs["Location"].default_value = (self.rng.random(), self.rng.random(), 0)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        return tex

    @staticmethod
    def _multiply(nt, a, b_socket):
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        s = {x.identifier: x for x in mix.inputs}
        s["Factor_Float"].default_value = 1.0
        if isinstance(a, tuple):
            s["A_Color"].default_value = (*a, 1)
        else:
            nt.links.new(a, s["A_Color"])
        nt.links.new(b_socket, s["B_Color"])
        return next(x for x in mix.outputs if x.identifier == "Result_Color")

    def painted(self, tile, rgb, scale=0.5, emission=0.14):
        """A wall in an exact colour, with the hand-painted grain of a texture tile."""
        mat, nt, bsdf = self._material(f"M_wall_{self.count}_{tile}", emission)
        tex = self._texture(nt, tile, scale)
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        nt.links.new(tex.outputs["Color"], bw.inputs["Color"])
        grain = nt.nodes.new("ShaderNodeMapRange")
        grain.inputs["To Min"].default_value = 0.6
        grain.inputs["To Max"].default_value = 1.2
        nt.links.new(bw.outputs["Val"], grain.inputs["Value"])
        out = self._multiply(nt, srgb_to_linear(rgb), grain.outputs["Result"])
        nt.links.new(out, bsdf.inputs["Base Color"])
        nt.links.new(out, bsdf.inputs["Emission Color"])
        return mat

    def textured(self, tile, tint=(1.0, 1.0, 1.0), scale=0.6, emission=0.12):
        """A texture tile in its own colours (thatch, roof tiles, wood), optionally tinted."""
        mat, nt, bsdf = self._material(f"M_{tile}_{self.count}", emission)
        tex = self._texture(nt, tile, scale)
        out = self._multiply(nt, srgb_to_linear(tint), tex.outputs["Color"])
        nt.links.new(out, bsdf.inputs["Base Color"])
        nt.links.new(out, bsdf.inputs["Emission Color"])
        return mat

    def flat(self, rgb, emission=0.12):
        mat, nt, bsdf = self._material(f"M_flat_{self.count}", emission)
        lin = (*srgb_to_linear(rgb), 1)
        bsdf.inputs["Base Color"].default_value = lin
        bsdf.inputs["Emission Color"].default_value = lin
        return mat

    def tin(self, rgb=None):
        """Corrugated sheet: ridges about 8 cm apart, patches of rust."""
        rgb = rgb or self.rng.choice(TINS)
        mat, nt, bsdf = self._material(f"M_tin_{self.count}", 0.1)
        coord = nt.nodes.new("ShaderNodeTexCoord")
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "X"
        wave.inputs["Scale"].default_value = 4.0  # Blender's bands repeat every 0.314 / scale
        nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 1.2
        noise.inputs["Detail"].default_value = 8.0
        noise.noise_dimensions = "4D"  # the W input only exists in 4D mode
        noise.inputs["W"].default_value = self.rng.random() * 10
        nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
        rust = nt.nodes.new("ShaderNodeMapRange")
        rust.inputs["From Min"].default_value = self.rng.uniform(0.44, 0.56)
        rust.inputs["From Max"].default_value = rust.inputs["From Min"].default_value + 0.14
        nt.links.new(noise.outputs["Fac"], rust.inputs["Value"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        s = {x.identifier: x for x in mix.inputs}
        s["A_Color"].default_value = (*srgb_to_linear(rgb), 1)
        s["B_Color"].default_value = (*srgb_to_linear((0.62, 0.32, 0.14)), 1)
        nt.links.new(rust.outputs["Result"], s["Factor_Float"])
        ridges = nt.nodes.new("ShaderNodeMapRange")
        ridges.inputs["To Min"].default_value = 0.72
        ridges.inputs["To Max"].default_value = 1.05
        nt.links.new(wave.outputs["Fac"], ridges.inputs["Value"])
        out = self._multiply(nt, next(x for x in mix.outputs if x.identifier == "Result_Color"), ridges.outputs["Result"])
        nt.links.new(out, bsdf.inputs["Base Color"])
        nt.links.new(out, bsdf.inputs["Emission Color"])
        return mat

    def stripes(self, a, b, period=0.45):
        """Two-colour cloth stripes running down the slope, `period` metres per pair."""
        mat, nt, bsdf = self._material(f"M_stripes_{self.count}", 0.16)
        coord = nt.nodes.new("ShaderNodeTexCoord")
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "X"
        wave.inputs["Scale"].default_value = 0.314 / period
        nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        ramp.color_ramp.elements[0].color = (*srgb_to_linear(a), 1)
        ramp.color_ramp.elements[1].position = 0.5
        ramp.color_ramp.elements[1].color = (*srgb_to_linear(b), 1)
        nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
        return mat

    # ------------------------------------------------------------------ geometry
    def _adopt(self, name, mat, smooth=False):
        """Takes the object a bpy.ops primitive just made into this kit's collection."""
        obj = bpy.context.active_object
        obj.name = name
        obj.data.materials.append(mat)
        if smooth:
            for poly in obj.data.polygons:
                poly.use_smooth = True
        for c in obj.users_collection:
            c.objects.unlink(obj)
        self.col.objects.link(obj)
        return obj

    def cylinder(self, name, x, y, z0, z1, radius, mat, verts=16):
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=z1 - z0, location=(x, y, (z0 + z1) / 2))
        return self._adopt(name, mat, smooth=True)

    def cone(self, name, x, y, z0, z1, radius, mat, verts=24):
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=radius, radius2=0.04, depth=z1 - z0,
                                        location=(x, y, (z0 + z1) / 2))
        return self._adopt(name, mat, smooth=True)

    def blob(self, name, x, y, z, size, mat):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1, location=(x, y, z))
        obj = self._adopt(name, mat, smooth=True)
        obj.scale = size
        return obj

    def mesh(self, name, verts, faces, mat):
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts, [], faces)
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        obj = bpy.data.objects.new(name, me)
        self.col.objects.link(obj)
        return obj

    def box(self, name, x0, y0, z0, x1, y1, z1, mat):
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        return self.mesh(name, v, f, mat)

    def gable(self, name, x0, x1, y0, y1, ze, zr, mat):
        """A gable roof whose ridge runs along the street."""
        ym = (y0 + y1) / 2
        v = [(x0, y0, ze), (x1, y0, ze), (x1, ym, zr), (x0, ym, zr), (x0, y1, ze), (x1, y1, ze)]
        f = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)]
        return self.mesh(name, v, f, mat)

    def hip(self, name, x0, x1, y0, y1, ze, zr, ridge_frac, mat):
        """A hipped roof: four slopes up to a short ridge."""
        ym = (y0 + y1) / 2
        inset = (x1 - x0) * (1 - ridge_frac) / 2
        v = [(x0, y0, ze), (x1, y0, ze), (x1, y1, ze), (x0, y1, ze), (x0 + inset, ym, zr), (x1 - inset, ym, zr)]
        f = [(0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4), (0, 3, 2, 1)]
        return self.mesh(name, v, f, mat)

    def shed(self, name, x0, x1, y0, y1, z_front, z_back, mat, thick=0.06):
        """A single-slope roof, low at the front."""
        v = [(x0, y0, z_front), (x1, y0, z_front), (x1, y1, z_back), (x0, y1, z_back),
             (x0, y0, z_front + thick), (x1, y0, z_front + thick), (x1, y1, z_back + thick), (x0, y1, z_back + thick)]
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        return self.mesh(name, v, f, mat)

    # ------------------------------------------------------------------ details
    def door(self, tag, cx, y0, w, h, door_rgb, frame_rgb, z=0.0):
        self.box(f"{tag}_frame", cx - w / 2 - 0.09, y0 - 0.025, z, cx + w / 2 + 0.09, y0 + 0.01, z + h + 0.09,
                 self.flat(frame_rgb))
        self.box(f"{tag}_door", cx - w / 2, y0 - 0.05, z, cx + w / 2, y0, z + h,
                 self.textured("wood_planks", door_rgb, scale=1.2))

    def window(self, tag, cx, y0, z, w, h, style):
        r = self.rng
        self.box(f"{tag}_frame", cx - w / 2 - 0.07, y0 - 0.02, z - 0.07, cx + w / 2 + 0.07, y0 + 0.01, z + h + 0.07,
                 self.flat(r.choice(FRAMES)))
        self.box(f"{tag}_dark", cx - w / 2, y0 - 0.03, z, cx + w / 2, y0, z + h, self.flat((0.12, 0.08, 0.06), 0.0))
        if style == "bars":
            bar = self.flat((0.25, 0.4, 0.75))
            n = 4
            for i in range(n):
                bx = cx - w / 2 + w * (i + 0.5) / n
                self.box(f"{tag}_bar{i}", bx - 0.015, y0 - 0.06, z, bx + 0.015, y0 - 0.03, z + h, bar)
        else:  # wooden shutters swung open
            wood = self.textured("wood_planks", r.choice(DOORS), scale=1.5)
            for side in (-1, 1):
                sx = cx + side * (w / 2 + w / 4 + 0.05)
                self.box(f"{tag}_shutter{side}", sx - w / 4, y0 - 0.08, z, sx + w / 4, y0 - 0.04, z + h, wood)

    def steps(self, tag, cx, y0, w, n, rgb):
        mat = self.painted("limewash_wall", rgb, scale=1.0)
        for i in range(n):
            self.box(f"{tag}_step{i}", cx - w / 2 - 0.1 * (n - i), y0 - 0.32 * (n - i), 0.0,
                     cx + w / 2 + 0.1 * (n - i), y0, 0.15 * (i + 1), mat)

    # ------------------------------------------------------------------ houses
    def build(self, kind, x0, y0, avoid_colours=()):
        """Builds one house with its left edge at x0. Returns (width, door_x, wall_colour)."""
        self.count += 1
        tag = f"{kind}_{self.count}"
        self.doorstep_y = y0 - 0.95
        used = self.kind_colours.setdefault(kind, [])
        result = getattr(self, f"_{kind}")(tag, x0, y0, tuple(avoid_colours) + tuple(used[-3:]))
        used.append(result[2])
        return result

    def _pick(self, choices, avoid):
        options = [c for c in choices if c[1] not in avoid] or choices
        return self.rng.choice(options)

    def _hut(self, tag, x0, y0, avoid):
        r = self.rng
        tile, rgb = self._pick(MUD, avoid)
        lime = self.painted("limewash_wall", (0.95, 0.93, 0.87), 1.0)
        thatch = self.textured("thatch", (r.uniform(0.9, 1.0), r.uniform(0.85, 0.95), 0.8), scale=0.9)
        if r.random() < 0.45:  # round hut under a cone of thatch
            rad, h = r.uniform(1.3, 1.65), r.uniform(1.6, 1.9)
            cx, cy = x0 + rad + 0.4, y0 + rad
            self.cylinder(f"{tag}_walls", cx, cy, 0, h, rad, self.painted(tile, rgb, 0.7), 28)
            self.cylinder(f"{tag}_band", cx, cy, 0, 0.32, rad + 0.02, lime, 28)
            self.cone(f"{tag}_roof", cx, cy, h - 0.12, h + r.uniform(1.6, 2.1), rad + r.uniform(0.4, 0.55), thatch)
            door_x = cx  # the wall's front-most point, so the door sits flush on the curve
            self.door(f"{tag}_d", door_x, y0, 0.62, 1.3, r.choice(DOORS[:4]), (0.36, 0.22, 0.14))
            return 2 * rad + 0.8, door_x, rgb
        w, d, h = r.uniform(2.6, 3.4), r.uniform(2.4, 2.9), r.uniform(1.65, 1.95)
        self.box(f"{tag}_walls", x0, y0, 0, x0 + w, y0 + d, h, self.painted(tile, rgb, 0.7))
        self.box(f"{tag}_band", x0 - 0.02, y0 - 0.02, 0, x0 + w + 0.02, y0 + d + 0.02, 0.32, lime)
        oh = r.uniform(0.35, 0.5)
        self.hip(f"{tag}_roof", x0 - oh, x0 + w + oh, y0 - oh, y0 + d + oh, h - 0.08, h + r.uniform(1.4, 1.9),
                 r.uniform(0.15, 0.45), thatch)
        door_x = x0 + w * r.uniform(0.3, 0.65)
        self.door(f"{tag}_d", door_x, y0, 0.68, 1.35, r.choice(DOORS[:4]), (0.36, 0.22, 0.14))
        wx = x0 + w * (0.15 if door_x > x0 + w / 2 else 0.82)
        self.window(f"{tag}_w", wx, y0, 0.95, 0.38, 0.36, "shutters")
        return w, door_x, rgb

    def _mud_tin(self, tag, x0, y0, avoid):
        r = self.rng
        w, d, h = r.uniform(2.7, 3.8), r.uniform(2.8, 3.4), r.uniform(2.25, 2.6)
        tile, rgb = self._pick(MUD, avoid)
        # A lean-to of old planks on one side, under its own lower sheet.
        lean = r.random() < 0.5
        lw = r.uniform(1.2, 1.7) if lean else 0.0
        lean_left = lean and r.random() < 0.5
        hx = x0 + (lw if lean_left else 0.0)  # the main house's left edge
        if lean:
            lx0 = x0 if lean_left else hx + w
            lh = h * r.uniform(0.68, 0.8)
            self.box(f"{tag}_lean", lx0, y0 + 0.25, 0, lx0 + lw, y0 + d * 0.75, lh,
                     self.textured("wood_planks", r.choice([(0.9, 0.75, 0.6), (0.75, 0.8, 0.85), (0.8, 0.65, 0.5)]), 1.0))
            self.shed(f"{tag}_lean_roof", lx0 - (0.1 if lean_left else 0), lx0 + lw + (0 if lean_left else 0.1),
                      y0 - 0.1, y0 + d * 0.8, lh, lh + 0.45, self.tin())
        x0 = hx
        self.box(f"{tag}_walls", x0, y0, 0, x0 + w, y0 + d, h, self.painted(tile, rgb, 0.6))
        self.box(f"{tag}_plinth", x0 - 0.02, y0 - 0.02, 0, x0 + w + 0.02, y0 + d + 0.02, r.uniform(0.35, 0.5),
                 self.flat(r.choice(PLINTHS)))
        oh = r.uniform(0.45, 0.6)
        tin = self.tin()
        if r.random() < 0.35:  # a low gable of sheets
            ya, yb, za, zb = y0 - oh, (y0 - oh + y0 + d + 0.3) / 2, h - 0.05, h + r.uniform(0.9, 1.15)
            self.gable(f"{tag}_roof", x0 - 0.2, x0 + w + 0.2, y0 - oh, y0 + d + 0.3, za, zb, tin)
        else:  # a steep slope up to the back, so the sheets show from the low game camera
            ya, yb, za, zb = y0 - oh, y0 + d + 0.1, h + 0.05 - oh * 0.18, h + r.uniform(0.95, 1.25)
            self.shed(f"{tag}_roof", x0 - 0.12, x0 + w + 0.12, ya, yb, za, zb, tin)
            za += 0.06  # the slab's thickness

        def on_roof(y):  # height of the front slope's top surface at depth y
            return za + (y - ya) / (yb - ya) * (zb - za)
        # Stones and an old tyre hold the sheets down.
        stone = self.flat((0.5, 0.48, 0.45))
        for i in range(r.randint(2, 4)):
            sx = x0 + r.uniform(0.3, w - 0.3)
            sy = y0 + r.uniform(0.0, d * 0.4)
            bpy.ops.mesh.primitive_ico_sphere_add(radius=r.uniform(0.09, 0.14), subdivisions=1,
                                                  location=(sx, sy, on_roof(sy) + 0.07))
            s = bpy.context.active_object
            s.name = f"{tag}_stone{i}"
            s.data.materials.append(stone)
            for c in s.users_collection:
                c.objects.unlink(s)
            self.col.objects.link(s)
        if r.random() < 0.7:
            ty = y0 + d * 0.3
            bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.09,
                                             location=(x0 + r.uniform(0.6, w - 0.6), ty, on_roof(ty) + 0.1))
            t = bpy.context.active_object
            t.name = f"{tag}_tyre"
            t.rotation_euler = (math.atan2(zb - za, yb - ya), 0, 0)  # lying on the slope
            t.data.materials.append(self.flat((0.08, 0.08, 0.09), 0.0))
            for c in t.users_collection:
                c.objects.unlink(t)
            self.col.objects.link(t)
        door_left = r.random() < 0.6
        door_x = x0 + w * (r.uniform(0.28, 0.42) if door_left else r.uniform(0.6, 0.72))
        self.door(f"{tag}_d", door_x, y0, 0.8, 1.8, r.choice(DOORS[1:]), r.choice(FRAMES))
        self.window(f"{tag}_w", x0 + w * (0.74 if door_left else 0.26), y0, 1.05, 0.55, 0.5, r.choice(["bars", "shutters"]))
        return w + lw, door_x, rgb

    def _tiled(self, tag, x0, y0, avoid):
        r = self.rng
        w, d, h = r.uniform(3.4, 4.6), r.uniform(3.2, 3.8), r.uniform(2.6, 3.0)
        tile, rgb = self._pick(WALLS, avoid)
        self.box(f"{tag}_walls", x0, y0, 0, x0 + w, y0 + d, h, self.painted(tile, rgb, 0.5))
        self.box(f"{tag}_plinth", x0 - 0.02, y0 - 0.02, 0, x0 + w + 0.02, y0 + d + 0.02, r.uniform(0.4, 0.6),
                 self.flat(r.choice(PLINTHS)))
        veranda = w > 3.9 and r.random() < 0.6
        front_oh = 1.25 if veranda else r.uniform(0.45, 0.6)
        tiles = self.textured("roof_tiles", (0.95, 0.85, 0.8), scale=1.7)
        self.gable(f"{tag}_roof", x0 - 0.3, x0 + w + 0.3, y0 - front_oh, y0 + d + 0.45, h - (0.25 if veranda else 0.0),
                   h + r.uniform(1.1, 1.5), tiles)
        if veranda:
            pillar = self.textured("wood_planks", (1.0, 0.85, 0.6), scale=2.0)
            for px in (x0 + 0.25, x0 + w - 0.25):
                self.box(f"{tag}_pillar{px:.1f}", px - 0.09, y0 - 1.1, 0, px + 0.09, y0 - 0.92, h - 0.2, pillar)
            sitout = self.painted("limewash_wall", r.choice([(0.72, 0.28, 0.20), (0.95, 0.93, 0.87)]), 0.8)
            self.box(f"{tag}_sitout", x0, y0 - 1.15, 0, x0 + w, y0, 0.45, sitout)
        door_x = x0 + w * r.uniform(0.4, 0.6)
        self.door(f"{tag}_d", door_x, y0, 0.95, 2.0, r.choice(DOORS), r.choice(FRAMES), z=0.45 if veranda else 0.0)
        side = -1 if r.random() < 0.5 else 1
        self.window(f"{tag}_w", door_x + side * w * 0.3, y0, 1.15, 0.62, 0.62, r.choice(["bars", "shutters"]))
        if not veranda:
            self.steps(f"{tag}_s", door_x, y0, 1.0, 2, (0.72, 0.28, 0.2))
        return w, door_x, rgb

    def _parapet(self, tag, x0, y0, avoid):
        r = self.rng
        w, d, h = r.uniform(2.8, 4.0), r.uniform(3.0, 3.6), r.uniform(2.9, 3.4)
        tile, rgb = self._pick(WALLS, avoid)
        wall = self.painted(tile, rgb, 0.5)
        self.box(f"{tag}_walls", x0, y0, 0, x0 + w, y0 + d, h, wall)
        self.box(f"{tag}_ledge", x0 - 0.08, y0 - 0.12, h, x0 + w + 0.08, y0 + d + 0.08, h + 0.1,
                 self.painted("limewash_wall", (0.95, 0.93, 0.87), 1.0))
        # Crenellated front parapet: solid blocks with slots, plain at the sides and back.
        top = h + 0.1 + r.uniform(0.45, 0.65)
        slots = r.randint(3, 6)
        seg = w / (slots * 2 + 1)
        for i in range(slots * 2 + 1):
            if i % 2 == 0:
                self.box(f"{tag}_pp{i}", x0 + i * seg, y0 - 0.02, h + 0.1, x0 + (i + 1) * seg, y0 + 0.15, top, wall)
            else:
                self.box(f"{tag}_pp{i}", x0 + i * seg, y0 - 0.02, top - 0.18, x0 + (i + 1) * seg, y0 + 0.15, top, wall)
        self.box(f"{tag}_ppback", x0, y0 + 0.15, h + 0.1, x0 + w, y0 + d, h + 0.35, wall)
        self.box(f"{tag}_plinth", x0 - 0.02, y0 - 0.02, 0, x0 + w + 0.02, y0 + d + 0.02, r.uniform(0.4, 0.6),
                 self.flat(r.choice(PLINTHS)))
        door_x = x0 + w * r.uniform(0.35, 0.65)
        self.door(f"{tag}_d", door_x, y0, 0.9, 2.0, r.choice(DOORS), r.choice(FRAMES), z=0.3)
        self.steps(f"{tag}_s", door_x, y0, 1.0, 2, r.choice([(0.72, 0.28, 0.2), (0.95, 0.93, 0.87)]))
        side = -1 if door_x > x0 + w / 2 else 1
        self.window(f"{tag}_w", door_x + side * w * 0.28, y0, 1.25, 0.58, 0.66, r.choice(["bars", "shutters"]))
        return w, door_x, rgb

    def _shop(self, tag, x0, y0, avoid):
        """A petty shop: the whole front opens onto a counter, shelves and hanging sachet strips."""
        r = self.rng
        w, d, h = r.uniform(2.7, 3.5), r.uniform(2.6, 3.0), r.uniform(2.5, 2.8)
        tile, rgb = self._pick(WALLS, avoid)
        wall = self.painted(tile, rgb, 0.5)
        ox0, ox1, top, recess = x0 + 0.3, x0 + w - 0.3, 2.1, 0.9
        self.box(f"{tag}_back", x0, y0 + recess, 0, x0 + w, y0 + d, h, wall)
        self.box(f"{tag}_pierL", x0, y0, 0, ox0, y0 + recess, h, wall)
        self.box(f"{tag}_pierR", ox1, y0, 0, x0 + w, y0 + recess, h, wall)
        self.box(f"{tag}_lintel", ox0, y0, top, ox1, y0 + recess, h, wall)
        self.box(f"{tag}_inside", ox0, y0 + recess - 0.03, 0, ox1, y0 + recess - 0.01, top, self.flat((0.2, 0.13, 0.09), 0.03))
        self.box(f"{tag}_ceiling", ox0, y0, top - 0.02, ox1, y0 + recess, top, self.flat((0.16, 0.1, 0.07), 0.0))
        # A parapet above, with a blank signboard (no words: the art has none).
        self.box(f"{tag}_parapet", x0, y0, h, x0 + w, y0 + 0.15, h + 0.55, wall)
        board_rgb = r.choice([c for c in BRIGHT if c != rgb])
        self.box(f"{tag}_board", x0 + 0.2, y0 - 0.05, h + 0.02, x0 + w - 0.2, y0, h + 0.5, self.flat((0.97, 0.93, 0.85)))
        self.box(f"{tag}_board_in", x0 + 0.28, y0 - 0.07, h + 0.08, x0 + w - 0.28, y0 - 0.04, h + 0.44, self.flat(board_rgb))
        # Shelves of tins and packets at the back.
        shelf = self.textured("wood_planks", (0.85, 0.65, 0.45), 1.5)
        for k, z in enumerate((1.05, 1.45, 1.85)):
            self.box(f"{tag}_shelf{k}", ox0, y0 + 0.55, z - 0.03, ox1, y0 + recess - 0.03, z, shelf)
            px = ox0 + 0.05
            while px < ox1 - 0.15:
                pw, ph = r.uniform(0.08, 0.15), r.uniform(0.12, 0.26)
                self.box(f"{tag}_item{k}_{px:.2f}", px, y0 + 0.62, z, px + pw, y0 + 0.74, z + ph, self.flat(r.choice(BRIGHT)))
                px += pw + r.uniform(0.01, 0.05)
        # The counter, with a row of glass sweet jars.
        counter_mat = r.choice([self.textured("wood_planks", (0.95, 0.8, 0.6), 1.2), self.flat(r.choice(FRAMES))])
        self.box(f"{tag}_counter", ox0, y0 - 0.12, 0, ox1, y0 + 0.4, 0.95, counter_mat)
        glass, lid = self.flat((0.80, 0.88, 0.86), 0.2), self.flat((0.85, 0.2, 0.15))
        jx = ox0 + 0.18
        while jx < ox1 - 0.15:
            self.cylinder(f"{tag}_jar{jx:.2f}", jx, y0 + 0.05, 0.95, 1.2, 0.08, glass, 10)
            self.cylinder(f"{tag}_sweets{jx:.2f}", jx, y0 + 0.05, 0.96, 1.1, 0.075, self.flat(r.choice(BRIGHT)), 10)
            self.cylinder(f"{tag}_lid{jx:.2f}", jx, y0 + 0.05, 1.2, 1.24, 0.085, lid, 10)
            jx += r.uniform(0.22, 0.3)
        # Strips of sachets hanging from the lintel, and a bunch of bananas.
        for k in range(r.randint(4, 7)):
            sx = ox0 + 0.15 + k * 0.13
            if sx > ox1 - 0.4:
                break
            length = r.uniform(0.45, 0.85)
            a, b = r.sample(BRIGHT, 2)
            self.box(f"{tag}_sachets{k}a", sx, y0 - 0.02, top - length / 2, sx + 0.08, y0 + 0.01, top, self.flat(a))
            self.box(f"{tag}_sachets{k}b", sx, y0 - 0.02, top - length, sx + 0.08, y0 + 0.01, top - length / 2, self.flat(b))
        self.blob(f"{tag}_bananas", ox1 - 0.25, y0 + 0.05, top - 0.35, (0.16, 0.12, 0.3), self.flat((0.82, 0.78, 0.25)))
        # An awning on two bamboo poles: striped cloth or a tin sheet.
        oh = r.uniform(0.95, 1.25)
        z_front = h - r.uniform(0.6, 0.75)
        awning = self.stripes(*r.choice(AWNINGS)) if r.random() < 0.6 else self.tin()
        self.shed(f"{tag}_awning", x0 - 0.1, x0 + w + 0.1, y0 - oh, y0 + 0.02, z_front, h - 0.1, awning, thick=0.03)
        pole = self.flat((0.78, 0.64, 0.40))
        for px in (x0 + 0.05, x0 + w - 0.05):
            self.cylinder(f"{tag}_pole{px:.1f}", px, y0 - oh + 0.08, 0, z_front, 0.035, pole, 8)
        if r.random() < 0.5:  # a bench for the regulars
            bx = r.choice([x0 - 0.2, x0 + w - 1.3])
            bench = self.textured("wood_planks", (0.85, 0.65, 0.45), 1.2)
            self.box(f"{tag}_bench", bx, y0 - oh - 0.05, 0.42, bx + 1.5, y0 - oh + 0.3, 0.48, bench)
            for lx in (bx + 0.1, bx + 1.32):
                self.box(f"{tag}_bench_leg{lx:.1f}", lx, y0 - oh, 0, lx + 0.08, y0 - oh + 0.25, 0.42, bench)
        self.doorstep_y = y0 - oh - 0.55
        return w, (ox0 + ox1) / 2, rgb

    def _head(self, tag, x0, y0, avoid):
        """The village head's house: wide, two storeys, a raised pillared veranda (thinnai) under tiles."""
        r = self.rng
        w, d = r.uniform(6.4, 7.2), r.uniform(3.8, 4.3)
        plinth, h1, h2 = 0.75, r.uniform(2.9, 3.2), r.uniform(2.2, 2.5)
        tile, rgb = self._pick([WALLS[0], WALLS[2], WALLS[3], WALLS[5]], avoid)  # pale and proud
        wall = self.painted(tile, rgb, 0.45)
        lime = self.painted("limewash_wall", (0.95, 0.93, 0.87), 1.0)
        trim_rgb = r.choice([(0.70, 0.25, 0.18), (0.20, 0.45, 0.60), (0.25, 0.50, 0.30)])
        ver = r.uniform(1.6, 1.85)
        # Plinth and veranda floor in red oxide, edged in lime.
        self.box(f"{tag}_plinth", x0 - 0.1, y0 - ver, 0, x0 + w + 0.1, y0 + d, plinth,
                 self.painted("limewash_wall", (0.72, 0.28, 0.20), 0.8))
        self.box(f"{tag}_edge", x0 - 0.12, y0 - ver - 0.02, plinth - 0.1, x0 + w + 0.12, y0 + d, plinth, lime)
        z1 = plinth + h1
        self.box(f"{tag}_walls", x0, y0, plinth, x0 + w, y0 + d, z1, wall)
        self.box(f"{tag}_dado", x0 - 0.01, y0 - 0.01, plinth, x0 + w + 0.01, y0 + d, plinth + 0.45, self.flat(trim_rgb))
        # Pillars along the veranda, white with coloured bases and capitals.
        n = r.choice([4, 5, 6])
        pillar, cap = self.painted("limewash_wall", (0.96, 0.95, 0.9), 1.2), self.flat(trim_rgb)
        top = z1 - 0.35
        for i in range(n):
            px = x0 + 0.25 + (w - 0.5) * i / (n - 1)
            py = y0 - ver + 0.28
            self.box(f"{tag}_base{i}", px - 0.17, py - 0.17, plinth, px + 0.17, py + 0.17, plinth + 0.3, cap)
            self.cylinder(f"{tag}_pillar{i}", px, py, plinth + 0.3, top - 0.18, 0.11, pillar, 16)
            self.box(f"{tag}_capital{i}", px - 0.19, py - 0.19, top - 0.18, px + 0.19, py + 0.19, top, cap)
        self.box(f"{tag}_beam", x0 - 0.05, y0 - ver + 0.08, top, x0 + w + 0.05, y0 - ver + 0.48, top + 0.2,
                 self.textured("wood_planks", (0.9, 0.7, 0.5), 1.0))
        tiles = self.textured("roof_tiles", (0.95, 0.85, 0.8), scale=1.7)
        self.shed(f"{tag}_ver_roof", x0 - 0.3, x0 + w + 0.3, y0 - ver - 0.45, y0 + 0.05, top + 0.05, z1 + 0.35, tiles, 0.08)
        # The roof terrace and the upper storey, set back, with its own tiled gable.
        self.box(f"{tag}_terrace", x0 - 0.06, y0, z1, x0 + w + 0.06, y0 + d, z1 + 0.14, lime)
        ux0, ux1 = x0 + w * r.uniform(0.15, 0.22), x0 + w * r.uniform(0.78, 0.85)
        uy0 = y0 + 0.7
        z2 = z1 + 0.14 + h2
        self.box(f"{tag}_upper", ux0, uy0, z1 + 0.14, ux1, y0 + d - 0.3, z2, wall)
        self.gable(f"{tag}_roof", ux0 - 0.4, ux1 + 0.4, uy0 - 0.5, y0 + d + 0.1, z2 - 0.05, z2 + r.uniform(1.2, 1.5), tiles)
        for i, fx in enumerate((0.25, 0.5, 0.75)):
            self.window(f"{tag}_uw{i}", ux0 + (ux1 - ux0) * fx, uy0, z1 + 0.85, 0.5, 0.75, "shutters" if i != 1 else "bars")
        # A railing along the terrace's front edge.
        rail = self.flat(trim_rgb)
        self.box(f"{tag}_rail", x0, y0 + 0.02, z1 + 0.62, x0 + w, y0 + 0.1, z1 + 0.7, rail)
        bx = x0 + 0.1
        while bx < x0 + w:
            if not (ux0 - 0.1 < bx < ux1 + 0.1):
                self.box(f"{tag}_bal{bx:.2f}", bx, y0 + 0.03, z1 + 0.14, bx + 0.05, y0 + 0.09, z1 + 0.62, rail)
            bx += 0.22
        # The big door with a mango-leaf garland (thoranam), and barred windows either side.
        door_x = x0 + w * 0.5
        self.door(f"{tag}_d", door_x, y0, 1.3, 2.3, r.choice([(0.95, 0.80, 0.55), (0.62, 0.24, 0.22)]), trim_rgb, z=plinth)
        leaf = self.flat((0.25, 0.55, 0.2))
        for k in range(11):
            lx = door_x - 0.75 + k * 0.15
            self.box(f"{tag}_leaf{k}", lx - 0.035, y0 - 0.08, plinth + 2.05, lx + 0.035, y0 - 0.06, plinth + 2.38, leaf)
        for side in (-1, 1):
            self.window(f"{tag}_w{side}", door_x + side * w * 0.3, y0, plinth + 0.9, 0.7, 0.9, "bars")
        self.steps(f"{tag}_s", door_x, y0 - ver, 1.6, 5, (0.72, 0.28, 0.20))
        self.doorstep_y = y0 - ver - 2.1
        return w, door_x, rgb

    def compound(self, tag, x0, x1, y, h, avoid=()):
        """A compound wall between houses: coping, a coloured dado, end pillars, sometimes decorative openings."""
        r = self.rng
        tile, rgb = self._pick(WALLS + MUD, avoid)
        wall = self.painted(tile, rgb, 0.6)
        lime = self.painted("limewash_wall", (0.95, 0.93, 0.87), 1.0)
        t = 0.25
        self.box(f"{tag}_wall", x0, y, 0, x1, y + t, h, wall)
        self.box(f"{tag}_coping", x0 - 0.04, y - 0.05, h, x1 + 0.04, y + t + 0.05, h + 0.09, lime)
        self.box(f"{tag}_dado", x0 - 0.01, y - 0.01, 0, x1 + 0.01, y + t, 0.35, self.flat(r.choice(PLINTHS)))
        for px in (x0 + 0.16, x1 - 0.16):
            self.box(f"{tag}_pier{px:.1f}", px - 0.16, y - 0.06, 0, px + 0.16, y + t + 0.06, h + 0.25, wall)
            self.box(f"{tag}_cap{px:.1f}", px - 0.2, y - 0.1, h + 0.25, px + 0.2, y + t + 0.1, h + 0.34, lime)
        if r.random() < 0.5:
            dark = self.flat((0.18, 0.12, 0.08), 0.0)
            n = max(1, int((x1 - x0 - 0.8) / 0.4))
            for i in range(n):
                cx = x0 + 0.4 + (x1 - x0 - 0.8) * (i + 0.5) / n
                self.box(f"{tag}_hole{i}", cx - 0.08, y - 0.01, h - 0.42, cx + 0.08, y + 0.02, h - 0.22, dark)
        return rgb

    # ------------------------------------------------------------------ coconut palms and palm-leaf fences
    def _palm_materials(self):
        """Shared by every palm: two trunk barks, three frond colours (green, sunlit, dry), two coconut colours."""
        if getattr(self, "_palm_mats", None):
            return self._palm_mats
        trunks = []
        for rgb in ((0.58, 0.50, 0.42), (0.50, 0.44, 0.38)):
            mat, nt, bsdf = self._material(f"M_palm_trunk_{len(trunks)}", 0.1)
            geo = nt.nodes.new("ShaderNodeNewGeometry")
            rings = nt.nodes.new("ShaderNodeTexWave")
            rings.wave_type = "BANDS"
            rings.bands_direction = "Z"
            rings.inputs["Scale"].default_value = 0.314 / 0.13  # a ring every 13 cm
            rings.inputs["Distortion"].default_value = 1.5
            nt.links.new(geo.outputs["Position"], rings.inputs["Vector"])
            shade = nt.nodes.new("ShaderNodeMapRange")
            shade.inputs["To Min"].default_value, shade.inputs["To Max"].default_value = 0.72, 1.08
            nt.links.new(rings.outputs["Fac"], shade.inputs["Value"])
            out = self._multiply(nt, srgb_to_linear(rgb), shade.outputs["Result"])
            nt.links.new(out, bsdf.inputs["Base Color"])
            nt.links.new(out, bsdf.inputs["Emission Color"])
            trunks.append(mat)
        fronds = [self._frond_material(n, a, b) for n, a, b in (
            ("green", (0.16, 0.34, 0.10), (0.40, 0.56, 0.16)),
            ("sunlit", (0.28, 0.48, 0.13), (0.62, 0.70, 0.24)),
            ("dry", (0.55, 0.42, 0.22), (0.80, 0.66, 0.36)))]
        nuts = [self.flat((0.45, 0.56, 0.18)), self.flat((0.55, 0.36, 0.18))]
        self._palm_mats = trunks, fronds, nuts
        return self._palm_mats

    def _frond_material(self, name, base, tip):
        """Leaflets cut out of a ribbon by alpha: slanted strips, a solid midrib, a few leaflets missing."""
        mat, nt, bsdf = self._material(f"M_frond_{name}", 0.16)
        N, L = nt.nodes, nt.links
        uvn = N.new("ShaderNodeTexCoord")
        sep = N.new("ShaderNodeSeparateXYZ")
        L.new(uvn.outputs["UV"], sep.inputs[0])
        u, v = sep.outputs["X"], sep.outputs["Y"]

        def m(op, a, b=0.0):
            n = N.new("ShaderNodeMath")
            n.operation = op
            for i, val in enumerate((a, b)):
                if isinstance(val, bpy.types.NodeSocket):
                    L.new(val, n.inputs[i])
                else:
                    n.inputs[i].default_value = val
            return n.outputs[0]

        phase = m("SUBTRACT", m("MULTIPLY", u, 28.0), m("MULTIPLY", v, 1.8))  # leaflets slant toward the tip
        duty = m("SUBTRACT", 0.86, m("MULTIPLY", v, 0.42))                    # and taper to points
        leaf = m("LESS_THAN", m("FRACT", phase), duty)
        hole = N.new("ShaderNodeTexWhiteNoise")
        hole.noise_dimensions = "1D"
        L.new(m("FLOOR", phase), hole.inputs["W"])
        leaf = m("MULTIPLY", leaf, m("GREATER_THAN", hole.outputs["Value"], 0.1))
        alpha = m("MAXIMUM", leaf, m("LESS_THAN", v, 0.05))                   # the midrib
        L.new(alpha, bsdf.inputs["Alpha"])
        mix = N.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        s = {x.identifier: x for x in mix.inputs}
        L.new(m("ADD", m("MULTIPLY", u, 0.6), m("MULTIPLY", v, 0.4)), s["Factor_Float"])
        s["A_Color"].default_value = (*srgb_to_linear(base), 1)
        s["B_Color"].default_value = (*srgb_to_linear(tip), 1)
        out = next(x for x in mix.outputs if x.identifier == "Result_Color")
        L.new(out, bsdf.inputs["Base Color"])
        L.new(out, bsdf.inputs["Emission Color"])
        mat.surface_render_method = "DITHERED"
        return mat

    def coconut_palm(self, tag, x, y, height=None, collection=None):
        """A coconut palm: a curved, ringed trunk, a crown of 12-18 fronds (one or two dry), a bunch of coconuts.
        Every palm differs in height, lean, curve, frond count, frond angles and colours."""
        r = self.rng
        trunks, fronds, nuts = self._palm_materials()
        H = height or r.uniform(6.0, 10.5)
        lx, ly = r.uniform(-1, 1) * H * 0.16, r.uniform(-0.2, 0.5)

        def centre(t):
            bend = 1 - (1 - t) ** 2  # most of the curve near the base, as palms reach for light
            return x + lx * bend, y + ly * bend, H * t

        verts, faces, seg, rings = [], [], 9, 18
        for i in range(rings + 1):
            t = i / rings
            cx, cy, cz = centre(t)
            rad = 0.17 - 0.06 * t + (0.07 if i == 0 else 0.0)
            for k in range(seg):
                a = 2 * math.pi * k / seg
                verts.append((cx + rad * math.cos(a), cy + rad * math.sin(a), cz))
        for i in range(rings):
            for k in range(seg):
                a, b = i * seg + k, i * seg + (k + 1) % seg
                faces.append((a, b, b + seg, a + seg))
        col, self.col = self.col, collection or self.col
        trunk = self.mesh(f"{tag}_trunk", verts, faces, r.choice(trunks))
        for poly in trunk.data.polygons:
            poly.use_smooth = True

        top = centre(1.0)
        fv, ff, fuv, fmat = [], [], [], []
        n = r.randint(17, 24)
        dry = set(r.sample(range(n), r.choice([0, 1, 1, 2])))
        for j in range(n):
            az = 2 * math.pi * j / n + r.uniform(-0.25, 0.25)
            # Young fronds stand up in the middle, older ones arch out and hang; dry ones hang straight down.
            elev = math.radians(r.uniform(-20, 70)) if j not in dry else math.radians(r.uniform(-80, -60))
            length = r.uniform(2.8, 4.0) * (H / 8.5) ** 0.3
            sag = r.uniform(0.14, 0.26) * (1.4 if elev < 0.3 else 1.0)
            d = (math.cos(az), math.sin(az))
            perp = (-d[1], d[0])
            steps = 10
            for side in (-1, 1):
                base = len(fv)
                for i in range(steps + 1):
                    s = i / steps
                    run = length * s
                    px = top[0] + d[0] * run * math.cos(elev)
                    py = top[1] + d[1] * run * math.cos(elev)
                    pz = top[2] + run * math.sin(elev) - sag * run * run
                    w = 0.7 * math.sin(math.pi * min(1.0, 0.12 + s * 0.95)) ** 0.6
                    droop = math.radians(r.uniform(45, 65))
                    ex = px + side * perp[0] * w * math.cos(droop)
                    ey = py + side * perp[1] * w * math.cos(droop)
                    ez = pz - w * math.sin(droop)
                    fv += [(px, py, pz), (ex, ey, ez)]
                    fuv += [(s, 0.0), (s, 1.0)]
                for i in range(steps):
                    a = base + 2 * i
                    ff.append((a, a + 2, a + 3, a + 1))
                    fmat.append(2 if j in dry else (1 if r.random() < 0.35 else 0))
        me = bpy.data.meshes.new(f"{tag}_crown")
        me.from_pydata(fv, [], ff)
        uv = me.uv_layers.new()
        for poly in me.polygons:
            for li in poly.loop_indices:
                uv.data[li].uv = fuv[me.loops[li].vertex_index]
        for mat in fronds:
            me.materials.append(mat)
        for poly, k in zip(me.polygons, fmat):
            poly.material_index = k
        crown = bpy.data.objects.new(f"{tag}_crown", me)
        self.col.objects.link(crown)
        # A bunch of coconuts under the crown.
        nut = r.choice(nuts)
        for k in range(r.randint(3, 8)):
            a = r.uniform(0, 6.28)
            self.blob(f"{tag}_nut{k}", top[0] + 0.16 * math.cos(a), top[1] + 0.16 * math.sin(a),
                      top[2] - r.uniform(0.15, 0.4), (0.1, 0.1, 0.11), nut)
        self.col = col
        return trunk

    def fence(self, tag, x0, x1, y0, y1, height, style="palm", gap=None):
        """A fence of woven dried coconut leaves ("palm") or split-bamboo matting ("bamboo") along a straight line,
        on thin posts, with a ragged top. gap=(a, b): leave an opening between those fractions of its length."""
        r = self.rng
        if style == "palm":
            panel = self.textured("thatch", (r.uniform(0.74, 0.84), r.uniform(0.62, 0.70), 0.50), scale=1.3)
        else:
            panel = self.textured("bamboo_weave", (1.0, 0.86, 0.66), scale=1.6)
        post = self.flat((0.45, 0.33, 0.22))
        length = math.hypot(x1 - x0, y1 - y0)
        dx, dy = (x1 - x0) / length, (y1 - y0) / length
        spans = [(0.0, gap[0]), (gap[1], 1.0)] if gap else [(0.0, 1.0)]
        for si, (a, b) in enumerate(spans):
            cols = max(2, int(length * (b - a) / 0.18))
            verts, faces = [], []
            for i in range(cols + 1):
                f = a + (b - a) * i / cols
                px, py = x0 + dx * length * f, y0 + dy * length * f
                top = height + (r.uniform(-0.14, 0.06) if style == "palm" else r.uniform(-0.03, 0.03))
                verts += [(px, py, 0.02), (px, py, top)]
            for i in range(cols):
                k = 2 * i
                faces.append((k, k + 2, k + 3, k + 1))
            self.mesh(f"{tag}_panel{si}", verts, faces, panel)
            run = length * (b - a)
            for p in range(int(run / 1.6) + 2):
                f = a + (b - a) * min(1.0, p * 1.6 / run)
                self.cylinder(f"{tag}_post{si}_{p}", x0 + dx * length * f, y0 + dy * length * f - 0.04, 0,
                              height + 0.12, 0.035, post, 6)
